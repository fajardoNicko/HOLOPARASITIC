# -*- coding: utf-8 -*-
r"""Part 1 of the Appendix C builder: preamble, formulas, provenance."""

from __future__ import annotations


def preamble(C):
    w = C["w"]
    w(r"\documentclass[12pt,a4paper]{article}")
    w(r"\usepackage[T1]{fontenc}")
    w(r"\usepackage[utf8]{inputenc}")
    w(r"\usepackage[margin=1in]{geometry}")
    w(r"\usepackage{amsmath,amssymb}")
    w(r"\usepackage{booktabs}")
    w(r"\usepackage{longtable}")
    w(r"\usepackage{array}")
    w(r"\usepackage{float}")
    w(r"\usepackage{caption}")
    w(r"\usepackage[hidelinks]{hyperref}")
    w(r"\usepackage{times}")
    w(r"\setlength{\parindent}{0.5in}")
    w(r"\renewcommand{\arraystretch}{1.10}")
    w(r"\captionsetup[table]{labelsep=newline,justification=raggedright,")
    w(r"                     singlelinecheck=false,font=normalsize}")
    w(r"\renewcommand{\thesection}{C.\arabic{section}}")
    w(r"\renewcommand{\thetable}{C\arabic{table}}")
    w(r"\renewcommand{\theequation}{C.\arabic{equation}}")
    w(r"\begin{document}")
    w()
    # Appendix-opening drop, matching the heading placement in Appendix G.
    #
    # \vspace* is the documented way to do this but TeX still discards glue at
    # the very top of a page, so the drop is laid down as a zero-height rule
    # (a box, which stops the discard) followed by a plain \vskip.
    #
    # The drop is paid for out of page 1: the opening paragraph below was cut
    # from seven typeset lines to two, freeing 5 x \baselineskip = 72.5pt
    # against the 72.27pt the drop costs. Page 1 therefore holds exactly the
    # material it held before and no later page moves. If \appdrop is retuned,
    # that paragraph has to gain or lose a line per 14.5pt to keep the balance.
    w(r"\newlength{\appdrop}")
    w(r"\setlength{\appdrop}{1in}")
    w(r"\hrule height 0pt\relax")
    w(r"\vskip\appdrop")
    w(r"\begin{center}")
    w(r"{\large\textbf{Appendix C}}\\[6pt]")
    w(r"{\large\textbf{DATA ANALYSIS AND COMPUTATION}}")
    w(r"\end{center}")
    w(r"\vspace{1em}")
    w()
    w(r"""\noindent This appendix re-derives every quantity reported in the
Results from the archived data, in the order the Results presents them. Notation
and formulas are collected in Section~\ref{sec:formulas}.""")
    w()


