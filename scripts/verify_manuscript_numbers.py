# -*- coding: utf-8 -*-
r"""
verify_manuscript_numbers.py -- check every reported statistic in
MANUSCRIPT_REVISED_SECTIONS.md against the ARCHIVED result files, never against
a previous manuscript version.

Each check names the value, the archive file and key it comes from, and whether
the manuscript string is present. Run this after any edit to the manuscript or
any rerun of an analysis.

    python scripts/verify_manuscript_numbers.py

Exit code 1 if any check fails.  ASCII-only stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MS = ROOT / "MANUSCRIPT_REVISED_SECTIONS.md"


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    text = " ".join(MS.read_text(encoding="utf-8").split())

    rv = load("results_verified.json")
    cl = load("criterion_and_locality.json")
    cav = load("cavitation_sensitivity.json")
    spa = load("second_pass_audit.json")
    frc = load("final_resolution_checks.json")
    rcs = load("resistance_convention_sensitivity.json")

    T3, T5, T7 = rv["T3_attack_thresholds"], rv["T5_predictors"], rv["T7_reticulation_and_bridges"]
    T8, T9, T10 = rv["T8_quartiles"], rv["T9_enhancement"], rv["T10_gain_dependence"]
    T11, T6 = rv["T11_validation"], rv["T6_synthetic_grid"]
    crit, loc = cl["criterion_comparison"], cl["locality_comparison"]
    rep = cl["replication_check_vs_archive"]
    assoc = cl["associations_under_each_criterion"]

    checks = [
        # (label, source, expected string in manuscript)
        ("median p_c uniform", "results_verified T3.random.Mdn",
         "%.4f" % T3["random"]["Mdn"]),
        ("median p_c degree-weighted", "results_verified T3.degree_targeted.Mdn",
         "%.4f" % T3["degree_targeted"]["Mdn"]),
        ("median paired difference", "results_verified T3.difference.Mdn",
         "%.4f" % T3["difference"]["Mdn"]),
        ("uniform-vs-weighted reduction", "results_verified T3 relative_reduction_of_median_pct",
         "%.1f%%" % T3["relative_reduction_of_median_pct"]),
        ("p_c ~ mean degree", "results_verified T5.spearman.mean_degree.rho",
         ".%s" % ("%.3f" % T5["spearman_with_pc_random"]["mean_degree"]["rho"]).split(".")[1]),
        ("p_c ~ D", "results_verified T5.spearman.D.rho",
         ".%s" % ("%.3f" % T5["spearman_with_pc_random"]["D"]["rho"]).split(".")[1]),
        ("regression R2", "results_verified T5.regression R2",
         ".%s" % ("%.3f" % T5["regression_semi_standardized"]["R2"]).split(".")[1]),
        ("loop x targeted p_c", "results_verified T7.loop_x_pc_degree_targeted",
         ".%s" % ("%.3f" % T7["loop_x_pc_degree_targeted"]["rho"]).split(".")[1]),
        ("loop x attack gap", "results_verified T7.loop_x_attack_gap",
         "−.%s" % ("%.3f" % abs(T7["loop_x_attack_gap"]["rho"])).split(".")[1]),
        ("quartile Q1 median", "results_verified T8.quartiles[0].median_pc",
         "%.4f" % T8["quartiles"][0]["median_pc"]),
        ("quartile Q4 median", "results_verified T8.quartiles[3].median_pc",
         "%.4f" % T8["quartiles"][3]["median_pc"]),
        ("quartile relative gain", "results_verified T8.relative_gain_pct",
         "%.1f%%" % T8["relative_gain_pct"]),
        ("enhancement median current", "results_verified T9.median_pc_current",
         "%.4f" % T9["median_pc_current"]),
        ("enhancement median enhanced", "results_verified T9.median_pc_enhanced",
         "%.4f" % T9["median_pc_enhanced"]),
        ("enhancement improved count", "results_verified T9.n_improved",
         "%d improved" % T9["n_improved"]),
        ("enhancement ceiling", "results_verified T9.ceiling_mean_degree",
         "%.3f" % T9["ceiling_mean_degree"]),
        ("gain ~ initial mean degree", "results_verified T10.spearman rho",
         "−.%s" % ("%.3f" % abs(T10["spearman_initial_mean_degree_x_delta"]["rho"])).split(".")[1]),
        ("gain model R2", "results_verified T10.regression R2",
         ".%s" % ("%.3f" % T10["regression_semi_standardized"]["R2"]).split(".")[1]),
        ("resistance check n veins", "results_verified T11.n_veins",
         "{:,}".format(T11["hydraulic_resistance"]["n_veins"])),
        ("K_leaf rho", "results_verified T11.kleaf.rho",
         ".%s" % ("%.3f" % T11["kleaf"]["rho"]).split(".")[1]),
        ("K_leaf n species", "results_verified T11.kleaf.n_species",
         "n = %d species" % T11["kleaf"]["n_species"]),
        ("grid beta mean degree (full)", "results_verified T6.random ols_fully_standardized",
         ".%s" % ("%.3f" % T6["random"]["ols_fully_standardized"]["beta"][0]).split(".")[1]),
        ("grid R2 (full)", "results_verified T6.random ols R2",
         ".%s" % ("%.3f" % T6["random"]["ols_raw"]["R2"]).split(".")[1]),

        ("criterion: median GCC", "criterion_and_locality median_gcc",
         "%.4f" % crit["median_gcc"]),
        ("criterion: median source", "criterion_and_locality median_source",
         "%.4f" % crit["median_source"]),
        ("criterion: spearman", "criterion_and_locality spearman",
         ".%s" % ("%.3f" % crit["spearman"]).split(".")[1]),
        ("criterion: n source lower", "criterion_and_locality n_source_lower",
         "%d of %d" % (crit["n_source_lower"], cl["n"])),
        ("locality: disc1 median", "criterion_and_locality median_disc1",
         "%.4f" % loc["median_disc1"]),
        ("locality: disc10 median", "criterion_and_locality median_disc10",
         "%.4f" % loc["median_disc10"]),
        ("replication spearman", "criterion_and_locality replication",
         ".%s" % ("%.3f" % rep["spearman_gcc_vs_archived"]).split(".")[1]),
        ("assoc disc10 ~ D", "criterion_and_locality assoc.disc10 x D",
         ".%s" % ("%.3f" % assoc["disc10"]["spearman_x_D"][0]).split(".")[1]),

        ("sink: baseline min psi", "cavitation_sensitivity baseline_control",
         "%.4f" % abs(cav["baseline_control"]["min_interior_psi_MPa"])),
        ("sink: patch depression slope", "cavitation_sensitivity patch_depression_law",
         "%.4f" % abs(cav["patch_depression_law"]["slope_MPa_per_MPa_of_gradient"])),
        ("sink: parasite share of margin", "cavitation_sensitivity margin_decomposition",
         "%.1f%%" % cav["margin_decomposition"]["parasite_share_of_total_margin_pct"]),
        ("sink: calibrated K_h", "cavitation_sensitivity setup",
         "%.4f" % cav["setup"]["calibrated_K_h"]),

        ("grade Kruskal p (raw)", "second_pass_audit kruskal_on_raw_delta",
         ".%s" % ("%.3f" % spa["enhancement_mediation"]["kruskal_on_raw_delta_by_grade"][1]).split(".")[1]),
        ("no-C p_c ~ <k>", "second_pass_audit grade_C_sensitivity",
         ".%s" % ("%.3f" % spa["grade_C_sensitivity"]["excluding_any_C_flag"]["spearman_pc_x_mean_degree"][0]).split(".")[1]),
        ("D explained by log N", "second_pass_audit fractal_dimension_audit R2",
         "%d%%" % round(100 * spa["fractal_dimension_audit"]["R2_of_D_on_logN"])),
        ("p_c ~ D given log N", "second_pass_audit partial_pc_x_D_given_logN",
         ".%s" % ("%.3f" % spa["fractal_dimension_audit"]["partial_pc_x_D_given_logN"][0]).split(".")[1]),

        ("K_leaf manuscript cohort n", "final_resolution_checks kleaf_cohorts",
         "n = %d species" % frc["kleaf_cohorts"]["manuscript_cohort"]["n"]),
        ("K_leaf all-leaves rho", "final_resolution_checks kleaf_cohorts",
         ".%s" % ("%.3f" % frc["kleaf_cohorts"]["all_leaves_cohort"]["spearman_r4"][0]).split(".")[1]),
        ("resistance convention r2 rho", "resistance_convention_sensitivity kleaf_validation",
         ".%s" % ("%.3f" % rcs["kleaf_validation"]["spearman_r2_vs_measured"][0]).split(".")[1]),
    ]

    width = max(len(c[0]) for c in checks)
    fails = 0
    for label, source, expected in checks:
        ok = expected in text
        if not ok:
            fails += 1
        print("  %s  %-*s  expects %-28s  [%s]"
              % ("OK  " if ok else "FAIL", width, label, repr(expected), source))

    print()
    print("%d checks, %d failed" % (len(checks), fails))
    if fails:
        print("Manuscript values disagree with the archive. Fix the MANUSCRIPT, "
              "not the archive.")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
