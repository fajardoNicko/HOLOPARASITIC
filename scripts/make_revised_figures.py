# -*- coding: utf-8 -*-
r"""
make_revised_figures.py -- redraw every paper figure that the SRC revisions
changed, numbered as in the revised paper (SRC_WRITING_REVISIONS, Results map).

Changed figures and why:
  Figure 1   pipeline: "Attack simulation" is now "Removal simulation"; adds the
             crossing filter, localized damage, the collapse-criterion check and
             the local-leaf validation.
  Figure 2   Cissus antarctica window, enhancement rebuilt WITH the crossing
             filter (no added vein crosses a traced vein).
  Figure 4   collapse curves: "uniform" / "degree-weighted" removal, and the
             uncapped 95% bootstrap intervals (data/uncapped_ci.json).
  Figure 6   p_c against <k> and D (old Figure 7): neutral title; the D
             association depends on the collapse criterion (Figure 8).
  Figure 9   enhancement gain per network, from the crossing-filtered rerun
             (data/planarity_check.csv); no network can fall below the diagonal
             by construction, and the figure says so.
  Figure 10  Metapanax davidii before/after, crossing filter.
  Figure 11  placement control (old Figure 14), crossing-filtered arms
             (data/planar_edge_control.csv); random node pairs relabelled.
  Figure 12  haustorial sink field (old Figure 6): drawn by make_sink_demo.py,
             whose titles no longer claim the sink "never" causes failure.
  Figure 15  size sweep (old Figure 12): labels state that loop fraction fell.
Unchanged figures (3, 5, 7, 13) and the new Figure 8 are copied in under their
new numbers so figures/revised/ holds the full set. Figure 14 (local leaves) is
drawn by make_local_validation_figure.py.

Everything is read from data/ except Figures 2 and 10 (they rebuild the
enhanced network from the Matos tracings) and the degree-weighted curve of
Figure 4, which is computed once on the reference network (100,000 trials,
the original budget) and cached in data/hero_degree_curve.json.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_revised_figures.py [1 2 4 ...]
"""
import csv
import glob
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats

import config
from holoparasitic import network, percolation, realleaf, planarity

DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(FIG, "revised")
LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
TARGET_K = 2.811

INK, MUTED = "#20303A", "#5A6A73"
RED, GREEN, BLUE, VEIN, ORANGE = "#c1121f", "#1f6f4a", "#2F7FA8", "#7A4E2D", "#E4572E"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#8a959c", "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.titlecolor": INK,
                     "axes.titlesize": 11, "axes.titleweight": "bold"})


def out(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def save(fig, name, dpi=300):
    p = out(name)
    fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=0.12, facecolor="white")
    plt.close(fig)
    print("SAVED", os.path.relpath(p, ROOT))


def master():
    return list(csv.DictReader(open(os.path.join(DATA, "analysis_master.csv"), newline="")))


def leaf(spp):
    d = os.path.join(LEAFDIR, spp)
    return realleaf.load_matos(glob.glob(os.path.join(d, "*_nodes.csv"))[0],
                               glob.glob(os.path.join(d, "*_veins.csv"))[0], name=spp)


def planar_enhanced(G):
    cand = planarity.delaunay_candidates(G)
    crosses = planarity.crossing_candidates(G, cand)
    G2, added, skipped = planarity.add_loops_planar(G, TARGET_K, cand, crosses)
    return G2, added, skipped


def draw_net(ax, G, xlim=None, ylim=None, lw_base=(0.05, 0.9), lw_add=0.35, show_added=True):
    pos = {n: G.nodes[n]["pos"] for n in G.nodes}
    base, add, brad = [], [], []
    for u, v, d in G.edges(data=True):
        (x0, y0), (x1, y1) = pos[u], pos[v]
        if xlim is not None and (max(x0, x1) < xlim[0] or min(x0, x1) > xlim[1]
                                 or max(y0, y1) < ylim[0] or min(y0, y1) > ylim[1]):
            continue
        if d.get("kind") == "added_loop":
            add.append([pos[u], pos[v]])
        else:
            base.append([pos[u], pos[v]]); brad.append(d.get("radius", 0.01))
    brad = np.array(brad, float)
    lw = lw_base[0] + lw_base[1] * (brad / (brad.max() if brad.size else 1.0)) ** 0.5
    ax.add_collection(LineCollection(base, colors=VEIN, linewidths=lw, capstyle="round", zorder=2))
    if show_added and add:
        ax.add_collection(LineCollection(add, colors=BLUE, linewidths=lw_add, capstyle="round",
                                         zorder=3, alpha=0.9))
    if xlim is None:
        P = np.array(list(pos.values()))
        xlim, ylim = (P[:, 0].min(), P[:, 0].max()), (P[:, 1].min(), P[:, 1].max())
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")
    return len(add)


