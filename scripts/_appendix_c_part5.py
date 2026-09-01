# -*- coding: utf-8 -*-
r"""Part 5 of the Appendix C builder: normality screening, the association of
architecture with the threshold, the regression, and the synthetic causal grid
(Results Tables 6 and 7)."""

from __future__ import annotations

import math

import numpy as np
from scipy import stats


def _psp(x, y, z):
    a = float(stats.spearmanr(x, y)[0])
    b = float(stats.spearmanr(x, z)[0])
    c = float(stats.spearmanr(y, z)[0])
    return (a - b * c) / math.sqrt((1 - b * b) * (1 - c * c)), a, b, c


def normality(C):
    w, num, pval, check = C["w"], C["num"], C["pval"], C["check"]
    V, T5 = C["V"], C["T5"]
    n = len(V["PC"])
    w(r"\section{Normality Screening}\label{sec:normality}")
    w()
    w(r"""The Shapiro--Wilk statistic has no closed form usable by hand, so the
values below are those returned by the standard implementation, reported so that
the decision rule they drove is auditable.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Shapiro--Wilk Screening of the Variables Entering the "
      r"Association Analyses}}\label{tab:shapiro}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{lccl}")
    w(r"\toprule")
    w(r"Variable & $W$ & $p$ & Decision at $\alpha = .05$ \\")
    w(r"\midrule")
    for label, key, jkey in [
            ("Critical removed fraction $p_{c}$", "PC", "p_c_random"),
            (r"Mean degree $\langle k\rangle$", "K", "mean_degree"),
            ("Fractal dimension $D$", "DD", "D"),
            ("Loop fraction", "LF", "loop_fraction")]:
        W_, p_ = stats.shapiro(V[key])
        w(r"%s & %s & %s & %s \\"
          % (label, num(W_, 4), pval(p_),
             "Reject normality" if p_ < .05 else "Retain normality"))
        check("Shapiro-Wilk W, %s" % jkey, T5["shapiro_wilk"][jkey]["W"],
              float(W_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    w(r"""\noindent \textit{Note.} $n = %d$. Normality was rejected for the
outcome and both connectivity predictors. Under rule (i) of
Section~\ref{sec:formulas}, rejection anywhere in the set forces Spearman's
$\rho$ on every association test, and makes every group comparison in
Section~\ref{sec:comparisons} distribution-free. A product-moment coefficient
therefore appears in this appendix only as a diagnostic
(Sections~\ref{sec:collinearity} and~\ref{sec:grid}).""" % n)
    w()


def predictors(C):
    w, steps, num = C["w"], C["steps"], C["num"]
    rho_, pval, check = C["rho"], C["pval"], C["check"]
    V, T5 = C["V"], C["T5"]
    PC, K, DD, LF, LN = V["PC"], V["K"], V["DD"], V["LF"], V["LN"]
    n = len(PC)

    w(r"\section{Association of Architecture With the Threshold}"
      r"\label{sec:predictors}")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Rank-Order Association of Each Descriptor With the "
      r"Critical Removed Fraction}}\label{tab:pcassoc}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{lrccc}")
    w(r"\toprule")
    w(r"Pair & $\sum d_{i}^{2}$ & $\rho$ & $t$ & $p$ \\")
    w(r"\midrule")
    for label, x, key in [(r"$p_{c}$ and $\langle k\rangle$", K, "mean_degree"),
                          ("$p_{c}$ and $D$", DD, "D"),
                          ("$p_{c}$ and loop fraction", LF, "loop_fraction")]:
        d2 = float(((stats.rankdata(PC) - stats.rankdata(x)) ** 2).sum())
        r_, p_ = stats.spearmanr(PC, x)
        t_ = float(r_) * math.sqrt((n - 2) / (1 - float(r_) ** 2))
        w(r"%s & %s & %s & %s & %s \\"
          % (label, "{:,.1f}".format(d2), rho_(r_), C["sgn"](t_, 3),
             pval(p_)))
        check("Spearman rho, p_c and %s" % key,
              T5["spearman_with_pc_random"][key]["rho"], float(r_))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    d2k = float(((stats.rankdata(PC) - stats.rankdata(K)) ** 2).sum())
    rk = float(stats.spearmanr(PC, K)[0])
    den = n * (n * n - 1)
    short = 1 - 6 * d2k / den
    q = (n - 2) / (1 - rk * rk)
    n_tied = n - len(set(PC.tolist()))
    w(r"""\noindent \textit{Note.} $n = %d$; $df = %d$. Worked example, first
row:""" % (n, n - 2))
    steps(
        r"\rho &= 1 - \frac{6\sum d_{i}^{2}}{n(n^{2}-1)}"
        r" = 1 - \frac{6(%s)}{%d(%d^{2}-1)}"
        % ("{:,.1f}".format(d2k), n, n),
        r"&= 1 - \frac{%s}{%s} = 1 - %s = %s"
        % ("{:,.0f}".format(6 * d2k), "{:,.0f}".format(den),
           num(6 * d2k / den, 6), num(short, 6)),
        r"t &= \rho\sqrt{\frac{n-2}{1-\rho^{2}}}"
        r" = %s\sqrt{\frac{%d}{%s}} = %s \times %s = %.3f"
        % (num(rk, 4), n - 2, num(1 - rk * rk, 6), num(rk, 4),
           num(math.sqrt(q), 4), rk * math.sqrt(q)),
    )
    w(r"""The threshold column carries %d tied values; the tie-corrected
coefficient from the midranks is %s, differing from the shortcut by %s.""" %
      (n_tied, num(rk, 6), num(abs(short - rk), 6)))
    w()

    # ---- partials ---------------------------------------------------------
    w(r"\subsection{Partial Rank-Order Association}")
    w()
    w(r"""Each association is recomputed with the competing descriptor held
constant, and again with $\log N$ held constant, through
Equation~\eqref{eq:partial}. Log size is the control because the size
distribution spans nearly three orders of magnitude and
Equation~\eqref{eq:box} is area-dependent.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Partial Rank-Order Association With the Critical "
      r"Removed Fraction}}\label{tab:partial}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
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
        v, a, b, c = _psp(PC, x, z)
        w(r"%s & %s & %s & %s & %s & \textbf{%s} \\"
          % (lab, zlab, rho_(a), rho_(b), rho_(c), rho_(v)))
        if key:
            check("Partial Spearman, %s" % key, T5["partial_spearman"][key], v)
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    vk, a, b, c = _psp(PC, K, LN)
    _pn = a - b * c
    _pd = math.sqrt((1 - b * b) * (1 - c * c))
    w(r"""\noindent Worked example, fourth row:""")
    steps(
        r"\rho_{xy\cdot z} &= \frac{\rho_{xy}-\rho_{xz}\rho_{yz}}"
        r"{\sqrt{(1-\rho_{xz}^{2})(1-\rho_{yz}^{2})}}"
        r" = \frac{%s-(%s)(%s)}{\sqrt{(1-%s^{2})(1-%s^{2})}}"
        % (num(a, 4), num(b, 4), num(c, 4), num(b, 4), num(c, 4)),
        r"&= \frac{%s}{\sqrt{(%s)(%s)}} = \frac{%s}{%s} = %s"
        % (num(_pn, 6), num(1 - b * b, 6), num(1 - c * c, 6), num(_pn, 6),
           num(_pd, 6), num(vk, 6)),
    )
    vD, aD, bD, cD = _psp(PC, DD, LN)
    rDN = float(stats.spearmanr(DD, LN)[0])
    r2DN = float(np.corrcoef(DD, LN)[0, 1]) ** 2
    w(r"""Every association is larger with size held constant than without it,
which a size confound would not produce. $D$ nonetheless requires an explicit
qualification: it is rank-correlated with $\log N$ at $\rho = %s$, and""" %
      rho_(rDN))
    w(r"\begin{equation}")
    w(r"R^{2} = r^{2}_{D,\log N} = (%s)^{2} = %s"
      % (num(math.sqrt(r2DN), 4), num(r2DN, 4)))
    w(r"\end{equation}")
    w(r"""so roughly %s of what the estimator reports on these tracings is a
readout of traced area. Its association with the threshold survives the control
and strengthens, from %s raw to %s partialled, but the raw coefficient is not
read as a pure geometry effect anywhere in the Results.""" %
      ("%.0f\\%%" % (100 * r2DN), rho_(aD), rho_(vD)))
    w()

    # ---- regression -------------------------------------------------------
    w(r"\subsection{Multiple Regression on the Two Architectural Axes}")
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
    w(r"""Predictors $z$-scored, outcome in its own units, per
Equation~\eqref{eq:ols}:""")
    w(r"\begin{equation}\label{eq:empfit}")
    w(r"p_{c} = %s + %s\,z_{\langle k\rangle} + %s\,z_{D}"
      % (num(beta[0]), num(beta[1]), num(beta[2])))
    w(r"\end{equation}")
    steps(
        r"R^{2} &= 1-\frac{SS_{\text{res}}}{SS_{\text{tot}}}"
        r" = 1-\frac{%s}{%s} = 1-%s = %s"
        % (num(ss_res, 6), num(ss_tot, 6), num(ss_res / ss_tot, 6),
           num(r2, 4)),
        # The compound fraction is tall, so the substitution takes one line and
        # the arithmetic the next; on a single line the two stacked stages run
        # past the text block.
        r"F &= \frac{\dfrac{R^{2}}{k}}{\dfrac{1-R^{2}}{n-k-1}}"
        r" = \frac{\dfrac{%s}{2}}{\dfrac{1-%s}{%d}}"
        % (num(r2, 4), num(r2, 4), n - 3),
        r"&= \frac{%s}{%s} = %.2f"
        % (num(r2 / 2, 6), num((1 - r2) / (n - 3), 6), Fv),
        r"\beta_{\langle k\rangle} &= \frac{%s}{%s} = %s, \qquad"
        r"\beta_{D} = \frac{%s}{%s} = %s"
        % (num(beta[1]), num(sd_y, 4), num(bstd[0], 4),
           num(beta[2]), num(sd_y, 4), num(bstd[1], 4)),
    )
    w(r"""on $(2, %d)$ degrees of freedom. The intercept is the fitted threshold
at the cohort mean of both predictors and reproduces the cohort mean of
Table~\ref{tab:pcsummary}, as it must with both predictors centred. The
standardised coefficients put connectivity ahead of geometry by a factor of %s;
$1 - R^{2} = %s$ of the variance lies outside these two descriptors.
Collinearity is checked in Section~\ref{sec:collinearity}.""" %
      (n - 3, "%.2f" % (bstd[0] / bstd[1]), num(1 - r2, 4)))
    w()


def synthetic_grid(C):
    w, steps, num = C["w"], C["steps"], C["num"]
    rho_, check = C["rho"], C["check"]
    grid, T6, refit = C["grid"], C["T6"], C["rrl"]["synthetic_grid_refit"]

    K = np.array([float(r["mean_degree"]) for r in grid])
    D = np.array([float(r["D"]) for r in grid])
    n = len(grid)

    w(r"\section{The Synthetic Causal Grid}\label{sec:grid}")
    w()
    pr = float(np.corrcoef(K, D)[0, 1])
    sr = float(stats.spearmanr(K, D)[0])
    check("Grid Pearson k x D", T6["predictor_decoupling"]["pearson"], pr)
    check("Grid Spearman k x D", T6["predictor_decoupling"]["spearman"], sr)
    w(r"""In the empirical cohort the two architectural axes co-vary as the
leaves present them. The grid is %d generated networks in which mesh fraction
sets connectivity and generation depth sets space-filling, so the axes are
decoupled by construction: $r_{\langle k\rangle,D} = %s$ and
$\rho_{\langle k\rangle,D} = %s$.""" % (n, num(pr, 4), num(sr, 4)))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Threshold Regressed on Two Decoupled Architectural "
      r"Axes}}\label{tab:grid}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{llccccc}")
    w(r"\toprule")
    w(r"Removal mode & Predictor & $\rho$ & OLS $b$ & Standardised $\beta$ & "
      r"$R^{2}$ & $F$ \\")
    w(r"\midrule")
    fits = {}
    for mode, colname, jkey in [("Random, uniform", "pc_random", "random"),
                                ("Degree-weighted", "pc_degree",
                                 "degree_targeted")]:
        y = np.array([float(r[colname]) for r in grid])
        X = np.column_stack([np.ones(n), K, D])
        b = np.linalg.lstsq(X, y, rcond=None)[0]
        yh = X @ b
        r2 = 1 - float(((y - yh) ** 2).sum()) / float(((y - y.mean()) ** 2).sum())
        F = (r2 / 2) / ((1 - r2) / (n - 3))
        sy = y.std(ddof=1)
        bz = [b[1] * K.std(ddof=1) / sy, b[2] * D.std(ddof=1) / sy]
        rk = float(stats.spearmanr(y, K)[0])
        rd = float(stats.spearmanr(y, D)[0])
        fits[jkey] = dict(b=b, r2=r2, F=F, bz=bz, y=y)
        w(r"%s & Mean degree $\langle k\rangle$ & %s & %s & %s & %s & %.2f \\"
          % (mode, rho_(rk), num(b[1], 4), num(bz[0], 3), num(r2, 3), F))
        w(r" & Fractal dimension $D$ & %s & %s & %s & %s & %.2f \\"
          % (rho_(rd), num(b[2], 4), num(bz[1], 3), num(r2, 3), F))
        check("Grid rho k, %s" % jkey, T6[jkey]["spearman_mean_degree"]["rho"],
              rk)
        check("Grid rho D, %s" % jkey, T6[jkey]["spearman_D"]["rho"], rd)
        check("Grid OLS beta k, %s" % jkey,
              T6[jkey]["ols_raw"]["beta_mean_degree"], float(b[1]))
        check("Grid OLS beta D, %s" % jkey, T6[jkey]["ols_raw"]["beta_D"],
              float(b[2]))
        check("Grid R2, %s" % jkey, T6[jkey]["ols_raw"]["R2"], r2)
        check("Grid F, %s" % jkey, T6[jkey]["ols_raw"]["F"], F, 0.05)
        check("Grid std beta k, %s" % jkey,
              T6[jkey]["ols_fully_standardized"]["beta"][0], bz[0])
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    fr = fits["random"]
    w(r"""\noindent \textit{Note.} $n = %d$; $df = (2, %d)$. Raw coefficients are
per unit of the raw predictor and are \emph{not} comparable with one another,
because $\langle k\rangle$ spans %s units across the grid and $D$ spans %s; only
the standardised column supports a comparison. $R^{2}$ and $F$ are the
two-predictor model's and are identical for both rows of a mode. The uniform-mode
surface is""" % (n, n - 3, num(K.max() - K.min(), 2),
                 num(D.max() - D.min(), 2)))
    w(r"\begin{equation}\label{eq:gridfit}")
    w(r"p_{c} = %s + %s\,\langle k\rangle + %s\,D, \qquad R^{2} = %s"
      % (num(fr["b"][0], 4), num(fr["b"][1], 4), num(fr["b"][2], 4),
         num(fr["r2"], 3)))
    w(r"\end{equation}")
    w(r"""with a standardised dominance ratio of
$%s / %s = %s$ to one.""" %
      (num(fr["bz"][0], 4), num(fr["bz"][1], 4),
       "%.1f" % (fr["bz"][0] / fr["bz"][1])))
    w()

    # ---- restricted refit -------------------------------------------------
    emax = refit["empirical_max_mean_degree"]
    m = K <= emax
    nr = int(m.sum())
    y = fr["y"][m]
    Kr, Dr = K[m], D[m]
    zK = (Kr - Kr.mean()) / Kr.std(ddof=1)
    zD = (Dr - Dr.mean()) / Dr.std(ddof=1)
    zy = (y - y.mean()) / y.std(ddof=1)
    Zr = np.column_stack([np.ones(nr), zK, zD])
    bz = np.linalg.lstsq(Zr, zy, rcond=None)[0]
    yh = Zr @ bz
    r2r = 1 - float(((zy - yh) ** 2).sum()) / float(((zy - zy.mean()) ** 2).sum())
    Fr = (r2r / 2) / ((1 - r2r) / (nr - 3))
    check("Restricted grid beta k",
          refit["restricted_to_empirical_range"]["beta_mean_degree"],
          float(bz[1]))
    check("Restricted grid beta D",
          refit["restricted_to_empirical_range"]["beta_D"], float(bz[2]))
    check("Restricted grid R2", refit["restricted_to_empirical_range"]["R2"],
          r2r)
    check("Restricted grid F", refit["restricted_to_empirical_range"]["F"], Fr,
          0.05)
    w(r"""The grid's connectivity axis reaches $\langle k\rangle = %s$ against an
empirical maximum of %s, so %d of %d cells sit above the densest network measured
and Equation~\eqref{eq:gridfit} is in part an extrapolation. Refitting on the %d
cells inside the empirical range:""" %
      (num(K.max(), 2), num(emax, 4), int((~m).sum()), n, nr))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Full and Range-Restricted Fits on the Synthetic Grid}}"
      r"\label{tab:gridrefit}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    w(r"\begin{tabular}{lcccccc}")
    w(r"\toprule")
    w(r"Fit & $n$ & $\beta_{\langle k\rangle}$ & $\beta_{D}$ & Ratio & "
      r"$R^{2}$ & $F$ \\")
    w(r"\midrule")
    w(r"Full grid & %d & %s & %s & %s & %s & %.2f \\"
      % (n, num(fr["bz"][0], 3), num(fr["bz"][1], 3),
         "%.1f" % (fr["bz"][0] / fr["bz"][1]), num(fr["r2"], 3), fr["F"]))
    w(r"$\langle k\rangle \leq %s$ & %d & %s & %s & %s & %s & %.2f \\"
      % (num(emax, 2), nr, num(bz[1], 3), num(bz[2], 3),
         "%.1f" % (bz[1] / bz[2]), num(r2r, 3), Fr))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()

    def par(a, b_, c_):
        rab = float(np.corrcoef(a, b_)[0, 1])
        rac = float(np.corrcoef(a, c_)[0, 1])
        rbc = float(np.corrcoef(b_, c_)[0, 1])
        return (rab - rac * rbc) / math.sqrt((1 - rac ** 2) * (1 - rbc ** 2))

    pk, pd = par(y, Kr, Dr), par(y, Dr, Kr)
    pdf = par(fr["y"], D, K)
    gnd = refit["grid_spearman_N_x_D"]
    w(r"""\noindent \textit{Note.} Fully standardised, uniform removal.
Restricting to the range real leaves occupy makes the fit stronger ($R^{2}$ %s to
%s) and the dominance of connectivity smaller (%s to one, against %s), so the
extrapolation was inflating the contrast rather than creating it. Partial
product-moment correlations within the range are $r = %s$ for
$\langle k\rangle$ given $D$ and $r = %s$ for $D$ given $\langle k\rangle$, the
latter more than double its full-grid value of %s. One design limit is disclosed:
because the $D$ axis is realised by varying generation depth, $D$ and $N$ are
rank-correlated at %s \emph{within} the grid, so the grid decouples geometry from
connectivity but not from scale. The size-controlled empirical partials of
Table~\ref{tab:partial} are therefore the ones reported for the geometry
claim.""" %
      (num(fr["r2"], 3), num(r2r, 3), "%.1f" % (bz[1] / bz[2]),
       "%.1f" % (fr["bz"][0] / fr["bz"][1]), num(pk, 3), num(pd, 3),
       num(pdf, 3), rho_(gnd)))
    w()
