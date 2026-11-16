# -*- coding: utf-8 -*-
r"""
run_size_matched_windows.py -- size-matched comparison for the local-leaf
validation.

The local leaves were traced as one 5.9 x 5.9 mm window each, but the archived
cohort networks are whole leaves. A small window holds far fewer junctions and
its edges cut through veins, so its threshold is not on the same footing as a
whole leaf's. This script cuts windows of the local size out of every
percolation-cohort leaf and measures them with the same engine, so the local
leaves can be compared with archived windows of the same size.

Window rules (fixed before the comparison was read):
  * side W_MM = 5.9088 mm, the local window (3,693 px x 1.6 um/px);
  * the window must lie inside the leaf, at least MARGIN_MM = 0.5 mm in from the
    leaf outline (the local windows sat >= 0.5 mm inside the cut edges). The
    outline is the junction-occupancy mask on a 0.25 mm grid, closed by 1 mm and
    hole-filled;
  * up to N_WIN = 3 non-overlapping windows per leaf, placed at random among the
    valid positions (seed 1 per leaf); leaves with no valid position are left
    out and counted;
  * inside a window: junctions inside the square, veins with both ends inside
    (veins crossing the edge are cut, as in the local windows), then only the
    largest connected component is kept, as LeafVeinCNN's "GCC" option did for
    the local leaves;
  * percolation exactly as the cohort and the local leaves: uniform removal,
    40 removal fractions up to 0.6, 60 trials each (2,400), 50% criterion, seed 1.

A leaf's value is the mean over its windows. The tolerance line and its 95%
prediction band are refitted to these per-leaf window values, and the local
leaves are checked against it.

Output:
    data/size_matched_windows.csv   one row per window
    data/size_matched_windows.json  per-leaf values, fit, local-leaf checks

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_size_matched_windows.py --workers 3
"""
import os, sys, csv, json, time, glob, argparse, zlib
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np

LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
MASTER = os.path.join(ROOT, "data", "analysis_master.csv")
LOCAL = os.path.join(ROOT, "empirical", "local_leaves.csv")
OUT_CSV = os.path.join(ROOT, "data", "size_matched_windows.csv")
OUT_JSON = os.path.join(ROOT, "data", "size_matched_windows.json")

W_MM = 3693 * 0.0016
MARGIN_MM = 0.5
CELL_MM = 0.25
CLOSE_MM = 1.0
N_WIN = 3
TARGET_NODES = 2000      # median node count of the four scored local windows (821-4,517)
MIN_NODES = 500          # windows with fewer junctions in their largest component are not analysed
FIELDS = ["mode", "species", "window", "side_mm", "x0_mm", "y0_mm", "n_nodes_window", "n_nodes",
          "n_edges", "mean_degree", "loop_fraction", "p_c", "leaf_density_per_mm2", "leaf_n_nodes",
          "leaf_mean_degree", "leaf_pc"]


def cohort():
    rows = [r for r in csv.DictReader(open(MASTER, newline=""))
            if r["in_percolation_cohort_100"] == "True"]
    rows.sort(key=lambda r: -int(r["n_nodes"]))
    return rows


def leaf_mask(xy):
    """Junction-occupancy mask of the leaf (closed, hole-filled) and its eroded version."""
    from scipy import ndimage
    x0, y0 = xy.min(0)
    ij = np.floor((xy - [x0, y0]) / CELL_MM).astype(int)
    shape = ij.max(0) + 1
    occ = np.zeros(shape, bool)
    occ[ij[:, 0], ij[:, 1]] = True
    r = int(round(CLOSE_MM / CELL_MM))
    disk = np.hypot(*np.mgrid[-r:r + 1, -r:r + 1]) <= r
    occ = np.pad(occ, r + 1)
    mask = ndimage.binary_fill_holes(ndimage.binary_closing(occ, structure=disk))
    m = int(round(MARGIN_MM / CELL_MM))
    dk = np.hypot(*np.mgrid[-m:m + 1, -m:m + 1]) <= m
    full_mask = mask[r + 1:-(r + 1), r + 1:-(r + 1)]
    mask = ndimage.binary_erosion(mask, structure=dk)[r + 1:-(r + 1), r + 1:-(r + 1)]
    return full_mask, mask, (x0, y0)


