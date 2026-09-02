# -*- coding: utf-8 -*-
r"""Part 6 of the Appendix C builder: reticulation and bridge dependence,
reticulation quartiles, the enhancement experiment, the dependence of the gain
on initial architecture, and the largest gainers (Results Tables 8 to 12)."""

from __future__ import annotations

import math

import numpy as np
from scipy import stats


def _partial_spearman(x, y, z):
    a = float(stats.spearmanr(x, y)[0])
    b = float(stats.spearmanr(x, z)[0])
    c = float(stats.spearmanr(y, z)[0])
    return (a - b * c) / math.sqrt((1 - b * b) * (1 - c * c))


def reticulation(C):
    w, num = C["w"], C["num"]
    rho_, pval, check = C["rho"], C["pval"], C["check"]
    V, T7 = C["V"], C["T7"]
    PC, PCD, K, LF, LN, BF = (V["PC"], V["PCD"], V["K"], V["LF"], V["LN"],
                              V["BF"])
    GAP = PC - PCD
    n = len(PC)

    w(r"\section{Reticulation, Bridge Dependence, and the Removal-Mode Gap}"
      r"\label{sec:reticulation}")
    w()
    w(r"""Loop and bridge fraction are complementary by
Equation~\eqref{eq:loopfrac}, so each coefficient involving one is the exact
negative of the other's; both are tabulated because the Results quotes both. The
third quantity is the removal-mode gap $d$ of
Equation~\eqref{eq:paireddiff}.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Reticulation, Bridge Dependence, and Damage Tolerance}}"
      r"\label{tab:reticulation}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{lcccl}")
    w(r"\toprule")
    w(r"Variables correlated & $\rho$ & $t$ & $p$ & Decision on $H_{0}$ \\")
    w(r"\midrule")
    resid = LF - np.polyval(np.polyfit(K, LF, 1), K)
    for label, x, y, key in [
            ("Loop fraction and $p_{c}$ (uniform)", LF, PC, "loop_x_pc_random"),
            ("Bridge fraction and $p_{c}$ (uniform)", BF, PC,
             "bridge_x_pc_random"),
            ("Loop fraction and $p_{c}$ (degree-weighted)", LF, PCD,
             "loop_x_pc_degree_targeted"),
            ("Bridge fraction and $p_{c}$ (degree-weighted)", BF, PCD,
             "bridge_x_pc_degree_targeted"),
            ("Loop fraction and the removal-mode gap", LF, GAP,
             "loop_x_attack_gap"),
            ("Mean degree and the removal-mode gap", K, GAP,
             "mean_degree_x_attack_gap"),
            (r"Residual loop fraction ($\langle k\rangle$ controlled) "
             r"and $p_{c}$", resid, PC,
             "residual_loop_given_mean_degree_x_pc")]:
        r_, p_ = stats.spearmanr(x, y)
        t_ = float(r_) * math.sqrt((n - 2) / (1 - float(r_) ** 2))
        w(r"%s & %s & %s & %s & %s \\"
          % (label, rho_(r_), C["sgn"](t_, 2), pval(p_),
             "Reject" if p_ < .05 else "Fail to reject"))
        check("Reticulation rho, %s" % key, T7[key]["rho"], float(r_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    gp = _partial_spearman(LF, GAP, LN)
    rgn, pgn = stats.spearmanr(GAP, np.exp(LN))
    w(r"""\noindent \textit{Note.} $n = %d$; $df = %d$. The final row regresses
loop fraction on mean degree and correlates the residual with the threshold; its
non-significance follows from the near-collinearity of
Table~\ref{tab:descassoc} and is not evidence that reticulation is unimportant.
The gap relationship is %s with $\log N$ held constant, and the gap itself is
uncorrelated with size ($\rho = %s$, $p$ %s).""" %
      (n, n - 2, rho_(gp), rho_(rgn), pval(pgn)))
    w()


def quartiles(C):
    w, steps, num = C["w"], C["steps"], C["num"]
    describe, check, quartile_cut = C["describe"], C["check"], C["quartile_cut"]
    perc, T8 = C["perc"], C["T8"]

    lf = [float(r["loop_fraction_nonbridge"]) for r in perc]
    q1, q2, q3 = (quartile_cut(lf, 0.25), quartile_cut(lf, 0.50),
                  quartile_cut(lf, 0.75))
    w(r"\section{Damage Tolerance by Reticulation Quartile}\label{sec:quartiles}")
    w()
    w(r"""The percolation cohort was split at the loop-fraction quartile cut
points $Q_{1} = %s$, $Q_{2} = %s$, $Q_{3} = %s$, giving %d networks per group.
Medians are reported because the within-group distributions inherit the
non-normality of Section~\ref{sec:normality}.""" %
      (num(q1, 4), num(q2, 4), num(q3, 4), len(perc) // 4))
    w()

    def band(lo, hi):
        return [r for r in perc
                if (lo is None or float(r["loop_fraction_nonbridge"]) > lo)
                and (hi is None or float(r["loop_fraction_nonbridge"]) <= hi)]

    groups = [("Q1 (least reticulate)", band(None, q1)),
              ("Q2", band(q1, q2)), ("Q3", band(q2, q3)),
              ("Q4 (most reticulate)", band(q3, None))]
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Damage Tolerance by Reticulation Quartile}}"
      r"\label{tab:quartiles}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{lccccc}")
    w(r"\toprule")
    w(r"Quartile & $n$ & $Mdn$ loop fraction & $Mdn$ $\langle k\rangle$ & "
      r"$Mdn$ $p_{c}$ & $Mdn$ $D$ \\")
    w(r"\midrule")
    qmed = []
    for label, grp in groups:
        a = describe([r["loop_fraction_nonbridge"] for r in grp])
        b = describe([r["mean_degree"] for r in grp])
        c_ = describe([r["pc_random"] for r in grp])
        d_ = describe([r["D"] for r in grp])
        qmed.append(c_["Mdn"])
        w(r"%s & %d & %s & %s & %s & %s \\"
          % (label, a["n"], num(a["Mdn"], 3), num(b["Mdn"], 3), num(c_["Mdn"]),
             num(d_["Mdn"], 3)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    for i, qd in enumerate(T8["quartiles"]):
        check("Quartile %d median p_c" % (i + 1), qd["median_pc"], qmed[i])
    absd = qmed[3] - qmed[0]
    relgain = 100.0 * absd / qmed[0]
    check("Quartile absolute difference", T8["absolute_difference"], absd)
    check("Quartile relative gain (%)", T8["relative_gain_pct"], relgain, 0.05)
    w(r"""\noindent \textit{Note.} $D$ is tabulated so that the monotone rise in
$p_{c}$ can be seen not to be a geometry gradient. The formal test of the extreme
groups is in Section~\ref{sec:comparisons}. The Q4--Q1 contrast is""")
    steps(
        r"\tilde{p}_{Q4} - \tilde{p}_{Q1} &= %s-%s = %s"
        % (num(qmed[3]), num(qmed[0]), num(absd)),
        r"\frac{\tilde{p}_{Q4} - \tilde{p}_{Q1}}{\tilde{p}_{Q1}}\times 100"
        r" &= \frac{%s}{%s}\times 100 = %s\%%"
        % (num(absd), num(qmed[0]), "%.2f" % relgain),
    )
    w()


def enhancement(C):
    w, steps, num, esc = C["w"], C["steps"], C["num"], C["esc"]
    describe, check = C["describe"], C["check"]
    pval = C["pval"]
    enh, T9 = C["enh"], C["T9"]

    dpc = [float(r["delta_pc"]) for r in enh]
    Sc = describe([r["pc_current"] for r in enh])
    Ss = describe([r["pc_suggested"] for r in enh])
    Sdel = describe(dpc)
    C["Sc"], C["Ss"], C["Sdel"] = Sc, Ss, Sdel

    w(r"\section{Reticulation Enhancement}\label{sec:enhancement}")
    w()
    w(r"""Each network of the enhancement cohort was evaluated twice at 10,000
trials per arm (as traced, and after the areole-closure construction of
Section~\ref{sec:engine} raised its mean degree to the ceiling
$\langle k\rangle = %.3f$) under common random numbers, so each network is its
own control and the Monte Carlo error cancels from the difference.""" %
      T9["ceiling_mean_degree"])
    w()

    imp = sum(1 for v in dpc if v > 0)
    unch = sum(1 for v in dpc if v == 0)
    wor = sum(1 for v in dpc if v < 0)
    check("Enhancement median before", T9["median_pc_current"], Sc["Mdn"])
    check("Enhancement median after", T9["median_pc_enhanced"], Ss["Mdn"])
    check("Enhancement mean delta", T9["delta_pc"]["M"], Sdel["M"])
    check("Enhancement SD delta", T9["delta_pc"]["SD"], Sdel["SD"])
    check("Enhancement median delta", T9["delta_pc"]["Mdn"], Sdel["Mdn"])
    check("Networks improved", T9["n_improved"], imp, 0.5)
    check("Networks unchanged", T9["n_unchanged"], unch, 0.5)
    check("Networks worsened", T9["n_worsened"], wor, 0.5)
    w(r"""The %d per-network before-and-after pairs, with the edge count added to
each, are tabulated in full as Table~B9 of Appendix~B and are not repeated here.
Loop addition modifies only the edge set, so no part of $\Delta p_{c}$ can be a
size effect. Of the %d networks, %d improved, %d were unchanged and %d worsened;
every unchanged network is one already at or above the ceiling, for which
Equation~\eqref{eq:loopsadded} gives $\Delta E = 0$ and the two arms are the same
graph.""" % (Sdel["n"], Sdel["n"], imp, unch, wor))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Sufficient Sums and Summary Statistics of the "
      r"Enhancement Cohort}}\label{tab:enhsummary}")
    w(r"\small\setlength{\tabcolsep}{7pt}")
    w(r"\begin{tabular}{lccc}")
    w(r"\toprule")
    w(r"Statistic & Before & After & $\Delta p_{c}$ \\")
    w(r"\midrule")
    w(r"$\sum x$ & %s & %s & %s \\"
      % (num(Sc["sum"]), num(Ss["sum"]), num(Sdel["sum"])))
    w(r"$\sum x^{2}$ & %s & %s & %s \\"
      % (num(Sc["sum_sq"], 6), num(Ss["sum_sq"], 6), num(Sdel["sum_sq"], 6)))
    w(r"$M$ & %s & %s & %s \\" % (num(Sc["M"]), num(Ss["M"]), num(Sdel["M"])))
    w(r"$SD$ & %s & %s & %s \\"
      % (num(Sc["SD"]), num(Ss["SD"]), num(Sdel["SD"])))
    w(r"$Mdn$ & %s & %s & %s \\"
      % (num(Sc["Mdn"]), num(Ss["Mdn"]), num(Sdel["Mdn"])))
    w(r"Range & %s--%s & %s--%s & %s--%s \\"
      % (num(Sc["min"]), num(Sc["max"]), num(Ss["min"]), num(Ss["max"]),
         num(Sdel["min"]), num(Sdel["max"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    _cg = Sdel["n"] * Sdel["M"] ** 2
    pct_imp = 100.0 * imp / Sdel["n"]
    check("Percent improved", T9["pct_improved"], pct_imp, 0.05)
    relg = sorted(100.0 * (float(r["pc_suggested"]) - float(r["pc_current"]))
                  / float(r["pc_current"]) for r in enh)
    mid = len(relg) // 2
    mrg = relg[mid] if len(relg) % 2 else (relg[mid - 1] + relg[mid]) / 2.0
    check("Median relative gain (%)", T9["median_relative_gain_pct"], mrg, 0.05)
    w(r"""\noindent Worked computation of the gain, from the third column:""")
    steps(
        r"\overline{\Delta p_{c}} &= \frac{\sum \Delta p_{c}}{n}"
        r" = \frac{%s}{%d} = %s"
        % (num(Sdel["sum"], 6), Sdel["n"], num(Sdel["M"], 6)),
        r"s_{\Delta}^{2} &= \frac{\sum \Delta p_{c}^{2}"
        r"-n\overline{\Delta p_{c}}^{2}}{n-1}"
        r" = \frac{%s-%s}{%d} = %s"
        % (num(Sdel["sum_sq"], 6), num(_cg, 6), Sdel["n"] - 1,
           num(Sdel["SD"] ** 2, 8)),
        r"s_{\Delta} &= \sqrt{%s} = %s"
        % (num(Sdel["SD"] ** 2, 8), num(Sdel["SD"], 6)),
        r"\text{improved} &= \frac{%d}{%d}\times 100 = %s\%%"
        % (imp, Sdel["n"], "%.1f" % pct_imp),
        r"\mathrm{Mdn}\!\left[\frac{p_{c,\text{after}}-p_{c,\text{before}}}"
        r"{p_{c,\text{before}}}\times 100\right] &= %s\%%" % ("%.2f" % mrg),
    )
    w(r"""The relative gain is computed per network and then summarised, not
derived from the column medians; the ratio of the medians is %s\%%, a different
statistic and not the one reported.""" %
      ("%.2f" % (100 * (Ss["Mdn"] - Sc["Mdn"]) / Sc["Mdn"])))
    w()

    # ---- by grade ---------------------------------------------------------
    w(r"\subsection{The Effect by Tracing-Quality Grade}")
    w()
    gr = np.array([r["grade"] for r in enh])
    dp = np.array(dpc)
    w(r"""Grade is the leading flag of the deposit's comma-separated
extraction-quality code: A no vein-level defect, B missing minor veins, C
spurious minor veins, D physical damage. These are defect \emph{types} with
opposite effects on connectivity, not severity levels, so no ordering among B, C
and D is implied.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Reticulation-Enhancement Effect by Tracing-Quality "
      r"Grade}}\label{tab:bygrade}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lcccccc}")
    w(r"\toprule")
    w(r"Grade & $n$ & $Mdn$ before & $Mdn$ after & $Mdn$ $\Delta p_{c}$ & "
      r"\% improved & $Mdn$ $\langle k\rangle_{0}$ \\")
    w(r"\midrule")
    med = C["spa"]["enhancement_mediation"]
    for g in ["A", "B", "C", "D"]:
        sel = [r for r in enh if r["grade"] == g]
        a = describe([r["pc_current"] for r in sel])
        b = describe([r["pc_suggested"] for r in sel])
        c_ = describe([r["delta_pc"] for r in sel])
        k_ = describe([r["mean_degree"] for r in sel])
        pi = 100.0 * sum(1 for r in sel if float(r["delta_pc"]) > 0) / len(sel)
        w(r"%s & %d & %s & %s & %s & %s\%% & %s \\"
          % (g, len(sel), num(a["Mdn"]), num(b["Mdn"]), num(c_["Mdn"]),
             "%.0f" % pi, num(k_["Mdn"], 4)))
        ref = [x for x in T9["by_grade"] if x["grade"] == g][0]
        check("Grade %s median delta" % g, ref["median_delta_pc"], c_["Mdn"])
        check("Grade %s n" % g, ref["n"], len(sel), 0.5)
    w(r"\midrule")
    w(r"Full cohort & %d & %s & %s & %s & %s\%% & n/a \\"
      % (len(enh), num(Sc["Mdn"]), num(Ss["Mdn"]), num(Sdel["Mdn"]),
         "%.0f" % pct_imp))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    H, pk = stats.kruskal(*[dp[gr == g] for g in ["A", "B", "C", "D"]])
    check("Kruskal-Wallis H, grade",
          med["kruskal_on_raw_delta_by_grade"][0], float(H), 0.005)
    w(r"""\noindent \textit{Note.} Differences in the raw change are not
significant: $H = %.3f$, $p$ %s. The operative covariate is initial connectivity,
not tracing quality: grade A starts at the highest median
$\langle k\rangle_{0}$, and by Section~\ref{sec:gain} a denser start gains less.
Testing the residual gain after regressing $\Delta p_{c}$ on baseline mean degree
gives $H = %.3f$, $p$ %s, with grade A carrying the largest positive residual
(%s against %s for grade B), the opposite sign to the artefact
hypothesis.""" %
      (H, pval(pk), med["kruskal_on_residual_delta_by_grade"][0],
       pval(med["kruskal_on_residual_delta_by_grade"][1]),
       C["sgn"](med["residual_median_by_grade"]["A"], 5),
       C["sgn"](med["residual_median_by_grade"]["B"], 5)))
    w()


