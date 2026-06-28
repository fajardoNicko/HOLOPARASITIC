"""
export_csv.py — turn a results .npz into human-readable CSV tables you can open
in Excel / VS Code or paste into the paper.

    C:\\laragon\\bin\\python\\python-3.13\\python.exe scripts\\export_csv.py
    ...\\python.exe scripts\\export_csv.py data\\results_preview.npz

Writes into data/csv/:
    sigmoid.csv     rho, p_collapse, gcc_fraction   (the hero curve, 50 rows)
    pc_vs_D.csv     D, p_c                           (threshold vs dimension)
    pc_surface.csv  p_c table: rows = D, columns = K_h   (the heatmap)
"""

import os
import sys
import csv
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "results.npz")
if not os.path.exists(src):
    src = os.path.join("data", "results_preview.npz")
outdir = os.path.join("data", "csv")
os.makedirs(outdir, exist_ok=True)

z = np.load(src, allow_pickle=True)
keys = set(z.files)
print(f"reading {src}  ({len(keys)} arrays)")


def write_rows(name, header, rows):
    path = os.path.join(outdir, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path}  ({len(rows)} rows)")


# 1) hero sigmoid -------------------------------------------------------
if {"rhos", "p_collapse", "gcc_fraction"} <= keys:
    rows = [[f"{r:.6f}", f"{p:.6f}", f"{g:.6f}"]
            for r, p, g in zip(z["rhos"], z["p_collapse"], z["gcc_fraction"])]
    write_rows("sigmoid.csv", ["rho", "p_collapse", "gcc_fraction"], rows)

# 2) p_c vs D -----------------------------------------------------------
if {"pcd_D", "pcd_pc"} <= keys:
    rows = [[f"{d:.4f}", f"{p:.4f}"] for d, p in zip(z["pcd_D"], z["pcd_pc"])]
    write_rows("pc_vs_D.csv", ["D", "p_c"], rows)

# 3) (K_h, D) surface as a table ---------------------------------------
if {"surface_D", "surface_kh", "surface_pc"} <= keys:
    D, kh, pc = z["surface_D"], z["surface_kh"], z["surface_pc"]
    header = ["D \\ K_h"] + [f"{k:.2f}" for k in kh]
    rows = [[f"{D[i]:.4f}"] + [f"{pc[i, j]:.4f}" for j in range(len(kh))]
            for i in range(len(D))]
    write_rows("pc_surface.csv", header, rows)

print("done.")
