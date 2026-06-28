"""
network.py  (Person A) — synthetic host vascular network generator.

Builds a 2-D hydraulic network by recursive Murray's-law bifurcation and then
adds *anastomoses* (reticulation / cross-links) so the network contains loops.

WHY RETICULATION MATTERS
    A strict branching tree has no redundant paths: removing any internal node
    disconnects its whole subtree, so the giant component bleeds off roughly
    linearly and there is NO sharp percolation transition. Real vascular tissue
    (especially leaf venation) is reticulate. The `reticulation` parameter adds
    the loops that make a sharp threshold p_c — and the hero sigmoid — exist.

Produces a `networkx.Graph` following the FROZEN schema documented in config.py.
"""

from __future__ import annotations

import math
import numpy as np
import networkx as nx
from scipy.spatial import cKDTree
from scipy.sparse import csr_array

import config


# ----------------------------------------------------------------------------
# Murray's law: r_parent^n = r_c1^n + r_c2^n.  For a symmetric bifurcation the
# two children are equal, so r_child = r_parent / 2^(1/n).
# ----------------------------------------------------------------------------
def _child_radius(parent_radius: float, exponent: float) -> float:
    return parent_radius / (2.0 ** (1.0 / exponent))


def _hagen_poiseuille_resistance(radius: float, length: float) -> float:
    """Real Hagen-Poiseuille resistance R = 8 eta L / (pi r^4)  [Pa.s/m^3]."""
    return 8.0 * config.ETA * length / (math.pi * radius ** 4)


def _add_edge(G, u, v, radius, length, kind):
    """Attach an edge with both the real resistance and the normalised
    conductance g = r^4 / L used by the (well-conditioned) solver."""
    G.add_edge(
        u, v,
        radius=radius,
        length=length,
        resistance=_hagen_poiseuille_resistance(radius, length),
        conductance=(radius ** 4) / length,   # normalised (r0 = 1)
        kind=kind,
    )


def generate(params: config.NetworkParams | None = None) -> nx.Graph:
    """Generate one reticulate Murray network. Returns a networkx.Graph."""
    p = params or config.DEFAULT_NETWORK
    rng = config.new_rng(p.seed)

    G = nx.Graph()
    # Root junction at the stem base; the main stem points "downward" (-y).
    G.add_node(0, pos=(0.0, 0.0), gen=0, radius=p.root_radius, kind="root")

    # Each stack entry: (node_id, direction_angle_rad, vessel_length, radius, gen)
    stack = [(0, -math.pi / 2.0, p.root_length, p.root_radius, 0)]
    next_id = 1

    while stack:
        node, angle, length, radius, gen = stack.pop()
        if gen >= p.generations:
            G.nodes[node]["kind"] = "terminal"
            continue

        child_r = _child_radius(radius, p.radius_exponent)
        child_l = length * p.length_ratio
        px, py = G.nodes[node]["pos"]

        for sign in (+1.0, -1.0):
            jitter = math.radians(rng.uniform(-p.angle_jitter, p.angle_jitter))
            ca = angle + sign * math.radians(p.branch_angle) + jitter
            cx = px + math.cos(ca) * child_l
            cy = py + math.sin(ca) * child_l
            cid = next_id
            next_id += 1
            G.add_node(cid, pos=(cx, cy), gen=gen + 1,
                       radius=child_r, kind="internal")
            _add_edge(G, node, cid, child_r, child_l, "axial")
            stack.append((cid, ca, child_l, child_r, gen + 1))

    _add_reticulation(G, p, rng)
    return G


def _add_reticulation(G, p: config.NetworkParams, rng) -> None:
    """Join spatially-close nodes from different branches with thin anastomoses,
    creating the loops that give the network a true percolation threshold.

    The number of cross-links is fixed at ``reticulation * (N-1)`` and the
    SHORTEST available links are added first, so mean degree is held constant
    across length_ratio (which would otherwise change local point density and
    confound the D sweep)."""
    if p.reticulation <= 0.0:
        return

    ids = list(G.nodes)
    pos = np.array([G.nodes[i]["pos"] for i in ids])
    n = len(ids)
    k = min(p.reticulation_knn + 1, n)
    dist, nbr = cKDTree(pos).query(pos, k=k)

    # Collect unique candidate cross-links (not already tree edges), keyed by
    # length so we can add the shortest ones first.
    cand = {}
    for a in range(n):
        for jj in range(1, k):
            b = int(nbr[a, jj])
            if b == a:
                continue
            u, v = (a, b) if a < b else (b, a)
            if (u, v) in cand or G.has_edge(ids[u], ids[v]):
                continue
            cand[(u, v)] = float(dist[a, jj])
    if not cand:
        return

    ordered = sorted(cand.items(), key=lambda kv: kv[1])
    n_target = min(len(ordered), int(round(p.reticulation * (n - 1))))
    for (u, v), length in ordered[:n_target]:
        radius = min(G.nodes[ids[u]]["radius"], G.nodes[ids[v]]["radius"])
        _add_edge(G, ids[u], ids[v], radius, length or 1e-6, "anastomosis")


# ----------------------------------------------------------------------------
# Conversions / summaries used by the rest of the pipeline.
# ----------------------------------------------------------------------------
def to_csr(G: nx.Graph) -> tuple[csr_array, list]:
    """Convert G to a CSR adjacency matrix ONCE (integer-indexed). Returns the
    matrix and the node-order list so results can be mapped back to G.

    The Monte Carlo hot loop runs entirely on this matrix and never touches
    NetworkX — this is what makes 1e6 trials tractable (see the brief)."""
    nodes = list(G.nodes)
    adj = nx.to_scipy_sparse_array(G, nodelist=nodes, format="csr", dtype=np.int8)
    return adj, nodes


def conductance_csr(G: nx.Graph):
    """Weighted adjacency (edge conductances) for the hydraulic solver."""
    nodes = list(G.nodes)
    W = nx.to_scipy_sparse_array(G, nodelist=nodes, weight="conductance",
                                 format="csr", dtype=float)
    return W, nodes


def summary(G: nx.Graph) -> dict:
    n_anas = sum(1 for _, _, d in G.edges(data=True) if d["kind"] == "anastomosis")
    n_term = sum(1 for _, d in G.nodes(data=True) if d["kind"] == "terminal")
    return {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "n_anastomoses": n_anas,
        "n_terminals": n_term,
        "n_cycles": G.number_of_edges() - G.number_of_nodes() + 1,
        "mean_degree": 2 * G.number_of_edges() / G.number_of_nodes(),
    }


if __name__ == "__main__":
    G = generate()
    print("network summary:", summary(G))
