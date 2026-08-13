r"""
calibrate.py — measure real branching geometry from Matos leaf networks and emit
synthetic-generator parameters, so the synthetic phase is anchored to real
venation while D stays a controlled variable.

THE DESIGN CONSTRAINT (stated, not hidden): the fractal dimension D is not an
independent knob — it EMERGES from branching angle, Murray exponent, daughter
length ratio and loop density. You cannot pin all of those to real values AND
freely dial D. So the strategy is:

  1. CALIBRATE the branching geometry (branch angle + jitter, Murray exponent,
     daughter asymmetry, daughter length ratio) to the real measured medians and
     HOLD them fixed.
  2. SWEEP loop/reticulation density to move D across the real observed range.
     Loop density genuinely varies between real leaves, so every point on the
     D-axis is a biologically plausible network with real branching geometry.

What is NOT calibrated here (honest scope): the exact loop nesting / areole-size
hierarchy of real venation. Matching that needs an optimisation-based generator
(Ronellenfitsch & Katifori) rather than bifurcation + kNN links — future work.

All measurements run on a networkx graph carrying the frozen attribute contract
(pos, gen, radius, length, kind), so the SAME code measures a synthetic network
or a real leaf loaded by realleaf.load_matos().
"""

from __future__ import annotations

import math

import numpy as np
import networkx as nx

import config


def _ang(G, n, m):
    (x0, y0), (x1, y1) = G.nodes[n]["pos"], G.nodes[m]["pos"]
    return math.atan2(y1 - y0, x1 - x0)


def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def _solve_murray(r0, r1, r2, lo=0.5, hi=8.0):
    """Exponent x with r0^x = r1^x + r2^x, or None if no root in [lo, hi]."""
    if not (r0 > 0 and r1 > 0 and r2 > 0) or r0 <= max(r1, r2):
        return None                      # parent must exceed each daughter
    from scipy.optimize import brentq
    f = lambda x: r1 ** x + r2 ** x - r0 ** x
    if f(lo) * f(hi) > 0:
        return None
    try:
        return float(brentq(f, lo, hi, maxiter=200))
    except Exception:
        return None


def measure_from_graph(G) -> dict:
    """Real branching-geometry statistics at every 3+ way junction of G.

    parent = the incident vein toward the root (lowest gen); the two widest of
    the remaining incident veins are the daughters. Returns medians (robust to
    the long tails real venation shows) plus the counts they rest on."""
    angles, murray, symm, lratio = [], [], [], []
    for n in G:
        nb = list(G.neighbors(n))
        if len(nb) < 3:
            continue
        parent = min(nb, key=lambda m: G.nodes[m].get("gen", 1 << 30))
        daughters = [m for m in nb if m != parent]
        if len(daughters) < 2:
            continue
        daughters.sort(key=lambda m: G[n][m]["radius"], reverse=True)
        d1, d2 = daughters[0], daughters[1]
        r0 = G[n][parent]["radius"]
        r1, r2 = G[n][d1]["radius"], G[n][d2]["radius"]

        x = _solve_murray(r0, r1, r2)
        if x is not None:
            murray.append(x)
        if max(r1, r2) > 0:
            symm.append(min(r1, r2) / max(r1, r2))
        Lp = G[n][parent]["length"]
        if Lp > 0:
            lratio.append(0.5 * (G[n][d1]["length"] + G[n][d2]["length"]) / Lp)

        pax = _ang(G, n, parent) + math.pi          # reverse of parent axis
        for d in (d1, d2):
            angles.append(math.degrees(abs(_wrap(_ang(G, n, d) - pax))))

    E, N = G.number_of_edges(), G.number_of_nodes()
    loops = sum(1 for *_, d in G.edges(data=True) if d["kind"] == "anastomosis")
    med = lambda v: float(np.median(v)) if v else None
    return {
        "branch_angle_deg": med(angles),
        "branch_angle_std": float(np.std(angles)) if angles else None,
        "murray_exponent": med(murray),
        "daughter_symmetry": med(symm),
        "length_ratio": med(lratio),
        "loop_fraction": loops / E if E else 0.0,
        "mean_degree": 2 * E / N if N else 0.0,
        "D": None,                                  # filled by caller if wanted
        "n_junctions": len(angles) // 2,
        "n_murray": len(murray),
    }


