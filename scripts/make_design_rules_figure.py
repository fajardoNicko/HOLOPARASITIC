# -*- coding: utf-8 -*-
r"""
make_design_rules_figure.py -- Figure 15: the empirical design rules, one panel each.

Reads data/design_rules.json, data/design_rules_perleaf.csv, data/design_rules_grid.csv
and data/random_edge_control.csv (all written by run_design_rules.py).  Writes
figures/design_rules.png.  Run AFTER scripts/run_design_rules.py.  ASCII-only stdout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "figures" / "design_rules.png"

INK = "#20303A"; MUTED = "#6B7780"; GRID = "#E3E7EA"
BLUE = "#2A6FB5"; ACCENT = "#E4572E"; SURFACE = "#FFFFFF"

R = json.loads((DATA / "design_rules.json").read_text())
leaf = pd.read_csv(DATA / "design_rules_perleaf.csv")
grid = pd.read_csv(DATA / "design_rules_grid.csv")
edge = pd.read_csv(DATA / "random_edge_control.csv").dropna(subset=["d_delaunay", "d_rand_del", "d_rand_any"])

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.titlecolor": INK, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
})


def dots(ax, x, y, color=BLUE, s=28, label=None, zorder=3, **kw):
    ax.scatter(x, y, s=s, color=color, edgecolor=SURFACE, linewidth=0.9,
               alpha=0.9, label=label, zorder=zorder, **kw)


fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.4))
(a, b, c), (d, e, f) = axes

# (a) tolerance line: f50 vs <k>, with the tree line and the Y-ceiling -----------
k = leaf["mean_degree"].to_numpy(); pc = leaf["pc_random"].to_numpy()
fit = R["R3_tolerance_law"]["cohort_ols_pc_on_(k-2)"]["beta"]
dots(a, k, pc)
xx = np.linspace(2.0, 3.0, 50)
a.plot(xx, fit[0] + fit[1] * (xx - 2), color=ACCENT, lw=2, zorder=4)
for xv in (2.0, 3.0):
    a.axvline(xv, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=2)
a.text(2.03, 0.285, "tree line\n<k> = 2", color=MUTED, fontsize=8.5, ha="left", va="top")
a.text(2.97, 0.012, "Y-ceiling\n<k> = 3", color=MUTED, fontsize=8.5, ha="right", va="bottom")
a.set_xlim(1.95, 3.05); a.set_ylim(0, 0.30)
a.set_xlabel("mean junction degree  <k>")
a.set_ylabel("critical removed fraction  p_c")
a.set_title("(a) Tolerance rises with loops")
a.text(2.04, 0.012, "p_c = %.3f + %.3f (<k> - 2)\nSpearman rho = %.2f, n = 100"
       % (fit[0], fit[1], R["R3_tolerance_law"]["spearman_k_vs_pc"][0]),
       color=INK, fontsize=8.5, ha="left", va="bottom",
       bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec=GRID))

# (b) the junction identity: <k> = 3 - 2t --------------------------------------
t = leaf["p1"].to_numpy()
dots(b, t, k)
tt = np.linspace(0, 0.5, 20)
b.plot(tt, 3 - 2 * tt, color=ACCENT, lw=2, ls=(0, (5, 3)), zorder=4)
b.set_xlim(-0.01, 0.5); b.set_ylim(1.95, 3.05)
b.set_xlabel("fraction of junctions that are free vein endings  t")
b.set_ylabel("mean junction degree  <k>")
b.set_title("(b) Every free ending is half a loop not built")
r2 = R["R2_free_endings"]["ols_k_on_t"]
b.text(0.49, 2.98, "identity  <k> = 3 - 2t\nfitted slope %.2f +/- %.2f,  R2 = %.3f"
       % (r2["slope"], r2["se_slope"], r2["R2"]), color=INK, fontsize=8.5,
       ha="right", va="top", bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec=GRID))

# (c) count the core: f50 vs (k_core - 2), real leaves + synthetic grid ----------
kc = leaf["k_core"].to_numpy() - 2
s = R["R11_transfer_test"]["real_law_slope_through_origin"]
dots(c, kc, pc, label="real leaves (n = 100)")
gk = grid["k_core"].to_numpy() - 2
c.scatter(gk, grid["pc_random"], s=34, facecolor="none", edgecolor=ACCENT, linewidth=1.3,
          label="synthetic grid (n = 42)", zorder=3)
xx = np.linspace(0, 1.05, 30)
c.plot(xx, s * xx, color=BLUE, lw=2, zorder=4)
c.set_xlim(0, 2.25); c.set_ylim(0, 0.45)
c.set_xlabel("excess degree of the looped core  (k_core - 2)")
c.set_ylabel("critical removed fraction  p_c")
c.set_title("(c) Count the core, not the whole leaf")
c.legend(loc="lower right", frameon=False, fontsize=8.5)
c.text(0.03, 0.43, "real leaves:  p_c = %.2f (k_core - 2),  no intercept\nSpearman rho = %.2f "
       "(vs %.2f for <k>)\nsynthetic: same ranking (rho = %.2f), different slope"
       % (s, R["R10b_core_density"]["spearman_kcore_vs_pc"][0],
          R["R10b_core_density"]["spearman_k_vs_pc"][0],
          R["R11_transfer_test"]["spearman_kcore_vs_pc_grid"][0]),
       color=INK, fontsize=8.5, ha="left", va="top",
       bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec=GRID))

# (d) a loop is worth what it bypasses ------------------------------------------
tiers = [("shortest\nplanar closure", edge["d_delaunay"]),
         ("random\nplanar closure", edge["d_rand_del"]),
         ("random\nnon-planar link", edge["d_rand_any"])]
xs = np.arange(3)
meds = [float(np.median(v)) for _, v in tiers]
d.bar(xs, meds, width=0.42, color=BLUE, zorder=3)
rng = np.random.default_rng(1)
for i, (_, v) in enumerate(tiers):
    d.scatter(i + rng.uniform(-0.1, 0.1, len(v)), v, s=14, color=INK, alpha=0.35,
              edgecolor="none", zorder=4)
for i, m in enumerate(meds):
    d.text(i, m + 0.006, "+%.3f" % m, ha="center", va="bottom", color=INK, fontsize=9)
d.set_xticks(xs); d.set_xticklabels([n for n, _ in tiers])
d.set_ylim(0, 0.32)
d.set_ylabel("gain in p_c at equal number of added veins")
d.set_title("(d) A loop is worth what it bypasses")
d.text(0.02, 0.30, "n = 27 leaves, same edge budget per arm\nbars = median, dots = leaves",
       color=MUTED, fontsize=8.5, ha="left", va="top")

# (e) the hole rule --------------------------------------------------------------
cols = [("dispersed\n(uniform)", leaf["pc_random"]),
        ("ten lesions", leaf["pc_disc10"]),
        ("one lesion", leaf["pc_disc1"])]
bp = e.boxplot([v.to_numpy() for _, v in cols], positions=[0, 1, 2], widths=0.42,
               patch_artist=True, showfliers=False, zorder=3,
               medianprops=dict(color=SURFACE, lw=2),
               boxprops=dict(facecolor=BLUE, edgecolor=BLUE),
               whiskerprops=dict(color=BLUE, lw=1.2), capprops=dict(color=BLUE, lw=1.2))
for i, (_, v) in enumerate(cols):
    e.scatter(i + rng.uniform(-0.12, 0.12, len(v)), v, s=12, color=INK, alpha=0.25,
              edgecolor="none", zorder=4)
    e.text(i, float(np.median(v)) + 0.025, "median %.3f" % float(np.median(v)),
           ha="center", va="bottom", color=INK, fontsize=8.5)
mr = R["R4_molloy_reed"]["fc_MR_quartiles"][1]
e.axhline(mr, color=ACCENT, lw=1.6, ls=(0, (5, 3)), zorder=2)
e.text(-0.42, mr + 0.012, "Molloy-Reed ceiling for scattered loss (median %.2f)" % mr,
       color=ACCENT, fontsize=8, ha="left", va="bottom")
e.set_xticks([0, 1, 2]); e.set_xticklabels([n for n, _ in cols])
e.set_ylim(0, 0.62)
e.set_ylabel("critical removed fraction")
e.set_title("(e) Loops protect against scattered loss, not a hole")

# (f) no hubs: weighted-removal penalty vs <k> -----------------------------------
pen = leaf["attack_gap"] / leaf["pc_random"]
dots(f, k, 100 * pen)
f.set_xlim(2.1, 3.02); f.set_ylim(0, 70)
f.set_xlabel("mean junction degree  <k>")
f.set_ylabel("tolerance lost when removal favours\nhigh-degree junctions  (%)")
f.set_title("(f) No hubs: the looped mesh has no weak spot")
rr = R["R5_no_hubs"]["spearman_relpenalty_vs_k"][0]
f.text(2.98, 66, "max degree 4-5 in every leaf\nmedian penalty %.0f%%; Spearman rho = %.2f"
       % (100 * R["R5_no_hubs"]["penalty_rel_quartiles"][1], rr),
       color=INK, fontsize=8.5, ha="right", va="top",
       bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec=GRID))

fig.suptitle("Empirical design rules for a damage-tolerant leaf venation (percolation cohort, n = 100)",
             fontsize=12.5, color=INK, fontweight="bold", y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.975))
OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, dpi=220, facecolor=SURFACE)
plt.close(fig)
print("saved", OUT.relative_to(ROOT))
