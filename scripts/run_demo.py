"""
run_demo.py — fast end-to-end demo (~seconds). Use during development and for
the live booth demo.

    C:\\laragon\\bin\\python\\python-3.13\\python.exe scripts\\run_demo.py
    ...\\python.exe scripts\\run_demo.py 50000        # override trial count
"""

import os
import sys

# make the project root importable when run as a loose script
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from holoparasitic import network, fractal, percolation, sweep, viz


def main():
    n_trials = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
    figdir = config.PATHS.figures

    print("=" * 64)
    print("HOLOPARASITIC VASCULAR PERCOLATION — DEMO")
    print("=" * 64)

    # 1. Network + fractal dimension --------------------------------------
    G = network.generate()
    s = network.summary(G)
    D = fractal.fractal_dimension(G)
    print(f"[1] network: N={s['n_nodes']} edges={s['n_edges']} "
          f"loops={s['n_cycles']} anastomoses={s['n_anastomoses']}")
    print(f"    box-counting fractal dimension D = {D:.3f}")
    viz.plot_network(G, os.path.join(figdir, "network.png"))

    # 2. Percolation threshold (random site percolation) ------------------
    pp = config.PercolationParams(mode="random", n_trials=n_trials,
                                  n_densities=50)
    res = percolation.find_pc(G, pp, with_ci=True)
    print(f"[2] p_c = {res['p_c']:.4f}  "
          f"(crossing={res['p_c_crossing']:.4f}, "
          f"95% CI={tuple(round(x, 4) for x in res['ci']['ci95'])})")
    viz.plot_sigmoid(res, os.path.join(figdir, "sigmoid.png"))
    viz.plot_collapse_montage(G, os.path.join(figdir, "collapse_montage.png"))

    # 3. Small p_c vs D and a small (K_h, D) surface ----------------------
    print("[3] p_c vs D (random, 3 networks):")
    sweep.pc_vs_D(reticulation_grid=(0.3, 0.9, 1.8),
                  perc=config.PercolationParams(mode="random",
                                                n_trials=12_000,
                                                n_densities=30))
    print("    small (K_h, D) hydraulic surface (3x3):")
    surf = sweep.pc_surface(
        config.SweepParams(reticulation_grid=(0.3, 0.9, 1.8),
                           k_h_grid=(0.3, 0.7, 1.5),
                           n_trials_coupled=300, n_densities=20))
    viz.plot_pc_heatmap(surf, os.path.join(figdir, "pc_heatmap.png"))

    print("-" * 64)
    print(f"figures written to {os.path.abspath(figdir)}\\")
    print("done.")


if __name__ == "__main__":
    main()
