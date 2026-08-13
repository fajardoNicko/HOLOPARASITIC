r"""
run_boundary_check.py — set the inclusion threshold from the data, not by fiat.

100 of the 120 Matos networks are cropped WINDOWS of leaves. Veins severed by
the window edge terminate in degree-1 nodes that are cut ends, not real vein
endings, and they depress mean degree. Since mean degree is the variable our
headline result rests on, the size at which this artifact stops mattering is
exactly the size at which a network becomes admissible.

That is a better basis for an inclusion criterion than a round number chosen in
advance. This script measures the artifact across every leaf and reports the
smallest network size above which it is negligible.

    ...python.exe scripts\run_boundary_check.py --data-dir DIR
    ...python.exe scripts\run_boundary_check.py --data-dir DIR --max-bt-frac 0.05

Outputs
    data/boundary_check.csv    per-leaf raw vs interior-corrected topology
    data/boundary_check.json   the same, plus the recommended threshold
"""

import os
import sys
import csv
import json
import time
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
from scipy import stats

import config
from holoparasitic import realleaf, boundary, metadata as md


def main():
    ap = argparse.ArgumentParser(description="Cropping-artifact check.")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--margin-frac", type=float, default=0.02)
    ap.add_argument("--max-bt-frac", type=float, default=0.05,
                    help="largest tolerable fraction of terminals that are cut "
                         "ends (default 0.05)")
    ap.add_argument("--max-shift", type=float, default=0.05,
                    help="largest tolerable mean-degree distortion (default 0.05)")
    args = ap.parse_args()

    ddir = args.data_dir if os.path.isabs(args.data_dir) \
        else os.path.join(ROOT, args.data_dir)
    pairs = realleaf.find_leaf_pairs(ddir)
    if args.limit:
        pairs = pairs[:args.limit]
    if not pairs:
        print(f"No leaf pairs under {ddir}")
        return
    meta = md.load_metadata(ddir)

    print("=" * 82)
    print(f"CROPPING-ARTIFACT CHECK · {len(pairs)} leaves · "
          f"margin = {args.margin_frac:.1%} of the short side")
    print("=" * 82)

    rows, failed = [], []
    t0 = time.time()
    for i, (spp, npath, vpath) in enumerate(pairs, 1):
        try:
            G = realleaf.load_matos(npath, vpath, name=spp)
            p = boundary.boundary_profile(G, margin_frac=args.margin_frac)
        except Exception as e:
            failed.append({"species": spp, "error": str(e)})
            print(f"[{i:3d}/{len(pairs)}] {spp:10s} FAILED — {e}", flush=True)
            continue
        m = meta.get(spp, {})
        p["name"] = spp
        p["is_crop"] = "crop" in os.path.basename(npath).lower()
        p["quality"] = m.get("quality", "")
        p["n_edges"] = G.number_of_edges()
        p["n_nodes"] = G.number_of_nodes()
        rows.append(p)
        print(f"[{i:3d}/{len(pairs)}] {spp:10s} E={p['n_edges']:7,} "
              f"<k>={p['mean_degree']:5.3f}->{p['mean_degree_interior']:5.3f} "
              f"({p['mean_degree_shift']:+.3f})  cut-end frac="
              f"{p['boundary_terminal_frac']:.3f}", flush=True)

    if not rows:
        print("Nothing measured.")
        return

    E = np.array([r["n_edges"] for r in rows], float)
    bt = np.array([r["boundary_terminal_frac"] for r in rows], float)
    sh = np.abs(np.array([r["mean_degree_shift"] for r in rows], float))

    # --- does the artifact really scale with size, as the mechanism predicts? --
    ok = E > 0
    rho_bt, p_bt = stats.spearmanr(np.log(E[ok]), bt[ok])
    rho_sh, p_sh = stats.spearmanr(np.log(E[ok]), sh[ok])

    # --- smallest size above which EVERY leaf is under tolerance --------------
    order = np.argsort(E)
    Es, bts, shs = E[order], bt[order], sh[order]
    threshold = None
    for j in range(len(Es)):
        if np.all(bts[j:] <= args.max_bt_frac) and np.all(shs[j:] <= args.max_shift):
            threshold = float(Es[j])
            break

    clean_n = int(np.sum((bt <= args.max_bt_frac) & (sh <= args.max_shift)))
    summary = {
        "n_leaves": len(rows),
        "margin_frac": args.margin_frac,
        "tolerances": {"max_boundary_terminal_frac": args.max_bt_frac,
                       "max_mean_degree_shift": args.max_shift},
        "spearman_logE_vs_boundary_frac": {"rho": float(rho_bt), "p": float(p_bt)},
        "spearman_logE_vs_abs_shift": {"rho": float(rho_sh), "p": float(p_sh)},
        "n_within_tolerance": clean_n,
        "recommended_min_edges": threshold,
        "median_boundary_terminal_frac": float(np.median(bt)),
        "max_boundary_terminal_frac": float(bt.max()),
        "median_abs_shift": float(np.median(sh)),
        "max_abs_shift": float(sh.max()),
        "n_crop_files": int(sum(1 for r in rows if r["is_crop"])),
        "failed": failed,
    }

    datadir = os.path.join(ROOT, config.PATHS.data)
    os.makedirs(datadir, exist_ok=True)
    keys = ["name", "n_nodes", "n_edges", "is_crop", "quality", "mean_degree",
            "mean_degree_interior", "mean_degree_shift",
            "boundary_terminal_frac", "boundary_node_frac",
            "n_terminals", "n_boundary_terminals", "n_interior_terminals",
            "n_nodes_interior", "n_edges_interior", "n_cycles_interior",
            "loop_fraction_interior", "sqrt_area_over_perimeter", "margin_frac"]
    cpath = os.path.join(datadir, "boundary_check.csv")
    with open(cpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(datadir, "boundary_check.json"), "w") as f:
        json.dump({"summary": summary, "per_leaf": rows}, f, indent=2)

    print("-" * 82)
    print(f"  crop files                     {summary['n_crop_files']}/{len(rows)}")
    print(f"  cut-end fraction               median {np.median(bt):.3f}  "
          f"max {bt.max():.3f}")
    print(f"  |mean-degree distortion|       median {np.median(sh):.4f}  "
          f"max {sh.max():.4f}")
    print(f"  artifact vs size (Spearman)    cut-end frac: rho={rho_bt:+.3f} "
          f"p={p_bt:.3g}   |shift|: rho={rho_sh:+.3f} p={p_sh:.3g}")
    print(f"  within tolerance               {clean_n}/{len(rows)}")
    if threshold is not None:
        print(f"  RECOMMENDED min_edges          {threshold:,.0f}  "
              f"(every leaf at or above this is within tolerance)")
    else:
        print("  RECOMMENDED min_edges          none — artifact never becomes "
              "uniformly negligible")
    print(f"wrote {os.path.relpath(cpath, ROOT)} + boundary_check.json")


if __name__ == "__main__":
    main()
