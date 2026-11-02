# -*- coding: utf-8 -*-
r"""
run_planarity_check.py -- does the reticulation enhancement create veins that
cross existing veins, and does removing those crossings change the result?

Answers SRC Reviewer 1: "Verify planarity and edge-intersection handling in the
enhancement procedure."

What the original enhancement did (scripts/make_real_suggested.py::add_loops):
take every Delaunay non-edge of the leaf's own junction coordinates, sort by
length, add the shortest ones until <k> reaches 2.811. It never checked whether
an added segment crosses a traced vein. Delaunay edges cannot cross each other,
but traced veins are not Delaunay edges, so crossings are possible.

For every network in the enhancement cohort (n = 105) this script
  1. counts how many of the originally added edges cross a traced vein
     (straight segments between junction coordinates; see planarity.py),
  2. counts crossings among the traced veins themselves, as the baseline that
     the straight-segment approximation produces on its own,
  3. rebuilds the enhancement with a crossing filter (skip any candidate that
     crosses a traced vein, keep going shortest first to the same <k>),
  4. re-measures p_c on the traced network and on the planar enhanced network
     with the original settings (10,000 trials, 40 densities, rho_max 0.6,
     seed 1), at three collapse criteria: largest component below 30, 50 and
     70% of its original size. At 50% the traced-network value reproduces the
     archived pc_current exactly, so the archived and new runs share their
     random draws (common random numbers).

Output (incremental, resumable):
    data/planarity_check.csv        one row per network
    data/planarity_check.json       summary (written by --summarize, also at end)

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_planarity_check.py --workers 4
"""
import os, sys, csv, glob, json, time, argparse
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
OUT_CSV = os.path.join(ROOT, "data", "planarity_check.csv")
OUT_JSON = os.path.join(ROOT, "data", "planarity_check.json")
MASTER = os.path.join(ROOT, "data", "analysis_master.csv")
FRACTIONS = (0.3, 0.5, 0.7)
TARGET_K = 2.811

FIELDS = (["species", "N", "E", "k_current", "need", "n_candidates",
           "orig_added", "orig_crossing_edges", "orig_crossing_pct",
           "traced_crossing_pairs", "traced_crossing_pct_of_E",
           "planar_added", "planar_skipped", "k_planar"]
          + ["pc_current_f%d" % round(100 * f) for f in FRACTIONS]
          + ["pc_planar_f%d" % round(100 * f) for f in FRACTIONS]
          + ["area_current", "area_planar",
             "pc_current_archived", "pc_suggested_archived", "seconds"])


def cohort():
    rows = list(csv.DictReader(open(MASTER, newline="")))
    keep = [r for r in rows if r["in_enhancement_cohort_105"] == "True"]
    keep.sort(key=lambda r: -int(r["n_nodes"]))      # largest first: balances workers
    return keep


def one_leaf(r):
    import config
    from holoparasitic import realleaf, percolation, planarity
    s = r["name"]
    t0 = time.time()
    nf = glob.glob(os.path.join(LEAFDIR, s, "*_nodes.csv"))[0]
    vf = glob.glob(os.path.join(LEAFDIR, s, "*_veins.csv"))[0]
    G = realleaf.load_matos(nf, vf, name=s)
    N, E = G.number_of_nodes(), G.number_of_edges()
    need = max(int(TARGET_K * N / 2) - E, 0)

    cand = planarity.delaunay_candidates(G)
    crosses = planarity.crossing_candidates(G, cand)
    orig_added = min(need, len(cand))       # add_loops takes the first `need`
    orig_cross = int(crosses[:orig_added].sum())
    traced = planarity.crossing_pairs(G, list(G.edges()), list(G.edges()),
                                      same_set=True).shape[1]
    G3, p_added, p_skipped = planarity.add_loops_planar(G, TARGET_K, cand, crosses)
    n_cand = len(cand)
    del cand, crosses

    pp = config.PercolationParams(mode="random", n_densities=40, n_trials=10000)
    cur = percolation.find_pc_multi(G, pp, rho_max=0.6, fractions=FRACTIONS)
    pla = (cur if p_added == 0 else
           percolation.find_pc_multi(G3, pp, rho_max=0.6, fractions=FRACTIONS))

    row = {"species": s, "N": N, "E": E, "k_current": round(2 * E / N, 4),
           "need": need, "n_candidates": n_cand,
           "orig_added": orig_added, "orig_crossing_edges": orig_cross,
           "orig_crossing_pct": round(100 * orig_cross / orig_added, 3) if orig_added else 0.0,
           "traced_crossing_pairs": traced,
           "traced_crossing_pct_of_E": round(100 * traced / E, 3),
           "planar_added": p_added, "planar_skipped": p_skipped,
           "k_planar": round(2 * G3.number_of_edges() / N, 4),
           "area_current": round(cur["robustness_area"], 6),
           "area_planar": round(pla["robustness_area"], 6),
           "pc_current_archived": r["pc_current"],
           "pc_suggested_archived": r["pc_suggested"],
           "seconds": round(time.time() - t0, 1)}
    for f in FRACTIONS:
        row["pc_current_f%d" % round(100 * f)] = round(cur["p_c"][f], 4)
        row["pc_planar_f%d" % round(100 * f)] = round(pla["p_c"][f], 4)
    return row


