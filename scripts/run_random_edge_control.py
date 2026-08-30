# -*- coding: utf-8 -*-
r"""
run_random_edge_control.py -- the missing null arm for the reticulation-
enhancement experiment.

THE QUESTION
------------
run_cohort_suggested.py showed that adding shortest-Delaunay areole closures up
to <k> = 2.811 raises p_c in 93 of 105 networks and lowers it in none. That gain
is consistent with two very different stories:

  (a) closing the smallest areoles specifically confers tolerance, or
  (b) adding ANY 'need' edges to a sparse planar graph raises site-percolation
      tolerance, and the Delaunay rule is incidental.

Story (b) is close to an arithmetic property of site percolation, so the
enhancement result does not support (a) until (b) is ruled out. This script runs
the missing controls at MATCHED EDGE COUNT.

ARMS (all four measured on the same leaf, same seed -> common random numbers)
----------------------------------------------------------------------------
  current    the leaf as traced
  delaunay   shortest Delaunay non-edges, shortest-first  [the paper's arm]
  rand_del   the SAME Delaunay candidate pool, drawn in RANDOM order
             -> isolates the 'shortest-first / smallest areoles' heuristic
  rand_any   uniformly random non-adjacent node pairs, ignoring geometry
             -> isolates planarity/locality; expect an inflated gain, because
                long-range chords are small-world shortcuts a leaf cannot build

Every arm adds exactly the same number of edges as `delaunay` needs to reach
TARGET_K, so <k> is identical across the three enhanced arms and only the
PLACEMENT RULE differs. That is the comparison the defence question asks for.

INTERPRETATION
--------------
  delaunay > rand_del   -> the shortest-first rule matters (areole size)
  delaunay ~ rand_del   -> the candidate pool matters, the ordering does not
  delaunay >= rand_any  -> geometry-respecting closure is competitive with
                           physically impossible shortcuts (a strong result)
  rand_any >> delaunay  -> expected; report it as the ceiling a real leaf
                           cannot reach, NOT as a failure of the Delaunay arm

USAGE
-----
    python scripts/run_random_edge_control.py --limit 30 --trials 2400
    python scripts/run_random_edge_control.py --limit 0 --trials 10000   # full

Output (incremental, resumable -- re-run to continue where it stopped):
    data/random_edge_control.csv

ASCII-only stdout.
"""
import argparse
import csv
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
from scipy.spatial import Delaunay

import config
from holoparasitic import realleaf, percolation

LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
OUT = os.path.join(ROOT, "data", "random_edge_control.csv")

TARGET_K = 2.811        # identical to make_real_suggested.TARGET_K
RHO_MAX = 0.6
SEED = 1                # common random numbers: same seed for every arm

FIELDS = [
    "species", "N", "E", "k_current", "D", "quality",
    "edges_added",                       # identical across the three arms
    "k_delaunay", "k_rand_del", "k_rand_any",
    "pc_current", "pc_delaunay", "pc_rand_del", "pc_rand_any",
    "d_delaunay", "d_rand_del", "d_rand_any",
    "seconds",
]


# --------------------------------------------------------------------------
# edge-addition rules -- all three return (G2, n_added) with n_added matched
# --------------------------------------------------------------------------
def _delaunay_candidates(G):
    """Every Delaunay non-edge on the leaf's own node positions, with length."""
    nodes = list(G.nodes)
    pos = np.array([G.nodes[n]["pos"] for n in nodes], float)
    tri = Delaunay(pos)
    seen, cand = set(), []
    for s in tri.simplices:
        for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2])):
            key = (a, b) if a < b else (b, a)
            if key in seen:
                continue
            seen.add(key)
            na, nb = nodes[key[0]], nodes[key[1]]
            if G.has_edge(na, nb):
                continue
            d = float(np.hypot(pos[key[0]][0] - pos[key[1]][0],
                               pos[key[0]][1] - pos[key[1]][1]))
            cand.append((d, na, nb))
    return cand


def _need(G, target_k):
    """Edges required to reach target mean degree. Matched across all arms."""
    return max(0, int(target_k * G.number_of_nodes() / 2) - G.number_of_edges())


def _thin_radius(G2, na, nb):
    """New anastomoses are thin minor veins -- same rule as the paper's arm."""
    ra = min((G2[na][x].get("radius", 0.01) for x in G2.neighbors(na)), default=0.01)
    rb = min((G2[nb][x].get("radius", 0.01) for x in G2.neighbors(nb)), default=0.01)
    return min(ra, rb)


