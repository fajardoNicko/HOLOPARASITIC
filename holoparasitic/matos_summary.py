r"""
matos_summary.py — read the per-leaf metrics Matos et al. already computed.

Each species directory holds more than the nodes/veins pair our loader uses:

    <leaf>_summary.csv        ~160 precomputed whole-leaf metrics, ONE row
    <leaf>_HLD.csv            hierarchical loop decomposition: Horton-Strahler
                              order + degree/area asymmetry per loop
    <leaf>_areoles.csv        every areole (the region enclosed by a vein loop)
                              with its area, perimeter, circularity, elongation
    <leaf>_polygons.csv       the same for the polygon tessellation
    <leaf>_areole_edges.csv   areole adjacency
    <leaf>_polygon_edges.csv  polygon adjacency

Two reasons this matters to us.

1. INDEPENDENT CROSS-CHECKS. `Valpha` is the alpha (meshedness) index,
   (E - N + 1) / (2N - 5) — the standard graph-theoretic measure of how much of
   a planar network's possible circuitry is actually realised. It is computed
   from their extraction, not ours, so comparing it against our own cycle
   density tests the loader end to end. Likewise VNE/VNN against our edge and
   node counts.

2. LOOP ORGANISATION IS ALREADY MEASURED. calibrate.py's docstring lists the
   areole-size hierarchy and loop nesting as explicitly NOT calibrated, on the
   grounds that matching it needs an optimisation-based generator. The areole
   and HLD tables mean the TARGETS at least exist in the data, even if the
   generator that reproduces them does not yet.

Only a working subset of the ~160 summary columns is named here. The full row is
kept under "raw" so nothing is silently discarded.
"""

from __future__ import annotations

import os
import csv
import glob

import numpy as np

#: summary-column -> readable name, for the columns we actually reason about
SUMMARY_FIELDS = {
    "VNE": "n_vein_edges",          # their edge count
    "VNN": "n_vein_nodes",          # their node count
    "VFE": "n_free_ends",           # dangling vein endings
    "VFEratio": "free_end_ratio",
    "Valpha": "alpha_index",        # meshedness: (E-N+1)/(2N-5)
    "VTotL": "vein_length_total",
    "VLoopL": "vein_length_loop",   # length in loop-forming veins
    "VTreeL": "vein_length_tree",   # length in tree-like veins
    "VTotLD": "vein_length_density",
    "VLoopLD": "vein_length_density_loop",
    "VTreeLD": "vein_length_density_tree",
    "VTotV": "vein_volume_total",
    "VNND": "node_density",
    "TotA": "leaf_area",
    "VTotavLen": "vein_length_mean",
    "VTotavWid": "vein_width_mean",
    "VavTor": "tortuosity_mean",
    "ANN": "n_areoles",
    "AloopND": "areole_loop_density",
    "AavAre": "areole_area_mean",
    "AmdAre": "areole_area_median",
    "AsdAre": "areole_area_sd",
    "AavCir": "areole_circularity_mean",
    "AavElg": "areole_elongation_mean",
    "AavSld": "areole_solidity_mean",
    "NavBD0": "branch_diam_parent_mean",
    "NavBD1": "branch_diam_daughter1_mean",
    "NavBD2": "branch_diam_daughter2_mean",
    "NavA10": "branch_angle_10_mean",
    "NavA20": "branch_angle_20_mean",
    "NavA21": "branch_angle_21_mean",
    "resolution": "resolution_mm_px",
}


