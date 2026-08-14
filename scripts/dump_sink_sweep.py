# -*- coding: utf-8 -*-
r"""
dump_sink_sweep.py -- re-run the haustorial gradient sweep of make_sink_demo.py
and archive the per-gradient numbers to data/sink_sweep.csv.

make_sink_demo.py computes this sweep to draw the right-hand panel of the
water-potential figure but stores only its endpoint (the cavitation onset, NaN
when no gradient reaches the threshold). The appendix of worked computations
needs the sweep itself, so this script reproduces it with the same functions and
the same calibrated K_h and writes the numbers out. It touches no existing file.

Run:  C:\laragon\bin\python\python-3.13\python.exe scripts\dump_sink_sweep.py
"""
import os
import sys
import csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import network, hydraulics
from scripts.make_sink_demo import (GRADIENT_MPA, calibrate_kh, parasite_flux,
                                    source_influx)

OUT = os.path.join(ROOT, "data", "sink_sweep.csv")


def main():
    G = network.generate()
    solver, psi0 = hydraulics.baseline_potentials(G)

    # same contact patch as make_sink_demo.py: interior node nearest the lamina
    # centroid, grown two hops
    pos = np.array([G.nodes[n]["pos"] for n in solver.nodes], float)
    fixed = {solver.root, *solver.terminals}
    interior = [(i, n) for i, n in enumerate(solver.nodes) if n not in fixed]
    cx, cy = pos[:, 0].mean(), pos[:, 1].mean()
    h_node = min(interior,
                 key=lambda t: (pos[t[0], 0] - cx) ** 2 + (pos[t[0], 1] - cy) ** 2)[1]
    patch, frontier = {h_node}, {h_node}
    for _ in range(2):
        nxt = set()
        for n in frontier:
            nxt |= set(G.neighbors(n))
        patch |= nxt
        frontier = nxt
    patch = [n for n in patch if n not in fixed][:16]

    psi_host_local = psi0[solver.index[h_node]]
    k_h, frac, _ = calibrate_kh(solver, patch, psi_host_local - GRADIENT_MPA)
    print("calibrated K_h = %.6f (diverts %.4f at %.1f MPa)"
          % (k_h, frac, GRADIENT_MPA))

    prot = {solver.root, *solver.terminals}
    free_idx = [solver.index[n] for n in solver.nodes if n not in prot]

    rows = []
    for g in np.linspace(0.0, 3.0, 31):
        pp = psi_host_local - g
        psi_g = solver.solve(haustoria={n: k_h for n in patch}, relative=True,
                             psi_parasite=pp)
        emb = solver.embolized_nodes(psi_g)
        rows.append({
            "gradient_MPa": round(float(g), 3),
            "psi_parasite_MPa": float(pp),
            "min_psi_MPa": float(psi_g[free_idx].min()),
            "margin_to_cavitation_MPa": float(psi_g[free_idx].min()
                                              - config.PSI_CAVITATION),
            "n_embolized": len(emb),
            "embolized_fraction": len(emb) / len(solver.nodes),
            "diversion_fraction": float(parasite_flux(solver, psi_g, patch, k_h, pp)
                                        / source_influx(solver, psi_g)),
        })
        print("  grad=%.2f  min_psi=%.4f  margin=%.4f  embolized=%d"
              % (rows[-1]["gradient_MPa"], rows[-1]["min_psi_MPa"],
                 rows[-1]["margin_to_cavitation_MPa"], rows[-1]["n_embolized"]),
              flush=True)

    with open(OUT, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    worst = min(rows, key=lambda r: r["min_psi_MPa"])
    print("worst case: gradient %.1f MPa -> min psi %.4f MPa (margin %.4f), "
          "K_h = %.6f, cavitation threshold %.1f MPa"
          % (worst["gradient_MPa"], worst["min_psi_MPa"],
             worst["margin_to_cavitation_MPa"], k_h, config.PSI_CAVITATION))
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
