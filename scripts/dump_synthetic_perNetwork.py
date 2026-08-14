# -*- coding: utf-8 -*-
r"""
dump_synthetic_perNetwork.py -- regenerate the 42 synthetic grid networks and
write EVERY per-network metric used in Table 1 to a CSV, so the appendix of
worked computations can show the actual sums instead of a stored summary.

Deterministic: same grid_params() and same global seed as run_synthetic_grid.py.

Run:  C:\laragon\bin\python\python-3.13\python.exe scripts\dump_synthetic_perNetwork.py
"""
import os
import sys
import csv
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import network, fractal, calibrate as cal
from holoparasitic.characterize import _effective_conductance

import networkx as nx

OUT = os.path.join(ROOT, "data", "synthetic_pernetwork.csv")
FIELDS = ["idx", "req_mean_degree", "generations", "N", "E", "mean_degree",
          "degree_sd", "D", "loop_fraction_nonbridge", "bridge_fraction",
          "effective_conductance", "gcc_fraction", "seconds"]


def main():
    grid = cal.grid_params(config.SWEEP_MEAN_DEGREES, config.SWEEP_GENERATIONS)
    rows = []
    for idx, (params, md_req, gen) in enumerate(grid):
        t0 = time.time()
        G = network.generate(params)
        N = G.number_of_nodes()
        E = G.number_of_edges()
        deg = np.array([d for _, d in G.degree()], float)
        n_bridges = len(list(nx.bridges(G)))
        gcc = max(nx.connected_components(G), key=len)
        rows.append({
            "idx": idx,
            "req_mean_degree": round(md_req, 3),
            "generations": gen,
            "N": N,
            "E": E,
            "mean_degree": 2.0 * E / N,
            "degree_sd": float(deg.std(ddof=1)),   # sample SD, as in characterize.py
            "D": fractal.fractal_dimension(G),
            "loop_fraction_nonbridge": (E - n_bridges) / E if E else 0.0,
            "bridge_fraction": n_bridges / E if E else 0.0,
            "effective_conductance": _effective_conductance(G),
            "gcc_fraction": len(gcc) / N,
            "seconds": round(time.time() - t0, 1),
        })
        print("[%2d/%2d] N=%d k=%.4f sd=%.4f D=%.4f lf=%.4f (%.1fs)"
              % (idx + 1, len(grid), N, rows[-1]["mean_degree"],
                 rows[-1]["degree_sd"], rows[-1]["D"],
                 rows[-1]["loop_fraction_nonbridge"], rows[-1]["seconds"]),
              flush=True)

    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
