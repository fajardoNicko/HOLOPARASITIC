r"""
build_cohort.py — assemble the definitive analysis cohort with one auditable
inclusion criterion, joining every screen computed so far.

By this point three independent characterizations exist on disk:
    data/characterization.csv   topology, D, geometry, conductance (Phase 3)
    data/boundary_check.csv     the cropping artifact per leaf (boundary.py)
    UCBG..._metadata.csv        Matos' extraction-quality flags (metadata.py)

This script joins them and applies the inclusion criterion that the analyses
above established, producing the single list of leaves the percolation study
runs on. The criterion is deliberately structural — every clause is a property
of the network or its provenance, decided BEFORE any p_c is computed, so
inclusion cannot be reverse-engineered from the result:

    INCLUDE a leaf iff
        n_edges          >= MIN_EDGES        (finite-size resolvability)
        n_cycles         >= 1                (a transition can exist at all)
        cut_end_frac     <= MAX_CUT_END      (cropping artifact negligible)
        |mean_deg_shift| <= MAX_SHIFT        (cropping does not bias <k>)

Quality flags (A/B/C/D) are recorded but DO NOT gate inclusion: run_quality_check
showed the flags track leaf identity, not vein-count error, so excluding on them
would bias the sample rather than clean it. They are carried through instead as a
sensitivity variable — the core analysis is repeated on clean-A-only downstream.

    ...python.exe scripts\build_cohort.py --data-dir DIR

Outputs
    data/cohort.csv     every leaf, every screen value, include flag + reason
    data/cohort.json    the criterion + the included/excluded partition
"""

import os
import sys
import csv
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import metadata as md

# --- the inclusion criterion, in one place -----------------------------------
MIN_EDGES = 2000        # finite-size resolvability; below this the crop artifact
                        # starts to dominate <k>
MIN_CYCLES = 1          # no loops -> no percolation transition
MAX_CUT_END = 0.05      # <=5% of terminals may be window cut-ends
MAX_SHIFT = 0.05        # stripping cut-ends may move <k> by at most this


