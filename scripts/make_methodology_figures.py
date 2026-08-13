r"""
make_methodology_figures.py — generate the DATA-DRIVEN figures for Chapter III.

These six figures use the real pipeline (real Matos leaf, calibrated synthetic
generator, real box-counting, real percolation) so nothing in the methodology is
a mock-up. The purely schematic figures (pipeline, dataset, solver, stats tree)
are drawn as vector diagrams in METHODOLOGY_FIGURES.html instead.

Outputs (figures/methodology/):
  fig04_real_network.png       largest real leaf as a graph, annotated
  fig05_synthetic_network.png  calibrated synthetic network, annotated
  fig07_boxcounting.png        box-counting at 3 scales + regression
  fig09_attack_modes.png       random / degree / betweenness removal
  fig10_gcc.png                giant component before vs after attack
  fig11_montecarlo.png         collapse-probability sigmoid, p_c marked
"""

import os
import sys
import glob
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle

import config
from holoparasitic import realleaf, network, fractal, percolation, calibrate as cal

FIG = os.path.join(ROOT, "figures", "methodology")
os.makedirs(FIG, exist_ok=True)
INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#3B8EA5"; VEIN = "#7A4E2D"


def _draw_edges(G, ax, color_by="radius", lw_scale=1.0, edgecolor=None):
    pos = {n: G.nodes[n]["pos"] for n in G.nodes}
    segs, rad, kind = [], [], []
    for u, v, d in G.edges(data=True):
        segs.append([pos[u], pos[v]]); rad.append(d.get("radius", 0.01))
        kind.append(d.get("kind", "axial"))
    segs = np.array(segs); rad = np.array(rad, float)
    rmax = rad.max() if rad.size else 1.0
    lw = lw_scale * (0.15 + 2.4 * (rad / rmax) ** 0.5)
    if edgecolor is not None:
        cols = edgecolor
    elif color_by == "kind":
        cols = np.where(np.array(kind) == "anastomosis", BLUE, VEIN)
    else:
        r = np.log(rad + 1e-9); rng = r.max() - r.min() or 1.0
        cols = plt.cm.copper_r(0.12 + 0.82 * (r - r.min()) / rng)
    ax.add_collection(LineCollection(segs, linewidths=lw, colors=cols,
                                     capstyle="round"))
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs), max(xs)); ax.set_ylim(min(ys), max(ys))
    ax.set_aspect("equal"); ax.axis("off")
    return pos


def fig04_real():
    d = os.path.join(ROOT, "UCBG_venation_form_data",
                     "UCBG_venation_form_data", "Cis_ant")
    n = glob.glob(d + "/*_nodes.csv")[0]; v = glob.glob(d + "/*_veins.csv")[0]
    t0 = time.time(); G = realleaf.load_matos(n, v, name="Cis_ant")
    N, E = G.number_of_nodes(), G.number_of_edges()
    print(f"  fig04: Cis_ant N={N:,} E={E:,} loaded {time.time()-t0:.0f}s")
    fig, ax = plt.subplots(figsize=(8.2, 8.6))
    pos = _draw_edges(G, ax)
    rt = G.graph.get("root")
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if rt in pos:
        ax.plot(*pos[rt], "o", ms=13, mfc=ACCENT, mec="white", mew=1.5, zorder=6)
        ax.annotate("Hydraulic source\n(widest vein)", pos[rt],
                    xytext=(pos[rt][0]+(x1-x0)*0.12, pos[rt][1]+(y1-y0)*0.06),
                    fontsize=10, fontweight="bold", color=ACCENT,
                    arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.6))
    # representative structural annotations
    ax.annotate("Midrib / major veins\n(thickest, dark)",
                (x0+(x1-x0)*0.5, y0+(y1-y0)*0.5),
                xytext=(x0+(x1-x0)*0.02, y1-(y1-y0)*0.06), fontsize=10,
                color=VEIN, fontweight="bold")
    ax.annotate("Secondary veins",
                (x0+(x1-x0)*0.7, y0+(y1-y0)*0.7),
                xytext=(x1-(x1-x0)*0.30, y1-(y1-y0)*0.05), fontsize=10,
                color="#5B7B8A", fontweight="bold")
    ax.annotate("Reticulate loops\n(areole mesh)",
                (x0+(x1-x0)*0.55, y0+(y1-y0)*0.30),
                xytext=(x1-(x1-x0)*0.34, y0+(y1-y0)*0.02), fontsize=10,
                color=BLUE, fontweight="bold")
    ax.set_title(f"Real host-leaf network — Cistus (largest in cohort)\n"
                 f"{N:,} junctions · {E:,} veins · "
                 f"$\\langle k\\rangle$={2*E/N:.2f} · D={fractal.fractal_dimension(G):.2f}",
                 fontsize=12, color=INK)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig04_real_network.png", dpi=200,
                                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig05_synthetic():
    G = network.generate(cal.calibrated_base(generations=10))
    N, E = G.number_of_nodes(), G.number_of_edges()
    br = set(nx.bridges(G)) if nx.is_connected(G) else set()
    loop = 1 - len(br) / E
    fig, ax = plt.subplots(figsize=(8.2, 8.6))
    pos = _draw_edges(G, ax, color_by="kind")
    rt = G.graph.get("root", 0)
    if rt in pos:
        ax.plot(*pos[rt], "o", ms=13, mfc=ACCENT, mec="white", mew=1.5, zorder=6)
        ax.annotate("Root node (source)", pos[rt],
                    xytext=(pos[rt][0], pos[rt][1]+0.6), fontsize=10,
                    fontweight="bold", color=ACCENT, ha="center",
                    arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.6))
    ax.plot([], [], color=VEIN, lw=3, label="Axial veins (major branches)")
    ax.plot([], [], color=BLUE, lw=2, label="Anastomoses (loops)")
    ax.legend(loc="lower right", fontsize=9, framealpha=.9)
    ax.set_title("Calibrated synthetic network (mesh reticulation)\n"
                 f"$\\langle k\\rangle$={2*E/N:.2f} (controlled) · "
                 f"D={fractal.fractal_dimension(G):.2f} (controlled) · "
                 f"loop={loop:.2f} · topology preserved, leaf shape not",
                 fontsize=12, color=INK)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig05_synthetic_network.png",
                                    dpi=200, bbox_inches="tight",
                                    facecolor="white")
    plt.close(fig)


