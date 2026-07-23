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
