"""
run_full.py — final production run for the paper figures.

Reproduces the paper claim: 1,000,000 Monte Carlo simulations across 50
haustorial-density values (20,000 trials per density) for the hero sigmoid,
then the full p_c-vs-D curve and the (K_h, D) surface, then every figure plus
the collapse animation.

Results are saved INCREMENTALLY: data/results.npz and data/summary.json are
rewritten after every stage, so (a) partial data is on disk the moment each
stage finishes — results.npz appears right after the hero sigmoid, not only at
the very end — and (b) a crash in a later stage never loses earlier work. The
heavy sweep/animation stages are individually guarded so one failure doesn't
abort the rest.

    C:\\laragon\\bin\\python\\python-3.13\\python.exe scripts\\run_full.py
    ...\\python.exe scripts\\run_full.py 100000     # lighter final run

Note: the 1e6-trial sigmoid is the long pole (~20-25 min on an N=1023 network,
i5-8265U); the hydraulic (K_h, D) surface re-solves a sparse system per trial
and is the other slow part. Override the argument for a faster pass.
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import config
from holoparasitic import network, fractal, percolation, sweep, viz


def _py(x):
    """Make numpy types JSON-serialisable."""
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (list, tuple)):
        return [_py(v) for v in x]
    if isinstance(x, dict):
        return {k: _py(v) for k, v in x.items()}
    return x


def _checkpoint(datadir, results, summary, stage):
    """Rewrite results.npz + summary.json with everything computed so far."""
    summary["last_completed_stage"] = stage
    np.savez(os.path.join(datadir, "results.npz"), **results)
    with open(os.path.join(datadir, "summary.json"), "w") as f:
        json.dump(_py(summary), f, indent=2)
    print(f"    checkpoint -> data/results.npz + summary.json (stage {stage})",
          flush=True)


def main():
    # line-buffer stdout so progress is visible live in a background/redirected
    # run instead of only flushing at the end.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    n_trials = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    figdir, datadir = config.PATHS.figures, config.PATHS.data
    os.makedirs(datadir, exist_ok=True)
    os.makedirs(figdir, exist_ok=True)

    results, summary = {}, {}

    print("=" * 64, flush=True)
    print("HOLOPARASITIC VASCULAR PERCOLATION — FULL RUN", flush=True)
    print(f"hero sigmoid: N={n_trials:,} trials", flush=True)
    print("=" * 64, flush=True)

    # [1] network + fractal dimension ------------------------------------
    G = network.generate()
    D = fractal.fractal_dimension(G)
    net_summary = network.summary(G)
    print(f"[1] network N={net_summary['n_nodes']}  D={D:.3f}", flush=True)
    viz.plot_network(G, os.path.join(figdir, "network.png"))
    summary["network"] = net_summary
    summary["D"] = D
    _checkpoint(datadir, results, summary, "1-network")

    # [2] hero sigmoid (the headline 1e6-trial result) -------------------
    pp = config.PercolationParams(mode="random", n_trials=n_trials,
                                  n_densities=50)
    print(f"[2] running {n_trials:,} trials "
          f"({pp.trials_per_density:,} per density) ...", flush=True)
    res = percolation.find_pc(G, pp, with_ci=True)
    print(f"    p_c = {res['p_c']:.5f}  95% CI={res['ci']['ci95']}", flush=True)
    viz.plot_sigmoid(res, os.path.join(figdir, "sigmoid.png"))
    results.update(rhos=res["rhos"], p_collapse=res["p_collapse"],
                   gcc_fraction=res["gcc_fraction"])
    summary.update(p_c_random=res["p_c"], p_c_ci95=res["ci"]["ci95"],
                   n_trials=res["n_trials"])
    _checkpoint(datadir, results, summary, "2-hero-sigmoid")

    # [3] targeted-attack comparison: backbone (betweenness) vs degree -----
    try:
        print("[3] targeted-attack comparison (betweenness vs degree) ...",
              flush=True)
        _, nodes_t = network.to_csr(G)
        tparams = config.PercolationParams(mode="targeted",
                                           n_trials=max(50_000, n_trials // 10),
                                           n_densities=50)
        res_t = percolation.find_pc(G, tparams)            # betweenness (default)
        w_deg = percolation.importance_weights(G, nodes_t, metric="degree")
        res_td = percolation.find_pc(G, tparams, weights=w_deg)   # degree
        print(f"    p_c(random)={res['p_c']:.4f}  "
              f"p_c(betweenness-backbone)={res_t['p_c']:.4f}  "
              f"p_c(degree)={res_td['p_c']:.4f}", flush=True)
        viz.plot_sigmoid(res_t, os.path.join(figdir, "sigmoid_targeted.png"))
        results.update(targeted_rhos=res_t["rhos"],
                       targeted_p_collapse=res_t["p_collapse"])
        summary["p_c_targeted_betweenness"] = res_t["p_c"]
        summary["p_c_targeted_degree"] = res_td["p_c"]
        _checkpoint(datadir, results, summary, "3-targeted")
    except Exception as e:
        print(f"    [3] FAILED: {e}", flush=True)

    # [4] p_c vs D -------------------------------------------------------
    try:
        print("[4] p_c vs D ...", flush=True)
        pcd = sweep.pc_vs_D()
        results.update(pcd_D=pcd["D"], pcd_pc=pcd["p_c"],
                       pcd_reticulation=pcd["reticulation"],
                       pcd_mean_degree=pcd["mean_degree"])
        _checkpoint(datadir, results, summary, "4-pc-vs-D")
    except Exception as e:
        print(f"    [4] FAILED: {e}", flush=True)

    # [5] (K_h, D) hydraulic surface -------------------------------------
    try:
        print("[5] (K_h, D) hydraulic surface ...", flush=True)
        surf = sweep.pc_surface()
        viz.plot_pc_heatmap(surf, os.path.join(figdir, "pc_heatmap.png"))
        results.update(surface_D=surf["D"], surface_kh=surf["k_h"],
                       surface_pc=surf["pc"],
                       surface_reticulation=surf["reticulation"])
        _checkpoint(datadir, results, summary, "5-surface")
    except Exception as e:
        print(f"    [5] FAILED: {e}", flush=True)

    # [6] collapse animation ---------------------------------------------
    try:
        print("[6] collapse animation ...", flush=True)
        viz.animate_collapse(G, res, os.path.join(figdir, "collapse.gif"))
        viz.plot_collapse_montage(G, os.path.join(figdir,
                                                  "collapse_montage.png"))
    except Exception as e:
        print(f"    [6] FAILED: {e}", flush=True)

    _checkpoint(datadir, results, summary, "6-complete")
    print("-" * 64, flush=True)
    print(f"figures -> {os.path.abspath(figdir)}", flush=True)
    print(f"data    -> {os.path.abspath(datadir)}", flush=True)
    print("done.", flush=True)


if __name__ == "__main__":
    main()