# ---------------------------------------------------------------- Figure 1
def fig01():
    rows = [
        ("STAGE 1  Network data", ["Dryad dataset\n(Matos et al., 2024c)", "Graph reconstruction\n(NetworkX)",
                                   "Characterization of\nreal networks", "Reticulation enhancement\n(with crossing filter)"]),
        ("STAGE 2  Simulation", ["Removal simulation\n(uniform, degree-weighted)", "Localized damage\n(1 and 10 lesions)",
                                 "Monte Carlo percolation\n(logistic fit, p_c)", "Collapse-criterion check\n(10% to 90%)"]),
        ("STAGE 3  Analysis and checks", ["Haustorial sink model\n(separate hydraulic lens)", "Statistical analysis",
                                          "Local-leaf validation\n(crop and non-crop)", "Outputs\n(CSV, JSON, figures)"]),
    ]
    fill, edge, txt = "#dcefff", "#5aa9e6", "#2f7fc4"
    fig, ax = plt.subplots(figsize=(13, 6.4))
    ax.set_xlim(0, 13); ax.set_ylim(0, 6.4); ax.axis("off")
    bw, bh, xs = 2.55, 0.95, [1.55, 4.45, 7.35, 10.25]
    ys = [5.0, 3.0, 1.0]
    n = 0
    centers = []
    for r, (stage, boxes) in enumerate(rows):
        order = xs if r % 2 == 0 else xs[::-1]
        if r == 2:   # the arrow into row 3 comes down on the left, so label this row on the right
            ax.text(12.95, ys[r] + 0.78, stage, fontsize=10.5, fontweight="bold", color=txt, ha="right")
        else:
            ax.text(0.05, ys[r] + 0.78, stage, fontsize=10.5, fontweight="bold", color=txt)
        row_c = []
        for x, label in zip(order, boxes):
            n += 1
            ax.add_patch(FancyBboxPatch((x - bw / 2 + 0.6, ys[r] - bh / 2), bw, bh,
                                        boxstyle="round,pad=0.02,rounding_size=0.18",
                                        fc=fill, ec=edge, lw=1.6))
            ax.text(x + 0.6, ys[r], label, ha="center", va="center", fontsize=9.6, color=txt)
            ax.text(x - bw / 2 + 0.72, ys[r] + bh / 2 - 0.1, str(n), ha="left", va="top",
                    fontsize=8.5, fontweight="bold", color=edge)
            row_c.append((x + 0.6, ys[r]))
        centers.append(row_c)
    arrow = dict(arrowstyle="-|>", mutation_scale=16, color=edge, lw=1.6)
    for r, row_c in enumerate(centers):
        for (x0, y0), (x1, y1) in zip(row_c[:-1], row_c[1:]):
            sgn = 1 if x1 > x0 else -1
            ax.add_patch(FancyArrowPatch((x0 + sgn * bw / 2, y0), (x1 - sgn * bw / 2, y1), **arrow))
        if r < len(centers) - 1:
            x, y = row_c[-1]
            ax.add_patch(FancyArrowPatch((x, y - bh / 2), (x, ys[r + 1] + bh / 2), **arrow))
    save(fig, "Figure_01_pipeline.png")


