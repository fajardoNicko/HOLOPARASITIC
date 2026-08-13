# -*- coding: utf-8 -*-
r"""
run_synthetic_grid.py -- Phase-2 causal complement to the real-cohort result.

The real cohort (run_cohort_percolation.py) found that <k> and D each independently
predict p_c, but <k> and D could not be *intervened* on -- they are whatever each
species happens to have. Here we GENERATE a 2D grid of synthetic networks that all
share the cohort-calibrated branching geometry but vary <k> (reticulation) and D
(generations) on near-orthogonal axes, run the SAME percolation engine, and regress
p_c on the MEASURED <k> and D. Because the axes are manipulated, this is the causal
statement the observational cohort regression cannot make.

Attack modes match the real cohort: random + degree-targeted.
Incremental, resumable save to data/synthetic_grid_pc.csv.

Run:  PYTHONIOENCODING=utf-8 python scripts/run_synthetic_grid.py
      python scripts/run_synthetic_grid.py --analyze-only
ASCII-only stdout (Windows cp1252 safety).
"""
import os
import sys
import csv
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import network, fractal, percolation, calibrate as cal

CSV = os.path.join(ROOT, "data", "synthetic_grid_pc.csv")
ANALYSIS = os.path.join(ROOT, "data", "synthetic_grid_analysis.json")

FIELDS = ["idx", "req_mean_degree", "generations", "N", "E",
          "mean_degree", "D", "loop_fraction", "pc_random", "pc_degree", "seconds"]

# trial budget per (network, mode): 40 densities x 80 trials = 3200
PP_RANDOM = config.PercolationParams(n_densities=40, n_trials=3200, mode="random")
PP_TARGET = config.PercolationParams(n_densities=40, n_trials=3200, mode="targeted")


def measure(G):
    N = G.number_of_nodes()
    E = G.number_of_edges()
    k = 2.0 * E / N if N else 0.0
    loops = sum(1 for *_, d in G.edges(data=True)
                if d.get("kind") == "anastomosis")
    lf = loops / E if E else 0.0
    D = fractal.fractal_dimension(G)
    return N, E, k, D, lf


def load_done():
    if not os.path.exists(CSV):
        return {}
    done = {}
    with open(CSV, newline="") as f:
        for r in csv.DictReader(f):
            done[int(r["idx"])] = r
    return done


def append_row(row):
    exists = os.path.exists(CSV)
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        w.writerow(row)


def run():
    grid = cal.grid_params(config.SWEEP_MEAN_DEGREES, config.SWEEP_GENERATIONS)
    done = load_done()
    print("grid cells: %d  already done: %d" % (len(grid), len(done)))
    for idx, (params, md_req, gen) in enumerate(grid):
        if idx in done:
            continue
        t0 = time.time()
        G = network.generate(params)
        N, E, k, D, lf = measure(G)
        # random attack
        r_rand = percolation.find_pc(G, PP_RANDOM, rho_max=1.0)
        # degree-targeted attack: pass explicit degree weights (else 'targeted'
        # defaults to betweenness, which is infeasible on the deep-gen networks)
        _, nodes = network.to_csr(G)
        w_deg = percolation.importance_weights(G, nodes, metric="degree")
        r_deg = percolation.find_pc(G, PP_TARGET, weights=w_deg, rho_max=1.0)
        row = {
            "idx": idx, "req_mean_degree": round(md_req, 3), "generations": gen,
            "N": N, "E": E, "mean_degree": round(k, 4), "D": round(D, 4),
            "loop_fraction": round(lf, 4),
            "pc_random": round(float(r_rand["p_c"]), 5),
            "pc_degree": round(float(r_deg["p_c"]), 5),
            "seconds": round(time.time() - t0, 1),
        }
        append_row(row)
        print("[%2d/%2d] k=%.2f D=%.3f  N=%d  pc_rand=%.3f pc_deg=%.3f  (%.1fs)"
              % (idx + 1, len(grid), k, D, N, row["pc_random"],
                 row["pc_degree"], row["seconds"]))
    print("grid run complete ->", os.path.relpath(CSV, ROOT))


# ---------------------------------------------------------------- analysis
def _partial_corr(a, b, c):
    """Partial correlation of a,b controlling for c (residual method)."""
    a, b, c = map(lambda v: np.asarray(v, float), (a, b, c))
    def resid(y, x):
        A = np.vstack([np.ones_like(x), x]).T
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        return y - A @ beta
    ra, rb = resid(a, c), resid(b, c)
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def _ols(y, X):
    """OLS with intercept; returns coefs, R2. X columns = predictors."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ beta
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
    return beta.tolist(), r2


def analyze():
    rows = list(csv.DictReader(open(CSV, newline="")))
    def col(name, cast=float):
        return [cast(r[name]) for r in rows]
    k = col("mean_degree"); D = col("D")
    out = {"n_cells": len(rows),
           "mean_degree_range": [min(k), max(k)],
           "D_range": [min(D), max(D)],
           "corr_k_D": float(np.corrcoef(k, D)[0, 1])}
    for mode in ("pc_random", "pc_degree"):
        pc = col(mode)
        # drop NaN rows for this mode
        m = [i for i, v in enumerate(pc) if np.isfinite(v)]
        kk = [k[i] for i in m]; DD = [D[i] for i in m]; pp = [pc[i] for i in m]
        beta, r2 = _ols(pp, np.column_stack([kk, DD]))
        out[mode] = {
            "n": len(m),
            "spearman_k": float(_spearman(kk, pp)),
            "spearman_D": float(_spearman(DD, pp)),
            "partial_r_pc_k_given_D": _partial_corr(pp, kk, DD),
            "partial_r_pc_D_given_k": _partial_corr(pp, DD, kk),
            "ols_intercept": beta[0], "ols_beta_k": beta[1],
            "ols_beta_D": beta[2], "ols_R2": r2,
        }
    json.dump(out, open(ANALYSIS, "w"), indent=2)
    print(json.dumps(out, indent=2))
    print("analysis ->", os.path.relpath(ANALYSIS, ROOT))


def _spearman(x, y):
    from scipy.stats import spearmanr
    return spearmanr(x, y).statistic


if __name__ == "__main__":
    if "--analyze-only" not in sys.argv:
        run()
    analyze()
