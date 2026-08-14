r"""
run_finite_size_fixedD.py — a finite-size sweep in which the ARCHITECTURE IS
HELD FIXED, so that the size effect is not confounded with fractal dimension.

WHY THIS EXISTS
  `scripts/run_scaling_mesh.py` grows the network with the `generations` knob,
  which raises N and D together (N 511 -> 8191 while D 1.267 -> 1.741 in
  data/scaling_mesh.json). Because D is itself one of this study's predictors of
  p_c, the rise of p_c from .2531 to .2857 in that sweep cannot be attributed to
  size. This run separates the two: at every size, `length_ratio` is tuned until
  the MEASURED box-counting D hits a common target and `mesh_frac` is tuned until
  the MEASURED mean degree hits the cohort value. Only N then varies.

  With architecture fixed, a residual size trend is a genuine finite-size effect
  and a residual sharpening of the transition is genuine critical behaviour.

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_finite_size_fixedD.py
"""

import os
import sys
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
from holoparasitic import network, fractal, percolation, calibrate as cal

GENERATIONS = (9, 10, 11, 12, 13)     # N = 1023 ... 16383
D_TARGET = 1.3868                     # the hero network's measured D
K_TARGET = 2.4888                     # the hero network's measured mean degree
N_TRIALS = 40_000
N_DENSITIES = 50
SEED = 21


def _params(base, lr, mf):
    return config.NetworkParams(**{**base.__dict__,
                                   "length_ratio": lr, "mesh_frac": mf})


def _k_of(p):
    return network.summary(network.generate(p))["mean_degree"]


def _D_of(p):
    return fractal.fractal_dimension(network.generate(p))


def _bisect(f, lo, hi, target, tol, iters):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        v = f(mid)
        if abs(v - target) <= tol:
            return mid
        if v < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def tuned(generations):
    """Network at `generations` with measured D ~ D_TARGET and <k> ~ K_TARGET."""
    base = cal.calibrated_base(generations=generations)
    lr, mf = base.length_ratio, base.mesh_frac
    for _ in range(2):
        lr = _bisect(lambda x: _D_of(_params(base, x, mf)),
                     0.40, 1.45, D_TARGET, 0.005, 11)
        mf = _bisect(lambda x: _k_of(_params(base, lr, x)),
                     0.01, 0.40, K_TARGET, 0.004, 11)
    p = _params(base, lr, mf)
    G = network.generate(p)
    return G, p, network.summary(G)["mean_degree"], fractal.fractal_dimension(G)


