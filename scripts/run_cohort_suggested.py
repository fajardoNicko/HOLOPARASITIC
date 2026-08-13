# -*- coding: utf-8 -*-
r"""
run_cohort_suggested.py -- for EVERY real Matos leaf: measure the random-attack
percolation threshold p_c on (a) the leaf as traced [CURRENT] and (b) the same leaf
with shortest Delaunay areole-closures added up to the cohort reticulation ceiling
[SUGGESTED]. This is the cohort-wide version of the 5 fig_realsuggested_*.png panels.

The parasite is modelled ONLY as random functional loss of xylem nodes (site
percolation) -- no parasite-specific efficiency/attachment assumptions. The question
is purely: how much more collapse-resistant does each real leaf become when made more
reticulate?

Trials: 10,000 per network (TOTAL; n_trials/n_densities per rho). Real leaves collapse
below rho~0.3 so the sweep is concentrated with rho_max=0.6.

Output (incremental, resumable -- re-run to continue where it stopped):
    data/cohort_suggested.csv     one row per leaf
ASCII-only stdout.

    C:\\laragon\\bin\\python\\python-3.13\\python.exe scripts\\run_cohort_suggested.py
"""
import os, sys, csv, glob, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import config
from holoparasitic import realleaf, percolation
from scripts.make_real_suggested import add_loops, TARGET_K   # reuse EXACT loop-closure

LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
OUT     = os.path.join(ROOT, "data", "cohort_suggested.csv")
PP      = config.PercolationParams(mode="random", n_densities=40, n_trials=10000)
RHO_MAX = 0.6

FIELDS = ["species", "N", "E", "k_current", "loops_current",
          "k_suggested", "loops_added", "D", "quality",
          "pc_current", "pc_suggested", "delta_pc", "seconds"]


def meta_lookup():
    """D + quality per leaf from characterization_annotated.csv (avoids recomputing D)."""
    m = {}
    p = os.path.join(ROOT, "data", "characterization_annotated.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, newline="")):
            m[r["name"]] = (r.get("D", ""), r.get("quality", ""))
    return m


def measure(G):
    return float(percolation.find_pc(G, PP, rho_max=RHO_MAX)["p_c"])


def done_set():
    if not os.path.exists(OUT):
        return set()
    return {r["species"] for r in csv.DictReader(open(OUT, newline=""))}


def append_row(row, write_header):
    with open(OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        w.writerow(row)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    meta = meta_lookup()
    spp = sorted(d for d in os.listdir(LEAFDIR)
                 if os.path.isdir(os.path.join(LEAFDIR, d)))
    already = done_set()
    write_header = not os.path.exists(OUT)
    print("leaves total=%d  already done=%d  todo=%d  (%d trials/network)"
          % (len(spp), len(already), len(spp) - len(already), PP.n_trials), flush=True)

    for i, s in enumerate(spp, 1):
        if s in already:
            continue
        t0 = time.time()
        try:
            nf = glob.glob(os.path.join(LEAFDIR, s, "*_nodes.csv"))[0]
            vf = glob.glob(os.path.join(LEAFDIR, s, "*_veins.csv"))[0]
            G = realleaf.load_matos(nf, vf, name=s)
            N, E = G.number_of_nodes(), G.number_of_edges()
            k0 = 2 * E / N
            loops0 = E - N + 1                       # cyclomatic (connected approx)
            pc0 = measure(G)
            G2, nadd = add_loops(G, TARGET_K)
            k1 = 2 * G2.number_of_edges() / G2.number_of_nodes()
            pc1 = measure(G2)
            D, q = meta.get(s, ("", ""))
            row = {"species": s, "N": N, "E": E,
                   "k_current": round(k0, 4), "loops_current": loops0,
                   "k_suggested": round(k1, 4), "loops_added": nadd,
                   "D": D, "quality": q,
                   "pc_current": round(pc0, 4), "pc_suggested": round(pc1, 4),
                   "delta_pc": round(pc1 - pc0, 4), "seconds": round(time.time() - t0, 1)}
            append_row(row, write_header); write_header = False
            print("  [%3d/%3d] %-8s N=%-7d <k> %.2f->%.2f (+%d)  pc %.3f->%.3f  "
                  "d=%+0.3f  (%.0fs)"
                  % (i, len(spp), s, N, k0, k1, nadd, pc0, pc1, pc1 - pc0,
                     time.time() - t0), flush=True)
        except Exception as e:
            print("  [%3d/%3d] %-8s FAILED: %s" % (i, len(spp), s, e), flush=True)

    print("DONE -> %s" % os.path.relpath(OUT, ROOT), flush=True)


if __name__ == "__main__":
    main()