# ---------------------------------------------------------------- Figure 2
def fig02():
    spp, frac = "Cis_ant", 0.26
    G = leaf(spp)
    G2, added, skipped = planar_enhanced(G)
    k0 = 2 * G.number_of_edges() / G.number_of_nodes()
    k1 = 2 * G2.number_of_edges() / G2.number_of_nodes()
    pos = {n: G2.nodes[n]["pos"] for n in G2.nodes}
    P = np.array(list(pos.values()), float)
    xr, yr = (P[:, 0].min(), P[:, 0].max()), (P[:, 1].min(), P[:, 1].max())
    side = frac * max(xr[1] - xr[0], yr[1] - yr[0])
    mids = np.array([((pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2)
                     for u, v, d in G2.edges(data=True) if d.get("kind") == "added_loop"])
    C = np.median(mids, axis=0)
    cx = float(np.clip(C[0], xr[0] + side / 2, xr[1] - side / 2))
    cy = float(np.clip(C[1], yr[0] + side / 2, yr[1] - side / 2))
    xl, yl = (cx - side / 2, cx + side / 2), (cy - side / 2, cy + side / 2)
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(15, 7.7))
    draw_net(a0, G, xl, yl, lw_base=(0.5, 2.2))
    shown = draw_net(a1, G2, xl, yl, lw_base=(0.5, 2.2), lw_add=1.1)
    a0.set_title("Original (traced network)", fontsize=13)
    a1.set_title("Enhanced (added veins in blue)", fontsize=13)
    a0.text(0.5, -0.02, r"$\langle k \rangle$ = %.2f" % k0, transform=a0.transAxes,
            ha="center", va="top", fontsize=11, color=INK)
    a1.text(0.5, -0.02, r"$\langle k \rangle$ = %.2f    +%d added veins in view    no added vein crosses a traced vein"
            % (k1, shown), transform=a1.transAxes, ha="center", va="top", fontsize=11, color=BLUE)
    print("  Cis_ant: N=%d  <k> %.3f -> %.3f  added %d  skipped (crossing) %d"
          % (G.number_of_nodes(), k0, k1, added, skipped))
    save(fig, "Figure_02_Cissus_enhancement.png", dpi=350)


# ---------------------------------------------------------------- Figure 4
def hero_degree_curve():
    path = os.path.join(DATA, "hero_degree_curve.json")
    if os.path.exists(path):
        return json.load(open(path))
    G = network.generate()
    _, nodes = network.to_csr(G)
    pp = config.PercolationParams(mode="targeted", n_trials=100_000, n_densities=50)
    w = percolation.importance_weights(G, nodes, metric="degree")
    r = percolation.find_pc(G, pp, weights=w)
    d = {"what": "degree-weighted removal on the calibrated synthetic reference network "
                 "(network.generate()), 100,000 trials, 50 densities, seed 1; same call as run_full.py",
         "N": G.number_of_nodes(), "n_trials": 100_000, "p_c": float(r["p_c"]),
         "rhos": [float(x) for x in r["rhos"]], "p_collapse": [float(x) for x in r["p_collapse"]],
         "gcc_fraction": [float(x) for x in r["gcc_fraction"]]}
    json.dump(d, open(path, "w"), indent=1)
    return d


def _curve(ax, rhos, pcol, gcc, tpd, pc, ci, title):
    rhos, pcol = np.asarray(rhos), np.asarray(pcol)
    X = np.repeat(rhos, tpd)
    y = np.concatenate([np.r_[np.ones(int(round(p * tpd))), np.zeros(tpd - int(round(p * tpd)))] for p in pcol])
    fit = percolation.fit_pc(X, y)
    xs = np.linspace(0, 1, 400)
    ax.scatter(rhos, pcol, s=18, color=RED, zorder=3, label="P(collapse), Monte Carlo")
    ax.plot(xs, fit["model"].predict_proba(xs.reshape(-1, 1))[:, 1], color=RED, lw=2, label="logistic fit")
    ax.plot(rhos, gcc, color=GREEN, lw=2, marker="o", ms=3, label="largest-component fraction")
    ax.axhline(0.5, color="0.6", ls=":", lw=1)
    ax.axvline(pc, color="black", ls="--", lw=1.5)
    ax.axvspan(ci[0], ci[1], color="black", alpha=0.08)
    ax.text(pc + 0.02, 0.14, "$p_c$ = %.4f\n95%% CI [%.4f, %.4f]" % (pc, ci[0], ci[1]), fontsize=10)
    ax.set_xlim(0, 1); ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel(r"fraction of junctions removed, $\rho$")
    ax.set_ylabel("probability / fraction")
    ax.set_title(title, loc="left")
    ax.legend(loc="center right", fontsize=8.5); ax.grid(alpha=0.25)


def fig04():
    z = np.load(os.path.join(DATA, "results.npz"))
    U = json.load(open(os.path.join(DATA, "uncapped_ci.json")))["results"]
    dg = hero_degree_curve()
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5))
    _curve(a, z["rhos"], z["p_collapse"], z["gcc_fraction"], 20_000, U["random"]["p_c"],
           U["random"]["ci95_uncapped"], "4.a  Uniform removal (N = 1,023, 1,000,000 trials)")
    _curve(b, dg["rhos"], dg["p_collapse"], dg["gcc_fraction"], 2_000, U["degree"]["p_c"],
           U["degree"]["ci95_uncapped"], "4.b  Degree-weighted removal (N = 1,023, 100,000 trials)")
    if abs(dg["p_c"] - U["degree"]["p_c"]) > 5e-4:
        print("  WARNING: cached degree curve p_c %.4f differs from uncapped_ci %.4f" % (dg["p_c"], U["degree"]["p_c"]))
    fig.text(0.5, -0.02, "Collapse: largest connected component below half of the original junctions. "
             "Shaded band: 95% percentile bootstrap interval (B = 200), resampling all trials.",
             ha="center", fontsize=9, color=MUTED, style="italic")
    save(fig, "Figure_04_collapse_curves.png")


