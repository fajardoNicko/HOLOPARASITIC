# -*- coding: utf-8 -*-
r"""
run_second_pass_audit.py -- confound and robustness battery for the second-pass
scientific audit (SECOND_PASS_AUDIT.md Parts V and VI).

Covers, on the archive only (no simulation is re-run):

  1. QUALITY GRADE STRUCTURE. The source deposit's A-F codes are defect TYPES,
     not severity levels (B = under-segmentation, C = over-segmentation /
     spurious minor veins, D = physical damage). analysis_master keeps only the
     LEADING flag of a comma-separated code, which discards the rest and is not
     a severity ranking. This measures how much is lost and whether any result
     depends on the discarded information.

  2. GRADE-C CONTAMINATION. C inflates connectivity by adding veins that are not
     there. Every connectivity-based result is therefore biased upward on those
     leaves. Reruns the headline associations excluding all C-flagged leaves.

  3. FRACTAL DIMENSION vs NETWORK SIZE. D is rank-correlated with N at 0.88.
     Residualises D on log N and re-tests whether D retains any association with
     p_c, and whether the D result survives at all.

  4. ENHANCEMENT ROBUSTNESS. Re-tests the reticulation gain under every
     defensible subsetting, and separates the baseline-<k> mediation from the
     grade effect with an explicit mediation decomposition.

  5. SIZE CONTROLS on every headline association.

    python scripts/run_second_pass_audit.py

Outputs data/second_pass_audit.json.  ASCII-only stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from scipy import stats

OUT = ROOT / "data" / "second_pass_audit.json"
MASTER = ROOT / "data" / "analysis_master.csv"


def partial_spearman(x, y, z):
    rx, ry, rz = (stats.rankdata(np.asarray(v, float)) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    r, p = stats.pearsonr(ex, ey)
    return round(float(r), 4), float(p)


def sp(x, y):
    r, p = stats.spearmanr(x, y)
    return round(float(r), 4), float(p)


def has_flag(q, letter):
    return letter in {c.strip() for c in str(q).split(",")}


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    d = pd.read_csv(MASTER)
    d["qflags"] = d.quality.fillna("").map(
        lambda q: tuple(sorted(c.strip() for c in str(q).split(",") if c.strip())))
    d["n_flags"] = d.qflags.map(len)
    for L in "ABCDEF":
        d[f"flag_{L}"] = d.quality.fillna("").map(lambda q, L=L: has_flag(q, L))

    P = d[d.in_percolation_cohort_100].copy()
    E = d[d.in_enhancement_cohort_105].copy()
    out = {
        "_purpose": "second-pass confound and robustness battery",
        "_generated_by": "scripts/run_second_pass_audit.py",
    }

    # ---- 1. quality grade structure ---------------------------------------
    multi = d[d.n_flags > 1]
    lost = multi[multi.apply(
        lambda r: r["grade"] != max(r["qflags"]), axis=1)]
    out["grade_structure"] = {
        "n_leaves": int(len(d)),
        "flag_combinations": {",".join(k) if k else "(none)": int(v)
                              for k, v in d.qflags.value_counts().items()},
        "n_multi_flag": int((d.n_flags > 1).sum()),
        "pct_multi_flag": round(float((d.n_flags > 1).mean() * 100), 1),
        "leading_flag_counts": {str(k): int(v)
                                for k, v in d.grade.value_counts().items()},
        "any_C_flag": int(d.flag_C.sum()),
        "leading_grade_C": int((d.grade == "C").sum()),
        "C_hidden_by_leading_flag": int(d.flag_C.sum() - (d.grade == "C").sum()),
        "any_D_flag": int(d.flag_D.sum()),
        "leading_grade_D": int((d.grade == "D").sum()),
        "D_hidden_by_leading_flag": int(d.flag_D.sum() - (d.grade == "D").sum()),
        "ordinality_verdict": (
            "NOT ORDINAL. Per the deposit's data dictionary B = under-"
            "segmentation (>80% of veins correct), C = spurious minor veins "
            "(over-segmentation), D = physical damage <25% of leaf area. These "
            "are orthogonal defect TYPES with opposite effects on connectivity, "
            "so any statement of the form 'A > B > C > D' as a quality gradient "
            "is invalid, and the leading-flag reduction is arbitrary rather "
            "than conservative."),
    }

    # ---- 2. grade-C contamination -----------------------------------------
    def assoc_block(df, label):
        return {
            "label": label, "n": int(len(df)),
            "spearman_pc_x_mean_degree": sp(df.mean_degree, df.pc_random),
            "spearman_pc_x_loop_fraction": sp(df.loop_fraction_nonbridge,
                                              df.pc_random),
            "spearman_pc_x_D": sp(df.D, df.pc_random),
            "partial_pc_x_mean_degree_given_logN": partial_spearman(
                df.mean_degree, df.pc_random, np.log10(df.n_nodes)),
            "partial_pc_x_D_given_logN": partial_spearman(
                df.D, df.pc_random, np.log10(df.n_nodes)),
            "median_pc_random": round(float(df.pc_random.median()), 4),
            "median_mean_degree": round(float(df.mean_degree.median()), 4),
        }

    out["grade_C_sensitivity"] = {
        "full_cohort": assoc_block(P, "all 100"),
        "excluding_any_C_flag": assoc_block(P[~P.flag_C], "no C flag"),
        "grade_A_only": assoc_block(P[P.grade == "A"], "leading grade A"),
        "flag_A_only_single_flag": assoc_block(
            P[(P.n_flags == 1) & (P.grade == "A")], "A and only A"),
        "reading": (
            "C-flagged leaves carry spurious minor veins, which inflates both "
            "mean degree and loop fraction; if the connectivity result were an "
            "artefact of over-segmentation it would weaken on the C-free "
            "subset."),
    }

    # ---- 3. fractal dimension vs network size ------------------------------
    logN = np.log10(P.n_nodes)
    D_resid = P.D - np.polyval(np.polyfit(logN, P.D, 1), logN)
    out["fractal_dimension_audit"] = {
        "spearman_D_x_N": sp(P.n_nodes, P.D),
        "pearson_D_x_logN": [round(float(stats.pearsonr(logN, P.D)[0]), 4),
                             float(stats.pearsonr(logN, P.D)[1])],
        "R2_of_D_on_logN": round(float(np.corrcoef(logN, P.D)[0, 1] ** 2), 4),
        "spearman_pc_x_D_raw": sp(P.D, P.pc_random),
        "spearman_pc_x_D_residualised_on_logN": sp(D_resid, P.pc_random),
        "partial_pc_x_D_given_logN": partial_spearman(P.D, P.pc_random, logN),
        "spearman_D_resid_x_mean_degree": sp(D_resid, P.mean_degree),
        "reading": (
            "D is %.0f%% explained by log network size in this cohort. After "
            "residualising D on log N its association with p_c is reported "
            "below; the raw D-p_c correlation cannot be interpreted as a "
            "geometry effect without this control."
            % (100 * np.corrcoef(logN, P.D)[0, 1] ** 2)),
    }

    # ---- 4. enhancement robustness ----------------------------------------
    def enh_block(df, label):
        dd = df.delta_pc.values
        nz = dd[dd != 0]
        res = {
            "label": label, "n": int(len(df)),
            "improved": int((dd > 0).sum()), "unchanged": int((dd == 0).sum()),
            "worsened": int((dd < 0).sum()),
            "median_delta_pc": round(float(np.median(dd)), 5),
            "median_baseline_mean_degree": round(float(df.mean_degree.median()), 4),
        }
        if nz.size >= 5:
            res["wilcoxon_pratt_p"] = float(
                stats.wilcoxon(dd, zero_method="pratt").pvalue)
            res["sign_test_p"] = float(stats.binomtest(
                int((dd > 0).sum()), int((dd != 0).sum()), 0.5).pvalue)
        return res

    subsets = {
        "full_105": E,
        "excluding_any_C_flag": E[~E.flag_C],
        "leading_grade_A": E[E.grade == "A"],
        "A_and_only_A": E[(E.n_flags == 1) & (E.grade == "A")],
        "excluding_any_D_flag": E[~E.flag_D],
        "A_or_B_only_no_C_no_D": E[(~E.flag_C) & (~E.flag_D)],
        "boundary_ok_only": E[E.boundary_ok == True],  # noqa: E712
    }
    out["enhancement_robustness"] = {k: enh_block(v, k) for k, v in subsets.items()}

    # mediation: does grade survive after conditioning on baseline <k>?
    fit = np.polyfit(E.mean_degree, E.delta_pc, 1)
    E = E.assign(resid=E.delta_pc - np.polyval(fit, E.mean_degree))
    grp = [E.resid[E.grade == g].values for g in sorted(E.grade.unique())
           if (E.grade == g).sum() > 1]
    H, ph = stats.kruskal(*grp)
    r_raw, p_raw = sp(E.mean_degree, E.delta_pc)
    out["enhancement_mediation"] = {
        "spearman_baseline_k_x_delta": [r_raw, p_raw],
        "R2_of_delta_on_baseline_k": round(
            float(np.corrcoef(E.mean_degree, E.delta_pc)[0, 1] ** 2), 4),
        "kruskal_on_raw_delta_by_grade": [
            round(float(stats.kruskal(
                *[E.delta_pc[E.grade == g].values
                  for g in sorted(E.grade.unique())
                  if (E.grade == g).sum() > 1]).statistic), 3),
            float(stats.kruskal(
                *[E.delta_pc[E.grade == g].values
                  for g in sorted(E.grade.unique())
                  if (E.grade == g).sum() > 1]).pvalue)],
        "kruskal_on_residual_delta_by_grade": [round(float(H), 3), float(ph)],
        "residual_median_by_grade": {
            str(g): round(float(E.resid[E.grade == g].median()), 5)
            for g in sorted(E.grade.unique())},
        "baseline_k_median_by_grade": {
            str(g): round(float(E.mean_degree[E.grade == g].median()), 4)
            for g in sorted(E.grade.unique())},
        "reading": (
            "grade differences in the RAW gain are largely explained by grade "
            "differences in baseline connectivity; the residual test asks "
            "whether anything survives that mediation, and its sign tells you "
            "whether the artefact hypothesis (larger gain in worse tracings) "
            "or the diminishing-returns hypothesis is supported."),
    }

    # ---- 5. size controls on every headline association --------------------
    out["size_controls"] = {
        "cohort_n": int(len(P)),
        "N_range": [int(P.n_nodes.min()), int(P.n_nodes.max())],
        "raw": {
            "pc_x_mean_degree": sp(P.mean_degree, P.pc_random),
            "pc_x_loop_fraction": sp(P.loop_fraction_nonbridge, P.pc_random),
            "pc_x_D": sp(P.D, P.pc_random),
            "pc_x_N": sp(P.n_nodes, P.pc_random),
            "attack_gap_x_loop_fraction": sp(P.loop_fraction_nonbridge,
                                             P.attack_gap),
            "attack_gap_x_N": sp(P.n_nodes, P.attack_gap),
        },
        "controlling_logN": {
            "pc_x_mean_degree": partial_spearman(P.mean_degree, P.pc_random, logN),
            "pc_x_loop_fraction": partial_spearman(P.loop_fraction_nonbridge,
                                                   P.pc_random, logN),
            "pc_x_D": partial_spearman(P.D, P.pc_random, logN),
            "attack_gap_x_loop_fraction": partial_spearman(
                P.loop_fraction_nonbridge, P.attack_gap, logN),
        },
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # ---- console ----------------------------------------------------------
    g = out["grade_structure"]
    print("=== 1. quality-grade structure ===")
    print("  multi-flag leaves: %d of %d (%.1f%%)"
          % (g["n_multi_flag"], g["n_leaves"], g["pct_multi_flag"]))
    print("  leaves carrying a C (over-segmentation) flag: %d; classified as "
          "leading-grade C: %d; HIDDEN by the leading-flag rule: %d"
          % (g["any_C_flag"], g["leading_grade_C"], g["C_hidden_by_leading_flag"]))
    print("  leaves carrying a D (damage) flag: %d; leading-grade D: %d; hidden: %d"
          % (g["any_D_flag"], g["leading_grade_D"], g["D_hidden_by_leading_flag"]))

    print("\n=== 2. grade-C contamination sensitivity (percolation cohort) ===")
    for k in ("full_cohort", "excluding_any_C_flag", "grade_A_only",
              "flag_A_only_single_flag"):
        b = out["grade_C_sensitivity"][k]
        print("  %-26s n=%3d  pc~<k> %+.3f  pc~loop %+.3f  pc~D %+.3f  "
              "pc~<k>|logN %+.3f"
              % (b["label"], b["n"], b["spearman_pc_x_mean_degree"][0],
                 b["spearman_pc_x_loop_fraction"][0], b["spearman_pc_x_D"][0],
                 b["partial_pc_x_mean_degree_given_logN"][0]))

    f = out["fractal_dimension_audit"]
    print("\n=== 3. fractal dimension vs size ===")
    print("  Spearman(N, D) = %+.4f ; D is %.0f%% explained by log N"
          % (f["spearman_D_x_N"][0], 100 * f["R2_of_D_on_logN"]))
    print("  pc~D raw %+.4f -> residualised on log N %+.4f (partial %+.4f)"
          % (f["spearman_pc_x_D_raw"][0],
             f["spearman_pc_x_D_residualised_on_logN"][0],
             f["partial_pc_x_D_given_logN"][0]))

    print("\n=== 4. enhancement robustness ===")
    for k, b in out["enhancement_robustness"].items():
        print("  %-24s n=%3d  med delta %.5f  imp/unch/wors %d/%d/%d  "
              "med baseline <k> %.3f%s"
              % (k, b["n"], b["median_delta_pc"], b["improved"],
                 b["unchanged"], b["worsened"], b["median_baseline_mean_degree"],
                 ("  sign p=%.2e" % b["sign_test_p"]) if "sign_test_p" in b else ""))
    m = out["enhancement_mediation"]
    print("  baseline <k> explains R2=%.3f of the gain; Kruskal by grade on RAW "
          "delta p=%.2e, on RESIDUAL delta p=%.2e"
          % (m["R2_of_delta_on_baseline_k"], m["kruskal_on_raw_delta_by_grade"][1],
             m["kruskal_on_residual_delta_by_grade"][1]))
    print("  residual median by grade:", m["residual_median_by_grade"])

    print("\n=== 5. size controls ===")
    for k in out["size_controls"]["raw"]:
        raw = out["size_controls"]["raw"][k]
        ctl = out["size_controls"]["controlling_logN"].get(k)
        print("  %-28s raw %+.4f (p=%.2e)%s"
              % (k, raw[0], raw[1],
                 ("   | logN-controlled %+.4f (p=%.2e)" % (ctl[0], ctl[1]))
                 if ctl else ""))
    print("\nwrote %s" % OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
