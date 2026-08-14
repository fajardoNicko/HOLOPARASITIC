r"""
build_analysis_master.py — one merged per-leaf table, one cohort-provenance
record, and one verified-statistics file that every number in the Results and in
Appendix C should be read from.

WHY THIS EXISTS
  1. Two different loop-fraction columns were in circulation. The tagged column
     in characterization.csv/cohort_pc.csv and the non-bridge column in
     loop_fraction_perleaf.csv differ slightly, and the draft mixed them (Table 1
     quoted the non-bridge median 0.776 while Table 5 quoted the tagged
     correlation 0.719). This script makes NON-BRIDGE canonical everywhere -- it
     is the definition stated in the Table 1 note and the exact complement of
     bridge fraction -- and recomputes every affected statistic from it.
  2. Four nested cohorts (120 -> 112 -> 105 -> 100) with three different screens
     were defined in three different scripts, so the Results could not state n
     consistently. They are recorded here in one place, with the membership
     differences spelled out.
  3. The crop-edge boundary test reported only a count (105 of 120 within
     tolerance) and never named the failures or checked whether any of them
     survive into an analysis cohort. Three do, including the paper's
     largest-gain leaf.

OUTPUTS
  data/analysis_master.csv     one row per traced leaf, every screen and result
  data/cohort_provenance.json  the four cohorts, their rules, budgets, members
  data/results_verified.json   every Results statistic, recomputed from the above

    C:\laragon\bin\python\python-3.13\python.exe scripts\build_analysis_master.py
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import pandas as pd
from scipy import stats

import config

DATA = config.PATHS.data
LOOP = "loop_fraction_nonbridge"      # the canonical definition


def _r(x, d=4):
    if x is None:
        return None
    x = float(x)
    return None if not np.isfinite(x) else round(x, d)


def desc(x, d=6):
    x = np.asarray(x, float)
    return {"n": int(x.size), "M": _r(x.mean(), d), "SD": _r(x.std(ddof=1), d),
            "Mdn": _r(np.median(x), d), "min": _r(x.min(), d),
            "max": _r(x.max(), d), "sum": _r(x.sum(), d),
            "sum_sq": _r((x ** 2).sum(), d)}


def spearman(a, b):
    rho, p = stats.spearmanr(a, b)
    n = len(a)
    t = rho * np.sqrt((n - 2) / (1 - rho ** 2)) if abs(rho) < 1 else np.inf
    return {"n": n, "rho": _r(rho), "t": _r(t, 3), "df": n - 2, "p": float(p)}


def partial_spearman(x, y, z):
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    rxy = np.corrcoef(rx, ry)[0, 1]
    rxz = np.corrcoef(rx, rz)[0, 1]
    ryz = np.corrcoef(ry, rz)[0, 1]
    # kept to six places: rounding here and again at report time would shift the
    # third decimal (0.50255 -> 0.5025 -> .502 instead of .503)
    return _r((rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2)), 6)


def regress(y, preds, standardize_outcome=False):
    """OLS with z-scored predictors; outcome raw unless asked otherwise."""
    y = np.asarray(y, float)
    Z = [((np.asarray(p, float) - np.mean(p)) / np.std(p, ddof=1))
         for p in preds]
    X = np.column_stack([np.ones(len(y))] + Z)
    yy = (y - y.mean()) / y.std(ddof=1) if standardize_outcome else y
    b, *_ = np.linalg.lstsq(X, yy, rcond=None)
    yhat = X @ b
    r2 = 1 - ((yy - yhat) ** 2).sum() / ((yy - yy.mean()) ** 2).sum()
    k = len(preds)
    F = (r2 / k) / ((1 - r2) / (len(y) - k - 1))
    return {"intercept": _r(b[0], 5), "beta": [_r(v, 5) for v in b[1:]],
            "R2": _r(r2), "F": _r(F, 2), "df": [k, len(y) - k - 1],
            "p": float(stats.f.sf(F, k, len(y) - k - 1)),
            "convention": ("predictors z-scored; outcome "
                           + ("z-scored (fully standardized betas)"
                              if standardize_outcome
                              else "raw (betas are outcome units per 1 SD "
                                   "of predictor)"))}


def main():
    ch = pd.read_csv(os.path.join(DATA, "characterization.csv"))
    lf = pd.read_csv(os.path.join(DATA, "loop_fraction_perleaf.csv"))
    cpc = pd.read_csv(os.path.join(DATA, "cohort_pc.csv"))
    sug = pd.read_csv(os.path.join(DATA, "cohort_suggested.csv"))
    bnd = pd.read_csv(os.path.join(DATA, "boundary_check.csv"))
    grid = pd.read_csv(os.path.join(DATA, "synthetic_grid_pc.csv"))
    syn = pd.read_csv(os.path.join(DATA, "synthetic_pernetwork.csv"))
    rc = pd.read_csv(os.path.join(DATA, "robustness_ceiling.csv"))

    # ---------------- master table ---------------------------------------
    m = ch[["name", "n_nodes", "n_edges", "mean_degree", "degree_sd", "D",
            "effective_conductance", "gcc_fraction", "n_cycles",
            "valid_for_percolation", "validity_note"]].copy()
    m = m.merge(lf[["name", LOOP, "loop_fraction_tagged", "bridge_fraction",
                    "terminal_fraction"]], on="name", how="left")
    m = m.merge(bnd[["name", "is_crop", "quality", "mean_degree_shift",
                     "boundary_terminal_frac"]], on="name", how="left")
    m = m.merge(cpc[["species", "pc_random", "pc_degree", "n_trials"]]
                .rename(columns={"species": "name",
                                 "n_trials": "n_trials_percolation"}),
                on="name", how="left")
    m = m.merge(sug[["species", "k_suggested", "loops_added", "pc_current",
                     "pc_suggested", "delta_pc"]]
                .rename(columns={"species": "name"}), on="name", how="left")

    m["grade"] = m.quality.astype(str).str[0]
    m["boundary_ok"] = ((m.boundary_terminal_frac <= 0.05)
                        & (m.mean_degree_shift.abs() <= 0.05))
    m["in_characterization_112"] = m.valid_for_percolation.astype(bool)
    m["in_percolation_cohort_100"] = m.name.isin(cpc.species)
    sug_valid = sug[(sug.N >= 1000) & (sug.pc_current >= 0.02)].species
    m["in_enhancement_cohort_105"] = m.name.isin(sug_valid)
    m["attack_gap"] = m.pc_random - m.pc_degree
    m = m.sort_values("name")
    mpath = os.path.join(DATA, "analysis_master.csv")
    m.to_csv(mpath, index=False)
    print(f"wrote {mpath}  ({len(m)} leaves, {len(m.columns)} columns)")

    # ---------------- provenance -----------------------------------------
    s112 = set(m[m.in_characterization_112].name)
    s105 = set(m[m.in_enhancement_cohort_105].name)
    s100 = set(m[m.in_percolation_cohort_100].name)
    fails = sorted(m[~m.boundary_ok].name)
    prov = {
        "traced": {"n": int(len(m)), "rule": "all Matos leaves loaded",
                   "note": ("%d of the %d source files are calibrated crop "
                            "windows rather than entire laminae, so network "
                            "extent is bounded by the traced window and "
                            "\"whole-leaf\" is not an accurate description of "
                            "the cohort." % (int(m.is_crop.sum()), len(m)))},
        "characterization_112": {
            "n": len(s112), "rule": "n_edges >= 500 (characterize.py)",
            "trials": None,
            "excluded": sorted(set(m.name) - s112),
            "exclusion_reasons": {r["name"]: r["validity_note"] for _, r in
                                  m[~m.in_characterization_112].iterrows()}},
        "percolation_cohort_100": {
            "n": len(s100),
            "rule": ("n_edges >= 2000 AND n_cycles >= 1 AND window cut-end "
                     "terminal fraction <= 0.05 AND |mean-degree shift| <= 0.05 "
                     "(build_cohort.py)"),
            "trials_per_leaf_per_mode": int(cpc.n_trials.iloc[0]),
            "attacks": ["random", "degree-targeted"],
            "subset_of_112": s100 <= s112},
        "enhancement_cohort_105": {
            "n": len(s105),
            "rule": "N >= 1000 AND current p_c >= 0.02 (run_cohort_suggested.py)",
            "trials_per_leaf": 10000, "attacks": ["random"],
            "subset_of_112": s105 <= s112,
            "superset_of_100": s100 <= s105,
            "in_105_not_in_100": sorted(s105 - s100),
            "excluded": sorted(set(m.name) - s105)},
        "synthetic_reference_network": {
            "n": 1, "N": 1023,
            "trials": {"random": 1000000, "each_targeted": 100000},
            "note": ("the ONLY object evaluated at one million trials; it is not "
                     "an empirical leaf")},
        "synthetic_grid": {"n": int(len(grid)),
                           "rule": "6 mean-degree x 7 generation cells"},
        "hydraulic_validation": {"n_leaves": 119, "n_veins": 5668467,
                                 "skipped": ["Equ_tel (fewer than 50 usable "
                                             "veins)"]},
        "kleaf_validation": {"n_species": 93},
        "boundary_check": {
            "n": int(len(bnd)), "n_within_tolerance": int(m.boundary_ok.sum()),
            "n_outside_tolerance": int((~m.boundary_ok).sum()),
            "tolerances": {"boundary_terminal_frac": 0.05,
                           "mean_degree_shift": 0.05},
            "outside_tolerance": fails,
            "outside_tolerance_but_in_enhancement_cohort":
                sorted(set(fails) & s105),
            "outside_tolerance_but_in_percolation_cohort":
                sorted(set(fails) & s100),
            "note": ("15 of 120 leaves fall outside the crop-edge tolerances; "
                     "three of them remain in the 105-leaf enhancement cohort, "
                     "one of which (Clu_ala) is the largest-gain leaf reported")},
        "nesting": "100 subset of 105 subset of 112 subset of 120",
        "canonical_loop_fraction": (
            "loop_fraction_nonbridge (proportion of edges lying on at least one "
            "cycle). The tagged column in characterization.csv differs slightly "
            "and must not be mixed with it."),
    }
    ppath = os.path.join(DATA, "cohort_provenance.json")
    with open(ppath, "w") as f:
        json.dump(prov, f, indent=2)
    print(f"wrote {ppath}")

    # ---------------- verified statistics --------------------------------
    E = m[m.in_characterization_112]          # n = 112
    C = m[m.in_percolation_cohort_100]        # n = 100
    S = m[m.in_enhancement_cohort_105]        # n = 105

    R = {"_canonical_loop_fraction": LOOP,
         "_generated_by": "scripts/build_analysis_master.py"}

    R["T1_characterization"] = {
        "empirical_n": int(len(E)), "synthetic_n": int(len(syn)),
        "empirical": {
            "D": desc(E.D), "hydraulic_conductance": desc(E.effective_conductance),
            "mean_degree": desc(E.mean_degree), "degree_sd": desc(E.degree_sd),
            "loop_fraction": desc(E[LOOP]),
            "bridge_fraction": desc(E.bridge_fraction),
            "gcc_fraction": desc(E.gcc_fraction), "N": desc(E.n_nodes)},
        "synthetic": {
            "D": desc(syn.D),
            "hydraulic_conductance": desc(syn.effective_conductance),
            "mean_degree": desc(syn.mean_degree), "degree_sd": desc(syn.degree_sd),
            "loop_fraction": desc(syn.loop_fraction_nonbridge),
            "bridge_fraction": desc(syn.bridge_fraction),
            "gcc_fraction": desc(syn.gcc_fraction), "N": desc(syn.N)}}

    R["T2_descriptor_correlations"] = {
        "n": int(len(E)),
        "mean_degree_x_loop": spearman(E.mean_degree, E[LOOP]),
        "loop_x_terminal": spearman(E[LOOP], E.terminal_fraction),
        "loop_x_gcc": spearman(E[LOOP], E.gcc_fraction),
        "mean_degree_x_D": spearman(E.mean_degree, E.D),
        "loop_x_D": spearman(E[LOOP], E.D),
        "loop_x_N": spearman(E[LOOP], E.n_nodes)}

    d = C.pc_random - C.pc_degree
    w = stats.wilcoxon(C.pc_random, C.pc_degree)
    R["T3_attack_thresholds"] = {
        "n": int(len(C)), "trials_per_leaf_per_mode": int(C.n_trials_percolation.iloc[0]),
        "random": desc(C.pc_random), "degree_targeted": desc(C.pc_degree),
        "difference": desc(d),
        "n_positive": int((d > 0).sum()), "n_zero": int((d == 0).sum()),
        "n_negative": int((d < 0).sum()),
        "wilcoxon": {"W": float(w.statistic), "p": float(w.pvalue),
                     "n_nonzero": int((d != 0).sum())},
        "relative_reduction_of_mean_pct": _r(100 * (1 - C.pc_degree.mean()
                                                    / C.pc_random.mean()), 2),
        "relative_reduction_of_median_pct": _r(100 * (1 - C.pc_degree.median()
                                                      / C.pc_random.median()), 2)}

    shap = {k: {"W": _r(stats.shapiro(v)[0], 4), "p": float(stats.shapiro(v)[1])}
            for k, v in {"p_c_random": C.pc_random, "mean_degree": C.mean_degree,
                         "D": C.D, "loop_fraction": C[LOOP]}.items()}
    b_res = np.polyfit(C.mean_degree, C[LOOP], 1)
    resid = C[LOOP] - (b_res[1] + b_res[0] * C.mean_degree)
    R["T5_predictors"] = {
        "n": int(len(C)), "shapiro_wilk": shap,
        "spearman_with_pc_random": {
            "mean_degree": spearman(C.mean_degree, C.pc_random),
            "D": spearman(C.D, C.pc_random),
            "loop_fraction": spearman(C[LOOP], C.pc_random)},
        "partial_spearman": {
            "mean_degree_given_D": partial_spearman(C.mean_degree, C.pc_random, C.D),
            "D_given_mean_degree": partial_spearman(C.D, C.pc_random, C.mean_degree),
            "loop_given_D": partial_spearman(C[LOOP], C.pc_random, C.D)},
        "pearson": {"mean_degree_x_pc": _r(np.corrcoef(C.mean_degree, C.pc_random)[0, 1]),
                    "D_x_pc": _r(np.corrcoef(C.D, C.pc_random)[0, 1]),
                    "mean_degree_x_D": _r(np.corrcoef(C.mean_degree, C.D)[0, 1])},
        "regression_semi_standardized": regress(C.pc_random, [C.mean_degree, C.D]),
        "regression_fully_standardized": regress(C.pc_random, [C.mean_degree, C.D],
                                                 standardize_outcome=True)}

    R["T7_reticulation_and_bridges"] = {
        "n": int(len(C)),
        "loop_x_pc_random": spearman(C[LOOP], C.pc_random),
        "bridge_x_pc_random": spearman(C.bridge_fraction, C.pc_random),
        "loop_x_pc_degree_targeted": spearman(C[LOOP], C.pc_degree),
        "bridge_x_pc_degree_targeted": spearman(C.bridge_fraction, C.pc_degree),
        "loop_x_attack_gap": spearman(C[LOOP], C.attack_gap),
        "bridge_x_attack_gap": spearman(C.bridge_fraction, C.attack_gap),
        "mean_degree_x_attack_gap": spearman(C.mean_degree, C.attack_gap),
        "residual_loop_given_mean_degree_x_pc": spearman(resid, C.pc_random),
        "residual_regression_slope": _r(b_res[0]),
        "LABEL_WARNING": ("loop fraction is POSITIVELY associated with both "
                          "thresholds (+.727 random, +.818 targeted). The "
                          "negative -.818 belongs to BRIDGE fraction vs the "
                          "targeted threshold and the negative -.786 belongs to "
                          "LOOP fraction vs the random-minus-targeted gap.")}

    q = C.copy()
    q["Q"] = pd.qcut(q[LOOP], 4, labels=[1, 2, 3, 4])
    quart = [{"quartile": int(k), "n": int(len(g)),
              "median_loop_fraction": _r(g[LOOP].median()),
              "median_mean_degree": _r(g.mean_degree.median()),
              "median_pc": _r(g.pc_random.median())}
             for k, g in q.groupby("Q", observed=True)]
    q1, q4 = q[q.Q == 1].pc_random, q[q.Q == 4].pc_random
    u = stats.mannwhitneyu(q1, q4, alternative="two-sided")
    R["T8_quartiles"] = {
        "quartiles": quart,
        "mann_whitney": {"U": float(u.statistic), "p": float(u.pvalue),
                         "n1": int(len(q1)), "n2": int(len(q4))},
        "absolute_difference": _r(q4.median() - q1.median()),
        "relative_gain_pct": _r(100 * (q4.median() - q1.median()) / q1.median(), 2)}

    nz = S[S.delta_pc != 0]
    ws = stats.wilcoxon(S.pc_suggested, S.pc_current, zero_method="wilcox")
    grades = [{"grade": g, "n": int(len(gg)),
               "median_pc_current": _r(gg.pc_current.median()),
               "median_pc_enhanced": _r(gg.pc_suggested.median()),
               "median_delta_pc": _r(gg.delta_pc.median()),
               "pct_improved": _r(100 * (gg.delta_pc > 0).mean(), 1)}
              for g, gg in S.groupby("grade")]
    R["T9_enhancement"] = {
        "n": int(len(S)), "trials_per_leaf": 10000,
        "ceiling_mean_degree": 2.811,
        "ceiling_source": "90th percentile of the 100-network percolation cohort",
        "ceiling_percentiles": {
            "P90_percolation_cohort_100": _r(np.percentile(C.mean_degree, 90)),
            "P90_characterization_112": _r(np.percentile(E.mean_degree, 90)),
            "P90_all_120": _r(np.percentile(m.mean_degree, 90))},
        "median_pc_current": _r(S.pc_current.median()),
        "median_pc_enhanced": _r(S.pc_suggested.median()),
        "delta_pc": desc(S.delta_pc),
        "n_improved": int((S.delta_pc > 0).sum()),
        "n_unchanged": int((S.delta_pc == 0).sum()),
        "n_worsened": int((S.delta_pc < 0).sum()),
        "pct_improved": _r(100 * (S.delta_pc > 0).mean(), 1),
        "median_relative_gain_pct": _r(
            (100 * (S.pc_suggested - S.pc_current) / S.pc_current).median(), 2),
        "wilcoxon": {"W": float(ws.statistic), "p": float(ws.pvalue),
                     "n_nonzero": int(len(nz)),
                     "n_zero_discarded": int(len(S) - len(nz))},
        "by_grade": grades,
        "grade_note": ("grade is the LEADING flag of the source dataset's "
                       "comma-separated extraction-quality code: A = no "
                       "vein-level defect, B = missing minor veins, C = spurious "
                       "minor veins, D = physical damage or partial lamina")}

    R["T10_gain_dependence"] = {
        "n": int(len(S)),
        "spearman_initial_mean_degree_x_delta": spearman(S.mean_degree, S.delta_pc),
        "spearman_D_x_delta": spearman(S.D, S.delta_pc),
        "regression_semi_standardized": regress(S.delta_pc, [S.mean_degree, S.D]),
        "regression_fully_standardized": regress(S.delta_pc, [S.mean_degree, S.D],
                                                 standardize_outcome=True)}

    top = S.sort_values("delta_pc", ascending=False).head(6)
    R["T12_top_gainers"] = [
        {"name": r["name"], "N": int(r.n_nodes), "mean_degree": _r(r.mean_degree),
         "loops_added": int(r.loops_added), "pc_before": _r(r.pc_current),
         "pc_after": _r(r.pc_suggested), "delta_pc": _r(r.delta_pc),
         "boundary_ok": bool(r.boundary_ok),
         "boundary_terminal_frac": _r(r.boundary_terminal_frac)}
        for _, r in top.iterrows()]

    R["T6_synthetic_grid"] = {
        "n": int(len(grid)),
        "predictor_decoupling": {"pearson": _r(np.corrcoef(grid.mean_degree,
                                                           grid.D)[0, 1]),
                                 "spearman": _r(stats.spearmanr(grid.mean_degree,
                                                                grid.D)[0])},
        "ranges": {"mean_degree": [_r(grid.mean_degree.min()),
                                   _r(grid.mean_degree.max())],
                   "D": [_r(grid.D.min()), _r(grid.D.max())],
                   "empirical_mean_degree": [_r(E.mean_degree.min()),
                                             _r(E.mean_degree.max())],
                   "empirical_D": [_r(E.D.min()), _r(E.D.max())]},
        "extrapolation_note": ("the grid's connectivity axis reaches <k> = %.2f "
                               "against an empirical maximum of %.2f, so its "
                               "upper third has no empirical counterpart"
                               % (grid.mean_degree.max(), E.mean_degree.max())),
    }
    for attack, col in (("random", "pc_random"), ("degree_targeted", "pc_degree")):
        y = grid[col].values
        X = np.column_stack([np.ones(len(grid)), grid.mean_degree, grid.D])
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        r2 = 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        R["T6_synthetic_grid"][attack] = {
            "spearman_mean_degree": spearman(grid.mean_degree, y),
            "spearman_D": spearman(grid.D, y),
            "ols_raw": {"intercept": _r(b[0], 5), "beta_mean_degree": _r(b[1], 5),
                        "beta_D": _r(b[2], 5), "R2": _r(r2),
                        "F": _r((r2 / 2) / ((1 - r2) / (len(grid) - 3)), 2),
                        "units": "p_c per unit of the raw predictor"},
            "ols_fully_standardized":
                regress(y, [grid.mean_degree, grid.D], standardize_outcome=True)}

    hv = json.load(open(os.path.join(DATA, "hydraulic_validation.json")))["summary"]
    kv = json.load(open(os.path.join(DATA, "kleaf_validation_summary.json")))
    R["T11_validation"] = {
        "hydraulic_resistance": {
            "n_leaves": hv["n_leaves"], "n_veins": hv["total_veins_compared"],
            "n_exact": hv["n_exact"],
            "min_pearson_log_r": hv["min_pearson_log_r"],
            "worst_ratio_cv": hv["worst_ratio_cv"],
            "worst_abs_median_ratio_minus_1": hv["worst_abs_median_ratio_minus_1"],
            "cv_tolerance": hv["cv_tolerance"],
            "skipped": hv["skipped"],
            "defensible_claim": ("agreement to within ~1e-7, i.e. floating-point "
                                 "precision; the correlation alone does not "
                                 "establish equality")},
        "wrong_exponent_control": hv["median_pearson_wrong_exponent_control"],
        "kleaf": {"n_species": kv["n_species"], "rho": _r(kv["spearman_rho"]),
                  "p": kv["spearman_p"],
                  "significant_at_.05": bool(kv["spearman_p"] < 0.05),
                  "reading": "weak AND non-significant; xylem-only model"},
        "boundary": {"n": 120, "n_within": int(m.boundary_ok.sum()),
                     "n_outside": int((~m.boundary_ok).sum()),
                     "outside_in_enhancement_cohort": sorted(set(fails) & s105)}}

    R["T4_sink"] = json.load(open(os.path.join(DATA, "sink_demo.json")))
    sw = pd.read_csv(os.path.join(DATA, "sink_sweep.csv"))
    R["T4_sink_sweep"] = {
        "n_gradients": int(len(sw)),
        "gradient_range_MPa": [float(sw.gradient_MPa.min()),
                               float(sw.gradient_MPa.max())],
        "total_embolized_across_sweep": int(sw.n_embolized.sum()),
        "min_margin_MPa": _r(sw.margin_to_cavitation_MPa.min()),
        "diversion_at_0_MPa": _r(sw.diversion_fraction.iloc[0]),
        "diversion_at_max_gradient": _r(sw.diversion_fraction.iloc[-1]),
        "note": ("diversion is gradient-specific; the 20% figure holds at the "
                 "illustrative 1.5 MPa gradient only")}

    rcm = rc.merge(m[["name", "pc_random"]], left_on="species", right_on="name",
                   how="left")
    R["headroom_diagnostic"] = {
        "n": int(len(rc)),
        "dominant_lever_counts": rc.dominant_lever.value_counts().to_dict(),
        "median_gain_from_reticulation": _r(rc.gain_from_reticulation.median()),
        "median_gain_from_D": _r(rc.gain_from_D.median()),
        "median_pc_measured": _r(rc.pc_measured.median()),
        "median_pc_predicted_by_surface": _r(rc.pc_model_now.median()),
        "median_prediction_bias": _r((rc.pc_model_now - rc.pc_measured).median()),
        "pearson_predicted_vs_measured": _r(np.corrcoef(rc.pc_model_now,
                                                        rc.pc_measured)[0, 1]),
        "measured_median_delta_from_rewiring": _r(S.delta_pc.median()),
        "ratio_predicted_to_measured_gain": _r(
            rc.gain_from_reticulation.median() / S.delta_pc.median(), 2),
        "caveat": ("the response surface over-predicts the measured threshold "
                   "and its predicted reticulation gain is several times the "
                   "gain actually measured by rewiring each leaf; the two must "
                   "not be presented as mutually corroborating")}

    vpath = os.path.join(DATA, "results_verified.json")
    with open(vpath, "w") as f:
        json.dump(R, f, indent=2)
    print(f"wrote {vpath}")

    print("\nkey values")
    print("  loop x pc(random)          %+.4f" % R["T7_reticulation_and_bridges"]["loop_x_pc_random"]["rho"])
    print("  loop x pc(degree-targeted) %+.4f" % R["T7_reticulation_and_bridges"]["loop_x_pc_degree_targeted"]["rho"])
    print("  bridge x pc(targeted)      %+.4f" % R["T7_reticulation_and_bridges"]["bridge_x_pc_degree_targeted"]["rho"])
    print("  loop x attack gap          %+.4f" % R["T7_reticulation_and_bridges"]["loop_x_attack_gap"]["rho"])
    print("  loop x pc (canonical)      %+.4f  (was .719 on the tagged column)"
          % R["T5_predictors"]["spearman_with_pc_random"]["loop_fraction"]["rho"])


if __name__ == "__main__":
    main()
