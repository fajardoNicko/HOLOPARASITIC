"""
viz.py — figures for the paper and the Science Talent Fair board.

  plot_network          the synthetic vascular network (Result 1)
  plot_sigmoid          GCC survival / collapse sigmoid with p_c  (HERO figure)
  plot_pc_heatmap       p_c over the (K_h, D) grid (Result 3)
  plot_collapse_montage static collapse sequence (board-safe, no video writer)
  animate_collapse      animated GCC collapse -> GIF (falls back to montage)

Uses the Agg backend so everything renders head-less on the team's laptops.
"""

from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

import config
from . import network


# ----------------------------------------------------------------------------
def _ensure(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    return path


def _segments(G, kept=None):
    """LineCollection segments + per-edge linewidths/colors. `kept` is an
    optional set of surviving node ids (both endpoints must survive)."""
    pos = {i: d["pos"] for i, d in G.nodes(data=True)}
    segs, widths, colors = [], [], []
    for u, v, d in G.edges(data=True):
        if kept is not None and (u not in kept or v not in kept):
            continue
        segs.append((pos[u], pos[v]))
        widths.append(0.3 + 6.0 * d["radius"] ** 1.5)
        colors.append("#8c4a2f" if d["kind"] == "anastomosis" else "#1f6f4a")
    return segs, widths, colors


# ----------------------------------------------------------------------------
def plot_network(G, path="figures/network.png", title=None, dpi=160):
    """Result 1 — the generated network. Anastomoses drawn in a contrasting hue."""
    segs, widths, colors = _segments(G)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.add_collection(LineCollection(segs, linewidths=widths, colors=colors,
                                     capstyle="round"))
    term = np.array([d["pos"] for _, d in G.nodes(data=True)
                     if d["kind"] == "terminal"])
    if len(term):
        ax.scatter(term[:, 0], term[:, 1], s=4, c="#2e7d32", zorder=3)
    ax.autoscale(); ax.set_aspect("equal"); ax.axis("off")
    s = network.summary(G)
    ax.set_title(title or f"Synthetic vascular network "
                 f"(N={s['n_nodes']}, loops={s['n_cycles']})")
    fig.tight_layout(); fig.savefig(_ensure(path), dpi=dpi); plt.close(fig)
    return path


# ----------------------------------------------------------------------------
def plot_sigmoid(res, path="figures/sigmoid.png", dpi=160):
    """HERO figure — P(collapse) sigmoid + GCC survival, with p_c marked."""
    rhos = res["rhos"]
    fig, ax = plt.subplots(figsize=(8, 5.5))

    ax.scatter(rhos, res["p_collapse"], s=22, color="#c1121f", zorder=3,
               label="P(collapse) — Monte Carlo")
    if res.get("model") is not None:
        xs = np.linspace(0, 1, 400)
        ys = res["model"].predict_proba(xs.reshape(-1, 1))[:, 1]
        ax.plot(xs, ys, color="#c1121f", lw=2, label="logistic fit")
    ax.plot(rhos, res["gcc_fraction"], color="#1f6f4a", lw=2, marker="o",
            ms=3, label="GCC fraction (survival)")
    ax.axhline(0.5, color="0.6", ls=":", lw=1)

    pc = res["p_c"]
    if np.isfinite(pc):
        ax.axvline(pc, color="black", ls="--", lw=1.6)
        label = f"$p_c$ = {pc:.3f}"
        if "ci" in res and np.isfinite(res["ci"]["ci95"][0]):
            lo, hi = res["ci"]["ci95"]
            ax.axvspan(lo, hi, color="black", alpha=0.08)
            label += f"\n95% CI [{lo:.3f}, {hi:.3f}]"
        ax.text(pc + 0.02, 0.12, label, fontsize=11)

    ax.set_xlabel(r"haustorial density $\rho$  (fraction removed)")
    ax.set_ylabel("probability / fraction")
    ax.set_xlim(0, 1); ax.set_ylim(-0.02, 1.02)
    ax.set_title(f"Vascular percolation threshold "
                 f"({res['mode']} mode, N={res['n_nodes']}, "
                 f"{res['n_trials']:,} trials)")
    ax.legend(loc="center left"); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(_ensure(path), dpi=dpi); plt.close(fig)
    return path


# ----------------------------------------------------------------------------
def plot_pc_heatmap(surface, path="figures/pc_heatmap.png", dpi=160):
    """Result 3 — p_c over (K_h, D)."""
    D, kh, pc = surface["D"], surface["k_h"], surface["pc"]
    order = np.argsort(D)
    D_s, pc_s = D[order], pc[order, :]

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    im = ax.pcolormesh(kh, D_s, pc_s, shading="auto", cmap="viridis")
    fig.colorbar(im, ax=ax, label=r"percolation threshold $p_c$")
    ax.set_xlabel(r"haustorial sink strength $K_h$")
    ax.set_ylabel("fractal dimension $D$")
    ax.set_title(r"$p_c$ surface: stronger sinks & sparser networks collapse sooner")
    for i, d in enumerate(D_s):
        for j, k in enumerate(kh):
            if np.isfinite(pc_s[i, j]):
                ax.text(k, d, f"{pc_s[i, j]:.2f}", ha="center", va="center",
                        fontsize=8, color="white")
    fig.tight_layout(); fig.savefig(_ensure(path), dpi=dpi); plt.close(fig)
    return path


# ----------------------------------------------------------------------------
def _cumulative_kept(G, rho, seed=0):
    """Deterministic node set surviving removal fraction rho (for animation)."""
    rng = config.new_rng(seed)
    nodes = list(G.nodes)
    order = rng.permutation(len(nodes))
    n_remove = int(round(rho * len(nodes)))
    removed = {nodes[i] for i in order[:n_remove]}
    return set(nodes) - removed


def plot_collapse_montage(G, path="figures/collapse_montage.png",
                          rhos=(0.0, 0.2, 0.4, 0.6, 0.8), dpi=150):
    """Board-safe static collapse sequence (no video writer needed)."""
    fig, axes = plt.subplots(1, len(rhos), figsize=(3.0 * len(rhos), 3.2))
    for ax, rho in zip(np.atleast_1d(axes), rhos):
        kept = _cumulative_kept(G, rho)
        segs, widths, colors = _segments(G, kept=kept)
        if segs:
            ax.add_collection(LineCollection(segs, linewidths=widths,
                                             colors=colors))
        ax.autoscale(); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(rf"$\rho$={rho:.2f}", fontsize=11)
    fig.suptitle("Progressive vascular fragmentation under haustorial load")
    fig.tight_layout(); fig.savefig(_ensure(path), dpi=dpi); plt.close(fig)
    return path


def plot_parasite_comparison(results, path="figures/parasites.png", dpi=160):
    """Bar chart of p_c across parasite profiles (generality result)."""
    from matplotlib.patches import Patch
    results = sorted(results, key=lambda r: r["p_c"])
    names = [r["name"] for r in results]
    pcs = [r["p_c"] for r in results]
    colors = ["#1f6f4a" if r["kind"] == "holoparasite" else "#8c4a2f"
              for r in results]

    # 95% bootstrap CI error bars (if present)
    yerr = None
    if all("ci_lo" in r and np.isfinite(r["ci_lo"]) for r in results):
        yerr = [[pcs[i] - r["ci_lo"] for i, r in enumerate(results)],
                [r["ci_hi"] - pcs[i] for i, r in enumerate(results)]]

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.bar(range(len(names)), pcs, color=colors, width=0.62,
           yerr=yerr, capsize=5, ecolor="black")
    for i, r in enumerate(results):
        top = r.get("ci_hi", pcs[i])
        ax.text(i, top + 0.008, f"{pcs[i]:.2f}", ha="center", fontsize=11,
                fontweight="bold")
        ax.text(i, 0.012, r["attachment"].replace("_", "-")
                + f"  (eff={r['efficiency']})",
                ha="center", va="bottom", fontsize=8, color="white", rotation=90)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=12, ha="right", fontsize=9)
    ax.set_ylabel(r"vascular percolation threshold $p_c$")
    ax.set_title("Generality: collapse threshold across parasitic weeds\n"
                 "(lower $p_c$ = host collapses sooner = more devastating)")
    ax.legend(handles=[Patch(color="#1f6f4a", label="holoparasite (strong sink)"),
                       Patch(color="#8c4a2f", label="hemiparasite (moderate)")],
              loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(_ensure(path), dpi=dpi); plt.close(fig)
    return path


def animate_collapse(G, res=None, path="figures/collapse.gif",
                     n_frames=40, fps=10, dpi=120):
    """Animated GCC collapse beside the filling-in sigmoid. Saves a GIF if a
    Pillow writer is available; otherwise falls back to the static montage."""
    import matplotlib.animation as manim

    fig, (axn, axs) = plt.subplots(1, 2, figsize=(11, 5.2),
                                   gridspec_kw={"width_ratios": [1, 1]})
    pos = {i: d["pos"] for i, d in G.nodes(data=True)}
    xs = np.array([p[0] for p in pos.values()])
    ys = np.array([p[1] for p in pos.values()])
    axn.set_xlim(xs.min(), xs.max()); axn.set_ylim(ys.min(), ys.max())
    axn.set_aspect("equal"); axn.axis("off")

    lc = LineCollection([], colors="#1f6f4a")
    axn.add_collection(lc)

    rhos_anim = np.linspace(0, 1, n_frames)
    if res is not None:
        axs.scatter(res["rhos"], res["p_collapse"], s=14, color="#c1121f")
        if np.isfinite(res.get("p_c", np.nan)):
            axs.axvline(res["p_c"], color="black", ls="--", lw=1.4)
    axs.set_xlim(0, 1); axs.set_ylim(0, 1.02)
    axs.set_xlabel(r"$\rho$"); axs.set_ylabel("GCC fraction")
    axs.grid(alpha=0.25)
    (curve,) = axs.plot([], [], color="#1f6f4a", lw=2)
    gcc_hist_x, gcc_hist_y = [], []

    adj, nodes = network.to_csr(G)
    n = adj.shape[0]
    from scipy.sparse.csgraph import connected_components

    def frame(k):
        rho = rhos_anim[k]
        kept = _cumulative_kept(G, rho)
        segs, widths, colors = _segments(G, kept=kept)
        lc.set_segments(segs); lc.set_linewidths(widths); lc.set_color(colors)
        idx = np.array([i for i, nd in enumerate(nodes) if nd in kept], int)
        if idx.size:
            sub = adj[idx][:, idx]
            _, labels = connected_components(sub, directed=False)
            gcc = int(np.bincount(labels).max()) / n
        else:
            gcc = 0.0
        gcc_hist_x.append(rho); gcc_hist_y.append(gcc)
        curve.set_data(gcc_hist_x, gcc_hist_y)
        axn.set_title(rf"$\rho$={rho:.2f}   GCC={gcc:.2f}")
        return lc, curve

    anim = manim.FuncAnimation(fig, frame, frames=n_frames, blit=False)
    try:
        anim.save(_ensure(path), writer=manim.PillowWriter(fps=fps), dpi=dpi)
        plt.close(fig)
        return path
    except Exception as e:                       # no Pillow / writer available
        plt.close(fig)
        print(f"  [animate] GIF writer unavailable ({e}); using static montage")
        return plot_collapse_montage(G, path=path.replace(".gif", "_montage.png"))