def width_10_90(rhos, pcol):
    """Width of the 10%-90% collapse-probability window (transition sharpness)."""
    rhos = np.asarray(rhos, float)
    pcol = np.asarray(pcol, float)

    def cross(level):
        idx = np.where(pcol >= level)[0]
        if idx.size == 0 or idx[0] == 0:
            return np.nan
        i = idx[0]
        x0, x1 = rhos[i - 1], rhos[i]
        y0, y1 = pcol[i - 1], pcol[i]
        return x0 if y1 == y0 else x0 + (level - y0) * (x1 - x0) / (y1 - y0)

    return float(cross(0.9) - cross(0.1))


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    t0 = time.time()
    print("Finite-size sweep at FIXED architecture")
    print(f"  target D = {D_TARGET}, target <k> = {K_TARGET}, "
          f"{N_TRIALS:,} trials per size\n")

    pp = config.PercolationParams(mode="random", n_trials=N_TRIALS,
                                  n_densities=N_DENSITIES, seed=SEED)
    rows = []
    for g in GENERATIONS:
        t = time.time()
        G, p, k, D = tuned(g)
        print(f"  g={g}  N={G.number_of_nodes():>6}  <k>={k:.4f}  D={D:.4f}  "
              f"(length_ratio={p.length_ratio:.4f}, mesh_frac={p.mesh_frac:.4f})"
              f"  [tune {time.time() - t:.0f}s]", flush=True)
        t = time.time()
        res = percolation.find_pc(G, pp, with_ci=True)
        ci = res["ci"]["ci95"]
        w = width_10_90(res["rhos"], res["p_collapse"])
        rows.append({"generations": g, "N": G.number_of_nodes(),
                     "E": G.number_of_edges(), "mean_degree": round(k, 4),
                     "D": round(D, 4), "length_ratio": round(p.length_ratio, 4),
                     "mesh_frac": round(p.mesh_frac, 4),
                     "p_c": round(float(res["p_c"]), 4),
                     "ci95": [round(ci[0], 4), round(ci[1], 4)],
                     "ci_width": round(ci[1] - ci[0], 4),
                     "width_0.1_0.9": round(w, 4)})
        print(f"      p_c={rows[-1]['p_c']:.4f} CI{rows[-1]['ci95']} "
              f"width(.1-.9)={w:.4f}   [{time.time() - t:.0f}s]", flush=True)

    N = np.array([r["N"] for r in rows], float)
    pc = np.array([r["p_c"] for r in rows], float)
    wd = np.array([r["width_0.1_0.9"] for r in rows], float)
    Dm = np.array([r["D"] for r in rows], float)
    km = np.array([r["mean_degree"] for r in rows], float)

    # residual size trend with architecture held fixed
    b_pc = np.polyfit(np.log2(N), pc, 1)[0]
    b_w = np.polyfit(np.log2(N), wd, 1)[0]
    spread_pc = float(pc.max() - pc.min())

    out = {
        "purpose": ("finite-size sweep with fractal dimension and mean degree "
                    "held FIXED, so the size effect is not confounded with "
                    "architecture (unlike data/scaling_mesh.json)"),
        "target_D": D_TARGET, "target_mean_degree": K_TARGET,
        "n_trials": N_TRIALS, "n_densities": N_DENSITIES, "seed": SEED,
        "sizes": rows,
        "D_spread_achieved": round(float(Dm.max() - Dm.min()), 4),
        "mean_degree_spread_achieved": round(float(km.max() - km.min()), 4),
        "p_c_spread": round(spread_pc, 4),
        "slope_p_c_per_doubling": round(float(b_pc), 5),
        "slope_width_per_doubling": round(float(b_w), 5),
        "confounded_comparison": ("data/scaling_mesh.json varies D from 1.267 to "
                                  "1.741 across the same size range; the p_c "
                                  "spread there (0.0326) mixes size and D"),
        "seconds": round(time.time() - t0, 1),
    }
    dpath = os.path.join(config.PATHS.data, "finite_size_fixedD.json")
    with open(dpath, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {dpath}")

    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.0))
    ax[0].errorbar(N, pc,
                   yerr=[pc - np.array([r["ci95"][0] for r in rows]),
                         np.array([r["ci95"][1] for r in rows]) - pc],
                   fmt="o-", capsize=3, color="#2b6cb0")
    ax[0].set_xscale("log", base=2)
    ax[0].set_xlabel("network size $N$ (nodes)")
    ax[0].set_ylabel("$p_c$ (random attack)")
    ax[0].set_title(f"A. Threshold at fixed $D$ = {Dm.mean():.2f}, "
                    f"$\\langle k\\rangle$ = {km.mean():.2f}",
                    loc="left", fontsize=10)
    ax[1].plot(N, wd, "s-", color="#b7791f")
    ax[1].set_xscale("log", base=2)
    ax[1].set_xlabel("network size $N$ (nodes)")
    ax[1].set_ylabel("10-90% collapse window")
    ax[1].set_title("B. Transition sharpness", loc="left", fontsize=10)
    fig.tight_layout()
    fpath = os.path.join(config.PATHS.figures, "finite_size_fixedD.png")
    fig.savefig(fpath, dpi=200)
    print(f"wrote {fpath}")

    print(f"\nWith D and <k> held fixed (D spread {out['D_spread_achieved']}, "
          f"<k> spread {out['mean_degree_spread_achieved']}), p_c spans "
          f"{spread_pc:.4f} across a {N[-1] / N[0]:.0f}x size range "
          f"({b_pc:+.5f} per doubling) and the transition window narrows "
          f"{wd[0]:.4f} -> {wd[-1]:.4f} ({b_w:+.5f} per doubling).")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
