# -*- coding: utf-8 -*-
r"""
run_local_leaves.py -- percolation on the locally collected leaves (one window
per species), with the SAME engine and settings as the archived cohort run
(scripts/run_cohort_percolation.py): uniform (random) removal, 40 removal
fractions up to 0.6, 60 trials each (2,400 trials), 50% collapse criterion,
seed 1, loaded through realleaf.load_matos exactly like a Matos leaf.

Input per leaf: the LeafVeinCNN v2.14 "Save Data" workbook
summary/results/<image>.xlsx (sheets graphWeighted Nodes / Edges). LeafVeinCNN
overwrites an existing workbook in place and does NOT clear old rows, so each
table is cut to the true node and vein counts (VNN, VNE) recorded in the same
run's results.xlsx. The cut tables are written as Matos-style CSVs to
empirical/local_tracings/ and then loaded from there.

Writes empirical/local_leaves.csv (read by make_local_validation_figure.py).
The fern is converted and reported but NOT written to local_leaves.csv: its
tracing failed (only the midrib, traced hollow, survived).

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_local_leaves.py
"""
import csv
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import pandas as pd

import config
from holoparasitic import realleaf, percolation

LV = os.path.join(ROOT, "LOCAL VALIDATION")
OUTDIR = os.path.join(ROOT, "empirical", "local_tracings")
OUTCSV = os.path.join(ROOT, "empirical", "local_leaves.csv")
#  key: (folder, image stem, species, common, group, crop T,L,W,H, use)
LEAVES = [
    ("Talisay_cleaned", "talisay_final_red_inverted", "Terminalia catappa", "talisay", "non-crop", (786, 1272, 3693, 3693), True),
    ("Okra_cleaned", "okra_final_red_inverted", "Abelmoschus esculentus", "okra", "crop", (984, 1568, 3693, 3693), True),
    ("Guyabano_cleaned", "guyabano_final_red_inverted", "Annona muricata", "guyabano", "crop", (1200, 1064, 3693, 3693), True),
    ("Gumamela_cleaned", "gumamela_final_inverted_red", "Hibiscus rosa-sinensis", "gumamela", "non-crop", (1696, 1816, 3693, 3693), True),
    ("Fern2_cleaned", "sf_final_red", "Nephrolepis sp.", "sword fern", "non-crop", (464, 1360, 3039, 4704), False),
]
FIELDS = ["species", "common_name", "group", "plant_id", "leaf_id", "window_id", "collection_date",
          "window_mm2", "n_junctions", "mean_degree", "loop_fraction", "p_c", "notes"]


def true_counts(folder):
    r = pd.read_excel(os.path.join(LV, folder, "results.xlsx"), header=None)
    d = dict(zip(r.iloc[0], r.iloc[1]))
    return int(d["VNN"]), int(d["VNE"])


def convert(folder, stem):
    x = os.path.join(LV, folder, "summary", "results", stem + ".xlsx")
    N = pd.read_excel(x, sheet_name="graphWeighted Nodes")
    E = pd.read_excel(x, sheet_name="graphWeighted Edges")
    nn, ne = true_counts(folder)
    stale = (len(N) - nn, len(E) - ne)
    N, E = N.iloc[:nn], E.iloc[:ne]
    if E[["EndNodes_1", "EndNodes_2"]].values.max() > nn:
        raise ValueError(f"{folder}: vein table points past node {nn}")
    os.makedirs(OUTDIR, exist_ok=True)
    npath = os.path.join(OUTDIR, stem + "_nodes.csv")
    vpath = os.path.join(OUTDIR, stem + "_veins.csv")
    N.to_csv(npath, index=False)
    E.to_csv(vpath, index=False)
    return npath, vpath, stale


def main():
    rows = []
    for folder, stem, spp, common, group, (T, L, W, H), use in LEAVES:
        t0 = time.time()
        npath, vpath, stale = convert(folder, stem)
        G = realleaf.load_matos(npath, vpath, name=common)
        s = realleaf.summary(G)
        pr = config.PercolationParams(mode="random", n_trials=2400, n_densities=40)
        res = percolation.find_pc(G, pr, rho_max=0.6)
        pc = float(res["p_c"])
        n_junc = sum(1 for _, d in G.degree() if d >= 3)
        print(f"{common:10s} N={s['n_nodes']:5d} E={s['n_edges']:5d} comps={s['n_components']} "
              f"<k>={s['mean_degree']:.3f} loop(nonbridge)={s['loop_fraction_nonbridge']:.3f} "
              f"p_c={pc:.4f} (crossing {res['p_c_crossing']:.4f})  stale rows cut {stale}  "
              f"{time.time()-t0:.0f}s", flush=True)
        if use:
            rows.append({"species": spp, "common_name": common, "group": group, "plant_id": 1, "leaf_id": 1,
                         "window_id": 1, "collection_date": "",
                         "window_mm2": round(W * H * 0.0016 ** 2, 2), "n_junctions": n_junc,
                         "mean_degree": round(s["mean_degree"], 4),
                         "loop_fraction": round(s["loop_fraction_nonbridge"], 4), "p_c": round(pc, 4),
                         "notes": f"LeafVeinCNN v2.14 as traced; crop T{T} L{L} W{W} H{H}; "
                                  f"N={s['n_nodes']} E={s['n_edges']}; 2400 trials, seed 1"})
    with open(OUTCSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("wrote", os.path.relpath(OUTCSV, ROOT))


if __name__ == "__main__":
    main()
