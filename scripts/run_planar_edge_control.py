# -*- coding: utf-8 -*-
r"""
run_planar_edge_control.py -- the edge-placement control, redone without
crossing veins.

run_random_edge_control.py compared three ways of adding the same number of
edges (27 networks, 2,400 trials per arm, seed 1):
  delaunay   shortest Delaunay non-edges first        [the paper's arm]
  rand_del   the same Delaunay pool in random order
  rand_any   random non-adjacent node pairs
None of the arms checked for crossings with traced veins. The paper called the
rand_del pool "planar"; it is planar only among its own edges. This script
  1. counts how many edges each original arm added across a traced vein,
  2. re-runs the two Delaunay arms with the crossing filter
     (planarity.add_loops_planar): shortest-first, and the SAME random order
     the original rand_del arm used, skipping any candidate that crosses a
     traced vein, until the same number of edges is added,
  3. measures p_c at the original settings (2,400 trials, 40 densities,
     rho_max 0.6, seed 1) at collapse criteria 30/50/70%.
rand_any is not re-run: random long-range pairs cannot be made non-crossing
without turning them into a different rule. Its crossing count is reported so
it can be labelled as a physically impossible reference.

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_planar_edge_control.py

Output: data/planar_edge_control.csv, data/planar_edge_control.json
"""
import os, sys, csv, json, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import realleaf, percolation, planarity
from scripts.run_random_edge_control import (_delaunay_candidates, _need,
                                             add_random_any, LEAFDIR, TARGET_K,
                                             SEED, RHO_MAX)

ARCHIVE = os.path.join(ROOT, "data", "random_edge_control.csv")
OUT_CSV = os.path.join(ROOT, "data", "planar_edge_control.csv")
OUT_JSON = os.path.join(ROOT, "data", "planar_edge_control.json")
FR = (0.3, 0.5, 0.7)
FIELDS = (["species", "N", "k_current", "edges_added",
           "cross_delaunay", "cross_rand_del", "cross_rand_any",
           "planar_added_delaunay", "planar_added_rand_del"]
          + ["pc_%s_f%d" % (a, round(100 * f)) for a in
             ("current", "delaunay_planar", "rand_del_planar") for f in FR]
          + ["pc_current_archived", "pc_delaunay_archived", "pc_rand_del_archived",
             "pc_rand_any_archived", "seconds"])


def measure(G):
    pp = config.PercolationParams(mode="random", n_densities=40, n_trials=2400,
                                  seed=SEED)
    return percolation.find_pc_multi(G, pp, rho_max=RHO_MAX, fractions=FR)["p_c"]


