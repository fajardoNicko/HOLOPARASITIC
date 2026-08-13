# -*- coding: utf-8 -*-
r"""
make_real_suggested.py -- per-species "suggested more-reticulate leaf", built from
EACH SPECIES' OWN real Matos venation network (not a generic cohort network).

For each species:
  * CURRENT  = its real leaf as loaded (realleaf.load_matos)
  * SUGGESTED = that SAME real leaf with extra loops added to IT: the shortest
    Delaunay areole-closures on its own node positions, up to a target mean degree
    (the cohort 90th percentile). So the suggestion is recalibrated per leaf -- a
    sparse leaf gains many loops, an already-reticulate one gains few.
Both panels are annotated with MEASURED random-attack p_c (rho_max=0.6), so the
gain is apples-to-apples on the species' own network.

Usage:  python scripts/make_real_suggested.py Met_dav Chl_spi Cam_sin Ane_cal Cis_ant
Output: figures/methodology/fig_realsuggested_<spp>.png  (resumable: skips existing)
ASCII-only stdout.
"""
import os
import sys
import csv
import glob
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import networkx as nx
from scipy.spatial import Delaunay
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

import config
from holoparasitic import realleaf, percolation

FIG = os.path.join(ROOT, "figures", "methodology")
LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#2F7FA8"; VEIN = "#7A4E2D"
TARGET_K = 2.811   # cohort 90th-percentile mean degree (observed reticulation ceiling)
PP = config.PercolationParams(mode="random", n_densities=40, n_trials=1600)


def cohort_D():
    D = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "data", "cohort.csv"), newline="")):
        try:
            D[r["name"]] = float(r["D"])
        except ValueError:
            pass
    return D


def add_loops(G, target_k):
    """Close the leaf's own areoles: add the shortest Delaunay non-edges on the
    real node positions, tagged kind='added_loop', up to target mean degree."""
    nodes = list(G.nodes)
    pos = np.array([G.nodes[n]["pos"] for n in nodes], float)
    tri = Delaunay(pos)
    seen = set()
    cand = []
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
    cand.sort(key=lambda t: t[0])
    G2 = G.copy()
    need = int(target_k * G2.number_of_nodes() / 2) - G2.number_of_edges()
    added = 0
    for d, na, nb in cand:
        if added >= need:
            break
        ra = min((G2[na][x].get("radius", 0.01) for x in G2.neighbors(na)),
                 default=0.01)
        rb = min((G2[nb][x].get("radius", 0.01) for x in G2.neighbors(nb)),
                 default=0.01)
        G2.add_edge(na, nb, radius=min(ra, rb), length=d, kind="added_loop")
        added += 1
    return G2, added


def measure_pc(G):
    r = percolation.find_pc(G, PP, rho_max=0.6)
    return float(r["p_c"])


def draw(ax, G, title, kk, D, pc, added_only=False):
    pos = {n: G.nodes[n]["pos"] for n in G.nodes}
    base, add, brad = [], [], []
    for u, v, d in G.edges(data=True):
        seg = [pos[u], pos[v]]
        if d.get("kind") == "added_loop":
            add.append(seg)
        else:
            base.append(seg); brad.append(d.get("radius", 0.01))
    brad = np.array(brad, float)
    rmax = brad.max() if brad.size else 1.0
    lw = 0.05 + 0.9 * (brad / rmax) ** 0.5
    ax.add_collection(LineCollection(base, colors=VEIN, linewidths=lw,
                                     capstyle="round", zorder=2))
    if add:
        ax.add_collection(LineCollection(add, colors=BLUE, linewidths=0.35,
                                         capstyle="round", zorder=3, alpha=0.8))
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs), max(xs)); ax.set_ylim(min(ys), max(ys))
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=6)
    sub = (r"$\langle k \rangle$ = %.2f    D = %.2f    measured $p_c$ = %.2f"
           % (kk, D, pc))
    ax.text(0.5, -0.03, sub, transform=ax.transAxes, ha="center", va="top",
            fontsize=10.5, color=INK)
    if add:
        ax.text(0.5, -0.08, "+%d added loop veins (blue)" % len(add),
                transform=ax.transAxes, ha="center", va="top", fontsize=9,
                color=BLUE, style="italic")


def one(spp, Dmap):
    out = os.path.join(FIG, "fig_realsuggested_%s.png" % spp)
    if os.path.exists(out):
        print("skip (exists):", spp); return
    t0 = time.time()
    d = os.path.join(LEAFDIR, spp)
    n = glob.glob(d + "/*_nodes.csv")[0]; v = glob.glob(d + "/*_veins.csv")[0]
    G = realleaf.load_matos(n, v, name=spp)
    k0 = 2 * G.number_of_edges() / G.number_of_nodes()
    D = Dmap.get(spp, float("nan"))
    pc0 = measure_pc(G)
    G2, nadd = add_loops(G, TARGET_K)
    k1 = 2 * G2.number_of_edges() / G2.number_of_nodes()
    pc1 = measure_pc(G2)
    print("  %s N=%d  <k> %.2f->%.2f (+%d loops)  pc %.3f->%.3f  (%.0fs)"
          % (spp, G.number_of_nodes(), k0, k1, nadd, pc0, pc1, time.time() - t0))

    fig, (a0, a1) = plt.subplots(1, 2, figsize=(15, 7.6))
    fig.patch.set_facecolor("white")
    draw(a0, G, "Current (real leaf)", k0, D, pc0)
    draw(a1, G2, "Suggested (its own leaf, more reticulate)", k1, D, pc1)
    fig.suptitle("%s  —  loops added to ITS OWN venation, measured $p_c$ "
                 "%.2f → %.2f  (+%.2f)" % (spp, pc0, pc1, pc1 - pc0),
                 fontsize=12.5, color=INK, y=0.99)
    fig.text(0.5, 0.015, "Current = the species' real Matos leaf; Suggested = that "
             "same leaf with the shortest areole-closures added to it "
             "(blue), up to the cohort reticulation ceiling.",
             ha="center", fontsize=8.6, style="italic", color="#5A6A73")
    fig.savefig(out, dpi=220, bbox_inches="tight", pad_inches=0.2, facecolor="white")
    plt.close(fig)
    print("  SAVED:", os.path.relpath(out, ROOT))


def main():
    spp_list = sys.argv[1:] or ["Met_dav", "Chl_spi", "Cam_sin", "Ane_cal", "Cis_ant"]
    Dmap = cohort_D()
    for spp in spp_list:
        try:
            one(spp, Dmap)
        except Exception as e:
            print("  FAILED %s: %s" % (spp, e))


if __name__ == "__main__":
    main()
