# -*- coding: utf-8 -*-
r"""
run_threshold_sensitivity.py -- do the cohort results depend on the 50% collapse
criterion?

Answers SRC Reviewer 2, compliance item 3: "Include calibration/optimization
parameters so that findings can be consistent regardless of the threshold set."

The study calls a network collapsed when its largest connected component falls
below 50% of its original size, and p_c is the removed fraction at which half
of the trials have collapsed. The 50% is a convention. This script re-runs the
percolation cohort (n = 100) with the original settings (2,400 trials per
network per mode = 40 densities x 60 trials, rho_max 0.6, seed 1) but keeps
every trial's largest-component size, so p_c can be read off at any collapse
criterion from 10% to 90% of the original size. At 50% it reproduces the
archived data/cohort_pc.csv exactly. It also records a threshold-free measure:
the area under the mean largest-component curve over rho in [0, 0.6].

For each criterion it repeats the headline tests: Spearman of p_c with mean
degree, fractal dimension D and loop fraction; the partial Spearman of each
axis controlling for the other; the two-predictor regression; and the
degree-weighted vs uniform comparison.

Output (incremental, resumable):
    data/threshold_sensitivity.csv     one row per network
    data/threshold_sensitivity.json    the tests at each criterion

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_threshold_sensitivity.py --workers 2
"""
import os, sys, csv, json, time, argparse
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
OUT_CSV = os.path.join(ROOT, "data", "threshold_sensitivity.csv")
OUT_JSON = os.path.join(ROOT, "data", "threshold_sensitivity.json")
MASTER = os.path.join(ROOT, "data", "analysis_master.csv")
FRACTIONS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
TAG = lambda f: "f%d" % round(100 * f)
FIELDS = (["species", "N"]
          + ["pc_random_" + TAG(f) for f in FRACTIONS]
          + ["pc_degree_" + TAG(f) for f in FRACTIONS]
          + ["area_random", "area_degree", "pc_random_archived",
             "pc_degree_archived", "seconds"])


def cohort():
    rows = list(csv.DictReader(open(MASTER, newline="")))
    keep = [r for r in rows if r["in_percolation_cohort_100"] == "True"]
    keep.sort(key=lambda r: -int(r["n_nodes"]))
    return keep


def one_leaf(r):
    import glob
    import config
    from holoparasitic import realleaf, percolation
    s = r["name"]
    t0 = time.time()
    nf = glob.glob(os.path.join(LEAFDIR, s, "*_nodes.csv"))[0]
    vf = glob.glob(os.path.join(LEAFDIR, s, "*_veins.csv"))[0]
    G = realleaf.load_matos(nf, vf, name=s)
    pr = config.PercolationParams(mode="random", n_trials=2400, n_densities=40)
    ran = percolation.find_pc_multi(G, pr, rho_max=0.6, fractions=FRACTIONS)
    w = percolation.importance_weights(G, list(G.nodes), metric="degree")
    pt = config.PercolationParams(mode="targeted", n_trials=2400, n_densities=40)
    deg = percolation.find_pc_multi(G, pt, weights=w, rho_max=0.6, fractions=FRACTIONS)
    row = {"species": s, "N": G.number_of_nodes(),
           "area_random": round(ran["robustness_area"], 6),
           "area_degree": round(deg["robustness_area"], 6),
           "pc_random_archived": r["pc_random"], "pc_degree_archived": r["pc_degree"],
           "seconds": round(time.time() - t0, 1)}
    for f in FRACTIONS:
        row["pc_random_" + TAG(f)] = round(ran["p_c"][f], 4)
        row["pc_degree_" + TAG(f)] = round(deg["p_c"][f], 4)
    return row


def done():
    if not os.path.exists(OUT_CSV):
        return set()
    return {r["species"] for r in csv.DictReader(open(OUT_CSV, newline=""))}