def n_crossing(G, G2):
    added = [(u, v) for u, v, d in G2.edges(data=True) if d.get("kind") == "added_loop"]
    pairs = planarity.crossing_pairs(G, added, list(G.edges()))
    return int(len(np.unique(pairs[0]))) if pairs.shape[1] else 0


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    arch = list(csv.DictReader(open(ARCHIVE, newline="")))
    pairs = {sp: (nf, vf) for sp, nf, vf in realleaf.find_leaf_pairs(LEAFDIR)}
    done = set()
    if os.path.exists(OUT_CSV):
        done = {r["species"] for r in csv.DictReader(open(OUT_CSV, newline=""))}
    new = not os.path.exists(OUT_CSV) or os.path.getsize(OUT_CSV) == 0
    fh = open(OUT_CSV, "a", newline="")
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    if new:
        w.writeheader()
    for i, a in enumerate(arch, 1):
        sp = a["species"]
        if sp in done:
            continue
        t0 = time.time()
        G = realleaf.load_matos(*pairs[sp], name=sp)
        need = _need(G, TARGET_K)
        cand = _delaunay_candidates(G)               # original (unsorted) order
        crosses = planarity.crossing_candidates(G, cand)
        shortest = np.argsort([c[0] for c in cand], kind="stable")
        rng = np.random.default_rng(SEED)
        perm = rng.permutation(len(cand))            # == original rand_del draw
        Ga, _ = add_random_any(G, need, rng)         # same rng stream as original
        cross_del = int(crosses[shortest[:need]].sum())
        cross_rdel = int(crosses[perm[:need]].sum())
        cross_rany = n_crossing(G, Ga)
        del Ga
        Gd, nd, _ = planarity.add_loops_planar(G, TARGET_K, cand, crosses, order=shortest)
        Gr, nr, _ = planarity.add_loops_planar(G, TARGET_K, cand, crosses, order=perm)
        pc0, pcd, pcr = measure(G), measure(Gd), measure(Gr)
        row = {"species": sp, "N": G.number_of_nodes(),
               "k_current": a["k_current"], "edges_added": need,
               "cross_delaunay": cross_del, "cross_rand_del": cross_rdel,
               "cross_rand_any": cross_rany,
               "planar_added_delaunay": nd, "planar_added_rand_del": nr,
               "pc_current_archived": a["pc_current"],
               "pc_delaunay_archived": a["pc_delaunay"],
               "pc_rand_del_archived": a["pc_rand_del"],
               "pc_rand_any_archived": a["pc_rand_any"],
               "seconds": round(time.time() - t0, 1)}
        for f in FR:
            t = round(100 * f)
            row["pc_current_f%d" % t] = round(pc0[f], 6)
            row["pc_delaunay_planar_f%d" % t] = round(pcd[f], 6)
            row["pc_rand_del_planar_f%d" % t] = round(pcr[f], 6)
        w.writerow(row); fh.flush()
        print("[%2d/%2d] %-8s +%d  cross del %d rdel %d rany %d | pc50 cur %.4f del %.4f rdel %.4f"
              % (i, len(arch), sp, need, cross_del, cross_rdel, cross_rany,
                 pc0[0.5], pcd[0.5], pcr[0.5]), flush=True)
    fh.close()
    summarize()


def summarize():
    from scipy import stats
    rows = list(csv.DictReader(open(OUT_CSV, newline="")))
    f = lambda k: np.array([float(r[k]) for r in rows])
    added = f("edges_added")
    S = {"n": len(rows), "trials_per_arm": 2400,
         "crossing_pct_of_added": {
             arm: round(100 * f("cross_" + arm).sum() / added.sum(), 2)
             for arm in ("delaunay", "rand_del", "rand_any")},
         "current_reproduces_archive": int(np.sum(np.abs(
             f("pc_current_f50") - f("pc_current_archived")) < 5e-6)),
         "by_criterion": {}}
    arch_d = f("pc_delaunay_archived") - f("pc_current_archived")
    arch_r = f("pc_rand_del_archived") - f("pc_current_archived")
    arch_a = f("pc_rand_any_archived") - f("pc_current_archived")
    S["archived_unfiltered_median_gain"] = {
        "delaunay": round(float(np.median(arch_d)), 4),
        "rand_del": round(float(np.median(arch_r)), 4),
        "rand_any": round(float(np.median(arch_a)), 4)}
    for fr in FR:
        t = round(100 * fr)
        c = f("pc_current_f%d" % t)
        dd = f("pc_delaunay_planar_f%d" % t) - c
        dr = f("pc_rand_del_planar_f%d" % t) - c
        S["by_criterion"]["f%d" % t] = {
            "median_gain_delaunay_planar": round(float(np.median(dd)), 4),
            "median_gain_rand_del_planar": round(float(np.median(dr)), 4),
            "n_rand_del_above_delaunay": int((dr > dd).sum()),
            "wilcoxon_rand_del_vs_delaunay_p": float(stats.wilcoxon(dr - dd).pvalue),
            "median_ratio_rand_del_over_delaunay": round(float(np.median(
                dr[dd > 0] / dd[dd > 0])), 2)}
    json.dump(S, open(OUT_JSON, "w"), indent=2)
    print(json.dumps(S, indent=1))
    return S


if __name__ == "__main__":
    main()
