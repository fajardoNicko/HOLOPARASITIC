r"""
boundary.py — is our headline result a cropping artifact?

THE PROBLEM. 100 of the 120 Matos networks are `*_crop*` files: rectangular
WINDOWS cut out of a larger leaf, not whole leaves. (Matos' own metadata only
notes "Not whole-leaf" on 5 of them, so the filename is the reliable indicator,
not the OBS column.)

Every vein severed by the window edge ends in a node of degree 1. Those are not
real free vein endings — they are cut ends. They inflate the terminal count and
DEPRESS the mean degree by an amount that scales with the window's
perimeter-to-area ratio, i.e. more severely in small windows.

Why that is dangerous HERE specifically. Our headline finding is that mean
degree, not fractal dimension, predicts the percolation threshold. If small
windows have artificially low mean degree, and small windows also behave
differently under percolation for ordinary finite-size reasons, then the
mean-degree/threshold relationship could be partly manufactured by the cropping
rather than by the biology. This module exists to measure that, not to assume
it away.

THE TEST. Classify each degree-1 node as a cut end or a genuine vein ending by
where it sits relative to the network's bounding box, then recompute mean degree
with the cut ends and their pendant veins removed. Compare:

    mean_degree            as measured on the raw window
    mean_degree_interior   with cut ends stripped
    boundary_terminal_frac what fraction of terminals are cut ends

If the interior-corrected mean degree still predicts the threshold, the finding
is about venation. If it does not, the finding was about cropping.

THE MARGIN. A node counts as "on the boundary" if it lies within `margin_frac`
of the bounding box's shorter side from any edge. The default 2% is a
compromise: large enough to catch cut ends despite the ragged trace, small
enough not to eat genuine marginal venation. `boundary_sensitivity()` re-runs
the whole classification across a range of margins so the choice is shown to be
non-critical instead of merely asserted.
"""

from __future__ import annotations

import numpy as np
import networkx as nx


def _positions(G):
    return np.array([G.nodes[n]["pos"] for n in G.nodes], float)


def classify_terminals(G, margin_frac: float = 0.02) -> dict:
    """Split degree-1 nodes into window cut-ends vs genuine free vein endings."""
    if G.number_of_nodes() == 0:
        return {"boundary": set(), "interior": set(), "margin": 0.0}

    nodes = list(G.nodes)
    pos = _positions(G)
    lo, hi = pos.min(axis=0), pos.max(axis=0)
    span = hi - lo
    # margin measured off the SHORTER side, so a long thin window is not
    # judged by its long axis
    short = float(min(s for s in span if s > 0)) if np.any(span > 0) else 0.0
    margin = margin_frac * short

    boundary, interior = set(), set()
    for n, p in zip(nodes, pos):
        if G.degree(n) != 1:
            continue
        near = (abs(p - lo) <= margin).any() or (abs(p - hi) <= margin).any()
        (boundary if near else interior).add(n)
    return {"boundary": boundary, "interior": interior, "margin": margin}


def interior_subgraph(G, margin_frac: float = 0.02):
    """G with window cut-ends removed. Removal is iterated: stripping a pendant
    vein can expose a new degree-1 node that was itself only one step inside the
    window edge, and that node is just as much an artifact as the first."""
    H = G.copy()
    for _ in range(50):                       # converges in a few passes
        cls = classify_terminals(H, margin_frac)
        if not cls["boundary"]:
            break
        H.remove_nodes_from(cls["boundary"])
        H.remove_nodes_from([n for n in list(H.nodes) if H.degree(n) == 0])
    return H


def boundary_profile(G, margin_frac: float = 0.02) -> dict:
    """Raw vs interior-corrected topology for one network."""
    N, E = G.number_of_nodes(), G.number_of_edges()
    cls = classify_terminals(G, margin_frac)
    n_bt, n_it = len(cls["boundary"]), len(cls["interior"])

    H = interior_subgraph(G, margin_frac)
    Ni, Ei = H.number_of_nodes(), H.number_of_edges()
    n_loop_i = sum(1 for *_, d in H.edges(data=True)
                   if d.get("kind") == "anastomosis")

    k_raw = (2 * E / N) if N else 0.0
    k_int = (2 * Ei / Ni) if Ni else 0.0
    return {
        "margin_frac": margin_frac,
        "n_terminals": n_bt + n_it,
        "n_boundary_terminals": n_bt,
        "n_interior_terminals": n_it,
        "boundary_terminal_frac": float(n_bt / (n_bt + n_it)) if (n_bt + n_it) else 0.0,
        # what fraction of the whole network the cropping artifact accounts for
        "boundary_node_frac": float(n_bt / N) if N else 0.0,
        "mean_degree": float(k_raw),
        "mean_degree_interior": float(k_int),
        "mean_degree_shift": float(k_int - k_raw),
        "n_nodes_interior": Ni,
        "n_edges_interior": Ei,
        "loop_fraction_interior": float(n_loop_i / Ei) if Ei else 0.0,
        "n_cycles_interior": int(Ei - Ni + nx.number_connected_components(H)) if Ni else 0,
        # perimeter/area proxy: small windows are hit hardest by cut ends
        "sqrt_area_over_perimeter": _shape_ratio(G),
    }


def _shape_ratio(G):
    """sqrt(bbox area) / bbox perimeter — a scale-free compactness measure. Cut
    ends scale with perimeter while real venation scales with area, so this is
    the covariate the boundary artifact should track if it is present."""
    if G.number_of_nodes() < 2:
        return None
    pos = _positions(G)
    span = pos.max(axis=0) - pos.min(axis=0)
    w, h = float(span[0]), float(span[1])
    per = 2 * (w + h)
    return float((w * h) ** 0.5 / per) if per > 0 else None


def boundary_sensitivity(G, margins=(0.005, 0.01, 0.02, 0.04, 0.08)) -> list[dict]:
    """Repeat the correction across margin choices, so the 2% default is shown
    to be non-critical rather than assumed to be."""
    out = []
    for m in margins:
        p = boundary_profile(G, margin_frac=m)
        out.append({"margin_frac": m,
                    "boundary_terminal_frac": p["boundary_terminal_frac"],
                    "mean_degree": p["mean_degree"],
                    "mean_degree_interior": p["mean_degree_interior"],
                    "mean_degree_shift": p["mean_degree_shift"]})
    return out