def notation(C):
    w = C["w"]
    w(r"\section{Notation and Formulas}\label{sec:formulas}")
    w()
    w(r"""$n$ is the number of observations, $x$ an observation, $\bar{x}$ their
mean, $s$ their standard deviation. $p_{c}$ is the critical removed fraction,
$\langle k\rangle$ mean degree, $D$ the box-counting fractal dimension, $N$ the
node count, and $p$ a significance value.""")
    w()
    w(r"\subsection{Descriptive}")
    w()
    w(r"\begin{equation}\label{eq:mean}")
    w(r"\bar{x} = \frac{\sum x}{n}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:sd}")
    w(r"s = \sqrt{\frac{\sum (x-\bar{x})^{2}}{n-1}}"
      r" = \sqrt{\frac{\sum x^{2}-n\bar{x}^{2}}{n-1}}")
    w(r"\end{equation}")
    w(r"""The right-hand form of Equation~\eqref{eq:sd} is the computational
identity used throughout, so each standard deviation is checkable from the two
sums $\sum x$ and $\sum x^{2}$ tabulated with it. The divisor $n-1$ is the sample
form. Medians are the central order statistic (the mean of the two central values
for even $n$); quartile cut points are linearly interpolated between order
statistics.""")
    w()
    w(r"\subsection{Association}")
    w()
    w(r"\begin{equation}\label{eq:spearman}")
    w(r"\rho = 1 - \frac{6\sum d_{i}^{2}}{n(n^{2}-1)}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:tstat}")
    w(r"t = \rho\sqrt{\frac{n-2}{1-\rho^{2}}}, \qquad df = n-2")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:pearson}")
    w(r"r = \frac{\sum (x-\bar{x})(y-\bar{y})}"
      r"{\sqrt{\sum (x-\bar{x})^{2}\sum (y-\bar{y})^{2}}}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:partial}")
    w(r"\rho_{xy\cdot z} = \frac{\rho_{xy}-\rho_{xz}\rho_{yz}}"
      r"{\sqrt{(1-\rho_{xz}^{2})(1-\rho_{yz}^{2})}}")
    w(r"\end{equation}")
    w(r"""$d_{i}$ in Equation~\eqref{eq:spearman} is the difference between the
two ranks of network $i$. That form is exact only without ties; where ties occur
the coefficient reported is Equation~\eqref{eq:pearson} applied to midranks, and
the discrepancy is quantified at the point of use.
Equation~\eqref{eq:pearson} is used only as a diagnostic (collinearity, and
the constructed grid) and is labelled $r$ wherever it appears.
Equation~\eqref{eq:partial} is the rank analogue of the first-order partial
correlation.""")
    w()
    w(r"\subsection{Regression}")
    w()
    w(r"\begin{equation}\label{eq:ols}")
    w(r"\hat{y} = b_{0} + b_{1}z_{1} + b_{2}z_{2}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:r2}")
    w(r"R^{2} = 1-\frac{SS_{\text{res}}}{SS_{\text{tot}}}"
      r" = 1-\frac{\sum(y-\hat{y})^{2}}{\sum(y-\bar{y})^{2}}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:Fstat}")
    # Built as a true compound fraction. Written with solidi the ratio of two
    # ratios reads as ambiguous at a glance, so both stages carry a rule, and
    # \dfrac keeps the inner ones at display size inside the outer one.
    w(r"F = \frac{\dfrac{R^{2}}{k}}{\dfrac{1-R^{2}}{n-k-1}},"
      r" \qquad df = (k,\,n-k-1)")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:vif}")
    w(r"\mathrm{VIF} = \frac{1}{1-R^{2}_{\text{aux}}} = \frac{1}{1-r^{2}}")
    w(r"\end{equation}")
    w(r"""Predictors are $z$-scored and the outcome left in its own units, so each
$b$ in Equation~\eqref{eq:ols} is the change in the outcome per one standard
deviation of its predictor; dividing by the outcome's standard deviation gives
the fully standardised $\beta$. Equation~\eqref{eq:vif} takes the closed form
shown because for two predictors the auxiliary $R^{2}$ equals their squared
correlation.""")
    w()
    w(r"\subsection{Distribution-Free Tests and Effect Sizes}")
    w()
    w(r"\begin{equation}\label{eq:rrb}")
    w(r"r_{rb} = \frac{\#(d>0)}{n}-\frac{\#(d<0)}{n}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:cliff}")
    w(r"\delta = \frac{\#(x_{2}>x_{1})-\#(x_{2}<x_{1})}{n_{1}n_{2}}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:sign}")
    w(r"p = 2\,P(X \geq k), \qquad X \sim \mathrm{Binomial}(m,\,0.5)")
    w(r"\end{equation}")
    w(r"""Paired comparisons use the Wilcoxon signed-rank test on the per-network
differences: non-zero differences are ranked by absolute magnitude, ranks are
signed, and $W$ is the smaller signed-rank sum. Zero differences are discarded by
default; the Pratt treatment, which retains them, is reported alongside where
ties are numerous. Independent groups use Mann--Whitney $U$; more than two groups
use Kruskal--Wallis $H$. Equation~\eqref{eq:rrb} records direction only, not
magnitude. Equation~\eqref{eq:cliff} runs over all $n_{1}n_{2}$ cross-group
pairs. Equation~\eqref{eq:sign} is the two-sided binomial tail on the $m$
informative pairs, of which $k$ favour the treated condition.""")
    w()
    w(r"\subsection{Concentration and Simulation Error}")
    w()
    w(r"\begin{equation}\label{eq:gini}")
    w(r"G = \frac{\sum_{i}\sum_{j}\lvert w_{i}-w_{j}\rvert}{2n^{2}\bar{w}}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:mcse}")
    w(r"\mathrm{SE}(\hat{P}) = \sqrt{\frac{\hat{P}(1-\hat{P})}{N_{\text{trials}}}}")
    w(r"\end{equation}")
    w(r"""Equation~\eqref{eq:mcse} is maximal at $\hat{P} = 0.50$, which is where
the threshold is read, so its worst case governs the precision of every reported
threshold and is tabulated per budget in Section~\ref{sec:budgets}.""")
    w()
    w(r"\subsection{Decision Rules Fixed in Advance}")
    w()
    w(r"""Three rules were fixed before the analyses ran. (i) Every variable
entering an association analysis was screened by Shapiro--Wilk at
$\alpha = .05$; because the outcome and both connectivity predictors failed,
Spearman's $\rho$ was applied uniformly to every association test rather than
chosen variable by variable. (ii) All inferential tests are two-sided at
$\alpha = .05$. (iii) Non-normal quantities are summarised by median and range
alongside mean and standard deviation, and the median is the value quoted in the
running text where the two disagree.""")
    w()