# ---------------------------------------------------------------- Figure 6
def _partial_spearman(x, y, z):
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    rxy, rxz, ryz = (np.corrcoef(a, b)[0, 1] for a, b in ((rx, ry), (rx, rz), (ry, rz)))
    return (rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def fig06():
    rows = [r for r in master() if r["in_percolation_cohort_100"] == "True"]
    pc = np.array([float(r["pc_random"]) for r in rows])
    k = np.array([float(r["mean_degree"]) for r in rows])
    D = np.array([float(r["D"]) for r in rows])
    A = np.array([r["grade"] == "A" for r in rows])
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, x, other, name, lab in ((axs[0], k, D, r"$\langle k \rangle$", "6.a"), (axs[1], D, k, "D", "6.b")):
        rho, p = stats.spearmanr(x, pc)
        part = _partial_spearman(x, pc, other)
        ax.scatter(x[~A], pc[~A], s=22, color="#7fb3d5", edgecolor="white", lw=0.4, label="grades B, C, D")
        ax.scatter(x[A], pc[A], s=26, color=ORANGE, edgecolor="white", lw=0.4, label="grade A (artifact-free)")
        sl, ic = np.polyfit(x, pc, 1)
        xx = np.linspace(x.min(), x.max(), 50)
        ax.plot(xx, ic + sl * xx, color=INK, ls="--", lw=1.2)
        ax.set_title("%s  Threshold vs %s" % (lab, "mean degree" if name != "D" else "fractal dimension"), loc="left")
        ax.text(0.03, 0.96, "Spearman ρ = %.3f (p < .001)\npartial ρ, %s held = %.3f"
                % (rho, "D" if name != "D" else r"$\langle k \rangle$", part),
                transform=ax.transAxes, va="top", fontsize=9.5, color=INK)
        ax.set_xlabel(("mean degree " + r"$\langle k \rangle$") if name != "D" else "fractal dimension D")
        ax.grid(alpha=0.25)
    axs[0].set_ylabel("$p_c$ (uniform removal)")
    axs[1].legend(loc="lower right", fontsize=8.5)
    fig.text(0.5, -0.03, "n = 100 percolation-cohort networks, 50% criterion. The D association depends on the "
             "collapse criterion (Figure 8) and on network size; the mean-degree association does not.",
             ha="center", fontsize=9, color=MUTED, style="italic")
    save(fig, "Figure_06_threshold_vs_architecture.png")


# ---------------------------------------------------------------- Figure 9
def fig09():
    rows = list(csv.DictReader(open(os.path.join(DATA, "planarity_check.csv"), newline="")))
    cur = np.array([float(r["pc_current_f50"]) for r in rows])
    enh = np.array([float(r["pc_planar_f50"]) for r in rows])
    d = enh - cur
    same = np.array([int(r["planar_added"]) == 0 for r in rows])
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.15]})
    a.scatter(cur[~same], enh[~same], s=20, color=BLUE, edgecolor="white", lw=0.4,
              label="veins added (%d)" % (~same).sum())
    a.scatter(cur[same], enh[same], s=20, color="0.6", edgecolor="white", lw=0.4,
              label="already above the ceiling (%d)" % same.sum())
    lim = (0, max(cur.max(), enh.max()) * 1.05)
    a.plot(lim, lim, color=INK, lw=1, ls="--")
    a.set_xlim(lim); a.set_ylim(lim); a.set_aspect("equal")
    a.set_xlabel("$p_c$, traced network"); a.set_ylabel("$p_c$, enhanced network")
    a.set_title("9.a  Each network against itself", loc="left")
    a.legend(loc="lower right", fontsize=8.5); a.grid(alpha=0.25)
    b.hist(d[~same], bins=18, color=ORANGE, edgecolor="white")
    med = np.median(d)
    b.axvline(med, color=INK, ls="--", lw=1.4)
    b.text(med + 0.001, b.get_ylim()[1] * 0.92, "median gain, all %d = %.4f\n(%d networks gained 0)" % (len(d), med, same.sum()), fontsize=9.5)
    b.set_xlabel(r"$\Delta p_c$ (enhanced $-$ traced)"); b.set_ylabel("networks")
    b.set_title("9.b  Size of the gain (networks that received veins)", loc="left")
    b.grid(alpha=0.25, axis="y")
    fig.text(0.5, -0.04, "n = 105 enhancement-cohort networks, 10,000 trials each, crossing filter on, 50% criterion. "
             "No point can fall below the diagonal: the enhanced network keeps every traced vein\n"
             "and shares the original's removal draws, so the result rests on the size of the gain.",
             ha="center", fontsize=9, color=MUTED, style="italic")
    save(fig, "Figure_09_enhancement_gain.png")


