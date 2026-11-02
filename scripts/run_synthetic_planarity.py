# -*- coding: utf-8 -*-
r"""
run_synthetic_planarity.py -- are the synthetic "planar mesh" networks planar?

The paper calls the synthetic reference network and the 42-network grid a
"calibrated planar mesh". The generator lays out a bifurcating tree and then
adds the shortest Delaunay non-edges (network._add_mesh_reticulation) without
checking them against the tree. This script measures, for the reference network
and every grid network:
  * crossings among the tree edges themselves (straight segments between the
    generated junction coordinates),
  * mesh edges that cross a tree edge, and mesh edges crossing each other,
  * whether the GRAPH is planar at all (networkx.check_planarity: can it be
    drawn in the plane with no crossings in SOME layout?).

p_c depends only on which junctions are connected (the layout is never read
by the percolation engine), so crossings in the drawing do not change any
threshold. They do decide whether "planar" is a true description of the
networks and whether the drawing is a physically possible leaf.

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_synthetic_planarity.py

Output: data/synthetic_planarity.json
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import networkx as nx
import config
from holoparasitic import network, planarity, calibrate as cal


def check(G):
    tree = [(u, v) for u, v, d in G.edges(data=True) if d.get("kind") != "anastomosis"]
    mesh = [(u, v) for u, v, d in G.edges(data=True) if d.get("kind") == "anastomosis"]
    tt = planarity.crossing_pairs(G, tree, tree, same_set=True)
    mt = planarity.crossing_pairs(G, mesh, tree)
    mm = planarity.crossing_pairs(G, mesh, mesh, same_set=True)
    is_planar, _ = nx.check_planarity(G)
    return {"N": G.number_of_nodes(), "E": G.number_of_edges(),
            "tree_edges": len(tree), "mesh_edges": len(mesh),
            "tree_tree_crossing_pairs": int(tt.shape[1]),
            "tree_edges_in_a_crossing": int(len(set(tt[0]) | set(tt[1]))),
            "mesh_edges_crossing_tree": int(len(set(mt[0]))),
            "mesh_mesh_crossing_pairs": int(mm.shape[1]),
            "graph_is_planar": bool(is_planar)}


def main():
    out = {"reference_network": check(network.generate(config.DEFAULT_NETWORK)),
           "grid": []}
    print("reference", out["reference_network"], flush=True)
    for params, md, gen in cal.grid_params(config.SWEEP_MEAN_DEGREES,
                                           config.SWEEP_GENERATIONS):
        r = check(network.generate(params))
        r.update({"req_mean_degree": md, "generations": gen})
        out["grid"].append(r)
        print(gen, md, r, flush=True)
    g = out["grid"]
    out["grid_summary"] = {
        "n": len(g),
        "networks_with_tree_crossings": sum(r["tree_tree_crossing_pairs"] > 0 for r in g),
        "networks_with_mesh_tree_crossings": sum(r["mesh_edges_crossing_tree"] > 0 for r in g),
        "networks_graph_planar": sum(r["graph_is_planar"] for r in g),
        "mesh_edges_total": sum(r["mesh_edges"] for r in g),
        "mesh_edges_crossing_tree_total": sum(r["mesh_edges_crossing_tree"] for r in g),
        "tree_edges_total": sum(r["tree_edges"] for r in g),
        "tree_edges_in_a_crossing_total": sum(r["tree_edges_in_a_crossing"] for r in g)}
    print(out["grid_summary"])
    json.dump(out, open(os.path.join(ROOT, "data", "synthetic_planarity.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
