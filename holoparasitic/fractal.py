"""
fractal.py  (Person A) — box-counting fractal dimension D of a network.

The drawn network (its edges, not just its nodes) is rasterised into points;
the number of occupied boxes N(eps) is counted across a range of box sizes eps.
For a fractal,  N(eps) ~ eps^(-D),  so D is the slope of log N vs log(1/eps).

Dicotyledonous crop venation is empirically D ~ 1.5-2.0; the generator's
`angle_jitter` knob moves the synthetic network across that range, which is how
the study sweeps D.
"""

from __future__ import annotations

import numpy as np
import networkx as nx


def _edge_point_cloud(G: nx.Graph, samples_per_unit: float = 4000.0,
                      max_points: int = 400_000) -> np.ndarray:
    """Sample points densely ALONG every edge (so thin branches register)."""
    pos = {i: np.asarray(d["pos"], float) for i, d in G.nodes(data=True)}
    chunks = []
    for u, v in G.edges():
        a, b = pos[u], pos[v]
        length = float(np.hypot(*(b - a)))
        n = max(2, int(length * samples_per_unit))
        t = np.linspace(0.0, 1.0, n)[:, None]
        chunks.append(a[None, :] * (1 - t) + b[None, :] * t)
    pts = np.vstack(chunks) if chunks else np.array([[0.0, 0.0]])
    if len(pts) > max_points:                      # subsample for speed
        idx = np.linspace(0, len(pts) - 1, max_points).astype(int)
        pts = pts[idx]
    return pts


def box_counting_dimension(G: nx.Graph, n_sizes: int = 12,
                           min_boxes: int = 16, max_boxes: int = 1024) -> dict:
    """Return {'D', 'sizes', 'counts', 'fit'} for network G.

    `D` is the fitted box-counting dimension; `sizes` are box counts per axis,
    `counts` the occupied-box tallies, `fit` the (slope, intercept) of the
    log-log regression (slope == D).

    The fit deliberately spans an intermediate-to-fine WINDOW of box sizes
    (default 16..1024 boxes per axis). The coarsest boxes are excluded because
    at a finite ~10^3-node network they sit in the finite-size-saturated regime
    (everything looks 2-D), which otherwise biases D upward and destroys the
    monotonic dependence on network morphology. Fitting the genuine scaling
    regime is standard practice for box-counting on finite objects.
    """
    pts = _edge_point_cloud(G)

    # Normalise the cloud into the unit square so box sizes are comparable.
    lo = pts.min(axis=0)
    span = np.ptp(pts, axis=0)
    span[span == 0] = 1.0
    unit = (pts - lo) / span.max()                 # keep aspect ratio (square box)

    ks = np.unique(np.round(
        np.geomspace(min_boxes, max_boxes, n_sizes)).astype(int))
    counts = []
    for k in ks:
        cells = np.floor(np.clip(unit, 0, 1 - 1e-12) * k).astype(np.int64)
        occupied = len(np.unique(cells[:, 0] * (k + 1) + cells[:, 1]))
        counts.append(occupied)
    counts = np.asarray(counts, float)

    # D = slope of  log N  vs  log k   (since eps = 1/k => log(1/eps) = log k)
    x = np.log(ks.astype(float))
    y = np.log(counts)
    slope, intercept = np.polyfit(x, y, 1)

    return {"D": float(slope), "sizes": ks, "counts": counts,
            "fit": (float(slope), float(intercept))}


def fractal_dimension(G: nx.Graph) -> float:
    """Convenience: just the scalar D."""
    return box_counting_dimension(G)["D"]


if __name__ == "__main__":
    from . import network
    G = network.generate()
    print("box-counting D =", round(fractal_dimension(G), 3))
