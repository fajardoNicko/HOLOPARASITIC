# -*- coding: utf-8 -*-
r"""
make_local_validation_figure.py -- Figure 14 of the revised paper: the locally
collected leaves against the archived cohort's tolerance line.

Draws the 100 percolation-cohort networks, the tolerance line
p_c = a + b(<k> - 2) fitted to them by ordinary least squares, and its 95%
prediction band. Local leaves are read from empirical/local_leaves.csv (one row
per traced window: species, common_name, group, leaf_id, mean_degree, p_c, ...)
and plotted on top, crops and non-crops with different markers. Until that file
has rows, the figure shows the cohort and the band only.

If data/size_matched_windows.json exists (scripts/run_size_matched_windows.py),
a second panel repeats the comparison against archived windows matched in size
to the local ones; MODE picks the area-matched or junction-matched set.

It also prints the two pre-set success checks: the one-sided Spearman test of
p_c rising with <k> among the local leaves, and how many fall inside the band.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_local_validation_figure.py
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

LOCAL = os.path.join(ROOT, "empirical", "local_leaves.csv")
OUT = os.path.join(ROOT, "figures", "revised", "Figure_14_local_leaves.png")
WINDOWS = os.path.join(ROOT, "data", "size_matched_windows.json")
MODE = "area"    # which size-matched set panel B shows: "area" (5.9 mm) or "nodes" (~2,000 junctions)
SPECIES = {   # scientific name: (common name, group, colour, marker)
    "Annona muricata": ("guyabano", "crop", "#c1121f", "^"),
    "Abelmoschus esculentus": ("okra", "crop", "#E4572E", "^"),
    "Terminalia catappa": ("talisay", "non-crop", "#1f6f4a", "o"),
    "Hibiscus rosa-sinensis": ("gumamela", "non-crop", "#7a2468", "o"),
    "Nephrolepis sp.": ("sword fern", "non-crop", "#2F7FA8", "o"),
}
INK, MUTED = "#20303A", "#5A6A73"


def cohort():
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "data", "analysis_master.csv"), newline=""))
            if r["in_percolation_cohort_100"] == "True"]
    return np.array([float(r["mean_degree"]) for r in rows]), np.array([float(r["pc_random"]) for r in rows])


def band(k, pc, xs):
    x = k - 2
    n = len(x)
    b, a = np.polyfit(x, pc, 1)
    resid = pc - (a + b * x)
    s = np.sqrt((resid ** 2).sum() / (n - 2))
    t = stats.t.ppf(0.975, n - 2)
    se = s * np.sqrt(1 + 1 / n + (xs - 2 - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())
    yhat = a + b * (xs - 2)
    return a, b, s, yhat, yhat - t * se, yhat + t * se


def local():
    if not os.path.exists(LOCAL):
        return []
    return [r for r in csv.DictReader(open(LOCAL, newline="")) if r.get("p_c") and r.get("mean_degree")]


def windows(mode):
    """Per-leaf size-matched window values from run_size_matched_windows.py, or None."""
    if not os.path.exists(WINDOWS):
        return None
    W = json.load(open(WINDOWS))[mode]
    if "line" not in W:
        return None
    k = np.array([l["mean_degree"] for l in W["leaves"]])
    pc = np.array([l["p_c"] for l in W["leaves"]])
    return k, pc, W


def draw(ax, k, pc, L, cohort_label, title):
    xs = np.linspace(1.75, 3.05, 200)
    a, b, s, yhat, lo, hi = band(k, pc, xs)
    ax.fill_between(xs, lo, hi, color="#9fb6d6", alpha=0.35, label="95% prediction band")
    ax.plot(xs, yhat, color=INK, lw=1.6,
            label=r"line: $p_c$ = %.3f + %.3f($\langle k \rangle$ $-$ 2)" % (a, b))
    ax.scatter(k, pc, s=16, color="0.65", edgecolor="white", lw=0.3, label=cohort_label)
    for name, (common, group, col, mk) in SPECIES.items():
        pts = [r for r in L if r["species"].strip() == name]
        if pts:
            ax.scatter([float(r["mean_degree"]) for r in pts], [float(r["p_c"]) for r in pts], s=70,
                       marker=mk, color=col, edgecolor="black", lw=0.6, zorder=4,
                       label="%s (%s)" % (common, group))
    if not L:
        ax.text(0.02, 0.96, "Local leaves: not measured yet", transform=ax.transAxes, va="top",
                fontsize=10, color=MUTED, style="italic")
    ax.set_title(title, fontsize=10.5, color=INK, loc="left")
    ax.set_xlabel(r"mean degree $\langle k \rangle$")
    ax.set_xlim(1.75 if k.min() < 1.95 else 1.95, 3.05); ax.grid(alpha=0.25)
    ax.legend(fontsize=7.5, loc="upper left")
    return a, b, s


def checks(label, k, pc, L):
    if len(L) < 3:
        return
    lk = np.array([float(r["mean_degree"]) for r in L]); lp = np.array([float(r["p_c"]) for r in L])
    rho, p2 = stats.spearmanr(lk, lp)
    p1 = p2 / 2 if rho > 0 else 1 - p2 / 2
    _, _, _, _, l2, h2 = band(k, pc, lk)
    inside = int(((lp >= l2) & (lp <= h2)).sum())
    print("%s: local leaves n=%d  Spearman rho=%.3f  one-sided p=%.4g  inside band %d/%d"
          % (label, len(L), rho, p1, inside, len(L)))


def main():
    k, pc = cohort()
    L = local()
    win = windows(MODE)
    if win is None:
        fig, ax = plt.subplots(figsize=(8.6, 5.6))
        axes = [ax]
    else:
        fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.6), sharey=True)
    a, b, s = draw(axes[0], k, pc, L, "archived whole leaves (n = %d)" % len(k),
                   "A.  Against whole archived leaves" if win else "")
    axes[0].set_ylabel("$p_c$ (uniform removal, 50% criterion)")
    print("whole-leaf line: p_c = %.4f + %.4f(<k> - 2); residual SD %.4f" % (a, b, s))
    checks("whole leaves", k, pc, L)
    if win is not None:
        wk, wpc, W = win
        what = ("5.9 x 5.9 mm windows" if MODE == "area"
                else "windows of about %d junctions" % json.load(open(WINDOWS))["target_nodes_nodes_mode"])
        a2, b2, s2 = draw(axes[1], wk, wpc, L, "archived leaves, %s (n = %d)" % (what, len(wk)),
                          "B.  Against size-matched archived windows")
        print("window line (%s): p_c = %.4f + %.4f(<k> - 2); residual SD %.4f" % (MODE, a2, b2, s2))
        checks("size-matched windows", wk, wpc, L)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
    print("SAVED", os.path.relpath(OUT, ROOT))
    for g in ("crop", "non-crop"):
        gp = [float(r["p_c"]) for r in L if SPECIES.get(r["species"].strip(), ("", ""))[1] == g]
        if gp:
            print("  %s: median p_c %.4f (n=%d)" % (g, float(np.median(gp)), len(gp)))


if __name__ == "__main__":
    main()
