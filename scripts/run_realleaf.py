r"""
run_realleaf.py — PHASE 1 of the hybrid: real Matos leaf networks get the physics.

For each leaf (a <spp>_nodes.csv + <spp>_veins.csv pair from Matos'
UCBG_venation_form_data.zip) it:
  1. loads the real extracted network (holoparasitic.realleaf.load_matos),
  2. measures its box-counting D with the SAME core used on synthetic networks,
  3. runs the SAME percolation engine to estimate p_c (random + degree attack;
     betweenness is optional — it is slow on large real graphs),
  4. optionally runs the coupled hydraulic model at a swept K_h.

Phase 2 (synthetic) is unchanged: scripts/run_full.py.

USAGE
  # point at the unzipped Matos data dir (folders or flat *_nodes.csv/*_veins.csv):
  ...python.exe scripts\run_realleaf.py --data-dir path\to\venation_form\data

  # limit how many leaves, and add the (slow) betweenness attack + hydraulic mode:
  ...python.exe scripts\run_realleaf.py --data-dir DIR --limit 20 --betweenness --hydraulic

Outputs data/realleaf_pc.csv and data/realleaf_summary.json, and (with the
synthetic curve in data/results.npz) prints where each real leaf's D lands on
the model's p_c-vs-D curve — the hybrid comparison.
"""

import os
import sys
import csv
import json
import glob
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import realleaf, fractal, percolation


def find_pairs(data_dir):
    """Return [(spp, nodes_csv, veins_csv)] discovered under data_dir.
    Matches <stem>_nodes.csv with <stem>_veins.csv (recursively)."""
    nodes = glob.glob(os.path.join(data_dir, "**", "*_nodes.csv"), recursive=True)
    pairs = []
    for npath in sorted(nodes):
        vpath = npath.replace("_nodes.csv", "_veins.csv")
        if os.path.exists(vpath):
            spp = os.path.basename(npath)[:-len("_nodes.csv")]
            pairs.append((spp, npath, vpath))
    return pairs


