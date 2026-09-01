# -*- coding: utf-8 -*-
r"""Part 8 of the Appendix C builder: size dependence, the sensitivity battery,
and the distribution-free comparisons."""

from __future__ import annotations

import numpy as np
from scipy import stats


def size_dependence(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    rho_, pval = C["rho"], C["pval"]
    fz, sm = C["fz"], C["sm"]
    rrl = C["rrl"]["size_confound"]

    w(r"\section{Size Dependence at Fixed and at Varying Architecture}"
      r"\label{sec:size}")
    w()
    w(r"""Two size sweeps were run on the generator. In the first, depth raises
size and $D$ together ($D = %s$ at $N = %s$ to $D = %s$ at $N = %s$), so the
accompanying rise in $p_{c}$ from %s to %s mixes the two and is not
interpretable. The second, tabulated below, pinned $D$ and mean degree at each
size by tuning length ratio and mesh fraction.""" %
      (num(sm["finite_size"][0]["D"], 3), C["mint"](sm["finite_size"][0]["N"]),
       num(sm["finite_size"][-1]["D"], 3),
       C["mint"](sm["finite_size"][-1]["N"]),
       num(sm["finite_size"][0]["p_c"]), num(sm["finite_size"][-1]["p_c"])))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Fixed-Architecture Size Sweep}}\label{tab:size}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{rcccccc}")
    w(r"\toprule")
    w(r"$N$ & $D$ & $\langle k\rangle$ & Loop fraction & $p_{c}$ & 95\% CI & "
      r"10--90\% window \\")
    w(r"\midrule")
    for s in fz["sizes"]:
        w(r"%s & %s & %s & %s & %s & [%s, %s] & %s \\"
          % ("{:,}".format(s["N"]), num(s["D"], 3), num(s["mean_degree"], 3),
             num(s["unpinned_descriptors"]["loop_fraction_nonbridge"], 3),
             num(s["p_c"]), num(s["ci95"][0]), num(s["ci95"][1]),
             num(s["width_0.1_0.9"], 4)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    ad = fz["architecture_drift_audit"]
    check("Fixed-D sweep p_c spread", fz["p_c_spread"],
          fz["sizes"][0]["p_c"] - fz["sizes"][-1]["p_c"], 5e-4)
    bt = sm["beta_test"]
    steps(
        r"\Delta p_{c} &= %s - %s = %s, \qquad"
        r"\frac{\Delta p_{c}}{\text{doubling}} = %s"
        % (num(fz["sizes"][0]["p_c"]), num(fz["sizes"][-1]["p_c"]),
           num(fz["p_c_spread"], 4), num(fz["slope_p_c_per_doubling"], 5)),
    )
    w(r"""\noindent \textit{Note.} %s trials per size over %d density points,
seed %d; the pinned descriptors varied by at most %s in $D$ and %s in mean degree
across a sixteen-fold range of $N$. The decline nonetheless cannot be attributed
to size: pinning $D$ and mean degree does not pin the architecture. Loop fraction
drifts by %s across the range (%s to %s) and is itself a predictor of the
threshold, the two moving together within the sweep at $r = %s$. \textbf{No
finite-size claim (convergence or divergence) is made from this
generator}, and for the same reason no critical exponent is reported.""" %
      ("{:,}".format(fz["n_trials"]), fz["n_densities"], fz["seed"],
       num(fz["D_spread_achieved"], 4),
       num(fz["mean_degree_spread_achieved"], 4),
       num(ad["loop_fraction_spread"], 4), num(ad["loop_fraction_range"][1], 4),
       num(ad["loop_fraction_range"][0], 4),
       num(ad["pearson_loop_fraction_vs_pc"], 4)))
    w()
    w(r"""One quantity from the largest of these networks is quoted in the
Results and must be labelled carefully: the connectivity threshold
$f_{c} = %s$ on the $N = %s$ network is the fraction at which the giant component
\emph{vanishes}, a different criterion from the half-size $p_{c}$ of
Equation~\eqref{eq:criterion}. Against the generating-function prediction, from
the degree ratio $\kappa = \langle k^{2}\rangle/\langle k\rangle = %s$:""" %
      (num(bt["empirical_fc"], 3), C["mint"](bt["N"]), num(bt["kappa"], 3)))
    steps(
        r"f_{c} &= 1 - \frac{1}{\kappa - 1} = 1 - \frac{1}{%s}"
        r" = 1 - %s = %s"
        % (num(bt["kappa"] - 1, 3), num(1.0 / (bt["kappa"] - 1), 4),
           num(1 - 1.0 / (bt["kappa"] - 1), 3)),
    )
    w(r"""against the measured %s. The agreement is qualitative only: the formula
assumes a locally tree-like graph while the planar mesh contains short loops by
construction.""" % num(bt["empirical_fc"], 3))
    w()
    w(r"""This size dependence does not propagate into the empirical results.
Across the percolation cohort the threshold rises \emph{weakly} with size
($\rho = %s$, $p$ %s), the opposite sign to the synthetic sweep; mean degree
and loop fraction are unrelated to size ($\rho = %s$ and %s); and every
architecture--threshold association strengthens under size control
(Table~\ref{tab:partial}).""" %
      (rho_(rrl["spearman_N_x_pc_random"]["rho"]),
       pval(rrl["spearman_N_x_pc_random"]["p"]),
       rho_(rrl["spearman_N_x_mean_degree"]["rho"]),
       rho_(rrl["spearman_N_x_loop_fraction_nonbridge"]["rho"])))
    w()


def sensitivity(C):
    w, num, check = C["w"], C["num"], C["check"]
    rho_, pval = C["rho"], C["pval"]
    cav, spa, rcs, cl = C["cav"], C["spa"], C["rcs"], C["cl"]
    perc, enh = C["perc"], C["enh"]

    w(r"\section{Sensitivity and Robustness Battery}\label{sec:sensitivity}")
    w()
    w(r"""Seven analyses test whether a reported conclusion depends on a
modelling or cohort choice.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Summary of Sensitivity and Robustness Analyses}}"
      r"\label{tab:sensitivity}")
    w(r"\small\setlength{\tabcolsep}{3pt}")
    w(r"\begin{tabular}{p{2.6cm}p{3.2cm}p{4.5cm}p{3.7cm}}")
    w(r"\toprule")
    w(r"Analysis & Comparison & Result & Effect on conclusions \\")
    w(r"\midrule")
    onset = cav["cavitation_onset_gradient_by_threshold"]
    w(r"Cavitation threshold & $-1.00$ to $-3.00$ MPa, calibrated sink & "
      r"Onset gradient rises from %.1f MPa at $-1.00$ to %.1f at $-2.00$ and "
      r"%.1f at $-3.00$ & Absence of embolism is threshold-dependent and "
      r"reported as such \\"
      % (onset["-1.00"], onset["-2.00"], onset["-3.00"]))
    bcs = cav["leaf_boundary_condition_sweep"]
    worst = bcs[-1]
    w(r"Host operating potential & $\psi_{\text{leaf}}$ from $-0.5$ to "
      r"$-2.5$ MPa & At $\psi_{\text{leaf}} = %.1f$ MPa, %d vessels embolise "
      r"with \emph{no} parasite present & The margin is governed by the "
      r"boundary condition, not the parasite \\"
      % (worst["psi_leaf_MPa"], worst["baseline_embolised_at_-2.00"]))
    w(r"Resistance convention & $\ell/r^{4}$ versus $\ell/r^{2}$ & "
      r"$K_{\text{leaf}}$: $\rho = %s$ versus $%s$ ($n = %d$) & None; $p_{c}$ "
      r"does not use conductance at all \\"
      % (rho_(rcs["kleaf_validation"]["spearman_r4_vs_measured"][0]),
         rho_(rcs["kleaf_validation"]["spearman_r2_vs_measured"][0]),
         rcs["kleaf_validation"]["n"]))
    crit = cl["criterion_comparison"]
    w(r"Connectivity criterion & GCC versus source-anchored, identical draws & "
      r"$\rho = %s$; median paired difference %s; source lower in %d of %d & "
      r"None (Section~\ref{sec:criterion}) \\"
      % (rho_(crit["spearman"]),
         C["sgn"](crit["median_paired_difference_source_minus_gcc"]),
         crit["n_source_lower"], cl["n"]))
    loc = cl["locality_comparison"]
    w(r"Damage locality & Dispersed versus contiguous-disc removal & "
      r"One lesion %s, ten lesions %s, versus dispersed %s & Dispersed removal "
      r"is conservative; connectivity result is scope-limited "
      r"(Section~\ref{sec:locality}) \\"
      % (num(loc["median_disc1"]), num(loc["median_disc10"]),
         num(loc["median_random_gcc"])))
    gcs = spa["grade_C_sensitivity"]
    er = spa["enhancement_robustness"]
    w(r"Over-segmentation & Excluding every C-flagged network & "
      r"$p_{c}\sim\langle k\rangle$ rises from %s to %s; median "
      r"$\Delta p_{c}$ from %s to %s & None; both principal results "
      r"strengthen \\"
      % (rho_(gcs["full_cohort"]["spearman_pc_x_mean_degree"][0]),
         rho_(gcs["excluding_any_C_flag"]["spearman_pc_x_mean_degree"][0]),
         num(er["full_105"]["median_delta_pc"]),
         num(er["excluding_any_C_flag"]["median_delta_pc"])))
    sub = [r for r in perc if float(r["gcc_fraction"]) > 0.99]
    rsub = float(stats.spearmanr([float(r["pc_random"]) for r in sub],
                                 [float(r["mean_degree"]) for r in sub])[0])
    sub2 = [r for r in enh if float(r["gcc_fraction"]) > 0.99]
    d2 = [float(r["delta_pc"]) for r in sub2]
    check("Baseline-fragmentation subset rho", 0.731, rsub, 0.001)
    w(r"Baseline fragmentation & Excluding baseline GCC fraction "
      r"$\leq .99$ & $p_{c}\sim\langle k\rangle = %s$ ($n = %d$); "
      r"$\Delta p_{c}$ median %s, %d improved / %d unchanged / %d worsened "
      r"($n = %d$) & None \\"
      % (rho_(rsub), len(sub), num(float(np.median(d2))),
         sum(1 for v in d2 if v > 0), sum(1 for v in d2 if v == 0),
         sum(1 for v in d2 if v < 0), len(sub2)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Embolism Onset Gradient by Stipulated Cavitation "
      r"Threshold}}\label{tab:cavsens}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{lcccccccc}")
    w(r"\toprule")
    keys = ["-1.00", "-1.10", "-1.25", "-1.50", "-1.75", "-2.00", "-2.50",
            "-3.00"]
    w(r"$\psi_{\text{cav}}$ (MPa) & "
      + " & ".join("$-$%s" % k.lstrip("-") for k in keys) + r" \\")
    w(r"\midrule")
    w(r"Onset gradient (MPa) & "
      + " & ".join(("%.1f" % onset[k]) if onset[k] is not None else "---"
                   for k in keys) + r" \\")
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    gs = spa["grade_structure"]
    w(r"""\noindent \textit{Note.} The absence of embolism reported in
Section~\ref{sec:sink} is specific to thresholds at or below $-1.10$ MPa within
the 0--3 MPa sweep. A threshold at or above the boundary condition of $-1.0$ MPa
makes the healthy leaf embolise, so it is not freely choosable. At
$\psi_{\text{leaf}} = %.1f$ MPa the baseline solve embolises %d vessels against
%d with the sink attached, a parasite contribution of %d. On the grade
battery: the C flag marks spurious minor veins, which would inflate connectivity,
so an artefact would \emph{weaken} the result on the C-free subset; it
strengthens instead. The flags are not a gradient: %d of %d networks carry
more than one (%s\%%), and the leading-flag reduction hides %d C-flagged and %d
D-flagged networks behind another letter.""" %
      (worst["psi_leaf_MPa"], worst["baseline_embolised_at_-2.00"],
       worst["sink_embolised_at_-2.00"],
       worst["sink_embolised_at_-2.00"] - worst["baseline_embolised_at_-2.00"],
       gs["n_multi_flag"], gs["n_leaves"], "%.1f" % gs["pct_multi_flag"],
       gs["C_hidden_by_leading_flag"], gs["D_hidden_by_leading_flag"]))
    w()


def comparisons(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    pval = C["pval"]
    V = C["V"]
    PC, PCD, LF = V["PC"], V["PCD"], V["LF"]
    enh = C["enh"]
    n = len(PC)

    w(r"\section{Paired and Group Comparisons}\label{sec:comparisons}")
    w()
    dvec = PC - PCD
    Wst, pw = stats.wilcoxon(dvec)
    nz = int((dvec != 0).sum())
    dp = np.array([float(r["delta_pc"]) for r in enh])
    Wst2, pw2 = stats.wilcoxon(dp[dp != 0])
    Wp, pwp = stats.wilcoxon(dp, zero_method="pratt")
    q1c, q3c = float(np.quantile(LF, .25)), float(np.quantile(LF, .75))
    g1, g4 = PC[LF <= q1c], PC[LF > q3c]
    U, pu = stats.mannwhitneyu(g1, g4, alternative="two-sided")
    n_gt = int(np.sum(g4[:, None] > g1[None, :]))
    n_lt = int(np.sum(g4[:, None] < g1[None, :]))
    cliff = (n_gt - n_lt) / float(len(g1) * len(g4))
    gr = np.array([r["grade"] for r in enh])
    H, pk = stats.kruskal(*[dp[gr == g] for g in ["A", "B", "C", "D"]])
    check("Wilcoxon W, removal modes", C["T3"]["wilcoxon"]["W"], float(Wst), 0.5)
    check("Wilcoxon nonzero pairs, removal modes",
          C["T3"]["wilcoxon"]["n_nonzero"], nz, 0.5)
    check("Mann-Whitney U, quartiles", C["T8"]["mann_whitney"]["U"],
          float(U), 0.5)
    check("Cliff's delta, quartiles",
          C["rrl"]["effect_sizes"]["loop_quartiles_Q1_vs_Q4"]["cliffs_delta"],
          cliff)
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Distribution-Free Comparisons Reported in the Results}}"
      r"\label{tab:tests}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{llcccl}")
    w(r"\toprule")
    w(r"Comparison & Test & $n$ & Statistic & $p$ & Effect size \\")
    w(r"\midrule")
    w(r"Uniform vs.\ degree-weighted & Wilcoxon signed-rank & %d & $W = %d$ & "
      r"%s & $r_{rb} = 1.00$ \\" % (nz, int(Wst), pval(pw)))
    w(r"Before vs.\ after enhancement & Wilcoxon signed-rank & %d & $W = %d$ & "
      r"%s & $r_{rb} \approx 1.00$ \\"
      % (int((dp != 0).sum()), int(Wst2), pval(pw2)))
    w(r"Before vs.\ after, Pratt & Wilcoxon signed-rank & %d & $W = %d$ & %s & "
      r"--- \\" % (len(dp), int(Wp), pval(pwp)))
    w(r"Quartile 1 vs.\ quartile 4 & Mann--Whitney & %d, %d & $U = %d$ & %s & "
      r"$\delta = %s$ \\"
      % (len(g1), len(g4), int(U), pval(pu), num(cliff, 3)))
    w(r"$\Delta p_{c}$ across quality grades & Kruskal--Wallis & %d & "
      r"$H = %.3f$ & %s & --- \\" % (len(dp), H, pval(pk)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    steps(
        r"r_{rb} &= \frac{%d}{%d}-\frac{%d}{%d} = 1.00"
        % (int((dvec > 0).sum()), n, int((dvec < 0).sum()), n),
        r"\delta &= \frac{\#(x_{4}>x_{1})-\#(x_{4}<x_{1})}{n_{1}n_{4}}"
        r" = \frac{%d-%d}{%d\times%d} = \frac{%d}{%d} = %s"
        % (n_gt, n_lt, len(g1), len(g4), n_gt - n_lt,
           len(g1) * len(g4), num(cliff, 4)),
    )
    w(r"""\noindent \textit{Note.} The first comparison uses the %d non-zero
differences of Table~B8; the second the %d non-zero differences of
Table~B9, and the third repeats it under the Pratt treatment,
which retains all %d and gives the same conclusion. In both signed-rank rows
$W = 0$, the smallest value the statistic can take: every signed rank fell on the
same side. $r_{rb}$ records direction only; the magnitude is
$Mdn\ d = %s$. Of the %d cross-quartile pairs, %d favour the more reticulate
quartile and %d the less, so the two distributions are nearly disjoint.""" %
      (nz, int((dp != 0).sum()), len(dp), num(float(np.median(dvec)), 4),
       len(g1) * len(g4), n_gt, n_lt))
    w()


def sign_test(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    enh = C["enh"]
    dp = np.array([float(r["delta_pc"]) for r in enh])
    gr = np.array([r["grade"] for r in enh])
    ga = dp[gr == "A"]
    a_imp = int((ga > 0).sum())
    a_unc = int((ga == 0).sum())
    a_wor = int((ga < 0).sum())
    a_m = a_imp + a_wor
    a_p = float(stats.binomtest(a_imp, a_m, 0.5).pvalue)
    ROB = C["spa"]["enhancement_robustness"]["A_and_only_A"]
    check("Grade-A improved", ROB["improved"], a_imp, 0.5)
    check("Grade-A unchanged", ROB["unchanged"], a_unc, 0.5)
    check("Grade-A worsened", ROB["worsened"], a_wor, 0.5)
    check("Grade-A sign-test p", ROB["sign_test_p"], a_p, 1e-6)

    w(r"\section{Exact Sign Test on the Grade-A Subset}\label{sec:signtest}")
    w()
    w(r"""The grade-A subset carries no vein-level defect flag and is where an
artefact explanation of the enhancement result has least purchase. It is small,
so direction is tested by the exact sign test of
Equation~\eqref{eq:sign}. Of its %d networks, %d improved, %d were unchanged and
%d worsened; the unchanged carry no sign and are excluded, leaving $m = %d$
informative pairs of which $k = %d$ favour the enhanced graph.""" %
      (len(ga), a_imp, a_unc, a_wor, a_m, a_imp))
    steps(
        r"p &= 2\,P(X \geq %d), \qquad X \sim \mathrm{Binomial}(%d, 0.5)"
        % (a_imp, a_m),
        r"&= 2\binom{%d}{%d}\left(\tfrac{1}{2}\right)^{%d}"
        r" = \frac{2}{%s} = %.8f" % (a_m, a_imp, a_m,
                                     "{:,}".format(2 ** a_m), a_p),
    )
    w(r"""Because every informative pair moved the same way the test attains its
smallest possible value for this sample size, so the $p$-value is a function of
$m$ alone. It establishes direction, not magnitude; the magnitude is
$Mdn\ \Delta p_{c} = %s$, the smallest of the four grades, which is the
diminishing-returns pattern Section~\ref{sec:gain} predicts for a subset starting
at the highest baseline connectivity.""" % num(float(np.median(ga)), 4))
    w()
