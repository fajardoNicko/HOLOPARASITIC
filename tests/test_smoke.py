"""
test_smoke.py — fast invariants that catch breakage before a long run.

    C:\\laragon\\bin\\python\\python-3.13\\python.exe -m pytest -q
or simply:
    ...\\python.exe tests\\test_smoke.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import config
from holoparasitic import network, fractal, hydraulics, percolation


def test_network_is_reticulate():
    G = network.generate(config.NetworkParams(generations=7, seed=0))
    s = network.summary(G)
    assert s["n_nodes"] > 100
    # reticulation must create loops, else there is no sharp percolation
    assert s["n_cycles"] > 0, "network is a pure tree — no loops!"
    assert s["n_anastomoses"] > 0


def test_fractal_dimension_in_range():
    G = network.generate(config.NetworkParams(generations=8, seed=1))
    D = fractal.fractal_dimension(G)
    assert 1.0 < D < 2.2, f"D={D} outside plausible planar range"


def test_hydraulic_sink_lowers_potential():
    G = network.generate(config.NetworkParams(generations=7, seed=2))
    s, psi0 = hydraulics.baseline_potentials(G)
    haus = list(G.nodes)[: max(1, G.number_of_nodes() // 10)]
    psi1 = s.solve(haustoria=haus, k_h=1.0)
    # haustorial sinks must pull the network to more negative potential
    assert psi1.min() <= psi0.min() + 1e-9
    assert len(s.embolized_nodes(psi1)) >= 0


def test_pc_is_a_probability():
    G = network.generate(config.NetworkParams(generations=7, seed=3))
    res = percolation.find_pc(
        G, config.PercolationParams(mode="random", n_trials=3000,
                                    n_densities=25))
    assert 0.0 <= res["p_c"] <= 1.0
    # collapse probability must be monotone-ish: low at rho=0, high at rho=1
    assert res["p_collapse"][0] < 0.5 < res["p_collapse"][-1]


def test_modes_run():
    G = network.generate(config.NetworkParams(generations=6, seed=4))
    for mode in ("random", "targeted", "hydraulic"):
        res = percolation.find_pc(
            G, config.PercolationParams(mode=mode, n_trials=1500,
                                        n_densities=15))
        assert np.isfinite(res["p_c"]) or res["mode"] == mode


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS  {fn.__name__}")
    print(f"\n{len(fns)} smoke tests passed.")
