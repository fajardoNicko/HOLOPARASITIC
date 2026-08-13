r"""
characterize.py — PHASE 3: biological characterization of a vascular network.

Computes the full architectural + hydraulic profile of one leaf (real or
synthetic). The same function characterizes both, so Phase 1 measurements and
Phase 2 synthetic networks are described in identical terms — which is what
makes the calibration in Phase 4 and the comparison in Chapter 4 like-for-like.

Answers SOP 1 (fractal dimension, hydraulic conductance, giant connected
component) and supplies the calibration targets for the synthetic generator.

Cost note: everything here is cheap (~1-2 s/leaf) EXCEPT betweenness centrality,
which is O(V*E) exactly and still expensive approximately. It is therefore
opt-in (`betweenness=True`), not default — a 400k-edge leaf would otherwise
dominate the entire run.
"""

from __future__ import annotations

import math

import numpy as np
import networkx as nx

import config
from . import fractal, calibrate


def _gcc(G):
    """Largest connected component: (node count, fraction of network)."""
    if G.number_of_nodes() == 0:
        return 0, 0.0
    comps = list(nx.connected_components(G))
    biggest = max(len(c) for c in comps)
    return biggest, biggest / G.number_of_nodes()


def _effective_conductance(G):
    """Whole-leaf conductance: total flow entering the root per unit potential
    drop, from the steady-state solve. This is the model analogue of a measured
    K_leaf, so it can be compared against the source dataset's kmax values.
    Returns None if the system cannot be solved."""
    try:
        from . import hydraulics
        solver = hydraulics.HydraulicSolver(G)
        psi = solver.solve(haustoria=None)
        root = solver.root
        idx = solver.index
        q = 0.0
        for nbr in G.neighbors(root):
            g = G[root][nbr]["conductance"]
            q += g * (psi[idx[root]] - psi[idx[nbr]])
        drop = abs(config.PSI_SOURCE - config.PSI_LEAF)
        return float(q / drop) if drop > 0 else None
    except Exception:
        return None


def characterize(G, name: str | None = None, betweenness: bool = False,
                 bc_samples: int = 100) -> dict:
    """Full biological profile of one vascular network."""
    N, E = G.number_of_nodes(), G.number_of_edges()
    degs = np.array([d for _, d in G.degree()], float) if N else np.array([0.0])
    radii = np.array([d["radius"] for *_, d in G.edges(data=True)], float) \
        if E else np.array([])
    lens = np.array([d["length"] for *_, d in G.edges(data=True)], float) \
        if E else np.array([])
    conds = np.array([d["conductance"] for *_, d in G.edges(data=True)], float) \
        if E else np.array([])
    # loop_fraction = fraction of edges lying on at least one cycle (non-bridge
    # edges). Construction-independent: a spanning-tree edge that a later chord
    # closes into a loop counts here, whereas the old "anastomosis"-tag count did
    # not, which under-reported reticulation on the synthetic meshes.
    n_loop = E - len(list(nx.bridges(G)))
    n_comp = nx.number_connected_components(G) if N else 0
    gcc_n, gcc_frac = _gcc(G)

    prof = {
        "name": name,
        # --- size / topology -------------------------------------------------
        "n_nodes": N,
        "n_edges": E,
        "n_components": n_comp,
        "gcc_nodes": gcc_n,
        "gcc_fraction": float(gcc_frac),
        "mean_degree": float(degs.mean()) if N else 0.0,
        "degree_sd": float(degs.std(ddof=1)) if N > 1 else 0.0,
        "max_degree": int(degs.max()) if N else 0,
        # cycle rank = independent loops (Euler): E - N + components
        "n_cycles": int(E - N + n_comp),
        "cycle_density": float((E - N + n_comp) / N) if N else 0.0,
        "loop_fraction": float(n_loop / E) if E else 0.0,
        "n_terminals": sum(1 for _, d in G.nodes(data=True)
                           if d.get("kind") == "terminal"),
        # --- geometry (mm, when loaded from real data) -----------------------
        "mean_vein_length": float(lens.mean()) if lens.size else None,
        "total_vein_length": float(lens.sum()) if lens.size else None,
        "mean_radius": float(radii.mean()) if radii.size else None,
        # hydraulically weighted diameter, the standard 4th-power convention
        "hydraulic_diameter": (float((np.sum((2 * radii) ** 4) / radii.size)
                                     ** 0.25) if radii.size else None),
        # --- hydraulics ------------------------------------------------------
        "total_conductance": float(conds.sum()) if conds.size else None,
        "effective_conductance": _effective_conductance(G),
        # --- architecture ----------------------------------------------------
        "D": None,
    }

    # fractal dimension (the SOP-1 headline architectural descriptor)
    try:
        prof["D"] = float(fractal.fractal_dimension(G))
    except Exception:
        prof["D"] = None

    # branching geometry -> the Phase 4 calibration targets
    try:
        prof.update({f"geom_{k}": v
                     for k, v in calibrate.measure_from_graph(G).items()
                     if k not in ("loop_fraction", "mean_degree")})
    except Exception:
        pass

    # betweenness: opt-in, approximate (k-sample) — exact is O(V*E)
    if betweenness and N > 2:
        try:
            k = min(bc_samples, N)
            bc = np.array(list(nx.betweenness_centrality(
                G, k=k, normalized=True, seed=1).values()), float)
            prof["betweenness_mean"] = float(bc.mean())
            prof["betweenness_max"] = float(bc.max())
            prof["betweenness_sd"] = float(bc.std(ddof=1)) if bc.size > 1 else 0.0
        except Exception:
            pass

    return prof


