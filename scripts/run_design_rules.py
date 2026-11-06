# -*- coding: utf-8 -*-
r"""
run_design_rules.py -- derive the empirical "design rules" for damage-tolerant
leaf venation from the archived cohort results, and test each one.

Reads ONLY the archive (data/*.csv, data/*.json) plus the raw Matos deposit (for
per-leaf degree distributions).  Never re-runs percolation.

Rules tested
  R1  bounds        : 2 <= <k> <= 3 for a venation whose junctions are 3-way;
                      loops per junction L = <k>/2 - 1  (cycle rank identity)
  R2  free endings  : <k> = 3 - 2t   (t = fraction of nodes with degree 1)
                      -> every free vein ending is half a loop not built
  R3  tolerance law : f50 = a + b (<k> - 2)   cohort OLS, synthetic in-range OLS
  R4  Molloy-Reed   : f50 < 1 - 1/(kappa - 1), kappa = <k^2>/<k>, per leaf
  R5  no hubs       : max degree <= 5, degree SD < 1 -> weighted-removal penalty
                      is small and shrinks with loop fraction
  R6  loop span     : gain per added edge rises with the span of the loop closed
                      (shortest planar < random planar < non-planar), equal edge counts
  R7  diminishing   : delta f50 = c (k_ceiling - k0)
  R8  locality      : a contiguous lesion needs ~2.3-2.5x the loss; under lesions
                      only D predicts
  R9  geometry      : branch angle, Murray exponent, daughter symmetry, length
                      ratio, vein length/radius do NOT move f50 (rank tests)

Outputs
  data/design_rules.json
  data/design_rules_perleaf.csv
  figures/design_rules.png

    python scripts/run_design_rules.py
ASCII-only stdout.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from holoparasitic import realleaf  # noqa: E402

DATA = ROOT / "data"
FIG = ROOT / "figures"
MATOS = ROOT / "UCBG_venation_form_data" / "UCBG_venation_form_data"

K_CEILING = 2.811  # cohort P90 used by the enhancement experiment


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def degree_distribution(veins_csv: Path) -> dict:
    """Degree distribution of the graph exactly as realleaf.load_matos builds it:
    self-loops dropped, non-finite/zero width or length dropped, parallel
    edges collapsed.  Returns counts of degree 1..max and <k>, <k^2>."""
    df = pd.read_csv(veins_csv, usecols=["EndNodes_1", "EndNodes_2", "Width", "Length"])
    a = df["EndNodes_1"].astype(float).astype(int).to_numpy()
    b = df["EndNodes_2"].astype(float).astype(int).to_numpy()
    w = df["Width"].to_numpy(dtype=float)
    ln = df["Length"].to_numpy(dtype=float)
    keep = (a != b) & np.isfinite(w) & (w > 0) & np.isfinite(ln) & (ln > 0)
    a, b = a[keep], b[keep]
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    pairs = np.unique(np.stack([lo, hi], axis=1), axis=0)
    ids, deg = np.unique(pairs.ravel(), return_counts=True)
    kmax = int(deg.max())
    counts = np.bincount(deg, minlength=kmax + 1)[1:]  # index 0 -> degree 1
    n = int(len(ids))
    e = int(len(pairs))
    k = deg.mean()
    k2 = (deg.astype(float) ** 2).mean()
    return {"N": n, "E": e, "mean_degree": float(k), "mean_k2": float(k2),
            "max_degree": kmax,
            "p_k": {int(i + 1): float(c / n) for i, c in enumerate(counts)}}


def two_core(veins_csv: Path) -> dict:
    """Iteratively prune degree<=1 nodes (same edge filter as load_matos).
    Returns the 2-core fraction, the hanging-tree node fraction and the number
    and mean size of hanging trees (one attachment edge per tree)."""
    df = pd.read_csv(veins_csv, usecols=["EndNodes_1", "EndNodes_2", "Width", "Length"])
    a = df["EndNodes_1"].astype(float).astype(int).to_numpy()
    b = df["EndNodes_2"].astype(float).astype(int).to_numpy()
    w = df["Width"].to_numpy(dtype=float)
    ln = df["Length"].to_numpy(dtype=float)
    keep = (a != b) & np.isfinite(w) & (w > 0) & np.isfinite(ln) & (ln > 0)
    a, b = a[keep], b[keep]
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    pairs = np.unique(np.stack([lo, hi], axis=1), axis=0)
    ids, inv = np.unique(pairs.ravel(), return_inverse=True)
    u, v = inv.reshape(-1, 2).T
    n = len(ids)
    alive_e = np.ones(len(u), bool)
    alive_n = np.ones(n, bool)
    rounds = 0
    while True:
        deg = np.bincount(u[alive_e], minlength=n) + np.bincount(v[alive_e], minlength=n)
        kill = alive_n & (deg <= 1)
        if not kill.any():
            break
        alive_n &= ~kill
        alive_e &= alive_n[u] & alive_n[v]
        rounds += 1
    core = int(alive_n.sum())
    # attachment edges: one endpoint in core, the other pruned (original edge set)
    att = int(((alive_n[u]) ^ (alive_n[v])).sum())
    pruned = n - core
    return {"N": n, "core_nodes": core, "core_frac": core / n,
            "hanging_frac": pruned / n, "n_hanging_trees": att,
            "mean_hanging_tree_size": (pruned / att) if att else 0.0,
            "prune_rounds": rounds}


def partial_spearman_multi(x, y, Z):
    """Spearman partial correlation of x and y controlling for the columns of Z."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    Z = np.column_stack([np.asarray(z, float) for z in Z])
    m = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(Z), axis=1)
    rx, ry = stats.rankdata(x[m]), stats.rankdata(y[m])
    RZ = np.column_stack([stats.rankdata(Z[m, j]) for j in range(Z.shape[1])])
    A = np.column_stack([np.ones(m.sum()), RZ])

    def resid(a):
        beta, *_ = np.linalg.lstsq(A, a, rcond=None)
        return a - A @ beta

    r, p = stats.pearsonr(resid(rx), resid(ry))
    return float(r), float(p), int(m.sum())


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    r, p = stats.spearmanr(x[m], y[m])
    return float(r), float(p), int(m.sum())


