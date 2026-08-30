# -*- coding: utf-8 -*-
r"""
make_edge_control_figure.py -- Figure 14, the placement-rule control.

Reads data/random_edge_control.csv (written by run_random_edge_control.py) and
draws the comparison between the three edge-placement rules at matched edge
count.

Panel A is a slopegraph. Each line is one network carried across the three
rules, so the reader sees that the ordering holds within networks rather than
only on average. Panel B plots the same three gains against the network's
baseline mean degree, which is the variable the gain depends on most strongly.

    python scripts/make_edge_control_figure.py

Writes figures/edge_control.png and prints the numbers needed for Table 16.
ASCII-only stdout.
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

SRC = os.path.join(ROOT, "data", "random_edge_control.csv")
OUT = os.path.join(ROOT, "figures", "edge_control.png")

ARMS = [
    ("d_delaunay", "Delaunay\nshortest first", "#1b6ca8"),
    ("d_rand_del", "Delaunay pool\nrandom order", "#c8102e"),
    ("d_rand_any", "Random\nnode pairs", "#8c4a2f"),
]


def load():
    if not os.path.exists(SRC):
        print("ERROR: %s not found. Run run_random_edge_control.py first."
              % os.path.relpath(SRC, ROOT))
        sys.exit(1)
    return list(csv.DictReader(open(SRC, newline="")))


def main():
    rows = load()
    n = len(rows)
    k0 = np.array([float(r["k_current"]) for r in rows])
    gains = {key: np.array([float(r[key]) for r in rows]) for key, _, _ in ARMS}

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(11.5, 4.8))

    # ---- Panel A: within-network slopegraph -------------------------------
    xs = np.arange(len(ARMS))
    stacked = np.column_stack([gains[k] for k, _, _ in ARMS])
    for row in stacked:
        axA.plot(xs, row, color="0.65", lw=0.8, alpha=0.55, zorder=1)
    for i, (key, label, colour) in enumerate(ARMS):
        v = gains[key]
        axA.scatter(np.full(len(v), i), v, s=26, color=colour, zorder=3,
                    edgecolor="white", linewidth=0.5)
        axA.hlines(np.median(v), i - 0.22, i + 0.22, color="black", lw=2.2,
                   zorder=4)
        axA.text(i + 0.27, np.median(v), "Mdn %+.4f" % np.median(v),
                 va="bottom", ha="left", fontsize=8.5, zorder=5)
    axA.axhline(0, color="black", lw=0.9, ls=":")
    axA.set_xticks(xs)
    axA.set_xticklabels([lab for _, lab, _ in ARMS], fontsize=9)
    axA.set_ylabel(r"change in threshold  $\Delta p_c$")
    axA.set_title("A. Same edge count, three placement rules", fontsize=10.5,
                  loc="left")
    axA.grid(alpha=0.25, axis="y")

    # ---- Panel B: gain against baseline connectivity ----------------------
    for key, label, colour in ARMS:
        axB.scatter(k0, gains[key], s=26, color=colour, alpha=0.85,
                    edgecolor="white", linewidth=0.5,
                    label=label.replace("\n", " "))
        if len(k0) > 2:
            b, a = np.polyfit(k0, gains[key], 1)
            xx = np.linspace(k0.min(), k0.max(), 50)
            axB.plot(xx, a + b * xx, color=colour, lw=1.3, ls="--", alpha=0.9)
    axB.axhline(0, color="black", lw=0.9, ls=":")
    axB.set_xlabel(r"baseline mean degree  $\langle k \rangle_0$")
    axB.set_ylabel(r"change in threshold  $\Delta p_c$")
    axB.set_title("B. Gain against baseline connectivity", fontsize=10.5,
                  loc="left")
    axB.legend(fontsize=8.5, loc="upper right", framealpha=0.9)
    axB.grid(alpha=0.25)

    fig.suptitle("Edge placement at matched edge count (n = %d networks, "
                 "all raised to the same mean degree)" % n, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=160)
    plt.close(fig)
    print("figure -> %s" % os.path.relpath(OUT, ROOT))

    # ---- numbers for Table 16 --------------------------------------------
    print("\nTable 16 values, n = %d networks" % n)
    print("%-26s %10s %10s %18s" % ("Placement rule", "Mdn dpc", "improved",
                                    "vs Delaunay"))
    dd = gains["d_delaunay"]
    for key, label, _ in ARMS:
        v = gains[key]
        imp = int((v > 0).sum())
        if key == "d_delaunay":
            note = "reference"
        else:
            diff = dd - v
            nz = diff[diff != 0]
            W, p = stats.wilcoxon(nz) if len(nz) >= 3 else (float("nan"),
                                                            float("nan"))
            higher = int((diff > 0).sum())
            note = "W=%.0f, p=%.2g, %d/%d" % (W, p, higher, len(diff))
        print("%-26s %+10.5f %6d/%-3d %18s"
              % (label.replace("\n", " "), float(np.median(v)), imp, n, note))

    print("\nmedian edges added   : %d" % np.median(
        [int(r["edges_added"]) for r in rows]))
    print("baseline <k> range   : %.3f to %.3f" % (k0.min(), k0.max()))
    print("network size range   : %d to %d nodes"
          % (min(int(r["N"]) for r in rows), max(int(r["N"]) for r in rows)))
    ratio_rd = np.median(gains["d_rand_del"]) / np.median(dd)
    ratio_ra = np.median(gains["d_rand_any"]) / np.median(dd)
    print("median gain ratios   : rand_del %.1fx, rand_any %.1fx the Delaunay arm"
          % (ratio_rd, ratio_ra))


if __name__ == "__main__":
    main()