# ----------------------------------------------------------------------------
# Validity screening — decided on STRUCTURAL grounds, before any p_c exists.
# ----------------------------------------------------------------------------
def is_valid_for_percolation(prof: dict, min_edges: int = 2000,
                             min_cycles: int = 1,
                             max_cut_end_frac: float = 0.05,
                             max_degree_shift: float = 0.05) -> tuple[bool, str]:
    """Whether a network can support a meaningful, unbiased percolation threshold.

    Requirements, all independent of any simulation outcome:
      1. It must contain cycles. A network with no loops has NO percolation
         transition — every edge is critical, so no threshold exists to measure.
      2. It must be large enough that a threshold is resolvable rather than
         dominated by finite-size noise. The 2,000-vein floor is data-driven:
         below it the cropping artifact (see boundary.py) starts to dominate
         mean degree, the response variable.
      3. The cropping artifact must be negligible. 100 of the 120 Matos networks
         are cropped WINDOWS; veins severed by the window edge become spurious
         degree-1 nodes that depress mean degree. `scripts/run_boundary_check.py`
         quantifies this per leaf. A network is admitted only if at most
         max_cut_end_frac of its terminals are cut ends AND stripping them shifts
         mean degree by at most max_degree_shift. This gate is what excludes thin
         SLIVER windows (e.g. a leaf with thousands of veins but a 98% cut-end
         fraction) that a pure size floor would wrongly admit.

    The boundary fields are optional: if a profile lacks them (e.g. a synthetic
    network, which has no window), the boundary gate is simply skipped.

    Returning the reason as well as the verdict so every exclusion is auditable.
    """
    if prof.get("n_edges", 0) < min_edges:
        return False, f"too small ({prof.get('n_edges', 0)} < {min_edges} veins)"
    if prof.get("n_cycles", 0) < min_cycles:
        return False, f"acyclic ({prof.get('n_cycles', 0)} cycles) — no transition"
    if prof.get("D") is None:
        return False, "fractal dimension could not be measured"
    # boundary gate — only applied when the metrics are present
    btf = prof.get("boundary_terminal_frac")
    if btf is not None and btf > max_cut_end_frac:
        return False, (f"cropping artifact ({btf:.0%} of terminals are cut ends "
                       f"> {max_cut_end_frac:.0%}) — a sliver window")
    shift = prof.get("mean_degree_shift")
    if shift is not None and abs(shift) > max_degree_shift:
        return False, (f"cropping distorts mean degree by {abs(shift):.3f} "
                       f"> {max_degree_shift}")
    return True, "ok"
