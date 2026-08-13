r"""
run_calibration.py — verify the synthetic generator is calibrated to the real
cohort, and that its 2D sweep spans the real (mean-degree, D) region.

Phase 2 (synthetic) only earns its place if its networks branch like real leaves
AND can vary mean degree and fractal dimension independently across the observed
range. This script demonstrates both, from the cohort medians measured in Phase
3, and writes the evidence so the calibration is auditable rather than asserted.

It answers three questions:
  1. Does the calibrated generator reproduce the real BRANCHING GEOMETRY?
     (branch angle, Murray exponent, daughter symmetry — held fixed)
  2. Do the two knobs move <k> and D INDEPENDENTLY, as they are in real leaves?
  3. Does the 2D grid COVER the real cohort's (<k>, D) region?

    ...python.exe scripts\run_calibration.py

Outputs
    data/calibration.json          targets vs achieved, grid coverage
    figures/calibration_grid.png   synthetic grid over the real (<k>, D) cloud
"""

import os
import sys
import csv
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
from holoparasitic import network, fractal, calibrate as cal


def _measure(p):
    import networkx as nx
    G = network.generate(p)
    m = cal.measure_from_graph(G)
    N, E = G.number_of_nodes(), G.number_of_edges()
    # loop fraction as the fraction of edges that lie on a cycle (1 - bridges/E):
    # this is the topological analogue of Matos' EL/ET label and the honest
    # like-for-like comparison against the real cohort's 0.78.
    bridges = set(nx.bridges(G)) if (N and nx.is_connected(G)) else set()
    edges_on_cycle = 1.0 - len(bridges) / E if E else 0.0
    return {"n_nodes": N, "n_edges": E, "mean_degree": 2 * E / N,
            "D": fractal.fractal_dimension(G),
            "branch_angle_deg": m["branch_angle_deg"],
            "murray_exponent": m["murray_exponent"],
            "daughter_symmetry": m["daughter_symmetry"],
            "loop_fraction": edges_on_cycle}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    T = cal.COHORT_TARGETS
    print("=" * 78)
    print("SYNTHETIC GENERATOR CALIBRATION vs the 100-leaf real cohort")
    print("=" * 78)

    # -- 1. geometry match at the calibrated hero (cohort median <k> & D) ------
    hero = cal.calibrated_base(generations=11)
    hm = _measure(hero)
    print("1) BRANCHING GEOMETRY (fixed targets) — calibrated hero, gen=11")
    print(f"   {'metric':20s} {'target':>10s} {'achieved':>10s}")
    for key, tgt in [("branch_angle_deg", T["branch_angle_deg"]),
                     ("murray_exponent", T["murray_exponent"]),
                     ("daughter_symmetry", T["daughter_symmetry"]),
                     ("mean_degree", T["mean_degree"])]:
        print(f"   {key:20s} {tgt:10.3f} {hm[key]:10.3f}")
    print(f"   {'loop_fraction':20s} {T['loop_fraction']:10.3f} "
          f"{hm['loop_fraction']:10.3f}   (edges-on-cycle; planar-mesh reticulation)")

    # -- 2. the 2D grid --------------------------------------------------------
    k_targets = list(config.SWEEP_MEAN_DEGREES)
    gens = list(config.SWEEP_GENERATIONS)
    grid = cal.grid_params(k_targets, gens)
    print(f"\n2) 2D SWEEP — {len(k_targets)} mean-degree x {len(gens)} "
          f"generations = {len(grid)} networks")
    rows = []
    t0 = time.time()
    for p, k_req, g in grid:
        m = _measure(p)
        m.update({"k_target": k_req, "generations": g})
        rows.append(m)
    print(f"   generated {len(rows)} networks in {time.time()-t0:.0f}s")

    ks = np.array([r["mean_degree"] for r in rows])
    Ds = np.array([r["D"] for r in rows])
    # collinearity of the two achieved axes — want them near-orthogonal
    rkD = float(np.corrcoef(ks, Ds)[0, 1])
    print(f"   achieved <k> range {ks.min():.2f}..{ks.max():.2f}   "
          f"D range {Ds.min():.3f}..{Ds.max():.3f}")
    print(f"   grid <k>-D correlation r={rkD:+.3f}  (near 0 = independent knobs)")

    # -- 3. coverage of the real cohort ---------------------------------------
    real = _load_real()
    cover = None
    if real is not None:
        rk, rD = real["mean_degree"], real["D"]
        # fraction of real leaves whose (<k>, D) lies inside the grid's hull box
        inside = ((rk >= ks.min()) & (rk <= ks.max()) &
                  (rD >= Ds.min()) & (rD <= Ds.max()))
        cover = float(inside.mean())
        print(f"\n3) COVERAGE — {cover:.0%} of real cohort leaves fall inside the "
              f"synthetic grid's (<k>, D) box")

    # -- outputs ---------------------------------------------------------------
    datadir = os.path.join(ROOT, config.PATHS.data)
    os.makedirs(datadir, exist_ok=True)
    with open(os.path.join(datadir, "calibration.json"), "w") as f:
        json.dump({"targets": T, "hero_gen11": hm,
                   "grid": rows, "grid_k_D_correlation": rkD,
                   "grid_k_range": [float(ks.min()), float(ks.max())],
                   "grid_D_range": [float(Ds.min()), float(Ds.max())],
                   "real_coverage_fraction": cover}, f, indent=2)

    figdir = os.path.join(ROOT, "figures")
    os.makedirs(figdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    if real is not None:
        ax.scatter(real["mean_degree"], real["D"], s=28, c="#B0B0B0",
                   alpha=.55, edgecolor="none", label="real cohort (n=100)")
    sc = ax.scatter(ks, Ds, s=70, c=[r["generations"] for r in rows],
                    cmap="viridis", edgecolor="white", linewidth=.6,
                    label="synthetic grid", zorder=3)
    plt.colorbar(sc, label="generations (D knob)")
    ax.set_xlabel("Mean degree  ⟨k⟩  (reticulation knob)")
    ax.set_ylabel("Fractal dimension  D")
    ax.set_title("Calibrated synthetic grid spans the real (⟨k⟩, D) region\n"
                 f"grid ⟨k⟩–D correlation r={rkD:+.2f} (independent knobs)",
                 fontsize=10)
    ax.legend(fontsize=8); ax.grid(alpha=.25)
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, "calibration_grid.png"), dpi=200,
                bbox_inches="tight")
    print(f"\nwrote data/calibration.json + figures/calibration_grid.png")


def _load_real():
    path = os.path.join(ROOT, config.PATHS.data, "cohort_pc.csv")
    if not os.path.exists(path):
        path = os.path.join(ROOT, config.PATHS.data, "characterization.csv")
        if not os.path.exists(path):
            return None
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))

    def col(n):
        out = []
        for r in rows:
            try:
                out.append(float(r[n]))
            except (KeyError, TypeError, ValueError):
                out.append(np.nan)
        return np.array(out)
    k, D = col("mean_degree"), col("D")
    m = np.isfinite(k) & np.isfinite(D)
    return {"mean_degree": k[m], "D": D[m]}


if __name__ == "__main__":
    main()
