# -*- coding: utf-8 -*-
r"""
run_criterion_and_locality.py -- FINAL PASS sections 2 and 3.

Two questions the second-pass audit left open, answered on the SAME leaves with
the SAME engine settings as the archived cohort run (n_densities=40,
trials_per_density=60 -> 2400 trials/leaf, rho_max=0.6, mode=random).

(2) SOURCE-ANCHORED CONNECTIVITY.
    The manuscript scores the giant connected component. Both prior venation-
    robustness studies score connectivity to a SOURCE (Mander & Williams 2024:
    "attached to the structural vein"; Price & Weitz 2014: "connected to the
    root node"). realleaf already assigns a source and records the rule in
    G.graph['root_rule'] (operative rule here: 'widest_vein' -- the endpoint of
    the largest-caliber vein, since no Matos leaf carries a petiole flag).
    Both criteria are evaluated on the SAME removal draws, so the comparison is
    exactly paired.

    Convention: the source node is PROTECTED from removal, matching Mander &
    Williams, where the structural vein is a separate layer that is not attacked.
    Protecting one node of N >= 1436 shifts the removed fraction by < 0.07%, so
    the GCC threshold remains directly comparable to the archived value -- which
    this script checks explicitly per leaf.

(3) LOCALISED CONTIGUOUS-DISC REMOVAL.
    Random site removal disperses damage uniformly. A haustorial lesion, a bite
    or a necrotic patch is spatially contiguous. Two localised protocols are run
    at MATCHED REALISED REMOVED FRACTIONS, so the x-axis is identical to the
    random case and the thresholds are directly comparable:
      disc1  -- one disc: remove the f*N non-source nodes nearest a random centre
      disc10 -- ten discs: round-robin from ten random centres until f*N removed
    (Mander & Williams used many small circular blade holes; disc10 is the
    closer analogue, disc1 the harsher single-lesion bound.)

    python scripts/run_criterion_and_locality.py [--limit N] [--resume]

Outputs data/criterion_and_locality.{csv,json}.  Resumable.  ASCII-only stdout.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy import stats

import config
from holoparasitic import realleaf, network, percolation

LEAFDIR = ROOT / "UCBG_venation_form_data" / "UCBG_venation_form_data"
OUT_CSV = ROOT / "data" / "criterion_and_locality.csv"
OUT_JSON = ROOT / "data" / "criterion_and_locality.json"

N_DENSITIES = 40
TRIALS_PER_DENSITY = 60
RHO_MAX = 0.6
SEED = 1
COLLAPSE_FRACTION = 0.5

FIELDS = ["species", "N", "E", "root_rule", "pc_gcc", "pc_source",
          "pc_disc1", "pc_disc10", "pc_archived", "seconds"]


def cohort_species() -> list[str]:
    """The locked 100-leaf percolation cohort, ASCENDING in size so that a run
    interrupted early still yields a broad, documented sample rather than only
    the handful of largest leaves."""
    path = ROOT / "data" / "cohort.csv"
    with open(path, newline="") as f:
        rows = [r for r in csv.DictReader(f)
                if r.get("include", "").strip() == "True"]
    rows.sort(key=lambda r: int(r["n_edges"]))
    return [r["name"] for r in rows]


def archived_pc() -> dict:
    out = {}
    with open(ROOT / "data" / "analysis_master.csv", newline="") as f:
        for r in csv.DictReader(f):
            try:
                out[r["name"]] = float(r["pc_random"])
            except (ValueError, KeyError):
                pass
    return out


def _fit(rhos_all, outcomes_all):
    """Logistic p_c with the crossing fallback -- identical to percolation.find_pc."""
    X = np.asarray(rhos_all, float)
    y = np.asarray(outcomes_all, np.int8)
    fit = percolation.fit_pc(X, y)
    pc = fit["p_c"]
    # empirical crossing on the per-density means
    rhos = np.unique(X)
    means = np.array([y[X == r].mean() for r in rhos])
    cross = percolation.pc_crossing(rhos, means)
    if not np.isfinite(pc) or not (0.0 <= pc <= 1.0):
        pc = cross
    return float(pc)


def run_leaf(G, rng_seed=SEED):
    """Return (pc_gcc, pc_source, pc_disc1, pc_disc10) for one graph."""
    adj, nodes = network.to_csr(G)
    n = adj.shape[0]
    idx_of = {nd: i for i, nd in enumerate(nodes)}
    root_i = idx_of[G.graph["root"]]
    pos = np.array([G.nodes[nd]["pos"] for nd in nodes], float)
    threshold = COLLAPSE_FRACTION * n
    rhos = np.linspace(0.0, RHO_MAX, N_DENSITIES)

    pool = np.setdiff1d(np.arange(n), np.array([root_i]))  # source protected

    def sizes(keep_idx):
        """(gcc size, size of the component containing the source)."""
        if keep_idx.size == 0:
            return 0, 0
        sub = adj[keep_idx][:, keep_idx]
        ncomp, labels = connected_components(sub, directed=False)
        counts = np.bincount(labels)
        gcc = int(counts.max())
        where_root = np.flatnonzero(keep_idx == root_i)
        src = int(counts[labels[where_root[0]]]) if where_root.size else 0
        return gcc, src

    # ---- paired random sweep: GCC and source-anchored on identical draws ----
    rng = config.new_rng(rng_seed)
    X, y_gcc, y_src = [], [], []
    for rho in rhos:
        for _ in range(TRIALS_PER_DENSITY):
            drop = rng.random(pool.size) < rho
            keep = np.concatenate(([root_i], pool[~drop]))
            keep.sort()
            g, s = sizes(keep)
            X.append(rho)
            y_gcc.append(1 if g < threshold else 0)
            y_src.append(1 if s < threshold else 0)
    pc_gcc = _fit(X, y_gcc)
    pc_src = _fit(X, y_src)

    # ---- localised removal at matched realised fractions -------------------
    #  Each replicate draws its centres ONCE and grows the lesion across the
    #  density sweep, so the removed sets are nested (a growing patch, which is
    #  also the more realistic damage progression and matches Mander & Williams'
    #  "varying the proportion removed"). This also removes the per-density
    #  re-sort, which is what made the naive version intractable on 300k-node
    #  leaves.
    max_m = int(round(RHO_MAX * n))

    def disc_sweep(n_discs, seed):
        r2 = config.new_rng(seed)
        Xd, yd = [], []
        for _ in range(TRIALS_PER_DENSITY):
            centres = r2.choice(pool, size=n_discs, replace=False)
            # per centre, the pool ordered by distance, truncated to what the
            # largest density could possibly need
            need = min(pool.size, max_m + n_discs)
            orders = []
            for c in centres:
                d2 = ((pos[pool] - pos[c]) ** 2).sum(axis=1)
                if need < pool.size:
                    part = np.argpartition(d2, need - 1)[:need]
                    part = part[np.argsort(d2[part], kind="stable")]
                else:
                    part = np.argsort(d2, kind="stable")
                orders.append(pool[part])
            # round-robin merge -> one ordering whose prefixes are the nested
            # multi-disc lesions
            merged, seen = [], set()
            j = 0
            while len(merged) < max_m and j < need:
                for o in orders:
                    if len(merged) >= max_m:
                        break
                    v = int(o[j])
                    if v not in seen:
                        seen.add(v)
                        merged.append(v)
                j += 1
            merged = np.array(merged, int)
            all_idx = np.arange(n)
            for rho in rhos:
                m = min(int(round(rho * n)), merged.size)
                keep = (all_idx if m <= 0
                        else np.setdiff1d(all_idx, merged[:m], assume_unique=True))
                g, _s = sizes(keep)
                Xd.append((n - keep.size) / n)      # REALISED removed fraction
                yd.append(1 if g < threshold else 0)
        return _fit(Xd, yd)

    pc_d1 = disc_sweep(1, SEED + 11)
    pc_d10 = disc_sweep(10, SEED + 12)
    return pc_gcc, pc_src, pc_d1, pc_d10


def summarise() -> dict:
    rows = list(csv.DictReader(open(OUT_CSV, newline="")))
    def col(k):
        return np.array([float(r[k]) for r in rows if r[k] not in ("", "nan")])
    g, s = col("pc_gcc"), col("pc_source")
    d1, d10 = col("pc_disc1"), col("pc_disc10")
    a = col("pc_archived")
    paired = [(float(r["pc_gcc"]), float(r["pc_source"]), float(r["pc_disc1"]),
               float(r["pc_disc10"]), float(r["pc_archived"])) for r in rows]
    P = np.array(paired)
    out = {
        "_purpose": "final-pass sections 2 and 3: criterion choice and damage "
                    "locality",
        "_generated_by": "scripts/run_criterion_and_locality.py",
        "settings": {"n_densities": N_DENSITIES,
                     "trials_per_density": TRIALS_PER_DENSITY,
                     "n_trials_per_leaf_per_mode": N_DENSITIES * TRIALS_PER_DENSITY,
                     "rho_max": RHO_MAX, "seed": SEED,
                     "collapse_criterion": "component < 0.5 * N0, P = 0.50",
                     "source_rule": "realleaf G.graph['root_rule'] "
                                    "(operative: widest_vein); source protected "
                                    "from removal"},
        "n": len(rows),
        "replication_check_vs_archive": {
            "spearman_gcc_vs_archived": round(float(stats.spearmanr(P[:, 0], P[:, 4])[0]), 4),
            "median_abs_difference": round(float(np.median(np.abs(P[:, 0] - P[:, 4]))), 5),
            "median_gcc_here": round(float(np.median(P[:, 0])), 4),
            "median_gcc_archived": round(float(np.median(P[:, 4])), 4),
        },
        "criterion_comparison": {
            "median_gcc": round(float(np.median(g)), 4),
            "iqr_gcc": [round(float(np.percentile(g, 25)), 4),
                        round(float(np.percentile(g, 75)), 4)],
            "median_source": round(float(np.median(s)), 4),
            "iqr_source": [round(float(np.percentile(s, 25)), 4),
                           round(float(np.percentile(s, 75)), 4)],
            "spearman": round(float(stats.spearmanr(P[:, 0], P[:, 1])[0]), 4),
            "pearson": round(float(stats.pearsonr(P[:, 0], P[:, 1])[0]), 4),
            "median_paired_difference_source_minus_gcc": round(
                float(np.median(P[:, 1] - P[:, 0])), 5),
            "wilcoxon_p": float(stats.wilcoxon(P[:, 1] - P[:, 0]).pvalue)
            if np.any(P[:, 1] != P[:, 0]) else 1.0,
            "n_source_lower": int((P[:, 1] < P[:, 0]).sum()),
            "n_source_higher": int((P[:, 1] > P[:, 0]).sum()),
        },
        "locality_comparison": {
            "median_random_gcc": round(float(np.median(g)), 4),
            "median_disc1": round(float(np.median(d1)), 4),
            "iqr_disc1": [round(float(np.percentile(d1, 25)), 4),
                          round(float(np.percentile(d1, 75)), 4)],
            "median_disc10": round(float(np.median(d10)), 4),
            "iqr_disc10": [round(float(np.percentile(d10, 25)), 4),
                           round(float(np.percentile(d10, 75)), 4)],
            "median_paired_difference_disc1_minus_random": round(
                float(np.median(P[:, 2] - P[:, 0])), 5),
            "median_paired_difference_disc10_minus_random": round(
                float(np.median(P[:, 3] - P[:, 0])), 5),
            "wilcoxon_disc1_p": float(stats.wilcoxon(P[:, 2] - P[:, 0]).pvalue),
            "wilcoxon_disc10_p": float(stats.wilcoxon(P[:, 3] - P[:, 0]).pvalue),
            "n_disc1_lower_than_random": int((P[:, 2] < P[:, 0]).sum()),
            "n_disc10_lower_than_random": int((P[:, 3] < P[:, 0]).sum()),
        },
    }
    # does the connectivity result survive under each criterion?
    master = {r["name"]: r for r in
              csv.DictReader(open(ROOT / "data" / "analysis_master.csv", newline=""))}
    k, lf, D = [], [], []
    for r in rows:
        m = master.get(r["species"])
        if m:
            k.append(float(m["mean_degree"]))
            lf.append(float(m["loop_fraction_nonbridge"]))
            D.append(float(m["D"]))
    k, lf, D = np.array(k), np.array(lf), np.array(D)
    out["associations_under_each_criterion"] = {}
    for label, col_ in (("gcc", P[:, 0]), ("source_anchored", P[:, 1]),
                        ("disc1", P[:, 2]), ("disc10", P[:, 3])):
        out["associations_under_each_criterion"][label] = {
            "spearman_x_mean_degree": [round(float(stats.spearmanr(k, col_)[0]), 4),
                                       float(stats.spearmanr(k, col_)[1])],
            "spearman_x_loop_fraction": [round(float(stats.spearmanr(lf, col_)[0]), 4),
                                         float(stats.spearmanr(lf, col_)[1])],
            "spearman_x_D": [round(float(stats.spearmanr(D, col_)[0]), 4),
                             float(stats.spearmanr(D, col_)[1])],
        }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--summarise-only", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    if args.summarise_only:
        print(json.dumps(summarise(), indent=2))
        return

    spp = cohort_species()
    if args.limit:
        spp = spp[:args.limit]
    arch = archived_pc()
    done = set()
    if OUT_CSV.exists():
        with open(OUT_CSV, newline="") as f:
            done = {r["species"] for r in csv.DictReader(f)}
    print("cohort leaves: %d (done %d); %d trials/leaf/mode"
          % (len(spp), len(done), N_DENSITIES * TRIALS_PER_DENSITY))

    write_header = not OUT_CSV.exists()
    for i, s in enumerate(spp, 1):
        if s in done:
            continue
        t0 = time.time()
        try:
            nf = glob.glob(str(LEAFDIR / s / "*_nodes.csv"))[0]
            vf = glob.glob(str(LEAFDIR / s / "*_veins.csv"))[0]
            G = realleaf.load_matos(nf, vf, name=s)
            pc_g, pc_s, pc_1, pc_10 = run_leaf(G)
        except Exception as exc:
            print("  [%d/%d] %s FAILED: %s" % (i, len(spp), s, exc))
            continue
        row = {"species": s, "N": G.number_of_nodes(), "E": G.number_of_edges(),
               "root_rule": G.graph.get("root_rule", ""),
               "pc_gcc": round(pc_g, 4), "pc_source": round(pc_s, 4),
               "pc_disc1": round(pc_1, 4), "pc_disc10": round(pc_10, 4),
               "pc_archived": arch.get(s, ""),
               "seconds": round(time.time() - t0, 1)}
        with open(OUT_CSV, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if write_header:
                w.writeheader()
                write_header = False
            w.writerow(row)
        print("  [%d/%d] %-9s N=%-7d gcc=%.4f src=%.4f d1=%.4f d10=%.4f "
              "(arch %.4f) %.1fs"
              % (i, len(spp), s, row["N"], pc_g, pc_s, pc_1, pc_10,
                 arch.get(s, float("nan")), row["seconds"]))

    print(json.dumps(summarise(), indent=2))
    print("\nwrote %s and %s" % (OUT_CSV.relative_to(ROOT),
                                 OUT_JSON.relative_to(ROOT)))


if __name__ == "__main__":
    main()
