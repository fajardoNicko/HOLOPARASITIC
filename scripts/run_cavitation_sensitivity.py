# -*- coding: utf-8 -*-
r"""
run_cavitation_sensitivity.py -- P0 audit: is the "0 vessels embolise" result an
empirical finding or a consequence of stipulated boundary conditions?

The sink demonstration (scripts/make_sink_demo.py) reports that the calibrated
haustorium embolises no vessels at any host->parasite gradient in [0, 3] MPa,
against PSI_CAVITATION = -2.0 MPa. That result is conditional on THREE stipulated
numbers, not one:

    PSI_SOURCE     =  0.0 MPa   (root Dirichlet)
    PSI_LEAF       = -1.0 MPa   (terminal Dirichlet -- the transpirational pull)
    PSI_CAVITATION = -2.0 MPa   (embolism threshold)

Every interior potential is bracketed by the two Dirichlet conditions plus
whatever the sink pulls. So the "margin to cavitation" is largely the STIPULATED
gap PSI_LEAF - PSI_CAVITATION, and only partly the parasite's doing. This script
separates the two and reports the quantity that is invariant to both stipulations:

    dPSI_min = min interior psi WITH sink  -  min interior psi WITHOUT sink

It sweeps, on the calibrated hero mesh:
  1. the cavitation threshold        (-1.00 ... -3.00 MPa)
  2. the host->parasite gradient     (0 ... 3 MPa, as in make_sink_demo)
  3. the sink strength               (1x ... 64x the calibrated K_h)
  4. the leaf boundary condition     (-0.5 ... -2.5 MPa, i.e. host operating point)

and reports, for every combination, embolised counts for the sink case AND for
the no-parasite baseline control -- the control the original demonstration omits.

    python scripts/run_cavitation_sensitivity.py

Outputs data/cavitation_sensitivity.json.  ASCII-only stdout.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

import config
from holoparasitic import network, hydraulics
from scripts.make_sink_demo import (source_influx, parasite_flux,
                                    diversion_fraction, calibrate_kh,
                                    GRADIENT_MPA, TARGET_DIV)

OUT = ROOT / "data" / "cavitation_sensitivity.json"

THRESHOLDS = [-1.00, -1.10, -1.25, -1.50, -1.75, -2.00, -2.50, -3.00]
GRADIENTS = np.linspace(0.0, 3.0, 31)
# extended range: the -2.0 MPa onset lies far outside the manuscript's 0-3 sweep
GRADIENTS_EXT = np.concatenate([np.linspace(0.0, 3.0, 31), np.arange(3.5, 12.5, 0.5)])
KH_MULTIPLES = [1, 2, 4, 8, 16, 32, 64, 128, 256]
LEAF_BCS = [-0.5, -1.0, -1.5, -2.0, -2.5]


def build_patch(G, solver):
    """Reproduce make_sink_demo's contact patch: interior node nearest the
    lamina centroid, plus two hops, capped at 16 free nodes."""
    pos = np.array([G.nodes[n]["pos"] for n in solver.nodes], float)
    fixed = {solver.root, *solver.terminals}
    interior = [(i, n) for i, n in enumerate(solver.nodes) if n not in fixed]
    cx, cy = pos[:, 0].mean(), pos[:, 1].mean()
    h_node = min(interior, key=lambda t: (pos[t[0], 0] - cx) ** 2
                 + (pos[t[0], 1] - cy) ** 2)[1]
    patch, frontier = {h_node}, {h_node}
    for _ in range(2):
        nxt = set()
        for n in frontier:
            nxt |= set(G.neighbors(n))
        patch |= nxt
        frontier = nxt
    return [n for n in patch if n not in fixed][:16], h_node


def count_embolised(psi, free_idx, threshold):
    """Free (non-Dirichlet) nodes below the threshold. The solver protects root
    and terminals from embolism, so the control must use the same convention."""
    return int((psi[free_idx] < threshold).sum())


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    G = network.generate()
    solver, psi0 = hydraulics.baseline_potentials(G)
    prot = {solver.root, *solver.terminals}
    free_idx = np.array([solver.index[n] for n in solver.nodes
                         if n not in prot], int)
    patch, h_node = build_patch(G, solver)
    psi_host_local = float(psi0[solver.index[h_node]])
    psi_parasite_ref = psi_host_local - GRADIENT_MPA

    k_h, frac, psi_cal = calibrate_kh(solver, patch, psi_parasite_ref)
    print("calibrated K_h = %.4f (diverts %.1f%% at %.1f MPa); patch=%d; "
          "host-local psi=%.4f" % (k_h, 100 * frac, GRADIENT_MPA, len(patch),
                                   psi_host_local))

    out: dict = {
        "_purpose": "P0 cavitation-threshold sensitivity; see "
                    "SECOND_PASS_AUDIT.md Part II",
        "_generated_by": "scripts/run_cavitation_sensitivity.py",
        "setup": {
            "network": "config.DEFAULT_NETWORK (cohort-calibrated planar mesh)",
            "N": int(len(solver.nodes)),
            "n_free_nodes": int(free_idx.size),
            "patch_size": len(patch),
            "psi_source_MPa": config.PSI_SOURCE,
            "psi_leaf_MPa": config.PSI_LEAF,
            "psi_cavitation_default_MPa": config.PSI_CAVITATION,
            "calibrated_K_h": float(k_h),
            "achieved_diversion": float(frac),
            "psi_host_local_MPa": psi_host_local,
            "K_h_is_relative": "K_h multiplies each host node's own incident "
                               "conductance, so a haustorium taps a vessel in "
                               "proportion to its caliber",
        },
    }

    # ---- 1. the baseline control the demonstration omits --------------------
    base = {
        "min_interior_psi_MPa": float(psi0[free_idx].min()),
        "median_interior_psi_MPa": float(np.median(psi0[free_idx])),
        "embolised_by_threshold": {
            f"{t:.2f}": count_embolised(psi0, free_idx, t) for t in THRESHOLDS},
    }
    base["reading"] = (
        "with NO parasite the interior field already spans %0.3f to %0.3f MPa, "
        "because the terminal Dirichlet condition is fixed at %.1f MPa; any "
        "cavitation threshold at or above PSI_LEAF makes the healthy leaf "
        "embolise, so the threshold is not freely choosable"
        % (psi0[free_idx].min(), psi0[free_idx].max(), config.PSI_LEAF))
    out["baseline_control"] = base

    # ---- 2. gradient x threshold at the calibrated K_h ----------------------
    #  Two potentials are tracked. The GLOBAL minimum is what the manuscript
    #  reports, but it is dominated by terminal-adjacent nodes clamped at
    #  PSI_LEAF and is therefore insensitive to the sink until the sink beats
    #  the boundary condition. The PATCH-LOCAL depression is the quantity the
    #  parasite actually controls, and it is linear in the gradient.
    patch_idx = np.array([solver.index[n] for n in patch], int)
    grad_rows = []
    for g in GRADIENTS_EXT:
        pp = psi_host_local - g
        psi_g = solver.solve(haustoria={n: k_h for n in patch}, relative=True,
                             psi_parasite=pp)
        qp = parasite_flux(solver, psi_g, patch, k_h, pp)
        qs = source_influx(solver, psi_g)
        grad_rows.append({
            "gradient_MPa": round(float(g), 4),
            "psi_parasite_MPa": round(float(pp), 4),
            "min_interior_psi_MPa": round(float(psi_g[free_idx].min()), 5),
            "delta_min_psi_vs_baseline_MPa": round(
                float(psi_g[free_idx].min() - psi0[free_idx].min()), 5),
            "patch_min_psi_MPa": round(float(psi_g[patch_idx].min()), 5),
            "delta_patch_psi_vs_baseline_MPa": round(
                float((psi_g[patch_idx] - psi0[patch_idx]).min()), 5),
            "diversion_fraction": round(float(qp / qs) if qs else 0.0, 5),
            "embolised_by_threshold": {
                f"{t:.2f}": count_embolised(psi_g, free_idx, t)
                for t in THRESHOLDS},
        })
    out["gradient_sweep_at_calibrated_Kh"] = grad_rows

    # onset gradient per threshold
    onset = {}
    for t in THRESHOLDS:
        hit = [r["gradient_MPa"] for r in grad_rows
               if r["embolised_by_threshold"][f"{t:.2f}"] > 0]
        onset[f"{t:.2f}"] = hit[0] if hit else None
    out["cavitation_onset_gradient_by_threshold"] = onset

    # the patch depression is linear in the gradient; report the slope so the
    # null becomes derivable rather than merely observed
    gg = np.array([r["gradient_MPa"] for r in grad_rows])
    dp = np.array([r["delta_patch_psi_vs_baseline_MPa"] for r in grad_rows])
    slope, intercept = np.polyfit(gg, dp, 1)
    resid = dp - (slope * gg + intercept)
    out["patch_depression_law"] = {
        "slope_MPa_per_MPa_of_gradient": round(float(slope), 5),
        "intercept_MPa": round(float(intercept), 6),
        "max_abs_residual_MPa": round(float(np.abs(resid).max()), 6),
        "single_node_analytic_clamp_Kh_over_1_plus_Kh": round(
            float(k_h / (1 + k_h)), 5),
        "gradient_required_to_reach_PSI_CAVITATION_MPa": round(
            float((config.PSI_CAVITATION - psi_host_local) / slope), 2),
        "reading": (
            "the tapped node sits at a conductance-weighted average of its "
            "neighbours and the parasite reservoir, with the reservoir's weight "
            "fixed at K_h/(1+K_h) per node because K_h is specified RELATIVE to "
            "each node's own incident conductance. The depression is therefore "
            "linear in the gradient with a slope set by K_h and the patch size, "
            "independent of leaf architecture -- so the absence of embolism is "
            "an arithmetic consequence of the sink parameterisation, not an "
            "emergent property of venation topology."),
    }

    # ---- 3. sink strength x threshold at the illustrative gradient ----------
    kh_rows = []
    pp_ref = psi_host_local - GRADIENT_MPA
    for m in KH_MULTIPLES:
        psi_m = solver.solve(haustoria={n: k_h * m for n in patch},
                             relative=True, psi_parasite=pp_ref)
        qp = parasite_flux(solver, psi_m, patch, k_h * m, pp_ref)
        qs = source_influx(solver, psi_m)
        kh_rows.append({
            "K_h_multiple": m,
            "K_h": round(float(k_h * m), 6),
            "min_interior_psi_MPa": round(float(psi_m[free_idx].min()), 5),
            "diversion_fraction": round(float(qp / qs) if qs else 0.0, 5),
            "embolised_by_threshold": {
                f"{t:.2f}": count_embolised(psi_m, free_idx, t)
                for t in THRESHOLDS},
        })
    out["kh_sweep_at_illustrative_gradient"] = kh_rows
    onset_kh = {}
    for t in THRESHOLDS:
        hit = [r["K_h_multiple"] for r in kh_rows
               if r["embolised_by_threshold"][f"{t:.2f}"] > 0]
        onset_kh[f"{t:.2f}"] = hit[0] if hit else None
    out["cavitation_onset_Kh_multiple_by_threshold"] = onset_kh

    # ---- 4. the host operating point (leaf Dirichlet) ----------------------
    #   This is the variable that actually governs the margin. A real leaf at
    #   midday sits well below -1.0 MPa; the model holds it at -1.0 by fiat.
    bc_rows = []
    for bc in LEAF_BCS:
        psi_b0 = solver.solve(haustoria=None, psi_leaf=bc)
        psi_b1 = solver.solve(haustoria={n: k_h for n in patch}, relative=True,
                              psi_leaf=bc,
                              psi_parasite=float(psi_b0[solver.index[h_node]])
                              - GRADIENT_MPA)
        bc_rows.append({
            "psi_leaf_MPa": bc,
            "baseline_min_interior_psi_MPa": round(float(psi_b0[free_idx].min()), 5),
            "sink_min_interior_psi_MPa": round(float(psi_b1[free_idx].min()), 5),
            "delta_min_psi_MPa": round(
                float(psi_b1[free_idx].min() - psi_b0[free_idx].min()), 5),
            "baseline_embolised_at_-2.00": count_embolised(psi_b0, free_idx, -2.0),
            "sink_embolised_at_-2.00": count_embolised(psi_b1, free_idx, -2.0),
        })
    out["leaf_boundary_condition_sweep"] = bc_rows

    # ---- 5. the margin decomposition ---------------------------------------
    dpsi_cal = float(psi_cal[free_idx].min() - psi0[free_idx].min())
    in_range = [r for r in grad_rows if r["gradient_MPa"] <= 3.0]
    dpsi_max = min(r["delta_min_psi_vs_baseline_MPa"] for r in in_range)
    stipulated_gap = float(config.PSI_LEAF - config.PSI_CAVITATION)
    out["margin_decomposition"] = {
        "stipulated_gap_PSI_LEAF_minus_PSI_CAVITATION_MPa": stipulated_gap,
        "parasite_contribution_at_calibrated_Kh_and_1.5MPa_MPa": round(dpsi_cal, 5),
        "parasite_contribution_at_worst_gradient_in_0_3_MPa": round(dpsi_max, 5),
        "parasite_share_of_total_margin_pct": round(
            100 * abs(dpsi_cal) / abs(stipulated_gap), 2),
        "reading": (
            "the reported ~0.98 MPa margin to cavitation is dominated by the "
            "stipulated 1.0 MPa gap between the transpirational boundary "
            "condition and the embolism threshold; the parasite itself moves "
            "the leaf's minimum potential by only the delta reported here. "
            "dPSI_min is invariant to the choice of PSI_CAVITATION and is the "
            "quantity the paper should report."),
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # ---- console summary ----------------------------------------------------
    print("\nBASELINE (no parasite): min interior psi = %.4f MPa"
          % base["min_interior_psi_MPa"])
    print("  embolised at each threshold:", base["embolised_by_threshold"])
    print("\nCALIBRATED SINK at 1.5 MPa: min interior psi = %.4f MPa "
          "(delta vs baseline = %+.4f MPa)"
          % (psi_cal[free_idx].min(), dpsi_cal))
    print("  embolised at each threshold:",
          {f"{t:.2f}": count_embolised(psi_cal, free_idx, t) for t in THRESHOLDS})
    print("\nWorst case within the manuscript's 0-3 MPa sweep: min psi = %.4f "
          "MPa (delta %+.4f)"
          % (min(r["min_interior_psi_MPa"] for r in in_range), dpsi_max))
    pl = out["patch_depression_law"]
    print("Patch depression law: %.4f MPa per MPa of gradient (max resid %.4f);"
          " reaching PSI_CAVITATION needs a %.2f MPa gradient"
          % (pl["slope_MPa_per_MPa_of_gradient"], pl["max_abs_residual_MPa"],
             pl["gradient_required_to_reach_PSI_CAVITATION_MPa"]))
    print("\ncavitation onset gradient by threshold:", onset)
    print("cavitation onset K_h multiple by threshold (at 1.5 MPa):", onset_kh)
    print("\nleaf-BC sweep (baseline vs sink min psi, and embolised at -2.0):")
    for r in bc_rows:
        print("  psi_leaf=%.1f -> base %.3f / sink %.3f (delta %+.3f); "
              "embolised base=%d sink=%d"
              % (r["psi_leaf_MPa"], r["baseline_min_interior_psi_MPa"],
                 r["sink_min_interior_psi_MPa"], r["delta_min_psi_MPa"],
                 r["baseline_embolised_at_-2.00"], r["sink_embolised_at_-2.00"]))
    print("\nwrote %s" % OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
