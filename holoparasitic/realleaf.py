r"""
realleaf.py — load a REAL extracted leaf venation network (Matos et al. 2024,
UC Berkeley botanical garden, Dryad doi:10.5061/dryad.1g1jwsv36) as a networkx
graph that the EXISTING physics engine (hydraulics.py, percolation.py) can solve
unchanged. This is Phase 1 of the hybrid: real leaves get the physics; the
synthetic generator (network.py) is Phase 2.

INPUT — two CSVs per leaf, inside UCBG_venation_form_data.zip, keyed by species
code (first 3 letters of genus + first 3 of species):

  <spp>_nodes.csv   node_ID, node_Type (E edge / P petiole), node_X_pix,
                    node_Y_pix, Calibration (mm/pixel), node_Degree, ...
  <spp>_veins.csv   EndNodes_1, EndNodes_2, Type (EL loop / ET tree / EB
                    boundary / F petiole), Length (mm), Width (mm), ...

We map these onto the SAME attribute contract network.generate() produces, so
every downstream module treats a real leaf and a synthetic network identically:

  node: pos (mm), kind ('root'|'terminal'|'internal'), gen (BFS hops from root)
  edge: radius (mm), length (mm), conductance, resistance, kind
        ('axial'|'anastomosis'), matos_type

BOUNDARY CONDITIONS (the one real modelling choice a mesh forces on us):
  root      = the petiole node (node_Type 'P'); if several, the highest-degree
              one — the main insertion. This is where the solver holds psi = 0.
  terminals = free vein endings (graph degree 1) — the transpiration sites held
              at psi = PSI_LEAF. This is defensible and stated, not hidden.

CONDUCTANCE is built the SAME way as the synthetic pipeline: g ∝ r^4 / L
(Hagen–Poiseuille; the 8η/π constant is global and cancels in the potential
solve). Radii are normalised by the max radius so the sparse system stays
well-conditioned across the ~100x caliber range of a real leaf, exactly as
config.py notes for the synthetic solver.
"""

from __future__ import annotations

import csv
import math

import numpy as np
import networkx as nx

import config


# ---- column-name resolution (read by NAME, tolerant of minor header drift) --
def _get(row, *names, default=None):
    for n in names:
        if n in row and row[n] not in ("", None):
            return row[n]
    return default


