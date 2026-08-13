r"""
run_quality_check.py — does extraction quality bias the variable our result
rests on?

Our headline finding is that MEAN DEGREE, not fractal dimension, sets the
percolation threshold. Matos' own metadata flags 46 of 120 leaves as missing
minor veins (B) and 15 as carrying fabricated minor veins (C). Both act on the
minor vein orders, which is where the anastomoses are — i.e. both act directly
on mean degree. If B/C leaves differ systematically from clean (A) leaves, then
extraction error is confounded with the response variable and those leaves must
be excluded; if they do not, the full 120 can be kept and the larger n reported.

This script decides that empirically instead of assuming either way. It runs
AFTER run_characterize.py and needs no re-simulation.

    ...python.exe scripts\run_quality_check.py --data-dir DIR

Outputs
    data/characterization_annotated.csv   per-leaf table + quality columns
    data/quality_report.json              the group comparisons + verdict
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
from holoparasitic import metadata as md

#: metrics that extraction error could plausibly distort
METRICS = ["mean_degree", "loop_fraction", "cycle_density", "D",
           "n_edges", "mean_vein_length", "geom_branch_angle_deg",
           "geom_murray_exponent", "geom_daughter_symmetry"]


def _num(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _describe(vals):
    v = np.asarray([x for x in vals if x is not None], float)
    if v.size == 0:
        return None
    return {"n": int(v.size), "median": float(np.median(v)),
            "mean": float(v.mean()),
            "sd": float(v.std(ddof=1)) if v.size > 1 else 0.0}


def _compare(a, b):
    """Clean vs suspect: Mann-Whitney (no normality assumption on n~34 vs ~61)
    plus the rank-biserial effect size, which is what actually matters here —
    a significant but tiny shift does not justify discarding half the data."""
    a = np.asarray([x for x in a if x is not None], float)
    b = np.asarray([x for x in b if x is not None], float)
    if a.size < 3 or b.size < 3:
        return None
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    # rank-biserial r = 1 - 2U/(n1*n2); |r| .1 small, .3 medium, .5 large
    rb = 1.0 - (2.0 * u) / (a.size * b.size)
    return {"n_clean": int(a.size), "n_suspect": int(b.size),
            "median_clean": float(np.median(a)),
            "median_suspect": float(np.median(b)),
            "U": float(u), "p": float(p),
            "rank_biserial": float(rb),
            "effect": ("negligible" if abs(rb) < 0.10 else
                       "small" if abs(rb) < 0.30 else
                       "medium" if abs(rb) < 0.50 else "large")}


def main():
    ap = argparse.ArgumentParser(description="Quality-bias check on the real data.")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--alpha", type=float, default=0.05)
    args = ap.parse_args()

    ddir = args.data_dir if os.path.isabs(args.data_dir) \
        else os.path.join(ROOT, args.data_dir)
    meta = md.load_metadata(ddir)
    if not meta:
        print(f"No {md.METADATA_FILENAME} found under {ddir}")
        return

    datadir = os.path.join(ROOT, config.PATHS.data)
    cpath = os.path.join(datadir, "characterization.csv")
    if not os.path.exists(cpath):
        print("Run scripts/run_characterize.py first — no characterization.csv.")
        return
    with open(cpath, newline="") as f:
        rows = list(csv.DictReader(f))

    # ---- join ---------------------------------------------------------------
    unmatched = []
    for r in rows:
        m = meta.get(r["name"])
        if m is None:
            unmatched.append(r["name"])
            r.update({"quality": "", "quality_note": "no metadata row",
                      "hand_traced": "", "topology_suspect": "",
                      "damaged": "", "resolution_mm_px": ""})
            continue
        r.update({"quality": m["quality"],
                  "quality_note": md.quality_note(m),
                  "hand_traced": m["hand_traced"],
                  "topology_suspect": m["topology_suspect"],
                  "damaged": m["damaged"],
                  "resolution_mm_px": m["resolution_mm_px"]})

    apath = os.path.join(datadir, "characterization_annotated.csv")
    with open(apath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # ---- group comparisons --------------------------------------------------
    clean = [r for r in rows if meta.get(r["name"], {}).get("clean")]
    suspect = [r for r in rows if meta.get(r["name"], {}).get("topology_suspect")]
    missing = [r for r in rows if "B" in meta.get(r["name"], {}).get("quality_flags", [])]
    fake = [r for r in rows if "C" in meta.get(r["name"], {}).get("quality_flags", [])]
    damaged = [r for r in rows if meta.get(r["name"], {}).get("damaged")]

    groups = {"clean_A": clean, "topology_suspect_BC": suspect,
              "missing_veins_B": missing, "fake_veins_C": fake,
              "damaged_D": damaged, "all": rows}

    report = {
        "n_leaves": len(rows),
        "unmatched": unmatched,
        "group_sizes": {k: len(v) for k, v in groups.items()},
        "descriptives": {
            g: {m: _describe([_num(r.get(m)) for r in rs]) for m in METRICS}
            for g, rs in groups.items()},
        "clean_vs_suspect": {
            m: _compare([_num(r.get(m)) for r in clean],
                        [_num(r.get(m)) for r in suspect]) for m in METRICS},
    }

    # ---- mechanism + size-control tests (decide WHY the groups differ) -------
    # A naive clean-vs-suspect test cannot tell an extraction artifact from a
    # biased subsample. Two further tests disambiguate:
    #   (a) DIRECTION. If the flags act mechanically on connectivity, B (missing
    #       veins) and C (fake veins) must move mean degree in OPPOSITE
    #       directions. Same-direction shifts mean the flag tracks leaf identity,
    #       not vein-count error, and excluding B/C would bias the sample rather
    #       than clean it.
    #   (b) SIZE CONTROL. The groups differ in size; a shift that vanishes once
    #       log(edges) is partialled out is a size effect, not a quality effect.
    kd = lambda rs: [_num(r.get("mean_degree")) for r in rs]
    b_cmp = _compare(kd(clean), [_num(r.get("mean_degree")) for r in missing])
    c_cmp = _compare(kd(clean), [_num(r.get("mean_degree")) for r in fake])

    def _dir(cmp):
        if not cmp:
            return 0
        return -1 if cmp["median_suspect"] < cmp["median_clean"] else 1
    b_dir, c_dir = _dir(b_cmp), _dir(c_cmp)
    opposite = (b_dir * c_dir) < 0

    # size-controlled effect of "suspect" on mean degree: OLS beta with
    # log(n_edges) as covariate (no statsmodels dependency)
    suspect_beta = suspect_p = None
    xk = np.array([_num(r.get("mean_degree")) for r in rows], float)
    xe = np.array([_num(r.get("n_edges")) for r in rows], float)
    xs = np.array([1.0 if meta.get(r["name"], {}).get("topology_suspect") else 0.0
                   for r in rows], float)
    ok = np.isfinite(xk) & np.isfinite(xe) & (xe > 0)
    if ok.sum() >= 10:
        X = np.column_stack([np.ones(ok.sum()), xs[ok], np.log(xe[ok])])
        y = xk[ok]
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        dof = len(y) - X.shape[1]
        s2 = float(resid @ resid) / dof
        cov = s2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.diag(cov))
        t = beta[1] / se[1]
        suspect_beta = float(beta[1])
        suspect_p = float(2 * stats.t.sf(abs(t), dof))

    report["mechanism"] = {
        "clean_vs_B_missing": b_cmp, "clean_vs_C_fake": c_cmp,
        "B_direction": b_dir, "C_direction": c_dir,
        "flags_move_opposite_directions": bool(opposite),
        "size_controlled_suspect_beta": suspect_beta,
        "size_controlled_suspect_p": suspect_p,
    }

    # ---- verdict ------------------------------------------------------------
    key = report["clean_vs_suspect"].get("mean_degree")
    size_survives = (suspect_p is not None and suspect_p < args.alpha)
    if key is None:
        verdict = "inconclusive — too few leaves in one group"
    elif key["p"] >= args.alpha:
        verdict = ("KEEP ALL 120: no detectable shift in mean degree "
                   f"(p={key['p']:.3f}) — extraction flags do not bias the "
                   "response variable")
    elif opposite:
        verdict = ("EXCLUDE B/C: B and C move mean degree in OPPOSITE directions "
                   f"(B {'lower' if b_dir<0 else 'higher'}, "
                   f"C {'lower' if c_dir<0 else 'higher'} than clean) — the "
                   "signature of veins being mechanically mis-extracted, "
                   "confounding the response variable")
    else:
        # same-direction shift: the flag tracks leaf identity, not vein error
        size_txt = ("survives size control" if size_survives else
                    "does not survive size control")
        verdict = ("DO NOT EXCLUDE ON QUALITY — REPORT AS SENSITIVITY. B and C "
                   f"shift mean degree the SAME direction (both "
                   f"{'lower' if b_dir<0 else 'higher'} than clean), which is "
                   "sample bias (quality tracks leaf identity), not mechanical "
                   f"vein error; size-controlled suspect beta="
                   f"{suspect_beta:+.3f} ({size_txt}). Excluding B/C would bias "
                   "the sample. Instead rely on the size screen and repeat the "
                   "core p_c~<k> analysis on clean-A only as a robustness check.")
    report["verdict"] = verdict

    with open(os.path.join(datadir, "quality_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    # ---- print --------------------------------------------------------------
    print("=" * 78)
    print("EXTRACTION-QUALITY BIAS CHECK  (Matos metadata vs our measurements)")
    print("=" * 78)
    for g, rs in groups.items():
        print(f"  {g:22s} n={len(rs):3d}")
    if unmatched:
        print(f"  !! no metadata row for: {', '.join(unmatched)}")
    print("-" * 78)
    print(f"{'metric':26s} {'clean A':>10s} {'suspect BC':>11s} "
          f"{'p':>9s} {'effect':>12s}")
    for m in METRICS:
        c = report["clean_vs_suspect"].get(m)
        if not c:
            continue
        print(f"{m:26s} {c['median_clean']:10.3f} {c['median_suspect']:11.3f} "
              f"{c['p']:9.4g} {c['effect']:>12s}")
    print("-" * 78)
    mech = report["mechanism"]
    if b_cmp and c_cmp:
        print(f"mechanism  clean<k>={b_cmp['median_clean']:.3f}  "
              f"B(missing)<k>={b_cmp['median_suspect']:.3f}  "
              f"C(fake)<k>={c_cmp['median_suspect']:.3f}  "
              f"-> {'OPPOSITE' if mech['flags_move_opposite_directions'] else 'SAME'} direction")
    if mech["size_controlled_suspect_beta"] is not None:
        print(f"           size-controlled suspect beta="
              f"{mech['size_controlled_suspect_beta']:+.3f} "
              f"(p={mech['size_controlled_suspect_p']:.3g}, covariate log-edges)")
    print("-" * 78)
    print("VERDICT: " + verdict)
    print(f"wrote {os.path.relpath(apath, ROOT)} + quality_report.json")


if __name__ == "__main__":
    main()
