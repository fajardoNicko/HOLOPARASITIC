# -*- coding: utf-8 -*-
r"""
make_suggested_network.py -- illustrate the robustness PRESCRIPTION for a species:
its current (sparse) architecture vs a more-reticulate version at the observed
robustness ceiling, with the added loops highlighted and predicted p_c annotated.

HONEST SCOPE. The generator is calibrated to cohort medians, not to one species'
individual leaf, and is D-capped ~1.81. So this is an ILLUSTRATION of the
direction the ceiling analysis prescribes (more closed loops -> higher p_c), not
a literal designed "ideal leaf" for the species.

Output: figures/methodology/fig_suggested_<spp>.png  (landscape pair)
ASCII-only stdout.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

import config
from holoparasitic import network, fractal, calibrate as cal

FIG = os.path.join(ROOT, "figures", "methodology")
INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#3B8EA5"; VEIN = "#7A4E2D"
# fitted causal surface (run_robustness_ceiling.py): p_c = b0 + bk*<k> + bD*D
B0, BK, BD = -0.0907, 0.1202, 0.0287

SPP = sys.argv[1] if len(sys.argv) > 1 else "Chl_spi"
K_CURRENT = float(sys.argv[2]) if len(sys.argv) > 2 else 2.148
K_CEILING = 2.811   # cohort 90th-percentile mean degree (observed reticulation ceiling)
GEN = 10


def build(k):
    G = network.generate(cal.calibrated_base(generations=GEN, mean_degree=k))
    E = G.number_of_edges(); N = G.number_of_nodes()
    kk = 2 * E / N
    D = fractal.fractal_dimension(G)
    pc = B0 + BK * kk + BD * D
    return G, kk, D, pc


def draw(ax, G, title, kk, D, pc):
    pos = {n: G.nodes[n]["pos"] for n in G.nodes}
    axial, anas = [], []
    arad = []
    for u, v, d in G.edges(data=True):
        seg = [pos[u], pos[v]]
        if d.get("kind") == "anastomosis":
            anas.append(seg)
        else:
            axial.append(seg); arad.append(d.get("radius", 0.01))
    arad = np.array(arad, float)
    rmax = arad.max() if arad.size else 1.0
    lw = 0.2 + 2.2 * (arad / rmax) ** 0.5
    ax.add_collection(LineCollection(axial, colors=VEIN, linewidths=lw,
                                     capstyle="round", zorder=2))
    # the ADDED loops, highlighted
    ax.add_collection(LineCollection(anas, colors=BLUE, linewidths=1.3,
                                     capstyle="round", zorder=3, alpha=0.9))
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs), max(xs)); ax.set_ylim(min(ys), max(ys))
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=6)
    ax.text(0.5, -0.04, r"$\langle k \rangle$ = %.2f    D = %.2f    "
            "predicted $p_c$ = %.2f" % (kk, D, pc),
            transform=ax.transAxes, ha="center", va="top", fontsize=10.5,
            color=INK)
    ax.text(0.5, -0.10, "%d loop edges" % len(anas), transform=ax.transAxes,
            ha="center", va="top", fontsize=9, color=BLUE, style="italic")


def main():
    Gc, kc, Dc, pcc = build(K_CURRENT)
    Gs, ks, Ds, pcs = build(K_CEILING)
    print("current : <k>=%.2f D=%.2f pc=%.3f" % (kc, Dc, pcc))
    print("suggested: <k>=%.2f D=%.2f pc=%.3f  (+%.3f)" % (ks, Ds, pcs, pcs - pcc))

    fig, (a0, a1) = plt.subplots(1, 2, figsize=(15, 7.2))
    fig.patch.set_facecolor("white")
    draw(a0, Gc, "Current architecture", kc, Dc, pcc)
    draw(a1, Gs, "Suggested: more reticulate", ks, Ds, pcs)
    fig.suptitle("%s  —  robustness prescription: add reticulation (blue = "
                 "added loops), predicted $p_c$ %.2f → %.2f  (+%.2f)"
                 % (SPP, pcc, pcs, pcs - pcc), fontsize=12.5, color=INK, y=0.99)
    fig.text(0.5, 0.02, "Illustrative, cohort-calibrated synthetic networks (not a "
             "literal per-species leaf); the prescription is the direction, "
             "bounded by construction-cost trade-offs.", ha="center",
             fontsize=8.6, style="italic", color="#5A6A73")
    path = os.path.join(FIG, "fig_suggested_%s.png" % SPP)
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.2,
                facecolor="white")
    plt.close(fig)
    print("SAVED:", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
