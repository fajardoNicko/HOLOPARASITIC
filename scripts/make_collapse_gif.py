# -*- coding: utf-8 -*-
r"""
make_collapse_gif.py -- the fragmentation animation (deck slide 5).

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_collapse_gif.py
    ... --species Tas_lan --frames 60 --dpi 100

Replaces the 2026-07 figures/collapse.gif, which was drawn on the synthetic
calibrated mesh and carried the pre-retitle caption "under haustorial load".
Two things are different here.

First, the network is a real leaf from the analysis cohort rather than a
synthetic mesh. On a slide whose job is to make percolation intuitive, a traced
leaf is doing the same explanatory work while also being the object the study
actually measures.

Second, and the reason the old GIF undersold the result: every surviving vein
was drawn in one colour, so the eye read progressive thinning. What the study
claims is not thinning but fragmentation, so here the giant connected component
is drawn in one colour and everything that has broken away from it in another.
The moment the network stops being one object is then visible rather than
inferred, which is the entire point of the slide.

Removal is nested -- one seeded permutation, longer and longer prefixes -- so
nodes only ever leave, and the sequence is a genuine sweep rather than a series
of unrelated draws.

Writes figures/collapse.gif and prints the frames and the realised threshold.
ASCII-only stdout.
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manim
from matplotlib.collections import LineCollection
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from holoparasitic import realleaf

DATA_DIR = os.path.join(ROOT, "UCBG_venation_form_data",
                        "UCBG_venation_form_data")
LOCALITY = os.path.join(ROOT, "data", "criterion_and_locality.csv")
OUT = os.path.join(ROOT, "figures", "collapse.gif")

# Deck palette (PPT_BUILD_GUIDE.pdf section 1).
INK = "#1A1D21"
PAPER = "#FAFAF7"
VEIN = "#2E7D5B"
LOSS = "#C1462F"
MUTED = "#6B7280"
RULE = "#D9D9D2"

FRAGMENT = "#C9C9C2"     # detached from the giant component
RHO_MAX = 0.55           # sweep past the threshold, not all the way to 1.0
COHORT_MEDIAN_PC = 0.1998


def pick_species(preferred=None):
    """Choose a cohort leaf: small enough to animate, threshold near the median.

    Animating a 300,000-node network is neither feasible nor legible, so the
    candidate set is capped by size; among those the one whose own threshold
    sits closest to the cohort median is the least misleading choice, since the
    slide is showing a representative collapse rather than a specific species.
    """
    rows = []
    with open(LOCALITY, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append((row["species"], int(row["N"]), float(row["pc_gcc"])))
    if preferred:
        for spp, n, pc in rows:
            if spp == preferred:
                return spp, n, pc
        raise SystemExit("ERROR: %s is not in the percolation cohort."
                         % preferred)
    small = [r for r in rows if r[1] <= 2500]
    if not small:
        raise SystemExit("ERROR: no cohort network small enough to animate.")
    return min(small, key=lambda r: abs(r[2] - COHORT_MEDIAN_PC))


def load_graph(species):
    for spp, nodes_csv, veins_csv in realleaf.find_leaf_pairs(DATA_DIR):
        if spp == species:
            return realleaf.load_matos(nodes_csv, veins_csv, name=species)
    raise SystemExit("ERROR: no CSV pair found for %s under %s"
                     % (species, os.path.relpath(DATA_DIR, ROOT)))


def prepare(G):
    """Flatten the graph into arrays the frame function can index cheaply."""
    nodes = list(G.nodes)
    index = {nd: i for i, nd in enumerate(nodes)}
    pos = np.array([G.nodes[nd]["pos"][:2] for nd in nodes], float)

    # Traced crop windows are usually taller than wide, which leaves a thin
    # column of leaf in a wide panel. The panel is a schematic, so quarter-turn
    # it to fill the space; nothing downstream depends on the orientation.
    span = pos.max(axis=0) - pos.min(axis=0)
    if span[1] > span[0]:
        pos = pos[:, ::-1]

    edges = np.array([(index[u], index[v]) for u, v in G.edges], int)
    segments = np.stack([pos[edges[:, 0]], pos[edges[:, 1]]], axis=1)

    n = len(nodes)
    data = np.ones(len(edges))
    adj = coo_matrix((data, (edges[:, 0], edges[:, 1])), shape=(n, n)).tocsr()
    adj = adj + adj.T
    return pos, edges, segments, adj, n


def gcc_membership(adj, alive):
    """Boolean mask of the nodes in the largest surviving component."""
    idx = np.flatnonzero(alive)
    member = np.zeros(alive.shape, bool)
    if idx.size == 0:
        return member, 0.0
    _, labels = connected_components(adj[idx][:, idx], directed=False)
    counts = np.bincount(labels)
    biggest = int(counts.argmax())
    member[idx[labels == biggest]] = True
    return member, counts[biggest] / alive.size


def build(species, n_nodes, pc, frames, fps, dpi, out):
    G = load_graph(species)
    pos, edges, segments, adj, n = prepare(G)

    rng = np.random.default_rng(0)
    order = rng.permutation(n)          # one permutation, nested prefixes
    rhos = np.linspace(0.0, RHO_MAX, frames)

    fig, (axn, axc) = plt.subplots(
        1, 2, figsize=(11.0, 4.9), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.patch.set_facecolor(PAPER)
    for ax in (axn, axc):
        ax.set_facecolor(PAPER)

    axn.set_xlim(pos[:, 0].min(), pos[:, 0].max())
    axn.set_ylim(pos[:, 1].min(), pos[:, 1].max())
    axn.set_aspect("equal")
    axn.axis("off")
    lc = LineCollection(segments, linewidths=0.75)
    axn.add_collection(lc)

    axc.set_xlim(0, RHO_MAX)
    axc.set_ylim(0, 1.02)
    axc.set_xlabel("fraction of junctions removed", fontsize=12, color=INK)
    axc.set_ylabel("largest component, share of survivors",
                   fontsize=12, color=INK)
    axc.tick_params(labelsize=11, colors=INK)
    axc.yaxis.grid(True, color=RULE, linewidth=0.8)
    axc.set_axisbelow(True)
    for side in ("top", "right"):
        axc.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axc.spines[side].set_color(RULE)

    axc.axhline(0.5, color=MUTED, ls=":", lw=1.3)
    axc.annotate("half size: the collapse criterion", xy=(RHO_MAX * 0.02, 0.52),
                 fontsize=10.5, color=MUTED, va="bottom")
    axc.axvline(pc, color=LOSS, ls="--", lw=1.5)
    axc.annotate("threshold %.4f" % pc, xy=(pc + 0.012, 0.965),
                 fontsize=11, color=LOSS, fontweight="bold", va="top")

    (trace,) = axc.plot([], [], color=VEIN, lw=2.4)
    hist_x, hist_y = [], []

    # The running status sits inside the network panel in axes coordinates.
    # As a Matplotlib title it was centred on a narrow axis and ran out over
    # the figure edge.
    status = axn.text(0.0, 1.02, "", transform=axn.transAxes, ha="left",
                      va="bottom", fontsize=13, color=INK)

    fig.suptitle("Connectivity does not decay. It shatters.",
                 fontsize=16, color=INK, x=0.5, y=0.985)
    fig.text(0.5, 0.012,
             "%s, %d junctions. Green is the largest connected component; "
             "grey has broken away from it." % (species, n),
             ha="center", fontsize=10.5, color=MUTED)

    def frame(k):
        rho = rhos[k]
        alive = np.ones(n, bool)
        alive[order[:int(round(rho * n))]] = False

        member, share = gcc_membership(adj, alive)
        both = alive[edges[:, 0]] & alive[edges[:, 1]]
        in_gcc = member[edges[:, 0]] & member[edges[:, 1]]

        colours = np.empty(len(edges), dtype=object)
        colours[:] = PAPER                       # removed: invisible
        colours[both] = FRAGMENT
        colours[in_gcc] = VEIN
        lc.set_color(list(colours))

        hist_x.append(rho)
        hist_y.append(share)
        trace.set_data(hist_x, hist_y)
        status.set_text("removed %.0f%%     largest component %.0f%% "
                        "of survivors" % (rho * 100, share * 100))
        return lc, trace, status

    # Hold on the intact network, then hold again on the shattered end state,
    # so the loop does not snap back before either has registered.
    fig.subplots_adjust(left=0.02, right=0.975, top=0.87, bottom=0.17,
                        wspace=0.16)

    sequence = [0] * max(1, fps // 2) + list(range(frames)) \
        + [frames - 1] * max(1, fps)
    anim = manim.FuncAnimation(fig, frame, frames=sequence, blit=False)
    anim.save(out, writer=manim.PillowWriter(fps=fps), dpi=dpi,
              savefig_kwargs={"facecolor": PAPER})
    plt.close(fig)
    return n, len(edges), len(sequence), hist_x, hist_y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--species", default=None,
                    help="cohort species code; default picks automatically")
    ap.add_argument("--frames", type=int, default=56)
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    species, n_nodes, pc = pick_species(args.species)
    print("network: %s  N=%d  threshold=%.4f  (cohort median %.4f)"
          % (species, n_nodes, pc, COHORT_MEDIAN_PC))

    n, m, total, xs, ys = build(species, n_nodes, pc, args.frames,
                                args.fps, args.dpi, args.out)

    below = [x for x, y in zip(xs, ys) if y < 0.5]
    print("wrote %s" % os.path.relpath(args.out, ROOT))
    print("  %d nodes, %d edges, %d frames at %d fps, dpi %d"
          % (n, m, total, args.fps, args.dpi))
    print("  size: %.2f MB" % (os.path.getsize(args.out) / 1e6))
    if below:
        print("  largest component first falls below half at removed fraction "
              "%.3f in this single realisation" % below[0])
    else:
        print("  largest component stayed above half over the swept range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