def measure_from_matos_nodes(nodes_csv: str) -> dict:
    """Branching geometry read from Matos' OWN per-junction columns.

    Why this exists alongside measure_from_graph(). measure_from_graph()
    reconstructs each junction from our loaded topology: it decides which
    incident vein is the parent (lowest BFS gen from a root WE chose) and takes
    the two widest of the rest as daughters. That is a defensible reconstruction,
    but it is ours, and a panelist can reasonably ask whether the calibration
    targets are an artifact of it.

    The nodes CSV already carries the dataset authors' curated answer:

        node_D0, node_D1, node_D2   parent and two daughter DIAMETERS (mm)
        node_Symmetry               their daughter-symmetry ratio
        node_AreaRatio              (D1^2 + D2^2) / D0^2
        theta_D1_D0, theta_D2_D0    daughter-to-parent angles (deg)
        theta_D2_D1                 angle between the two daughters (deg)

    ANGLE CONVENTION. The theta_Dk_D0 columns measure the angle between the
    parent segment and daughter k as drawn, i.e. ~180 deg for a daughter that
    continues straight on. The branching angle in the generator is the DEVIATION
    from the parent axis, so it is 180 - theta. Both are reported below rather
    than silently converted.

    Using these as the calibration targets makes the synthetic phase answerable
    to the source data rather than to our own graph reconstruction; agreement
    between the two routes is itself a check on the loader.

    TWO CAVEATS THAT MUST BE REPORTED, NOT BURIED:

    1. The per-junction Murray exponent is solved by bracketed root-finding on
       [0.5, 8]. Junctions whose exponent lies outside that window have no root
       to report and are dropped (~10% of junctions). Widening the bracket
       raises the median (2.55 -> 2.78 on Abe_mex at [0.05, 20]), so the number
       is bracket-sensitive and the returned n_murray/n_junctions ratio is there
       to make the discard rate visible. The distribution is very broad
       (IQR ~1.7-4.0), so the median is the honest summary and the IQR must
       travel with it.

    2. The theta columns are computed on a pixel grid, so branching angles are
       quantised — the median lands on values like 53.13 deg (= atan(4/3))
       across different species not by coincidence but because the underlying
       distribution is discrete at small pixel offsets.

    Neither caveat threatens the qualitative finding, which both routes agree
    on: real leaves branch at ~50-57 deg with markedly asymmetric daughters
    (~0.75) and a Murray exponent well BELOW the classical 3.
    """
    import csv as _csv

    d0, d1, d2, symm, arat = [], [], [], [], []
    th10, th20, th21 = [], [], []
    with open(nodes_csv, newline="") as f:
        for row in _csv.DictReader(f):
            def g(col):
                try:
                    v = float(row.get(col, ""))
                    return v if np.isfinite(v) else None
                except (TypeError, ValueError):
                    return None
            a, b, c = g("node_D0"), g("node_D1"), g("node_D2")
            if None in (a, b, c) or min(a, b, c) <= 0:
                continue
            d0.append(a); d1.append(b); d2.append(c)
            for col, dest in (("node_Symmetry", symm), ("node_AreaRatio", arat),
                              ("theta_D1_D0", th10), ("theta_D2_D0", th20),
                              ("theta_D2_D1", th21)):
                v = g(col)
                if v is not None:
                    dest.append(v)

    if not d0:
        return {"n_junctions": 0}

    # Murray exponent per junction: D0^x = D1^x + D2^x (diameters, not radii —
    # the equation is scale-free in the ratio, so radii vs diameters agree).
    murray = []
    for a, b, c in zip(d0, d1, d2):
        x = _solve_murray(a, b, c)
        if x is not None:
            murray.append(x)

    med = lambda v: float(np.median(v)) if v else None
    # deviation from the parent axis, averaged over both daughters
    dev = [180.0 - t for t in th10 + th20 if 0.0 < t <= 180.0]
    return {
        "branch_angle_deg": med(dev),
        "branch_angle_std": float(np.std(dev)) if dev else None,
        "theta_daughter_parent_deg": med(th10 + th20),   # raw, as stored
        "theta_between_daughters_deg": med(th21),
        "murray_exponent": med(murray),
        "murray_iqr": ([float(np.percentile(murray, 25)),
                        float(np.percentile(murray, 75))] if murray else None),
        "daughter_symmetry": med(symm),
        "area_ratio": med(arat),
        "n_junctions": len(d0),
        "n_murray": len(murray),
        "source": "matos_native_columns",
    }


