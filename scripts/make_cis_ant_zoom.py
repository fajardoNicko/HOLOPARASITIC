# -*- coding: utf-8 -*-
r"""make_cis_ant_zoom.py -- high-resolution ZOOMED view of the Cis_ant "suggested"
(more-reticulate) network for the methodology figure, so it stays crisp when enlarged.

Renders a sub-window centred on the densest added-reticulation region at high DPI.
Outputs (figures/methodology/):
  fig_realsuggested_Cis_ant_zoom.png       -- suggested only, zoomed (what was asked)
  fig_realsuggested_Cis_ant_zoom_pair.png  -- current | suggested, same window (bonus)

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_cis_ant_zoom.py
"""
import os, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from holoparasitic import realleaf
from scripts.make_real_suggested import add_loops, TARGET_K

FIG = os.path.join(ROOT, "figures", "methodology")
LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
SPP = "Cis_ant"
INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#2F7FA8"; VEIN = "#7A4E2D"

ZOOM_FRAC = 0.26     # window side as a fraction of the larger bbox dimension
DPI = 500


def load():
    d = os.path.join(LEAFDIR, SPP)
    nf = glob.glob(os.path.join(d, "*_nodes.csv"))[0]
    vf = glob.glob(os.path.join(d, "*_veins.csv"))[0]
    return realleaf.load_matos(nf, vf, name=SPP)


def zoom_window(G2):
    """Centre the zoom on the median position of the ADDED loops (the reticulation
    we want to showcase); fall back to the node centroid."""
    pos = {n: G2.nodes[n]["pos"] for n in G2.nodes}
    P = np.array(list(pos.values()), float)
    xr = (P[:, 0].min(), P[:, 0].max()); yr = (P[:, 1].min(), P[:, 1].max())
    side = ZOOM_FRAC * max(xr[1] - xr[0], yr[1] - yr[0])
    mids = [((pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2)
            for u, v, d in G2.edges(data=True) if d.get("kind") == "added_loop"]
    C = np.median(np.array(mids), axis=0) if mids else P.mean(axis=0)
    cx = float(np.clip(C[0], xr[0] + side / 2, xr[1] - side / 2))
    cy = float(np.clip(C[1], yr[0] + side / 2, yr[1] - side / 2))
    return (cx - side / 2, cx + side / 2), (cy - side / 2, cy + side / 2)


def draw(ax, G, xlim, ylim, title, show_added):
    pos = {n: G.nodes[n]["pos"] for n in G.nodes}
    base, add, brad = [], [], []
    for u, v, d in G.edges(data=True):
        # keep only segments touching the window (speeds LineCollection on big leaves)
        (x0, y0), (x1, y1) = pos[u], pos[v]
        if max(x0, x1) < xlim[0] or min(x0, x1) > xlim[1] or \
           max(y0, y1) < ylim[0] or min(y0, y1) > ylim[1]:
            continue
        seg = [pos[u], pos[v]]
        if d.get("kind") == "added_loop":
            add.append(seg)
        else:
            base.append(seg); brad.append(d.get("radius", 0.01))
    brad = np.array(brad, float)
    rmax = brad.max() if brad.size else 1.0
    lw = 0.5 + 2.2 * (brad / rmax) ** 0.5
    ax.add_collection(LineCollection(base, colors=VEIN, linewidths=lw,
                                     capstyle="round", zorder=2))
    if show_added and add:
        ax.add_collection(LineCollection(add, colors=BLUE, linewidths=1.1,
                                         capstyle="round", zorder=3, alpha=0.9))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=6)
    return len(add)


def main():
    os.makedirs(FIG, exist_ok=True)
    G = load()
    k0 = 2 * G.number_of_edges() / G.number_of_nodes()
    G2, nadd = add_loops(G, TARGET_K)
    k1 = 2 * G2.number_of_edges() / G2.number_of_nodes()
    xlim, ylim = zoom_window(G2)
    print("%s N=%d  <k> %.2f->%.2f  (+%d loops total)  window x%s y%s"
          % (SPP, G.number_of_nodes(), k0, k1, nadd,
             tuple(round(v, 2) for v in xlim), tuple(round(v, 2) for v in ylim)))

    # ---- 1) suggested only, zoomed ----
    fig, ax = plt.subplots(figsize=(8, 8)); fig.patch.set_facecolor("white")
    nshown = draw(ax, G2, xlim, ylim,
                  "Cis_ant \u2014 suggested (more reticulate), zoomed", True)
    ax.text(0.5, -0.02, r"$\langle k \rangle$ = %.2f    added areole loops in blue "
            "(%d in view)" % (k1, nshown), transform=ax.transAxes, ha="center",
            va="top", fontsize=10.5, color=INK)
    p = os.path.join(FIG, "fig_realsuggested_Cis_ant_zoom.png")
    fig.savefig(p, dpi=DPI, bbox_inches="tight", pad_inches=0.12, facecolor="white")
    plt.close(fig); print("SAVED:", os.path.relpath(p, ROOT))

    # ---- 2) current | suggested pair, same window ----
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(15, 7.7)); fig.patch.set_facecolor("white")
    draw(a0, G, xlim, ylim, "Current (real leaf), zoomed", False)
    a0.text(0.5, -0.02, r"$\langle k \rangle$ = %.2f" % k0, transform=a0.transAxes,
            ha="center", va="top", fontsize=10.5, color=INK)
    nshown = draw(a1, G2, xlim, ylim, "Suggested (more reticulate), zoomed", True)
    a1.text(0.5, -0.02, r"$\langle k \rangle$ = %.2f    +%d loops in view" % (k1, nshown),
            transform=a1.transAxes, ha="center", va="top", fontsize=10.5, color=BLUE)
    fig.suptitle("Cis_ant \u2014 same lamina window, before and after reticulation "
                 "enhancement", fontsize=13, color=INK, y=0.99)
    p2 = os.path.join(FIG, "fig_realsuggested_Cis_ant_zoom_pair.png")
    fig.savefig(p2, dpi=350, bbox_inches="tight", pad_inches=0.15, facecolor="white")
    plt.close(fig); print("SAVED:", os.path.relpath(p2, ROOT))


if __name__ == "__main__":
    main()
