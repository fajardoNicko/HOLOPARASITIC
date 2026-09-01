# -*- coding: utf-8 -*-
r"""Part 4 of the Appendix C builder: the two empirical removal modes
(Results Table 3) and the synthetic reference network (Results Table 4)."""

from __future__ import annotations


def thresholds(C):
    w, steps, num, esc = C["w"], C["steps"], C["num"], C["esc"]
    describe, check = C["describe"], C["check"]
    perc, T3 = C["perc"], C["T3"]

    ru = [float(r["pc_random"]) for r in perc]
    rd = [float(r["pc_degree"]) for r in perc]
    dd = [a - b for a, b in zip(ru, rd)]
    Su, Sd, Sdiff = describe(ru), describe(rd), describe(dd)
    C["Su"], C["Sd"], C["Sdiff"] = Su, Sd, Sdiff

    w(r"\section{Critical Removed Fraction Under Uniform and Degree-Weighted "
      r"Removal}\label{sec:thresholds}")
    w()
    w(r"""Each network of the percolation cohort was evaluated twice under the
engine of Section~\ref{sec:pcengine} at 2,400 trials per network per mode, on the
same collapse criterion and the same sweep, so the two thresholds of a network
are directly subtractable. The paired observation is""")
    w(r"\begin{equation}\label{eq:paireddiff}")
    w(r"d = p_{c,\text{uniform}} - p_{c,\text{degree}}")
    w(r"\end{equation}")
    w(r"""formed per network before any summary is taken.""")
    w()

    w(r"""The %d per-network threshold pairs are tabulated in full as Table~B8
of Appendix~B and are not repeated here. Table~\ref{tab:pcsummary} gives the
sufficient sums and summary statistics from which every quantity reported in the
Results is derived through Equations~\eqref{eq:mean} and~\eqref{eq:sd}."""
      % len(perc))
    w()

    # ---- summary block ----------------------------------------------------
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Sufficient Sums and Summary Statistics of the Two "
      r"Removal Modes}}\label{tab:pcsummary}")
    w(r"\small\setlength{\tabcolsep}{7pt}")
    w(r"\begin{tabular}{lccc}")
    w(r"\toprule")
    w(r"Statistic & $p_{u}$ & $p_{d}$ & $d$ \\")
    w(r"\midrule")
    w(r"$\sum x$ & %s & %s & %s \\"
      % (num(Su["sum"]), num(Sd["sum"]), num(Sdiff["sum"])))
    w(r"$\sum x^{2}$ & %s & %s & %s \\"
      % (num(Su["sum_sq"], 6), num(Sd["sum_sq"], 6), num(Sdiff["sum_sq"], 6)))
    w(r"$M$ & %s & %s & %s \\"
      % (num(Su["M"]), num(Sd["M"]), num(Sdiff["M"])))
    w(r"$SD$ & %s & %s & %s \\"
      % (num(Su["SD"]), num(Sd["SD"]), num(Sdiff["SD"])))
    w(r"$Mdn$ & %s & %s & %s \\"
      % (num(Su["Mdn"]), num(Sd["Mdn"]), num(Sdiff["Mdn"])))
    w(r"Range & %s--%s & %s--%s & %s--%s \\"
      % (num(Su["min"]), num(Su["max"]), num(Sd["min"]), num(Sd["max"]),
         num(Sdiff["min"]), num(Sdiff["max"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Mean p_c uniform", T3["random"]["M"], Su["M"])
    check("SD p_c uniform", T3["random"]["SD"], Su["SD"])
    check("Median p_c uniform", T3["random"]["Mdn"], Su["Mdn"])
    check("Mean p_c degree-weighted", T3["degree_targeted"]["M"], Sd["M"])
    check("SD p_c degree-weighted", T3["degree_targeted"]["SD"], Sd["SD"])
    check("Median p_c degree-weighted", T3["degree_targeted"]["Mdn"], Sd["Mdn"])
    check("Mean paired difference", T3["difference"]["M"], Sdiff["M"])
    check("SD paired difference", T3["difference"]["SD"], Sdiff["SD"])
    check("Median paired difference", T3["difference"]["Mdn"], Sdiff["Mdn"])

    # ---- worked computations ---------------------------------------------
    w(r"\subsection{Worked Computations}")
    w()
    w(r"""\noindent Uniform removal, from the first numeric column of
Table~\ref{tab:pcsummary}:""")
    _c = Su["n"] * Su["M"] ** 2
    steps(
        r"\bar{p}_{u} &= \frac{\sum p_{u}}{n} = \frac{%s}{%d} = %s"
        % (num(Su["sum"], 4), Su["n"], num(Su["M"], 6)),
        r"s_{u}^{2} &= \frac{\sum p_{u}^{2}-n\bar{p}_{u}^{2}}{n-1}"
        r" = \frac{%s-%s}{%d} = %s"
        % (num(Su["sum_sq"], 6), num(_c, 6), Su["n"] - 1,
           num(Su["SD"] ** 2, 8)),
        r"s_{u} &= \sqrt{%s} = %s" % (num(Su["SD"] ** 2, 8), num(Su["SD"], 6)),
    )
    _c2 = Sd["n"] * Sd["M"] ** 2
    w(r"""\noindent Degree-weighted removal, second column:""")
    steps(
        r"\bar{p}_{d} &= \frac{%s}{%d} = %s"
        % (num(Sd["sum"], 4), Sd["n"], num(Sd["M"], 6)),
        r"s_{d}^{2} &= \frac{%s-%s}{%d} = %s"
        % (num(Sd["sum_sq"], 6), num(_c2, 6), Sd["n"] - 1,
           num(Sd["SD"] ** 2, 8)),
        r"s_{d} &= \sqrt{%s} = %s" % (num(Sd["SD"] ** 2, 8), num(Sd["SD"], 6)),
    )
    _nd, _sd, _sq = Sdiff["n"], Sdiff["sum"], Sdiff["sum_sq"]
    _md = _sd / _nd
    _corr = _nd * _md * _md
    _var = (_sq - _corr) / (_nd - 1)
    w(r"""\noindent Paired difference, third column:""")
    steps(
        r"\bar{d} &= \frac{\sum d}{n} = \frac{%s}{%d} = %s"
        % (num(_sd, 6), _nd, num(_md, 6)),
        r"s_{d}^{2} &= \frac{\sum d^{2}-n\bar{d}^{2}}{n-1}"
        r" = \frac{%s-%d(%s)^{2}}{%d}"
        % (num(_sq, 6), _nd, num(_md, 6), _nd - 1),
        r"&= \frac{%s-%s}{%d} = \frac{%s}{%d} = %s"
        % (num(_sq, 6), num(_corr, 6), _nd - 1, num(_sq - _corr, 6),
           _nd - 1, num(_var, 8)),
        r"s_{d} &= \sqrt{%s} = %s" % (num(_var, 8), num(Sdiff["SD"], 6)),
    )
    npos = sum(1 for v in dd if v > 0)
    nneg = sum(1 for v in dd if v < 0)
    rel = 100.0 * (Su["Mdn"] - Sd["Mdn"]) / Su["Mdn"]
    check("Relative reduction of the median (%)",
          T3["relative_reduction_of_median_pct"], rel, 0.05)
    _gap = Su["Mdn"] - Sd["Mdn"]
    w(r"""\noindent Effect size by Equation~\eqref{eq:rrb}, and the relative
reduction of the median quoted in the Results:""")
    steps(
        r"r_{rb} &= \frac{%d}{%d}-\frac{%d}{%d} = %.2f"
        % (npos, len(dd), nneg, len(dd), (npos - nneg) / float(len(dd))),
        r"\frac{\tilde{p}_{u}-\tilde{p}_{d}}{\tilde{p}_{u}}\times 100"
        r" &= \frac{%s-%s}{%s}\times 100 = %s \times 100 = %s\%%"
        % (num(Su["Mdn"]), num(Sd["Mdn"]), num(Su["Mdn"]),
           num(_gap / Su["Mdn"], 6), "%.2f" % rel),
    )
    relm = 100.0 * (Su["M"] - Sd["M"]) / Su["M"]
    w(r"""The uniform threshold exceeded the degree-weighted threshold in %d of
%d networks, so $r_{rb} = 1.00$ records direction, not magnitude; the magnitude
is $Mdn\ d = %s$. The same reduction computed on the means is %s\%%; the Results
quotes the median form. The formal test is in Section~\ref{sec:comparisons}. The
separation is modest because the degree distribution of a planar venation network
is narrow (maximum degree four to five), so degree weighting departs only
mildly from uniform removal, as Section~\ref{sec:concentration} shows
directly.""" % (npos, len(dd), num(Sdiff["Mdn"]), "%.1f" % relm))
    w()


def reference_network(C):
    w, num, check = C["w"], C["num"], C["check"]
    summ, tci = C["summ"], C["tci"]
    gma = C["gma"]["targeted_attack_axis"]

    w(r"\section{High-Precision Thresholds on the Synthetic Reference Network}"
      r"\label{sec:reference}")
    w()
    w(r"""One synthetic mesh carries a trial budget two to three orders of
magnitude above the cohort budget, because the betweenness comparison, the size
sweep of Section~\ref{sec:size} and the separation interval of
Section~\ref{sec:dynamics} all need an interval narrow enough to be negligible.
Its descriptors are $N = %s$, $E = %s$, $\langle k\rangle = %s$, $D = %s$. It is
not a leaf and its absolute threshold is not comparable with the cohort
medians.""" %
      (C["mint"](summ["network"]["n_nodes"]),
       C["mint"](summ["network"]["n_edges"]),
       num(summ["network"]["mean_degree"], 4), num(summ["D"], 4)))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Threshold Estimates on the Synthetic Reference Network}}"
      r"\label{tab:reference}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{lcccc}")
    w(r"\toprule")
    w(r"Removal mode & $p_{c}$ (control parameter) & Realised removed fraction "
      r"& 95\% CI & Trials \\")
    w(r"\midrule")
    w(r"Uniform & %s & %s & [%s, %s] & 1,000,000 \\"
      % (num(summ["p_c_random"]), num(summ["p_c_random"]),
         num(summ["p_c_ci95"][0]), num(summ["p_c_ci95"][1])))
    dg = tci["results"]["degree"]
    w(r"Degree-weighted & %s & %s & [%s, %s] & %s \\"
      % (num(dg["p_c"]), num(dg["p_c"]), num(dg["ci95"][0]),
         num(dg["ci95"][1]), "{:,}".format(dg["n_trials"])))
    bt = tci["results"]["betweenness"]
    realised = gma["betweenness"]["realised_at_nominal_0.1889"]
    w(r"Betweenness-weighted & %s & \textbf{%s} & [%s, %s] & %s \\"
      % (num(bt["p_c"]), num(realised), num(bt["ci95"][0]),
         num(bt["ci95"][1]), "{:,}".format(bt["n_trials"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Reference p_c uniform", 0.2711, summ["p_c_random"])
    check("Reference p_c degree", 0.2023, dg["p_c"])
    check("Reference p_c betweenness nominal", 0.1889, bt["p_c"])
    check("Reference realised betweenness fraction", 0.1498, realised)
    w(r"""\noindent \textit{Note.} Percentile bootstrap intervals on the control
parameter, audited in Section~\ref{sec:budgets}. The control parameter and the
realised fraction coincide for uniform and degree weighting, because
Equation~\eqref{eq:clip} clips no node at these intensities, and diverge under
betweenness weighting by""")
    w(r"\begin{equation}")
    w(r"\frac{%s - %s}{%s}\times 100 = %s\%%"
      % (num(bt["p_c"]), num(realised), num(bt["p_c"]),
         "%.1f" % (100 * (bt["p_c"] - realised) / bt["p_c"])))
    w(r"\end{equation}")
    w(r"""of the nominal value; only the realised column is comparable across
modes, and the mechanism is quantified in Section~\ref{sec:concentration}.""")
    w()
