# -*- coding: utf-8 -*-
r"""
make_flowchart_figures.py -- high-quality LANDSCAPE flowchart figures for Ch. III.

Rebuilds the schematic (non-data) figures as publication-quality PNGs that match
the house palette of the data figures (make_methodology_figures.py):

  fig01_pipeline.png          Overall software pipeline (snake, 10 stages)
  fig02_dataset.png           Structure of the original Matos dataset
  fig03_reconstruction.png    Node/Vein tables -> reconstructed graph
  fig07_hydraulic_flow.png    Source -> gradient -> Q = g dpsi -> sinks
  fig08b_cavitation_loop.png  Iterative cavitation-cascade loop (NEW, optional)

All are landscape. ASCII-only stdout (Windows cp1252 safety).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.collections import LineCollection

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures", "methodology")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "figure.dpi": 300,
    "savefig.dpi": 300,
})

# ---- house palette ----
INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#3B8EA5"; VEIN = "#7A4E2D"
GREEN = "#3F8F5B"; ARROW = "#8494A0"; PAGE = "#FFFFFF"

# fill / edge pairs per category
CAT = {
    "data":   ("#E7F0F3", BLUE),
    "net":    ("#EFE6DC", VEIN),
    "phys":   ("#FBE6DC", ACCENT),
    "stat":   ("#E4E9EC", INK),
    "out":    ("#E3F0E8", GREEN),
}


def card(ax, cx, cy, w, h, title, subs=None, cat="stat", title_size=12,
         sub_size=9.2, line_h=2.55):
    fill, edge = CAT[cat]
    box = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                         boxstyle="round,pad=0.015,rounding_size=0.12",
                         linewidth=1.8, edgecolor=edge, facecolor=fill,
                         mutation_aspect=1.0, zorder=3)
    ax.add_patch(box)
    subs = subs or []
    if subs:
        ty = cy + h * 0.26
    else:
        ty = cy
    ax.text(cx, ty, title, ha="center", va="center", color=INK,
            fontsize=title_size, fontweight="bold", zorder=4)
    if subs:
        n = len(subs)
        block_top = cy - h * 0.04 + (n - 1) * line_h / 2.0
        for i, line in enumerate(subs):
            ax.text(cx, block_top - i * line_h, line,
                    ha="center", va="center", color="#41505A",
                    fontsize=sub_size, zorder=4)


def arrow(ax, p0, p1, color=ARROW, lw=2.0, style="-|>", rad=0.0, ms=16):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms,
                        linewidth=lw, color=color, zorder=2,
                        connectionstyle=f"arc3,rad={rad}",
                        shrinkA=3, shrinkB=3, capstyle="round")
    ax.add_patch(a)


def newfig(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * h / w)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(PAGE)
    return fig, ax


def save(fig, name):
    path = os.path.join(FIG, name)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.15, facecolor=PAGE)
    plt.close(fig)
    print("SAVED:", os.path.relpath(path, ROOT))


# =====================================================================
# FIGURE 1 -- Overall software pipeline (10-stage snake)
# =====================================================================
def fig01_pipeline():
    fig, ax = newfig(15.5, 6.2)
    H = 100 * 6.2 / 15.5
    top = H * 0.70
    bot = H * 0.26
    w, h = 16.5, 15.5
    xs = np.linspace(11, 89, 5)

    top_stages = [
        ("Dryad dataset", ["Matos et al. (2024)", "122 leaf networks"], "data"),
        ("Load CSV tables", ["node + vein tables", "per species"], "data"),
        ("Graph reconstruction", ["NetworkX", "junctions -> nodes"], "net"),
        ("Characterize", ["real networks:", "D, <k>, GCC ..."], "net"),
        ("Synthetic generator", ["calibrated to", "cohort medians"], "net"),
    ]
    bot_stages = [  # drawn right -> left
        ("Hydraulic solver", ["Kirchhoff /", "Laplacian solve"], "phys"),
        ("Attack simulator", ["haustorial sink;", "random/deg/betw."], "phys"),
        ("Monte-Carlo", ["percolation;", "p_c estimation"], "phys"),
        ("Statistical analysis", ["logistic fit,", "partial corr."], "stat"),
        ("Outputs", ["CSV / JSON /", "figures"], "out"),
    ]

    # top row L->R
    for x, (t, s, c) in zip(xs, top_stages):
        card(ax, x, top, w, h, t, s, c, title_size=11.5, sub_size=8.6)
    # bottom row: place right->left so reading order snakes
    bx = xs[::-1]
    for x, (t, s, c) in zip(bx, bot_stages):
        card(ax, x, bot, w, h, t, s, c, title_size=11.5, sub_size=8.6)

    # arrows top L->R
    for i in range(4):
        arrow(ax, (xs[i] + w / 2, top), (xs[i + 1] - w / 2, top))
    # down connector on the right (stage 5 -> stage 6)
    arrow(ax, (xs[4], top - h / 2), (xs[4], bot + h / 2), color=ACCENT, lw=2.2)
    # arrows bottom R->L
    for i in range(4):
        arrow(ax, (bx[i] - w / 2, bot), (bx[i + 1] + w / 2, bot))

    ax.text(50, H * 0.99, "A single shared physics + percolation engine analyses "
            "real and synthetic networks identically",
            ha="center", va="top", fontsize=9.5, style="italic", color="#5A6A73")
    save(fig, "fig01_pipeline.png")


# =====================================================================
# FIGURE 2 -- Structure of the original dataset
# =====================================================================
def fig02_dataset():
    fig, ax = newfig(14.5, 7.4)
    H = 100 * 7.4 / 14.5
    top = H * 0.86
    mid = H * 0.50
    bot = H * 0.12

    card(ax, 50, top, 30, 12, "Dryad dataset",
         ["Matos et al. (2024) -- doi:10.5061/dryad.1g1jwsv36"], "data",
         title_size=13, sub_size=9)

    cols = [22, 50, 78]
    kids = [
        ("<leaf>_nodes.csv", ["node_ID", "X, Y coordinates",
                              "Calibration", "Degree"]),
        ("<leaf>_veins.csv", ["EndNodes_1, EndNodes_2", "Width (radius)",
                              "Length", "Type"]),
        ("metadata.csv", ["spp_code", "resolution", "quality flag",
                          "hand_traced"]),
    ]
    kw, kh = 26, 20
    for x, (t, s, ) in zip(cols, [(k[0], k[1]) for k in kids]):
        card(ax, x, mid, kw, kh, t, s, "net", title_size=11.5, sub_size=8.8)
        arrow(ax, (50, top - 6), (x, mid + kh / 2), rad=0.0)
        arrow(ax, (x, mid - kh / 2), (50, bot + 6))

    card(ax, 50, bot, 44, 11, "Python framework  ->  Graph representation",
         None, "out", title_size=12)
    save(fig, "fig02_dataset.png")


# =====================================================================
# FIGURE 3 -- Graph reconstruction
# =====================================================================
def fig03_reconstruction():
    fig, ax = newfig(14.5, 6.0)
    H = 100 * 6.0 / 14.5
    cy = H * 0.52

    card(ax, 16, cy + 11, 24, 13, "Node Table",
         ["junction coordinates (X, Y)"], "data", title_size=12, sub_size=8.8)
    card(ax, 16, cy - 11, 24, 13, "Vein Table",
         ["connectivity + radius, length"], "net", title_size=12, sub_size=8.8)

    arrow(ax, (30, cy + 11), (39, cy + 2), color=ARROW, lw=2.2)
    arrow(ax, (30, cy - 11), (39, cy - 2), color=ARROW, lw=2.2)
    # big transform arrow
    arrow(ax, (40, cy), (52, cy), color=INK, lw=3.2, ms=26)
    ax.text(46, cy + 5.2, "reconstruct", ha="center", fontsize=9,
            style="italic", color="#5A6A73")

    # mini reconstructed graph (with a loop / areole)
    nodes = {
        "S": (60, cy + 9),
        "a": (70, cy + 14), "b": (71, cy - 1), "c": (82, cy + 9),
        "d": (84, cy - 6), "e": (92, cy + 2), "f": (77, cy - 13),
    }
    edges = [("S", "a", 3.4), ("S", "b", 3.4), ("a", "c", 2.3),
             ("b", "c", 2.3), ("c", "e", 1.7), ("b", "d", 2.0),
             ("d", "e", 1.7), ("d", "f", 1.4)]
    segs = [[nodes[u], nodes[v]] for u, v, _ in edges]
    lws = [lw for _, _, lw in edges]
    ax.add_collection(LineCollection(segs, colors=VEIN, linewidths=lws,
                                     capstyle="round", zorder=3))
    for k, (x, y) in nodes.items():
        if k == "S":
            ax.add_patch(Circle((x, y), 1.9, color=ACCENT, zorder=5))
        else:
            ax.add_patch(Circle((x, y), 1.15, color=INK, zorder=5))
    ax.text(nodes["S"][0] - 1, nodes["S"][1] + 4.2, "Source  (psi = 0)",
            ha="center", fontsize=9.2, fontweight="bold", color=ACCENT)
    # annotate the loop
    lx = (nodes["b"][0] + nodes["c"][0] + nodes["d"][0] + nodes["e"][0]) / 4
    ly = (nodes["b"][1] + nodes["c"][1] + nodes["d"][1] + nodes["e"][1]) / 4
    ax.text(lx + 1, ly, "reticulate\nloop (areole)", ha="center", va="center",
            fontsize=7.6, style="italic", color=BLUE)
    ax.text(78, cy - 19, "edge width proportional to vein radius",
            ha="center", fontsize=8, style="italic", color="#5A6A73")
    save(fig, "fig03_reconstruction.png")


# =====================================================================
# FIGURE 7 -- Hydraulic flow model (row of 4)
# =====================================================================
def fig07_hydraulic():
    fig, ax = newfig(15.5, 4.6)
    H = 100 * 4.6 / 15.5
    cy = H * 0.52
    xs = [13, 37.5, 62, 87]
    w, h = 20, 17

    card(ax, xs[0], cy, w, h, "Source", ["widest basal vein",
         "(petiole proxy)", "psi = 0"], "phys", title_size=12, sub_size=9)
    card(ax, xs[1], cy, w, h, "Pressure gradient", ["across the",
         "vascular network", "(delta-psi)"], "data", title_size=12, sub_size=9)
    # equation box drawn manually for mathtext
    fill, edge = CAT["net"]
    ax.add_patch(FancyBboxPatch((xs[2] - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.015,rounding_size=0.12", linewidth=1.8,
                 edgecolor=edge, facecolor=fill, zorder=3))
    ax.text(xs[2], cy + h * 0.24, "Flow through veins", ha="center",
            va="center", fontsize=12, fontweight="bold", color=INK, zorder=4)
    ax.text(xs[2], cy - h * 0.02, r"$Q = g\,\Delta\psi$", ha="center",
            va="center", fontsize=15, color=INK, zorder=4)
    ax.text(xs[2], cy - h * 0.27, r"$g \;\propto\; r^{4}/L$", ha="center",
            va="center", fontsize=13, color=ACCENT, zorder=4)
    card(ax, xs[3], cy, w, h, "Terminal veins", ["hydraulic sinks",
         r"psi = psi(leaf)"], "out", title_size=12, sub_size=9)

    for i in range(3):
        arrow(ax, (xs[i] + w / 2, cy), (xs[i + 1] - w / 2, cy), lw=2.3, ms=18)
    ax.text(50, H * 0.985, "Steady-state flow solved with Kirchhoff's current "
            "law (conservation at every junction)",
            ha="center", va="top", fontsize=9, style="italic", color="#5A6A73")
    save(fig, "fig07_hydraulic_flow.png")


# =====================================================================
# FIGURE 8b (NEW) -- Iterative cavitation-cascade loop
# =====================================================================
def fig08b_cavitation_loop():
    fig, ax = newfig(15.0, 6.6)
    H = 100 * 6.6 / 15.0
    cy = H * 0.56
    w, h = 19, 15
    xs = [13, 37, 61, 85]

    card(ax, xs[0], cy, w, h, "Solve hydraulics", ["water potentials",
         "at every node"], "phys", title_size=11.5, sub_size=8.8)
    card(ax, xs[1], cy, w, h, "Identify failures", ["tension >",
         "cavitation threshold"], "phys", title_size=11.5, sub_size=8.8)
    card(ax, xs[2], cy, w, h, "Remove vessels", ["embolised veins",
         "leave the network"], "net", title_size=11.5, sub_size=8.8)
    card(ax, xs[3], cy, w, h, "Recompute GCC", ["measure remaining",
         "connectivity"], "stat", title_size=11.5, sub_size=8.8)

    for i in range(3):
        arrow(ax, (xs[i] + w / 2, cy), (xs[i + 1] - w / 2, cy), lw=2.2)

    # feedback loop arrow from GCC back to Solve hydraulics (curved under)
    arrow(ax, (xs[3], cy - h / 2), (xs[0], cy - h / 2), color=ACCENT, lw=2.3,
          rad=-0.32, ms=18)
    ax.text(49, cy - h / 2 - H * 0.20, "iterate until target disruption reached",
            ha="center", fontsize=9, style="italic", color=ACCENT)

    # exit arrow
    card(ax, xs[3], cy + h * 0.02 + H * 0.30, w * 0.92, h * 0.62,
         "Collapse curve", ["GCC vs. removal -> p_c"], "out",
         title_size=10.5, sub_size=8.4)
    arrow(ax, (xs[3], cy + h / 2), (xs[3], cy + h * 0.02 + H * 0.30 - h * 0.31),
          color=GREEN, lw=2.2)

    ax.text(50, H * 0.99, "Hydraulic failure emerges from the flow-topology "
            "feedback rather than being imposed", ha="center", va="top",
            fontsize=9, style="italic", color="#5A6A73")
    save(fig, "fig08b_cavitation_loop.png")


if __name__ == "__main__":
    fig01_pipeline()
    fig02_dataset()
    fig03_reconstruction()
    fig07_hydraulic()
    fig08b_cavitation_loop()
    print("DONE")