def partial_spearman(x, y, z):
    """Spearman partial correlation of x and y controlling for z (rank residuals)."""
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    m = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    rx, ry, rz = (stats.rankdata(v[m]) for v in (x, y, z))

    def resid(a, c):
        A = np.column_stack([np.ones_like(c), c])
        beta, *_ = np.linalg.lstsq(A, a, rcond=None)
        return a - A @ beta

    ex, ey = resid(rx, rz), resid(ry, rz)
    r, p = stats.pearsonr(ex, ey)
    return float(r), float(p), int(m.sum())


def ols(X, y):
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ beta
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    n, p = A.shape
    dof = n - p
    sigma2 = ss_res / dof
    cov = sigma2 * np.linalg.inv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    return {"beta": beta.tolist(), "se": se.tolist(),
            "t": (beta / se).tolist(), "R2": 1 - ss_res / ss_tot, "n": int(n),
            "dof": int(dof), "rmse": float(np.sqrt(sigma2))}


def q(x, qs=(0.25, 0.5, 0.75)):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return [float(np.quantile(x, v)) for v in qs]


# --------------------------------------------------------------------------
# load archive
# --------------------------------------------------------------------------
master = pd.read_csv(DATA / "analysis_master.csv")
char = pd.read_csv(DATA / "characterization.csv")
loc = pd.read_csv(DATA / "criterion_and_locality.csv")
edge = pd.read_csv(DATA / "random_edge_control.csv")
grid = pd.read_csv(DATA / "synthetic_grid_pc.csv")
sugg = pd.read_csv(DATA / "cohort_suggested.csv")

geom_cols = ["geom_branch_angle_deg", "geom_branch_angle_std", "geom_murray_exponent",
             "geom_daughter_symmetry", "geom_length_ratio", "mean_vein_length",
             "mean_radius", "max_degree", "n_cycles", "n_terminals", "n_components"]
geom_cols = [c for c in geom_cols if c not in master.columns]   # avoid _x/_y suffixes
df = master.merge(char[["name"] + geom_cols], on="name", how="left")
df = df.merge(loc[["species", "pc_disc1", "pc_disc10", "pc_source", "pc_gcc"]]
              .rename(columns={"species": "name"}), on="name", how="left")

coh = df[df["in_percolation_cohort_100"] == True].copy()   # noqa: E712
enh = df[df["in_enhancement_cohort_105"] == True].copy()   # noqa: E712
assert len(coh) == 100, len(coh)
assert len(enh) == 105, len(enh)

# --------------------------------------------------------------------------
# per-leaf degree distributions (cohort of 100) + native branching angle
# --------------------------------------------------------------------------
t0 = time.time()
DD_CACHE = DATA / "design_rules_degree.csv"
if (DD_CACHE.exists() and "areole_elongation_median" in pd.read_csv(DD_CACHE, nrows=1).columns
        and set(pd.read_csv(DD_CACHE)["name"]) >= set(coh["name"])):
    dd_df = pd.read_csv(DD_CACHE)
    print(f"degree distributions: loaded cache {DD_CACHE.name}")
else:
    pairs = {name: (n, v) for name, n, v in realleaf.find_leaf_pairs(str(MATOS))}
    rows = []
    for name in coh["name"]:
        nodes_csv, veins_csv = pairs[name]
        dd = degree_distribution(Path(veins_csv))
        tc = two_core(Path(veins_csv))
        pk = dd["p_k"]
        nd = pd.read_csv(nodes_csv, usecols=["theta_D2_D1", "node_Degree"])
        th = nd.loc[nd["node_Degree"] == 3, "theta_D2_D1"].to_numpy(float)
        th = th[np.isfinite(th)]
        # Matos' own summary table: median areole area + areole count
        sm_files = sorted(Path(veins_csv).parent.glob("*_summary.csv"))
        sm = pd.read_csv(sm_files[0]) if sm_files else pd.DataFrame()
        rows.append({
            "name": name, "N_dd": dd["N"], "E_dd": dd["E"], "k_dd": dd["mean_degree"],
            "k2_dd": dd["mean_k2"], "max_degree_dd": dd["max_degree"],
            "p1": pk.get(1, 0.0), "p2": pk.get(2, 0.0), "p3": pk.get(3, 0.0),
            "p4": pk.get(4, 0.0), "p5plus": sum(v for k_, v in pk.items() if k_ >= 5),
            "theta_daughters_median_deg": float(np.median(th)) if len(th) else np.nan,
            "theta_n": int(len(th)),
            "core_frac": tc["core_frac"], "hanging_frac": tc["hanging_frac"],
            "n_hanging_trees": tc["n_hanging_trees"],
            "mean_hanging_tree_size": tc["mean_hanging_tree_size"],
            "prune_rounds": tc["prune_rounds"],
            "areole_median_area_mm2": float(sm["AmdAre"].iloc[0]) if "AmdAre" in sm else np.nan,
            "areole_count": float(sm["ANN"].iloc[0]) if "ANN" in sm else np.nan,
            "areole_elongation_median": float(sm["AmdElg"].iloc[0]) if "AmdElg" in sm else np.nan,
            "areole_circularity_median": float(sm["AmdCir"].iloc[0]) if "AmdCir" in sm else np.nan,
            "areole_eccentricity_median": float(sm["AmdEcc"].iloc[0]) if "AmdEcc" in sm else np.nan,
            "vein_mean_len_mm": float(sm["VTotavLen"].iloc[0]) if "VTotavLen" in sm else np.nan,
        })
        print(f"  {name:<8} N={dd['N']:>7} <k>={dd['mean_degree']:.4f} "
              f"p1={pk.get(1,0):.3f} p3={pk.get(3,0):.3f} kmax={dd['max_degree']} "
              f"core={tc['core_frac']:.3f} trees={tc['n_hanging_trees']} "
              f"size={tc['mean_hanging_tree_size']:.2f}")
    dd_df = pd.DataFrame(rows)
    dd_df.to_csv(DD_CACHE, index=False)
    print(f"degree distributions: {time.time()-t0:.0f}s (cached to {DD_CACHE.name})")