def gain_dependence(C):
    w, steps, num = C["w"], C["steps"], C["num"]
    rho_, pval, check = C["rho"], C["pval"], C["check"]
    enh, T10 = C["enh"], C["T10"]

    K = np.array([float(r["mean_degree"]) for r in enh])
    D = np.array([float(r["D"]) for r in enh])
    Y = np.array([float(r["delta_pc"]) for r in enh])
    n = len(enh)

    w(r"\section{Dependence of the Gain on Initial Architecture}"
      r"\label{sec:gain}")
    w()
    Z = np.column_stack([np.ones(n), (K - K.mean()) / K.std(ddof=1),
                         (D - D.mean()) / D.std(ddof=1)])
    b = np.linalg.lstsq(Z, Y, rcond=None)[0]
    yh = Z @ b
    r2 = 1 - float(((Y - yh) ** 2).sum()) / float(((Y - Y.mean()) ** 2).sum())
    F = (r2 / 2) / ((1 - r2) / (n - 3))
    sy = Y.std(ddof=1)
    bz = [float(b[1]) / sy, float(b[2]) / sy]
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Dependence of the Threshold Gain on Initial "
      r"Architecture}}\label{tab:gain}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{lcccc}")
    w(r"\toprule")
    w(r"Initial trait & $\rho$ with $\Delta p_{c}$ & $p$ & "
      r"$b$ (per 1 $SD$) & Standardised $\beta$ \\")
    w(r"\midrule")
    for label, x, coef, bs, key in [
            (r"Initial mean degree $\langle k\rangle$", K, b[1], bz[0],
             "spearman_initial_mean_degree_x_delta"),
            ("Fractal dimension $D$", D, b[2], bz[1], "spearman_D_x_delta")]:
        r_, p_ = stats.spearmanr(x, Y)
        w(r"%s & %s & %s & %s & %s \\"
          % (label, rho_(r_), pval(p_), C["sgn"](coef, 5), rho_(bs)))
        check("Gain rho, %s" % key, T10[key]["rho"], float(r_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Gain regression R2", T10["regression_semi_standardized"]["R2"], r2)
    check("Gain regression beta k",
          T10["regression_semi_standardized"]["beta"][0], float(b[1]))
    check("Gain standardised beta k",
          T10["regression_fully_standardized"]["beta"][0], bz[0])
    w(r"""\noindent \textit{Note.} $n = %d$; both columns come from the same
model, the fourth in outcome units and the fifth standardised:""" % n)
    w(r"\begin{equation}\label{eq:gainfit}")
    w(r"\Delta p_{c} = %s %s %s\,z_{\langle k\rangle} + %s\,z_{D},"
      r" \qquad R^{2} = %s,\ F(2,%d) = %.2f"
      % (num(b[0], 5), "-" if b[1] < 0 else "+", num(abs(b[1]), 5),
         num(b[2], 5), num(r2, 4), n - 3, F))
    w(r"\end{equation}")
    w(r"""The gain depends strongly and negatively on initial mean degree, which
is what Equation~\eqref{eq:loopsadded} predicts: a sparser network is further
from the ceiling and receives more edges. $D$ is unrelated. Regressing on
baseline mean degree alone gives $R^{2} = %s$ against %s for the two-predictor
model, so connectivity accounts for essentially all the explained variance. The
clearest individual cases are in Section~\ref{sec:gainers}.""" %
      (num(C["spa"]["enhancement_mediation"]["R2_of_delta_on_baseline_k"], 4),
       num(r2, 4)))
    w()


def top_gainers(C):
    w, num, esc = C["w"], C["num"], C["esc"]
    T12 = C["T12"]
    w(r"\section{Networks With the Largest Threshold Gain}\label{sec:gainers}")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Networks Exhibiting the Largest Threshold Gain From "
      r"Added Reticulation}}\label{tab:gainers}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lrcrccc}")
    w(r"\toprule")
    w(r"Network & $N$ & $\langle k\rangle_{0}$ & $\Delta E$ & Before & After & "
      r"$\Delta p_{c}$ \\")
    w(r"\midrule")
    for r in T12:
        w(r"%s & %s & %s & %s & %s & %s & %s \\"
          % (esc(r["name"]), "{:,}".format(int(r["N"])),
             num(r["mean_degree"], 3), "{:,}".format(int(r["loops_added"])),
             num(r["pc_before"]), num(r["pc_after"]), num(r["delta_pc"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    bad = [r for r in T12 if not r["boundary_ok"]]
    r0 = C["by_name"].get(T12[3]["name"])
    rel = (100.0 * (float(r0["pc_suggested"]) - float(r0["pc_current"]))
           / float(r0["pc_current"])) if r0 else 0.0
    w(r"""\noindent \textit{Note.} Sorted by descending gain; every entry began
near the lower bound of the cohort's mean-degree range. %s falls outside the
crop-edge tolerance of Section~\ref{sec:boundary} (boundary terminal fraction %s
against 0.05), so its extent is more strongly window-bounded than the rest, and
it is the largest-gain entry. The fourth entry, %s, is the network shown as a
before-and-after pair in the Results; its relative gain is
$(%s-%s)/%s \times 100 = %s\%%$, against a cohort median of %s\%%, so it is an
illustration of the mechanism rather than a representative magnitude.""" %
      (", ".join(esc(r["name"]) for r in bad),
       num(bad[0]["boundary_terminal_frac"], 4) if bad else "n/a",
       esc(T12[3]["name"]), num(r0["pc_suggested"]), num(r0["pc_current"]),
       num(r0["pc_current"]), "%.1f" % rel,
       "%.2f" % C["T9"]["median_relative_gain_pct"]))
    w()