def provenance(C):
    w = C["w"]
    prov = C["prov"]
    w(r"\section{Provenance and Analysis Sets}\label{sec:provenance}")
    w()
    w(r"""Each computation draws on archived files written by a simulation or
measurement script and thereafter read only; no value is carried over from the
manuscript text.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Source File for Each Computation}}\label{tab:provenance}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lp{5.2cm}p{5.4cm}}")
    w(r"\toprule")
    w(r"\S & Quantity & Source file \\")
    w(r"\midrule")
    for sec, quantity, src in [
        (r"\ref{sec:empirical}", "Empirical descriptors; associations; "
         "thresholds; quartiles; enhancement",
         r"\texttt{analysis\_master.csv}"),
        (r"\ref{sec:synthetic}", "Synthetic comparison set",
         r"\texttt{synthetic\_pernetwork.csv}"),
        (r"\ref{sec:reference}", "Synthetic reference thresholds",
         r"\texttt{summary.json}, \texttt{targeted\_ci.json}, "
         r"\texttt{graph\_metric\_audit.json}"),
        (r"\ref{sec:grid}", "Synthetic causal grid",
         r"\texttt{synthetic\_grid\_pc.csv}, \texttt{rrl\_diagnostics.json}"),
        (r"\ref{sec:sink}", "Haustorial sink sweep",
         r"\texttt{cavitation\_sensitivity.json}"),
        (r"\ref{sec:surface}", "Coupled haustorial-density surface",
         r"\texttt{sink\_surface.json}"),
        (r"\ref{sec:verification}", r"Hydraulic verification; $K_{\text{leaf}}$",
         r"\texttt{results\_verified.json}, "
         r"\texttt{final\_resolution\_checks.json}"),
        (r"\ref{sec:criterion}", "Criterion and damage locality",
         r"\texttt{criterion\_and\_locality.json}"),
        (r"\ref{sec:size}", "Size dependence",
         r"\texttt{finite\_size\_fixedD.json}, \texttt{scaling\_mesh.json}"),
        (r"\ref{sec:sensitivity}", "Sensitivity battery",
         r"\texttt{second\_pass\_audit.json}, "
         r"\texttt{resistance\_convention\_sensitivity.json}"),
        (r"\ref{sec:budgets}", "Trial budgets and intervals",
         r"\texttt{final\_resolution\_checks.json}"),
        (r"\ref{sec:dynamics}", "Separation interval",
         r"\texttt{dynamics.json}"),
    ]:
        w(r"%s & %s & %s \\" % (sec, quantity, src))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Definition and Size of Each Analysis Set}}"
      r"\label{tab:nesting}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{lcp{7.0cm}c}")
    w(r"\toprule")
    w(r"Set & $n$ & Inclusion rule & Trials \\")
    w(r"\midrule")
    w(r"Traced & %d & Every leaf loaded from the source deposit & n/a \\"
      % prov["traced"]["n"])
    w(r"Characterisation & %d & At least 500 veins & n/a \\"
      % prov["characterization_112"]["n"])
    w(r"Enhancement cohort & %d & $N \geq 1{,}000$ and current "
      r"$p_{c} \geq 0.02$ & 10,000 \\" % prov["enhancement_cohort_105"]["n"])
    w(r"Percolation cohort & %d & At least 2,000 veins, at least one cycle, "
      r"window cut-end terminal fraction $\leq 0.05$, mean-degree shift "
      r"$\leq 0.05$ & 2,400 \\" % prov["percolation_cohort_100"]["n"])
    w(r"Synthetic reference & 1 & Single calibrated mesh, $N = 1{,}023$ & "
      r"1,000,000 \\")
    w(r"Synthetic grid & %d & Six mean-degree by seven depth cells & 3,200 \\"
      % prov["synthetic_grid"]["n"])
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    excl = prov["characterization_112"]["excluded"]
    add5 = prov["enhancement_cohort_105"]["in_105_not_in_100"]
    w(r"""\noindent \textit{Note.} Nesting is
$%d \subset %d \subset %d \subset %d$. The %d networks dropped at the
characterisation screen were dropped for size alone (%s). The %d in the
enhancement but not the percolation cohort are %s. Of the %d traced files, %d
are calibrated crop windows rather than entire laminae, so $N$ is a property of
the tracing as much as of the plant; every architecture--threshold association in
Section~\ref{sec:predictors} is therefore reported both raw and with $\log N$
held constant.""" %
      (prov["percolation_cohort_100"]["n"],
       prov["enhancement_cohort_105"]["n"],
       prov["characterization_112"]["n"], prov["traced"]["n"],
       len(excl), ", ".join(C["esc"](x) for x in excl),
       len(add5), ", ".join(C["esc"](x) for x in add5),
       prov["traced"]["n"], C["rrl"]["dataset_facts"]["n_crop_windows"]))
    w()