def add_delaunay_shortest(G, need, cand):
    """The paper's arm: shortest Delaunay non-edges first."""
    G2 = G.copy()
    for d, na, nb in sorted(cand, key=lambda t: t[0])[:need]:
        G2.add_edge(na, nb, radius=_thin_radius(G2, na, nb), length=d,
                    kind="added_loop")
    return G2, min(need, len(cand))


def add_delaunay_random(G, need, cand, rng):
    """Same candidate pool, random order -- isolates the shortest-first rule."""
    G2 = G.copy()
    idx = rng.permutation(len(cand))[:need]
    for i in idx:
        d, na, nb = cand[i]
        G2.add_edge(na, nb, radius=_thin_radius(G2, na, nb), length=d,
                    kind="added_loop")
    return G2, int(len(idx))


def add_random_any(G, need, rng):
    """Uniformly random non-adjacent pairs -- ignores geometry entirely."""
    G2 = G.copy()
    nodes = list(G2.nodes)
    pos = {n: G2.nodes[n]["pos"] for n in nodes}
    n = len(nodes)
    added, attempts, cap = 0, 0, need * 200 + 10_000
    while added < need and attempts < cap:
        attempts += 1
        a, b = rng.integers(0, n), rng.integers(0, n)
        if a == b:
            continue
        na, nb = nodes[a], nodes[b]
        if G2.has_edge(na, nb):
            continue
        d = float(np.hypot(pos[na][0] - pos[nb][0], pos[na][1] - pos[nb][1]))
        G2.add_edge(na, nb, radius=_thin_radius(G2, na, nb),
                    length=d or 1e-6, kind="added_loop")
        added += 1
    return G2, added


# --------------------------------------------------------------------------
def measure(G, trials):
    pp = config.PercolationParams(mode="random", n_densities=40,
                                  n_trials=trials, seed=SEED)
    return float(percolation.find_pc(G, pp, rho_max=RHO_MAX)["p_c"])


