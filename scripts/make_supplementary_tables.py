# -*- coding: utf-8 -*-
r"""
make_supplementary_tables.py -- build SUPPLEMENTARY_TABLES.md (Tables S1-S5) directly
from the archived JSON, so every quantity the Discussion cites has a numbered home in
the manuscript and no Discussion value is unsourced.

Each table collects quantities that were computed and archived but that the main
Results tables do not carry. Nothing here is a new analysis.

    python scripts/make_supplementary_tables.py

Writes SUPPLEMENTARY_TABLES.md.  ASCII-only stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "SUPPLEMENTARY_TABLES.md"


def L(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def r3(x):
    """APA rank statistic: no leading zero."""
    s = "%.3f" % abs(x)
    return ("−" if x < 0 else "") + "." + s.split(".")[1]


def fm(x):
    """4 dp, extended to 5 when 4 would round away a distinct archived value."""
    return ("%.5f" % x) if abs(round(x, 4) - x) > 1e-9 else ("%.4f" % x)


def p3(x):
    if x < 0.001:
        return "< .001"
    return "= ." + ("%.3f" % x).split(".")[1]


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    rv = L("results_verified.json")
    cl = L("criterion_and_locality.json")
    cav = L("cavitation_sensitivity.json")
    spa = L("second_pass_audit.json")
    frc = L("final_resolution_checks.json")
    rcs = L("resistance_convention_sensitivity.json")
    rrl = L("rrl_diagnostics.json")
    gma = L("graph_metric_audit.json")
    fsz = L("finite_size_fixedD.json")
    scl = L("scaling_mesh.json")
    rob = L("robustness.json")
    bnd = L("boundary_check.json")
    srf = L("sink_surface.json")
    hcs = L("robustness_ceiling_summary.json")
    hyd = rv["T11_validation"]["hydraulic_resistance"]
    T5, T7 = rv["T5_predictors"], rv["T7_reticulation_and_bridges"]
    crit, loc, assoc = (cl["criterion_comparison"], cl["locality_comparison"],
                        cl["associations_under_each_criterion"])
    hd = rv["headroom_diagnostic"]
    gm = gma["targeted_attack_axis"]
    sc = spa["size_controls"]
    em = spa["enhancement_mediation"]
    er = spa["enhancement_robustness"]
    ba = frc["bootstrap_audit"]

    # Recomputed here rather than read from data/graph_metric_audit.json, whose
    # cycle_rank_fraction_vs_identity field for the empirical set omits the
    # components correction and is therefore wrong (see the note under S3).
    import csv as _csv
    with open(ROOT / "data" / "analysis_master.csv", encoding="utf-8") as fh:
        rows = list(_csv.DictReader(fh))
    idmax, idn = 0.0, 0
    arms = []
    for r in rows:
        N, Ee = float(r["n_nodes"]), float(r["n_edges"])
        k, cyc = float(r["mean_degree"]), float(r["n_cycles"])
        comps = cyc - Ee + N
        idmax = max(idmax, abs(cyc / Ee - (1 - 2 / k + comps / Ee)))
        idn += 1
        if r["in_percolation_cohort_100"] == "True":
            arms.append((float(r["pc_random"]), float(r["pc_degree"])))
    _n = len(arms)
    _mx = sum(a for a, _ in arms) / _n
    _my = sum(b for _, b in arms) / _n
    _sxy = sum((a - _mx) * (b - _my) for a, b in arms)
    _sx = sum((a - _mx) ** 2 for a, _ in arms) ** 0.5
    _sy = sum((b - _my) ** 2 for _, b in arms) ** 0.5
    arm_r = _sxy / (_sx * _sy)
    _u = [float(r["mean_degree"]) for r in rows
          if r["in_enhancement_cohort_105"] == "True" and float(r["delta_pc"]) == 0.0]
    unch_lo, unch_hi = min(_u), max(_u)

    W = []
    a = W.append

    a("# Supplementary Tables")
    a("")
    a("These tables collect quantities that were computed and archived by the analysis "
      "scripts but that the main Results tables do not carry. **No table here reports a new "
      "analysis.** Each is generated directly from the archived result files by "
      "`scripts/make_supplementary_tables.py`, and each is cited from the Discussion so that "
      "no interpretive statement rests on an unnumbered value.")
    a("")
    a("| Table | Content | Source file |")
    a("|---|---|---|")
    a("| S1 | Removal-weight distributions; nominal versus realised removed fraction; "
      "betweenness as a proxy for solved flux | `data/graph_metric_audit.json`, "
      "`data/final_resolution_checks.json` |")
    a("| S2 | Reticulation-enhancement result across every quality and boundary subset; "
      "grade mediation by baseline connectivity; response-surface reconciliation | "
      "`data/second_pass_audit.json`, `data/rrl_diagnostics.json`, "
      "`data/robustness_ceiling_summary.json` |")
    a("| S3 | Predictor collinearity, size control, criterion and locality dispersion, "
      "crop-edge detail, bootstrap interval widths | `data/rrl_diagnostics.json`, "
      "`data/second_pass_audit.json`, `data/criterion_and_locality.json`, "
      "`data/boundary_check.json`, `data/final_resolution_checks.json` |")
    a("| S4 | Full haustorial-sink sensitivity: cavitation onset by threshold, by sink "
      "strength, and by host operating potential; haustorial-density surface | "
      "`data/cavitation_sensitivity.json`, `data/sink_surface.json` |")
    a("| S5 | Both synthetic size sweeps with the unpinned architectural descriptors; "
      "generating-function comparisons | `data/finite_size_fixedD.json`, "
      "`data/scaling_mesh.json`, `data/robustness.json` |")
    a("")
    a("---")
    a("")

    # ---------------- S1 -----------------------------------------------------
    a("**Table S1**")
    a("")
    a("*Removal-Weight Distributions, the Nominal Versus Realised Removal Axis, and "
      "Betweenness as a Proxy for Solved Flux*")
    a("")
    a("| Weight | Gini | Max (× mean) | Distinct values | Largest tied group | "
      "Realised fraction at nominal ρ = 0.1889 | at 0.2023 |")
    a("|---|---:|---:|---:|---:|---:|---:|")
    for key, lbl in [("degree", "Degree"), ("betweenness", "Betweenness")]:
        g = gm[key]
        a("| %s | %.3f | %.1f | %d | %.1f%% | %.4f | %.4f |"
          % (lbl, g["weight_gini"], g["weight_max"], g["n_distinct_weights"],
             100 * g["largest_tied_group_fraction"],
             g["realised_at_nominal_0.1889"], g["realised_at_nominal_0.2023"]))
    a("")
    a("| Network | N | Free nodes | ρ(betweenness, flux) | ρ(degree, flux) | "
      "ρ(betweenness, degree) | Flux Gini |")
    a("|---|---:|---:|---:|---:|---:|---:|")
    for n in frc["betweenness_vs_flux"]["per_network"]:
        a("| %s | %s | %s | %s | %s | %s | %.4f |"
          % (n["label"], "{:,}".format(n["N"]), "{:,}".format(n["n_free_nodes"]),
             r3(n["spearman_betweenness_x_flux"][0]), r3(n["spearman_degree_x_flux"][0]),
             r3(n["spearman_betweenness_x_degree"][0]), n["flux_gini"]))
    a("")
    a("*Note.* Removal is **weighted stochastic**: each node is removed with probability "
      "proportional to its centrality, clipped at unity, following the degree-dependent "
      "occupation formalism of Callaway et al. (2000). It is not rank-ordered deletion of "
      "the top-*k* nodes. Because the clip binds for heavy-tailed weights, the nominal "
      "control parameter overstates the realised removed fraction for betweenness but not "
      "for degree, which is why Table 4 reports both axes. Weight statistics are computed "
      "on the synthetic reference network (*N* = 1,023). Flux is the solved Kirchhoff "
      "through-flow at each node; all flux correlations have *p* < .001 except "
      "ρ(degree, flux) on *Tri_lan* (*p* = .004).")
    a("")
    a("---")
    a("")

    # ---------------- S2 -----------------------------------------------------
    a("**Table S2**")
    a("")
    a("*Reticulation Enhancement Across Every Quality and Boundary Subset, Grade Mediation, "
      "and the Response-Surface Reconciliation*")
    a("")
    a("| Subset | n | Improved | Unchanged | Worsened | Mdn Δp_c | Mdn baseline ⟨k⟩ | "
      "Wilcoxon (Pratt) p | Sign test p |")
    a("|---|---:|---:|---:|---:|---:|---:|---|---|")
    order = [("full_105", "Full enhancement cohort"),
             ("excluding_any_C_flag", "Excluding every network with a C flag"),
             ("excluding_any_D_flag", "Excluding every network with a D flag"),
             ("A_or_B_only_no_C_no_D", "A or B only, no C and no D"),
             ("leading_grade_A", "Leading grade A only"),
             ("boundary_ok_only", "Inside both crop-edge tolerances")]
    for key, lbl in order:
        r = er[key]
        a("| %s | %d | %d | %d | **%d** | %s | %.3f | %s | %s |"
          % (lbl, r["n"], r["improved"], r["unchanged"], r["worsened"],
             fm(r["median_delta_pc"]), r["median_baseline_mean_degree"],
             p3(r["wilcoxon_pratt_p"]), p3(r["sign_test_p"])))
    hg = frc["high_gcc_subcohort"]["enhancement_high_gcc"]
    a("| Baseline GCC fraction > .99 | %d | %d | %d | **%d** | %s | — | — | %s |"
      % (hg["n"], hg["improved"], hg["unchanged"], hg["worsened"],
         fm(hg["median_delta_pc"]), p3(hg["sign_test_p"])))
    a("")
    a("| Grade | n | Mdn raw Δp_c | Mdn baseline ⟨k⟩ | "
      "Mdn Δp_c residualised on baseline ⟨k⟩ |")
    a("|---|---:|---:|---:|---:|")
    for g in ["A", "B", "C", "D"]:
        bg = rrl["enhancement_artefact_test"]["by_grade"][g]
        a("| %s | %d | %.4f | %.4f | %s |"
          % (g, bg["n"], bg["median_delta_pc"], bg["median_baseline_mean_degree"],
             ("+" if em["residual_median_by_grade"][g] >= 0 else "−") + "%.5f" % abs(em["residual_median_by_grade"][g])))
    a("")
    a("| Comparison | Statistic | Value |")
    a("|---|---|---|")
    a("| Δp_c by grade, raw | Kruskal–Wallis H | %.3f, *p* %s |"
      % (em["kruskal_on_raw_delta_by_grade"][0], p3(em["kruskal_on_raw_delta_by_grade"][1])))
    a("| Δp_c by grade, residualised on baseline ⟨k⟩ | Kruskal–Wallis H | %.3f, *p* %s |"
      % (em["kruskal_on_residual_delta_by_grade"][0], p3(em["kruskal_on_residual_delta_by_grade"][1])))
    a("| Δp_c on baseline ⟨k⟩ | Spearman ρ | %s, *R*² = %s |"
      % (r3(em["spearman_baseline_k_x_delta"][0]), r3(em["R2_of_delta_on_baseline_k"])))
    a("| Response surface, predicted median gain | — | %.4f |" % hd["median_gain_from_reticulation"])
    a("| Rewiring, measured median gain | — | %.4f |" % hd["measured_median_delta_from_rewiring"])
    a("| **Ratio, predicted : measured** | — | **%.2f** |" % hd["ratio_predicted_to_measured_gain"])
    a("| Response surface, predicted median p_c | — | %.4f |" % hd["median_pc_predicted_by_surface"])
    a("| Measured median p_c | — | %.4f |" % hd["median_pc_measured"])
    a("| Networks for which reticulation is the dominant modelled lever | — | %d of %d |"
      % (hd["dominant_lever_counts"]["reticulation"], hd["n"]))
    a("| Enhancement ceiling ⟨k⟩ (P90 of the percolation cohort) | — | %.3f |"
      % rv["T9_enhancement"]["ceiling_mean_degree"])
    a("| Initial ⟨k⟩ of the 12 networks whose threshold did not change | — | %.4f – %.4f, "
      "**all already above the ceiling** |" % (unch_lo, unch_hi))
    a("")
    a("*Note.* Quality flags are **defect types, not severity levels**, and subsets are "
      "defined on flag *presence* rather than on the leading flag, because the archive "
      "retains only the leading flag of a comma-separated code and thereby hides 4 "
      "over-segmented and 28 damaged networks inside other leading grades. **No subset "
      "contains a single worsened network.** The residual column asks whether any grade "
      "difference survives mediation by baseline connectivity; grade A carries the largest "
      "positive residual, which is the opposite of what a tracing-recovery artefact would "
      "produce. The response surface extrapolates a between-network regression to a "
      "counterfactual architecture, whereas the rewiring measures a within-network "
      "perturbation; the two answer different questions and are not averaged.")
    a("")
    a("---")
    a("")

    # ---------------- S3 -----------------------------------------------------
    a("**Table S3**")
    a("")
    a("*Predictor Collinearity, Network-Size Control, Criterion and Locality Dispersion, "
      "Crop-Edge Detail, and Bootstrap Interval Widths*")
    a("")
    a("| Quantity | Value |")
    a("|---|---|")
    a("| Pearson r(⟨k⟩, D) | %s, *p* %s |"
      % (r3(rrl["collinearity"]["pearson_meandegree_x_D"]), p3(rrl["collinearity"]["p"])))
    a("| Variance inflation factor | %.2f |" % rrl["collinearity"]["VIF"])
    a("| Pearson r between the uniform and degree-weighted thresholds (n = %d) | %s |"
      % (_n, r3(arm_r)))
    a("| Spearman ρ(⟨k⟩, loop fraction) | %s |"
      % r3(rrl["collinearity"]["spearman_meandegree_x_loopfraction"]))
    a("| Pearson r(⟨k⟩, loop fraction) | %s |"
      % r3(rrl["collinearity"]["pearson_meandegree_x_loopfraction"]))
    a("| Cubic fit of loop fraction on ⟨k⟩ | *R*² = %s, residual *SD* = %.3f |"
      % (r3(gma["empirical_120_leaves"]["loop_fraction_given_mean_degree"]["cubic_fit_R2"]),
         gma["empirical_120_leaves"]["loop_fraction_given_mean_degree"]["residual_sd"]))
    a("| Cycle-rank fraction vs the identity 1 − 2/⟨k⟩ + c/E | max \\|difference\\| = %.1e "
      "across all %d traced networks (**exact to floating point**) |" % (idmax, idn))
    a("| Non-bridge loop fraction vs the same identity | mean \\|difference\\| = %.3f "
      "(**not** an identity) |"
      % gma["empirical_120_leaves"]["nonbridge_loop_fraction_vs_identity"]["mean_abs_difference"])
    a("| Non-bridge fraction ÷ cycle-rank fraction | %.2f |"
      % gma["empirical_120_leaves"]["nonbridge_vs_cycle_rank"]["ratio"])
    a("")
    a("| Association | Raw ρ | p | Controlling log N | p |")
    a("|---|---:|---|---:|---|")
    pairs = [("pc_x_mean_degree", "p_c × ⟨k⟩"),
             ("pc_x_loop_fraction", "p_c × loop fraction"),
             ("pc_x_D", "p_c × D"),
             ("attack_gap_x_loop_fraction", "Uniform-minus-weighted gap × loop fraction")]
    for key, lbl in pairs:
        a("| %s | %s | %s | **%s** | %s |"
          % (lbl, r3(sc["raw"][key][0]), p3(sc["raw"][key][1]),
             r3(sc["controlling_logN"][key][0]), p3(sc["controlling_logN"][key][1])))
    a("| p_c × N | %s | %s | — | — |"
      % (r3(sc["raw"]["pc_x_N"][0]), p3(sc["raw"]["pc_x_N"][1])))
    a("| Gap × N | %s | %s | — | — |"
      % (r3(sc["raw"]["attack_gap_x_N"][0]), p3(sc["raw"]["attack_gap_x_N"][1])))
    sz = rrl["size_confound"]
    for key, lbl in [("spearman_N_x_mean_degree", "N × ⟨k⟩"),
                     ("spearman_N_x_loop_fraction_nonbridge", "N × loop fraction"),
                     ("spearman_N_x_D", "N × D")]:
        a("| %s | %s | %s | — | — |"
          % (lbl, r3(sz[key]["rho"]), p3(sz[key]["p"])))
    a("| ⟨k⟩ × gap | %s | %s | — | — |"
      % (r3(T7["mean_degree_x_attack_gap"]["rho"]), p3(T7["mean_degree_x_attack_gap"]["p"])))
    a("| p_c × D, residualised on log N | %s | %s | — | — |"
      % (r3(spa["fractal_dimension_audit"]["spearman_pc_x_D_residualised_on_logN"][0]),
         p3(spa["fractal_dimension_audit"]["spearman_pc_x_D_residualised_on_logN"][1])))
    a("")
    a("| Damage scenario | Mdn threshold | IQR | ρ with ⟨k⟩ (p) | ρ with loop fraction (p) | "
      "ρ with D (p) |")
    a("|---|---:|---|---:|---:|---:|")
    a("| Dispersed (GCC criterion) | %.4f | %.4f – %.4f | %s | %s | %s |"
      % (crit["median_gcc"], crit["iqr_gcc"][0], crit["iqr_gcc"][1],
         "%s (%s)" % (r3(assoc["gcc"]["spearman_x_mean_degree"][0]), p3(assoc["gcc"]["spearman_x_mean_degree"][1])),
         "%s (%s)" % (r3(assoc["gcc"]["spearman_x_loop_fraction"][0]), p3(assoc["gcc"]["spearman_x_loop_fraction"][1])),
         "%s (%s)" % (r3(assoc["gcc"]["spearman_x_D"][0]), p3(assoc["gcc"]["spearman_x_D"][1]))))
    a("| Dispersed (source-anchored) | %.4f | %.4f – %.4f | %s | %s | %s |"
      % (crit["median_source"], crit["iqr_source"][0], crit["iqr_source"][1],
         "%s (%s)" % (r3(assoc["source_anchored"]["spearman_x_mean_degree"][0]), p3(assoc["source_anchored"]["spearman_x_mean_degree"][1])),
         "%s (%s)" % (r3(assoc["source_anchored"]["spearman_x_loop_fraction"][0]), p3(assoc["source_anchored"]["spearman_x_loop_fraction"][1])),
         "%s (%s)" % (r3(assoc["source_anchored"]["spearman_x_D"][0]), p3(assoc["source_anchored"]["spearman_x_D"][1]))))
    a("| Localised, 1 disc | %.4f | %.4f – %.4f | %s | %s | %s |"
      % (loc["median_disc1"], loc["iqr_disc1"][0], loc["iqr_disc1"][1],
         "%s (%s)" % (r3(assoc["disc1"]["spearman_x_mean_degree"][0]), p3(assoc["disc1"]["spearman_x_mean_degree"][1])),
         "%s (%s)" % (r3(assoc["disc1"]["spearman_x_loop_fraction"][0]), p3(assoc["disc1"]["spearman_x_loop_fraction"][1])),
         "%s (%s)" % (r3(assoc["disc1"]["spearman_x_D"][0]), p3(assoc["disc1"]["spearman_x_D"][1]))))
    a("| Localised, 10 discs | %.4f | %.4f – %.4f | %s | %s | %s |"
      % (loc["median_disc10"], loc["iqr_disc10"][0], loc["iqr_disc10"][1],
         "%s (%s)" % (r3(assoc["disc10"]["spearman_x_mean_degree"][0]), p3(assoc["disc10"]["spearman_x_mean_degree"][1])),
         "%s (%s)" % (r3(assoc["disc10"]["spearman_x_loop_fraction"][0]), p3(assoc["disc10"]["spearman_x_loop_fraction"][1])),
         "%s (%s)" % (r3(assoc["disc10"]["spearman_x_D"][0]), p3(assoc["disc10"]["spearman_x_D"][1]))))
    a("")
    a("| Crop-edge quantity | Value |")
    a("|---|---|")
    bs = bnd["summary"]
    a("| Networks inside both tolerances | %d of %d |" % (bs["n_within_tolerance"], bs["n_leaves"]))
    a("| Median boundary-terminal fraction | %.4f (tolerance %.2f) |"
      % (bs["median_boundary_terminal_frac"], bs["tolerances"]["max_boundary_terminal_frac"]))
    a("| Median \\|mean-degree shift\\| | %.4f (tolerance %.2f) |"
      % (bs["median_abs_shift"], bs["tolerances"]["max_mean_degree_shift"]))
    a("| Spearman ρ(log E, boundary-terminal fraction) | %s, *p* %s |"
      % (r3(bs["spearman_logE_vs_boundary_frac"]["rho"]), p3(bs["spearman_logE_vs_boundary_frac"]["p"])))
    a("| Spearman ρ(log E, \\|mean-degree shift\\|) | %s, *p* %s |"
      % (r3(bs["spearman_logE_vs_abs_shift"]["rho"]), p3(bs["spearman_logE_vs_abs_shift"]["p"])))
    a("| Failures entering the percolation cohort | 0 |")
    a("| Failures entering the enhancement cohort | 3 |")
    a("")
    a("| Bootstrap quantity | Capped replicate | Full-size replicate |")
    a("|---|---:|---:|")
    cap, full = ba["measured_on_hero_mesh"]["capped_at_50k"], ba["measured_on_hero_mesh"]["full_size_replicate"]
    a("| Resample size | %s | %s |" % ("{:,}".format(cap["n_resampled"]), "{:,}".format(full["n_resampled"])))
    a("| 95%% interval | [%.5f, %.5f] | [%.5f, %.5f] |"
      % (cap["ci95"][0], cap["ci95"][1], full["ci95"][0], full["ci95"][1]))
    a("| Interval width | %.6f | %.6f |" % (cap["width"], full["width"]))
    a("| Width ratio, capped : full | **%.3f** | (√(n/cap) predicts %.3f) |"
      % (ba["measured_on_hero_mesh"]["width_ratio_capped_over_full"],
         ba["measured_on_hero_mesh"]["expected_ratio_sqrt_n_over_cap"]))
    a("")
    a("| Resistance convention | Spearman ρ with measured K_leaf | p |")
    a("|---|---:|---|")
    kv = rcs["kleaf_validation"]
    a("| ℓ/r⁴ (reported) | %s | %s |" % (r3(kv["spearman_r4_vs_measured"][0]), p3(kv["spearman_r4_vs_measured"][1])))
    a("| ℓ/r² (deposit alternative) | %s | %s |" % (r3(kv["spearman_r2_vs_measured"][0]), p3(kv["spearman_r2_vs_measured"][1])))
    a("| Median ratio of the two modelled conductances | %.3f | — |"
      % rcs["agreement_between_conventions"]["median_ratio_r4_over_r2"])
    a("")
    a("*Note.* The graph-identity row is recomputed here directly from `data/analysis_master.csv`. "
      "The corresponding field in `data/graph_metric_audit.json` reports a mean |difference| of "
      "0.0147 with a maximum of 1.0 for the empirical set; that field is **superseded**, because its "
      "script omitted the components correction c/E, and 61 of the 120 traced networks have more than "
      "one component (up to 4,477). With the correction applied the identity is exact to floating "
      "point, and it holds for the **cycle-rank** fraction only — not for the non-bridge loop fraction "
      "reported throughout this study, which is a different quantity. "
      "n = 100 for every association, n = %d for the convention comparison, "
      "n = %d for the crop-edge check. Bootstrap intervals throughout the manuscript are "
      "percentile intervals with B = %d and seed %d, the resampling unit being the "
      "individual Monte Carlo trial, capped at %s trials per replicate. Where a run exceeds "
      "that cap the reported interval is **conservative**, never anti-conservative."
      % (kv["n"], bs["n_leaves"], ba["implementation"]["B"], ba["implementation"]["seed"],
         "{:,}".format(ba["implementation"]["sample_cap"])))
    a("")
    a("---")
    a("")

    # ---------------- S4 -----------------------------------------------------
    a("**Table S4**")
    a("")
    a("*Full Haustorial-Sink Sensitivity: Cavitation Onset by Threshold, by Sink Strength, "
      "and by Host Operating Potential*")
    a("")
    a("| Modelled cavitation threshold (MPa) | Host–parasite gradient required for the first "
      "embolised vessel (MPa) | Multiple of the calibrated K_h required at the illustrative "
      "1.5 MPa gradient |")
    a("|---:|---:|---:|")
    khm = cav["cavitation_onset_Kh_multiple_by_threshold"]
    for t, g in cav["cavitation_onset_gradient_by_threshold"].items():
        m = khm.get(t)
        a("| %s | %.1f | %s |" % (t, g, ("%d×" % m) if m else "none up to 256×"))
    a("")
    a("| Host operating potential ψ_leaf (MPa) | Min ψ without parasite | Min ψ with sink | "
      "Δψ | Vessels embolised without parasite | with sink |")
    a("|---:|---:|---:|---:|---:|---:|")
    for r in cav["leaf_boundary_condition_sweep"]:
        a("| %.1f | %.5f | %.5f | %.5f | %d | %d |"
          % (r["psi_leaf_MPa"], r["baseline_min_interior_psi_MPa"], r["sink_min_interior_psi_MPa"],
             r["delta_min_psi_MPa"], r["baseline_embolised_at_-2.00"], r["sink_embolised_at_-2.00"]))
    a("")
    a("| Threshold-independent sink quantity | Value |")
    a("|---|---|")
    pd_ = cav["patch_depression_law"]
    md = cav["margin_decomposition"]
    a("| Calibrated K_h | %.4f |" % cav["setup"]["calibrated_K_h"])
    a("| Diverted fraction at the illustrative gradient | %.1f%% |" % (100 * cav["setup"]["achieved_diversion"]))
    a("| Minimum interior ψ with no parasite | %.4f MPa |" % cav["baseline_control"]["min_interior_psi_MPa"])
    a("| Depression of the network minimum by the parasite | %.4f MPa |"
      % md["parasite_contribution_at_calibrated_Kh_and_1.5MPa_MPa"])
    a("| Stipulated ψ_leaf − ψ_cavitation gap | %.3f MPa |"
      % md["stipulated_gap_PSI_LEAF_minus_PSI_CAVITATION_MPa"])
    a("| **Parasite share of the reported margin** | **%.1f%%** |" % md["parasite_share_of_total_margin_pct"])
    a("| Patch depression, slope in the gradient | %.4f MPa per MPa |" % pd_["slope_MPa_per_MPa_of_gradient"])
    a("| Patch depression, intercept | %.5f MPa |" % pd_["intercept_MPa"])
    a("| Maximum residual from linearity across 0–12 MPa | %.3f MPa |" % pd_["max_abs_residual_MPa"])
    a("| Analytic per-node reservoir weight K_h/(1 + K_h) | %.4f |"
      % pd_["single_node_analytic_clamp_Kh_over_1_plus_Kh"])
    a("| **Gradient required to reach −2.0 MPa** | **%.2f MPa** |"
      % pd_["gradient_required_to_reach_PSI_CAVITATION_MPa"])
    a("")
    a("| Fractal dimension of the surface row | ⟨k⟩ held at | Smallest K_h multiple with a "
      "critical haustorial density | Critical density there |")
    a("|---:|---:|---:|---:|")
    rows = {}
    for c in srf["cells"]:
        if c["p_c_haustorial_density"] is not None:
            k = round(c["D"], 4)
            if k not in rows or c["k_h_multiple_of_calibrated"] < rows[k][0]:
                rows[k] = (c["k_h_multiple_of_calibrated"], c["p_c_haustorial_density"], c["mean_degree"])
    for k in sorted(rows):
        m, dens, mk = rows[k]
        a("| %.4f | %.4f | %d× | %.4f |" % (k, mk, m, dens))
    a("")
    a("*Note.* All values are computed on the cohort-calibrated synthetic mesh "
      "(*N* = 1,023). The haustorial-density surface reports the fraction of nodes **bearing "
      "a haustorium** at which the collapse criterion is met under the coupled hydraulic "
      "model, which is a different quantity from the removed-node fraction of Tables 3, 4 "
      "and 9 and is not comparable with those values. Mean degree is held essentially "
      "constant across the surface, so the row that first develops a threshold is the one "
      "with the **lowest fractal dimension**, not the least reticulate one. At the "
      "calibrated sink strength no row has a threshold at any density. The linearity of the "
      "patch depression is an arithmetic consequence of specifying K_h *relative* to each "
      "node's own incident conductance, which fixes the reservoir's weight at "
      "K_h/(1 + K_h) per node independently of the network; it is not an emergent property "
      "of venation topology.")
    a("")
    a("---")
    a("")

    # ---------------- S5 -----------------------------------------------------
    a("**Table S5**")
    a("")
    a("*Both Synthetic Size Sweeps With Their Unpinned Architectural Descriptors, and the "
      "Generating-Function Comparisons*")
    a("")
    a("| Sweep | N | D | ⟨k⟩ | Loop fraction | Bridge fraction | Terminal fraction | p_c |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|")
    for s in fsz["sizes"]:
        u = s["unpinned_descriptors"]
        a("| Pinned D and ⟨k⟩ | %s | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f |"
          % ("{:,}".format(s["N"]), s["D"], s["mean_degree"], u["loop_fraction_nonbridge"],
             u["bridge_fraction"], u["terminal_fraction"], s["p_c"]))
    for s in scl["finite_size"]:
        a("| Confounded (depth sets both) | %s | %.3f | — | — | — | — | %.4f |"
          % ("{:,}".format(s["N"]), s["D"], s["p_c"]))
    a("")
    a("| Drift audit of the pinned sweep | Value |")
    a("|---|---|")
    ad = fsz["architecture_drift_audit"]
    a("| D spread achieved across the sweep | %.4f |" % fsz["D_spread_achieved"])
    a("| ⟨k⟩ spread achieved | %.4f |" % fsz["mean_degree_spread_achieved"])
    a("| **Loop-fraction drift** | **%.3f** (%.3f → %.3f) |"
      % (ad["loop_fraction_spread"], ad["loop_fraction_range"][1], ad["loop_fraction_range"][0]))
    a("| Pearson r(loop fraction, p_c) across the sweep | %s |" % r3(ad["pearson_loop_fraction_vs_pc"]))
    a("| p_c spread | %.4f |" % fsz["p_c_spread"])
    a("| Slope of p_c per doubling of N | %.4f |" % fsz["slope_p_c_per_doubling"])
    a("")
    a("| Generating-function comparison | Network | κ = ⟨k²⟩/⟨k⟩ | "
      "Molloy–Reed f_c | Measured |")
    a("|---|---|---:|---:|---:|")
    a("| Confounded sweep, largest network | N = 8,191 | %.3f | %.3f | f_c = %.3f |"
      % (scl["beta_test"]["kappa"], scl["beta_test"]["molloy_reed_fc"], scl["beta_test"]["empirical_fc"]))
    a("| Separately generated mesh | N = 4,095 | %.3f | %.4f | p_c = %.4f |"
      % (rob["theory_comparison"]["kappa_<k2>/<k>"], rob["theory_comparison"]["molloy_reed_fc"],
         rob["theory_comparison"]["measured_pc_random"]))
    a("")
    a("| Empirical cohort, for contrast | ρ with N | p |")
    a("|---|---:|---|")
    for key, lbl in [("spearman_N_x_pc_random", "p_c"), ("spearman_N_x_mean_degree", "⟨k⟩"),
                     ("spearman_N_x_loop_fraction_nonbridge", "Loop fraction"), ("spearman_N_x_D", "D")]:
        a("| %s | %s | %s |" % (lbl, r3(sz[key]["rho"]), p3(sz[key]["p"])))
    a("")
    a("*Note.* **No finite-size claim — convergence or divergence — is made from either "
      "sweep.** Pinning D and ⟨k⟩ does not pin the architecture: loop fraction, itself one "
      "of this study's predictors of the threshold, drifts by 0.131 across the size range "
      "and correlates with p_c at r = .913 over the five sweep points, so size and "
      "reticulation cannot be separated with five points and two moving variables. The "
      "confounded sweep raises N and D together and is reported only to show why it cannot "
      "be read either. f_c is the removal fraction at which the giant component vanishes; "
      "p_c is the fraction at which it falls below half its undamaged size at *P* = .50. "
      "The two are different criteria on the same network and produce different numbers, "
      "which is why the N = 8,191 and N = 4,095 rows are not comparable with one another. "
      "Molloy–Reed assumes a locally tree-like graph while a planar mesh is dense in short "
      "loops, so the correspondence is qualitative and establishes no universality class. "
      "The empirical cohort's threshold rises **weakly with** size, the opposite sign to "
      "the pinned sweep, so the synthetic behaviour does not propagate into the reported "
      "results.")
    a("")

    OUT.write_text("\n".join(W) + "\n", encoding="utf-8")
    print("wrote %s" % OUT.name)
    print("  tables: S1-S5")
    print("  lines : %d" % len(W))


if __name__ == "__main__":
    main()
