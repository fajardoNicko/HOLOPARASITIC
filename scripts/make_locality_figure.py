# -*- coding: utf-8 -*-
r"""
make_locality_figure.py -- the damage-locality figure (deck slide 14).

Reads data/criterion_and_locality.csv and draws the critical removed fraction
under the three damage geometries: dispersed (uniform random removal), one
contiguous lesion, and ten contiguous lesions, at matched removal fractions.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_locality_figure.py

Boxplots alone would show only that the distributions separate. The claim being
made is stronger than that -- every network moved the same way, with no
exceptions -- so each network is also drawn as a faint line carried across the
three conditions. The reader can then see that the separation holds within
networks and not merely on average, which is the reason the result is worth a
slide.

Styled for projection rather than for print: type is set at the deck's minimum
legible size, the ground matches the deck's Paper token, and the dispersed
condition carries the deck's Loss red while the two lesion conditions are
neutral, so the colour still means "damage geometry under test".

Writes figures/locality_boxplots.png and prints the numbers quoted on the
slide. ASCII-only stdout.
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

SRC = os.path.join(ROOT, "data", "criterion_and_locality.csv")
OUT = os.path.join(ROOT, "figures", "locality_boxplots.png")

# Deck palette (PPT_BUILD_GUIDE.pdf section 1).
INK = "#1A1D21"
PAPER = "#FAFAF7"
LOSS = "#C1462F"
MUTED = "#6B7280"
RULE = "#D9D9D2"

CONDITIONS = [
    ("pc_gcc", "Dispersed\nuniform random", LOSS),
    ("pc_disc1", "1 lesion\ncontiguous patch", MUTED),
    ("pc_disc10", "10 lesions\ncontiguous patches", MUTED),
]


def load():
    if not os.path.exists(SRC):
        print("ERROR: %s not found." % os.path.relpath(SRC, ROOT))
        raise SystemExit(1)
    cols = {key: [] for key, _, _ in CONDITIONS}
    with open(SRC, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            values = [row[key] for key, _, _ in CONDITIONS]
            if any(v in ("", "nan", "NA") for v in values):
                continue
            for (key, _, _), value in zip(CONDITIONS, values):
                cols[key].append(float(value))
    return {k: np.asarray(v) for k, v in cols.items()}


def style():
    matplotlib.rcParams.update({
        "font.size": 16, "axes.labelsize": 18, "axes.titlesize": 20,
        "xtick.labelsize": 15, "ytick.labelsize": 15, "legend.fontsize": 15,
        "savefig.dpi": 200, "savefig.bbox": "tight",
        "figure.facecolor": PAPER, "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER, "text.color": INK,
        "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
        "axes.edgecolor": RULE,
    })


def draw(data):
    keys = [key for key, _, _ in CONDITIONS]
    series = [data[k] for k in keys]
    n = len(series[0])
    positions = np.arange(1, len(keys) + 1)

    fig, ax = plt.subplots(figsize=(9.5, 6.6))

    # Paired lines first, so the boxes sit on top of them.
    paired = np.column_stack(series)
    for row in paired:
        ax.plot(positions, row, color=MUTED, alpha=0.11, linewidth=0.8,
                zorder=1, solid_capstyle="round")

    box = ax.boxplot(
        series, positions=positions, widths=0.42, patch_artist=True,
        showfliers=False, zorder=3,
        medianprops=dict(color=INK, linewidth=2.4),
        whiskerprops=dict(color=INK, linewidth=1.2),
        capprops=dict(color=INK, linewidth=1.2),
        boxprops=dict(linewidth=1.2))
    for patch, (_, _, colour) in zip(box["boxes"], CONDITIONS):
        patch.set_facecolor(colour)
        patch.set_alpha(0.24)
        patch.set_edgecolor(colour)

    # Median above each box and ratio below it, so neither annotation can run
    # into its neighbour the way a right-hand label does at this box spacing.
    medians = [float(np.median(s)) for s in series]
    base = series[0]
    for pos, arr, med, (_, _, colour) in zip(positions, series, medians,
                                             CONDITIONS):
        top = float(np.max(arr[arr <= np.percentile(arr, 99)]))
        ax.annotate("%.4f" % med, xy=(pos, top + 0.022), ha="center",
                    va="bottom", fontsize=17, fontweight="bold", color=colour)
        if pos == positions[0]:
            continue
        bottom = float(np.min(arr))
        ax.annotate("%.2fx dispersed\n%d/%d networks"
                    % (float(np.median(arr / base)),
                       int((arr > base).sum()), n),
                    xy=(pos, bottom - 0.028), ha="center", va="top",
                    fontsize=14, color=MUTED, linespacing=1.35)

    ax.set_xticks(positions)
    ax.set_xticklabels([label for _, label, _ in CONDITIONS])
    ax.set_ylabel("Critical removed fraction")
    ax.set_ylim(0.0, 0.60)
    ax.set_xlim(0.5, len(keys) + 0.5)
    ax.yaxis.grid(True, color=RULE, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax.set_title("Localised damage is tolerated far better than dispersed damage",
                 fontsize=18, color=INK, pad=16, loc="left")
    fig.text(0.125, 0.005,
             "n = %d networks; each faint line is one network carried across "
             "the three damage geometries." % n,
             fontsize=13, color=MUTED, ha="left")

    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT)
    plt.close(fig)
    return medians, n


def main():
    style()
    data = load()
    medians, n = draw(data)
    base = data["pc_gcc"]
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    print("  n = %d networks" % n)
    for (key, label, _), med in zip(CONDITIONS, medians):
        flat = label.replace("\n", " ")
        print("  %-28s median %.4f" % (flat, med))
    for key, label, _ in CONDITIONS[1:]:
        arr = data[key]
        print("  %-28s median ratio %.2fx, higher in %d/%d networks"
              % (label.replace("\n", " "), float(np.median(arr / base)),
                 int((arr > base).sum()), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