def summarize():
    from scipy import stats
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from build_analysis_master import partial_spearman, regress
    rows = list(csv.DictReader(open(OUT_CSV, newline="")))
    master = {r["name"]: r for r in csv.DictReader(open(MASTER, newline=""))}
    k = np.array([float(master[r["species"]]["mean_degree"]) for r in rows])
    D = np.array([float(master[r["species"]]["D"]) for r in rows])
    LF = np.array([float(master[r["species"]]["loop_fraction_nonbridge"]) for r in rows])
    col = lambda c: np.array([float(r[c]) for r in rows])
    sp = lambda a, b: {"rho": round(float(stats.spearmanr(a, b)[0]), 4),
                       "p": float(stats.spearmanr(a, b)[1])}
    def pp(r, n=len(rows)):
        """partial rank correlation with its t-test p (df = n - 3)."""
        t = r * np.sqrt((n - 3) / (1 - r * r))
        return {"rho": round(float(r), 4), "p": float(2 * stats.t.sf(abs(t), n - 3))}

    ref = col("pc_random_f50")
    S = {"n": len(rows), "trials_per_network_per_mode": 2400,
         "reproduction_check": {
             "random_f50_equals_archived": int(np.sum(np.abs(ref - col("pc_random_archived")) < 5e-5)),
             "degree_f50_equals_archived": int(np.sum(np.abs(col("pc_degree_f50") - col("pc_degree_archived")) < 5e-5)),
             "of": len(rows)},
         "by_criterion": {}}
    for f in FRACTIONS + ("area",):
        if f == "area":
            pr, pdg = col("area_random"), col("area_degree")
            label = "threshold-free: area under the largest-component curve, rho 0-0.6"
        else:
            pr, pdg = col("pc_random_" + TAG(f)), col("pc_degree_" + TAG(f))
            label = "largest component < %d%% of original" % round(100 * f)
        gap = pr - pdg
        reg = regress(pr, [k, D], standardize_outcome=True)
        S["by_criterion"]["area" if f == "area" else TAG(f)] = {
            "criterion": label,
            "median_random": round(float(np.median(pr)), 4),
            "median_degree": round(float(np.median(pdg)), 4),
            "spearman_random_with": {"mean_degree": sp(k, pr), "D": sp(D, pr),
                                     "loop_fraction": sp(LF, pr)},
            "partial_spearman": {"mean_degree_given_D": pp(partial_spearman(k, pr, D)),
                                 "D_given_mean_degree": pp(partial_spearman(D, pr, k))},
            "regression_fully_standardized": {"beta_mean_degree": round(reg["beta"][0], 4),
                                              "beta_D": round(reg["beta"][1], 4),
                                              "R2": round(reg["R2"], 4)},
            "degree_vs_uniform": {"n_degree_lower": int((gap > 0).sum()),
                                  "n_equal": int((gap == 0).sum()),
                                  "n_degree_higher": int((gap < 0).sum()),
                                  "median_relative_reduction_pct": round(
                                      100 * (np.median(pr) - np.median(pdg)) / np.median(pr), 2)},
            "rank_agreement_with_f50": sp(ref, pr),
        }
    json.dump(S, open(OUT_JSON, "w"), indent=2)
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--summarize", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    if not args.summarize:
        todo = [r for r in cohort() if r["name"] not in done()]
        print("threshold sensitivity: %d networks, %d workers" % (len(todo), args.workers))
        new = not os.path.exists(OUT_CSV) or os.path.getsize(OUT_CSV) == 0
        with open(OUT_CSV, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            if new:
                w.writeheader()
            with Pool(args.workers) as pool:
                for i, row in enumerate(pool.imap_unordered(one_leaf, todo), 1):
                    w.writerow(row); fh.flush()
                    print("[%3d/%3d] %-8s N=%-7s pc30/50/70 %s %s %s (arch %s) %ss"
                          % (i, len(todo), row["species"], row["N"], row["pc_random_f30"],
                             row["pc_random_f50"], row["pc_random_f70"],
                             row["pc_random_archived"], row["seconds"]), flush=True)
    S = summarize()
    for t, b in S["by_criterion"].items():
        print(t, b["median_random"], b["spearman_random_with"]["mean_degree"]["rho"],
              b["spearman_random_with"]["D"]["rho"], b["degree_vs_uniform"]["n_degree_lower"],
              b["rank_agreement_with_f50"]["rho"])


if __name__ == "__main__":
    main()
