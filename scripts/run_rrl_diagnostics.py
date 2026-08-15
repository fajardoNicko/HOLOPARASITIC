"""Diagnostics requested by the deep-RRL pass (see DEEP_RRL_EVIDENCE_PACK.md Part 0).

Every number marked [computed] in the evidence pack is produced here.
Reads only the archive; writes data/rrl_diagnostics.json.

    python scripts/run_rrl_diagnostics.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "analysis_master.csv"
GRID = ROOT / "data" / "synthetic_grid_pc.csv"
OUT = ROOT / "data" / "rrl_diagnostics.json"

# K_leaf validation figures live in results_verified.json; repeated here for the CI.
KLEAF_RHO = 0.1868
KLEAF_N = 93


def partial_spearman(x, y, z):
    """Spearman of x,y controlling z, via ranks residualised on the rank of z."""
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    r, p = stats.pearsonr(ex, ey)
    return float(r), float(p)


def rank_biserial(diff):
    """Matched-pairs rank-biserial correlation (Kerby 2014): (R+ - R-) / (R+ + R-)."""
    nz = diff[diff != 0]
    ranks = stats.rankdata(np.abs(nz))
    pos, neg = ranks[nz > 0].sum(), ranks[nz < 0].sum()
    return float((pos - neg) / (pos + neg))


def cliffs_delta(a, b):
    gt = sum((y > x) for x in a for y in b)
    lt = sum((y < x) for x in a for y in b)
    return float((gt - lt) / (len(a) * len(b)))


def standardised_ols(df):
    """p_c ~ z(mean_degree) + z(D), outcome z-scored. Returns betas, R2, F."""
    X = np.column_stack([np.ones(len(df)), stats.zscore(df.mean_degree), stats.zscore(df.D)])
    y = stats.zscore(df.pc_random)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    r2 = 1 - (resid**2).sum() / ((y - y.mean()) ** 2).sum()
    n, k = len(df), 2
    f = (r2 / k) / ((1 - r2) / (n - k - 1))
    return dict(n=n, beta_mean_degree=float(beta[1]), beta_D=float(beta[2]),
                dominance_ratio=float(abs(beta[1] / beta[2])), R2=float(r2), F=float(f))


def main() -> None:
    d = pd.read_csv(MASTER)
    P = d[d.in_percolation_cohort_100].copy()
    E = d[d.in_enhancement_cohort_105].copy()
    out: dict = {
        "_purpose": "diagnostics requested by the deep-RRL pass; see DEEP_RRL_EVIDENCE_PACK.md Part 0",
        "_generated_by": "scripts/run_rrl_diagnostics.py",
    }

    # --- 0.1 size confound -------------------------------------------------
    size = {"n": int(len(P)), "N_min": int(P.n_nodes.min()), "N_max": int(P.n_nodes.max())}
    for v in ("pc_random", "pc_degree", "mean_degree", "D", "loop_fraction_nonbridge"):
        r, p = stats.spearmanr(P.n_nodes, P[v])
        size[f"spearman_N_x_{v}"] = {"rho": round(float(r), 4), "p": float(p)}
    logN = np.log10(P.n_nodes)
    for v in ("mean_degree", "D", "loop_fraction_nonbridge"):
        r, p = partial_spearman(P[v], P.pc_random, logN)
        size[f"partial_spearman_pc_x_{v}_given_logN"] = {"rho": round(r, 4), "p": float(p)}
    size["reading"] = (
        "empirical p_c rises weakly with N (+0.232), the OPPOSITE sign to the fixed-architecture "
        "synthetic sweep, so the finite-size artefact does not propagate into the cohort; but D is "
        "rank-correlated with N at +0.880 and must be disclosed as partly a size readout"
    )
    out["size_confound"] = size

    # --- 0.2 enhancement: artefact or diminishing returns? -----------------
    fit = np.polyfit(E.mean_degree, E.delta_pc, 1)
    E = E.assign(resid_delta=E.delta_pc - np.polyval(fit, E.mean_degree))
    by_grade = {}
    for g in sorted(E.grade.dropna().unique()):
        s = E[E.grade == g]
        by_grade[str(g)] = {
            "n": int(len(s)),
            "median_delta_pc": round(float(s.delta_pc.median()), 5),
            "median_baseline_mean_degree": round(float(s.mean_degree.median()), 4),
            "pct_improved": round(float((s.delta_pc > 0).mean() * 100), 1),
            "median_residual_delta_given_baseline_k": round(float(s.resid_delta.median()), 5),
        }
    groups = [E.resid_delta[E.grade == g].values for g in sorted(E.grade.dropna().unique())
              if (E.grade == g).sum() > 1]
    H, ph = stats.kruskal(*groups)
    A = E[E.grade == "A"]
    npos, nneg = int((A.delta_pc > 0).sum()), int((A.delta_pc < 0).sum())
    rho_k, p_k = stats.spearmanr(E.mean_degree, E.delta_pc)
    out["enhancement_artefact_test"] = {
        "by_grade": by_grade,
        "spearman_baseline_k_x_delta": {"rho": round(float(rho_k), 4), "p": float(p_k)},
        "kruskal_residual_delta_by_grade": {"H": round(float(H), 3), "p": float(ph)},
        "grade_A": {
            "n": int(len(A)), "improved": npos, "unchanged": int((A.delta_pc == 0).sum()),
            "worsened": nneg,
            "sign_test_p": float(stats.binomtest(npos, npos + nneg, 0.5).pvalue),
            "wilcoxon_p": float(stats.wilcoxon(A.delta_pc, zero_method="wilcox").pvalue),
            "wilcoxon_pratt_p": float(stats.wilcoxon(A.delta_pc, zero_method="pratt").pvalue),
        },
        "reading": (
            "grade A starts at the HIGHEST baseline <k> and has the LARGEST positive residual gain, "
            "so the smaller raw grade-A effect is diminishing returns, not measurement recovery; "
            "13 of the 13 grade-A leaves that changed at all improved"
        ),
    }

    # --- 0.3 predictor orthogonality --------------------------------------
    r_kd, p_kd = stats.pearsonr(P.mean_degree, P.D)
    out["collinearity"] = {
        "pearson_meandegree_x_D": round(float(r_kd), 4),
        "p": float(p_kd),
        "VIF": round(float(1 / (1 - r_kd**2)), 4),
        "spearman_meandegree_x_D": round(float(stats.spearmanr(P.mean_degree, P.D)[0]), 4),
        "spearman_meandegree_x_loopfraction": round(
            float(stats.spearmanr(P.mean_degree, P.loop_fraction_nonbridge)[0]), 4),
        "pearson_meandegree_x_loopfraction": round(
            float(stats.pearsonr(P.mean_degree, P.loop_fraction_nonbridge)[0]), 4),
        "note": "loop fraction ~ 1 - 2/<k> for a connected planar graph, so 0.994 is the "
                "finite-V residual of a graph identity, not an empirical coincidence",
    }

    # --- 0.4 synthetic grid, full vs restricted to the empirical range -----
    g = pd.read_csv(GRID)
    emp_max_k = float(P.mean_degree.max())
    out["synthetic_grid_refit"] = {
        "empirical_max_mean_degree": round(emp_max_k, 4),
        "n_grid_cells_above_empirical_max": int((g.mean_degree > emp_max_k).sum()),
        "full": standardised_ols(g),
        "restricted_to_empirical_range": standardised_ols(g[g.mean_degree <= emp_max_k]),
        "grid_spearman_N_x_D": round(float(stats.spearmanr(g.N, g.D)[0]), 4),
        "note": "the D axis was realised by varying generations, so D and N are coupled in the "
                "grid too (rho 0.99); the grid decouples D from <k>, not from size",
    }

    # --- 0.5 effect sizes --------------------------------------------------
    diff = (P.pc_random - P.pc_degree).values
    dd = E.delta_pc.values
    q = P.assign(Q=pd.qcut(P.loop_fraction_nonbridge, 4, labels=[1, 2, 3, 4]))
    a, b = q[q.Q == 1].pc_random.values, q[q.Q == 4].pc_random.values
    U, pu = stats.mannwhitneyu(a, b, alternative="two-sided")
    out["effect_sizes"] = {
        "random_vs_degree": {
            "n": int(len(diff)),
            "wilcoxon_p": float(stats.wilcoxon(diff, zero_method="wilcox").pvalue),
            "rank_biserial_r": round(rank_biserial(diff), 4),
            "common_language_pct": round(float((diff > 0).mean() * 100), 1),
            "median_difference": round(float(np.median(diff)), 4),
        },
        "enhancement": {
            "n": int(len(dd)),
            "wilcoxon_pratt_p": float(stats.wilcoxon(dd, zero_method="pratt").pvalue),
            "wilcoxon_nonzero_p": float(stats.wilcoxon(dd[dd != 0], zero_method="wilcox").pvalue),
            "rank_biserial_r_nonzero": round(rank_biserial(dd), 4),
            "improved": int((dd > 0).sum()), "unchanged": int((dd == 0).sum()),
            "worsened": int((dd < 0).sum()),
            "median_delta_pc": round(float(np.median(dd)), 5),
        },
        "loop_quartiles_Q1_vs_Q4": {
            "n1": int(len(a)), "n2": int(len(b)), "U": float(U), "p": float(pu),
            "cliffs_delta": round(cliffs_delta(a, b), 4),
            "median_Q1": round(float(np.median(a)), 4), "median_Q4": round(float(np.median(b)), 4),
        },
    }

    # --- 0.6 K_leaf interval ----------------------------------------------
    z = np.arctanh(KLEAF_RHO)
    se = 1.03 / np.sqrt(KLEAF_N - 3)  # Bonett-Wright SE for Spearman
    out["kleaf_interval"] = {
        "rho": KLEAF_RHO, "n": KLEAF_N,
        "ci95": [round(float(np.tanh(z - 1.96 * se)), 3), round(float(np.tanh(z + 1.96 * se)), 3)],
        "reading": "underpowered, not null: compatible with anything from no relationship to a "
                   "moderate positive one",
    }

    # --- 0.7 dataset facts -------------------------------------------------
    out["dataset_facts"] = {
        "n_crop_windows": int((d.is_crop == True).sum()),  # noqa: E712
        "n_whole_leaves": int((d.is_crop == False).sum()),  # noqa: E712
        "quality_flag_combinations": {str(k): int(v) for k, v in d.quality.value_counts().items()},
        "leading_grade_counts": {str(k): int(v) for k, v in d.grade.value_counts().items()},
        "distinct_quality_letters_present": sorted(
            {c.strip() for q in d.quality.dropna() for c in str(q).split(",")}),
        "note": "the source deposit defines a SIX-tier A-F scale (A excellent; B >80% of veins "
                "correct; C fake minor veins; D damage <25% of leaf area; E <80% segmented; "
                "F damage >25%). The retained set spans A-D only. The grades are NON-ORDINAL: "
                "C inflates connectivity while B and E deflate it.",
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    for k in out:
        if not k.startswith("_"):
            print(f"  - {k}")


if __name__ == "__main__":
    main()
