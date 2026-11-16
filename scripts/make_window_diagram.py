# -*- coding: utf-8 -*-
r"""
make_window_diagram.py -- where to cut the one imaging window from each local
leaf (protocol Step 5). Schematic, not to scale.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_window_diagram.py
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "figures", "revised", "local_window_diagram.png")
LEAF, VEIN, CUT, INK, MUTED, BLUE = "#8fc46a", "#4f7d36", "#c1121f", "#20303A", "#5A6A73", "#2F7FA8"


def ovate(n=200):
    t = np.linspace(0, np.pi, n)
    x = np.sin(t) * (1 - 0.25 * np.cos(t))         # widest a little below the middle
    y = -np.cos(t) * 1.6
    return np.r_[x, -x[::-1]], np.r_[y, y[::-1]]


def panel_simple(ax):
    x, y = ovate()
    blade = ax.fill(x, y, color=LEAF, ec=VEIN, lw=1.5)[0]
    ax.plot([0, 0], [-1.85, 1.6], color=VEIN, lw=3)                     # petiole + midrib
    for yy in np.linspace(-1.1, 1.1, 7):
        for s in (1, -1):
            ln, = ax.plot([0, s * 0.62, s * 0.78], [yy, yy + 0.32, yy + 0.52], color=VEIN, lw=1.2)
            ln.set_clip_path(blade)
    ax.add_patch(Rectangle((0.24, -0.05), 0.3, 0.3, fill=False, ec=CUT, lw=2.4))
    ax.annotate("cut ONE square here\n(about 12 × 12 mm)", (0.54, 0.22), xytext=(1.05, 0.9), color=CUT,
                fontsize=9.5, fontweight="bold", arrowprops=dict(arrowstyle="->", color=CUT))
    ax.annotate("not on the midrib", (0, -0.6), xytext=(-1.75, -1.05), fontsize=8.5, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED))
    ax.annotate("not at the edge", (-0.9, 0.3), xytext=(-1.85, 0.95), fontsize=8.5, color=MUTED,
                arrowprops=dict(arrowstyle="->", color=MUTED))
    ax.text(0, -2.25, "talisay, guyabano, gumamela", ha="center", fontsize=9.5, color=INK)
    ax.set_title("A  Simple leaf", loc="left")


def panel_okra(ax):
    ang = np.radians([90, 140, 40, 195, -15])
    for a in ang:
        L = 1.55 if a == np.radians(90) else 1.15
        tip = np.array([np.cos(a), np.sin(a)]) * L
        perp = np.array([-np.sin(a), np.cos(a)]) * 0.33
        ax.add_patch(Polygon([(0, -0.15), tuple(tip * 0.45 + perp), tuple(tip), tuple(tip * 0.45 - perp)],
                             closed=True, fc=LEAF, ec=VEIN, lw=1.4))
        ax.plot([0, tip[0] * 0.95], [-0.1, tip[1] * 0.95], color=VEIN, lw=2.2)
    ax.plot([0, 0], [-0.15, -1.0], color=VEIN, lw=3)
    ax.add_patch(Rectangle((0.07, 0.55), 0.24, 0.24, fill=False, ec=CUT, lw=2.4))
    ax.annotate("in the middle lobe,\nbeside (not on) the\nmain vein", (0.31, 0.7), xytext=(0.75, 1.3), color=CUT,
                fontsize=9.5, fontweight="bold", arrowprops=dict(arrowstyle="->", color=CUT))
    ax.text(0, -1.35, "okra (wear gloves)", ha="center", fontsize=9.5, color=INK)
    ax.set_title("B  Lobed leaf", loc="left")


def pinna_halfwidth(y, y0=-1.7, y1=1.8, w=0.42):
    t = np.clip((y - y0) / (y1 - y0), 0, 1)
    return w * np.sin(np.pi * t) ** 0.3 * (1 - 0.35 * t)


def panel_fern(ax):
    """One sword-fern pinna: free, forked side veins that join only at the midvein, so the window must
    contain the midvein -- a strip across the whole pinna, never a square beside the midvein."""
    yy = np.linspace(-1.7, 1.8, 200)
    hw = pinna_halfwidth(yy)
    blade = ax.fill(np.r_[hw, -hw[::-1]], np.r_[yy, yy[::-1]], color=LEAF, ec=VEIN, lw=1.5)[0]
    ax.plot([0, 0], [-2.0, 1.7], color=VEIN, lw=2.6)                      # stalk + midvein
    for y0 in np.linspace(-1.35, 1.45, 14):
        for s in (1, -1):
            w = pinna_halfwidth(y0 + 0.2)
            fork = (s * 0.32 * w / 0.42, y0 + 0.1)
            for end in ((s * w * 0.86, y0 + 0.3), (s * w * 0.86, y0 + 0.12)):
                ln, = ax.plot([0, fork[0], end[0]], [y0, fork[1], end[1]], color=VEIN, lw=0.9)
                ln.set_clip_path(blade)
                ax.plot(*end, "o", ms=1.8, color=VEIN)                    # free vein end (hydathode)
    wmid = pinna_halfwidth(0.0)
    ax.add_patch(Rectangle((-wmid - 0.08, -0.32), 2 * wmid + 0.16, 0.64, fill=False, ec=CUT, lw=2.4))
    ax.annotate("cut a strip across the\nWHOLE pinna, with the\nmidvein inside it", (wmid + 0.08, 0.0),
                xytext=(0.75, -0.75), color=CUT, fontsize=9.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=CUT))
    bx, by, bs = 0.08, 0.8, 0.26                                            # the wrong window
    ax.add_patch(Rectangle((bx, by), bs, bs, fill=False, ec=MUTED, lw=1.4, ls="--"))
    ax.plot([bx, bx + bs], [by, by + bs], color=MUTED, lw=1.2)
    ax.plot([bx, bx + bs], [by + bs, by], color=MUTED, lw=1.2)
    ax.annotate("not beside the midvein:\nthe veins there fall\napart into pieces", (bx + bs, by + bs / 2),
                xytext=(0.75, 1.15), fontsize=8.5, color=MUTED, arrowprops=dict(arrowstyle="->", color=MUTED))
    ax.text(0.45, -2.3, "Nephrolepis: one sterile pinna\nfrom the middle of the frond", ha="center", fontsize=9.5,
            color=INK)
    ax.set_title("C  Fern pinna", loc="left")


def panel_slide(ax):
    ax.add_patch(FancyBboxPatch((-1.9, -0.75), 3.8, 1.5, boxstyle="round,pad=0.02", fc="#e9f3fb", ec="#9fb6d6", lw=1.5))
    ax.add_patch(Rectangle((-0.6, -0.6), 1.2, 1.2, fc=LEAF, ec=VEIN, lw=1.2))
    ax.add_patch(Rectangle((-0.5, -0.5), 1.0, 1.0, fill=False, ec=BLUE, lw=2, ls="--"))
    ax.add_patch(Rectangle((-0.75, -0.72), 1.5, 1.44, fill=False, ec="#7aa0c8", lw=1))
    ax.text(0, 0.98, "slide  +  1-2 drops of water  +  coverslip", ha="center", fontsize=9, color=INK)
    ax.text(1.0, 0.12, "12 mm cut", fontsize=9, color=VEIN, va="center")
    ax.text(1.0, -0.2, "coverslip", fontsize=9, color="#7aa0c8", va="center")
    ax.text(0, -1.0, "dashed = the 10 × 10 mm window you image\n(the crushed 1 mm border is cropped away later)",
            ha="center", va="top", fontsize=9, color=BLUE)
    ax.set_title("D  On the microscope", loc="left")


fig, axs = plt.subplots(1, 4, figsize=(17, 5.6))
for ax, f, lim in zip(axs, (panel_simple, panel_okra, panel_fern, panel_slide),
                      ((-2, 2.2, -2.4, 2.1), (-1.8, 2.0, -1.5, 2.2), (-0.9, 2.4, -2.6, 2.1), (-2.0, 2.0, -1.9, 1.4))):
    f(ax)
    ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal"); ax.axis("off")
fig.suptitle("One window per leaf: one small square (A, B) or one strip across a fern pinna (C); the rest of the "
             "leaf is not used. Same window area on every leaf.", fontsize=12.5, color=INK, y=1.0)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=220, bbox_inches="tight", facecolor="white")
print("SAVED", os.path.relpath(OUT, ROOT))
