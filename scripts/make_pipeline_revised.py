# -*- coding: utf-8 -*-
r"""
make_pipeline_revised.py -- CORRECTED overall-pipeline flowchart matching the
current study (real-leaf reticulation cohort + calibrated sink), in the same
house style as make_flowchart_figures.py.

Changes vs the old fig01_pipeline:
  + adds the RETICULATION ENHANCEMENT step (the headline experiment)
  + adds the HAUSTORIAL SINK model as its own step (2nd lens)
  + corrects attack modes to random & degree-targeted (betweenness = subset only)
  - demotes the synthetic generator to a calibration note in the caption

Output: figures/methodology/fig01_pipeline_revised.png   (landscape, 300 dpi)
ASCII-only stdout.
    C:\laragon\bin\python\python-3.13\python.exe scripts\make_pipeline_revised.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures", "methodology")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "figure.dpi": 300, "savefig.dpi": 300,
})

# ---- house palette (identical to make_flowchart_figures.py) ----
INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#3B8EA5"; VEIN = "#7A4E2D"
GREEN = "#3F8F5B"; ARROW = "#8494A0"; PAGE = "#FFFFFF"
CAT = {
    "data": ("#E7F0F3", BLUE),
    "net":  ("#EFE6DC", VEIN),
    "head": ("#F6E7C1", "#C98A1E"),   # the headline step -- amber highlight
    "phys": ("#FBE6DC", ACCENT),
    "stat": ("#E4E9EC", INK),
    "out":  ("#E3F0E8", GREEN),
}


def card(ax, cx, cy, w, h, title, subs=None, cat="stat", title_size=11.0,
         sub_size=8.6, line_h=2.7):
    fill, edge = CAT[cat]
    lw = 2.6 if cat == "head" else 1.8
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.015,rounding_size=0.12",
        linewidth=lw, edgecolor=edge, facecolor=fill, zorder=3))
    subs = subs or []
    ty = cy + h * 0.27 if subs else cy
    ax.text(cx, ty, title, ha="center", va="center", color=INK,
            fontsize=title_size, fontweight="bold", zorder=4)
    if subs:
        n = len(subs)
        block_top = cy - h * 0.05 + (n - 1) * line_h / 2.0
        for i, line in enumerate(subs):
            ax.text(cx, block_top - i * line_h, line, ha="center", va="center",
                    color="#41505A", fontsize=sub_size, zorder=4)


def arrow(ax, p0, p1, color=ARROW, lw=2.0, style="-|>", rad=0.0, ms=16):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle=style, mutation_scale=ms, linewidth=lw, color=color,
        zorder=2, connectionstyle=f"arc3,rad={rad}", shrinkA=3, shrinkB=3,
        capstyle="round"))


def main():
    W, Hin = 16.0, 7.3
    fig, ax = plt.subplots(figsize=(W, Hin))
    H = 100 * Hin / W
    ax.set_xlim(0, 100); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor(PAGE)

    top = H * 0.66
    bot = H * 0.30
    w, h = 17.3, 13.5
    xs = np.linspace(11.5, 88.5, 5)          # 5 top positions

    top_stages = [
        ("Real leaf dataset", ["Matos et al. (2024)", "120 leaf networks"], "data"),
        ("Graph reconstruction", ["NetworkX;", "junctions -> nodes"], "net"),
        ("Characterize networks", ["D, <k>, reticulation,", "conductance, GCC"], "net"),
        ("Reticulation enhancement", ["add shortest Delaunay", "loops -> 'suggested'"], "head"),
        ("Attack simulation", ["random &", "degree-targeted"], "phys"),
    ]
    # 4 bottom positions, evenly spaced; drawn RIGHT -> LEFT so reading snakes
    bx = np.linspace(19.5, 88.5, 4)[::-1]     # [88.5, 65.5, 42.5, 19.5]
    bot_stages = [
        ("Monte-Carlo percolation", ["threshold p_c;", "current vs suggested"], "phys"),
        ("Haustorial sink model", ["calibrated K_h;", "water-potential solve"], "phys"),
        ("Statistical analysis", ["correlations,", "sensitivity, validation"], "stat"),
        ("Outputs", ["CSV / JSON /", "figures"], "out"),
    ]

    for x, (t, s, c) in zip(xs, top_stages):
        card(ax, x, top, w, h, t, s, c)
    for x, (t, s, c) in zip(bx, bot_stages):
        card(ax, x, bot, w, h, t, s, c)

    # arrows: top L->R
    for i in range(4):
        arrow(ax, (xs[i] + w / 2, top), (xs[i + 1] - w / 2, top))
    # down connector on the right (Attack -> Monte-Carlo)
    arrow(ax, (xs[4], top - h / 2), (bx[0], bot + h / 2), color=ACCENT, lw=2.3)
    # arrows: bottom R->L
    for i in range(3):
        arrow(ax, (bx[i] - w / 2, bot), (bx[i + 1] + w / 2, bot))

    # small tag marking the headline step
    ax.text(xs[3], top + h / 2 + H * 0.035, "HEADLINE", ha="center", va="bottom",
            fontsize=8.2, fontweight="bold", color="#C98A1E")

    ax.text(50, H * 0.99,
            "Two decoupled lenses share one engine: structural percolation "
            "(steps 5-6) and the hydraulic sink (step 7).",
            ha="center", va="top", fontsize=9.2, style="italic", color="#5A6A73")
    ax.text(50, H * 0.015,
            "Synthetic grids (not shown) calibrate the p_c-vs-architecture surface "
            "and the reticulation ceiling <k> = 2.811 used in step 4.",
            ha="center", va="bottom", fontsize=8.4, style="italic", color="#7A8894")

    path = os.path.join(FIG, "fig01_pipeline_revised.png")
    fig.savefig(path, bbox_inches="tight", pad_inches=0.16, facecolor=PAGE)
    plt.close(fig)
    print("SAVED:", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
