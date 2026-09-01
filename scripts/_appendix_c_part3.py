# -*- coding: utf-8 -*-
r"""Part 3 of the Appendix C builder: characterisation of the networks and the
association among the architectural descriptors (Results Tables 1 and 2)."""

from __future__ import annotations

import math

import numpy as np
from scipy import stats


def empirical_descriptors(C):
    w, steps, num = C["w"], C["steps"], C["num"]
    describe, check = C["describe"], C["check"]
    char, T1 = C["char"], C["T1"]

    w(r"\section{Structural and Hydraulic Characterisation of the Empirical "
      r"Networks}\label{sec:empirical}")
    w()
    w(r"""Descriptors are as defined in Section~\ref{sec:engine}:
Equation~\eqref{eq:meandeg} for mean degree, \eqref{eq:loopfrac} for the loop and
bridge fractions, \eqref{eq:box} for $D$, \eqref{eq:kleaf} for modelled
conductance. The two sum columns reproduce each mean and standard deviation
through Equations~\eqref{eq:mean} and~\eqref{eq:sd}.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Structural and Hydraulic Descriptors of the Empirical "
      r"Networks}}\label{tab:empdesc}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{lrrrrrr}")
    w(r"\toprule")
    w(r"Descriptor & $\sum x$ & $\sum x^{2}$ & $M$ & $SD$ & $Mdn$ & Range \\")
    w(r"\midrule")
    rows = [
        (r"Mean degree $\langle k\rangle$", "mean_degree", 3, "mean_degree"),
        ("Degree $SD$", "degree_sd", 3, "degree_sd"),
        ("Loop fraction", "loop_fraction_nonbridge", 3, "loop_fraction"),
        ("Bridge fraction", "bridge_fraction", 3, "bridge_fraction"),
        ("Fractal dimension $D$", "D", 3, "D"),
        ("GCC fraction", "gcc_fraction", 3, "gcc_fraction"),
    ]
    S_by_key = {}
    for label, col, dec, key in rows:
        S = describe([r[col] for r in char])
        S_by_key[key] = S
        w(r"%s & %s & %s & %s & %s & %s & [%s, %s] \\"
          % (label, num(S["sum"], 3), num(S["sum_sq"], 3), num(S["M"], dec),
             num(S["SD"], dec), num(S["Mdn"], dec), num(S["min"], dec),
             num(S["max"], dec)))
        check("Empirical %s M" % key, T1["empirical"][key]["M"], S["M"])
        check("Empirical %s SD" % key, T1["empirical"][key]["SD"], S["SD"])
        check("Empirical %s Mdn" % key, T1["empirical"][key]["Mdn"], S["Mdn"])
    SC = describe([r["effective_conductance"] for r in char])
    w(r"Modelled conductance & %s & %s & %s & %s & %s & [%s, %s] \\"
      % (num(SC["sum"], 4), num(SC["sum_sq"], 4), C["sci"](SC["M"]),
         C["sci"](SC["SD"]), C["sci"](SC["Mdn"]), C["sci"](SC["min"], 1),
         C["sci"](SC["max"], 1)))
    check("Empirical conductance M",
          T1["empirical"]["hydraulic_conductance"]["M"], SC["M"], 5e-5)
    check("Empirical conductance Mdn",
          T1["empirical"]["hydraulic_conductance"]["Mdn"], SC["Mdn"], 5e-5)
    SN = describe([r["n_nodes"] for r in char])
    w(r"Network size $N$ & %s & --- & %s & %s & %s & [%s, %s] \\"
      % ("{:,}".format(int(SN["sum"])), "{:,.0f}".format(SN["M"]),
         "{:,.0f}".format(SN["SD"]), "{:,.0f}".format(SN["Mdn"]),
         "{:,.0f}".format(SN["min"]), "{:,.0f}".format(SN["max"])))
    SE = describe([r["n_edges"] for r in char])
    w(r"Network size $E$ & %s & --- & %s & %s & %s & [%s, %s] \\"
      % ("{:,}".format(int(SE["sum"])), "{:,.0f}".format(SE["M"]),
         "{:,.0f}".format(SE["SD"]), "{:,.0f}".format(SE["Mdn"]),
         "{:,.0f}".format(SE["min"]), "{:,.0f}".format(SE["max"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Empirical N M", T1["empirical"]["N"]["M"], SN["M"], 0.5)
    check("Empirical N Mdn", T1["empirical"]["N"]["Mdn"], SN["Mdn"], 0.5)
    w(r"""\noindent \textit{Note.} $n = %d$ networks passing the characterisation
screen. Bridge fraction is the exact complement of loop fraction, so the two rows
sum to unity. The size rows omit $\sum x^{2}$, which exceeds ordinary display
precision; their dispersion is the range. Modelled conductance is in normalised
units and strongly right-skewed.""" % SN["n"])
    w()
    w(r"""\noindent Worked example, mean degree, from the first row:""")
    mk = S_by_key["mean_degree"]
    corr = mk["n"] * mk["M"] ** 2
    steps(
        r"\overline{\langle k\rangle} &= \frac{\sum \langle k\rangle}{n}"
        r" = \frac{%s}{%d} = %s"
        % (num(mk["sum"], 3), mk["n"], num(mk["M"], 6)),
        r"s^{2} &= \frac{\sum \langle k\rangle^{2}-n\bar{x}^{2}}{n-1}"
        r" = \frac{%s-%d(%s)^{2}}{%d}"
        % (num(mk["sum_sq"], 3), mk["n"], num(mk["M"], 6), mk["n"] - 1),
        r"&= \frac{%s-%s}{%d} = \frac{%s}{%d} = %s"
        % (num(mk["sum_sq"], 4), num(corr, 4), mk["n"] - 1,
           num(mk["sum_sq"] - corr, 6), mk["n"] - 1, num(mk["SD"] ** 2, 8)),
        r"s &= \sqrt{%s} = %s" % (num(mk["SD"] ** 2, 8), num(mk["SD"], 6)),
    )
    w()


def synthetic_descriptors(C):
    w, num, describe, check = C["w"], C["num"], C["describe"], C["check"]
    syn, T1 = C["syn"], C["T1"]
    w(r"\section{The Synthetic Networks as a Comparison Set}"
      r"\label{sec:synthetic}")
    w()
    w(r"""The %d synthetic networks are generated meshes, not leaves. They are
characterised by the same code path as the empirical networks (same
box-counting window, same bridge enumeration, same conductance solve), so
Table~\ref{tab:syndesc} is directly comparable with
Table~\ref{tab:empdesc}.""" % len(syn))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Descriptors of the Synthetic Networks}}"
      r"\label{tab:syndesc}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{lrrrrrr}")
    w(r"\toprule")
    w(r"Descriptor & $\sum x$ & $\sum x^{2}$ & $M$ & $SD$ & $Mdn$ & Range \\")
    w(r"\midrule")
    for label, col, dec, key in [
            (r"Mean degree $\langle k\rangle$", "mean_degree", 3, "mean_degree"),
            ("Degree $SD$", "degree_sd", 3, "degree_sd"),
            ("Loop fraction", "loop_fraction_nonbridge", 3, "loop_fraction"),
            ("Bridge fraction", "bridge_fraction", 3, "bridge_fraction"),
            ("Fractal dimension $D$", "D", 3, "D"),
            ("GCC fraction", "gcc_fraction", 3, "gcc_fraction")]:
        S = describe([r[col] for r in syn])
        w(r"%s & %s & %s & %s & %s & %s & [%s, %s] \\"
          % (label, num(S["sum"], 3), num(S["sum_sq"], 3), num(S["M"], dec),
             num(S["SD"], dec), num(S["Mdn"], dec), num(S["min"], dec),
             num(S["max"], dec)))
        check("Synthetic %s M" % key, T1["synthetic"][key]["M"], S["M"])
        check("Synthetic %s SD" % key, T1["synthetic"][key]["SD"], S["SD"])
        check("Synthetic %s Mdn" % key, T1["synthetic"][key]["Mdn"], S["Mdn"])
    SC = describe([r["effective_conductance"] for r in syn])
    w(r"Modelled conductance & %s & %s & %s & %s & %s & [%s, %s] \\"
      % (num(SC["sum"], 4), num(SC["sum_sq"], 6), C["sci"](SC["M"]),
         C["sci"](SC["SD"]), C["sci"](SC["Mdn"]), C["sci"](SC["min"], 1),
         C["sci"](SC["max"], 1)))
    SN = describe([r["N"] for r in syn])
    w(r"Network size $N$ & %s & --- & %s & %s & %s & [%s, %s] \\"
      % ("{:,}".format(int(SN["sum"])), "{:,.0f}".format(SN["M"]),
         "{:,.0f}".format(SN["SD"]), "{:,.0f}".format(SN["Mdn"]),
         "{:,.0f}".format(SN["min"]), "{:,.0f}".format(SN["max"])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Synthetic N M", T1["synthetic"]["N"]["M"], SN["M"], 0.5)
    Sk = describe([r["mean_degree"] for r in syn])
    SD_ = describe([r["D"] for r in syn])
    ek = describe([r["mean_degree"] for r in C["char"]])
    eD = describe([r["D"] for r in C["char"]])
    w(r"""\noindent \textit{Note.} $n = %d$. The synthetic set spans
$\langle k\rangle \in [%s, %s]$ against the empirical $[%s, %s]$, and
$D \in [%s, %s]$ against the empirical $[%s, %s]$: it brackets the empirical
envelope in connectivity and extends past it at the top, and falls short of the
most space-filling leaves in $D$ because the estimator saturates on a branching
generator. Its degree standard deviation is markedly higher (%s against %s), so
no synthetic threshold is comparable in absolute value with an empirical
one.""" %
      (len(syn), num(Sk["min"], 3), num(Sk["max"], 3),
       num(ek["min"], 3), num(ek["max"], 3),
       num(SD_["min"], 3), num(SD_["max"], 3),
       num(eD["min"], 3), num(eD["max"], 3),
       num(describe([r["degree_sd"] for r in syn])["M"], 3),
       num(describe([r["degree_sd"] for r in C["char"]])["M"], 3)))
    w()


def descriptor_associations(C):
    w, steps, num = C["w"], C["steps"], C["num"]
    rho_, pval, check = C["rho"], C["pval"], C["check"]
    char, T2 = C["char"], C["T2"]
    n = len(char)

    def col(k):
        return np.array([float(r[k]) for r in char])

    K, LF, TF = col("mean_degree"), col("loop_fraction_nonbridge"), \
        col("terminal_fraction")
    GC, DD, NN = col("gcc_fraction"), col("D"), col("n_nodes")

    w(r"\section{Rank-Order Association Among the Architectural Descriptors}"
      r"\label{sec:descassoc}")
    w()
    w(r"""Each coefficient is Equation~\eqref{eq:spearman}, tested by
Equation~\eqref{eq:tstat} on $%d$ degrees of freedom. $H_{0}$ in every row is no
monotone relationship.""" % (n - 2))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Rank-Order Correlations Among the Architectural "
      r"Descriptors}}\label{tab:descassoc}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{lrccll}")
    w(r"\toprule")
    w(r"Variables correlated & $\sum d_{i}^{2}$ & $\rho$ & $t$ & $p$ & "
      r"Decision \\")
    w(r"\midrule")
    first = None
    for label, x, y, key in [
            ("Mean degree and loop fraction", K, LF, "mean_degree_x_loop"),
            ("Loop fraction and terminal fraction", LF, TF, "loop_x_terminal"),
            ("Loop fraction and GCC fraction", LF, GC, "loop_x_gcc"),
            ("Mean degree and fractal dimension", K, DD, "mean_degree_x_D"),
            ("Loop fraction and fractal dimension", LF, DD, "loop_x_D"),
            ("Loop fraction and network size", LF, NN, "loop_x_N")]:
        d2 = float(((stats.rankdata(x) - stats.rankdata(y)) ** 2).sum())
        r_, p_ = stats.spearmanr(x, y)
        t_ = float(r_) * math.sqrt((n - 2) / (1 - float(r_) ** 2))
        w(r"%s & %s & %s & %s & %s & %s \\"
          % (label, "{:,.1f}".format(d2), rho_(r_), C["sgn"](t_, 3), pval(p_),
             "Reject" if p_ < .05 else "Fail to reject"))
        check("Descriptor rho, %s" % key, T2[key]["rho"], float(r_))
        if first is None:
            first = (d2, float(r_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    d2, r_ = first
    den = n * (n * n - 1)
    short = 1 - 6 * d2 / den
    q = (n - 2) / (1 - r_ * r_)
    w(r"""\noindent \textit{Note.} $n = %d$; $df = %d$. Strength bands: below .20
very weak, .20--.39 weak, .40--.59 moderate, .60--.79 strong, .80 or above very
strong. Mean degree and loop fraction are rank-correlated at %s, so the two index
one connectivity axis; only mean degree and $D$ are entered jointly in
Section~\ref{sec:predictors}, and the cost of entering loop fraction instead is
computed in Section~\ref{sec:collinearity}.""" %
      (n, n - 2, rho_(T2["mean_degree_x_loop"]["rho"])))
    w()
    w(r"""\noindent Worked example, first row:""")
    steps(
        r"\rho &= 1 - \frac{6\sum d_{i}^{2}}{n(n^{2}-1)}"
        r" = 1 - \frac{6(%s)}{%d(%d^{2}-1)}"
        % ("{:,.1f}".format(d2), n, n),
        r"&= 1 - \frac{%s}{%s} = 1 - %s = %s"
        % ("{:,.0f}".format(6 * d2), "{:,.0f}".format(den),
           num(6 * d2 / den, 6), num(short, 6)),
        r"t &= \rho\sqrt{\frac{n-2}{1-\rho^{2}}}"
        r" = %s\sqrt{\frac{%d}{%s}} = %.3f"
        % (num(r_, 4), n - 2, num(1 - r_ * r_, 6), r_ * math.sqrt(q)),
    )
    w(r"""The tie-corrected coefficient from the midranks is %s, differing from
the shortcut by %s.""" % (num(r_, 6), num(abs(short - r_), 6)))
    w()
