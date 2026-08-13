# -*- coding: utf-8 -*-
r"""
run_scaling_mesh.py -- finite-size scaling + critical exponent beta on the
PROMOTED MESH hero (not the legacy knn generator that validate_stats.py TEST 2/3
still use). Answers the open question: is the planar leaf mesh in the mean-field
class (beta~1, like the long-cross-link knn network) or the 2-D percolation class
(beta = 5/36 ~ 0.139)?

f_c is located EMPIRICALLY (rho where the giant component vanishes), because the
analytical Molloy-Reed f_c assumes a locally tree-like network and is unreliable
for a short-loop planar mesh.

Output: data/scaling_mesh.json + figures/stat_beta_mesh.png
ASCII-only stdout.
"""
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.sparse.csgraph import connected_components

import config
from holoparasitic import network, fractal, percolation, calibrate as cal

FIG = config.PATHS.figures
OUT = os.path.join(ROOT, "data", "scaling_mesh.json")


def order_parameter(G, rho_grid, n_trials, seed=0):
    adj, _ = network.to_csr(G)
    n = adj.shape[0]
    rng = config.new_rng(seed)
    S = np.empty(len(rho_grid))
    for i, rho in enumerate(rho_grid):
        g = np.empty(n_trials)
        for t in range(n_trials):
            idx = np.flatnonzero(rng.random(n) > rho)
            if idx.size:
                sub = adj[idx][:, idx]
                _, lab = connected_components(sub, directed=False)
                g[t] = np.bincount(lab).max()
            else:
                g[t] = 0
        S[i] = g.mean() / n
    return S


def finite_size():
    out = []
    for g in (8, 9, 10, 11, 12):
        G = network.generate(cal.calibrated_base(generations=g))
        r = percolation.find_pc(G, config.PercolationParams(
            mode="random", n_trials=30_000, n_densities=40), with_ci=True)
        w = 4.394 / r["coef"] if r["coef"] else float("nan")
        row = {"N": r["n_nodes"], "D": round(fractal.fractal_dimension(G), 3),
               "p_c": round(float(r["p_c"]), 4),
               "ci95": [round(r["ci"]["ci95"][0], 4), round(r["ci"]["ci95"][1], 4)],
               "width_0.1_0.9": round(float(w), 4)}
        out.append(row)
        print("  N=%5d D=%.3f p_c=%.4f width=%.4f" %
              (row["N"], row["D"], row["p_c"], row["width_0.1_0.9"]))
    return out


def beta_exponent():
    G = network.generate(cal.calibrated_base(generations=12))   # N~8191
    N = G.number_of_nodes()
    deg = np.array([d for _, d in G.degree()], float)
    kappa = (deg ** 2).mean() / deg.mean()
    mr_fc = 1 - 1 / (kappa - 1)
    # locate f_c EMPIRICALLY: rho where S drops below 2%
    coarse = np.linspace(0.2, 0.75, 40)
    Sc = order_parameter(G, coarse, n_trials=400, seed=11)
    below = np.where(Sc < 0.02)[0]
    f_c = float(coarse[below[0]]) if below.size else mr_fc
    print("  N=%d kappa=%.3f  Molloy-Reed f_c=%.3f  EMPIRICAL f_c=%.3f"
          % (N, kappa, mr_fc, f_c))
    # fine order parameter just below empirical f_c
    rho_grid = np.linspace(max(0.05, f_c - 0.30), f_c - 0.01, 32)
    S = order_parameter(G, rho_grid, n_trials=3000, seed=13)
    t = f_c - rho_grid
    mask = (S > 0) & (t >= 0.03) & (t <= 0.18)
    beta, intercept, r_val, p_val, se = stats.linregress(
        np.log(t[mask]), np.log(S[mask]))
    print("  fitted beta = %.3f +/- %.3f  (log-log R2=%.4f, n=%d)"
          % (beta, se, r_val ** 2, mask.sum()))
    print("  mean-field beta=1.0 ; 2-D percolation beta=5/36=0.139")
    # plot
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.loglog(t[S > 0], S[S > 0], "o", color="#bbbbbb", label="all")
    ax.loglog(t[mask], S[mask], "o", color="#E4572E", label="fit window")
    xs = np.linspace(t[mask].min(), t[mask].max(), 50)
    ax.loglog(xs, np.exp(intercept) * xs ** beta, "-", color="black",
              label="beta=%.2f" % beta)
    ax.set_xlabel(r"$f_c - \rho$ (empirical $f_c$=%.2f)" % f_c)
    ax.set_ylabel("giant component fraction S")
    ax.set_title("MESH hero critical scaling (N=%d, beta=%.2f$\\pm$%.2f)"
                 % (N, beta, se))
    ax.legend(); ax.grid(alpha=.3, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "stat_beta_mesh.png"), dpi=150)
    plt.close(fig)
    return {"N": N, "kappa": round(float(kappa), 3),
            "molloy_reed_fc": round(float(mr_fc), 3),
            "empirical_fc": round(f_c, 3),
            "beta": round(float(beta), 3), "beta_se": round(float(se), 3),
            "loglog_R2": round(float(r_val ** 2), 4), "n_fit": int(mask.sum()),
            "meanfield_beta": 1.0, "twoD_beta": round(5 / 36, 3),
            "SE_from_meanfield": round(abs(beta - 1) / se, 1),
            "SE_from_2D": round(abs(beta - 5 / 36) / se, 1)}


def main():
    print("== finite-size scaling (mesh) ==")
    fs = finite_size()
    print("== critical exponent beta (mesh) ==")
    be = beta_exponent()
    result = {"generator": "calibrated planar mesh (calibrate.calibrated_base)",
              "finite_size": fs, "beta_test": be,
              "note": ("Compare to validate_stats.py which runs TEST2/3 on the "
                       "legacy knn defaults (mean-field). f_c located empirically "
                       "because Molloy-Reed assumes tree-like connectivity.")}
    json.dump(result, open(OUT, "w"), indent=2)
    print(json.dumps(be, indent=2))
    print("-> %s + figures/stat_beta_mesh.png" % os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