def _num(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _load(path, key="name"):
    if not os.path.exists(path):
        return {}
    with open(path, newline="") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser(description="Assemble the analysis cohort.")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--min-edges", type=int, default=MIN_EDGES)
    ap.add_argument("--max-cut-end", type=float, default=MAX_CUT_END)
    ap.add_argument("--max-shift", type=float, default=MAX_SHIFT)
    args = ap.parse_args()

    datadir = os.path.join(ROOT, config.PATHS.data)
    ch = _load(os.path.join(datadir, "characterization.csv"))
    bd = _load(os.path.join(datadir, "boundary_check.csv"))
    if not ch:
        print("Run scripts/run_characterize.py first.")
        return
    if not bd:
        print("Run scripts/run_boundary_check.py first.")
        return
    ddir = args.data_dir if os.path.isabs(args.data_dir) \
        else os.path.join(ROOT, args.data_dir)
    meta = md.load_metadata(ddir)

    rows = []
    for name, c in ch.items():
        b = bd.get(name, {})
        m = meta.get(name, {})
        E = _num(c.get("n_edges")) or 0
        cyc = _num(c.get("n_cycles")) or 0
        cut = _num(b.get("boundary_terminal_frac"))
        shift = abs(_num(b.get("mean_degree_shift")) or 0.0)

        reasons = []
        if E < args.min_edges:
            reasons.append(f"n_edges {int(E)} < {args.min_edges}")
        if cyc < MIN_CYCLES:
            reasons.append("acyclic")
        if cut is not None and cut > args.max_cut_end:
            reasons.append(f"cut-end {cut:.0%} > {args.max_cut_end:.0%}")
        if shift > args.max_shift:
            reasons.append(f"<k> shift {shift:.3f} > {args.max_shift}")
        include = not reasons

        rows.append({
            "name": name,
            "n_nodes": int(_num(c.get("n_nodes")) or 0),
            "n_edges": int(E),
            "n_cycles": int(cyc),
            "mean_degree": _num(c.get("mean_degree")),
            "mean_degree_interior": _num(b.get("mean_degree_interior")),
            "loop_fraction": _num(c.get("loop_fraction")),
            "D": _num(c.get("D")),
            "cut_end_frac": cut,
            "mean_degree_shift": shift,
            "quality": m.get("quality", ""),
            "clean_A": bool(m.get("clean")),
            "is_crop": str(b.get("is_crop", "")).lower() in ("true", "1"),
            "include": include,
            "exclude_reason": "" if include else "; ".join(reasons),
        })

    rows.sort(key=lambda r: (not r["include"], -r["n_edges"]))
    incl = [r for r in rows if r["include"]]
    excl = [r for r in rows if not r["include"]]

    # --- report the cohort's characteristics (what Phase 4 must reproduce) ----
    def stat(field, rs):
        v = np.array([r[field] for r in rs
                      if isinstance(r[field], (int, float))], float)
        v = v[np.isfinite(v)]
        if not v.size:
            return None
        return {"median": float(np.median(v)), "min": float(v.min()),
                "max": float(v.max()), "n": int(v.size)}

    worst_cut = max((r["cut_end_frac"] for r in incl
                     if r["cut_end_frac"] is not None), default=None)
    worst_shift = max((r["mean_degree_shift"] for r in incl), default=None)
    clean_in = sum(1 for r in incl if r["clean_A"])

    summary = {
        "criterion": {"min_edges": args.min_edges, "min_cycles": MIN_CYCLES,
                      "max_cut_end_frac": args.max_cut_end,
                      "max_mean_degree_shift": args.max_shift,
                      "quality_flags_gate_inclusion": False},
        "n_total": len(rows), "n_included": len(incl), "n_excluded": len(excl),
        "n_clean_A_in_cohort": clean_in,
        "worst_included_cut_end_frac": worst_cut,
        "worst_included_mean_degree_shift": worst_shift,
        "cohort_stats": {f: stat(f, incl) for f in
                         ("n_edges", "mean_degree", "loop_fraction", "D")},
        "excluded": [{"name": r["name"], "n_edges": r["n_edges"],
                      "reason": r["exclude_reason"]} for r in excl],
    }

    with open(os.path.join(datadir, "cohort.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(datadir, "cohort.json"), "w") as f:
        json.dump({"summary": summary, "cohort": rows}, f, indent=2)

    print("=" * 78)
    print("ANALYSIS COHORT — combined structural inclusion criterion")
    print("=" * 78)
    print(f"  min_edges >= {args.min_edges}   n_cycles >= {MIN_CYCLES}   "
          f"cut-end <= {args.max_cut_end:.0%}   |<k> shift| <= {args.max_shift}")
    print(f"  quality flags recorded but NOT gating (sensitivity variable)")
    print("-" * 78)
    print(f"  INCLUDED  {len(incl):3d}   (clean-A among them: {clean_in})")
    print(f"  excluded  {len(excl):3d}")
    print(f"  worst artifact still in cohort: cut-end="
          f"{(worst_cut or 0):.3f}  |<k> shift|={(worst_shift or 0):.4f}")
    for f in ("n_edges", "mean_degree", "loop_fraction", "D"):
        s = summary["cohort_stats"][f]
        if s:
            print(f"  {f:14s} median={s['median']:9.3f}  "
                  f"range {s['min']:.3f}..{s['max']:.3f}")
    print("-" * 78)
    print("  excluded leaves:")
    for r in excl:
        print(f"    {r['name']:10s} E={r['n_edges']:6d}  {r['exclude_reason']}")
    print(f"wrote data/cohort.csv + cohort.json  ({len(incl)} leaves for percolation)")


if __name__ == "__main__":
    main()
