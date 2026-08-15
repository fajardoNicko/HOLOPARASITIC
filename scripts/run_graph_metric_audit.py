# -*- coding: utf-8 -*-
r"""
run_graph_metric_audit.py -- P0/P1 audit of two structural claims.

(A) MEAN DEGREE vs LOOP FRACTION.
    The first-pass RRL asserted "loop fraction ~ 1 - 2/<k> for a connected planar
    graph, so their rho = 0.9945 is a graph identity". That is WRONG for the
    definition this project actually uses. characterize.py computes

        loop_fraction = (E - |bridges|) / E          [non-bridge edge fraction]

    whereas the identity 1 - 2/<k> describes the CYCLE-RANK fraction

        (E - N + c) / E                              [independent loops per edge]

    These are different quantities: a spanning-tree edge lying between two chords
    is a non-bridge but contributes no independent cycle. This script tests both
    against 1 - 2/<k> on all 120 traced leaves and on the 42-network synthetic
    grid, and quantifies how much loop fraction is free to vary at fixed <k>.

(B) TARGETED ATTACK: NOMINAL rho vs REALISED REMOVED FRACTION.
    percolation._trial_weighted removes node i with probability
    clip(rho * w_i, 0, 1) where w is mean-normalised. Because of the clip, the
    expected removed fraction is BELOW rho once rho * w_max > 1, and the more
    heavy-tailed the weights the earlier that bites. The reported targeted
    thresholds are therefore quoted on the nominal-rho axis, which is not the
    same axis as the random threshold. This script measures the discrepancy
    exactly on the hero mesh for degree and betweenness weights.

    python scripts/run_graph_metric_audit.py

Outputs data/graph_metric_audit.json.  ASCII-only stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import networkx as nx
from scipy import stats

import config
from holoparasitic import network, percolation

OUT = ROOT / "data" / "graph_metric_audit.json"
SPECIES_DIR = ROOT / "data" / "species"


def load_species() -> pd.DataFrame:
    rows = []
    for p in sorted(SPECIES_DIR.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        rows.append({k: d.get(k) for k in
                     ("name", "n_nodes", "n_edges", "n_components", "n_cycles",
                      "loop_fraction", "mean_degree", "degree_sd", "max_degree",
                      "D")})
    return pd.DataFrame(rows)


def audit_loop_fraction(df: pd.DataFrame, label: str) -> dict:
    k = df.mean_degree.values
    E = df.n_edges.values.astype(float)
    pred = 1.0 - 2.0 / k                       # cycle-rank identity
    cyc = df.n_cycles.values / E               # measured cycle-rank fraction
    lf = df.loop_fraction.values               # measured NON-BRIDGE fraction

    # how much can loop fraction move at fixed <k>? residual of a monotone fit
    order = np.argsort(k)
    sm = np.poly1d(np.polyfit(k, lf, 3))
    resid = lf - sm(k)

    return {
        "label": label,
        "n": int(len(df)),
        "cycle_rank_fraction_vs_identity": {
            "pearson_r": round(float(stats.pearsonr(cyc, pred)[0]), 8),
            "max_abs_difference": round(float(np.abs(cyc - pred).max()), 8),
            "mean_abs_difference": round(float(np.abs(cyc - pred).mean()), 8),
            "verdict": "EXACT identity up to the components correction",
        },
        "nonbridge_loop_fraction_vs_identity": {
            "pearson_r": round(float(stats.pearsonr(lf, pred)[0]), 5),
            "spearman_rho": round(float(stats.spearmanr(lf, pred)[0]), 5),
            "max_abs_difference": round(float(np.abs(lf - pred).max()), 5),
            "mean_abs_difference": round(float(np.abs(lf - pred).mean()), 5),
            "verdict": "NOT an identity -- differs by a large, systematic margin",
        },
        "nonbridge_vs_cycle_rank": {
            "mean_nonbridge": round(float(lf.mean()), 5),
            "mean_cycle_rank": round(float(cyc.mean()), 5),
            "ratio": round(float(lf.mean() / cyc.mean()), 3),
        },
        "loop_fraction_given_mean_degree": {
            "spearman_rho": round(float(stats.spearmanr(k, lf)[0]), 5),
            "pearson_r": round(float(stats.pearsonr(k, lf)[0]), 5),
            "cubic_fit_R2": round(float(1 - (resid ** 2).sum()
                                        / ((lf - lf.mean()) ** 2).sum()), 5),
            "residual_sd": round(float(resid.std(ddof=1)), 5),
            "residual_range": [round(float(resid.min()), 5),
                               round(float(resid.max()), 5)],
            "loop_fraction_range": [round(float(lf.min()), 4),
                                    round(float(lf.max()), 4)],
        },
    }


def audit_targeted_axis() -> dict:
    """Exact expected removed fraction vs nominal rho on the hero mesh."""
    G = network.generate()
    adj, nodes = network.to_csr(G)
    n = adj.shape[0]
    out = {"N": int(n)}
    for metric in ("degree", "betweenness"):
        w = percolation.importance_weights(G, nodes, metric=metric)
        rows = []
        for rho in np.linspace(0.0, 1.0, 51):
            p = np.clip(rho * w, 0.0, 1.0)
            rows.append({"nominal_rho": round(float(rho), 4),
                         "expected_removed_fraction": round(float(p.mean()), 5),
                         "fraction_of_nodes_clipped": round(
                             float((rho * w > 1.0).mean()), 5)})
        # what nominal rho is needed to realise the reported thresholds?
        nom = np.array([r["nominal_rho"] for r in rows])
        real = np.array([r["expected_removed_fraction"] for r in rows])
        out[metric] = {
            "weight_mean": round(float(w.mean()), 5),
            "weight_sd": round(float(w.std(ddof=1)), 5),
            "weight_max": round(float(w.max()), 4),
            "weight_gini": round(float(_gini(w)), 4),
            "n_distinct_weights": int(np.unique(np.round(w, 9)).size),
            "largest_tied_group_fraction": round(
                float(np.bincount(np.unique(np.round(w, 9),
                                            return_inverse=True)[1]).max() / n), 4),
            "curve": rows,
            "realised_at_nominal_0.20": round(
                float(np.interp(0.20, nom, real)), 5),
            "realised_at_nominal_0.2023": round(
                float(np.interp(0.2023, nom, real)), 5),
            "realised_at_nominal_0.1889": round(
                float(np.interp(0.1889, nom, real)), 5),
        }
    out["reading"] = (
        "the targeted modes are WEIGHTED STOCHASTIC removal (removal probability "
        "proportional to centrality), not rank-ordered deletion of the top-k "
        "nodes. Two consequences: (i) the 'initial vs recalculated centrality' "
        "literature does not apply, and Callaway et al. (2000)'s degree-dependent "
        "occupation formalism is the correct precedent; (ii) because the removal "
        "probability is clipped at 1, the nominal rho over-states the realised "
        "removed fraction for heavy-tailed weights, so targeted and random "
        "thresholds are not quoted on identical axes.")
    return out


def _gini(x):
    x = np.sort(np.asarray(x, float))
    n = x.size
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    out = {
        "_purpose": "graph-metric dependence and targeted-attack axis audit; "
                    "see SECOND_PASS_AUDIT.md Part VI",
        "_generated_by": "scripts/run_graph_metric_audit.py",
        "loop_fraction_definition_in_code": (
            "characterize.py: loop_fraction = (E - len(nx.bridges(G))) / E "
            "-- the NON-BRIDGE edge fraction"),
    }

    emp = load_species()
    out["empirical_120_leaves"] = audit_loop_fraction(emp, "traced leaves (120)")

    grid = pd.read_csv(ROOT / "data" / "synthetic_grid_pc.csv")
    grid = grid.assign(n_nodes=grid.N, n_edges=grid.E,
                       n_cycles=grid.E - grid.N + 1, n_components=1)
    out["synthetic_grid_42"] = audit_loop_fraction(grid, "synthetic grid (42)")

    out["targeted_attack_axis"] = audit_targeted_axis()

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    a = out["empirical_120_leaves"]
    print("=== (A) loop fraction vs mean degree, 120 traced leaves ===")
    print("  cycle-rank fraction vs 1-2/<k>:  r = %.8f, max|diff| = %.2e  -> %s"
          % (a["cycle_rank_fraction_vs_identity"]["pearson_r"],
             a["cycle_rank_fraction_vs_identity"]["max_abs_difference"],
             a["cycle_rank_fraction_vs_identity"]["verdict"]))
    print("  NON-BRIDGE loop fraction vs 1-2/<k>: r = %.4f, mean|diff| = %.4f -> %s"
          % (a["nonbridge_loop_fraction_vs_identity"]["pearson_r"],
             a["nonbridge_loop_fraction_vs_identity"]["mean_abs_difference"],
             a["nonbridge_loop_fraction_vs_identity"]["verdict"]))
    print("  mean non-bridge %.3f vs mean cycle-rank %.3f (ratio %.2f)"
          % (a["nonbridge_vs_cycle_rank"]["mean_nonbridge"],
             a["nonbridge_vs_cycle_rank"]["mean_cycle_rank"],
             a["nonbridge_vs_cycle_rank"]["ratio"]))
    g = a["loop_fraction_given_mean_degree"]
    print("  loop fraction | <k>: Spearman %.4f, cubic R2 %.4f, residual SD %.4f, "
          "residual range [%.3f, %.3f]"
          % (g["spearman_rho"], g["cubic_fit_R2"], g["residual_sd"],
             g["residual_range"][0], g["residual_range"][1]))

    print("\n=== (B) targeted attack: nominal rho vs realised removed fraction ===")
    t = out["targeted_attack_axis"]
    for m in ("degree", "betweenness"):
        d = t[m]
        print("  %-12s weight SD %.3f, max %.1f, Gini %.3f, distinct weights %d, "
              "largest tied group %.1f%% of nodes"
              % (m, d["weight_sd"], d["weight_max"], d["weight_gini"],
                 d["n_distinct_weights"], 100 * d["largest_tied_group_fraction"]))
        print("               nominal 0.2000 -> realised %.4f | "
              "nominal 0.2023 -> realised %.4f"
              % (d["realised_at_nominal_0.20"], d["realised_at_nominal_0.2023"]))
    print("\nwrote %s" % OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
