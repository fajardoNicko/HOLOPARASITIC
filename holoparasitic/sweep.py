"""
sweep.py  (Person D) — parameter sweeps that turn single runs into the study's
two headline results:

  1. pc_vs_D       topological p_c as a function of fractal dimension D
                   (random site percolation; the cheap, high-trial result).

  2. pc_surface    p_c over the (K_h, D) grid using the COUPLED hydraulic mode,
                   so haustorial sink strength K_h actually moves the threshold.
                   This is the p_c heatmap for the board.

The D axis is realised physically at CONSTANT network size N: the anastomosis
(vein) density is varied and the box-counting dimension of each resulting
network is MEASURED — we never just assert a value of D. Denser venation gives a
higher D (and, as in real leaves, higher connectivity); a length_ratio sweep at
fixed connectivity is the documented geometric control.
"""

from __future__ import annotations

import numpy as np

import config
from . import network, fractal, percolation


def _network_for_reticulation(base: config.NetworkParams, reticulation: float,
                              seed):
    p = config.NetworkParams(**{**base.__dict__, "reticulation": reticulation,
                                "seed": seed})
    return network.generate(p)


def pc_vs_D(reticulation_grid=None, base_network=None, perc=None, verbose=True):
    """Topological p_c vs measured D (random removal). Returns dict of arrays."""
    rets = list(reticulation_grid or config.DEFAULT_SWEEP.reticulation_grid)
    base = base_network or config.DEFAULT_NETWORK
    pp = perc or config.PercolationParams(mode="random", n_trials=40_000,
                                          n_densities=40)
    Ds, pcs, Ns, degs = [], [], [], []
    for k, ret in enumerate(rets):
        G = _network_for_reticulation(base, ret, seed=100 + k)
        D = fractal.fractal_dimension(G)
        res = percolation.find_pc(G, pp)
        Ds.append(D); pcs.append(res["p_c"]); Ns.append(res["n_nodes"])
        degs.append(network.summary(G)["mean_degree"])
        if verbose:
            print(f"  reticulation={ret:.2f}  D={D:.3f}  p_c={res['p_c']:.4f}  "
                  f"(N={res['n_nodes']}, <k>={degs[-1]:.2f})")
    return {"reticulation": np.array(rets), "D": np.array(Ds),
            "p_c": np.array(pcs), "N": np.array(Ns),
            "mean_degree": np.array(degs)}


def pc_surface(sweep=None, base_network=None, verbose=True):
    """p_c over the (K_h, D) grid via the coupled hydraulic-cavitation model.

    Returns dict: D (rows), k_h (cols), pc (2-D matrix), reticulation (row knob).
    """
    sw = sweep or config.DEFAULT_SWEEP
    base = base_network or config.DEFAULT_NETWORK

    rets = list(sw.reticulation_grid)
    khs = list(sw.k_h_grid)
    pp = config.PercolationParams(mode="hydraulic",
                                  n_trials=sw.n_trials_coupled,
                                  n_densities=sw.n_densities,
                                  seed=sw.seed)

    D_vals = np.empty(len(rets))
    pc = np.full((len(rets), len(khs)), np.nan)

    for i, ret in enumerate(rets):
        G = _network_for_reticulation(base, ret, seed=200 + i)
        D_vals[i] = fractal.fractal_dimension(G)
        for jx, kh in enumerate(khs):
            res = percolation.find_pc(G, pp, k_h=kh)
            pc[i, jx] = res["p_c"]
            if verbose:
                print(f"  D={D_vals[i]:.3f}  K_h={kh:4.2f}  "
                      f"p_c={pc[i, jx]:.4f}")
    return {"D": D_vals, "k_h": np.array(khs), "pc": pc,
            "reticulation": np.array(rets)}


if __name__ == "__main__":
    print("pc_vs_D (random, topological):")
    pc_vs_D(reticulation_grid=(0.3, 0.9, 1.8),
            perc=config.PercolationParams(mode="random", n_trials=8000,
                                          n_densities=25))
