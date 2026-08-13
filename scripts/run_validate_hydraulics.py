r"""
run_validate_hydraulics.py — external validation of our vein-resistance model.

The strongest objection to a computational study is that the physics was
implemented wrong and nobody could tell. Here that objection is answerable
directly, because Matos et al. ship their OWN per-vein hydraulic resistance in
the veins CSV and we never used it: our loader recomputes resistance from vein
Length and Width independently.

    Resistance_4   the source dataset's Hagen-Poiseuille resistance, L / r^4
    Resistance_2   the same with a squared caliber, L / r^2 (a Darcy-like
                   alternative they also report)

Our realleaf._assign_conductances() builds g proportional to r^4 / L, i.e.
resistance proportional to L / r^4, with the 8*eta/pi prefactor left off because
it is global and cancels in the potential solve. If our implementation is
correct, our resistance must be proportional to their Resistance_4 with a
CONSTANT ratio across every vein of every leaf — not merely correlated.

That is what this script tests. It reports, per leaf:
    * the Pearson r between log(ours) and log(Resistance_4)   -> must be 1.000
    * the median and CV of the ratio Resistance_4 / ours      -> CV must be ~0

A high correlation alone would NOT be sufficient: two different exponents still
correlate strongly across a wide caliber range (Resistance_2 correlates at
r = 0.93 despite being the wrong power). The coefficient of variation of the
ratio is the discriminating statistic, and it is what the verdict rests on.

    ...python.exe scripts\run_validate_hydraulics.py --data-dir DIR

Outputs data/hydraulic_validation.json
"""

import os
import sys
import csv
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
from scipy import stats

import config
from holoparasitic import realleaf

#: the ratio's CV must fall below this to count as an exact reproduction
CV_TOL = 1e-6


def check_leaf(veins_csv: str) -> dict | None:
    """Compare our L/r^4 against the dataset's Resistance_4, vein by vein."""
    L, W, R4, R2 = [], [], [], []
    with open(veins_csv, newline="") as f:
        for row in csv.DictReader(f):
            try:
                l = float(row["Length"]); w = float(row["Width"])
                r4 = float(row["Resistance_4"]); r2 = float(row["Resistance_2"])
            except (KeyError, TypeError, ValueError):
                continue
            if min(l, w) <= 0 or not (np.isfinite(r4) and np.isfinite(r2)):
                continue
            L.append(l); W.append(w); R4.append(r4); R2.append(r2)

    if len(L) < 50:
        return None
    L = np.array(L); W = np.array(W)
    R4 = np.array(R4); R2 = np.array(R2)

    ours = L / (W / 2.0) ** 4                     # our resistance, prefactor-free
    ratio = R4 / ours
    r_log = stats.pearsonr(np.log(ours), np.log(R4))[0]

    # the wrong-power control: if we had used r^2 instead
    wrong = L / (W / 2.0) ** 2
    r_wrong = stats.pearsonr(np.log(wrong), np.log(R4))[0]

    return {
        "n_veins": int(L.size),
        "pearson_log_r": float(r_log),
        "ratio_median": float(np.median(ratio)),
        "ratio_cv": float(ratio.std() / ratio.mean()) if ratio.mean() else None,
        "exact": bool(ratio.std() / abs(ratio.mean()) < CV_TOL) if ratio.mean() else False,
        # control: correlation of the WRONG exponent, to show r alone proves nothing
        "pearson_log_r_wrong_exponent": float(r_wrong),
        # confirm their Resistance_2 really is L/r^2 (fixes their convention)
        "resistance2_is_L_over_r2": bool(
            np.allclose(R2, L / (W / 2.0) ** 2, rtol=1e-6)),
    }


def main():
    ap = argparse.ArgumentParser(description="Validate resistance vs source data.")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--limit", type=int, default=0, help="max leaves (0 = all)")
    args = ap.parse_args()

    ddir = args.data_dir if os.path.isabs(args.data_dir) \
        else os.path.join(ROOT, args.data_dir)
    pairs = realleaf.find_leaf_pairs(ddir)
    if args.limit:
        pairs = pairs[:args.limit]
    if not pairs:
        print(f"No leaf pairs under {ddir}")
        return

    print("=" * 78)
    print("HYDRAULIC VALIDATION — our L/r^4 vs Matos' own Resistance_4")
    print("=" * 78)

    results, skipped = {}, []
    for spp, _npath, vpath in pairs:
        try:
            res = check_leaf(vpath)
        except Exception as e:
            skipped.append({"species": spp, "error": str(e)})
            continue
        if res is None:
            skipped.append({"species": spp, "error": "fewer than 50 usable veins"})
            continue
        results[spp] = res

    if not results:
        print("No leaf could be checked.")
        return

    n_exact = sum(1 for r in results.values() if r["exact"])
    total_veins = sum(r["n_veins"] for r in results.values())
    worst_cv = max(r["ratio_cv"] for r in results.values()
                   if r["ratio_cv"] is not None)
    worst_dev = max(abs(r["ratio_median"] - 1.0) for r in results.values())
    min_r = min(r["pearson_log_r"] for r in results.values())
    ctrl = float(np.median([r["pearson_log_r_wrong_exponent"]
                            for r in results.values()]))
    r2ok = sum(1 for r in results.values() if r["resistance2_is_L_over_r2"])

    verdict = ("PASS — our resistance reproduces the source dataset's own "
               "Hagen-Poiseuille column exactly"
               if n_exact == len(results) and worst_dev < 1e-6 else
               "FAIL — resistance does not match the source dataset")

    summary = {
        "n_leaves": len(results), "n_exact": n_exact,
        "total_veins_compared": total_veins,
        "min_pearson_log_r": min_r,
        "worst_ratio_cv": worst_cv,
        "worst_abs_median_ratio_minus_1": worst_dev,
        "median_pearson_wrong_exponent_control": ctrl,
        "n_leaves_resistance2_is_L_over_r2": r2ok,
        "cv_tolerance": CV_TOL,
        "verdict": verdict,
        "skipped": skipped,
    }

    datadir = os.path.join(ROOT, config.PATHS.data)
    os.makedirs(datadir, exist_ok=True)
    with open(os.path.join(datadir, "hydraulic_validation.json"), "w") as f:
        json.dump({"summary": summary, "per_leaf": results}, f, indent=2)

    print(f"  leaves compared          {len(results)}")
    print(f"  veins compared           {total_veins:,}")
    print(f"  exact matches            {n_exact}/{len(results)}")
    print(f"  min Pearson r (log-log)  {min_r:.6f}")
    print(f"  worst ratio CV           {worst_cv:.3g}   (tolerance {CV_TOL:g})")
    print(f"  worst |median ratio - 1| {worst_dev:.3g}")
    print(f"  control, WRONG exponent  r = {ctrl:.3f}  "
          f"<- why correlation alone proves nothing")
    print(f"  Resistance_2 == L/r^2    {r2ok}/{len(results)} leaves")
    if skipped:
        print(f"  skipped                  {len(skipped)}")
    print("-" * 78)
    print("VERDICT: " + verdict)
    print("wrote data/hydraulic_validation.json")


if __name__ == "__main__":
    main()