coh = coh.merge(dd_df, on="name", how="left")

# consistency of the fast loader with the archived characterisation
assert np.allclose(coh["k_dd"], coh["mean_degree"], atol=2e-3), \
    float(np.abs(coh["k_dd"] - coh["mean_degree"]).max())

out: dict = {"_generated_by": "scripts/run_design_rules.py",
             "n_cohort": 100, "n_enhancement": 105,
             "k_ceiling": K_CEILING}

# --------------------------------------------------------------------------
# R1 bounds + loop budget
# --------------------------------------------------------------------------
coh["L_cycle_rank_per_node"] = coh["n_cycles"] / coh["n_nodes"]
coh["L_from_k"] = coh["mean_degree"] / 2 - 1
coh["k_core"] = 2 + (coh["mean_degree"] - 2) / coh["core_frac"]
coh["L_core"] = coh["L_cycle_rank_per_node"] / coh["core_frac"]
coh["L_resid"] = coh["L_cycle_rank_per_node"] - coh["L_from_k"]
out["R1_bounds"] = {
    "k_min": float(coh["mean_degree"].min()), "k_max": float(coh["mean_degree"].max()),
    "k_quartiles": q(coh["mean_degree"]),
    "max_degree_max": int(coh["max_degree_dd"].max()),
    "max_degree_counts": coh["max_degree_dd"].value_counts().sort_index().to_dict(),
    "degree_sd_quartiles": q(coh["degree_sd"]),
    "loops_per_node_quartiles": q(coh["L_cycle_rank_per_node"]),
    "loops_per_node_range": [float(coh["L_cycle_rank_per_node"].min()),
                             float(coh["L_cycle_rank_per_node"].max())],
    "identity_L_eq_k_over_2_minus_1_max_abs_resid": float(coh["L_resid"].abs().max()),
    "L_at_ceiling": K_CEILING / 2 - 1,
    "note": "cycle rank = E - N + c; per node = <k>/2 - 1 + c/N (exact)",
}

# --------------------------------------------------------------------------
# R2 free endings: <k> = 3 - 2 t
# --------------------------------------------------------------------------
coh["k_pred_from_t"] = 3 - 2 * coh["p1"]
coh["k_resid_from_t"] = coh["mean_degree"] - coh["k_pred_from_t"]
# exact decomposition: <k> = 3 - 2 p1 - p2 + p4 + 2 p5 + ...
r2_fit = ols(coh[["p1"]].to_numpy(), coh["mean_degree"].to_numpy())
pear = stats.pearsonr(coh["p1"], coh["mean_degree"])
out["R2_free_endings"] = {
    "identity": "<k> = 3 - 2*t - p2 + p4 + 2*p5 + ...; with p2,p4,p5 small, <k> ~ 3 - 2t",
    "p1_quartiles": q(coh["p1"]), "p2_quartiles": q(coh["p2"]),
    "p3_quartiles": q(coh["p3"]), "p4_quartiles": q(coh["p4"]),
    "p5plus_max": float(coh["p5plus"].max()),
    "resid_k_minus_(3-2t)_median": float(coh["k_resid_from_t"].median()),
    "resid_k_minus_(3-2t)_max_abs": float(coh["k_resid_from_t"].abs().max()),
    "pearson_r_t_vs_k": float(pear[0]), "pearson_p": float(pear[1]),
    "ols_k_on_t": {"intercept": r2_fit["beta"][0], "slope": r2_fit["beta"][1],
                   "R2": r2_fit["R2"], "se_slope": r2_fit["se"][1]},
    "spearman_t_vs_pc": spearman(coh["p1"], coh["pc_random"]),
    "loops_per_free_ending": "L = 1/2 - t  (each free ending is half a loop not built)",
}

# --------------------------------------------------------------------------
# R3 tolerance law
# --------------------------------------------------------------------------
km2 = (coh["mean_degree"] - 2).to_numpy()
pc = coh["pc_random"].to_numpy()
fit_k = ols(km2[:, None], pc)
fit_kD = ols(np.column_stack([km2, coh["D"].to_numpy() - 1.5]), pc)
fit_L = ols(coh[["L_cycle_rank_per_node"]].to_numpy(), pc)
fit_t = ols(coh[["p1"]].to_numpy(), pc)
g_in = grid[grid["mean_degree"] <= coh["mean_degree"].max()].copy()
fit_g = ols((g_in["mean_degree"] - 2).to_numpy()[:, None], g_in["pc_random"].to_numpy())
fit_gD = ols(np.column_stack([g_in["mean_degree"] - 2, g_in["D"] - 1.5]),
             g_in["pc_random"].to_numpy())