def _f(x, default=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _map_kind(matos_type):
    """Matos vein Type -> our edge 'kind'. Loops are the reticulation that gives
    a real percolation threshold, so preserve that distinction explicitly."""
    t = (matos_type or "").strip().upper()
    return "anastomosis" if t == "EL" else "axial"   # EL=loop; ET/EB/F=axial


def load_matos(nodes_csv: str, veins_csv: str, *, root=None,
               to_mm: bool = True, name: str | None = None) -> nx.Graph:
    """Build a networkx.Graph from one leaf's Matos nodes+veins CSV pair.

    root : optional node_ID to force as the source. Default: auto (petiole).
    to_mm: multiply pixel coords by Calibration so positions are in mm (only
           affects box-counting normalisation and plotting, not the physics).
    """
    # -- nodes --------------------------------------------------------------
    nodes = {}
    calib = 1.0
    with open(nodes_csv, newline="") as f:
        for row in csv.DictReader(f):
            nid = _get(row, "node_ID", "node_id", "Node_ID")
            if nid is None:
                continue
            nid = int(float(nid))
            cal = _f(_get(row, "Calibration", "calibration", default=1.0), 1.0)
            if math.isfinite(cal) and cal > 0:
                calib = cal
            x = _f(_get(row, "node_X_pix", "node_X", "X"))
            y = _f(_get(row, "node_Y_pix", "node_Y", "Y"))
            nodes[nid] = {
                "x": x, "y": y,
                "node_type": (_get(row, "node_Type", "node_type",
                                   default="E") or "E").strip().upper()[:1],
                "csv_degree": _f(_get(row, "node_Degree", "node_degree",
                                      default="nan")),
            }
    scale = calib if to_mm else 1.0

    # -- edges --------------------------------------------------------------
    G = nx.Graph()
    n_skip = 0
    with open(veins_csv, newline="") as f:
        for row in csv.DictReader(f):
            a = _get(row, "EndNodes_1", "endnodes_1")
            b = _get(row, "EndNodes_2", "endnodes_2")
            if a is None or b is None:
                continue
            a, b = int(float(a)), int(float(b))
            if a == b:                                   # drop self-loops
                n_skip += 1
                continue
            width = _f(_get(row, "Width", "Width_initial"))
            length = _f(_get(row, "Length", "Length_initial"))
            if not (np.isfinite(width) and width > 0
                    and np.isfinite(length) and length > 0):
                n_skip += 1
                continue
            radius = width / 2.0
            kind = _map_kind(_get(row, "Type", "type"))
            # parallel veins between the same pair collapse in a simple Graph;
            # keep the WIDEST (it dominates r^4 conductance) rather than lose it.
            if G.has_edge(a, b) and G[a][b]["radius"] >= radius:
                continue
            G.add_edge(a, b, radius=radius, length=length, kind=kind,
                       matos_type=(_get(row, "Type", "type") or "").strip())

    # attach positions / node_type only for nodes that survived as edge ends
    for nid in list(G.nodes):
        meta = nodes.get(nid, {})
        x, y = meta.get("x", 0.0), meta.get("y", 0.0)
        G.nodes[nid]["pos"] = (float((x if np.isfinite(x) else 0.0) * scale),
                               float((y if np.isfinite(y) else 0.0) * scale))
        G.nodes[nid]["node_type"] = meta.get("node_type", "E")

    if G.number_of_nodes() == 0:
        raise ValueError(f"{veins_csv}: no usable edges (skipped {n_skip})")

    _assign_roles(G, nodes, root)
    _assign_conductances(G)
    G.graph["source"] = "matos"
    G.graph["name"] = name
    G.graph["n_skipped_veins"] = n_skip
    return G


def _assign_roles(G, nodes, root):
    """Set every node's kind ('root'|'terminal'|'internal') and gen (BFS hops)."""
    deg = dict(G.degree())

    # ROOT: forced -> petiole node in-graph -> highest-degree petiole -> the
    # geometric base (extreme y) as a last resort. All defensible; logged.
    if root is not None and root in G:
        r = root
    else:
        petiole = [n for n in G if nodes.get(n, {}).get("node_type") == "P"]
        if petiole:
            r = max(petiole, key=lambda n: deg.get(n, 0))
        else:                                            # no petiole flag: base
            r = max(G.nodes, key=lambda n: G.nodes[n]["pos"][1])
    G.graph["root"] = r

    # gen = BFS hop distance from root on the largest component containing it
    gens = nx.single_source_shortest_path_length(G, r)
    gmax = (max(gens.values()) if gens else 0) + 1

    for n in G.nodes:
        G.nodes[n]["gen"] = int(gens.get(n, gmax))       # unreachable -> beyond
        if n == r:
            G.nodes[n]["kind"] = "root"
        elif deg.get(n, 0) <= 1:
            G.nodes[n]["kind"] = "terminal"              # free vein ending
        else:
            G.nodes[n]["kind"] = "internal"
        # node radius = widest incident vein (used by some diagnostics)
        rads = [G[n][m]["radius"] for m in G.neighbors(n)]
        G.nodes[n]["radius"] = float(max(rads)) if rads else 0.0


def _assign_conductances(G):
    """g ∝ (r/r_max)^4 / (L/L_mean) — same Hagen–Poiseuille form as the
    synthetic solver, normalised so the sparse system is well-conditioned."""
    radii = np.array([d["radius"] for *_ , d in G.edges(data=True)], float)
    lens = np.array([d["length"] for *_ , d in G.edges(data=True)], float)
    rmax = radii.max() if radii.size else 1.0
    lmean = lens[lens > 0].mean() if np.any(lens > 0) else 1.0
    for u, v, d in G.edges(data=True):
        rn = d["radius"] / rmax
        ln = max(d["length"] / lmean, 1e-9)
        g = (rn ** 4) / ln
        d["conductance"] = float(g)
        d["resistance"] = float(1.0 / g) if g > 0 else float("inf")


def summary(G) -> dict:
    """Same shape as network.summary(), plus real-leaf extras."""
    n_anas = sum(1 for *_, d in G.edges(data=True) if d["kind"] == "anastomosis")
    n_term = sum(1 for _, d in G.nodes(data=True) if d["kind"] == "terminal")
    E, N = G.number_of_edges(), G.number_of_nodes()
    return {
        "n_nodes": N, "n_edges": E,
        "n_anastomoses": n_anas, "n_terminals": n_term,
        "n_cycles": E - N + nx.number_connected_components(G),
        "mean_degree": 2 * E / N if N else 0.0,
        "n_components": nx.number_connected_components(G),
        "root": G.graph.get("root"),
        "loop_fraction": n_anas / E if E else 0.0,
    }
