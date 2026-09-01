# -*- coding: utf-8 -*-
r"""Part 9 of the Appendix C builder: weight concentration, collinearity, trial
budgets and interval construction, the separation interval, and figure logic."""

from __future__ import annotations

import math

import numpy as np


def concentration(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    GMA = C["gma"]["targeted_attack_axis"]
    gd, gb = GMA["degree"], GMA["betweenness"]

    w(r"\section{Concentration of the Removal Weights}\label{sec:concentration}")
    w()
    check("Gini, degree weights", 0.274, gd["weight_gini"])
    check("Gini, betweenness weights", 0.754, gb["weight_gini"])
    check("Max/mean, degree weights", 2.4, gd["weight_max"], 0.05)
    check("Max/mean, betweenness weights", 29.4, gb["weight_max"], 0.05)
    check("Distinct degree weights", 6, gd["n_distinct_weights"], 0.5)
    check("Distinct betweenness weights", 619, gb["n_distinct_weights"], 0.5)
    w(r"""How far a weighted mode departs from uniform removal depends on how
unevenly the weights of Equation~\eqref{eq:clip} are spread, measured here by
Equation~\eqref{eq:gini}.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Weight Concentration on the Synthetic Reference Network "
      r"($N = %d$)}}\label{tab:gini}" % GMA["N"])
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lcccccc}")
    w(r"\toprule")
    w(r"Weighting & Distinct values & Largest tie & Gini & Max & $SD$ & "
      r"Realised at $\rho = .20$ \\")
    w(r"\midrule")
    for lbl, g in (("Degree", gd), ("Betweenness", gb)):
        w(r"%s & %d & %s & %s & %s & %s & %s \\"
          % (lbl, g["n_distinct_weights"],
             num(g["largest_tied_group_fraction"], 3), num(g["weight_gini"], 4),
             num(g["weight_max"], 3), num(g["weight_sd"], 4),
             num(g["realised_at_nominal_0.20"], 4)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    _N = GMA["N"]
    lines = []
    for _lbl, _g in (("degree", gd), ("betweenness", gb)):
        _sad = _g["weight_gini"] * 2 * _N * _N * _g["weight_mean"]
        lines.append(
            r"G_{\text{%s}} &= \frac{\sum_{i}\sum_{j}"
            r"\lvert w_{i}-w_{j}\rvert}{2n^{2}\bar{w}}"
            r" = \frac{%s}{2(%d)^{2}(%s)} = \frac{%s}{%s} = %s"
            % (_lbl, "{:,.0f}".format(_sad), _N, num(_g["weight_mean"], 1),
               "{:,.0f}".format(_sad), "{:,.0f}".format(2 * _N * _N),
               num(_g["weight_gini"], 4)))
    steps(*lines)
    w(r"""\noindent \textit{Note.} Weights are normalised to a mean of one, so
the maximum column is the ratio of the largest weight to the mean. Degree takes
only %d distinct values (a planar venation graph has maximum degree four to
five), and %s of nodes fall in a single tied group, so degree-weighted removal
is barely distinguishable from uniform removal, which is why the paired
difference of Table~\ref{tab:pcsummary} is small in absolute terms while being
perfectly consistent in direction. Betweenness takes %d distinct values with a
maximum %s times the mean. Because Equation~\eqref{eq:clip} clips at unity, a
nominal $\rho = .20$ realises %s under degree weighting but only %s under
betweenness weighting, which is why Table~\ref{tab:reference} carries both
columns.""" %
      (gd["n_distinct_weights"], num(gd["largest_tied_group_fraction"], 3),
       gb["n_distinct_weights"], num(gb["weight_max"], 1),
       num(gd["realised_at_nominal_0.20"], 4),
       num(gb["realised_at_nominal_0.20"], 4)))
    w()


def collinearity(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    rho_ = C["rho"]
    K, DD = C["V"]["K"], C["V"]["DD"]
    COLL = C["rrl"]["collinearity"]

    w(r"\section{Collinearity Between the Two Predictors}"
      r"\label{sec:collinearity}")
    w()
    rkd = float(np.corrcoef(K, DD)[0, 1])
    vif = 1.0 / (1.0 - rkd * rkd)
    lf_vif = 1.0 / (1.0 - COLL["pearson_meandegree_x_loopfraction"] ** 2)
    check("Pearson r, mean degree x D", COLL["pearson_meandegree_x_D"], rkd)
    check("VIF, two-predictor model", COLL["VIF"], vif)
    w(r"""Equation~\eqref{eq:empfit} enters mean degree and $D$ together, so the
claim that its coefficients are individually interpretable is checked through
Equation~\eqref{eq:vif}:""")
    steps(
        r"\mathrm{VIF} &= \frac{1}{1-r^{2}} = \frac{1}{1-(%s)^{2}}"
        r" = \frac{1}{%s} = %s"
        % (num(rkd, 6), num(1 - rkd * rkd, 6), num(vif, 6)),
    )
    w(r"""against the conventional threshold of 5, so collinearity is negligible.
The counterfactual is worth stating: loop fraction and mean degree correlate at
$\rho = %s$ and $r = %s$, so entering both would give""" %
      (rho_(COLL["spearman_meandegree_x_loopfraction"]),
       rho_(COLL["pearson_meandegree_x_loopfraction"])))
    w(r"\begin{equation}")
    w(r"\mathrm{VIF} = \frac{1}{1-(%s)^{2}} = \frac{1}{%s} = %s"
      % (num(COLL["pearson_meandegree_x_loopfraction"], 4),
         num(1 - COLL["pearson_meandegree_x_loopfraction"] ** 2, 6),
         num(lf_vif, 2)))
    w(r"\end{equation}")
    w(r"""nearly %d times that threshold, at which the individual coefficients
would be uninterpretable. By Equations~\eqref{eq:loopfrac}
and~\eqref{eq:meandeg} the two are readings of one edge budget, and mean degree
is reported because it has the closed-form relationship to the node
count.""" % int(lf_vif / 5))
    w()


def budgets(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    mint = C["mint"]
    summ, tci = C["summ"], C["tci"]
    ba = C["frc"]["bootstrap_audit"]
    Su, Sd, Sc = C["Su"], C["Sd"], C["Sc"]

    w(r"\section{Monte Carlo Budgets, Standard Error, and Interval "
      r"Construction}\label{sec:budgets}")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Trial Budgets, Thresholds, and Worst-Case Monte Carlo "
      r"Standard Error}}\label{tab:budgets}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{llrcc}")
    w(r"\toprule")
    w(r"Analysis set & Removal mode & $N_{\text{trials}}$ & $p_{c}$ & "
      r"$\mathrm{SE}(\hat{P})$ \\")
    w(r"\midrule")
    for label, mode, nt, val in [
            (r"Percolation cohort ($n=100$)", "Uniform", 2400,
             num(Su["Mdn"]) + " (Mdn)"),
            (r"Percolation cohort ($n=100$)", "Degree-weighted", 2400,
             num(Sd["Mdn"]) + " (Mdn)"),
            (r"Enhancement cohort ($n=105$)", "Uniform, per arm", 10000,
             num(Sc["Mdn"]) + " (Mdn)"),
            (r"Synthetic grid ($n=42$)", "Uniform, per network", 3200,
             r"see Table~\ref{tab:grid}"),
            (r"Coupled density surface", "Hydraulic, per cell", 6000,
             r"see Table~\ref{tab:surface}"),
            (r"Synthetic reference", "Degree-weighted", 100000,
             num(tci["results"]["degree"]["p_c"])),
            (r"Synthetic reference", "Betweenness-weighted", 100000,
             num(tci["results"]["betweenness"]["p_c"]) + " nom."),
            (r"Synthetic reference", "Uniform", 1000000,
             num(summ["p_c_random"]))]:
        w(r"%s & %s & %s & %s & %s \\"
          % (label, mode, "{:,}".format(nt), val,
             num(math.sqrt(0.25 / nt), 5)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("MCSE at 2,400 trials", 0.0102, math.sqrt(0.25 / 2400), 5e-5)
    check("MCSE at 10,000 trials", 0.0050, math.sqrt(0.25 / 10000), 5e-5)
    w(r"""\noindent \textit{Note.} $\mathrm{SE}$ is Equation~\eqref{eq:mcse} at
its maximum $\hat{P} = 0.50$, which is where the threshold is read; it is on the
collapse-probability scale, not the threshold scale.""")
    steps(
        r"\mathrm{SE}_{2400} &= \sqrt{\frac{0.25}{2{,}400}} = %s, \qquad"
        r"\mathrm{SE}_{10000} = \sqrt{\frac{0.25}{10{,}000}} = %s"
        % (num(math.sqrt(0.25 / 2400), 6), num(math.sqrt(0.25 / 10000), 6)),
    )
    w(r"""The enhancement cohort is run at the higher budget because its estimand
is a paired difference of order $0.01$, comparable at 2,400 trials to the
worst-case error itself. Its two arms additionally share one sequence of removal
draws, so that error is common to both and cancels from the difference.""")
    w()
    imp = ba["implementation"]
    hm = ba["measured_on_hero_mesh"]
    w(r"""\noindent \textit{Bootstrap audit.} Intervals are percentile bootstrap
intervals with $B = %d$ resamples and seed %d, the resampling unit being the
individual trial drawn with replacement. The implementation caps each replicate
at %s trials, so where a run exceeds that budget the replicate is smaller than
the dataset and the interval is too wide by approximately $\sqrt{n/%s}$.
Measured on the reference network at %s trials:""" %
      (imp["B"], imp["seed"], "{:,}".format(imp["sample_cap"]),
       # Inside math a bare comma is punctuation and takes trailing space, so
       # the thousands separator has to be braced as it is in the display rows.
       mint(imp["sample_cap"]), "{:,}".format(hm["n_trials"])))
    steps(
        r"\text{ratio}_{\text{observed}} &= \frac{%s}{%s} = %s, \qquad"
        r"\text{ratio}_{\text{predicted}} = \sqrt{\frac{%s}{%s}} = %s"
        % (num(hm["capped_at_50k"]["width"], 6),
           num(hm["full_size_replicate"]["width"], 6),
           num(hm["width_ratio_capped_over_full"], 3),
           "{:,}".format(hm["n_trials"]), "{:,}".format(imp["sample_cap"]),
           num(hm["expected_ratio_sqrt_n_over_cap"], 3)),
    )
    w(r"""Every affected interval is therefore \emph{conservative} and none is
anti-conservative: the 100,000-trial weighted modes are inflated by roughly %s
and the 1,000,000-trial uniform run by roughly %s.""" %
      (num(math.sqrt(100000.0 / imp["sample_cap"]), 2),
       num(math.sqrt(1000000.0 / imp["sample_cap"]), 2)))
    w()


def dynamics(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    dyn = C["dyn"]
    w(r"\section{Supplementary: Modelled Separation Between Fragmentation and "
      r"Total Loss}\label{sec:dynamics}")
    w()
    w(r"""Exploratory, reported in the Supplementary Materials, and not a
biological finding. Given two removal fractions on one network and a stipulated
growth law, how far apart in growth-time are the two crossings? Infestation is
logistic growth in the affected node fraction, with closed-form solution and
inverse:""")
    w(r"\begin{equation}\label{eq:logisticode}")
    w(r"\frac{d\rho}{dt} = r\,\rho\,(1-\rho), \qquad \rho(0) = \rho_{0}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:logisticsol}")
    w(r"\rho(t) = \frac{1}{1 + A e^{-rt}}, \qquad A = \frac{1-\rho_{0}}{\rho_{0}}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:crossingtime}")
    w(r"t^{*} = \frac{1}{r}\,\ln\!\left[\frac{\text{target}}"
      r"{1-\text{target}}\cdot\frac{1-\rho_{0}}{\rho_{0}}\right]")
    w(r"\end{equation}")
    w(r"""The separation is the difference of two such times, at $p_{c} = %s$ and
at the vanishing fraction $f_{c} = %s$, both on the \textbf{synthetic reference
network} rather than the empirical cohort.""" %
      (num(dyn["p_c"]), num(dyn["f_c"])))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Modelled Separation Interval Across Stipulated Growth "
      r"Rates}}\label{tab:dynamics}")
    w(r"\small\setlength{\tabcolsep}{7pt}")
    w(r"\begin{tabular}{lccc}")
    w(r"\toprule")
    w(r"Growth rate & $t$ at $p_{c}$ & $t$ at $f_{c}$ & Separation \\")
    w(r"\midrule")
    for key in sorted(dyn["rates"], key=lambda k: dyn["rates"][k]["r"]):
        v = dyn["rates"][key]
        w(r"%s ($r = %.2f$) & %s & %s & %s \\"
          % (key.split(" ")[0].capitalize(), v["r"], num(v["t_c"], 2),
             num(v["t_wilt"], 2), num(v["window"], 2)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    v = dyn["rates"]["moderate (r=0.25)"]
    A = (1 - dyn["rho0"]) / dyn["rho0"]
    tc_arg = (dyn["p_c"] / (1 - dyn["p_c"])) * A
    tw_arg = (dyn["f_c"] / (1 - dyn["f_c"])) * A
    check("Dynamics window, moderate", 4.35, v["window"], 0.005)
    w(r"""\noindent Worked example at the moderate rate, with
$\rho_{0} = %s$ so $A = %s$:""" % (num(dyn["rho0"], 2), num(A, 1)))
    steps(
        r"t_{c} &= \frac{1}{%.2f}\ln\!\left[\frac{%s}{1-%s}\times %s\right]"
        r" = \frac{%s}{%.2f} = %s"
        % (v["r"], num(dyn["p_c"], 4), num(dyn["p_c"], 4), num(A, 1),
           num(math.log(tc_arg), 4), v["r"], num(v["t_c"], 4)),
        r"t_{\text{loss}} &= \frac{1}{%.2f}\ln\!\left[\frac{%s}{1-%s}"
        r"\times %s\right] = \frac{%s}{%.2f} = %s"
        % (v["r"], num(dyn["f_c"], 4), num(dyn["f_c"], 4), num(A, 1),
           num(math.log(tw_arg), 4), v["r"], num(v["t_wilt"], 4)),
        r"\text{separation} &= %s - %s = %s"
        % (num(v["t_wilt"], 4), num(v["t_c"], 4), num(v["window"], 4)),
    )
    w(r"""\noindent \textit{Note.} \textbf{The time unit is set by the assumed
growth rate and is not calibrated to any measured infestation time-course; the
values carry no calendar units.} Equation~\eqref{eq:logisticsol} was checked
against a numerical solution of Equation~\eqref{eq:logisticode}, agreeing to %s.
The separation is inversely proportional to $r$, visible in the table as
$r \times \text{separation} = %s$ at all three rates: its \emph{existence} is a
property of the two collapse criteria, its \emph{duration} a function of the
stipulated rate.""" % (C["sci"](v["max_abs_err_vs_numeric"], 1),
                       num(v["r"] * v["window"], 3)))
    w()


def figure_logic(C):
    w = C["w"]
    w(r"\section{Computational Logic Behind Each Figure}\label{sec:figures}")
    w()
    w(r"""Every figure plots an object derived above; none introduces a quantity
not computed here.""")
    w()
    w(r"\begin{longtable}{p{1.1cm}p{4.3cm}p{2.8cm}p{5.1cm}}")
    w(r"\caption{\textit{Data and Computation Behind Each Figure}}"
      r"\label{tab:figures}\\")
    w(r"\toprule")
    w(r"Fig. & What is plotted & Source object & Computation \\")
    w(r"\midrule")
    w(r"\endfirsthead")
    w(r"\multicolumn{4}{l}{\textit{Table \ref{tab:figures} (continued)}}\\")
    w(r"\toprule")
    w(r"Fig. & What is plotted & Source object & Computation \\")
    w(r"\midrule")
    w(r"\endhead")
    w(r"\bottomrule")
    w(r"\endfoot")
    rows = [
        ("2", "One traced leaf as nodes and edges at measured coordinates",
         "Traced network",
         r"Node--edge reduction only; line width scales with measured vein "
         r"radius, which enters no statistic"),
        ("3", "The calibrated synthetic mesh at the same reduction",
         "Reference network",
         r"Generator tuned to the medians of Table~\ref{tab:empdesc}; $D$ is "
         r"left to emerge and then measured by Equation~\eqref{eq:box}"),
        ("4", "Collapse probability and surviving GCC fraction against removed "
              "fraction, uniform removal",
         r"Density response, reference network",
         r"Points are per-density proportions; curve is "
         r"Equation~\eqref{eq:logit} fitted to all trial-level outcomes; the "
         r"marked inflection is Equation~\eqref{eq:pcdef}"),
        ("5", "The same under degree-weighted removal",
         "Density response, weighted",
         r"As Fig.~4 with removal probabilities from "
         r"Equation~\eqref{eq:clip}; the leftward shift is "
         r"Equation~\eqref{eq:paireddiff}"),
        ("6", "The giant component breaking into islands across the threshold",
         "Single-trial survivor sets",
         r"Snapshots of the trials the curves aggregate; component labelling "
         r"is the decomposition of Equation~\eqref{eq:criterion}"),
        ("7", "Solved host water-potential field with the haustorium attached",
         r"Solve of Equation~\eqref{eq:laplacian}",
         r"Colour is $\psi$ per node at calibrated $K_{h}$ and the "
         r"illustrative gradient; the minimum is the 1.5 MPa row of "
         r"Table~\ref{tab:sink}"),
        ("8", "Threshold against each architectural predictor, one point per "
              "network",
         r"Table~B8 and Table~\ref{tab:empdesc}",
         r"Scatter only; printed panel coefficients are product-moment, while "
         r"the reported statistics are the rank coefficients of "
         r"Table~\ref{tab:pcassoc}"),
        ("9", r"Grid networks over the cohort in the "
              r"$\langle k\rangle$--$D$ plane",
         r"Inputs of Table~\ref{tab:grid}",
         r"Scatter on shared axes; the overhang is the %d cells above the "
         r"empirical maximum that Table~\ref{tab:gridrefit} excludes"),
        ("10", "Enhanced against current threshold, and the distribution of the "
               "change",
         r"Table~B9",
         r"Left: the two threshold columns against the identity line. Right: "
         r"histogram of $\Delta p_{c}$. Every point on or above the diagonal "
         r"is the sign result of Section~\ref{sec:comparisons}"),
        ("11", "One network before and after enhancement",
         r"Construction of Section~\ref{sec:engine}",
         r"Added closures in a contrasting hue; their count is "
         r"Equation~\eqref{eq:loopsadded} and the thresholds are that "
         r"network's row of Table~B9"),
        ("12", "Critical haustorial density over sink strength and $D$",
         r"Table~\ref{tab:surface}",
         r"Coupled-threshold surface; cells with no crossing are blank rather "
         r"than large, per Equation~\eqref{eq:crossing}"),
        ("13", "Threshold against size at pinned architecture",
         r"Table~\ref{tab:size}",
         r"Threshold and interval per size; the drifting loop fraction in the "
         r"same table is why no finite-size claim is read from it"),
        ("14", "Affected fraction against growth time, both crossings marked",
         r"Table~\ref{tab:dynamics}",
         r"Curve is Equation~\eqref{eq:logisticsol}; the marked times are "
         r"Equation~\eqref{eq:crossingtime} at $p_{c}$ and $f_{c}$"),
    ]
    for fig, what, src, comp in rows:
        if "%d" in comp:
            comp = comp % C["n_grid_above"]
        w(r"%s & %s & %s & %s \\" % (fig, what, src, comp))
    w(r"\end{longtable}")
    w()
    w(r"""\noindent Three conventions hold throughout. Axes labelled as a removed
fraction are the \emph{realised} fraction, never the nominal control parameter,
except in Table~\ref{tab:reference} where both are given because they diverge.
Error bars and bands are the percentile bootstrap intervals audited in
Section~\ref{sec:budgets}. A plotted threshold is always
Equation~\eqref{eq:pcdef}, never a value read off a curve by eye.""")
    w()