def meta_lookup():
    m = {}
    p = os.path.join(ROOT, "data", "characterization_annotated.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, newline="")):
            m[r["name"]] = (r.get("D", ""), r.get("quality", ""))
    return m


MIN_NODES = 1000        # enhancement-cohort screen, as reported in the paper
MIN_PC = 0.02


def enhancement_cohort():
    """The 105 species of the enhancement cohort, with their baseline <k>.

    cohort_suggested.csv holds all 120 traced leaves, so the enhancement screen
    (N >= 1000 and a measurable current threshold) has to be applied here or the
    control runs on networks the paper's enhancement result never included --
    including degenerate ones such as Puy_alp, which is a 144-node matching with
    <k> = 1.0 and p_c = 0. This screen reproduces n = 105 exactly.
    """
    p = os.path.join(ROOT, "data", "cohort_suggested.csv")
    rows = []
    if os.path.exists(p):
        for r in csv.DictReader(open(p, newline="")):
            try:
                if int(r["N"]) < MIN_NODES or float(r["pc_current"]) < MIN_PC:
                    continue
                rows.append((r["species"], float(r["k_current"])))
            except (KeyError, ValueError):
                continue
    return rows


def stratified(rows, limit):
    """Even coverage of the baseline mean-degree range, since the paper's gain
    depends on it at rho = -0.821. Sorting then taking every m-th row keeps the
    sparse and dense ends both represented."""
    if limit <= 0 or limit >= len(rows):
        return [s for s, _ in rows]
    rows = sorted(rows, key=lambda t: t[1])
    step = len(rows) / float(limit)
    return [rows[min(int(i * step), len(rows) - 1)][0] for i in range(limit)]


def done_set():
    if not os.path.exists(OUT):
        return set()
    return {r["species"] for r in csv.DictReader(open(OUT, newline=""))}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=30,
                    help="networks to run (stratified by baseline <k>); 0 = all")
    ap.add_argument("--trials", type=int, default=2400,
                    help="Monte Carlo trials per network per arm")
    args = ap.parse_args()

    rows = enhancement_cohort()
    if not rows:
        print("ERROR: data/cohort_suggested.csv not found -- run "
              "run_cohort_suggested.py first (it defines the cohort).")
        return 1

    wanted = stratified(rows, args.limit)
    already = done_set()
    todo = [s for s in wanted if s not in already]
    meta = meta_lookup()

    print("random-edge control")
    print("  cohort      : %d networks (%d selected, %d already done)"
          % (len(rows), len(wanted), len(wanted) - len(todo)))
    print("  trials/arm  : %d      target <k> = %.3f     seed = %d (common)"
          % (args.trials, TARGET_K, SEED))
    print("  arms        : current | delaunay | rand_del | rand_any")
    print("  output      : %s" % os.path.relpath(OUT, ROOT))
    print("")

    # Pair node/vein CSVs the same way the rest of the pipeline does: the
    # archive is not internally consistent about stems, so per-directory
    # pairing is what find_leaf_pairs exists to handle.
    pairs = {sp: (nf, vf) for sp, nf, vf in realleaf.find_leaf_pairs(LEAFDIR)}

    write_header = not os.path.exists(OUT)
    for i, sp in enumerate(todo, 1):
        if sp not in pairs:
            print("  [%3d/%3d] %-28s SKIP (files not found)" % (i, len(todo), sp))
            continue

        t0 = time.time()
        try:
            nf, vf = pairs[sp]
            G = realleaf.load_matos(nf, vf, name=sp)
        except Exception as exc:
            print("  [%3d/%3d] %-28s SKIP (%s)" % (i, len(todo), sp, exc))
            continue

        N, E = G.number_of_nodes(), G.number_of_edges()
        k0 = 2.0 * E / N if N else 0.0
        need = _need(G, TARGET_K)
        if need <= 0:
            print("  [%3d/%3d] %-28s SKIP (already above target <k>)"
                  % (i, len(todo), sp))
            continue

        cand = _delaunay_candidates(G)
        rng = np.random.default_rng(SEED)

        Gd, n_d = add_delaunay_shortest(G, need, cand)
        Gr, n_r = add_delaunay_random(G, need, cand, rng)
        Ga, n_a = add_random_any(G, need, rng)

        pc0 = measure(G, args.trials)
        pcd = measure(Gd, args.trials)
        pcr = measure(Gr, args.trials)
        pca = measure(Ga, args.trials)

        D, q = meta.get(sp, ("", ""))
        row = {
            "species": sp, "N": N, "E": E, "k_current": round(k0, 4),
            "D": D, "quality": q, "edges_added": need,
            "k_delaunay": round(2.0 * (E + n_d) / N, 4),
            "k_rand_del": round(2.0 * (E + n_r) / N, 4),
            "k_rand_any": round(2.0 * (E + n_a) / N, 4),
            "pc_current": round(pc0, 6), "pc_delaunay": round(pcd, 6),
            "pc_rand_del": round(pcr, 6), "pc_rand_any": round(pca, 6),
            "d_delaunay": round(pcd - pc0, 6),
            "d_rand_del": round(pcr - pc0, 6),
            "d_rand_any": round(pca - pc0, 6),
            "seconds": round(time.time() - t0, 1),
        }
        with open(OUT, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if write_header:
                w.writeheader()
                write_header = False
            w.writerow(row)

        print("  [%3d/%3d] %-28s N=%-7d +%-6d  d_del=%+.4f  d_rdel=%+.4f  "
              "d_rany=%+.4f  (%.0fs)"
              % (i, len(todo), sp[:28], N, need,
                 row["d_delaunay"], row["d_rand_del"], row["d_rand_any"],
                 row["seconds"]))

    summarise()
    return 0


def summarise():
    """Paired Wilcoxon of delaunay against each null, on matched edge counts."""
    if not os.path.exists(OUT):
        return
    rows = list(csv.DictReader(open(OUT, newline="")))
    if len(rows) < 3:
        print("\n(too few rows to summarise)")
        return
    from scipy import stats

    dd = np.array([float(r["d_delaunay"]) for r in rows])
    dr = np.array([float(r["d_rand_del"]) for r in rows])
    da = np.array([float(r["d_rand_any"]) for r in rows])

    print("\n%d networks, edge counts matched across arms" % len(rows))
    print("  median gain  delaunay  %+.5f" % np.median(dd))
    print("  median gain  rand_del  %+.5f" % np.median(dr))
    print("  median gain  rand_any  %+.5f" % np.median(da))
    for label, other in (("delaunay vs rand_del", dr), ("delaunay vs rand_any", da)):
        diff = dd - other
        nz = diff[diff != 0]
        if len(nz) < 3:
            print("  %-22s all differences zero" % label)
            continue
        W, p = stats.wilcoxon(nz)
        wins = int((diff > 0).sum())
        print("  %-22s median diff %+.5f   delaunay higher in %d/%d   "
              "W=%.0f  p=%.2g" % (label, float(np.median(diff)), wins,
                                  len(diff), W, p))


if __name__ == "__main__":
    sys.exit(main())