# ---------------------------------------------------------------- Figure 10
def fig10():
    spp = "Met_dav"
    G = leaf(spp)
    G2, added, skipped = planar_enhanced(G)
    row = next(r for r in csv.DictReader(open(os.path.join(DATA, "planarity_check.csv"))) if r["species"] == spp)
    m = next(r for r in master() if r["name"] == spp)
    k0 = 2 * G.number_of_edges() / G.number_of_nodes()
    k1 = 2 * G2.number_of_edges() / G2.number_of_nodes()
    p0, p1 = float(row["pc_current_f50"]), float(row["pc_planar_f50"])
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(13, 7.2))
    draw_net(a0, G); draw_net(a1, G2)
    a0.set_title("Traced network", fontsize=13); a1.set_title("Enhanced network (added veins in blue)", fontsize=13)
    for ax, kk, pc in ((a0, k0, p0), (a1, k1, p1)):
        ax.text(0.5, -0.02, r"$\langle k \rangle$ = %.2f    D = %.2f    $p_c$ = %.3f" % (kk, float(m["D"]), pc),
                transform=ax.transAxes, ha="center", va="top", fontsize=11, color=INK)
    a1.text(0.5, -0.07, "+%d added veins; none crosses a traced vein; existing veins unchanged" % added,
            transform=a1.transAxes, ha="center", va="top", fontsize=9.5, color=BLUE, style="italic")
    fig.suptitle("Metapanax davidii: $p_c$ %.3f to %.3f (+%.4f)" % (p0, p1, p1 - p0), fontsize=12.5, y=0.99)
    print("  Met_dav: added %d  skipped %d  pc %.4f -> %.4f" % (added, skipped, p0, p1))
    save(fig, "Figure_10_Metapanax_enhancement.png", dpi=300)


# ---------------------------------------------------------------- Figure 11
def fig11():
    rows = list(csv.DictReader(open(os.path.join(DATA, "planar_edge_control.csv"), newline="")))
    k = np.array([float(r["k_current"]) for r in rows])
    g1 = np.array([float(r["pc_delaunay_planar_f50"]) - float(r["pc_current_f50"]) for r in rows])
    g2 = np.array([float(r["pc_rand_del_planar_f50"]) - float(r["pc_current_f50"]) for r in rows])
    g3 = np.array([float(r["pc_rand_any_archived"]) - float(r["pc_current_archived"]) for r in rows])
    arms = [("Shortest-first\nDelaunay", g1, BLUE), ("Random-order\nDelaunay", g2, ORANGE),
            ("Random node pairs\n(cross existing veins)", g3, RED)]
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5))
    for i in range(len(rows)):
        a.plot([0, 1, 2], [g1[i], g2[i], g3[i]], color="0.8", lw=0.8, zorder=1)
    for j, (lab, g, c) in enumerate(arms):
        a.scatter(np.full(len(g), j) + np.random.default_rng(j).uniform(-0.06, 0.06, len(g)), g, s=16, color=c, zorder=2)
        m = np.median(g)
        a.plot([j - 0.2, j + 0.2], [m, m], color="black", lw=2.5, zorder=3)
        a.text(j + 0.23, m, "median +%.4f" % m, va="center", fontsize=9)
    a.set_xticks([0, 1, 2]); a.set_xticklabels([x[0] for x in arms]); a.set_xlim(-0.45, 2.85)
    a.set_ylabel(r"$\Delta p_c$ (enhanced $-$ traced)")
    a.set_title("11.a  Same number of added veins, three placement rules", loc="left"); a.grid(alpha=0.25, axis="y")
    for lab, g, c in arms:
        b.scatter(k, g, s=18, color=c, label=lab.replace("\n", " "))
        sl, ic = np.polyfit(k, g, 1)
        xx = np.linspace(k.min(), k.max(), 20)
        b.plot(xx, ic + sl * xx, color=c, ls="--", lw=1)
    b.set_xlabel(r"baseline mean degree $\langle k \rangle$"); b.set_ylabel(r"$\Delta p_c$")
    b.set_title("11.b  Gain against baseline connectivity", loc="left")
    b.legend(fontsize=8.5); b.grid(alpha=0.25)
    fig.text(0.5, -0.03, "n = %d networks, 2,400 trials per arm, edge counts matched within each network. The two "
             "Delaunay arms use the crossing filter; random node pairs almost all cross an existing vein\n"
             "(a leaf cannot build them) and serve only as a reference." % len(rows),
             ha="center", fontsize=9, color=MUTED, style="italic")
    print("  medians: shortest %.4f  random-order %.4f  random pairs %.4f" % (np.median(g1), np.median(g2), np.median(g3)))
    save(fig, "Figure_11_placement_control.png")


