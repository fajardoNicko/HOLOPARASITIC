# -*- coding: utf-8 -*-
r"""
make_potential_relief.py -- 3D water-potential relief with a haustorial sink well.

The height/colour of the surface is the water potential psi (MPa) solved by the
real Kirchhoff HydraulicSolver on a synthetic leaf network. Left panel: healthy
host (source ridge at psi=0 sloping down to the transpiring margins). Right
panel: one haustorium attached mid-lamina -- a leak conductance K_h to the low
parasite reservoir -- which pulls a visible funnel/well into the field.

Output: figures/methodology/fig_hydraulic_relief3d.png  (landscape)
ASCII-only stdout (Windows cp1252 safety).
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from scipy.interpolate import griddata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from holoparasitic import network, hydraulics

FIG = os.path.join(ROOT, "figures", "methodology")
os.makedirs(FIG, exist_ok=True)

INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#3B8EA5"; VEIN = "#7A4E2D"
# water map: high psi (well-watered) = teal, mid = cream, low psi (tension) = orange
PSI_CMAP = LinearSegmentedColormap.from_list(
    "psi", [(0.00, ACCENT), (0.45, "#EFE1CF"), (0.75, BLUE), (1.0, "#1F5F6E")])


def _xy_psi(G, solver, psi):
    pos = np.array([G.nodes[n]["pos"] for n in solver.nodes], float)
    return pos[:, 0], pos[:, 1], np.asarray(psi, float)


def _grid(x, y, z, n=150, zmin=None):
    xi = np.linspace(x.min(), x.max(), n)
    yi = np.linspace(y.min(), y.max(), n)
    X, Y = np.meshgrid(xi, yi)
    # linear -> no cubic overshoot/ringing around the sharp sink well
    Z = griddata((x, y), z, (X, Y), method="linear")
    if zmin is not None:
        Z = np.clip(Z, zmin, 0.0)
    return X, Y, Z


def _panel(ax, X, Y, Z, norm, title, source_xy=None, sink_xy=None, sink_z=None):
    ax.plot_surface(X, Y, Z, cmap=PSI_CMAP, norm=norm, rcount=140, ccount=140,
                    linewidth=0, antialiased=True, alpha=0.97)
    # faint contour footprint on the floor
    zfloor = norm.vmin - 0.15
    try:
        ax.contourf(X, Y, Z, zdir="z", offset=zfloor, levels=14,
                    cmap=PSI_CMAP, norm=norm, alpha=0.35)
    except Exception:
        pass
    if source_xy is not None:
        ax.scatter([source_xy[0]], [source_xy[1]], [0.0], color=INK, s=55,
                   depthshade=False, zorder=6)
        ax.text(source_xy[0], source_xy[1], 0.35, "source  psi = 0",
                color=INK, fontsize=9, fontweight="bold")
    if sink_xy is not None:
        ax.scatter([sink_xy[0]], [sink_xy[1]], [sink_z], color=ACCENT, s=60,
                   depthshade=False, zorder=7)
        ax.text(sink_xy[0], sink_xy[1], sink_z - 0.45, "haustorial\nsink",
                color=ACCENT, fontsize=9, fontweight="bold", ha="center")
    ax.set_zlim(zfloor, 0.15)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_zlabel("water potential  psi  (MPa)", fontsize=9, color=INK,
                  labelpad=-6)
    ax.tick_params(axis="z", labelsize=8, colors=INK, pad=-1)
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=-2)
    ax.view_init(elev=34, azim=-58)
    ax.set_box_aspect((1, 1, 0.55))
    # lighten panes
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.pane.set_facecolor((1, 1, 1, 0))
        pane.pane.set_edgecolor((0.8, 0.8, 0.8, 0.4))
    ax.grid(False)


def main():
    rng = np.random.default_rng(7)
    G = network.generate()
    solver, psi0 = hydraulics.baseline_potentials(G)
    x, y, z0 = _xy_psi(G, solver, psi0)

    # choose a haustorium: interior node nearest the lamina centroid
    cx, cy = x.mean(), y.mean()
    fixed = {solver.root, *solver.terminals}
    cand = [(i, n) for i, n in enumerate(solver.nodes) if n not in fixed]
    ci = min(cand, key=lambda t: (x[t[0]] - cx) ** 2 + (y[t[0]] - cy) ** 2)
    h_idx, h_node = ci
    # haustorial contact patch: the node + up to 2-hop vein neighbours, so the
    # well has physical width instead of being a single-node needle
    patch, frontier = {h_node}, {h_node}
    for _ in range(2):
        nxt = set()
        for u in frontier:
            nxt |= set(G.neighbors(u))
        patch |= nxt
        frontier = nxt
    patch = [n for n in patch if n not in fixed][:16]
    psi1 = solver.solve(haustoria={n: 3.0 for n in patch}, relative=True)
    z1 = np.asarray(psi1, float)

    root_i = solver.index[solver.root]
    src_xy = (x[root_i], y[root_i])
    sink_xy = (x[h_idx], y[h_idx])

    vmin = min(z0.min(), z1.min())
    norm = Normalize(vmin=vmin, vmax=0.0)

    X0, Y0, Z0 = _grid(x, y, z0, zmin=vmin)
    X1, Y1, Z1 = _grid(x, y, z1, zmin=vmin)

    fig = plt.figure(figsize=(16, 7))
    fig.patch.set_facecolor("white")
    ax0 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1 = fig.add_subplot(1, 2, 2, projection="3d")
    _panel(ax0, X0, Y0, Z0, norm, "Healthy host", source_xy=src_xy)
    _panel(ax1, X1, Y1, Z1, norm, "With haustorial sink", source_xy=src_xy,
           sink_xy=sink_xy, sink_z=float(z1[h_idx]))

    sm = plt.cm.ScalarMappable(cmap=PSI_CMAP, norm=norm)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=[ax0, ax1], shrink=0.55, aspect=28, pad=0.02)
    cb.set_label("water potential  psi  (MPa)", fontsize=10, color=INK)
    cb.ax.tick_params(labelsize=8, colors=INK)

    fig.suptitle("Water-potential field over the leaf network: the haustorial "
                 "sink draws a well into the hydraulic surface",
                 fontsize=12.5, color=INK, y=0.97)

    path = os.path.join(FIG, "fig_hydraulic_relief3d.png")
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.2,
                facecolor="white")
    plt.close(fig)
    print("baseline psi range: [%.3f, %.3f]" % (z0.min(), z0.max()))
    print("sink node psi: %.3f (baseline %.3f)" % (z1[h_idx], z0[h_idx]))
    print("SAVED:", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