def fig07_boxcounting():
    # a moderate synthetic network so the grid overlay is legible
    G = network.generate(config.NetworkParams(generations=8, reticulation=0.6,
                                              seed=1))
    pts = fractal._edge_point_cloud(G)
    lo = pts.min(0); span = (pts.max(0) - lo); span[span == 0] = 1
    unit = (pts - lo) / span.max()

    # visible grids for the didactic panels (coarse enough to SEE the boxes)
    vis_grids = [6, 12, 24]
    fig, axes = plt.subplots(1, 4, figsize=(15.5, 4.2))
    for ax, k in zip(axes[:3], vis_grids):
        cells = np.floor(np.clip(unit, 0, 1-1e-9) * k).astype(int)
        occ = set(map(tuple, cells))
        for (cx, cy) in occ:
            ax.add_patch(Rectangle((cx/k, cy/k), 1/k, 1/k, fill=True,
                                   facecolor=BLUE, alpha=.30, edgecolor=BLUE,
                                   lw=.5))
        for g in range(k+1):                       # faint grid lines
            ax.axvline(g/k, color="#C9D5DA", lw=.4, zorder=0)
            ax.axhline(g/k, color="#C9D5DA", lw=.4, zorder=0)
        ax.scatter(unit[:, 0], unit[:, 1], s=0.5, c=VEIN, alpha=.6, zorder=3)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"grid {k}×{k}\n{len(occ)} occupied boxes", fontsize=10)

    # regression over the FULL scaling range (proper box-counting fit)
    res = fractal.box_counting_from_points(pts)
    ks = res["sizes"].astype(float); counts = res["counts"]
    slope, intercept = res["fit"]                  # slope = D, on log(k) axis
    ax = axes[3]
    x = np.log(ks); y = np.log(counts)             # log(1/box size)=log(k)
    ax.scatter(x, y, c=INK, s=28, zorder=3)
    xs = np.linspace(x.min(), x.max(), 20)
    ax.plot(xs, intercept + slope*xs, "--", color=ACCENT, lw=2,
            label=f"slope = D = {slope:.3f}")
    ax.set_xlabel("log (1 / box size)"); ax.set_ylabel("log (occupied boxes)")
    ax.set_title("Regression → fractal dimension", fontsize=10)
    ax.legend(fontsize=10, loc="upper left"); ax.grid(alpha=.25)
    fig.suptitle("Box-counting estimation of fractal dimension D",
                 fontsize=13, color=INK, y=1.03)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig07_boxcounting.png", dpi=200,
                                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig09_attack():
    # small legible network
    G = network.generate(config.NetworkParams(generations=6, reticulation=0.7,
                                              seed=3))
    nodes = list(G.nodes); pos = {n: G.nodes[n]["pos"] for n in nodes}
    frac = 0.25; nrem = int(frac*len(nodes))
    rng = np.random.default_rng(0)
    rand = set(rng.choice(nodes, nrem, replace=False))
    deg = set(sorted(nodes, key=lambda n: G.degree(n), reverse=True)[:nrem])
    bc = nx.betweenness_centrality(G, k=min(120, len(nodes)), seed=1)
    btw = set(sorted(nodes, key=lambda n: bc[n], reverse=True)[:nrem])

    fig, axes = plt.subplots(1, 4, figsize=(15.5, 4.3))
    titles = ["Original network", f"Random ({int(frac*100)}%)",
              "Degree-targeted", "Betweenness-targeted"]
    removed_sets = [set(), rand, deg, btw]
    for ax, title, rem in zip(axes, titles, removed_sets):
        segs = [[pos[u], pos[v]] for u, v in G.edges()
                if u not in rem and v not in rem]
        ax.add_collection(LineCollection(segs, colors="#9AA7AE", lw=0.8))
        keep = [n for n in nodes if n not in rem]
        ax.scatter([pos[n][0] for n in keep], [pos[n][1] for n in keep],
                   s=6, c=INK, zorder=3)
        if rem:
            ax.scatter([pos[n][0] for n in rem], [pos[n][1] for n in rem],
                       s=26, c=ACCENT, marker="x", zorder=4, linewidths=1.4)
        xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
        ax.set_xlim(min(xs), max(xs)); ax.set_ylim(min(ys), max(ys))
        ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=11)
    fig.suptitle("Attack modes — which vessels are removed (×, red)",
                 fontsize=13, color=INK, y=1.02)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig09_attack_modes.png", dpi=200,
                                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig10_gcc():
    G = network.generate(config.NetworkParams(generations=6, reticulation=0.5,
                                              seed=5))
    nodes = list(G.nodes); pos = {n: G.nodes[n]["pos"] for n in nodes}
    rng = np.random.default_rng(2)
    rem = set(rng.choice(nodes, int(0.35*len(nodes)), replace=False))
    H = G.subgraph([n for n in nodes if n not in rem]).copy()
    comps = sorted(nx.connected_components(H), key=len, reverse=True)
    gcc = comps[0] if comps else set()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.4))
    # before: whole network, GCC = all
    ax = axes[0]
    ax.add_collection(LineCollection([[pos[u], pos[v]] for u, v in G.edges()],
                                     colors=BLUE, lw=1.0))
    ax.scatter([pos[n][0] for n in nodes], [pos[n][1] for n in nodes], s=8,
               c=BLUE, zorder=3)
    ax.set_title(f"Before attack\ngiant component = 100% ({len(nodes)} nodes)",
                 fontsize=11)
    # after: fragments gray, GCC colored
    ax = axes[1]
    ax.add_collection(LineCollection([[pos[u], pos[v]] for u, v in H.edges()],
                                     colors="#C4CDD2", lw=0.8))
    gedges = [[pos[u], pos[v]] for u, v in H.edges() if u in gcc and v in gcc]
    ax.add_collection(LineCollection(gedges, colors=ACCENT, lw=1.3, zorder=3))
    other = [n for n in H.nodes if n not in gcc]
    ax.scatter([pos[n][0] for n in other], [pos[n][1] for n in other], s=7,
               c="#C4CDD2", zorder=2)
    ax.scatter([pos[n][0] for n in gcc], [pos[n][1] for n in gcc], s=10,
               c=ACCENT, zorder=4)
    ax.set_title(f"After 35% removal\nlargest surviving component = "
                 f"{len(gcc)/len(nodes)*100:.0f}% (red)", fontsize=11)
    for ax in axes:
        xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
        ax.set_xlim(min(xs), max(xs)); ax.set_ylim(min(ys), max(ys))
        ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("The giant connected component (GCC) — what percolation tracks",
                 fontsize=13, color=INK, y=1.0)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig10_gcc.png", dpi=200,
                                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig11_montecarlo():
    G = network.generate(config.NetworkParams(generations=8, reticulation=0.6,
                                              seed=1))
    pp = config.PercolationParams(mode="random", n_trials=40*400, n_densities=40)
    res = percolation.density_response(G, pp, rho_max=0.6)
    fit = percolation.fit_pc(res["X"], res["y"])
    pc = fit["p_c"]
    rhos, pcol = res["rhos"], res["p_collapse"]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.scatter(rhos, pcol, s=34, c=INK, zorder=3, label="Monte-Carlo trials")
    xs = np.linspace(0, rhos.max(), 200)
    w, b = fit["coef"], fit["intercept"]
    ax.plot(xs, 1/(1+np.exp(-(w*xs+b))), color=BLUE, lw=2.3,
            label="logistic fit")
    ax.axvline(pc, color=ACCENT, ls="--", lw=2)
    ax.axhline(0.5, color="#AAB4BA", ls=":", lw=1)
    ax.annotate(f"$p_c$ = {pc:.3f}", (pc, 0.5), xytext=(pc+0.06, 0.35),
                fontsize=13, fontweight="bold", color=ACCENT,
                arrowprops=dict(arrowstyle="->", color=ACCENT))
    ax.set_xlabel("Fraction of vessels removed  ρ")
    ax.set_ylabel("P(giant component collapse)")
    ax.set_title(f"Monte-Carlo collapse probability → threshold $p_c$\n"
                 f"{res['n_trials']:,} trials", fontsize=12, color=INK)
    ax.legend(fontsize=10); ax.grid(alpha=.25); ax.set_ylim(-0.03, 1.03)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig11_montecarlo.png", dpi=200,
                                    bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass
    jobs = [("fig05", fig05_synthetic), ("fig07", fig07_boxcounting),
            ("fig09", fig09_attack), ("fig10", fig10_gcc),
            ("fig11", fig11_montecarlo), ("fig04", fig04_real)]
    for name, fn in jobs:
        t0 = time.time()
        try:
            fn(); print(f"[ok] {name}  ({time.time()-t0:.0f}s)")
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"[FAIL] {name}: {e}")
    print("done ->", FIG)
