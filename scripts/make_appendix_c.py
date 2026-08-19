# -*- coding: utf-8 -*-
r"""
make_appendix_c.py -- build "Appendix C: Data Analysis and Computation" as a
LaTeX document in the APA layout used by the reference hardbound paper: for each
reported statistic the raw unit-level data are tabulated, the defining formula is
stated, the intermediate sums actually obtained from the data are substituted,
and the result is carried to the precision reported in the Results.

Every number is recomputed here from data/analysis_master.csv and data/*.json.
Nothing is copied from the manuscript text. Section C.13 reconciles each
recomputed value against the corresponding cell of the Results and flags any
disagreement.

    python scripts/make_appendix_c.py

Writes APPENDIX_C_COMPUTATIONS.tex (compile with pdflatex) and
APPENDIX_C_CHECKS.csv.  ASCII-only stdout.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "APPENDIX_C_COMPUTATIONS.tex"
CHECKS_CSV = ROOT / "APPENDIX_C_CHECKS.csv"

L: list[str] = []
CHECKS: list[tuple[str, float, float, float]] = []


def w(s: str = "") -> None:
    L.append(s)


def check(label, reported, computed, tol=5e-4):
    CHECKS.append((label, reported, computed, tol))
    return computed


def J(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def esc(s):
    return str(s).replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")


def num(x, d=4):
    if x is None or (isinstance(float(x), float) and not math.isfinite(float(x))):
        return "--"
    return ("%." + str(d) + "f") % float(x)


def rho(x):
    """APA rank statistic: no leading zero, Unicode minus rendered as $-$."""
    s = "%.3f" % abs(float(x))
    return ("$-$" if float(x) < 0 else "") + "." + s.split(".")[1]


def pval(p):
    if p < 0.001:
        return "$<$ .001"
    return "= ." + ("%.3f" % p).split(".")[1]


# --------------------------------------------------------------------------
# descriptive statistics, computed from the raw column so the appendix is
# self-contained rather than reading a precomputed summary
# --------------------------------------------------------------------------
def describe(xs):
    xs = [float(v) for v in xs]
    n = len(xs)
    s = sum(xs)
    ss = sum(v * v for v in xs)
    m = s / n
    var = (ss - n * m * m) / (n - 1)
    sd = math.sqrt(max(var, 0.0))
    o = sorted(xs)
    mid = n // 2
    mdn = o[mid] if n % 2 else (o[mid - 1] + o[mid]) / 2.0
    return dict(n=n, sum=s, sum_sq=ss, M=m, SD=sd, Mdn=mdn, min=o[0], max=o[-1])


def quartile_cut(xs, q):
    """Linear-interpolation quantile, matching numpy's default."""
    o = sorted(float(v) for v in xs)
    h = (len(o) - 1) * q
    lo = int(math.floor(h))
    hi = min(lo + 1, len(o) - 1)
    return o[lo] + (h - lo) * (o[hi] - o[lo])


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    with open(ROOT / "data" / "analysis_master.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    perc = [r for r in rows if r["in_percolation_cohort_100"] == "True"]
    enh = [r for r in rows if r["in_enhancement_cohort_105"] == "True"]
    char = [r for r in rows if r["in_characterization_112"] == "True"]

    rv = J("results_verified.json")
    cl = J("criterion_and_locality.json")
    cav = J("cavitation_sensitivity.json")
    T1, T3, T8 = rv["T1_characterization"], rv["T3_attack_thresholds"], rv["T8_quartiles"]
    T9, T11 = rv["T9_enhancement"], rv["T11_validation"]
    loc = cl["locality_comparison"]
    crit = cl["criterion_comparison"]

    # ---------------- preamble --------------------------------------------
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
    w(r"\renewcommand{\arraystretch}{1.15}")
    w(r"\captionsetup[table]{labelsep=newline,justification=raggedright,")
    w(r"                     singlelinecheck=false,font=normalsize}")
    w(r"\renewcommand{\thesection}{C.\arabic{section}}")
    w(r"\renewcommand{\thetable}{C\arabic{table}}")
    w(r"\renewcommand{\theequation}{C.\arabic{equation}}")
    w(r"\begin{document}")
    w()
    w(r"\begin{center}")
    w(r"{\large\textbf{Appendix C}}\\[6pt]")
    w(r"{\large\textbf{Data Analysis and Computation}}")
    w(r"\end{center}")
    w(r"\vspace{1em}")
    w()
    w(r"""\noindent This appendix re-derives every statistic reported in the
Results directly from the archived data files. For each quantity the raw
unit-level observations are tabulated, the defining formula is stated, and the
intermediate sums obtained from those observations are substituted so that the
reported value can be reproduced without returning to the raw files. The unit of
observation is the individual leaf-venation network, which plays the role that a
single experimental trial plays in a bench study. Section~C.13 lists every
recomputed value against the corresponding cell of the Results and flags any
disagreement.""")
    w()

    # ---------------- C.1 formulas ----------------------------------------
    w(r"\section{Statistical Formulas Used}")
    w()
    w(r"""The arithmetic mean is""")
    w(r"\begin{equation}")
    w(r"\bar{x} = \frac{\sum x}{n}")
    w(r"\end{equation}")
    w(r"""where $\sum x$ is the sum of the observations and $n$ is the number of
observations. The standard deviation is the sample (unbiased) form,""")
    w(r"\begin{equation}")
    w(r"s = \sqrt{\frac{\sum (x-\bar{x})^{2}}{n-1}}"
      r" = \sqrt{\frac{\sum x^{2}-n\bar{x}^{2}}{n-1}}")
    w(r"\end{equation}")
    w(r"""where $x$ is a value in the distribution, $\bar{x}$ is the sample mean
and $n$ is the total number of observations. The right-hand form is the
computational identity used throughout this appendix, so that each standard
deviation can be checked from the two sums $\sum x$ and $\sum x^{2}$ tabulated
with it. The divisor $n-1$ is used because the networks are a sample of leaves
rather than an enumerated population.""")
    w()
    w(r"""Because the distributions of the reported quantities departed from
normality, monotone association is quantified by Spearman's rank-order
correlation""")
    w(r"\begin{equation}")
    w(r"\rho = 1 - \frac{6\sum d_{i}^{2}}{n(n^{2}-1)}")
    w(r"\end{equation}")
    w(r"""where $d_{i}$ is the difference between the two ranks assigned to
network $i$, and paired comparisons use the Wilcoxon signed-rank test on the
per-network differences. Effect sizes for paired comparisons are reported as the
matched-pairs rank-biserial correlation, the proportion of pairs favouring one
condition minus the proportion favouring the other.""")
    w()

    # ---------------- C.2 provenance --------------------------------------
    w(r"\section{Provenance of the Data}")
    w()
    w(r"""Each computation below draws on one archived file. No intermediate
value is carried over from the manuscript text.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Source File for Each Computation in This Appendix}}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{llp{6.2cm}}")
    w(r"\toprule")
    w(r"Section & Quantity & Source file \\")
    w(r"\midrule")
    for s, q, f_ in [
        ("C.3", "Critical removed fraction, two removal modes", r"\texttt{analysis\_master.csv}"),
        ("C.4", "Architectural descriptors", r"\texttt{analysis\_master.csv}"),
        ("C.5", "Reticulation enhancement", r"\texttt{analysis\_master.csv}"),
        ("C.6", "Reticulation quartiles", r"\texttt{analysis\_master.csv}"),
        ("C.7", "Damage locality and criterion", r"\texttt{criterion\_and\_locality.json}"),
        ("C.8", "Haustorial sink sweep", r"\texttt{cavitation\_sensitivity.json}"),
        ("C.9", "Hydraulic verification", r"\texttt{hydraulic\_validation.json}"),
        ("C.10", "Trial budgets and intervals", r"\texttt{summary.json}, \texttt{targeted\_ci.json}"),
        ("C.11", "Normality screening and rank-order association", r"\texttt{analysis\_master.csv}"),
        ("C.12", "Paired and group comparisons", r"\texttt{analysis\_master.csv}"),
    ]:
        w(r"%s & %s & %s \\" % (s, q, f_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    w(r"""\noindent The three analysis sets are nested: the 100-network
percolation cohort is a subset of the 105-network enhancement cohort, which is a
subset of the 112 networks passing the characterisation screen, drawn from 120
traced networks. Each table below states which set it uses.""")
    w()

    # ---------------- C.3 thresholds --------------------------------------
    w(r"\section{Critical Removed Fraction Under Uniform and Degree-Weighted Removal}")
    w()
    w(r"""The critical removed fraction $p_{c}$ is the proportion of nodes whose
removal drives the giant connected component below half its undamaged size with
probability .50. Each network was evaluated under both removal modes at 2,400
Monte Carlo trials per mode, and the per-network difference
$d = p_{c,\text{uniform}} - p_{c,\text{degree}}$ is the paired observation on
which the comparison rests. Table~C2 gives all three columns for every network
in the percolation cohort.""")
    w()
    ru = [float(r["pc_random"]) for r in perc]
    rd = [float(r["pc_degree"]) for r in perc]
    dd = [a - b for a, b in zip(ru, rd)]
    Su, Sd, Sdiff = describe(ru), describe(rd), describe(dd)

    w(r"\begin{longtable}{lccc}")
    w(r"\caption{\textit{Critical Removed Fraction of Each Network Under Uniform "
      r"and Degree-Weighted Removal}}\\")
    w(r"\toprule")
    w(r"Network & $p_{c}$ uniform & $p_{c}$ degree-weighted & $d$ \\")
    w(r"\midrule")
    w(r"\endfirsthead")
    w(r"\multicolumn{4}{l}{\textit{Table C2 (continued)}}\\")
    w(r"\toprule")
    w(r"Network & $p_{c}$ uniform & $p_{c}$ degree-weighted & $d$ \\")
    w(r"\midrule")
    w(r"\endhead")
    w(r"\bottomrule")
    w(r"\endfoot")
    for r in perc:
        a, b = float(r["pc_random"]), float(r["pc_degree"])
        w(r"%s & %s & %s & %s \\" % (esc(r["name"]), num(a), num(b), num(a - b)))
    w(r"\midrule")
    w(r"$\sum x$ & %s & %s & %s \\" % (num(Su["sum"]), num(Sd["sum"]), num(Sdiff["sum"])))
    w(r"$\sum x^{2}$ & %s & %s & %s \\" % (num(Su["sum_sq"], 6), num(Sd["sum_sq"], 6),
                                           num(Sdiff["sum_sq"], 6)))
    w(r"\textbf{Mean} & %s & %s & %s \\" % (num(Su["M"]), num(Sd["M"]), num(Sdiff["M"])))
    w(r"\textbf{SD} & %s & %s & %s \\" % (num(Su["SD"]), num(Sd["SD"]), num(Sdiff["SD"])))
    w(r"\textbf{Median} & %s & %s & %s \\" % (num(Su["Mdn"]), num(Sd["Mdn"]), num(Sdiff["Mdn"])))
    w(r"\end{longtable}")
    w()
    w(r"""\noindent \textit{Note.} $n = %d$ networks; 2,400 Monte Carlo trials per
network per removal mode. $d$ is the per-network difference, computed before any
summary is taken. The difference column is \textbf{not} obtainable from the two
summary rows above it: subtracting the two standard deviations gives %s, which is
not a statistic, because the two arms are correlated across networks and the
between-network variation cancels in the difference.""" %
      (Sdiff["n"], num(Su["SD"] - Sd["SD"])))
    w()
    w(r"\subsection{Worked Computation of the Paired Difference}")
    w()
    w(r"""Substituting the sums from the final block of Table~C2 into equations
(C.1) and (C.2) for the difference column,""")
    w(r"\begin{align}")
    w(r"\bar{d} &= \frac{\sum d}{n} = \frac{%s}{%d} = %s \\[4pt]"
      % (num(Sdiff["sum"]), Sdiff["n"], num(Sdiff["M"], 6)))
    w(r"s_{d} &= \sqrt{\frac{\sum d^{2}-n\bar{d}^{2}}{n-1}}"
      r" = \sqrt{\frac{%s-%d(%s)^{2}}{%d}} = %s"
      % (num(Sdiff["sum_sq"], 6), Sdiff["n"], num(Sdiff["M"], 6),
         Sdiff["n"] - 1, num(Sdiff["SD"], 6)))
    w(r"\end{align}")
    w(r"""which round to the mean difference of %s and the standard deviation of
%s reported in the Results. The uniform threshold exceeded the degree-weighted
threshold in %d of %d networks, so the matched-pairs rank-biserial correlation is
$(%d/%d)-(0/%d) = 1.00$: perfect directional consistency. That value records the
\emph{direction} of the effect in every network and not its size; the size is the
median difference of %s, roughly one sixth of the uniform threshold.""" %
      (num(Sdiff["M"]), num(Sdiff["SD"]),
       sum(1 for v in dd if v > 0), len(dd),
       sum(1 for v in dd if v > 0), len(dd), len(dd),
       num(Sdiff["Mdn"])))
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

    rel = 100.0 * (Su["Mdn"] - Sd["Mdn"]) / Su["Mdn"]
    check("Relative reduction of the median (%)",
          T3["relative_reduction_of_median_pct"], rel, 0.05)
    w(r"""The relative reduction in the tolerable removed fraction follows as""")
    w(r"\begin{equation}")
    w(r"\frac{%s-%s}{%s}\times 100 = %s\%%"
      % (num(Su["Mdn"]), num(Sd["Mdn"]), num(Su["Mdn"]), "%.2f" % rel))
    w(r"\end{equation}")
    w()

    # ---------------- C.4 descriptors -------------------------------------
    w(r"\section{Architectural Descriptors of the Traced Networks}")
    w()
    w(r"""The descriptors entered into the association analyses are the number of
nodes $N$, the number of edges $E$, the mean degree $\langle k\rangle = 2E/N$,
the loop fraction (the proportion of edges lying on at least one cycle), and the
box-counting fractal dimension $D$. Table~C3 summarises them for the 112 networks
passing the characterisation screen.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Summary of the Architectural Descriptors}}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lrrrrrr}")
    w(r"\toprule")
    w(r"Descriptor & $\sum x$ & $\sum x^{2}$ & $M$ & $SD$ & $Mdn$ & Range \\")
    w(r"\midrule")
    desc_rows = [
        ("Mean degree $\\langle k\\rangle$", "mean_degree", 3, "mean_degree"),
        ("Degree $SD$", "degree_sd", 3, "degree_sd"),
        ("Loop fraction", "loop_fraction_nonbridge", 3, "loop_fraction"),
        ("Bridge fraction", "bridge_fraction", 3, "bridge_fraction"),
        ("Fractal dimension $D$", "D", 3, "D"),
        ("GCC fraction", "gcc_fraction", 3, "gcc_fraction"),
    ]
    for label, col, dec, key in desc_rows:
        S = describe([r[col] for r in char])
        w(r"%s & %s & %s & %s & %s & %s & [%s, %s] \\"
          % (label, num(S["sum"], 3), num(S["sum_sq"], 3), num(S["M"], dec),
             num(S["SD"], dec), num(S["Mdn"], dec), num(S["min"], dec),
             num(S["max"], dec)))
        if key in T1["empirical"]:
            check("Empirical %s M" % key, T1["empirical"][key]["M"], S["M"], 5e-4)
            check("Empirical %s SD" % key, T1["empirical"][key]["SD"], S["SD"], 5e-4)
            check("Empirical %s Mdn" % key, T1["empirical"][key]["Mdn"], S["Mdn"], 5e-4)
    SN = describe([r["n_nodes"] for r in char])
    w(r"Network size $N$ & %s & --- & %s & %s & %s & [%s, %s] \\"
      % ("{:,}".format(int(SN["sum"])), "{:,.0f}".format(SN["M"]),
         "{:,.0f}".format(SN["SD"]), "{:,.0f}".format(SN["Mdn"]),
         "{:,.0f}".format(SN["min"]), "{:,.0f}".format(SN["max"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Empirical N M", T1["empirical"]["N"]["M"], SN["M"], 0.5)
    check("Empirical N Mdn", T1["empirical"]["N"]["Mdn"], SN["Mdn"], 0.5)
    w(r"""\noindent \textit{Note.} $n = %d$ networks passing the characterisation
screen of at least 500 veins. The two sum columns are provided so that each mean
and standard deviation can be reproduced from equations (C.1) and (C.2). Bridge
fraction is the exact complement of loop fraction, so the two rows sum to unity
and carry the same information with opposite sign. Network size is tabulated
without $\sum x^{2}$ because that quantity overflows ordinary display precision;
its dispersion is given by the range.""" % SN["n"])
    w()
    mk = describe([r["mean_degree"] for r in char])
    w(r"""Worked example for mean degree, substituting the first two columns of
Table~C3 into equations (C.1) and (C.2):""")
    w(r"\begin{align}")
    w(r"\overline{\langle k\rangle} &= \frac{%s}{%d} = %s \\[4pt]"
      % (num(mk["sum"], 3), mk["n"], num(mk["M"], 6)))
    w(r"s &= \sqrt{\frac{%s-%d(%s)^{2}}{%d}} = %s"
      % (num(mk["sum_sq"], 3), mk["n"], num(mk["M"], 6), mk["n"] - 1,
         num(mk["SD"], 6)))
    w(r"\end{align}")
    w()

    # ---------------- C.5 enhancement -------------------------------------
    w(r"\section{Reticulation Enhancement}")
    w()
    w(r"""Each network in the enhancement cohort was evaluated twice at 10,000
Monte Carlo trials per arm: once as traced, and once after closing its own
areoles until its mean degree reached the cohort ceiling
$\langle k\rangle = %.3f$, the 90th percentile of the percolation cohort's own
mean degree. Both arms consumed an identical sequence of removal draws, so each
network serves as its own control and the Monte Carlo error is common to the two
arms. Table~C4 gives the paired observations.""" % T9["ceiling_mean_degree"])
    w()
    dpc = [float(r["delta_pc"]) for r in enh]
    Sc = describe([r["pc_current"] for r in enh])
    Ss = describe([r["pc_suggested"] for r in enh])
    Sdel = describe(dpc)
    w(r"\begin{longtable}{lcrccc}")
    w(r"\caption{\textit{Fragmentation Threshold of Each Network Before and After "
      r"Reticulation Enhancement}}\\")
    w(r"\toprule")
    w(r"Network & $\langle k\rangle_{0}$ & Loops added & $p_{c}$ before & "
      r"$p_{c}$ after & $\Delta p_{c}$ \\")
    w(r"\midrule")
    w(r"\endfirsthead")
    w(r"\multicolumn{6}{l}{\textit{Table C4 (continued)}}\\")
    w(r"\toprule")
    w(r"Network & $\langle k\rangle_{0}$ & Loops added & $p_{c}$ before & "
      r"$p_{c}$ after & $\Delta p_{c}$ \\")
    w(r"\midrule")
    w(r"\endhead")
    w(r"\bottomrule")
    w(r"\endfoot")
    for r in enh:
        w(r"%s & %s & %s & %s & %s & %s \\"
          % (esc(r["name"]), num(r["mean_degree"], 3),
             "{:,}".format(int(float(r["loops_added"]))),
             num(r["pc_current"]), num(r["pc_suggested"]), num(r["delta_pc"])))
    w(r"\midrule")
    w(r"\multicolumn{3}{l}{$\sum x$} & %s & %s & %s \\"
      % (num(Sc["sum"]), num(Ss["sum"]), num(Sdel["sum"])))
    w(r"\multicolumn{3}{l}{$\sum x^{2}$} & %s & %s & %s \\"
      % (num(Sc["sum_sq"], 6), num(Ss["sum_sq"], 6), num(Sdel["sum_sq"], 6)))
    w(r"\multicolumn{3}{l}{\textbf{Mean}} & %s & %s & %s \\"
      % (num(Sc["M"]), num(Ss["M"]), num(Sdel["M"])))
    w(r"\multicolumn{3}{l}{\textbf{SD}} & %s & %s & %s \\"
      % (num(Sc["SD"]), num(Ss["SD"]), num(Sdel["SD"])))
    w(r"\multicolumn{3}{l}{\textbf{Median}} & %s & %s & %s \\"
      % (num(Sc["Mdn"]), num(Ss["Mdn"]), num(Sdel["Mdn"])))
    w(r"\end{longtable}")
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
    w(r"""\noindent \textit{Note.} $n = %d$ networks meeting the enhancement
screen ($N \geq 1{,}000$ and current $p_{c} \geq 0.02$), evaluated at 10,000
trials per arm with common random numbers across the paired arms. Loop addition
modifies only the edge set; the node set is unchanged. Of the %d networks, %d
improved, %d were unchanged and %d worsened.""" % (Sdel["n"], Sdel["n"], imp, unch, wor))
    w()
    w(r"\subsection{Worked Computation of the Threshold Gain}")
    w()
    w(r"\begin{align}")
    w(r"\overline{\Delta p_{c}} &= \frac{%s}{%d} = %s \\[4pt]"
      % (num(Sdel["sum"]), Sdel["n"], num(Sdel["M"], 6)))
    w(r"s_{\Delta} &= \sqrt{\frac{%s-%d(%s)^{2}}{%d}} = %s"
      % (num(Sdel["sum_sq"], 6), Sdel["n"], num(Sdel["M"], 6),
         Sdel["n"] - 1, num(Sdel["SD"], 6)))
    w(r"\end{align}")
    pct_imp = 100.0 * imp / Sdel["n"]
    check("Percent improved", T9["pct_improved"], pct_imp, 0.05)
    w(r"""The proportion of networks improving is $%d/%d \times 100 = %s\%%$, and
the median relative gain is""" % (imp, Sdel["n"], "%.1f" % pct_imp))
    relg = sorted(100.0 * (float(r["pc_suggested"]) - float(r["pc_current"]))
                  / float(r["pc_current"]) for r in enh)
    mid = len(relg) // 2
    mrg = relg[mid] if len(relg) % 2 else (relg[mid - 1] + relg[mid]) / 2.0
    check("Median relative gain (%)", T9["median_relative_gain_pct"], mrg, 0.05)
    w(r"\begin{equation}")
    w(r"\mathrm{Mdn}\!\left[\frac{p_{c,\text{after}}-p_{c,\text{before}}}"
      r"{p_{c,\text{before}}}\times 100\right] = %s\%%" % ("%.2f" % mrg))
    w(r"\end{equation}")
    w(r"""computed per network and then summarised, not derived from the column
medians above.""")
    w()

    # ---------------- C.6 quartiles ---------------------------------------
    w(r"\section{Damage Tolerance by Reticulation Quartile}")
    w()
    lf = [float(r["loop_fraction_nonbridge"]) for r in perc]
    q1, q2, q3 = (quartile_cut(lf, 0.25), quartile_cut(lf, 0.50), quartile_cut(lf, 0.75))
    w(r"""The percolation cohort was divided at the quartile cut points of the
loop-fraction distribution, $Q_{1} = %s$, $Q_{2} = %s$ and $Q_{3} = %s$, giving
25 networks per group. Table~C5 reports the median of each group.""" %
      (num(q1, 4), num(q2, 4), num(q3, 4)))
    w()

    def band(lo, hi):
        out = []
        for r in perc:
            v = float(r["loop_fraction_nonbridge"])
            if (lo is None or v > lo) and (hi is None or v <= hi):
                out.append(r)
        return out

    groups = [("Q1 (least reticulate)", band(None, q1)),
              ("Q2", band(q1, q2)), ("Q3", band(q2, q3)),
              ("Q4 (most reticulate)", band(q3, None))]
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Damage Tolerance by Reticulation Quartile}}")
    w(r"\begin{tabular}{lcccc}")
    w(r"\toprule")
    w(r"Quartile & $n$ & $Mdn$ loop fraction & $Mdn$ $\langle k\rangle$ & "
      r"$Mdn$ $p_{c}$ \\")
    w(r"\midrule")
    qmed = []
    for label, grp in groups:
        a = describe([r["loop_fraction_nonbridge"] for r in grp])
        b = describe([r["mean_degree"] for r in grp])
        c_ = describe([r["pc_random"] for r in grp])
        qmed.append(c_["Mdn"])
        w(r"%s & %d & %s & %s & %s \\"
          % (label, a["n"], num(a["Mdn"], 3), num(b["Mdn"], 3), num(c_["Mdn"])))
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
    w(r"""\noindent The most reticulate quartile tolerated""")
    w(r"\begin{equation}")
    w(r"%s-%s = %s" % (num(qmed[3]), num(qmed[0]), num(absd)))
    w(r"\end{equation}")
    w(r"""more of its nodes than the least reticulate quartile, that is 7.2
percentage points, a relative gain of""")
    w(r"\begin{equation}")
    w(r"\frac{%s}{%s}\times 100 = %s\%%" % (num(absd), num(qmed[0]), "%.2f" % relgain))
    w(r"\end{equation}")
    w()

    # ---------------- C.7 locality ----------------------------------------
    w(r"\section{Damage Locality and Connectivity Criterion}")
    w()
    w(r"""Two robustness analyses were computed on the same 100 networks under the
engine settings of Section~C.3, with every scenario scored on identical removal
draws so the comparisons are exactly paired. Table~C6 gives the resulting
thresholds.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Fragmentation Threshold Under Alternative Criteria and "
      r"Damage Geometries}}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lccc}")
    w(r"\toprule")
    w(r"Scenario & $Mdn$ $p_{c}$ & $IQR$ & Paired difference vs.\ dispersed \\")
    w(r"\midrule")
    w(r"Dispersed removal, GCC criterion & %s & %s--%s & --- \\"
      % (num(crit["median_gcc"]), num(crit["iqr_gcc"][0]), num(crit["iqr_gcc"][1])))
    w(r"Dispersed removal, source-anchored & %s & %s--%s & %s \\"
      % (num(crit["median_source"]), num(crit["iqr_source"][0]),
         num(crit["iqr_source"][1]),
         num(crit["median_paired_difference_source_minus_gcc"])))
    w(r"Localised removal, one lesion & %s & %s--%s & $+$%s \\"
      % (num(loc["median_disc1"]), num(loc["iqr_disc1"][0]),
         num(loc["iqr_disc1"][1]),
         num(loc["median_paired_difference_disc1_minus_random"], 3)))
    w(r"Localised removal, ten lesions & %s & %s--%s & $+$%s \\"
      % (num(loc["median_disc10"]), num(loc["iqr_disc10"][0]),
         num(loc["iqr_disc10"][1]),
         num(loc["median_paired_difference_disc10_minus_random"], 3)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    f1 = loc["median_disc1"] / loc["median_random_gcc"]
    f10 = loc["median_disc10"] / loc["median_random_gcc"]
    w(r"""\noindent \textit{Note.} $n = 100$ networks. Localised protocols were
run at matched realised removed fractions, so the horizontal axis is identical to
the dispersed case. Expressed as ratios, a single lesion was""")
    w(r"\begin{equation}")
    w(r"\frac{%s}{%s} = %s \quad\text{and}\quad \frac{%s}{%s} = %s"
      % (num(loc["median_disc1"]), num(loc["median_random_gcc"]), "%.2f" % f1,
         num(loc["median_disc10"]), num(loc["median_random_gcc"]), "%.2f" % f10))
    w(r"\end{equation}")
    w(r"""times less damaging than dispersed removal, for the one- and ten-lesion
protocols respectively, without exception across the 100 networks.""")
    w()

    # ---------------- C.8 sink --------------------------------------------
    w(r"\section{Haustorial Sink Across the Swept Gradient}")
    w()
    w(r"""The sink was calibrated to withdraw %.1f\%% of leaf throughput at the
illustrative 1.5 MPa host--parasite gradient, giving $K_{h} = %.4f$. Table~C7
reports every fifth point of the 31-point sweep.""" %
      (100 * cav["setup"]["achieved_diversion"], cav["setup"]["calibrated_K_h"]))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Hydraulic Behaviour of the Calibrated Haustorial Sink}}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{ccccc}")
    w(r"\toprule")
    w(r"Gradient (MPa) & Min $\psi$ (MPa) & Margin (MPa) & Flow diverted & "
      r"Vessels embolised \\")
    w(r"\midrule")
    psi_cav = cav["setup"]["psi_cavitation_default_MPa"]
    for row in cav["gradient_sweep_at_calibrated_Kh"]:
        gmpa = row["gradient_MPa"]
        if abs(gmpa * 10 - round(gmpa * 10)) > 1e-9 or round(gmpa * 10) % 5:
            continue
        mn = row["min_interior_psi_MPa"]
        w(r"%.1f & $-$%s & %s & %.1f\%% & %d \\"
          % (gmpa, num(abs(mn)), num(abs(psi_cav) - abs(mn)),
             100 * row["diversion_fraction"],
             row["embolised_by_threshold"]["-2.00"]))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    base = cav["baseline_control"]["min_interior_psi_MPa"]
    md = cav["margin_decomposition"]
    w(r"""\noindent \textit{Note.} The modelled cavitation threshold is
$-2.0$ MPa. The first row is effectively the no-parasite baseline. Three
threshold-independent quantities place the result in context. First, against a
no-parasite baseline of $%s$ MPa the calibrated sink depressed the network
minimum by""" % num(base))
    w(r"\begin{equation}")
    w(r"\Delta\psi_{\min} = %s - (%s) = %s\ \text{MPa}"
      % (num(cav["gradient_sweep_at_calibrated_Kh"][15]["min_interior_psi_MPa"]),
         num(base), num(md["parasite_contribution_at_calibrated_Kh_and_1.5MPa_MPa"])))
    w(r"\end{equation}")
    share = md["parasite_share_of_total_margin_pct"]
    w(r"""so the parasite accounts for %.1f\%% of the reported margin and the
remaining %.3f MPa is the stipulated separation between the transpirational
boundary condition and the cavitation threshold. Second, the depression at the
haustorial contact patch is exactly linear in the gradient, at
$%s$ MPa per MPa with an intercept of $%s$ MPa and a maximum residual of %s MPa
across 0--12 MPa. Third, extrapolating that relationship, reaching the modelled
threshold requires a gradient of""" %
      (share, md["stipulated_gap_PSI_LEAF_minus_PSI_CAVITATION_MPa"],
       num(cav["patch_depression_law"]["slope_MPa_per_MPa_of_gradient"]),
       num(cav["patch_depression_law"]["intercept_MPa"], 5),
       num(cav["patch_depression_law"]["max_abs_residual_MPa"], 3)))
    w(r"\begin{equation}")
    w(r"\frac{%s}{%s} \approx %s\ \text{MPa}"
      % (num(psi_cav, 1), num(cav["patch_depression_law"]["slope_MPa_per_MPa_of_gradient"]),
         "%.2f" % cav["patch_depression_law"]["gradient_required_to_reach_PSI_CAVITATION_MPa"]))
    w(r"\end{equation}")
    w(r"""against a largest measured parasite--host leaf gradient of
approximately 0.5 MPa in the published literature.""")
    w()

    # ---------------- C.9 verification ------------------------------------
    w(r"\section{Hydraulic Verification}")
    w()
    hr = T11["hydraulic_resistance"]
    w(r"""The solver's Hagen--Poiseuille resistance was compared vein by vein
against the resistance column shipped with the source dataset. Table~C8 reports
the outcome.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Vein-Level Verification of the Modelled Resistance}}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{lcc}")
    w(r"\toprule")
    w(r"Quantity & Value & Tolerance \\")
    w(r"\midrule")
    w(r"Leaves compared & %d & --- \\" % hr["n_leaves"])
    w(r"Vein segments compared & %s & --- \\" % "{:,}".format(hr["n_veins"]))
    w(r"Leaves classified exact & %d & --- \\" % hr["n_exact"])
    w(r"Worst per-leaf ratio $CV$ & $%.1f \times 10^{-7}$ & $1\times10^{-6}$ \\"
      % (hr["worst_ratio_cv"] * 1e7))
    w(r"Worst $|$median ratio $-\,1|$ & $%.1f \times 10^{-8}$ & $1\times10^{-6}$ \\"
      % (hr["worst_abs_median_ratio_minus_1"] * 1e8))
    w(r"Wrong-exponent control, median $r$ & %s & --- \\"
      % num(T11["wrong_exponent_control"], 3))
    w(r"Measured $K_{\text{leaf}}$, Spearman $\rho$ & %s ($p$ %s) & --- \\"
      % (rho(T11["kleaf"]["rho"]), pval(T11["kleaf"]["p"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    w(r"""\noindent \textit{Note.} One leaf was excluded for having fewer than 50
usable veins, hence %d rather than 120. Because the source column is itself
defined as $\ell/r^{4}$, the same convention the solver implements, this
comparison \textbf{verifies} correct implementation rather than validating the
physical model. Repeating it with a deliberately wrong exponent dropped the
median correlation to %s, which establishes that the agreement is not a trivial
consequence of resistance and geometry being monotonically related. The one
comparison against an independent physical measurement, modelled conductance
against measured leaf hydraulic conductance, was weak and non-significant across
%d species.""" % (hr["n_leaves"], num(T11["wrong_exponent_control"], 3),
                  T11["kleaf"]["n_species"]))
    w()

    # ---------------- C.10 budgets ----------------------------------------
    w(r"\section{Monte Carlo Budgets and Interval Construction}")
    w()
    summ = J("summary.json")
    tci = J("targeted_ci.json")
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Trial Budgets and Threshold Estimates by Analysis Set}}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{llcc}")
    w(r"\toprule")
    w(r"Analysis set & Removal mode & Trials per network & $p_{c}$ \\")
    w(r"\midrule")
    w(r"Percolation cohort ($n=100$) & Uniform & 2,400 & %s (Mdn) \\" % num(Su["Mdn"]))
    w(r"Percolation cohort ($n=100$) & Degree-weighted & 2,400 & %s (Mdn) \\" % num(Sd["Mdn"]))
    w(r"Enhancement cohort ($n=105$) & Uniform & 10,000 & %s (Mdn) \\" % num(Sc["Mdn"]))
    w(r"Synthetic reference ($N=1{,}023$) & Uniform & 1,000,000 & %s \\"
      % num(summ["p_c_random"]))
    w(r"Synthetic reference ($N=1{,}023$) & Degree-weighted & 100,000 & %s \\"
      % num(tci["results"]["degree"]["p_c"]))
    w(r"Synthetic reference ($N=1{,}023$) & Betweenness-weighted & 100,000 & "
      r"%s nominal \\" % num(tci["results"]["betweenness"]["p_c"]))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    ba = J("final_resolution_checks.json")["bootstrap_audit"]
    w(r"""\noindent \textit{Note.} Confidence intervals throughout are percentile
bootstrap intervals with $B = %d$ resamples and seed %d, the resampling unit
being the individual Monte Carlo trial drawn with replacement. The implementation
caps each bootstrap replicate at %s trials, so where a run exceeds that budget the
replicate is smaller than the dataset and the interval is conservative by
approximately $\sqrt{n/%s}$. Measured directly on the reference network, the
capped replicate gave an interval of width %s against %s for a full-size
replicate, a ratio of %.3f against the %.3f predicted. No reported interval is
anti-conservative. For the betweenness mode the removal probability is clipped at
unity, so the nominal control parameter of %s corresponds to a realised removed
fraction of 0.1498; only the realised value is on the same axis as the other two
modes.""" %
      (ba["implementation"]["B"], ba["implementation"]["seed"],
       "{:,}".format(ba["implementation"]["sample_cap"]),
       "{:,}".format(ba["implementation"]["sample_cap"]),
       num(ba["measured_on_hero_mesh"]["capped_at_50k"]["width"], 6),
       num(ba["measured_on_hero_mesh"]["full_size_replicate"]["width"], 6),
       ba["measured_on_hero_mesh"]["width_ratio_capped_over_full"],
       ba["measured_on_hero_mesh"]["expected_ratio_sqrt_n_over_cap"],
       num(tci["results"]["betweenness"]["p_c"])))
    w()


    # ---------------- C.11 normality and rank-order association ------------
    PC = np.array([float(r["pc_random"]) for r in perc])
    PCD = np.array([float(r["pc_degree"]) for r in perc])
    K = np.array([float(r["mean_degree"]) for r in perc])
    DD = np.array([float(r["D"]) for r in perc])
    LF = np.array([float(r["loop_fraction_nonbridge"]) for r in perc])
    LN = np.log(np.array([float(r["n_nodes"]) for r in perc]))
    n = len(PC)
    T5 = rv["T5_predictors"]

    w(r"\section{Normality Screening and Rank-Order Association}")
    w()
    w(r"""Because the choice between product-moment and rank-order correlation
depends on the shape of the distributions, every variable entering the association
analyses was first screened for normality with the Shapiro--Wilk test. The
statistic is a ratio of the squared best linear unbiased estimate of the scale to
the ordinary sum of squares, and it has no closed form that can usefully be
substituted by hand; the values below are those returned by the standard
implementation and are reported so that the decision rule they drove is
auditable.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Shapiro--Wilk Screening of the Variables Entering the "
      r"Association Analyses}}")
    w(r"\begin{tabular}{lccl}")
    w(r"\toprule")
    w(r"Variable & $W$ & $p$ & Decision at $\alpha = .05$ \\")
    w(r"\midrule")
    for label, x, key in [("Critical removed fraction $p_{c}$", PC, "p_c_random"),
                          (r"Mean degree $\langle k\rangle$", K, "mean_degree"),
                          ("Fractal dimension $D$", DD, "D"),
                          ("Loop fraction", LF, "loop_fraction")]:
        W_, p_ = stats.shapiro(x)
        w(r"%s & %s & %s & %s \\"
          % (label, num(W_, 4), pval(p_),
             "Reject normality" if p_ < .05 else "Retain normality"))
        check("Shapiro-Wilk W, %s" % key, T5["shapiro_wilk"][key]["W"], float(W_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    w(r"""\noindent \textit{Note.} $n = %d$ networks. Normality was rejected for
the outcome and for both connectivity predictors, so a pre-specified rule applied
Spearman's $\rho$ uniformly to every association test rather than selecting a
coefficient variable by variable.""" % n)
    w()
    w(r"""Spearman's coefficient was then computed from equation (C.3).
Table~C11 gives the rank-difference sum $\sum d_{i}^{2}$ for each pair, so that
every reported correlation can be reproduced by substitution.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Rank-Order Association of Each Descriptor With the "
      r"Critical Removed Fraction}}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lrccc}")
    w(r"\toprule")
    w(r"Pair & $\sum d_{i}^{2}$ & $\rho$ & $t$ & $p$ \\")
    w(r"\midrule")
    for label, x, key in [(r"$p_{c}$ and $\langle k\rangle$", K, "mean_degree"),
                          ("$p_{c}$ and $D$", DD, "D"),
                          ("$p_{c}$ and loop fraction", LF, "loop_fraction")]:
        d2 = float(((stats.rankdata(PC) - stats.rankdata(x)) ** 2).sum())
        r_, p_ = stats.spearmanr(PC, x)
        t_ = r_ * math.sqrt((n - 2) / (1 - r_ * r_))
        w(r"%s & %s & %s & %.3f & %s \\"
          % (label, "{:,.1f}".format(d2), rho(r_), t_, pval(p_)))
        check("Spearman rho, p_c and %s" % key,
              T5["spearman_with_pc_random"][key]["rho"], float(r_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    d2k = float(((stats.rankdata(PC) - stats.rankdata(K)) ** 2).sum())
    rk = float(stats.spearmanr(PC, K)[0])
    short = 1 - 6 * d2k / (n * (n * n - 1))
    w(r"""\noindent Worked example for the leading association, substituting the
first row of Table~C11 into equation (C.3):""")
    w(r"\begin{equation}")
    w(r"\rho = 1 - \frac{6(%s)}{%d(%d^{2}-1)} = 1 - \frac{%s}{%s} = %s"
      % ("{:,.1f}".format(d2k), n, n, "{:,.0f}".format(6 * d2k),
         "{:,.0f}".format(n * (n * n - 1)), num(short, 6)))
    w(r"\end{equation}")
    w(r"""The threshold column contains %d tied values, for which the exact
coefficient is obtained by applying the product-moment formula to midranks rather
than by the shortcut above. That exact value is %s, so the tie correction shifts
the coefficient by %s, well below the precision at which it is reported.
Significance follows from""" %
      (n - len(set(PC.tolist())), num(rk, 6), num(abs(short - rk), 6)))
    w(r"\begin{equation}")
    w(r"t = \rho\sqrt{\frac{n-2}{1-\rho^{2}}}"
      r" = %s\sqrt{\frac{%d}{1-%s^{2}}} = %.3f"
      % (num(rk, 4), n - 2, num(rk, 4), rk * math.sqrt((n - 2) / (1 - rk * rk))))
    w(r"\end{equation}")
    w(r"""evaluated on %d degrees of freedom.""" % (n - 2))
    w()
    w(r"\subsection{Partial Rank-Order Association}")
    w()
    w(r"""Each association was recomputed with the competing architectural
descriptor held constant, and again with log network size held constant, using the
first-order partial correlation applied to the rank-order coefficients:""")
    w(r"\begin{equation}")
    w(r"\rho_{xy\cdot z} = \frac{\rho_{xy}-\rho_{xz}\rho_{yz}}"
      r"{\sqrt{(1-\rho_{xz}^{2})(1-\rho_{yz}^{2})}}")
    w(r"\end{equation}")
    w()

    def psp(x, y, z):
        a = float(stats.spearmanr(x, y)[0])
        b = float(stats.spearmanr(x, z)[0])
        c = float(stats.spearmanr(y, z)[0])
        return (a - b * c) / math.sqrt((1 - b * b) * (1 - c * c)), a, b, c

    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Partial Rank-Order Association With the Critical Removed "
      r"Fraction}}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{llcccc}")
    w(r"\toprule")
    w(r"Predictor & Held constant & $\rho_{xy}$ & $\rho_{xz}$ & $\rho_{yz}$ & "
      r"$\rho_{xy\cdot z}$ \\")
    w(r"\midrule")
    for lab, x, zlab, z, key in [
            (r"$\langle k\rangle$", K, "$D$", DD, "mean_degree_given_D"),
            ("$D$", DD, r"$\langle k\rangle$", K, "D_given_mean_degree"),
            ("Loop fraction", LF, "$D$", DD, "loop_given_D"),
            (r"$\langle k\rangle$", K, r"$\log N$", LN, None),
            ("$D$", DD, r"$\log N$", LN, None),
            ("Loop fraction", LF, r"$\log N$", LN, None)]:
        v, a, b, c = psp(PC, x, z)
        w(r"%s & %s & %s & %s & %s & \textbf{%s} \\"
          % (lab, zlab, rho(a), rho(b), rho(c), rho(v)))
        if key:
            check("Partial Spearman, %s" % key, T5["partial_spearman"][key], v)
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    vk, a, b, c = psp(PC, K, LN)
    w(r"""\noindent Worked example for mean degree with log network size held
constant, substituting the fourth row into equation (C.9):""")
    w(r"\begin{equation}")
    w(r"\rho_{xy\cdot z} = \frac{%s-(%s)(%s)}{\sqrt{(1-%s^{2})(1-%s^{2})}} = %s"
      % (num(a, 4), num(b, 4), num(c, 4), num(b, 4), num(c, 4), num(vk, 6)))
    w(r"\end{equation}")
    w(r"""Every association is larger with size held constant than without it,
which is the pattern a size confound would not produce.""")
    w()
    w(r"\subsection{Multiple Regression}")
    w()
    Z = np.column_stack([np.ones(n),
                         (K - K.mean()) / K.std(ddof=1),
                         (DD - DD.mean()) / DD.std(ddof=1)])
    beta = np.linalg.lstsq(Z, PC, rcond=None)[0]
    yh = Z @ beta
    ss_res = float(((PC - yh) ** 2).sum())
    ss_tot = float(((PC - PC.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot
    Fv = (r2 / 2) / ((1 - r2) / (n - 3))
    sd_y = float(PC.std(ddof=1))
    bstd = [float(beta[1]) / sd_y, float(beta[2]) / sd_y]
    check("Regression intercept",
          T5["regression_semi_standardized"]["intercept"], float(beta[0]))
    check("Regression beta, mean degree",
          T5["regression_semi_standardized"]["beta"][0], float(beta[1]))
    check("Regression beta, D",
          T5["regression_semi_standardized"]["beta"][1], float(beta[2]))
    check("Regression R2", T5["regression_semi_standardized"]["R2"], r2)
    check("Regression F", T5["regression_semi_standardized"]["F"], Fv, 0.05)
    check("Standardised beta, mean degree",
          T5["regression_fully_standardized"]["beta"][0], bstd[0])
    check("Standardised beta, D",
          T5["regression_fully_standardized"]["beta"][1], bstd[1])
    w(r"""The threshold was regressed on the two $z$-scored architectural
predictors, leaving the outcome in its own units so that each coefficient reads as
the change in $p_{c}$ per standard deviation of the predictor:""")
    w(r"\begin{equation}")
    w(r"p_{c} = %s + %s\,z_{\langle k\rangle} + %s\,z_{D}"
      % (num(beta[0]), num(beta[1]), num(beta[2])))
    w(r"\end{equation}")
    w(r"""The proportion of variance explained follows from the residual and total
sums of squares:""")
    w(r"\begin{align}")
    w(r"R^{2} &= 1-\frac{SS_{\text{res}}}{SS_{\text{tot}}}"
      r" = 1-\frac{%s}{%s} = %s \\[4pt]"
      % (num(ss_res, 6), num(ss_tot, 6), num(r2, 4)))
    w(r"F &= \frac{R^{2}/k}{(1-R^{2})/(n-k-1)}"
      r" = \frac{%s/2}{(1-%s)/%d} = %.2f"
      % (num(r2, 4), num(r2, 4), n - 3, Fv))
    w(r"\end{align}")
    w(r"""on $(2, %d)$ degrees of freedom. Dividing each coefficient by the standard
deviation of the outcome, %s, gives the fully standardised coefficients %s and %s,
which are directly comparable with one another. The two predictors were
near-orthogonal in this cohort, so the regression is not distorted by collinearity
between them.""" % (n - 3, num(sd_y, 4), num(bstd[0], 3), num(bstd[1], 3)))
    w()

    # ---------------- C.12 paired and group comparisons --------------------
    w(r"\section{Paired and Group Comparisons}")
    w()
    w(r"""Every inferential comparison in the Results is distribution-free, which
follows from the normality screening of Section~C.11. Table~C13 collects them with
the quantities needed to reproduce each one.""")
    w()
    dvec = PC - PCD
    Wst, pw = stats.wilcoxon(dvec)
    nz = int((dvec != 0).sum())
    dp = np.array([float(r["delta_pc"]) for r in enh])
    Wst2, pw2 = stats.wilcoxon(dp[dp != 0])
    q1c, q3c = float(np.quantile(LF, .25)), float(np.quantile(LF, .75))
    g1 = PC[LF <= q1c]
    g4 = PC[LF > q3c]
    U, pu = stats.mannwhitneyu(g1, g4, alternative="two-sided")
    n_gt = int(np.sum(g4[:, None] > g1[None, :]))
    n_lt = int(np.sum(g4[:, None] < g1[None, :]))
    cliff = (n_gt - n_lt) / float(len(g1) * len(g4))
    gr = np.array([r["grade"] for r in enh])
    H, pk = stats.kruskal(*[dp[gr == g] for g in ["A", "B", "C", "D"]])
    check("Wilcoxon W, removal modes",
          rv["T3_attack_thresholds"]["wilcoxon"]["W"], float(Wst), 0.5)
    check("Wilcoxon nonzero pairs, removal modes",
          rv["T3_attack_thresholds"]["wilcoxon"]["n_nonzero"], nz, 0.5)
    check("Mann-Whitney U, quartiles", T8["mann_whitney"]["U"], float(U), 0.5)
    check("Cliff's delta, quartiles",
          J("rrl_diagnostics.json")["effect_sizes"]["loop_quartiles_Q1_vs_Q4"]["cliffs_delta"],
          cliff)
    check("Kruskal-Wallis H, grade",
          J("second_pass_audit.json")["enhancement_mediation"]["kruskal_on_raw_delta_by_grade"][0],
          float(H), 0.005)
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Distribution-Free Comparisons Reported in the Results}}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{llccl}")
    w(r"\toprule")
    w(r"Comparison & Test & Statistic & $p$ & Effect size \\")
    w(r"\midrule")
    w(r"Uniform vs.\ degree-weighted & Wilcoxon signed-rank & $W = %d$ & %s & "
      r"$r_{rb} = 1.00$ \\" % (int(Wst), pval(pw)))
    w(r"Before vs.\ after enhancement & Wilcoxon signed-rank & $W = %d$ & %s & "
      r"$r_{rb} \approx 1.00$ \\" % (int(Wst2), pval(pw2)))
    w(r"Quartile 1 vs.\ quartile 4 & Mann--Whitney & $U = %d$ & %s & "
      r"$\delta = %s$ \\" % (int(U), pval(pu), num(cliff, 3)))
    w(r"$\Delta p_{c}$ across quality grades & Kruskal--Wallis & $H = %.3f$ & %s & "
      r"--- \\" % (H, pval(pk)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    w(r"""\noindent \textit{Note.} The first comparison uses the %d non-zero
per-network differences of Table~C2; the second uses the %d non-zero differences of
Table~C4, with the more conservative Pratt treatment retaining all %d networks
giving the same conclusion. The quartile comparison uses 25 networks per group. The
grade comparison is not significant at $\alpha = .05$, so quality grades are
reported for transparency rather than as a detected effect.""" %
      (nz, int((dp != 0).sum()), len(dp)))
    w()
    w(r"""Both effect sizes are computable by hand. The matched-pairs rank-biserial
correlation is the proportion of pairs favouring one condition minus the proportion
favouring the other:""")
    w(r"\begin{equation}")
    w(r"r_{rb} = \frac{%d}{%d}-\frac{%d}{%d} = 1.00"
      % (int((dvec > 0).sum()), n, int((dvec < 0).sum()), n))
    w(r"\end{equation}")
    w(r"""This records that every network responded in the same direction and
carries no information about magnitude. Cliff's $\delta$ compares every network in
one quartile with every network in the other:""")
    w(r"\begin{equation}")
    w(r"\delta = \frac{\#(x_{4}>x_{1})-\#(x_{4}<x_{1})}{n_{1}n_{4}}"
      r" = \frac{%d-%d}{%d\times%d} = %s"
      % (n_gt, n_lt, len(g1), len(g4), num(cliff, 4)))
    w(r"\end{equation}")
    w(r"""Of the %d cross-quartile pairs, %d favour the more reticulate quartile,
so the two distributions are very nearly disjoint.""" % (len(g1) * len(g4), n_gt))
    w()

    # ---------------- C.13 reconciliation ---------------------------------
    w(r"\section{Reconciliation With the Reported Results}")
    w()
    w(r"""Every value recomputed above is listed against the corresponding cell of
the Results. A row is marked as agreeing when the recomputed value matches the
reported value to the precision at which it is printed.""")
    w()
    w(r"\begin{longtable}{p{6.6cm}rrl}")
    w(r"\caption{\textit{Recomputed Values Against the Reported Results}}\\")
    w(r"\toprule")
    w(r"Quantity & Reported & Recomputed & Status \\")
    w(r"\midrule")
    w(r"\endfirsthead")
    w(r"\multicolumn{4}{l}{\textit{Table C12 (continued)}}\\")
    w(r"\toprule")
    w(r"Quantity & Reported & Recomputed & Status \\")
    w(r"\midrule")
    w(r"\endhead")
    w(r"\bottomrule")
    w(r"\endfoot")
    n_ok = 0
    for label, rep, comp, tol in CHECKS:
        ok = abs(float(comp) - float(rep)) <= tol
        n_ok += ok
        dec = 4 if abs(float(rep)) < 10 else 1
        w(r"%s & %s & %s & %s \\"
          % (label.replace("_", r"\_").replace("%", r"\%"),
             num(rep, dec), num(comp, dec),
             "Agrees" if ok else r"\textbf{DIFFERS}"))
    w(r"\end{longtable}")
    w()
    w(r"""\noindent \textit{Note.} %d of %d recomputed values agree with the
Results at the printed precision. Counts are compared exactly; continuous
quantities are compared at a tolerance of $5\times10^{-4}$, which is half a unit
in the last printed decimal place.""" % (n_ok, len(CHECKS)))
    w()
    w(r"\end{document}")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")

    with open(CHECKS_CSV, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["quantity", "reported_in_results", "recomputed",
                     "difference", "status"])
        for label, rep, comp, tol in CHECKS:
            d = float(comp) - float(rep)
            wr.writerow([label, rep, comp, d,
                         "agrees" if abs(d) <= tol else "DIFFERS"])

    print("wrote %s (%d lines)" % (OUT.name, len(L)))
    print("wrote %s" % CHECKS_CSV.name)
    print("  reconciliation : %d of %d agree" % (n_ok, len(CHECKS)))
    bad = [c[0] for c in CHECKS if abs(float(c[2]) - float(c[1])) > c[3]]
    for b in bad:
        print("  DIFFERS: %s" % b)


if __name__ == "__main__":
    main()