def model_curve():
    for f in ("results.npz", "results_preview.npz"):
        p = os.path.join(ROOT, config.PATHS.data, f)
        if os.path.exists(p):
            z = np.load(p, allow_pickle=True)
            if "pcd_D" in z.files:
                D = np.asarray(z["pcd_D"], float)
                pc = np.asarray(z["pcd_pc"], float)
                o = np.argsort(D)
                return D[o], pc[o]
    return None, None


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Phase 1: physics on real leaves.")
    ap.add_argument("--data-dir", required=True,
                    help="dir of Matos <spp>_nodes.csv / <spp>_veins.csv pairs")
    ap.add_argument("--limit", type=int, default=0, help="max leaves (0 = all)")
    ap.add_argument("--n-trials", type=int, default=40_000,
                    help="Monte Carlo trials per attack mode")
    ap.add_argument("--betweenness", action="store_true",
                    help="also run the (slow) betweenness-backbone attack")
    ap.add_argument("--hydraulic", action="store_true",
                    help="also run the coupled hydraulic mode (slower)")
    ap.add_argument("--k-h", type=float, default=config.K_H_DEFAULT,
                    help="haustorial sink strength for hydraulic mode")
    args = ap.parse_args()

    ddir = args.data_dir if os.path.isabs(args.data_dir) \
        else os.path.join(ROOT, args.data_dir)
    pairs = find_pairs(ddir)
    if args.limit:
        pairs = pairs[:args.limit]
    if not pairs:
        print(f"No *_nodes.csv/*_veins.csv pairs found under {ddir}")
        print("Unzip UCBG_venation_form_data.zip and point --data-dir at its "
              "'data' folder.")
        return

    D_grid, pc_grid = model_curve()
    print("=" * 70, flush=True)
    print(f"PHASE 1 — real leaf physics · {len(pairs)} leaves", flush=True)
    print("=" * 70, flush=True)

    rows = []
    for i, (spp, npath, vpath) in enumerate(pairs, 1):
        try:
            G = realleaf.load_matos(npath, vpath, name=spp)
        except Exception as e:
            print(f"[{i}/{len(pairs)}] {spp}: LOAD FAILED — {e}", flush=True)
            continue
        s = realleaf.summary(G)
        D = fractal.fractal_dimension(G)

        pp = config.PercolationParams(mode="random", n_trials=args.n_trials,
                                      n_densities=50)
        pc_rand = percolation.find_pc(G, pp)["p_c"]

        w_deg = percolation.importance_weights(G, list(G.nodes), metric="degree")
        tp = config.PercolationParams(mode="targeted",
                                      n_trials=max(20_000, args.n_trials // 2),
                                      n_densities=50)
        pc_deg = percolation.find_pc(G, tp, weights=w_deg)["p_c"]

        pc_btw = float("nan")
        if args.betweenness:
            w_btw = percolation.importance_weights(G, list(G.nodes),
                                                   metric="betweenness")
            pc_btw = percolation.find_pc(G, tp, weights=w_btw)["p_c"]

        pc_hyd = float("nan")
        if args.hydraulic:
            hp = config.PercolationParams(mode="hydraulic", n_trials=1500,
                                          n_densities=30)
            pc_hyd = percolation.find_pc(G, hp, k_h=args.k_h)["p_c"]

        pc_pred = (float(np.interp(D, D_grid, pc_grid))
                   if D_grid is not None else float("nan"))

        row = {"species": spp, "n_nodes": s["n_nodes"], "n_edges": s["n_edges"],
               "mean_degree": round(s["mean_degree"], 2),
               "loop_fraction": round(s["loop_fraction"], 3),
               "n_components": s["n_components"], "D": round(D, 4),
               "pc_random": round(pc_rand, 4), "pc_degree": round(pc_deg, 4),
               "pc_betweenness": round(pc_btw, 4), "pc_hydraulic": round(pc_hyd, 4),
               "pc_predicted_synthetic": round(pc_pred, 4)}
        rows.append(row)
        print(f"[{i}/{len(pairs)}] {spp:14s} N={s['n_nodes']:6d} "
              f"<k>={s['mean_degree']:.2f} loops={s['loop_fraction']:.2f} "
              f"D={D:.3f}  p_c(rand)={pc_rand:.3f} p_c(deg)={pc_deg:.3f}"
              + (f" p_c(btw)={pc_btw:.3f}" if args.betweenness else "")
              + (f" p_c(hyd)={pc_hyd:.3f}" if args.hydraulic else ""),
              flush=True)

    if not rows:
        print("No leaves loaded successfully.")
        return

    datadir = os.path.join(ROOT, config.PATHS.data)
    os.makedirs(datadir, exist_ok=True)
    csv_path = os.path.join(datadir, "realleaf_pc.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    D_arr = np.array([r["D"] for r in rows])
    pr_arr = np.array([r["pc_random"] for r in rows])
    summ = {"n_leaves": len(rows),
            "D_mean": float(D_arr.mean()), "D_min": float(D_arr.min()),
            "D_max": float(D_arr.max()),
            "pc_random_mean": float(np.nanmean(pr_arr)),
            "hybrid_note": "real-leaf D range vs synthetic p_c-vs-D curve"}
    if D_grid is not None and len(rows) >= 3:
        from scipy import stats
        pc_pred = np.array([r["pc_predicted_synthetic"] for r in rows])
        m = np.isfinite(pr_arr) & np.isfinite(pc_pred)
        if m.sum() >= 3:
            r, p = stats.pearsonr(D_arr[m], pr_arr[m])
            summ["pearson_D_vs_pc_random"] = {"r": float(r), "p": float(p),
                                              "n": int(m.sum())}
    with open(os.path.join(datadir, "realleaf_summary.json"), "w") as f:
        json.dump(summ, f, indent=2)

    print("-" * 70, flush=True)
    print(f"real D: {D_arr.min():.3f}..{D_arr.max():.3f}  "
          f"p_c(random): {np.nanmin(pr_arr):.3f}..{np.nanmax(pr_arr):.3f}",
          flush=True)
    if D_grid is not None:
        print(f"synthetic curve: D {D_grid[0]:.3f}..{D_grid[-1]:.3f} -> "
              f"p_c {pc_grid.min():.3f}..{pc_grid.max():.3f}  (hybrid overlay)",
              flush=True)
    print(f"wrote {os.path.relpath(csv_path, ROOT)} + realleaf_summary.json",
          flush=True)
    print("done.", flush=True)


if __name__ == "__main__":
    main()
