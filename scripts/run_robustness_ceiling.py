# -*- coding: utf-8 -*-
r"""
run_robustness_ceiling.py -- per-species robustness ceiling.

Uses the CAUSAL response surface p_c ~ <k> + D fitted on the synthetic grid
(run_synthetic_grid.py) to estimate, for each real cohort species, how much its
percolation threshold p_c could rise if its venation moved toward the reticulate
(high mean-degree) end of the BIOLOGICALLY OBSERVED range, holding its fractal
dimension fixed -- and, separately, the smaller gain from raising D.

This is a CONSTRAINED optimum, not "the ideal parasite-proof leaf":
  * <k> is capped at the cohort's 90th percentile (a real, observed reticulation
    level), never an unbounded mesh.
  * The gain is a first-order estimate from a linear model (R^2~0.89); it is a
    direction and a magnitude, not a designed network.
  * It ignores the trade-offs a real leaf pays for extra reticulation
    (construction cost, water-use efficiency) -- those bound how far one can go.

Output: data/robustness_ceiling.csv + data/robustness_ceiling_summary.json
ASCII-only stdout.
"""
import os
import sys
import csv
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

DATA = os.path.join(ROOT, "data")
GRID = os.path.join(DATA, "synthetic_grid_pc.csv")
COHORT = os.path.join(DATA, "cohort_pc.csv")
OUT = os.path.join(DATA, "robustness_ceiling.csv")
SUMMARY = os.path.join(DATA, "robustness_ceiling_summary.json")


def fit_surface():
    """OLS p_c ~ <k> + D on the synthetic grid (random attack)."""
    rows = list(csv.DictReader(open(GRID, newline="")))
    k = np.array([float(r["mean_degree"]) for r in rows])
    D = np.array([float(r["D"]) for r in rows])
    pc = np.array([float(r["pc_random"]) for r in rows])
    ok = np.isfinite(pc)
    A = np.column_stack([np.ones(ok.sum()), k[ok], D[ok]])
    beta, *_ = np.linalg.lstsq(A, pc[ok], rcond=None)
    yhat = A @ beta
    r2 = 1 - ((pc[ok] - yhat) ** 2).sum() / ((pc[ok] - pc[ok].mean()) ** 2).sum()
    return beta, float(r2)   # beta = [b0, b_k, b_D]


def predict(beta, k, D):
    return float(beta[0] + beta[1] * k + beta[2] * D)


def main():
    beta, r2 = fit_surface()
    print("surface: p_c = %.4f + %.4f*<k> + %.4f*D   (R2=%.3f)"
          % (beta[0], beta[1], beta[2], r2))

    rows = list(csv.DictReader(open(COHORT, newline="")))
    k = np.array([float(r["mean_degree"]) for r in rows])
    D = np.array([float(r["D"]) for r in rows])
    pc_meas = np.array([float(r["pc_random"]) for r in rows])

    k_cap = float(np.percentile(k, 90))   # observed reticulation ceiling
    D_cap = float(np.percentile(D, 90))
    print("observed caps: <k>_90=%.3f  D_90=%.3f" % (k_cap, D_cap))

    out_rows = []
    for i, r in enumerate(rows):
        ki, Di = k[i], D[i]
        pc_model_now = predict(beta, ki, Di)
        # raise reticulation to the observed ceiling, hold D
        pc_ceiling_k = predict(beta, max(ki, k_cap), Di)
        gain_k = pc_ceiling_k - pc_model_now
        # raise D to observed ceiling, hold <k>
        pc_ceiling_D = predict(beta, ki, max(Di, D_cap))
        gain_D = pc_ceiling_D - pc_model_now
        out_rows.append({
            "species": r["species"], "mean_degree": round(ki, 4), "D": round(Di, 4),
            "pc_measured": round(float(pc_meas[i]), 4),
            "pc_model_now": round(pc_model_now, 4),
            "pc_ceiling_reticulation": round(pc_ceiling_k, 4),
            "gain_from_reticulation": round(gain_k, 4),
            "gain_from_D": round(gain_D, 4),
            "dominant_lever": "reticulation" if gain_k >= gain_D else "fractal_D",
        })

    out_rows.sort(key=lambda d: d["gain_from_reticulation"], reverse=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    gains_k = np.array([d["gain_from_reticulation"] for d in out_rows])
    gains_D = np.array([d["gain_from_D"] for d in out_rows])
    summary = {
        "surface": {"intercept": beta[0], "beta_k": beta[1], "beta_D": beta[2],
                    "R2": r2},
        "caps": {"mean_degree_p90": k_cap, "D_p90": D_cap},
        "n_species": len(out_rows),
        "median_gain_reticulation": float(np.median(gains_k)),
        "max_gain_reticulation": float(gains_k.max()),
        "median_gain_D": float(np.median(gains_D)),
        "reticulation_is_dominant_lever_fraction":
            float(np.mean([d["dominant_lever"] == "reticulation" for d in out_rows])),
        "top5_headroom": out_rows[:5],
        "caveat": ("Constrained, first-order estimate from a linear response "
                   "surface (R^2~0.89); a direction+magnitude, not a designed "
                   "network; trade-offs (cost, efficiency) not modelled."),
    }
    json.dump(summary, open(SUMMARY, "w"), indent=2)
    print(json.dumps({k2: summary[k2] for k2 in
                      ("caps", "median_gain_reticulation", "max_gain_reticulation",
                       "median_gain_D", "reticulation_is_dominant_lever_fraction")},
                     indent=2))
    print("top-5 headroom species:",
          [(d["species"], d["gain_from_reticulation"]) for d in out_rows[:5]])
    print("-> %s  + summary" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
