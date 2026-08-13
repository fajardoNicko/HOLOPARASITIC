# -*- coding: utf-8 -*-
r"""
make_stats_tree.py -- Fig 12, the statistical-analysis flowchart, rebuilt to match
the analysis the code ACTUALLY runs (not a generic Shapiro -> ANOVA/Kruskal tree).

Three lanes, mirroring run_cohort_percolation.py / run_synthetic_grid.py / validate_stats.py:
  A  estimate p_c per network   (MC sweep -> logistic fit -> bootstrap CI)
  B  do <k> and D predict p_c   (Spearman -> partial correlation -> OLS + VIF)
  C  do attack modes differ     (pair per network -> Wilcoxon/Mann-Whitney -> rank-biserial)

Output: figures/methodology/fig12_stats_tree.png  (landscape)
ASCII-only stdout.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures", "methodology")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "savefig.dpi": 300})

INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#3B8EA5"; VEIN = "#7A4E2D"
GREEN = "#3F8F5B"; ARROW = "#8494A0"
CAT = {"a": ("#FBE6DC", ACCENT), "b": ("#E7F0F3", BLUE),
       "c": ("#E3F0E8", GREEN), "hdr": ("#E4E9EC", INK)}


def card(ax, cx, cy, w, h, title, subs, cat, ts=11, ss=8.6):
    fill, edge = CAT[cat]
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.015,rounding_size=0.10", linewidth=1.7,
                 edgecolor=edge, facecolor=fill, zorder=3))
    ax.text(cx, cy + h * 0.24, title, ha="center", va="center", color=INK,
            fontsize=ts, fontweight="bold", zorder=4)
    for i, line in enumerate(subs):
        ax.text(cx, cy - h * 0.02 + (len(subs) - 1) * 1.15 - i * 2.3, line,
                ha="center", va="center", color="#41505A", fontsize=ss, zorder=4)


def arrow(ax, p0, p1, color=ARROW, lw=2.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=15,
                 linewidth=lw, color=color, zorder=2, shrinkA=2, shrinkB=2))


fig, ax = plt.subplots(figsize=(15, 8.2))
H = 100 * 8.2 / 15
ax.set_xlim(0, 100); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.axis("off")
fig.patch.set_facecolor("white")

# header
card(ax, 50, H - 5, 46, 7.5, "Statistical analysis", [], "hdr", ts=13)

lanes = [
    (18, "a", "Estimate p_c  (per network)", [
        ("Monte-Carlo collapse sweep",
         ["ρ swept 0→1; 40 densities", "× 80 trials per density"]),
        ("Logistic regression",
         ["P(collapse) vs ρ;", "p_c = inflection (P = 0.5)"]),
        ("Bootstrap 95% CI",
         ["resample trials, refit;", "+ empirical-crossing fallback"]),
    ]),
    (50, "b", "Do  ⟨k⟩  and  D  predict p_c?", [
        ("Spearman rank ρ",
         ["monotonic assoc. of", "⟨k⟩–p_c and D–p_c (no normality)"]),
        ("Partial correlation",
         ["r(p_c,⟨k⟩ | D) and", "r(p_c,D | ⟨k⟩): isolate each"]),
        ("Multiple OLS  +  VIF",
         ["p_c ~ ⟨k⟩ + D;", "VIF checks collinearity"]),
    ]),
    (82, "c", "Do attack modes / parasites differ?", [
        ("Pair p_c per network",
         ["random vs degree vs", "betweenness (same networks)"]),
        ("Wilcoxon / Mann–Whitney",
         ["nonparametric paired /", "two-sample difference test"]),
        ("Rank-biserial effect size",
         ["magnitude + direction,", "not just significance"]),
    ]),
]

top = H - 13
gap = 12.5
w, h = 27, 9.6
for cx, cat, lane_title, boxes in lanes:
    ax.text(cx, H - 10.2, lane_title, ha="center", fontsize=11,
            fontweight="bold", color=CAT[cat][1])
    arrow(ax, (50, H - 8.7), (cx, top + h / 2 + 0.5), color="#B5BEC4", lw=1.6)
    ys = [top - i * (h + gap) for i in range(3)]
    for j, (t, s) in enumerate(boxes):
        card(ax, cx, ys[j], w, h, t, s, cat)
        if j < 2:
            arrow(ax, (cx, ys[j] - h / 2), (cx, ys[j + 1] + h / 2))

# bottom banner
by = top - 2 * (h + gap) - h / 2 - 6
ax.text(50, by, "Rank-based / nonparametric throughout — no normality assumed "
        "(p_c is bounded on [0,1], the D range is narrow, and the distributions are skewed).",
        ha="center", va="center", fontsize=9.3, style="italic", color="#5A6A73")

path = os.path.join(FIG, "fig12_stats_tree.png")
fig.savefig(path, bbox_inches="tight", pad_inches=0.15, facecolor="white")
plt.close(fig)
print("SAVED:", os.path.relpath(path, ROOT))