# ---------------------------------------------------------------- Figure 12
def fig12():
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "make_sink_demo.py")], check=True, cwd=ROOT)
    shutil.copy(os.path.join(FIG, "sink_demo.png"), out("Figure_12_sink_field.png"))
    print("SAVED figures/revised/Figure_12_sink_field.png (from make_sink_demo.py)")


# ---------------------------------------------------------------- Figure 15
def fig15():
    S = json.load(open(os.path.join(DATA, "finite_size_fixedD.json")))["sizes"]
    N = np.array([s["N"] for s in S]); pc = np.array([s["p_c"] for s in S])
    lo = np.array([s["ci95"][0] for s in S]); hi = np.array([s["ci95"][1] for s in S])
    w = np.array([s["width_0.1_0.9"] for s in S])
    lf = np.array([s["unpinned_descriptors"]["loop_fraction_nonbridge"] for s in S])
    D = [s["D"] for s in S]; k = [s["mean_degree"] for s in S]
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6))
    a.errorbar(N, pc, yerr=[pc - lo, hi - pc], color=BLUE, marker="o", capsize=3, lw=1.8)
    for i, (x, y, l) in enumerate(zip(N, pc, lf)):
        a.annotate("loop fraction %.2f" % l, (x, y), textcoords="offset points",
                   xytext=(6, 6) if i < len(N) - 1 else (-92, 10), fontsize=8, color=MUTED)
    a.set_xscale("log", base=2); a.set_xlabel("network size N (junctions)"); a.set_ylabel("$p_c$ (uniform removal)")
    a.set_title("15.a  Threshold by size", loc="left"); a.grid(alpha=0.25)
    b.plot(N, w, color=ORANGE, marker="o", lw=1.8)
    b.set_xscale("log", base=2); b.set_xlabel("network size N (junctions)")
    b.set_ylabel("10%-90% collapse window (removed fraction)")
    b.set_title("15.b  Width of the transition", loc="left"); b.grid(alpha=0.25)
    fig.text(0.5, -0.04, "Five synthetic sizes; D held at %.3f-%.3f and <k> at %.3f-%.3f, but loop fraction fell from "
             "%.2f to %.2f, so size and reticulation are not separated." % (min(D), max(D), min(k), max(k), lf.max(), lf.min()),
             ha="center", fontsize=9, color=MUTED, style="italic")
    save(fig, "Figure_15_size_sweep.png")


# ---------------------------------------------------------------- unchanged figures, new numbers
COPIES = {"Figure_03b_synthetic_network.png": "graph_synthetic.png",
          "Figure_03a_traced_network.png": "graph_real_Cis_ant.png",
          "Figure_05_fragmentation.png": "collapse_montage.png",
          "Figure_07_synthetic_grid.png": "calibration_grid.png",
          "Figure_08_collapse_criterion.png": "threshold_sensitivity.png",
          "Figure_13_sink_surface.png": "sink_surface.png"}


def copies():
    for new, old in COPIES.items():
        src = os.path.join(FIG, old)
        if os.path.exists(src):
            shutil.copy(src, out(new)); print("COPIED", old, "->", new)


FIGS = {"1": fig01, "2": fig02, "4": fig04, "6": fig06, "9": fig09, "10": fig10,
        "11": fig11, "12": fig12, "15": fig15, "copies": copies}

if __name__ == "__main__":
    pick = sys.argv[1:] or list(FIGS)
    for k in pick:
        print("== Figure", k)
        FIGS[k]()
    if not sys.argv[1:]:
        copies()
