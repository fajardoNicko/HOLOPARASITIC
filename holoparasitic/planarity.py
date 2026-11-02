"""
planarity.py — edge-crossing checks for the reticulation enhancement.

The enhancement (scripts/make_real_suggested.py::add_loops) adds the shortest
Delaunay non-edges of a leaf's own junction coordinates. Delaunay edges never
cross EACH OTHER, but nothing stops one from crossing an existing traced vein,
because the traced veins are not themselves Delaunay edges. A crossing vein with
no junction at the crossing is not something a leaf can build, so the SRC asked
for the planarity of the enhanced networks to be verified.

Geometry convention: every edge is the straight segment between its two
junction coordinates (`pos`). Real veins curve slightly (the source dataset
ships a tortuosity column), so a straight-segment crossing is an approximation;
the baseline count of crossings among the traced veins themselves
(`existing_crossings`) shows how much of the count that approximation alone
produces.

Two segments are counted as crossing when they share at least one point and do
not share a junction. Segments that meet at a common junction are a normal vein
junction, not a crossing.
"""

from __future__ import annotations

import numpy as np
import shapely
from scipy.spatial import Delaunay


def _segments(G, edges):
    """shapely LineStrings for a list of (u, v) edges, in the given order."""
    if not edges:
        return np.empty(0, dtype=object)
    coords = np.array([[G.nodes[u]["pos"], G.nodes[v]["pos"]] for u, v in edges],
                      float)
    return shapely.linestrings(coords)


def _endpoint_ids(edges, index):
    return np.array([[index[u], index[v]] for u, v in edges], dtype=np.int64)


def _filter_shared(pairs, q_ids, t_ids):
    """Drop (query, tree) index pairs whose edges share a junction."""
    if pairs.shape[1] == 0:
        return pairs
    q, t = q_ids[pairs[0]], t_ids[pairs[1]]
    shared = ((q[:, 0] == t[:, 0]) | (q[:, 0] == t[:, 1]) |
              (q[:, 1] == t[:, 0]) | (q[:, 1] == t[:, 1]))
    return pairs[:, ~shared]


def crossing_pairs(G, query_edges, tree_edges, same_set=False):
    """Index pairs (i, j): query_edges[i] crosses tree_edges[j].

    same_set=True counts crossings inside one edge set (each pair once)."""
    q_edges, t_edges = list(query_edges), list(tree_edges)
    if not q_edges or not t_edges:
        return np.empty((2, 0), dtype=np.int64)
    index = {n: i for i, n in enumerate(G.nodes)}
    q_ids = _endpoint_ids(q_edges, index)
    t_ids = q_ids if same_set else _endpoint_ids(t_edges, index)
    q_geom = _segments(G, q_edges)
    t_geom = q_geom if same_set else _segments(G, t_edges)
    tree = shapely.STRtree(t_geom)
    pairs = tree.query(q_geom, predicate="intersects")
    if same_set:
        pairs = pairs[:, pairs[0] < pairs[1]]
    return _filter_shared(pairs, q_ids, t_ids)


def delaunay_candidates(G):
    """Every Delaunay non-edge of G's junction coordinates as (length, u, v),
    shortest first — the same candidate list add_loops builds."""
    nodes = list(G.nodes)
    pos = np.array([G.nodes[n]["pos"] for n in nodes], float)
    tri = Delaunay(pos)
    seen, cand = set(), []
    for s in tri.simplices:
        for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2])):
            key = (a, b) if a < b else (b, a)
            if key in seen:
                continue
            seen.add(key)
            na, nb = nodes[key[0]], nodes[key[1]]
            if G.has_edge(na, nb):
                continue
            d = float(np.hypot(pos[key[0]][0] - pos[key[1]][0],
                               pos[key[0]][1] - pos[key[1]][1]))
            cand.append((d, na, nb))
    cand.sort(key=lambda t: t[0])
    return cand


def crossing_candidates(G, cand):
    """Boolean mask over `cand`: True where the candidate crosses a traced vein."""
    edges = [(u, v) for _, u, v in cand]
    pairs = crossing_pairs(G, edges, list(G.edges()))
    mask = np.zeros(len(cand), bool)
    mask[np.unique(pairs[0])] = True
    return mask


def _add(G2, na, nb, d):
    ra = min((G2[na][x].get("radius", 0.01) for x in G2.neighbors(na)),
             default=0.01)
    rb = min((G2[nb][x].get("radius", 0.01) for x in G2.neighbors(nb)),
             default=0.01)
    G2.add_edge(na, nb, radius=min(ra, rb), length=d, kind="added_loop")


def add_loops_planar(G, target_k, cand=None, crosses=None, order=None):
    """add_loops with a crossing filter: walk the Delaunay candidates in the
    given order (shortest first by default) and skip any candidate that crosses
    a traced vein. Accepted candidates cannot cross one another (they are all
    edges of one triangulation), so one check against the traced veins is
    enough. Returns (G2, n_added, n_skipped_crossing).

    order : optional index permutation of `cand` (used by the random-order arm
            of the placement control)."""
    if cand is None:
        cand = delaunay_candidates(G)
    if crosses is None:
        crosses = crossing_candidates(G, cand)
    idx = range(len(cand)) if order is None else order
    G2 = G.copy()
    need = int(target_k * G2.number_of_nodes() / 2) - G2.number_of_edges()
    added = skipped = 0
    for i in idx:
        if added >= need:
            break
        if crosses[i]:
            skipped += 1
            continue
        d, na, nb = cand[i]
        _add(G2, na, nb, d)
        added += 1
    return G2, added, skipped