def done():
    if not os.path.exists(OUT_CSV):
        return set()
    return {r["species"] for r in csv.DictReader(open(OUT_CSV, newline=""))}


# --------------------------------------------------------------------------
# summary
# --------------------------------------------------------------------------
def _desc(x):
    x = np.asarray(x, float)
    return {"n": int(len(x)), "Mdn": round(float(np.median(x)), 4),
            "Q1": round(float(np.percentile(x, 25)), 4),
            "Q3": round(float(np.percentile(x, 75)), 4),
            "M": round(float(x.mean()), 5), "min": round(float(x.min()), 4),
            "max": round(float(x.max()), 4)}


def summarize():
    from scipy import stats
    rows = list(csv.DictReader(open(OUT_CSV, newline="")))
    master = {r["name"]: r for r in csv.DictReader(open(MASTER, newline=""))}
    f = lambda k: np.array([float(r[k]) for r in rows])
    grade = [master[r["species"]]["grade"] for r in rows]
    k0 = f("k_current")
    added, cross = f("orig_added"), f("orig_crossing_edges")
    has = added > 0
    S = {"n_networks": len(rows),
         "geometry_note": ("edges are straight segments between junction "
                           "coordinates; a crossing is any shared point between "
                           "two edges that do not share a junction"),
         "original_enhancement": {
             "networks_with_added_edges": int(has.sum()),
             "added_edges_total": int(added.sum()),
             "crossing_edges_total": int(cross.sum()),
             "crossing_pct_of_added_total": round(100 * cross.sum() / added.sum(), 3),
             "networks_with_any_crossing": int((cross > 0).sum()),
             "per_network_crossing_pct": _desc(f("orig_crossing_pct")[has])},
         "traced_baseline": {
             "crossing_pairs_total": int(f("traced_crossing_pairs").sum()),
             "edges_total": int(f("E").sum()),
             "per_network_pct_of_E": _desc(f("traced_crossing_pct_of_E"))},
         "planar_enhancement": {
             "edges_added_total": int(f("planar_added").sum()),
             "candidates_skipped_total": int(f("planar_skipped").sum()),
             "networks_reaching_target_k": int(sum(
                 1 for r in rows if float(r["k_planar"]) >= TARGET_K - 1e-3
                 or int(r["need"]) == 0)),
             "k_planar": _desc(f("k_planar"))},
         "reproduction_check": {
             "pc_current_f50_equals_archived": int(sum(
                 1 for r in rows
                 if abs(float(r["pc_current_f50"]) - float(r["pc_current_archived"])) < 5e-5)),
             "of": len(rows)},
         "by_criterion": {}}

    arch_delta = f("pc_suggested_archived") - f("pc_current_archived")
    for fr in FRACTIONS:
        tag = "f%d" % round(100 * fr)
        cur, pla = f("pc_current_" + tag), f("pc_planar_" + tag)
        d = pla - cur
        nz = d[np.abs(d) > 0]
        w = stats.wilcoxon(nz) if len(nz) > 0 else None
        A = np.array([g == "A" for g in grade])
        dA = d[A]
        nA_pos, nA_neg = int((dA > 0).sum()), int((dA < 0).sum())
        sign_p = (float(stats.binomtest(nA_pos, nA_pos + nA_neg, 0.5).pvalue)
                  if nA_pos + nA_neg else None)
        rho_k, p_k = stats.spearmanr(k0, d)
        gap = np.clip(TARGET_K - k0, 0, None)       # as in design rule 7
        slope = float(np.polyfit(gap, d, 1)[0])
        slope0 = float((gap @ d) / (gap @ gap))
        block = {
            "collapse_criterion": "largest component < %d%% of original" % round(100 * fr),
            "median_pc_current": round(float(np.median(cur)), 4),
            "median_pc_planar": round(float(np.median(pla)), 4),
            "delta": _desc(d),
            "n_improved": int((d > 0).sum()), "n_unchanged": int((d == 0).sum()),
            "n_worsened": int((d < 0).sum()),
            "median_relative_gain_pct": round(float(np.median(d[cur > 0] / cur[cur > 0])) * 100, 2),
            "wilcoxon": ({"W": float(w.statistic), "p": float(w.pvalue),
                          "n_nonzero": int(len(nz))} if w is not None else None),
            "grade_A": {"n": int(A.sum()), "n_improved": nA_pos, "n_worsened": nA_neg,
                        "median_delta": round(float(np.median(dA)), 4),
                        "sign_test_p": sign_p},
            "spearman_initial_k_x_delta": {"rho": round(float(rho_k), 4), "p": float(p_k)},
            "gain_vs_headroom": {"slope_with_intercept": round(slope, 4),
                                 "slope_through_origin": round(slope0, 4),
                                 "headroom": "2.811 - initial <k>"},
        }
        if fr == 0.5:
            block["vs_archived_unfiltered"] = {
                "spearman_delta": round(float(stats.spearmanr(arch_delta, d)[0]), 4),
                "median_archived_delta": round(float(np.median(arch_delta)), 4),
                "median_abs_difference_pc_enhanced": round(float(np.median(
                    np.abs(pla - f("pc_suggested_archived")))), 4),
                "max_abs_difference_pc_enhanced": round(float(np.max(
                    np.abs(pla - f("pc_suggested_archived")))), 4),
                "archived_n_improved": int((arch_delta > 0).sum())}
        S["by_criterion"][tag] = block

    da = f("area_planar") - f("area_current")
    S["threshold_free_area"] = {
        "definition": "integral of the mean largest-component fraction over rho in [0, 0.6]",
        "delta": _desc(da), "n_improved": int((da > 0).sum()),
        "n_worsened": int((da < 0).sum())}
    json.dump(S, open(OUT_JSON, "w"), indent=2)
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--summarize", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    if not args.summarize:
        todo = [r for r in cohort() if r["name"] not in done()]
        print("planarity check: %d networks to run, %d workers" % (len(todo), args.workers))
        new = not os.path.exists(OUT_CSV) or os.path.getsize(OUT_CSV) == 0
        with open(OUT_CSV, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            if new:
                w.writeheader(); fh.flush()
            with Pool(args.workers) as pool:
                for i, row in enumerate(pool.imap_unordered(one_leaf, todo), 1):
                    w.writerow(row); fh.flush()
                    print("[%3d/%3d] %-8s N=%-7s cross %s/%s  pc50 %s -> %s (arch %s -> %s) %ss"
                          % (i, len(todo), row["species"], row["N"],
                             row["orig_crossing_edges"], row["orig_added"],
                             row["pc_current_f50"], row["pc_planar_f50"],
                             row["pc_current_archived"], row["pc_suggested_archived"],
                             row["seconds"]), flush=True)
    S = summarize()
    print(json.dumps(S["original_enhancement"], indent=1))
    print(json.dumps(S["by_criterion"]["f50"], indent=1))


if __name__ == "__main__":
    main()
