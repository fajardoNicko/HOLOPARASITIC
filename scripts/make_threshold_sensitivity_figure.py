# -*- coding: utf-8 -*-
r"""
make_threshold_sensitivity_figure.py -- figure for the collapse-criterion check.

Reads data/threshold_sensitivity.json (scripts/run_threshold_sensitivity.py) and
draws two panels over the collapse criterion (largest component below 10..90%
of its original size):
  A  Spearman rho of p_c with mean degree and with fractal dimension
     (hollow markers: p >= .05)
  B  median p_c under uniform and degree-weighted removal
The 50% criterion used in the paper is marked in both panels.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_threshold_sensitivity_figure.py

Output: figures/threshold_sensitivity.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures" / "threshold_sensitivity.png"
INK = "#20303A"; MUTED = "#6B7780"; GRID = "#E3E7EA"
BLUE = "#2A6FB5"; ACCENT = "#E4572E"; SURFACE = "#FFFFFF"

S = json.loads((ROOT / "data" / "threshold_sensitivity.json").read_text())
tags = ["f%d" % p for p in range(10, 100, 10)]
x = [int(t[1:]) for t in tags]
B = [S["by_criterion"][t] for t in tags]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.titlecolor": INK, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
})


def series(ax, y, sig, color, label, marker="o"):
    ax.plot(x, y, color=color, linewidth=2, zorder=2, label=label)
    for xi, yi, s in zip(x, y, sig):
        ax.plot(xi, yi, marker=marker, markersize=7, zorder=3, linestyle="none",
                markeredgecolor=color, markeredgewidth=1.6,
                markerfacecolor=color if s else SURFACE)


fig, (a, b) = plt.subplots(1, 2, figsize=(10.4, 4.0))

rk = [c["spearman_random_with"]["mean_degree"] for c in B]
rd = [c["spearman_random_with"]["D"] for c in B]
series(a, [r["rho"] for r in rk], [r["p"] < .05 for r in rk], BLUE, "mean degree <k>")
series(a, [r["rho"] for r in rd], [r["p"] < .05 for r in rd], ACCENT, "fractal dimension D", "s")
a.set_ylim(0, 1)
a.set_title("A  Association with the threshold (Spearman ρ)", loc="left")
a.set_ylabel("ρ with p_c (uniform removal)")
a.text(92.5, rk[-1]["rho"], "<k>", color=INK, fontsize=8.5, va="center")
a.text(92.5, rd[-1]["rho"], "D", color=INK, fontsize=8.5, va="center")
a.text(96, 0.03, "hollow marker: p ≥ .05", color=MUTED, fontsize=8, ha="right")

mr = [c["median_random"] for c in B]
md = [c["median_degree"] for c in B]
series(b, mr, [True] * 9, BLUE, "uniform removal")
series(b, md, [True] * 9, ACCENT, "degree-weighted removal", "s")
b.set_ylim(0, 0.28)
b.set_title("B  Median critical removed fraction (n = 100)", loc="left")
b.set_ylabel("median p_c")
for c, xi, yi in zip(B, x, md):
    n = c["degree_vs_uniform"]["n_degree_lower"]
    b.text(xi, yi - 0.012, "%d" % n, ha="center", va="top", color=MUTED, fontsize=7.5)
b.text(10, 0.012, "numbers: networks (of 100) where degree-weighted p_c < uniform p_c",
       color=MUTED, fontsize=7.5, ha="left")

for ax in (a, b):
    ax.axvline(50, color=MUTED, linewidth=1, linestyle=(0, (3, 3)), zorder=1)
    ax.set_xticks(x)
    ax.set_xlim(6, 99)
    ax.set_xlabel("collapse criterion: largest component below this % of its original size")
a.legend(loc="upper left", frameon=False, fontsize=8.5)
b.legend(loc="upper right", frameon=False, fontsize=8.5)
a.text(50.8, 0.97, "criterion used\nin the paper", color=MUTED, fontsize=7.5, va="top")

fig.tight_layout()
OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, dpi=220, facecolor=SURFACE)
plt.close(fig)
print("saved", OUT.relative_to(ROOT))