def aggregate(stats_list) -> dict:
    """Median across many leaves' per-leaf stats (drops Nones per field)."""
    keys = ["branch_angle_deg", "branch_angle_std", "murray_exponent",
            "daughter_symmetry", "length_ratio", "loop_fraction", "mean_degree",
            "D"]
    out = {}
    for k in keys:
        vals = [s[k] for s in stats_list if s.get(k) is not None]
        out[k] = float(np.median(vals)) if vals else None
    out["n_leaves"] = len(stats_list)
    return out


def calibrated_params(stats: dict, base: config.NetworkParams | None = None,
                      reticulation: float | None = None) -> config.NetworkParams:
    """Map measured real geometry onto a config.NetworkParams. Loop density can
    be overridden (this is the D-sweep knob); if None it matches the real
    mean degree."""
    base = base or config.DEFAULT_NETWORK
    kw = dict(base.__dict__)

    if stats.get("branch_angle_deg"):
        kw["branch_angle"] = float(np.clip(stats["branch_angle_deg"], 5.0, 85.0))
    if stats.get("branch_angle_std"):
        kw["angle_jitter"] = float(np.clip(stats["branch_angle_std"], 0.0, 30.0))
    if stats.get("murray_exponent"):
        kw["radius_exponent"] = float(np.clip(stats["murray_exponent"], 1.5, 5.0))
    if stats.get("daughter_symmetry"):
        kw["daughter_symmetry"] = float(np.clip(stats["daughter_symmetry"],
                                                0.2, 1.0))
    if stats.get("length_ratio"):
        kw["length_ratio"] = float(np.clip(stats["length_ratio"], 0.4, 0.95))

    if reticulation is not None:
        kw["reticulation"] = float(max(0.0, reticulation))
    elif stats.get("mean_degree"):
        # mean degree of the reticulate network ~ 2*(1 + reticulation)
        kw["reticulation"] = float(max(0.0, stats["mean_degree"] / 2.0 - 1.0))

    return config.NetworkParams(**kw)


def d_sweep_params(stats: dict, reticulations, base=None):
    """A list of NetworkParams that all share the real branching geometry but
    vary reticulation density — the biologically-anchored D sweep. Measure D on
    each generated network afterwards (D is emergent, never asserted)."""
    return [calibrated_params(stats, base=base, reticulation=r)
            for r in reticulations]


# ---------------------------------------------------------------------------
# COHORT calibration — the measured medians of the 100-leaf real cohort, and
# the 2D sweep design they imply.
# ---------------------------------------------------------------------------
#: median branching geometry over the 100-leaf cohort (scripts/build_cohort.py).
#: These are the FIXED targets the synthetic generator is calibrated to; only
#: mean degree and D are then swept. Measured 2026-07-25 (graph route); the
#: native-column route (measure_from_matos_nodes) agrees within tolerance.
COHORT_TARGETS = {
    "branch_angle_deg": 55.31,
    "branch_angle_std": 32.59,     # clipped to 30 (angle_jitter cap) on apply
    "murray_exponent": 2.00,
    "daughter_symmetry": 0.675,
    "length_ratio": 0.929,
    "mean_degree": 2.516,
    "loop_fraction": 0.776,        # NOT matched — see note in reticulation_for_k
    "D_median": 1.694,
    "D_min": 1.262,
    "D_max": 1.913,
    "mean_degree_min": 2.148,
    "mean_degree_max": 2.989,
}