def valid_positions(mask, origin, side):
    """Lower-left corners (mm) of every side x side square lying inside the eroded mask."""
    x0, y0 = origin
    s = int(np.ceil(side / CELL_MM))
    if mask.shape[0] < s or mask.shape[1] < s:
        return np.empty((0, 2))
    I = np.pad(mask.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    full = I[s:, s:] - I[:-s, s:] - I[s:, :-s] + I[:-s, :-s]
    ii, jj = np.nonzero(full == s * s)
    return np.c_[ii, jj] * CELL_MM + [x0, y0]


def one_leaf(r):
    import networkx as nx
    import config
    from holoparasitic import realleaf, percolation
    s = r["name"]
    t0 = time.time()
    nf = glob.glob(os.path.join(LEAFDIR, s, "*_nodes.csv"))[0]
    vf = glob.glob(os.path.join(LEAFDIR, s, "*_veins.csv"))[0]
    G = realleaf.load_matos(nf, vf, name=s)
    ids = np.array(list(G.nodes))
    xy = np.array([G.nodes[n]["pos"] for n in ids], float)
    full_mask, mask, origin = leaf_mask(xy)
    density = len(ids) / (full_mask.sum() * CELL_MM ** 2)        # junctions per mm^2 of leaf
    sides = {"area": W_MM, "nodes": float(np.sqrt(TARGET_NODES / density))}
    out = []
    for mode, side in sides.items():
        pos = valid_positions(mask, origin, side)
        rng = np.random.default_rng(zlib.crc32((s + mode).encode()) ^ 1)
        chosen = []
        for k in rng.permutation(len(pos)):
            p = pos[k]
            if all(max(abs(p[0] - q[0]), abs(p[1] - q[1])) >= side for q in chosen):
                chosen.append(p)
            if len(chosen) == N_WIN:
                break
        for w, (wx, wy) in enumerate(chosen, 1):
            inside = ((xy[:, 0] >= wx) & (xy[:, 0] < wx + side) &
                      (xy[:, 1] >= wy) & (xy[:, 1] < wy + side))
            H = G.subgraph(ids[inside].tolist()).copy()
            H.remove_nodes_from(list(nx.isolates(H)))
            if H.number_of_nodes() < 10:
                continue
            H = H.subgraph(max(nx.connected_components(H), key=len)).copy()
            sm = realleaf.summary(H)
            pr = config.PercolationParams(mode="random", n_trials=2400, n_densities=40)
            pc = float(percolation.find_pc(H, pr, rho_max=0.6)["p_c"])
            out.append({"mode": mode, "species": s, "window": w, "side_mm": round(side, 3),
                        "x0_mm": round(float(wx), 3), "y0_mm": round(float(wy), 3),
                        "n_nodes_window": int(inside.sum()), "n_nodes": H.number_of_nodes(),
                        "n_edges": H.number_of_edges(), "mean_degree": round(sm["mean_degree"], 4),
                        "loop_fraction": round(sm["loop_fraction_nonbridge"], 4), "p_c": round(pc, 4),
                        "leaf_density_per_mm2": round(density, 2), "leaf_n_nodes": r["n_nodes"],
                        "leaf_mean_degree": r["mean_degree"], "leaf_pc": r["pc_random"]})
    print(f"{s:8s} N={G.number_of_nodes():7d} density={density:6.1f}/mm2 node-side={sides['nodes']:5.1f} mm "
          f"windows={len(out)} {time.time() - t0:.0f}s", flush=True)
    return s, out


def band(x, y, xs):
    """OLS line on (x - 2) and its 95% prediction band at xs."""
    from scipy import stats
    X = x - 2
    b, a = np.polyfit(X, y, 1)
    n = len(x)
    s = np.sqrt(((y - (a + b * X)) ** 2).sum() / (n - 2))
    t = stats.t.ppf(0.975, n - 2)
    xs = np.asarray(xs) - 2
    se = s * np.sqrt(1 + 1 / n + (xs - X.mean()) ** 2 / ((X - X.mean()) ** 2).sum())
    yh = a + b * xs
    return a, b, s, yh, yh - t * se, yh + t * se


def analyse(rows, n_leaves):
    """Fit and checks for one matching mode. rows: that mode's windows, already node-filtered."""
    from scipy import stats
    by = {}
    for r in rows:
        by.setdefault(r["species"], []).append(r)
    leaves = []
    for s, ws in sorted(by.items()):
        leaves.append({"species": s, "n_windows": len(ws), "side_mm": float(ws[0]["side_mm"]),
                       "mean_degree": float(np.mean([float(w["mean_degree"]) for w in ws])),
                       "p_c": float(np.mean([float(w["p_c"]) for w in ws])),
                       "n_nodes": float(np.mean([int(w["n_nodes"]) for w in ws])),
                       "leaf_mean_degree": float(ws[0]["leaf_mean_degree"]),
                       "leaf_pc": float(ws[0]["leaf_pc"])})
    res = {"cohort_leaves": n_leaves, "leaves_with_window": len(leaves),
           "leaves_without_window": n_leaves - len(leaves), "n_windows": len(rows)}
    if len(leaves) < 5:
        res["note"] = "too few leaves with a usable window to fit a line"
        res["leaves"] = leaves
        return res
    k = np.array([l["mean_degree"] for l in leaves])
    pc = np.array([l["p_c"] for l in leaves])
    a, b, s, _, _, _ = band(k, pc, [2.0])
    rho, p = stats.spearmanr(k, pc)
    rho_kk, _ = stats.spearmanr(k, [l["leaf_mean_degree"] for l in leaves])
    rho_pp, _ = stats.spearmanr(pc, [l["leaf_pc"] for l in leaves])
    wk = np.array([float(r["mean_degree"]) for r in rows])
    wp = np.array([float(r["p_c"]) for r in rows])
    rho_w, p_w = stats.spearmanr(wk, wp)
    res.update({
        "median_side_mm": float(np.median([l["side_mm"] for l in leaves])),
        "median_window_nodes": float(np.median([int(r["n_nodes"]) for r in rows])),
        "median_window_mean_degree": float(np.median(k)), "median_window_pc": float(np.median(pc)),
        "median_whole_leaf_pc_same_leaves": float(np.median([l["leaf_pc"] for l in leaves])),
        "line": {"a_at_k2": a, "slope": b, "residual_sd": s},
        "spearman_k_pc_leaves": {"rho": rho, "p": p, "n": len(leaves)},
        "spearman_k_pc_windows": {"rho": rho_w, "p": p_w, "n": len(rows)},
        "window_vs_whole_leaf": {"rho_mean_degree": rho_kk, "rho_pc": rho_pp},
        "leaves": leaves})
    if os.path.exists(LOCAL):
        L = list(csv.DictReader(open(LOCAL, newline="")))
        lk = np.array([float(x["mean_degree"]) for x in L])
        lp = np.array([float(x["p_c"]) for x in L])
        _, _, _, yh, lo, hi = band(k, pc, lk)
        r1, p2 = stats.spearmanr(lk, lp)
        res["local"] = {"n": len(L), "inside_band": int(((lp >= lo) & (lp <= hi)).sum()),
                        "spearman_rho": r1,
                        "spearman_p_one_sided": (p2 / 2 if r1 > 0 else 1 - p2 / 2),
                        "leaves": [{"common_name": x["common_name"], "mean_degree": float(kk),
                                    "p_c": float(pp), "predicted": float(y), "lo": float(l_),
                                    "hi": float(h), "residual": float(pp - y)}
                                   for x, kk, pp, y, l_, h in zip(L, lk, lp, yh, lo, hi)]}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--summarize", action="store_true", help="re-analyse the saved CSV only")
    a = ap.parse_args()
    C = cohort()
    if not a.summarize:
        rows = []
        with Pool(a.workers) as pool:
            for s, out in pool.imap_unordered(one_leaf, C):
                rows.extend(out)
        rows.sort(key=lambda r: (r["mode"], r["species"], r["window"]))
        with open(OUT_CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
    rows = list(csv.DictReader(open(OUT_CSV, newline="")))
    res = {"window_mm_area_mode": round(W_MM, 4), "target_nodes_nodes_mode": TARGET_NODES,
           "min_nodes": MIN_NODES, "margin_mm": MARGIN_MM, "max_windows_per_leaf": N_WIN}
    for mode in ("area", "nodes"):
        allw = [r for r in rows if r["mode"] == mode]
        keep = [r for r in allw if int(r["n_nodes"]) >= MIN_NODES]
        res[mode] = analyse(keep, len(C))
        res[mode]["windows_cut"] = len(allw)
        res[mode]["windows_below_min_nodes"] = len(allw) - len(keep)
    json.dump(res, open(OUT_JSON, "w"), indent=1)
    for mode in ("area", "nodes"):
        print("==", mode, json.dumps({k: v for k, v in res[mode].items() if k != "leaves"}, indent=1))


if __name__ == "__main__":
    main()