fit_gall = ols((grid["mean_degree"] - 2).to_numpy()[:, None], grid["pc_random"].to_numpy())
# quartile medians by <k>
coh["k_quartile"] = pd.qcut(coh["mean_degree"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
quart = coh.groupby("k_quartile", observed=True).agg(
    n=("name", "size"), k_median=("mean_degree", "median"),
    L_median=("L_cycle_rank_per_node", "median"), t_median=("p1", "median"),
    pc_median=("pc_random", "median"), pc_degree_median=("pc_degree", "median"),
    disc1_median=("pc_disc1", "median"), disc10_median=("pc_disc10", "median"))
out["R3_tolerance_law"] = {
    "cohort_ols_pc_on_(k-2)": fit_k,
    "cohort_ols_pc_on_(k-2)_and_(D-1.5)": fit_kD,
    "cohort_ols_pc_on_L": fit_L,
    "cohort_ols_pc_on_t": fit_t,
    "synthetic_inrange_ols_pc_on_(k-2)": fit_g,
    "synthetic_inrange_ols_pc_on_(k-2)_and_(D-1.5)": fit_gD,
    "synthetic_fullgrid_ols_pc_on_(k-2)": fit_gall,
    "n_synthetic_inrange": int(len(g_in)),
    "per_0.1_k_cohort": fit_k["beta"][1] * 0.1,
    "per_0.1_k_synthetic": fit_g["beta"][1] * 0.1,
    "per_10pct_free_endings_cohort": fit_t["beta"][1] * 0.1,
    "spearman_k_vs_pc": spearman(coh["mean_degree"], coh["pc_random"]),
    "quartiles_by_k": quart.reset_index().to_dict(orient="records"),
}

# --------------------------------------------------------------------------
# R4 Molloy-Reed ceiling
# --------------------------------------------------------------------------
coh["kappa"] = coh["k2_dd"] / coh["k_dd"]
coh["fc_MR"] = 1 - 1 / (coh["kappa"] - 1)
coh["pc_over_fcMR"] = coh["pc_random"] / coh["fc_MR"]
# Also the naive kappa from (mean, sd) only, as a check
coh["kappa_from_sd"] = (coh["mean_degree"] ** 2 + coh["degree_sd"] ** 2) / coh["mean_degree"]
out["R4_molloy_reed"] = {
    "kappa_quartiles": q(coh["kappa"]), "kappa_range": [float(coh["kappa"].min()), float(coh["kappa"].max())],
    "kappa_vs_kappa_from_sd_max_abs_diff": float((coh["kappa"] - coh["kappa_from_sd"]).abs().max()),
    "fc_MR_quartiles": q(coh["fc_MR"]), "fc_MR_range": [float(coh["fc_MR"].min()), float(coh["fc_MR"].max())],
    "n_pc_below_fcMR": int((coh["pc_random"] < coh["fc_MR"]).sum()),
    "n_pc_degree_below_fcMR": int((coh["pc_degree"] < coh["fc_MR"]).sum()),
    "n_disc1_below_fcMR": int((coh["pc_disc1"] < coh["fc_MR"]).sum()),
    "n_disc10_below_fcMR": int((coh["pc_disc10"] < coh["fc_MR"]).sum()),
    "ratio_pc_over_fcMR_quartiles": q(coh["pc_over_fcMR"]),
    "spearman_fcMR_vs_pc": spearman(coh["fc_MR"], coh["pc_random"]),
    "spearman_kappa_vs_k": spearman(coh["kappa"], coh["mean_degree"]),
    "note": "f_c(MR) = 1 - 1/(kappa-1) is the giant-component-vanishes point for a "
            "locally tree-like random graph with this degree sequence; f50 (component "
            "< 50%) must lie below it. Planar meshes have short loops so MR is an "
            "upper reference, not an exact prediction.",
}

# --------------------------------------------------------------------------
# R5 no hubs: weighted-removal penalty
# --------------------------------------------------------------------------
coh["penalty_rel"] = coh["attack_gap"] / coh["pc_random"]
out["R5_no_hubs"] = {
    "max_degree_le_5_all": bool((coh["max_degree_dd"] <= 5).all()),
    "degree_sd_max": float(coh["degree_sd"].max()),
    "attack_gap_quartiles": q(coh["attack_gap"]),
    "penalty_rel_quartiles": q(coh["penalty_rel"]),
    "spearman_gap_vs_loop_fraction": spearman(coh["attack_gap"], coh["loop_fraction_nonbridge"]),
    "spearman_gap_vs_degree_sd": spearman(coh["attack_gap"], coh["degree_sd"]),
    "spearman_gap_vs_p1": spearman(coh["attack_gap"], coh["p1"]),
    "spearman_relpenalty_vs_k": spearman(coh["penalty_rel"], coh["mean_degree"]),
}

# --------------------------------------------------------------------------
# R6 loop span (random edge control, n=27, equal edge counts)
# --------------------------------------------------------------------------
e = edge.dropna(subset=["d_delaunay", "d_rand_del", "d_rand_any"]).copy()
e["dk"] = e["k_delaunay"] - e["k_current"]
for c in ("d_delaunay", "d_rand_del", "d_rand_any"):
    e[c + "_per_k"] = e[c] / e["dk"]
w1 = stats.wilcoxon(e["d_delaunay"], e["d_rand_del"])
w2 = stats.wilcoxon(e["d_rand_del"], e["d_rand_any"])
out["R6_loop_span"] = {
    "n": int(len(e)),
    "median_gain": {"shortest_planar": float(e["d_delaunay"].median()),
                    "random_planar": float(e["d_rand_del"].median()),
                    "random_nonplanar": float(e["d_rand_any"].median())},
    "median_gain_per_unit_k": {"shortest_planar": float(e["d_delaunay_per_k"].median()),
                               "random_planar": float(e["d_rand_del_per_k"].median()),
                               "random_nonplanar": float(e["d_rand_any_per_k"].median())},
    "ratio_random_planar_to_shortest": float(e["d_rand_del"].median() / e["d_delaunay"].median()),
    "ratio_nonplanar_to_shortest": float(e["d_rand_any"].median() / e["d_delaunay"].median()),
    "n_shortest_lt_random_planar": int((e["d_delaunay"] < e["d_rand_del"]).sum()),
    "n_random_planar_lt_nonplanar": int((e["d_rand_del"] < e["d_rand_any"]).sum()),
    "wilcoxon_shortest_vs_random_planar_p": float(w1.pvalue),
    "wilcoxon_random_planar_vs_nonplanar_p": float(w2.pvalue),
}

# --------------------------------------------------------------------------
# R7 diminishing returns (enhancement cohort)
# --------------------------------------------------------------------------
en = enh.copy()
en["headroom"] = (K_CEILING - en["mean_degree"]).clip(lower=0)
fit_h = ols(en[["headroom"]].to_numpy(), en["delta_pc"].to_numpy())
# slope through the origin
h = en["headroom"].to_numpy(); d = en["delta_pc"].to_numpy()
slope0 = float((h * d).sum() / (h * h).sum())
out["R7_diminishing_returns"] = {
    "n": int(len(en)),
    "spearman_delta_vs_k0": spearman(en["mean_degree"], en["delta_pc"]),
    "spearman_delta_vs_headroom": spearman(en["headroom"], en["delta_pc"]),
    "ols_delta_on_headroom": fit_h,
    "slope_through_origin": slope0,
    "n_zero_headroom": int((en["headroom"] == 0).sum()),
    "n_zero_gain": int((en["delta_pc"] == 0).sum()),
    "gain_per_unit_k_added_median": float((en.loc[en["headroom"] > 0, "delta_pc"]
                                           / en.loc[en["headroom"] > 0, "headroom"]).median()),
    "cross_sectional_slope_per_unit_k": fit_k["beta"][1],
}

# --------------------------------------------------------------------------
# R8 locality
# --------------------------------------------------------------------------
coh["D_tertile"] = pd.qcut(coh["D"], 3, labels=["low", "mid", "high"])
tert = coh.groupby("D_tertile", observed=True).agg(
    n=("name", "size"), D_median=("D", "median"), pc_median=("pc_random", "median"),
    disc1_median=("pc_disc1", "median"), disc10_median=("pc_disc10", "median"))
out["R8_locality"] = {
    "median_random": float(coh["pc_random"].median()),
    "median_disc1": float(coh["pc_disc1"].median()),
    "median_disc10": float(coh["pc_disc10"].median()),
    "ratio_disc1": float(coh["pc_disc1"].median() / coh["pc_random"].median()),
    "ratio_disc10": float(coh["pc_disc10"].median() / coh["pc_random"].median()),
    "n_disc1_ge_0.45": int((coh["pc_disc1"] >= 0.45).sum()),
    "disc1_range": [float(coh["pc_disc1"].min()), float(coh["pc_disc1"].max())],
    "spearman_disc1_vs_k": spearman(coh["mean_degree"], coh["pc_disc1"]),
    "spearman_disc10_vs_k": spearman(coh["mean_degree"], coh["pc_disc10"]),
    "spearman_disc1_vs_D": spearman(coh["D"], coh["pc_disc1"]),
    "spearman_disc10_vs_D": spearman(coh["D"], coh["pc_disc10"]),
    "partial_disc10_vs_D_given_logN": partial_spearman(coh["D"], coh["pc_disc10"], np.log(coh["n_nodes"])),
    "spearman_disc10_vs_logN": spearman(np.log(coh["n_nodes"]), coh["pc_disc10"]),
    "by_D_tertile": tert.reset_index().to_dict(orient="records"),
}

# --------------------------------------------------------------------------
# R9 geometry indifference
# --------------------------------------------------------------------------
logN = np.log(coh["n_nodes"].to_numpy(float))
geo = {}
for col, label in [("geom_branch_angle_deg", "branch_angle_graph_deg"),
                   ("theta_daughters_median_deg", "branch_angle_native_deg"),
                   ("geom_murray_exponent", "murray_exponent"),
                   ("geom_daughter_symmetry", "daughter_symmetry"),
                   ("geom_length_ratio", "length_ratio"),
                   ("mean_vein_length", "mean_vein_length_mm"),
                   ("mean_radius", "mean_radius_mm"),
                   ("areole_median_area_mm2", "areole_median_area_mm2"),
                   ("areole_elongation_median", "areole_elongation"),
                   ("areole_circularity_median", "areole_circularity"),
                   ("areole_eccentricity_median", "areole_eccentricity")]:
    geo[label] = {
        "quartiles": q(coh[col]),
        "spearman_vs_pc": spearman(coh[col], coh["pc_random"]),
        "partial_vs_pc_given_k": partial_spearman(coh[col], coh["pc_random"], coh["mean_degree"]),
        "partial_vs_pc_given_k_D_logN": partial_spearman_multi(
            coh[col], coh["pc_random"], [coh["mean_degree"], coh["D"], logN]),
        "partial_vs_pc_given_k_core": partial_spearman_multi(
            coh[col], coh["pc_random"], [coh["mean_degree"], coh["core_frac"]]),
        "partial_vs_pc_given_kcore": partial_spearman(coh[col], coh["pc_random"], coh["k_core"]),
        "partial_vs_pc_given_kcore_D_logN": partial_spearman_multi(
            coh[col], coh["pc_random"], [coh["k_core"], coh["D"], logN]),
        "spearman_vs_k": spearman(coh[col], coh["mean_degree"]),
        "spearman_vs_kcore": spearman(coh[col], coh["k_core"]),
        "spearman_vs_core_frac": spearman(coh[col], coh["core_frac"]),
        "spearman_vs_D": spearman(coh[col], coh["D"]),
        "spearman_vs_logN": spearman(coh[col], logN),
    }
out["R9_geometry"] = geo

# --------------------------------------------------------------------------
# R10 the looped core: hanging trees are dead weight
# --------------------------------------------------------------------------
fit_core = ols(np.column_stack([km2, coh["core_frac"]]), pc)
fit_kcore = ols((coh["k_core"] - 2).to_numpy()[:, None], pc)
fit_kcore_D = ols(np.column_stack([coh["k_core"] - 2, coh["D"] - 1.5]), pc)
fit_Lcore = ols(coh[["L_core"]].to_numpy(), pc)
out["R10b_core_density"] = {
    "identity": "k_core = 2 + (<k> - 2)/c  and  L_core = L/c  (all loops live in the core)",
    "k_core_quartiles": q(coh["k_core"]),
    "k_core_range": [float(coh["k_core"].min()), float(coh["k_core"].max())],
    "L_core_quartiles": q(coh["L_core"]),
    "spearman_kcore_vs_pc": spearman(coh["k_core"], coh["pc_random"]),
    "spearman_Lcore_vs_pc": spearman(coh["L_core"], coh["pc_random"]),
    "spearman_k_vs_pc": spearman(coh["mean_degree"], coh["pc_random"]),
    "spearman_kcore_vs_k": spearman(coh["k_core"], coh["mean_degree"]),
    "partial_kcore_vs_pc_given_k": partial_spearman(coh["k_core"], coh["pc_random"], coh["mean_degree"]),
    "partial_k_vs_pc_given_kcore": partial_spearman(coh["mean_degree"], coh["pc_random"], coh["k_core"]),
    "partial_kcore_vs_pc_given_D_logN": partial_spearman_multi(coh["k_core"], coh["pc_random"], [coh["D"], logN]),
    "partial_k_vs_pc_given_D_logN": partial_spearman_multi(coh["mean_degree"], coh["pc_random"], [coh["D"], logN]),
    "partial_D_vs_pc_given_kcore": partial_spearman(coh["D"], coh["pc_random"], coh["k_core"]),
    "partial_D_vs_pc_given_kcore_logN": partial_spearman_multi(coh["D"], coh["pc_random"], [coh["k_core"], logN]),
    "ols_pc_on_(kcore-2)": fit_kcore,
    "ols_pc_on_(kcore-2)_and_(D-1.5)": fit_kcore_D,
    "ols_pc_on_Lcore": fit_Lcore,
    "spearman_degree_pc_vs_kcore": spearman(coh["k_core"], coh["pc_degree"]),
    "spearman_degree_pc_vs_k": spearman(coh["mean_degree"], coh["pc_degree"]),
    "spearman_source_pc_vs_kcore": spearman(coh["k_core"], coh["pc_source"]),
    "spearman_source_pc_vs_k": spearman(coh["mean_degree"], coh["pc_source"]),
    "spearman_disc10_vs_kcore": spearman(coh["k_core"], coh["pc_disc10"]),
}
fit_core_only = ols(coh[["core_frac"]].to_numpy(), pc)
fit_core_D = ols(np.column_stack([km2, coh["core_frac"], coh["D"] - 1.5]), pc)
coh["core_resid_vs_t"] = coh["core_frac"] - (1 - coh["p1"])
out["R10_looped_core"] = {
    "core_frac_quartiles": q(coh["core_frac"]),
    "core_frac_range": [float(coh["core_frac"].min()), float(coh["core_frac"].max())],
    "hanging_frac_quartiles": q(coh["hanging_frac"]),
    "mean_hanging_tree_size_quartiles": q(coh["mean_hanging_tree_size"]),
    "mean_hanging_tree_size_range": [float(coh["mean_hanging_tree_size"].min()),
                                     float(coh["mean_hanging_tree_size"].max())],
    "prune_rounds_max": int(coh["prune_rounds"].max()),
    "spearman_core_vs_pc": spearman(coh["core_frac"], coh["pc_random"]),
    "spearman_core_vs_k": spearman(coh["core_frac"], coh["mean_degree"]),
    "spearman_core_vs_t": spearman(coh["core_frac"], coh["p1"]),
    "spearman_treesize_vs_pc": spearman(coh["mean_hanging_tree_size"], coh["pc_random"]),
    "spearman_treesize_vs_k": spearman(coh["mean_hanging_tree_size"], coh["mean_degree"]),
    "partial_core_vs_pc_given_k": partial_spearman(coh["core_frac"], coh["pc_random"], coh["mean_degree"]),
    "partial_core_vs_pc_given_k_D_logN": partial_spearman_multi(
        coh["core_frac"], coh["pc_random"], [coh["mean_degree"], coh["D"], logN]),
    "partial_treesize_vs_pc_given_k": partial_spearman(coh["mean_hanging_tree_size"], coh["pc_random"], coh["mean_degree"]),
    "partial_treesize_vs_pc_given_k_D_logN": partial_spearman_multi(
        coh["mean_hanging_tree_size"], coh["pc_random"], [coh["mean_degree"], coh["D"], logN]),
    "partial_k_vs_pc_given_core": partial_spearman(coh["mean_degree"], coh["pc_random"], coh["core_frac"]),
    "partial_D_vs_pc_given_k_core": partial_spearman_multi(coh["D"], coh["pc_random"], [coh["mean_degree"], coh["core_frac"]]),
    "ols_pc_on_core_only": fit_core_only,
    "ols_pc_on_(k-2)_and_core": fit_core,
    "ols_pc_on_(k-2)_core_(D-1.5)": fit_core_D,
    "core_minus_(1-t)_median": float(coh["core_resid_vs_t"].median()),
    "core_minus_(1-t)_quartiles": q(coh["core_resid_vs_t"]),
    "spearman_disc10_vs_core": spearman(coh["core_frac"], coh["pc_disc10"]),
    "spearman_disc1_vs_core": spearman(coh["core_frac"], coh["pc_disc1"]),
    "note": "2-core = what remains after repeatedly deleting degree<=1 nodes; every "
            "node outside it hangs from the core through a single vein and is lost "
            "whenever that vein's junction is removed.",
}

# --------------------------------------------------------------------------
# R11 transfer test: does the core-density law, fitted on REAL leaves, hold on
# the SYNTHETIC grid (different generator, different sizes, same engine)?
# The 42 grid networks are regenerated deterministically (seeded) and only their
# 2-core is measured; the archived p_c values are reused untouched.
# --------------------------------------------------------------------------
import config  # noqa: E402
from holoparasitic import network, calibrate as cal  # noqa: E402

GRID_CACHE = DATA / "design_rules_grid_core.csv"
if GRID_CACHE.exists():
    gcore = pd.read_csv(GRID_CACHE)
else:
    t0 = time.time()
    grows = []
    for idx, (params, md_req, gen) in enumerate(cal.grid_params(config.SWEEP_MEAN_DEGREES,
                                                                 config.SWEEP_GENERATIONS)):
        G = network.generate(params)
        N, E = G.number_of_nodes(), G.number_of_edges()
        core = nx.k_core(G, 2)
        c = core.number_of_nodes() / N
        pruned = N - core.number_of_nodes()
        att = sum(1 for u, v in G.edges if (u in core) != (v in core))
        p1 = sum(1 for _, d in G.degree() if d == 1) / N
        grows.append({"idx": idx, "N_regen": N, "E_regen": E, "k_regen": 2 * E / N,
                      "p1": p1, "core_frac": c, "hanging_frac": pruned / N,
                      "mean_hanging_tree_size": (pruned / att) if att else 0.0})
        print(f"  grid {idx:2d} gen={gen} N={N:6d} k={2*E/N:.3f} core={c:.3f}")
    gcore = pd.DataFrame(grows)
    gcore.to_csv(GRID_CACHE, index=False)
    print(f"grid cores: {time.time()-t0:.0f}s (cached to {GRID_CACHE.name})")

gg = grid.merge(gcore, on="idx", how="inner")
assert np.allclose(gg["N"], gg["N_regen"]) and np.allclose(gg["mean_degree"], gg["k_regen"], atol=2e-3), \
    "regenerated grid does not match the archived grid"
gg["k_core"] = 2 + (gg["mean_degree"] - 2) / gg["core_frac"]
gg_in = gg[gg["mean_degree"] <= coh["mean_degree"].max()]
fit_g_kcore = ols((gg["k_core"] - 2).to_numpy()[:, None], gg["pc_random"].to_numpy())
fit_g_kcore_in = ols((gg_in["k_core"] - 2).to_numpy()[:, None], gg_in["pc_random"].to_numpy())
fit_g_kcore_D = ols(np.column_stack([gg["k_core"] - 2, gg["D"] - 1.5]), gg["pc_random"].to_numpy())
# apply the REAL-leaf law (slope through origin from the cohort) to the grid
xr = (coh["k_core"] - 2).to_numpy(); yr = pc
law_slope = float((xr * yr).sum() / (xr * xr).sum())
xg = (gg["k_core"] - 2).to_numpy(); yg = gg["pc_random"].to_numpy()
pred = law_slope * xg
resid_g = yg - pred
out["R11_transfer_test"] = {
    "n_grid": int(len(gg)), "n_grid_inrange": int(len(gg_in)),
    "grid_core_frac_range": [float(gg["core_frac"].min()), float(gg["core_frac"].max())],
    "grid_k_core_range": [float(gg["k_core"].min()), float(gg["k_core"].max())],
    "grid_p1_range": [float(gg["p1"].min()), float(gg["p1"].max())],
    "grid_identity_k_eq_3_minus_2t_max_abs_resid": float((gg["mean_degree"] - (3 - 2 * gg["p1"])).abs().max()),
    "spearman_kcore_vs_pc_grid": spearman(gg["k_core"], gg["pc_random"]),
    "spearman_k_vs_pc_grid": spearman(gg["mean_degree"], gg["pc_random"]),
    "ols_grid_pc_on_(kcore-2)": fit_g_kcore,
    "ols_grid_inrange_pc_on_(kcore-2)": fit_g_kcore_in,
    "ols_grid_pc_on_(kcore-2)_and_(D-1.5)": fit_g_kcore_D,
    "real_law_slope_through_origin": law_slope,
    "real_law_applied_to_grid": {
        "rmse": float(np.sqrt((resid_g ** 2).mean())),
        "median_resid": float(np.median(resid_g)),
        "spearman_pred_vs_measured": spearman(pred, yg),
        "pearson_pred_vs_measured": float(stats.pearsonr(pred, yg)[0]),
        "n_within_0.03": int((np.abs(resid_g) <= 0.03).sum()),
        "n_within_0.05": int((np.abs(resid_g) <= 0.05).sum()),
    },
    "real_cohort_law_fit": {
        "rmse": float(np.sqrt(((yr - law_slope * xr) ** 2).mean())),
        "R2_through_origin": float(1 - ((yr - law_slope * xr) ** 2).sum() / ((yr - yr.mean()) ** 2).sum()),
        "spearman_pred_vs_measured": spearman(law_slope * xr, yr),
    },
    "note": "law fitted on the 100 real leaves (f50 = s * (k_core - 2), no intercept) and "
            "applied unchanged to the 42 synthetic grid networks (N 511-32,767).",
}
gg[["idx", "N", "mean_degree", "D", "pc_random", "pc_degree", "p1", "core_frac", "k_core"]].to_csv(
    DATA / "design_rules_grid.csv", index=False)

# --------------------------------------------------------------------------
# worked example: read one leaf with the rules
# --------------------------------------------------------------------------
def predict(k):
    return fit_k["beta"][0] + fit_k["beta"][1] * (k - 2)

examples = []
for nm in ["Chl_spi", "Abe_mex", "Cis_ant", "Aex_pun"]:
    r = coh[coh["name"] == nm]
    if r.empty:
        continue
    r = r.iloc[0]
    examples.append({
        "name": nm, "N": int(r["n_nodes"]), "t_free_endings": float(r["p1"]),
        "k_measured": float(r["mean_degree"]), "k_from_t": float(3 - 2 * r["p1"]),
        "loops_per_node": float(r["L_cycle_rank_per_node"]),
        "core_frac": float(r["core_frac"]),
        "mean_hanging_tree_size": float(r["mean_hanging_tree_size"]),
        "pc_predicted_R3": float(predict(r["mean_degree"])),
        "pc_predicted_R10": float(fit_core["beta"][0] + fit_core["beta"][1] * (r["mean_degree"] - 2)
                                  + fit_core["beta"][2] * r["core_frac"]),
        "pc_measured": float(r["pc_random"]), "fc_MR": float(r["fc_MR"]),
        "pc_disc1": float(r["pc_disc1"]),
        "headroom_to_ceiling": float(max(K_CEILING - r["mean_degree"], 0)),
        "delta_pc_measured": float(r["delta_pc"]) if np.isfinite(r["delta_pc"]) else None,
        "delta_pc_predicted_R7": float(slope0 * max(K_CEILING - r["mean_degree"], 0)),
    })
out["worked_examples"] = examples

# --------------------------------------------------------------------------
# save
# --------------------------------------------------------------------------
keep_cols = ["name", "n_nodes", "n_edges", "mean_degree", "degree_sd", "D", "grade",
             "p1", "p2", "p3", "p4", "p5plus", "max_degree_dd", "k_pred_from_t",
             "L_cycle_rank_per_node", "core_frac", "hanging_frac", "n_hanging_trees",
             "mean_hanging_tree_size", "k_core", "L_core", "areole_median_area_mm2",
             "areole_count", "areole_elongation_median", "areole_circularity_median",
             "kappa", "fc_MR", "pc_random", "pc_degree",
             "attack_gap", "pc_disc1", "pc_disc10", "pc_source", "loop_fraction_nonbridge",
             "theta_daughters_median_deg", "geom_branch_angle_deg", "geom_murray_exponent",
             "geom_daughter_symmetry", "geom_length_ratio", "k_suggested", "delta_pc"]
coh[keep_cols].to_csv(DATA / "design_rules_perleaf.csv", index=False)


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


(DATA / "design_rules.json").write_text(json.dumps(_clean(out), indent=2))

# --------------------------------------------------------------------------
# print summary
# --------------------------------------------------------------------------
print("\n=== R1 bounds ===")
print(json.dumps(_clean(out["R1_bounds"]), indent=1))
print("\n=== R2 free endings ===")
print(json.dumps(_clean(out["R2_free_endings"]), indent=1))
print("\n=== R3 tolerance law ===")
print(" cohort  pc = %.4f + %.4f (k-2)   R2=%.3f  se=%.4f" % (
    fit_k["beta"][0], fit_k["beta"][1], fit_k["R2"], fit_k["se"][1]))
print(" cohort  pc = %.4f + %.4f (k-2) + %.4f (D-1.5)   R2=%.3f" % (
    fit_kD["beta"][0], fit_kD["beta"][1], fit_kD["beta"][2], fit_kD["R2"]))
print(" cohort  pc = %.4f + %.4f t   R2=%.3f" % (fit_t["beta"][0], fit_t["beta"][1], fit_t["R2"]))
print(" synth in-range (n=%d)  pc = %.4f + %.4f (k-2)   R2=%.3f" % (
    len(g_in), fit_g["beta"][0], fit_g["beta"][1], fit_g["R2"]))
print(" synth in-range  pc = %.4f + %.4f (k-2) + %.4f (D-1.5)   R2=%.3f" % (
    fit_gD["beta"][0], fit_gD["beta"][1], fit_gD["beta"][2], fit_gD["R2"]))
print(quart.to_string())
print("\n=== R4 Molloy-Reed ===")
print(json.dumps(_clean(out["R4_molloy_reed"]), indent=1))
print("\n=== R5 no hubs ===")
print(json.dumps(_clean(out["R5_no_hubs"]), indent=1))
print("\n=== R6 loop span ===")
print(json.dumps(_clean(out["R6_loop_span"]), indent=1))
print("\n=== R7 diminishing ===")
print(json.dumps(_clean(out["R7_diminishing_returns"]), indent=1))
print("\n=== R8 locality ===")
print(json.dumps(_clean(out["R8_locality"]), indent=1))
print("\n=== R9 geometry ===")
for lab, g in out["R9_geometry"].items():
    print(" %-26s rho=%+.3f  |k=%+.3f  |k,D,N=%+.3f  |k,core=%+.3f  |kcore=%+.3f  |kcore,D,N=%+.3f   vs k=%+.3f kcore=%+.3f D=%+.3f N=%+.3f" % (
        lab, g["spearman_vs_pc"][0], g["partial_vs_pc_given_k"][0],
        g["partial_vs_pc_given_k_D_logN"][0], g["partial_vs_pc_given_k_core"][0],
        g["partial_vs_pc_given_kcore"][0], g["partial_vs_pc_given_kcore_D_logN"][0],
        g["spearman_vs_k"][0], g["spearman_vs_kcore"][0], g["spearman_vs_D"][0], g["spearman_vs_logN"][0]))
print("\n=== R10 looped core ===")
print(json.dumps(_clean(out["R10_looped_core"]), indent=1))
print("\n=== R10b core density ===")
print(json.dumps(_clean(out["R10b_core_density"]), indent=1))
print("\n=== R11 transfer test ===")
print(json.dumps(_clean(out["R11_transfer_test"]), indent=1))
print("\n=== worked examples ===")
print(json.dumps(_clean(examples), indent=1))
print("\nwrote data/design_rules.json, data/design_rules_perleaf.csv")
