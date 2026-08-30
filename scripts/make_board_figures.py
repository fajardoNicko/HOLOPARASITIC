r"""make_board_figures.py — the five vision-board figures, in the board palette.

Every panel is drawn from archived project data:
  data/cohort_pc.csv              p_c under uniform and degree-weighted removal
  data/cohort_suggested.csv       p_c before / after areole-closing loops
  data/criterion_and_locality.csv p_c under dispersed loss and contiguous lesions
  UCBG_venation_form_data/        one traced leaf, re-run through the same engine

Outputs figures/board_*.png at print resolution.

  ...python.exe scripts\make_board_figures.py
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
from matplotlib.collections import LineCollection

DATA = os.path.join(ROOT, "data")
FIGS = os.path.join(ROOT, "figures")

# ---------------------------------------------------------------- palette
DEEP, TEAL, GREEN, SAGE = "#12331A", "#1B5E20", "#66BB6A", "#A5D6A7"
RULE, TINT, SOFT = "#CDE7CE", "#E8F5E9", "#4A6650"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 20,
    "axes.titlesize": 21,
    "axes.labelsize": 20,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 18,
    "axes.edgecolor": SOFT,
    "axes.labelcolor": DEEP,
    "text.color": DEEP,
    "xtick.color": SOFT,
    "ytick.color": SOFT,
    "axes.linewidth": 1.1,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})
DPI = 260


def tidy(ax, grid="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(True, axis=grid, color=RULE, lw=0.9, alpha=0.9)
        ax.set_axisbelow(True)


def read(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def col(rows, key):
    out = []
    for r in rows:
        try:
            out.append(float(r[key]))
        except (TypeError, ValueError):
            out.append(float("nan"))
    return np.array(out)


def spearman(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / np.sqrt((ra @ ra) * (rb @ rb)))


# ================================================================ FIGURE 1
def fig_predictors():
    rows = read("cohort_pc.csv")
    pc, k, D = col(rows, "pc_random"), col(rows, "mean_degree"), col(rows, "D")

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7))
    for ax, x, lab, c in ((axes[0], k, "Mean degree  $\\langle k \\rangle$", TEAL),
                          (axes[1], D, "Fractal dimension  $D$", GREEN)):
        ok = np.isfinite(x) & np.isfinite(pc)
        ax.scatter(x[ok], pc[ok], s=34, c=c, alpha=.55, lw=.7, edgecolors="white")
        m, b = np.polyfit(x[ok], pc[ok], 1)
        xs = np.linspace(x[ok].min(), x[ok].max(), 50)
        ax.plot(xs, m * xs + b, color=DEEP, lw=2.2)
        ax.text(.04, .93, "$\\rho$ = %.3f" % spearman(x, pc), transform=ax.transAxes,
                fontsize=21, fontweight="bold", color=DEEP, va="top")
        ax.set_xlabel(lab)
        tidy(ax, grid="both")
    axes[0].set_ylabel("Collapse threshold  $p_c$")
    axes[1].tick_params(labelleft=False)
    for ax in axes:
        ax.set_ylim(0.10, 0.30)
    fig.tight_layout(w_pad=1.4)
    save(fig, "board_predictors.png")


# ================================================================ FIGURE 2
def fig_loops():
    rows = [r for r in read("cohort_suggested.csv")
            if r["pc_current"] not in ("", "nan")
            and float(r["N"]) >= 1000 and float(r["pc_current"]) >= 0.02]
    a, b = col(rows, "pc_current"), col(rows, "pc_suggested")
    gain = b - a
    up = int((gain > 0).sum())

    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.9),
                             gridspec_kw={"width_ratios": [1.25, 1]})

    ax = axes[0]
    lo, hi = 0.10, 0.32
    ax.plot([lo, hi], [lo, hi], color=SOFT, lw=1.6, ls="--", zorder=1)
    ax.fill_between([lo, hi], [lo, hi], hi, color=TINT, zorder=0)
    ax.scatter(a, b, s=38, c=TEAL, alpha=.6, lw=.7, edgecolors="white", zorder=3)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
    ax.set_xlabel("$p_c$  as traced")
    ax.set_ylabel("$p_c$  with loops added")
    ax.text(.05, .93, "%d of %d improved\nnone made worse" % (up, len(rows)),
            transform=ax.transAxes, fontsize=20, fontweight="bold",
            color=DEEP, va="top", linespacing=1.35)
    tidy(ax, grid="both")

    ax = axes[1]
    ax.hist(gain, bins=22, color=GREEN, edgecolor="white", lw=.8)
    ax.axvline(0, color=DEEP, lw=1.8)
    ax.axvline(np.median(gain), color=TEAL, lw=2.2, ls="--")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.18)
    ax.text(np.median(gain), ax.get_ylim()[1] * .95, "  median +%.3f" % np.median(gain),
            fontsize=18, color=TEAL, fontweight="bold", va="top")
    ax.set_xlabel("Change in $p_c$")
    ax.set_ylabel("Leaves")
    tidy(ax)
    fig.tight_layout(w_pad=1.6)
    save(fig, "board_loops.png")


# ================================================================ FIGURE 3
def fig_geometry():
    rows = read("criterion_and_locality.csv")
    series = [("Dispersed\nloss", col(rows, "pc_gcc"), TEAL),
              ("10 small\nlesions", col(rows, "pc_disc10"), GREEN),
              ("1 contiguous\nlesion", col(rows, "pc_disc1"), "#8CC98F")]
    base = np.nanmedian(series[0][1])

    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    rng = np.random.default_rng(11)
    for i, (lab, v, c) in enumerate(series):
        v = v[np.isfinite(v)]
        ax.scatter(rng.normal(i, .085, v.size), v, s=26, c=c, alpha=.45,
                   lw=.5, edgecolors="white", zorder=2)
        bp = ax.boxplot(v, positions=[i], widths=.42, patch_artist=True,
                        showfliers=False, zorder=3)
        bp["boxes"][0].set(facecolor="white", edgecolor=DEEP, lw=1.6, alpha=.92)
        for part in ("whiskers", "caps"):
            for ln in bp[part]:
                ln.set(color=DEEP, lw=1.4)
        bp["medians"][0].set(color=DEEP, lw=2.6)
        med = float(np.median(v))
        top = float(np.percentile(v, 75))
        top += 1.5 * (top - float(np.percentile(v, 25)))
        top = min(top, float(v.max()))
        ax.text(i, top + .035, "%.3f" % med, ha="center", fontsize=20,
                fontweight="bold", color=DEEP, zorder=4)
        if i:
            ax.text(i, .06, "%.2f$\\times$" % (med / base), ha="center",
                    fontsize=22, fontweight="bold", color=DEEP)
    ax.set_xticks(range(3), [s[0] for s in series])
    ax.set_ylabel("Collapse threshold  $p_c$")
    ax.set_ylim(0, .72)
    ax.set_xlim(-.6, 2.6)
    tidy(ax)
    fig.tight_layout()
    save(fig, "board_geometry.png")


# ============================================== FIGURES 4 & 5 (one real leaf)
def representative_leaf():
    """The cohort leaf whose p_c sits closest to the cohort median."""
    rows = read("cohort_pc.csv")
    pc = col(rows, "pc_random")
    target = float(np.median(pc))
    order = np.argsort(np.abs(pc - target))
    for i in order:
        if 1500 <= float(rows[i]["n_nodes"]) <= 9000:
            return rows[i]["species"], float(pc[i])
    return rows[order[0]]["species"], float(pc[order[0]])


def load_leaf(species):
    from holoparasitic import realleaf
    for name, nodes_csv, veins_csv in realleaf.find_leaf_pairs(
            os.path.join(ROOT, "UCBG_venation_form_data")):
        if name == species:
            return realleaf.load_matos(nodes_csv, veins_csv)
    raise SystemExit("leaf %s not found" % species)


def fig_collapse_and_montage():
    import networkx as nx
    import config
    from holoparasitic import percolation

    species, pc_ref = representative_leaf()
    G = load_leaf(species)
    print("   representative leaf: %s  (N=%d, archived p_c=%.4f)"
          % (species, G.number_of_nodes(), pc_ref))

    # ---------- collapse curve, same engine, uniform vs degree-weighted -----
    curves = {}
    for mode, label in (("random", "uniform"), ("targeted", "degree-weighted")):
        p = config.PercolationParams(n_densities=40, n_trials=16_000,
                                     mode=mode, seed=3)
        res = percolation.density_response(G, params=p, rho_max=0.45)
        fit = percolation.fit_pc(res["X"], res["y"])
        pc = fit["p_c"]
        if not np.isfinite(pc):
            pc = percolation.pc_crossing(res["rhos"], res["p_collapse"])
        curves[label] = (np.asarray(res["rhos"]),
                         np.asarray(res["p_collapse"]), float(pc), fit)
        print("      %-16s p_c = %.4f" % (label, pc))

    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    for (label, (rhos, pcol, pc, fit)), c in zip(curves.items(), (TEAL, GREEN)):
        ax.scatter(rhos, pcol, s=30, c=c, alpha=.55, lw=.6, edgecolors="white")
        xs = np.linspace(0, .45, 400)
        if fit.get("model") is not None:
            ys = 1 / (1 + np.exp(-(fit["coef"] * xs + fit["intercept"])))
            ax.plot(xs, ys, color=c, lw=2.6, label="%s   $p_c$ = %.3f" % (label, pc))
        ax.axvline(pc, color=c, lw=1.4, ls=":")
    ax.axhline(.5, color=SOFT, lw=1.1, ls="--")
    ax.set_xlabel("Fraction of junctions removed")
    ax.set_ylabel("P(network fragmented)")
    ax.set_xlim(0, .45); ax.set_ylim(-.03, 1.06)
    ax.legend(loc="lower right", frameon=False)
    tidy(ax, grid="both")
    fig.tight_layout()
    save(fig, "board_collapse.png")

    # ---------- montage: the giant component shrinking -----------------------
    pos = {i: d["pos"] for i, d in G.nodes(data=True)}
    nodes = list(G.nodes)
    rng = config.new_rng(5)
    order = rng.permutation(len(nodes))
    rhos = (0.0, 0.10, 0.20, 0.30, 0.45)

    fig, axes = plt.subplots(1, len(rhos), figsize=(12.6, 3.5))
    for ax, rho in zip(axes, rhos):
        kept = set(nodes) - {nodes[i] for i in order[:int(round(rho * len(nodes)))]}
        H = G.subgraph(kept)
        giant = max(nx.connected_components(H), key=len) if H.number_of_nodes() else set()
        rest, core = [], []
        for u, v in H.edges():
            (core if u in giant and v in giant else rest).append((pos[u], pos[v]))
        if rest:
            ax.add_collection(LineCollection(rest, linewidths=.5, colors=SAGE))
        if core:
            ax.add_collection(LineCollection(core, linewidths=.75, colors=TEAL))
        frac = len(giant) / len(nodes)
        ax.autoscale(); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title("%.0f%% removed\nconnected  %.0f%%"
                     % (100 * rho, 100 * frac), fontsize=17, color=DEEP,
                     linespacing=1.5)
    fig.tight_layout(w_pad=1.5)
    save(fig, "board_montage.png")


def save(fig, name):
    path = os.path.join(FIGS, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    from PIL import Image
    print("   %-26s %s" % (name, Image.open(path).size))


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    print("[1] predictors"); fig_predictors()
    print("[2] loops");      fig_loops()
    print("[3] geometry");   fig_geometry()
    print("[4] collapse curve + montage (re-running the engine on one leaf)")
    fig_collapse_and_montage()
    print("done")