def _f(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def load_summary(species_dir: str) -> dict | None:
    """Read <leaf>_summary.csv from one species directory (its single row)."""
    hits = glob.glob(os.path.join(species_dir, "*_summary.csv"))
    if not hits:
        return None
    with open(hits[0], newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None
    row = rows[0]
    out = {new: _f(row.get(old)) for old, new in SUMMARY_FIELDS.items()}
    out["file"] = (row.get("File") or "").strip()
    out["raw"] = row
    return out


def load_hld(species_dir: str) -> dict | None:
    """Summarise <leaf>_HLD.csv: the hierarchical loop decomposition.

    Horton-Strahler order is the classical branching-hierarchy index; max order
    is how many nested levels of loop structure the leaf carries. The asymmetry
    columns describe how evenly each split divides its subtree, which is the
    hierarchy analogue of the daughter-radius symmetry we already measure.

    The `Boundary` flag marks loops touching the image edge — directly relevant
    to the cropping artifact quantified in boundary.py, since it is the source
    dataset's own statement of which structures are cut by the window.
    """
    hits = glob.glob(os.path.join(species_dir, "*_HLD.csv"))
    if not hits:
        return None
    hs, da, sda, aa, saa, area, bnd = [], [], [], [], [], [], []
    with open(hits[0], newline="") as f:
        for row in csv.DictReader(f):
            for col, dest in (("nodeHortonStrahler", hs),
                              ("degreeAsymmetry", da),
                              ("subtreeDegreeAsymmetry", sda),
                              ("areaAsymmetry", aa),
                              ("subtreeAreaAsymmetry", saa),
                              ("nodeArea", area),
                              ("Boundary", bnd)):
                v = _f(row.get(col))
                if v is not None:
                    dest.append(v)
    if not hs:
        return None
    hs = np.asarray(hs)
    med = lambda v: float(np.median(v)) if len(v) else None
    return {
        "hld_n_loops": int(hs.size),
        "horton_strahler_max": int(hs.max()),
        "horton_strahler_mean": float(hs.mean()),
        "degree_asymmetry_median": med(da),
        "subtree_degree_asymmetry_median": med(sda),
        "area_asymmetry_median": med(aa),
        "subtree_area_asymmetry_median": med(saa),
        "loop_area_median": med(area),
        # what fraction of loops the source data itself flags as edge-touching
        "boundary_loop_frac": (float(np.mean(np.asarray(bnd) > 0))
                               if bnd else None),
    }


def load_areoles(species_dir: str) -> dict | None:
    """Summarise <leaf>_areoles.csv — the loop-enclosed regions.

    Areole size distribution is the quantity a synthetic generator would have to
    reproduce to claim realistic loop organisation. The coefficient of variation
    and the log-area SD describe the HIERARCHY: a leaf with one characteristic
    areole size looks very different from one with nested orders of them, and
    they can share a mean.
    """
    hits = glob.glob(os.path.join(species_dir, "*_areoles.csv"))
    if not hits:
        return None
    area, circ, elong, per = [], [], [], []
    with open(hits[0], newline="") as f:
        for row in csv.DictReader(f):
            for col, dest in (("Area", area), ("Circularity", circ),
                              ("Elongation", elong), ("Perimeter", per)):
                v = _f(row.get(col))
                if v is not None:
                    dest.append(v)
    if not area:
        return None
    a = np.asarray(area, float)
    pos = a[a > 0]
    med = lambda v: float(np.median(v)) if len(v) else None
    return {
        "n_areoles_measured": int(a.size),
        "areole_area_median": float(np.median(a)),
        "areole_area_cv": float(a.std() / a.mean()) if a.mean() else None,
        # spread of log-area = how many size ORDERS the areoles span
        "areole_log_area_sd": float(np.std(np.log(pos))) if pos.size > 1 else None,
        "areole_circularity_median": med(circ),
        "areole_elongation_median": med(elong),
        "areole_perimeter_median": med(per),
    }


def alpha_index(G) -> float | None:
    """Our own alpha (meshedness) index, to compare against their `Valpha`.

    alpha = (E - N + P) / (2N - 5), P = number of connected components. The
    denominator is the maximum possible independent loops in a planar graph, so
    alpha runs 0 (a tree) to 1 (maximally meshed).
    """
    import networkx as nx
    N, E = G.number_of_nodes(), G.number_of_edges()
    if N < 3:
        return None
    denom = 2 * N - 5
    if denom <= 0:
        return None
    P = nx.number_connected_components(G)
    return float((E - N + P) / denom)
