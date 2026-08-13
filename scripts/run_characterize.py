r"""
run_characterize.py — PHASE 3 driver: characterize every real leaf network.

Walks the Matos venation-form data directory, loads each species' network, and
computes its full architectural + hydraulic profile. Cheap (no Monte Carlo), so
the whole 120-leaf dataset runs in minutes and yields:

  * the SOP 1 results table (fractal dimension, conductance, GCC, topology)
  * the calibration targets for the Phase 4 synthetic generator
  * the structural basis for the percolation-validity screen

    ...python.exe scripts\run_characterize.py --data-dir DIR
    ...python.exe scripts\run_characterize.py --data-dir DIR --betweenness

Outputs
    data/characterization.csv     one row per leaf (all metrics)
    data/characterization.json    the same, plus the aggregate profile
    data/species/<spp>.json       per-species profile
"""

import os
import sys
import csv
import json
import glob
import time
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import realleaf, characterize as ch


find_pairs = realleaf.find_leaf_pairs      # shared, stem-mismatch tolerant


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Phase 3: characterize real leaves.")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--betweenness", action="store_true",
                    help="also compute approximate betweenness (slow)")
    ap.add_argument("--min-edges", type=int, default=500,
                    help="validity screen: minimum veins (default 500)")
    args = ap.parse_args()

    ddir = args.data_dir if os.path.isabs(args.data_dir) \
        else os.path.join(ROOT, args.data_dir)
    pairs = find_pairs(ddir)
    if args.limit:
        pairs = pairs[:args.limit]
    if not pairs:
        print(f"No *_nodes.csv/*_veins.csv pairs under {ddir}")
        return

    datadir = os.path.join(ROOT, config.PATHS.data)
    sppdir = os.path.join(datadir, "species")
    os.makedirs(sppdir, exist_ok=True)

    print("=" * 78, flush=True)
    print(f"PHASE 3 — biological characterization · {len(pairs)} leaves", flush=True)
    print("=" * 78, flush=True)

    profiles, failed = [], []
    t_start = time.time()
    for i, (spp, npath, vpath) in enumerate(pairs, 1):
        t0 = time.time()
        try:
            G = realleaf.load_matos(npath, vpath, name=spp)
            prof = ch.characterize(G, name=spp, betweenness=args.betweenness)
        except Exception as e:
            failed.append({"species": spp, "error": str(e)})
            print(f"[{i:3d}/{len(pairs)}] {spp:10s} FAILED — {e}", flush=True)
            continue

        ok, reason = ch.is_valid_for_percolation(prof, min_edges=args.min_edges)
        prof["valid_for_percolation"] = ok
        prof["validity_note"] = reason
        profiles.append(prof)

        with open(os.path.join(sppdir, f"{spp}.json"), "w") as f:
            json.dump(prof, f, indent=2)

        Dtxt = f"{prof['D']:.3f}" if prof["D"] is not None else "  n/a"
        print(f"[{i:3d}/{len(pairs)}] {spp:10s} N={prof['n_nodes']:7,} "
              f"E={prof['n_edges']:7,} <k>={prof['mean_degree']:5.2f} "
              f"cyc={prof['n_cycles']:6,} D={Dtxt} "
              f"{'' if ok else '  EXCLUDED: ' + reason}  ({time.time()-t0:.1f}s)",
              flush=True)

    if not profiles:
        print("No leaves characterized.")
        return

    # ---- write the per-leaf table -----------------------------------------
    keys = sorted({k for p in profiles for k in p})
    keys = ["name", "n_nodes", "n_edges", "mean_degree", "n_cycles",
            "cycle_density", "loop_fraction", "D", "effective_conductance",
            "gcc_fraction", "valid_for_percolation"] + \
           [k for k in keys if k not in {
               "name", "n_nodes", "n_edges", "mean_degree", "n_cycles",
               "cycle_density", "loop_fraction", "D", "effective_conductance",
               "gcc_fraction", "valid_for_percolation"}]
    csv_path = os.path.join(datadir, "characterization.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(profiles)

    # ---- aggregate profile (the Phase 4 calibration target) ----------------
    valid = [p for p in profiles if p["valid_for_percolation"]]
    def agg(field, rows):
        v = [r[field] for r in rows
             if isinstance(r.get(field), (int, float)) and np.isfinite(r[field])]
        if not v:
            return None
        v = np.asarray(v, float)
        return {"median": float(np.median(v)), "mean": float(v.mean()),
                "sd": float(v.std(ddof=1)) if v.size > 1 else 0.0,
                "min": float(v.min()), "max": float(v.max()), "n": int(v.size)}

    fields = ["D", "mean_degree", "loop_fraction", "cycle_density", "n_nodes",
              "n_edges", "effective_conductance", "hydraulic_diameter",
              "mean_radius", "mean_vein_length", "geom_branch_angle_deg",
              "geom_branch_angle_std", "geom_murray_exponent",
              "geom_daughter_symmetry", "geom_length_ratio"]
    summary = {
        "n_leaves_total": len(profiles),
        "n_valid": len(valid),
        "n_excluded": len(profiles) - len(valid),
        "n_failed": len(failed),
        "min_edges_criterion": args.min_edges,
        "aggregate_all": {f: agg(f, profiles) for f in fields},
        "aggregate_valid": {f: agg(f, valid) for f in fields},
        "excluded": [{"species": p["name"], "reason": p["validity_note"]}
                     for p in profiles if not p["valid_for_percolation"]],
        "failed": failed,
    }
    with open(os.path.join(datadir, "characterization.json"), "w") as f:
        json.dump({"summary": summary, "profiles": profiles}, f, indent=2)

    # ---- report ------------------------------------------------------------
    print("-" * 78, flush=True)
    print(f"characterized {len(profiles)}  ·  valid {len(valid)}  ·  "
          f"excluded {len(profiles)-len(valid)}  ·  failed {len(failed)}  "
          f"({time.time()-t_start:.0f}s)", flush=True)
    for f in ("D", "mean_degree", "loop_fraction", "effective_conductance",
              "geom_branch_angle_deg", "geom_murray_exponent",
              "geom_daughter_symmetry"):
        a = summary["aggregate_valid"].get(f)
        if a:
            print(f"  {f:26s} median={a['median']:8.3f}  "
                  f"range {a['min']:.3f}..{a['max']:.3f}  (n={a['n']})",
                  flush=True)
    if summary["excluded"]:
        print(f"  excluded: "
              f"{', '.join(e['species'] for e in summary['excluded'][:12])}"
              f"{' …' if len(summary['excluded']) > 12 else ''}", flush=True)
    print(f"wrote {os.path.relpath(csv_path, ROOT)} + characterization.json + "
          f"data/species/*.json", flush=True)


if __name__ == "__main__":
    main()