#: mesh_frac giving a target mean degree in 'mesh' mode. Fitted from the grid
#: (<k> ~ 2 + a*mesh_frac); a ~ 6 for the calibrated geometry, so
#: mesh_frac ~ (<k> - 2) / 6. Connectivity and loop fraction rise together, as
#: they do across real leaves, so this single knob sets both.
def mesh_frac_for_k(mean_degree: float) -> float:
    return float(np.clip((mean_degree - 2.0) / 6.0, 0.0, 1.0))


def reticulation_for_k(mean_degree: float) -> float:
    """('knn' mode only) reticulation density giving a target mean degree:
    reticulation = <k>/2 - 1, since knn adds reticulation*(N-1) links to the
    tree. Superseded by the 'mesh' mode (mesh_frac_for_k), which also reproduces
    the real loop fraction; kept for the pre-2026-07 hero network."""
    return float(max(0.0, mean_degree / 2.0 - 1.0))


def calibrated_base(generations: int = 11, mean_degree: float | None = None,
                    seed: int = 0) -> config.NetworkParams:
    """The cohort-calibrated generator: real branching geometry, real planar-MESH
    reticulation (loop_fraction ~0.78), mean degree set to the cohort median (or
    a supplied value), D left to emerge from `generations`. Anchor for Phase 2."""
    md = COHORT_TARGETS["mean_degree"] if mean_degree is None else mean_degree
    p = calibrated_params(
        COHORT_TARGETS,
        base=config.NetworkParams(generations=generations, seed=seed))
    return config.NetworkParams(**{**p.__dict__,
                                   "reticulation_mode": "mesh",
                                   "mesh_frac": mesh_frac_for_k(md)})


def grid_params(mean_degrees, generations, seed: int = 0):
    """The 2D synthetic sweep that mirrors the real cohort's independence of
    <k> and D.

    Two near-orthogonal knobs (verified empirically):
      * `generations` moves D  (deeper tree = more space-filling) at ~fixed <k>
      * reticulation moves <k>  (added cross-links) with only mild D drift

    Crossing them produces a grid spanning the real (<k>, D) region, so the
    synthetic phase can attribute p_c to each factor independently — the causal
    complement to the real-cohort regression, where <k> and D happened to be
    uncorrelated but could not be intervened on. Both <k> and D are MEASURED on
    each generated network afterwards; the grid axes are only the requested
    targets, never asserted outputs.

    Returns a list of (params, requested_mean_degree, generations) tuples.

    D CEILING (the one remaining honest limitation). With planar-MESH
    reticulation the loop fraction now matches real leaves (~0.70-0.78 at
    <k>~2.6), so the network is a genuine mesh, not a decorated tree. Box-counting
    D still SATURATES at ~1.81, because D is a property of WHERE the veins sit
    (the point cloud), which the branching layout fixes — adding mesh edges
    between existing points barely moves it, and deeper generations plateau. The
    ~22% of real leaves with D > 1.81 are the densest meshes; reaching them needs
    a space-filling/optimisation layout (Ronellenfitsch & Katifori), which is
    future work. The grid spans D 1.26-1.81 (78% of the real cloud), a wide
    causal range; it does not claim to reproduce every real leaf.
    """
    out = []
    for g in generations:
        for md in mean_degrees:
            out.append((calibrated_base(generations=int(g), mean_degree=md,
                                        seed=seed), float(md), int(g)))
    return out


if __name__ == "__main__":
    # self-check on a synthetic network: measure it, then confirm the calibrated
    # params round-trip into a generatable network.
    from . import network, fractal
    G = network.generate(config.NetworkParams(generations=8, daughter_symmetry=0.7,
                                              seed=0))
    s = measure_from_graph(G)
    s["D"] = fractal.fractal_dimension(G)
    print("measured:", {k: (round(v, 3) if isinstance(v, float) else v)
                        for k, v in s.items()})
    cp = calibrated_params(s)
    G2 = network.generate(cp)
    print(f"round-trip network: N={G2.number_of_nodes()} "
          f"D={fractal.fractal_dimension(G2):.3f} "
          f"symmetry={cp.daughter_symmetry:.2f} angle={cp.branch_angle:.1f}")
