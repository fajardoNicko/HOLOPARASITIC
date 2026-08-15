# -*- coding: utf-8 -*-
r"""
run_resistance_convention_sensitivity.py -- P1 audit item 8.

The Dryad deposit ships TWO resistance conventions for the same vein segments:

    Resistance_4 = l / r^4   "predicted resistance to flow based on Poiseuille flow"
    Resistance_2 = l / r^2   "predicted resistance based on the vein area", glossed
                             as treating resistance as scaling with the NUMBER of
                             equal-sized vessels in a bundle

realleaf._assign_conductances implements the r^4 convention, which is why the
solver reproduces Resistance_4 to ~1e-7: both sides assume the same formula. That
agreement is implementation VERIFICATION, not physical validation. The open
question is whether the study's hydraulic conclusions depend on the choice.

This script rebuilds each cohort leaf's network once and solves the baseline
source->terminal conductance under BOTH conventions, then rank-correlates each
against the measured Kleaf. If the two conventions rank species similarly, the
radius-inference vulnerability does not touch the reported hydraulic ordering.

NOTE the scope: the percolation results are purely topological (percolation.py
operates on the unweighted adjacency and on unweighted degree/betweenness), so
NO percolation result can be affected by this choice. Only the hydraulic
characterisation and the Kleaf check are at stake.

    python scripts/run_resistance_convention_sensitivity.py [--limit N]

Outputs data/resistance_convention_sensitivity.{csv,json}.  ASCII-only stdout.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from scipy import stats

from holoparasitic import realleaf, hydraulics

LEAFDIR = ROOT / "UCBG_venation_form_data" / "UCBG_venation_form_data"
KMAX = ROOT / "hydraulics" / "hydraulics" / "UCBG_venation_kmax.csv"
OUT_CSV = ROOT / "data" / "resistance_convention_sensitivity.csv"
OUT_JSON = ROOT / "data" / "resistance_convention_sensitivity.json"
FIELDS = ["spp_code", "N", "E", "k_model_r4", "k_model_r2", "kleaf_meas",
          "seconds"]


def _f(s):
    try:
        v = float(s)
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def measured_kleaf() -> dict:
    by: dict[str, list[float]] = {}
    if not KMAX.exists():
        return by
    with open(KMAX, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            code = (row.get("spp_code") or row.get("code") or "").strip()
            v = None
            for key in ("Kleaf", "kleaf", "Kmax", "kmax", "Kleaf_max"):
                if key in row:
                    v = _f(row[key])
                    if v is not None:
                        break
            if code and v is not None:
                by.setdefault(code, []).append(v)
    return {k: float(np.median(v)) for k, v in by.items()}


def set_conductance(G, exponent: int) -> None:
    """Re-assign g = (r/rmax)^exponent / (L/Lmean) on an already-built graph."""
    radii = np.array([d["radius"] for *_, d in G.edges(data=True)], float)
    lens = np.array([d["length"] for *_, d in G.edges(data=True)], float)
    rmax = radii.max() if radii.size else 1.0
    lmean = lens[lens > 0].mean() if np.any(lens > 0) else 1.0
    for _u, _v, d in G.edges(data=True):
        rn = d["radius"] / rmax
        ln = max(d["length"] / lmean, 1e-9)
        g = (rn ** exponent) / ln
        d["conductance"] = float(g)
        d["resistance"] = float(1.0 / g) if g > 0 else float("inf")


def source_conductance(G) -> float:
    """Effective source->terminal conductance = total flux leaving the root,
    divided by the imposed potential difference (which is 1.0 MPa here)."""
    solver, psi = hydraulics.baseline_potentials(G)
    root = solver.root
    q = 0.0
    for u, v, d in G.edges(data=True):
        if u == root:
            q += d["conductance"] * (psi[solver.index[u]] - psi[solver.index[v]])
        elif v == root:
            q += d["conductance"] * (psi[solver.index[v]] - psi[solver.index[u]])
    return float(q)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    meas = measured_kleaf()
    pairs = realleaf.find_leaf_pairs(str(LEAFDIR))
    if args.limit:
        pairs = pairs[:args.limit]
    print("found %d leaf pairs; %d species with measured Kleaf"
          % (len(pairs), len(meas)))

    done = set()
    if OUT_CSV.exists():
        with open(OUT_CSV, newline="") as f:
            done = {r["spp_code"] for r in csv.DictReader(f)}
        print("resuming: %d already done" % len(done))

    new = not OUT_CSV.exists()
    with open(OUT_CSV, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for i, (code, nodes_csv, veins_csv) in enumerate(pairs, 1):
            if code in done:
                continue
            t0 = time.time()
            try:
                G = realleaf.load_matos(nodes_csv, veins_csv)
                set_conductance(G, 4)
                k4 = source_conductance(G)
                set_conductance(G, 2)
                k2 = source_conductance(G)
                row = {"spp_code": code, "N": G.number_of_nodes(),
                       "E": G.number_of_edges(), "k_model_r4": k4,
                       "k_model_r2": k2, "kleaf_meas": meas.get(code, ""),
                       "seconds": round(time.time() - t0, 1)}
            except Exception as exc:  # keep the sweep resumable
                print("  [%d/%d] %s FAILED: %s" % (i, len(pairs), code, exc))
                continue
            w.writerow(row)
            fh.flush()
            print("  [%d/%d] %s N=%d k_r4=%.4g k_r2=%.4g (%.1fs)"
                  % (i, len(pairs), code, row["N"], k4, k2, row["seconds"]))

    # ---- summarise ---------------------------------------------------------
    rows = list(csv.DictReader(open(OUT_CSV, newline="")))
    k4 = np.array([float(r["k_model_r4"]) for r in rows])
    k2 = np.array([float(r["k_model_r2"]) for r in rows])
    has = [i for i, r in enumerate(rows) if _f(r["kleaf_meas"]) is not None]
    km = np.array([float(rows[i]["kleaf_meas"]) for i in has])

    summary = {
        "_purpose": "does the l/r^4 vs l/r^2 convention change the hydraulic "
                    "conclusions? See SECOND_PASS_AUDIT.md Part VI item 8",
        "_generated_by": "scripts/run_resistance_convention_sensitivity.py",
        "n_leaves": len(rows),
        "n_with_measured_kleaf": len(has),
        "agreement_between_conventions": {
            "spearman_r4_vs_r2": round(float(stats.spearmanr(k4, k2)[0]), 5),
            "pearson_log_r4_vs_log_r2": round(float(stats.pearsonr(
                np.log10(k4[k4 > 0]), np.log10(k2[k4 > 0]))[0]), 5),
            "median_ratio_r4_over_r2": round(float(np.median(
                k4[(k2 > 0) & (k4 > 0)] / k2[(k2 > 0) & (k4 > 0)])), 6),
            "n_zero_or_degenerate_conductance": int(((k2 <= 0) | (k4 <= 0)).sum()),
        },
        "percolation_is_unaffected": (
            "percolation.py operates on the unweighted CSR adjacency and on "
            "unweighted degree/betweenness, so p_c does not depend on the "
            "conductance convention at all"),
    }
    if len(has) >= 8:
        s4 = stats.spearmanr(k4[has], km)
        s2 = stats.spearmanr(k2[has], km)
        summary["kleaf_validation"] = {
            "n": len(has),
            "spearman_r4_vs_measured": [round(float(s4[0]), 4), float(s4[1])],
            "spearman_r2_vs_measured": [round(float(s2[0]), 4), float(s2[1])],
        }
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\n" + json.dumps(summary, indent=2))
    print("\nwrote %s and %s" % (OUT_CSV.relative_to(ROOT),
                                 OUT_JSON.relative_to(ROOT)))


if __name__ == "__main__":
    main()
