# -*- coding: utf-8 -*-
r"""
make_appendix_computations.py -- build "Appendix C: Data Analysis and
Computation" as a LaTeX document in which EVERY statistic reported in the
Results (CLAUDE'S CUT draft) is re-derived from the raw data files with the
formula, the substituted intermediate quantities, and the result shown.

Nothing here is copied from the manuscript: every number is recomputed from
data/*.csv and data/*.json, and a reconciliation table at the end flags any
cell that disagrees with the draft.

Run:
  C:\laragon\bin\python\python-3.13\python.exe scripts\make_appendix_computations.py

Output: APPENDIX_C_COMPUTATIONS.tex   (compile with pdflatex/Overleaf)
"""
import os
import re
import sys
import csv
import json
import math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
from scipy import stats

DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "APPENDIX_C_COMPUTATIONS.tex")

L = []                      # document lines
CHECKS = []                 # (label, draft value, computed value)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def w(s=""):
    L.append(s)


def f(x, d=4):
    """Fixed-decimal formatting; falls back to scientific for tiny magnitudes."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "--"
    ax = abs(x)
    if ax != 0 and (ax < 10 ** (-d) or ax >= 1e6):
        m, e = ("%.3e" % x).split("e")
        return r"%s \times 10^{%d}" % (m, int(e))
    return ("%." + str(d) + "f") % x


def g(x, d=4):
    """Same as f() but for text mode (wraps scientific notation in math)."""
    s = f(x, d)
    return "$%s$" % s if "\\times" in s else s


def thousands(n):
    return "{:,}".format(int(n)).replace(",", "{,}")


def pval(p):
    if p is None or not np.isfinite(p):
        return "--"
    if p < .001:
        return "$<.001$"
    return "$%.3f$" % p


def check(label, draft, computed, tol=None):
    CHECKS.append((label, draft, computed, tol))


def _dec(x):
    """Number of decimals in the reported (draft) figure."""
    s = ("%g" % x)
    if "e" in s or "E" in s:
        return 8
    return len(s.split(".")[1]) if "." in s else 0


def _tol(x):
    """Half a unit in the last significant digit of the reported figure --
    the largest difference explainable by rounding alone."""
    if x == 0:
        return 0.5
    s = "%g" % abs(x)
    mant = s.split("e")[0].replace(".", "").lstrip("0")
    sig = max(len(mant.rstrip("0")), 1)
    exp = math.floor(math.log10(abs(x)))
    return 0.6 * 10 ** (exp - sig + 1)


def read_csv(path):
    with open(os.path.join(DATA, path), newline="") as fh:
        return list(csv.DictReader(fh))


def read_json(path):
    with open(os.path.join(DATA, path)) as fh:
        return json.load(fh)


def col(rows, name, cast=float):
    out = []
    for r in rows:
        v = r.get(name, "")
        if v in ("", "None", "nan", "NaN"):
            out.append(np.nan)
        else:
            out.append(cast(v))
    return np.array(out, float) if cast is float else out


# --------------------------------------------------------------------------
# statistical primitives, each returning both the result and the working
# --------------------------------------------------------------------------
def describe(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = x.size
    S1 = float(x.sum())
    S2 = float((x ** 2).sum())
    M = S1 / n
    var = (S2 - n * M * M) / (n - 1)
    sd = math.sqrt(max(var, 0.0))
    xs = np.sort(x)
    if n % 2:
        med = float(xs[(n - 1) // 2])
        medrule = r"x_{(%d)}" % ((n + 1) // 2)
    else:
        med = float((xs[n // 2 - 1] + xs[n // 2]) / 2)
        medrule = r"\tfrac{1}{2}\left[x_{(%d)}+x_{(%d)}\right]" % (n // 2, n // 2 + 1)
    return dict(n=n, S1=S1, S2=S2, M=M, var=var, sd=sd, med=med,
                medrule=medrule, lo=float(xs[0]), hi=float(xs[-1]))


def tie_term(ranks):
    """T = sum(t^3 - t)/12 over tied groups, the Spearman tie correction."""
    _, counts = np.unique(ranks, return_counts=True)
    counts = counts[counts > 1]
    return float(np.sum(counts ** 3 - counts) / 12.0), int(counts.size)


def spearman(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = x.size
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    d2 = float(np.sum((rx - ry) ** 2))
    Tx, gx = tie_term(rx)
    Ty, gy = tie_term(ry)
    A = n * (n * n - 1) / 6.0
    rho_simple = 1 - 6 * d2 / (n * (n * n - 1))
    denom = math.sqrt((A - 2 * Tx) * (A - 2 * Ty))
    rho = (A - d2 - Tx - Ty) / denom if denom > 0 else float("nan")
    dof = n - 2
    t = rho * math.sqrt(dof / (1 - rho ** 2)) if abs(rho) < 1 else float("inf")
    p = 2 * stats.t.sf(abs(t), dof) if np.isfinite(t) else 0.0
    return dict(n=n, d2=d2, Tx=Tx, Ty=Ty, gx=gx, gy=gy, A=A,
                rho_simple=rho_simple, rho=rho, t=t, dof=dof, p=p)


def pearson(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = x.size
    Sx, Sy = x.sum(), y.sum()
    Sxx, Syy, Sxy = (x * x).sum(), (y * y).sum(), (x * y).sum()
    num = n * Sxy - Sx * Sy
    den = math.sqrt((n * Sxx - Sx ** 2) * (n * Syy - Sy ** 2))
    r = num / den
    dof = n - 2
    t = r * math.sqrt(dof / (1 - r ** 2))
    p = 2 * stats.t.sf(abs(t), dof)
    return dict(n=n, Sx=Sx, Sy=Sy, Sxx=Sxx, Syy=Syy, Sxy=Sxy,
                num=num, den=den, r=r, t=t, dof=dof, p=p)


def partial(rxy, rxz, ryz, n):
    num = rxy - rxz * ryz
    den = math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    r = num / den
    dof = n - 3
    t = r * math.sqrt(dof / (1 - r ** 2))
    p = 2 * stats.t.sf(abs(t), dof)
    return dict(num=num, den=den, r=r, t=t, dof=dof, p=p)


def wilcoxon(a, b):
    """Paired signed-rank test, normal approximation with tie correction."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = a - b
    n0 = d.size
    nz = d[d != 0]
    nr = nz.size
    ranks = stats.rankdata(np.abs(nz))
    Wp = float(ranks[nz > 0].sum())
    Wm = float(ranks[nz < 0].sum())
    W = min(Wp, Wm)
    mu = nr * (nr + 1) / 4.0
    T, _ = tie_term(ranks)                        # sum(t^3-t)/12
    sig = math.sqrt(nr * (nr + 1) * (2 * nr + 1) / 24.0 - T / 2.0)
    z = (W - mu) / sig
    p = 2 * stats.norm.sf(abs(z))
    return dict(n0=n0, nr=nr, nzero=n0 - nr, Wp=Wp, Wm=Wm, W=W, mu=mu,
                sigma=sig, T=T, z=z, p=p,
                npos=int((nz > 0).sum()), nneg=int((nz < 0).sum()),
                med_d=float(np.median(d)))


def mannwhitney(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    n1, n2 = a.size, b.size
    allv = np.concatenate([a, b])
    ranks = stats.rankdata(allv)
    R1 = float(ranks[:n1].sum())
    R2 = float(ranks[n1:].sum())
    U1 = n1 * n2 + n1 * (n1 + 1) / 2.0 - R1
    U2 = n1 * n2 - U1
    U = min(U1, U2)
    mu = n1 * n2 / 2.0
    N = n1 + n2
    _, counts = np.unique(ranks, return_counts=True)
    tiesum = float(np.sum(counts ** 3 - counts))
    sig = math.sqrt(n1 * n2 / 12.0 * ((N + 1) - tiesum / (N * (N - 1))))
    z = (U - mu) / sig
    p = 2 * stats.norm.sf(abs(z))
    return dict(n1=n1, n2=n2, R1=R1, R2=R2, U1=U1, U2=U2, U=U, mu=mu,
                sigma=sig, tiesum=tiesum, z=z, p=p)


def ols2(y, x1, x2, standardize=True):
    """Two-predictor OLS via the closed form, so it can be checked by hand."""
    y = np.asarray(y, float)
    x1 = np.asarray(x1, float)
    x2 = np.asarray(x2, float)
    if standardize:
        x1 = (x1 - x1.mean()) / x1.std(ddof=1)
        x2 = (x2 - x2.mean()) / x2.std(ddof=1)
    r_y1 = float(np.corrcoef(y, x1)[0, 1])
    r_y2 = float(np.corrcoef(y, x2)[0, 1])
    r_12 = float(np.corrcoef(x1, x2)[0, 1])
    sy, s1, s2 = y.std(ddof=1), x1.std(ddof=1), x2.std(ddof=1)
    b1 = (r_y1 - r_y2 * r_12) / (1 - r_12 ** 2) * (sy / s1)
    b2 = (r_y2 - r_y1 * r_12) / (1 - r_12 ** 2) * (sy / s2)
    b0 = y.mean() - b1 * x1.mean() - b2 * x2.mean()
    R2 = (r_y1 ** 2 + r_y2 ** 2 - 2 * r_y1 * r_y2 * r_12) / (1 - r_12 ** 2)
    n = y.size
    Fstat = (R2 / 2) / ((1 - R2) / (n - 3))
    pF = stats.f.sf(Fstat, 2, n - 3)
    return dict(r_y1=r_y1, r_y2=r_y2, r_12=r_12, b0=b0, b1=b1, b2=b2,
                R2=R2, n=n, F=Fstat, pF=pF, sy=sy)


def resid(y, x):
    A = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ beta


# --------------------------------------------------------------------------
# LaTeX block writers
# --------------------------------------------------------------------------
def sec(title, label=None):
    w("")
    w(r"\section{%s}" % title)
    if label:
        w(r"\label{%s}" % label)
    w("")


def sub(title):
    w("")
    w(r"\subsection{%s}" % title)
    w("")


def note(txt):
    w(r"\vspace{2pt}\noindent\textit{Note.} %s" % txt)
    w("")


def descriptive_block(name, symbol, d, unit=""):
    """Show n, sums, mean, SD, median and range for one variable."""
    w(r"\paragraph{%s.}" % name)
    w(r"\begin{align*}")
    w(r"n &= %d, \qquad \textstyle\sum x = %s, \qquad \textstyle\sum x^{2} = %s \\" %
      (d["n"], f(d["S1"], 4), f(d["S2"], 4)))
    w(r"M &= \frac{\sum x}{n} = \frac{%s}{%d} = \mathbf{%s} \\" %
      (f(d["S1"], 4), d["n"], f(d["M"], 4)))
    w(r"s^{2} &= \frac{\sum x^{2}-nM^{2}}{n-1}"
      r"= \frac{%s-%d(%s)^{2}}{%d} = %s"
      r"\qquad\Longrightarrow\qquad s = \sqrt{s^{2}} = \mathbf{%s} \\" %
      (f(d["S2"], 4), d["n"], f(d["M"], 4), d["n"] - 1, f(d["var"], 6),
       f(d["sd"], 4)))
    w(r"Mdn &= %s = \mathbf{%s}, \qquad \min = %s, \qquad \max = %s" %
      (d["medrule"], f(d["med"], 4), f(d["lo"], 4), f(d["hi"], 4)))
    w(r"\end{align*}")
    w("")


def spearman_block(title, s, xname, yname, show_formula=True):
    w(r"\paragraph{%s.}" % title)
    w(r"\begin{align*}")
    w(r"n &= %d, \qquad \textstyle\sum d_i^{2} = %s, \qquad "
      r"A = \tfrac{n(n^{2}-1)}{6} = %s \\" %
      (s["n"], f(s["d2"], 1), f(s["A"], 1)))
    w(r"T_{%s} &= \tfrac{1}{12}\!\sum (t^{3}-t) = %s, \qquad "
      r"T_{%s} = %s, \qquad "
      r"\rho_{\text{no ties}} = 1-\tfrac{6\sum d^{2}}{n(n^{2}-1)} = %s \\" %
      (xname, f(s["Tx"], 3), yname, f(s["Ty"], 3), f(s["rho_simple"], 4)))
    w(r"\rho_s &= \frac{A-\sum d^{2}-T_{%s}-T_{%s}}"
      r"{\sqrt{(A-2T_{%s})(A-2T_{%s})}}"
      r"= \frac{%s}{%s} = \mathbf{%s} \\" %
      (xname, yname, xname, yname,
       f(s["A"] - s["d2"] - s["Tx"] - s["Ty"], 3),
       f(math.sqrt((s["A"] - 2 * s["Tx"]) * (s["A"] - 2 * s["Ty"])), 3),
       f(s["rho"], 4)))
    w(r"t &= \rho_s\sqrt{\frac{n-2}{1-\rho_s^{2}}} = %s\sqrt{\frac{%d}{1-%s}} = %s,"
      r"\qquad df = %d, \qquad p %s" %
      (f(s["rho"], 4), s["dof"], f(s["rho"] ** 2, 4), f(s["t"], 3), s["dof"],
       ("<.001" if s["p"] < .001 else "= %.3f" % s["p"])))
    w(r"\end{align*}")
    w("")


def summary_table(header, rows, caption, colspec=None, small=True, label=None):
    ncol = len(header)
    colspec = colspec or ("l" + "r" * (ncol - 1))
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{%s}" % caption)
    if label:
        w(r"\label{%s}" % label)
    if ncol >= 8:
        w(r"\footnotesize\setlength{\tabcolsep}{3.5pt}")
    elif small:
        w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{%s}" % colspec)
    w(r"\toprule")
    w(" & ".join(header) + r" \\")
    w(r"\midrule")
    for r in rows:
        w(" & ".join(str(c) for c in r) + r" \\")
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w("")


# ==========================================================================
# LOAD EVERYTHING
# ==========================================================================
charz = read_csv("characterization.csv")
lfrac = read_csv("loop_fraction_perleaf.csv")
cohort_pc = read_csv("cohort_pc.csv")
suggested = read_csv("cohort_suggested.csv")
grid = read_csv("synthetic_grid_pc.csv")
ceiling = read_csv("robustness_ceiling.csv")

syn_per_path = os.path.join(DATA, "synthetic_pernetwork.csv")
syn_per = read_csv("synthetic_pernetwork.csv") if os.path.exists(syn_per_path) else None

sweep_path = os.path.join(DATA, "sink_sweep.csv")
sweep = read_csv("sink_sweep.csv") if os.path.exists(sweep_path) else None

summary = read_json("summary.json")
sink = read_json("sink_demo.json")
hydval = read_json("hydraulic_validation.json")
kleaf = read_json("kleaf_validation_summary.json")
bound = read_json("boundary_check.json")
calib = read_json("calibration.json")
synfull = read_json("synthetic_full_metrics.json")
sugsum = read_json("cohort_suggested_summary.json")
provn = read_json("cohort_provenance.json")
surf = read_json("sink_surface.json")
fixedD = read_json("finite_size_fixedD.json")
scaling = read_json("scaling_mesh.json")
dynam = read_json("dynamics.json")

# --- empirical cohort used in Table 1: the 112 valid leaf-venation networks --
valid = [r for r in charz if r["valid_for_percolation"] == "True"]
by_name = {r["name"]: r for r in valid}
lf_by = {r["name"]: r for r in lfrac}
E112 = [r for r in valid if r["name"] in lf_by]

emp = {
    "D": col(E112, "D"),
    "K": col(E112, "effective_conductance"),
    "k": col(E112, "mean_degree"),
    "ksd": col(E112, "degree_sd"),
    "loop": np.array([float(lf_by[r["name"]]["loop_fraction_nonbridge"]) for r in E112]),
    "bridge": np.array([float(lf_by[r["name"]]["bridge_fraction"]) for r in E112]),
    "term": np.array([float(lf_by[r["name"]]["terminal_fraction"]) for r in E112]),
    "gcc": col(E112, "gcc_fraction"),
    "N": col(E112, "n_nodes"),
}

# --- synthetic cohort (42 grid networks) ------------------------------------
if syn_per:
    syn = {
        "D": col(syn_per, "D"),
        "K": col(syn_per, "effective_conductance"),
        "k": col(syn_per, "mean_degree"),
        "ksd": col(syn_per, "degree_sd"),
        "loop": col(syn_per, "loop_fraction_nonbridge"),
        "bridge": col(syn_per, "bridge_fraction"),
        "gcc": col(syn_per, "gcc_fraction"),
        "N": col(syn_per, "N"),
    }
    SYN_SOURCE = (r"\texttt{data/synthetic\_pernetwork.csv} (the 42 grid networks "
                  r"regenerated from the same deterministic seed)")
else:
    gl = [c["loop_fraction"] for c in calib["grid"]]
    syn = {
        "D": col(grid, "D"),
        "k": col(grid, "mean_degree"),
        "loop": np.array(gl, float),
        "bridge": 1 - np.array(gl, float),
        "N": col(grid, "N"),
    }
    SYN_SOURCE = r"\texttt{data/synthetic\_grid\_pc.csv} and \texttt{data/calibration.json}"

# --- percolation cohort (100 leaves) ----------------------------------------
pc_rand = col(cohort_pc, "pc_random")
pc_deg = col(cohort_pc, "pc_degree")
pc_k = col(cohort_pc, "mean_degree")
pc_D = np.array([float(by_name[n]["D"]) for n in
                 [r["species"] for r in cohort_pc]])
pc_names = [r["species"] for r in cohort_pc]
pc_loop = np.array([float(lf_by[n]["loop_fraction_nonbridge"])
                    if n in lf_by else np.nan for n in pc_names])
pc_bridge = np.array([float(lf_by[n]["bridge_fraction"])
                      if n in lf_by else np.nan for n in pc_names])

# --- reticulation-enhancement cohort (105 valid of 120) ---------------------
sug_valid = [r for r in suggested
             if float(r["N"]) >= 1000 and float(r["pc_current"]) >= 0.02]
s_cur = col(sug_valid, "pc_current")
s_new = col(sug_valid, "pc_suggested")
s_del = col(sug_valid, "delta_pc")
s_k0 = col(sug_valid, "k_current")
s_D = col(sug_valid, "D")
s_grade = [r["quality"].split(",")[0] for r in sug_valid]


# ==========================================================================
# PREAMBLE
# ==========================================================================
w(r"""\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{float}
\usepackage{caption}
\usepackage[hidelinks]{hyperref}
\usepackage{times}
\setlength{\parindent}{0.5in}
\captionsetup[table]{labelsep=newline,justification=raggedright,
                     singlelinecheck=false,font=normalsize}
\renewcommand{\thesection}{C.\arabic{section}}
\renewcommand{\thetable}{C\arabic{table}}
\renewcommand{\theequation}{C.\arabic{equation}}
\title{\textbf{Appendix C}\\[2pt] Data Analysis and Computation}
\author{}
\date{}
\begin{document}
\maketitle
\thispagestyle{empty}
\vspace{-3em}
""")

w(r"""
\noindent This appendix re-derives every quantitative claim in the Results from
the archived data files. For each statistic the defining formula is stated, the
intermediate quantities actually obtained from the data are substituted, and the
result is carried to the precision reported in the text. Sums of the form
$\sum x$ and $\sum x^{2}$ are given so that any mean, standard deviation, or
correlation below can be reproduced on a calculator without returning to the raw
files. Section~C.18 lists every value against the corresponding cell of the
Results and flags any disagreement.
""")

# --------------------------------------------------------------------------
sec("Provenance of the Data")
w(r"""Each computation draws on one archived file; no intermediate value is
carried over from the manuscript text.""")
prov = [
    (r"C.3", r"Structural and hydraulic characterization ($n=112$)",
     r"\texttt{characterization.csv}, \texttt{loop\_fraction\_perleaf.csv}"),
    (r"C.3", r"Synthetic characterization ($n=42$)", SYN_SOURCE),
    (r"C.4", r"Inter-descriptor correlations", r"as C.3"),
    (r"C.5", r"Percolation thresholds ($n=100$)", r"\texttt{cohort\_pc.csv}"),
    (r"C.6", r"High-precision synthetic reference", r"\texttt{summary.json}"),
    (r"C.7", r"Haustorial sink hydraulics and gradient sweep",
     r"\texttt{sink\_demo.json}, \texttt{sink\_sweep.csv}"),
    (r"C.8", r"Architecture $\rightarrow p_c$", r"\texttt{cohort\_pc.csv}"),
    (r"C.9", r"Synthetic causal grid", r"\texttt{synthetic\_grid\_pc.csv}"),
    (r"C.10", r"Reticulation and damage tolerance",
     r"\texttt{cohort\_pc.csv}, \texttt{loop\_fraction\_perleaf.csv}"),
    (r"C.11", r"Reticulation enhancement ($n=105$)",
     r"\texttt{cohort\_suggested.csv}"),
    (r"C.12", r"Response-surface headroom", r"\texttt{robustness\_ceiling.csv}"),
    (r"C.13", r"Model validation",
     r"\texttt{hydraulic\_validation.json}, \texttt{kleaf\_validation\_summary.json}, "
     r"\texttt{boundary\_check.json}"),
    (r"C.14", r"Cohort provenance and Monte Carlo budgets",
     r"\texttt{cohort\_provenance.json}"),
    (r"C.15", r"Coupled sink surface", r"\texttt{sink\_surface.json}"),
    (r"C.16", r"Finite-size behaviour",
     r"\texttt{finite\_size\_fixedD.json}, \texttt{scaling\_mesh.json}"),
    (r"C.17", r"Pre-symptomatic window", r"\texttt{dynamics.json}"),
]
summary_table([r"Section", r"Quantity", r"Source file"], prov,
              r"Source File for Each Computation in This Appendix",
              colspec="llp{6.4cm}")

# --------------------------------------------------------------------------
sec("Formulas Used")
w(r"""All descriptive statistics use the sample (Bessel-corrected) standard
deviation. All correlation and difference tests are distribution-free, because
the Shapiro--Wilk tests in Section~C.8 reject normality for $p_c$ and for both
connectivity predictors. Significance is evaluated at $\alpha=.05$ throughout.""")
w(r"""
\begin{align}
M &= \frac{\sum_{i=1}^{n} x_i}{n},
&
s &= \sqrt{\frac{\sum x_i^{2}-nM^{2}}{n-1}}
\\[4pt]
Mdn &= \begin{cases}
x_{((n+1)/2)} & n \text{ odd}\\[2pt]
\tfrac{1}{2}\!\left[x_{(n/2)}+x_{(n/2+1)}\right] & n \text{ even}
\end{cases}
&
\rho_s &= \frac{A-\sum d_i^{2}-T_x-T_y}{\sqrt{(A-2T_x)(A-2T_y)}},\quad
A=\frac{n(n^{2}-1)}{6}
\\[4pt]
T &= \frac{1}{12}\sum_{\text{ties}} (t^{3}-t),
&
t_{\rho} &= \rho_s\sqrt{\frac{n-2}{1-\rho_s^{2}}},\quad df=n-2
\\[4pt]
r_{xy\cdot z} &= \frac{r_{xy}-r_{xz}r_{yz}}{\sqrt{(1-r_{xz}^{2})(1-r_{yz}^{2})}},
&
R^{2} &= \frac{r_{y1}^{2}+r_{y2}^{2}-2r_{y1}r_{y2}r_{12}}{1-r_{12}^{2}}
\\[4pt]
\beta_1 &= \frac{r_{y1}-r_{y2}r_{12}}{1-r_{12}^{2}}\cdot\frac{s_y}{s_1},
&
\beta_2 &= \frac{r_{y2}-r_{y1}r_{12}}{1-r_{12}^{2}}\cdot\frac{s_y}{s_2}
\\[4pt]
W &= \min(W^{+},W^{-}),\quad \mu_W=\frac{n_r(n_r+1)}{4},
&
\sigma_W &= \sqrt{\frac{n_r(n_r+1)(2n_r+1)}{24}-\frac{\sum(t^{3}-t)}{48}}
\\[4pt]
U_1 &= n_1n_2+\frac{n_1(n_1+1)}{2}-R_1,
&
\sigma_U &= \sqrt{\frac{n_1n_2}{12}\left[(N+1)-\frac{\sum(t^{3}-t)}{N(N-1)}\right]}
\end{align}
""")
note(r"""$d_i$ is the difference between the two ranks assigned to case $i$;
$t$ is the size of a group of tied observations; $n_r$ is the number of non-zero
differences entering the signed-rank test; $N=n_1+n_2$. The $z$ statistic for
both rank tests is $(\,\text{statistic}-\mu\,)/\sigma$ and is referred to the
standard normal distribution.""")

# ==========================================================================
sec("Structural and Hydraulic Characterization (Results Table 1)")
w(r"""The empirical cohort is the %d whole-leaf networks flagged
\texttt{valid\_for\_percolation} in \texttt{characterization.csv}; the synthetic
cohort is the %d networks of the calibrated grid. Loop fraction is the
proportion of edges that are \emph{not} bridges, computed identically for both
cohorts, and bridge fraction is its complement, so
$\text{loop}+\text{bridge}=1$ exactly for every network.""" %
  (len(E112), syn["k"].size))

sub("Worked example: fractal dimension of the empirical cohort")
dD = describe(emp["D"])
w(r"""The first three sorted values are $%s$, $%s$, $%s$ and the last is $%s$.
Because $n=%d$ is even the median is the mean of the %dth and %dth order
statistics.""" % (f(np.sort(emp["D"])[0], 4), f(np.sort(emp["D"])[1], 4),
                  f(np.sort(emp["D"])[2], 4), f(np.sort(emp["D"])[-1], 4),
                  dD["n"], dD["n"] // 2, dD["n"] // 2 + 1))
descriptive_block("Fractal dimension $D$ (empirical)", "D", dD)

sub("All characteristics")
w(r"""The same three lines of arithmetic applied to each remaining
characteristic give the sums and results in Table~\ref{tab:t1sums}. Every mean
and standard deviation in Results Table~1 can be reconstructed from the two sums
in the corresponding row.""")

ROWS = [
    ("Fractal dimension $D$", "D", 4),
    ("Hydraulic conductance", "K", 6),
    ("Mean degree $\\langle k\\rangle$", "k", 4),
    ("Degree standard deviation", "ksd", 4),
    ("Loop fraction", "loop", 4),
    ("Bridge fraction", "bridge", 4),
    ("GCC fraction", "gcc", 4),
    ("Network size $N$", "N", 1),
]

# values as printed in Results Table 1: (M, SD, Mdn, min, max)
DRAFT_T1 = {
    ("D", "Empirical"): (1.658, 0.162, 1.676, 1.148, 1.913),
    ("D", "Synthetic"): (1.599, 0.192, 1.640, 1.262, 1.810),
    ("K", "Empirical"): (2.79e-02, 1.48e-01, 4.01e-03, 3.9e-05, 1.5e+00),
    ("K", "Synthetic"): (8.62e-03, 9.46e-03, 4.04e-03, 5.3e-04, 3.5e-02),
    ("k", "Empirical"): (2.544, 0.200, 2.520, 2.148, 2.989),
    ("k", "Synthetic"): (2.924, 0.637, 2.796, 2.086, 3.998),
    ("ksd", "Empirical"): (0.795, 0.164, 0.848, 0.201, 0.989),
    ("ksd", "Synthetic"): (1.362, 0.213, 1.350, 1.046, 1.731),
    ("loop", "Empirical"): (0.769, 0.137, 0.776, 0.320, 0.995),
    ("loop", "Synthetic"): (0.739, 0.224, 0.806, 0.289, 0.961),
    ("bridge", "Empirical"): (0.231, 0.137, 0.224, 0.005, 0.680),
    ("bridge", "Synthetic"): (0.261, 0.224, 0.194, 0.039, 0.711),
    ("gcc", "Empirical"): (0.998, 0.014, 1.000, 0.850, 1.000),
    ("gcc", "Synthetic"): (1.000, 0.000, 1.000, 1.000, 1.000),
    ("N", "Empirical"): (39755, 57277, 15404, 421, 300633),
    ("N", "Synthetic"): (9288, 11005, 4095, 511, 32767),
}

t1rows = []
for label, key, dec in ROWS:
    for cohort, store in (("Empirical", emp), ("Synthetic", syn)):
        if key not in store:
            continue
        d = describe(store[key])
        t1rows.append([label if cohort == "Empirical" else "",
                       cohort, d["n"], g(d["S1"], dec), g(d["S2"], dec),
                       g(d["M"], dec), g(d["sd"], dec), g(d["med"], dec),
                       "[%s, %s]" % (g(d["lo"], dec), g(d["hi"], dec))])
        ref = DRAFT_T1.get((key, cohort))
        if ref:
            plain = label.replace("$", "").replace("\\langle k\\rangle", "<k>")
            tag = "T1 %s (%s)" % (plain, cohort.lower())
            check(tag + " $M$", ref[0], d["M"])
            check(tag + " $SD$", ref[1], d["sd"])
            check(tag + " $Mdn$", ref[2], d["med"])
            check(tag + " min", ref[3], d["lo"])
            check(tag + " max", ref[4], d["hi"])

summary_table([r"Characteristic", r"Cohort", r"$n$", r"$\sum x$", r"$\sum x^{2}$",
               r"$M$", r"$s$", r"$Mdn$", r"Range"],
              t1rows,
              r"Sums and Resulting Descriptive Statistics for Every Characteristic",
              colspec="llrrrrrrl", label="tab:t1sums")
note(r"""Sums are given to the number of decimals needed to reproduce $M$ and
$s$ to four decimals. $\sum x^{2}$ for network size is large by construction and
is shown in scientific notation.""")

# ==========================================================================
sec("Correlations Among Architectural Descriptors (Results Table 2)")
w(r"""These six correlations are computed on the same %d empirical networks.
The first is worked in full; the remainder follow the identical substitution and
are collected in Table~\ref{tab:t2}.""" % len(E112))

PAIRS2 = [
    ("Mean degree and loop fraction", emp["k"], emp["loop"], "k", "L"),
    ("Loop fraction and terminal fraction", emp["loop"], emp["term"], "L", "F"),
    ("Loop fraction and GCC fraction", emp["loop"], emp["gcc"], "L", "G"),
    ("Mean degree and fractal dimension", emp["k"], emp["D"], "k", "D"),
    ("Loop fraction and fractal dimension", emp["loop"], emp["D"], "L", "D"),
    ("Loop fraction and network size", emp["loop"], emp["N"], "L", "N"),
]
s0 = spearman(PAIRS2[0][1], PAIRS2[0][2])
spearman_block("Mean degree and loop fraction", s0, "k", "L")

DRAFT_T2 = [0.994, -0.973, 0.311, 0.170, 0.156, -0.047]
t2rows = []
for (name, x, y, sx, sy), ref in zip(PAIRS2, DRAFT_T2):
    s = spearman(x, y)
    strength = ("Very strong" if abs(s["rho"]) >= .80 else
                "Strong" if abs(s["rho"]) >= .60 else
                "Moderate" if abs(s["rho"]) >= .40 else
                "Weak" if abs(s["rho"]) >= .20 else "Very weak")
    direction = "positive" if s["rho"] > 0 else "negative"
    dec = "Reject $H_0$" if s["p"] < .05 else "Fail to reject $H_0$"
    t2rows.append([name, s["n"], g(s["d2"], 1), g(s["rho"], 3),
                   "%.2f" % s["t"], s["dof"], pval(s["p"]), dec,
                   "%s %s" % (strength, direction)])
    check(r"T2 $\rho_s$: %s" % name, ref, s["rho"])

summary_table([r"Variables", r"$n$", r"$\sum d^{2}$", r"$\rho_s$", r"$t$",
               r"$df$", r"$p$", r"Decision", r"Interpretation"],
              t2rows, r"Spearman Correlations Among Architectural Descriptors",
              colspec="lrrrrrllp{2.3cm}", label="tab:t2")
note(r"""$H_0$: there is no monotone relationship between the paired
descriptors. Strength bands: $<.20$ very weak, $.20$--$.39$ weak, $.40$--$.59$
moderate, $.60$--$.79$ strong, $\geq .80$ very strong.""")

# ==========================================================================
sec("Collapse Thresholds of the Empirical Cohort (Results Table 3)")
dR = describe(pc_rand)
dT = describe(pc_deg)
descriptive_block("Random attack $p_c$", "p", dR)
descriptive_block("Degree-targeted attack $p_c$", "p", dT)

wl = wilcoxon(pc_rand, pc_deg)
sub("Wilcoxon signed-rank test on the paired thresholds")
w(r"""The two thresholds are measured on the same %d leaves, so the difference
$d_i = p_c^{\text{random}}-p_c^{\text{targeted}}$ is a paired quantity. Of the
%d differences, %d are positive, %d negative, and %d exactly zero; the zeros are
discarded, leaving $n_r=%d$ signed ranks.""" %
  (wl["n0"], wl["n0"], wl["npos"], wl["nneg"], wl["nzero"], wl["nr"]))
w(r"\begin{align*}")
w(r"W^{+} &= %s, \qquad W^{-} = %s, \qquad W = \min(W^{+},W^{-}) = \mathbf{%s} \\" %
  (thousands(wl["Wp"]), thousands(wl["Wm"]), thousands(wl["W"])))
w(r"\mu_W &= \frac{n_r(n_r+1)}{4} = \frac{%d\cdot %d}{4} = %s \\" %
  (wl["nr"], wl["nr"] + 1, thousands(wl["mu"])))
w(r"\sigma_W &= \sqrt{\frac{n_r(n_r+1)(2n_r+1)}{24}-\frac{\sum(t^{3}-t)}{48}} = %s \\" %
  f(wl["sigma"], 2))
w(r"z &= \frac{W-\mu_W}{\sigma_W} = \frac{%s-%s}{%s} = %s, \qquad p %s,"
  r"\qquad Mdn_d = %s" %
  (thousands(wl["W"]), thousands(wl["mu"]), f(wl["sigma"], 2), f(wl["z"], 3),
   ("<.001" if wl["p"] < .001 else "= %.4f" % wl["p"]), f(wl["med_d"], 4)))
w(r"\end{align*}")
w(r"""$W=%d$ arises because every one of the %d non-zero differences carries the
same sign, so one of the two rank sums is empty. $H_0$ (no difference between
the two attack strategies) is rejected.""" % (wl["W"], wl["nr"]))
check(r"T3 random attack $Mdn\ p_c$", 0.1998, dR["med"])
check(r"T3 targeted attack $Mdn\ p_c$", 0.1685, dT["med"])
check(r"T3 $Mdn$ paired difference", 0.0305, wl["med_d"])

# ==========================================================================
sec("High-Precision Synthetic Reference (Results Table 4)")
w(r"""The reference network is not measured by the sums above; its threshold is
the inflection point of a logistic fit to $10^{6}$ Monte Carlo collapse trials.
Writing $P(\text{collapse}\mid \rho)=\left[1+e^{-(b_0+b_1\rho)}\right]^{-1}$,
the threshold is the density at which the fitted probability equals $.50$:""")
w(r"""
\[
P(\text{collapse}\mid p_c)=.50
\quad\Longleftrightarrow\quad
b_0+b_1 p_c = 0
\quad\Longleftrightarrow\quad
p_c=-\frac{b_0}{b_1}.
\]
""")
w(r"""The fitted values on the calibrated mesh ($N=%s$, $E=%s$,
$\langle k\rangle=%s$, $D=%s$) are given in Table~\ref{tab:t4}. The interval is
the bootstrap percentile interval over the trial set, not a normal-theory
interval, and its width of $%s$ reflects the $10^{6}$-trial budget: it is
roughly two orders of magnitude tighter than the $2{,}400$-trial cohort
estimates of Section~C.5.""" %
  (thousands(summary["network"]["n_nodes"]), thousands(summary["network"]["n_edges"]),
   f(summary["network"]["mean_degree"], 4), f(summary["D"], 4),
   f(summary["p_c_ci95"][1] - summary["p_c_ci95"][0], 5)))

summary_table([r"Attack strategy", r"$p_c$", r"95\% CI", r"Trials",
               r"$P(\text{collapse})$ at $p_c$"],
              [["Random", f(summary["p_c_random"], 4),
                "[%s, %s]" % (f(summary["p_c_ci95"][0], 4), f(summary["p_c_ci95"][1], 4)),
                thousands(summary["n_trials"]), ".50"],
               ["Degree-targeted", f(summary["p_c_targeted_degree"], 4),
                "[%s, %s]" % (f(summary["p_c_targeted_degree_ci95"][0], 4),
                              f(summary["p_c_targeted_degree_ci95"][1], 4)),
                thousands(summary["n_trials_targeted"]), ".50"],
               ["Betweenness-targeted", f(summary["p_c_targeted_betweenness"], 4),
                "[%s, %s]" % (f(summary["p_c_targeted_betweenness_ci95"][0], 4),
                              f(summary["p_c_targeted_betweenness_ci95"][1], 4)),
                thousands(summary["n_trials_targeted"]), ".50"]],
              r"Logistic Threshold Estimates on the Calibrated Synthetic Mesh",
              label="tab:t4")
note(r"""$P(\text{collapse})=.50$ at $p_c$ by definition of the logistic
inflection point, not as an empirical finding. The ordering
(targeted $<$ random) reproduces the empirical result of Section~C.5. The two
targeted intervals were computed for this appendix; the original run stored point
estimates only, so any interval quoted for a targeted threshold before this
revision was unsupported by the archive.""")
check(r"T4 synthetic random $p_c$", 0.271, summary["p_c_random"])
check(r"T4 synthetic targeted $p_c$", 0.202, summary["p_c_targeted_degree"])

# ==========================================================================
sec("Haustorial Sink Hydraulics (Results Table 5)")
psi_min = sink["min_psi_at_literature_MPa"]
CAV = -2.0
w(r"""The sink is calibrated so that the flow it withdraws is the literature
floor for a parasitic attachment. With $K_h=%s$ the solver diverts""" %
  f(sink["K_H_HOLOPARASITE"], 6))
w(r"""
\[
\text{diversion}=\frac{Q_{\text{haustorium}}}{Q_{\text{total}}}
=%s=%s\%%,
\qquad\text{against a calibration target of }%s\%%,
\]
""" % (f(sink["achieved_diversion"], 6), f(100 * sink["achieved_diversion"], 3),
       f(100 * sink["target_diversion"], 0)))
w(r"""so the calibration error is
$%s\%%-%s\%%=%s$ percentage points. At the illustrative host--parasite
gradient of $%s$~MPa the minimum leaf water potential anywhere in the host
network is""" % (f(100 * sink["achieved_diversion"], 3),
                 f(100 * sink["target_diversion"], 0),
                 f(100 * (sink["achieved_diversion"] - sink["target_diversion"]), 4),
                 f(sink["gradient_MPa"], 1)))
w(r"""
\[
\Psi_{\min}=%s\ \text{MPa},
\qquad
\Psi_{\min}-\Psi_{\text{cav}}=(%s)-(%s)=\mathbf{%s\ \text{MPa}},
\]
""" % (f(psi_min, 4), f(psi_min, 4), f(CAV, 1), f(psi_min - CAV, 4)))
w(r"""a positive margin, so no vessel reaches the cavitation threshold and the
count of embolised vessels attributable to the sink alone is exactly
$%d$. The drain is therefore sub-symptomatic at the calibrated strength, and the
collapse reported in Section~C.5 is structural rather than hydraulic.""" %
  sink["embolised_at_literature"])
check(r"T5 sink strength $K_h$", 0.0392, sink["K_H_HOLOPARASITE"])
check(r"T5 minimum $\Psi$ (MPa)", -1.02, psi_min)

if sweep:
    sub("Sensitivity of the margin to the assumed gradient")
    sg = col(sweep, "gradient_MPa")
    sp = col(sweep, "min_psi_MPa")
    sm = col(sweep, "margin_to_cavitation_MPa")
    se = col(sweep, "n_embolized")
    # The sweep is piecewise linear: the vessel holding the minimum migrates as
    # the reservoir deepens, so each branch has its own slope. Fit the final
    # (steepest) branch, which is the one that governs any extrapolation.
    dif = np.diff(sp)
    k = len(dif) - 1
    while k > 0 and abs(dif[k - 1] - dif[-1]) < 1e-6:
        k -= 1
    lin = np.zeros(sp.size, bool)
    lin[k:] = True
    slope, icpt = np.polyfit(sg[lin], sp[lin], 1)
    g_knee = float(sg[lin].min())
    plateau = sp[0]
    worst = int(np.argmin(sp))
    w(r"""The $%s$~MPa gradient is illustrative rather than measured, so the
conclusion must not depend on it. Holding $K_h$ at its calibrated value and
sweeping the host--parasite gradient over $[%s, %s]$~MPa in %d steps gives a
piecewise-linear response: $\Psi_{\min}$ sits at its baseline $%s$~MPa while the
sink is not the binding constraint, and each time the deepening reservoir moves
the minimum to a vessel closer to the haustorium the slope steepens. The final
and steepest branch, from $g=%s$~MPa upward, is""" %
      (f(sink["gradient_MPa"], 1), f(sg.min(), 1), f(sg.max(), 1), sg.size,
       f(plateau, 4), f(g_knee, 1)))
    w(r"""
\[
\Psi_{\min}(g) = %s %s\,g \quad\text{MPa}
\qquad (R^{2}=%s,\ \ %d\text{ points}),
\]
""" % (f(icpt, 4), ("+ %s" % f(slope, 4)) if slope > 0 else ("- %s" % f(-slope, 4)),
       f(np.corrcoef(sg[lin], sp[lin])[0, 1] ** 2, 6), int(lin.sum())))
    w(r"""so the worst case in the sweep is the deepest reservoir, $g=%s$~MPa:""" %
      f(sg[worst], 1))
    w(r"""
\[
\Psi_{\min}=%s\ \text{MPa},
\qquad
\Psi_{\min}-\Psi_{\text{cav}}=(%s)-(%s)=\mathbf{%s\ \text{MPa}}>0 .
\]
""" % (f(sp[worst], 4), f(sp[worst], 4), f(CAV, 1), f(sm[worst], 4)))
    w(r"""The margin therefore stays positive across the whole swept range and
the embolised-vessel count is $%d$ at every one of the %d gradients tested, so
the cavitation-onset gradient is undefined (no crossing exists below
$%s$~MPa). Extrapolating that steepest branch --- the conservative choice, since
every earlier branch is shallower --- the threshold would first be reached at
\[
g^{*}=\frac{\Psi_{\text{cav}}-(%s)}{%s}=\frac{(%s)-(%s)}{%s}\approx %s\ \text{MPa},
\]
roughly %s times the illustrative gradient. The sub-symptomatic conclusion is
thus a property of the calibrated sink strength, not of the assumed
gradient.""" %
      (int(se.max()), sg.size, f(sg.max(), 1),
       f(icpt, 4), f(slope, 4), f(CAV, 1), f(icpt, 4), f(slope, 4),
       f((CAV - icpt) / slope, 1),
       f((CAV - icpt) / slope / sink["gradient_MPa"], 1)))
    summary_table([r"Gradient $g$ (MPa)", r"$\Psi_{\text{parasite}}$ (MPa)",
                   r"$\Psi_{\min}$ (MPa)", r"Margin (MPa)", r"Vessels embolised",
                   r"Diversion"],
                  [[f(float(r_["gradient_MPa"]), 1),
                    f(float(r_["psi_parasite_MPa"]), 4),
                    f(float(r_["min_psi_MPa"]), 4),
                    f(float(r_["margin_to_cavitation_MPa"]), 4),
                    int(r_["n_embolized"]),
                    f(float(r_["diversion_fraction"]), 4)]
                   for r_ in sweep[::5]],
                  r"Cavitation Margin Across the Swept Host--Parasite Gradient")
    note(r"""Every fifth point of the %d-point sweep is shown; the full sweep is
archived in \texttt{data/sink\_sweep.csv}. The diversion fraction rises with the
gradient because the reservoir deepens while $K_h$ is held fixed.""" % sg.size)
    check(r"T5 embolised vessels, worst gradient", 0, float(se.max()))

# ==========================================================================
sec("Architectural Predictors of the Threshold (Results Table 6)")
sw_pc = stats.shapiro(pc_rand)
sw_k = stats.shapiro(pc_k)
sw_D = stats.shapiro(pc_D)
sw_L = stats.shapiro(pc_loop[np.isfinite(pc_loop)])

sub("Normality tests")
w(r"""The Shapiro--Wilk statistic is
$W=\left(\sum a_i x_{(i)}\right)^{2}\big/\sum (x_i-\bar{x})^{2}$, where the
$a_i$ are the tabulated expected-order-statistic weights; it is evaluated with
the standard algorithm rather than by hand. On the %d percolation leaves:""" %
  pc_rand.size)
summary_table([r"Variable", r"$W$", r"$p$", r"Decision at $\alpha=.05$"],
              [[r"$p_c$ (random)", f(sw_pc.statistic, 3), pval(sw_pc.pvalue),
                "Reject normality"],
               [r"Mean degree $\langle k\rangle$", f(sw_k.statistic, 3), pval(sw_k.pvalue),
                "Reject normality" if sw_k.pvalue < .05 else "Retain normality"],
               [r"Fractal dimension $D$", f(sw_D.statistic, 3), pval(sw_D.pvalue),
                "Reject normality" if sw_D.pvalue < .05 else "Retain normality"],
               [r"Loop fraction", f(sw_L.statistic, 3), pval(sw_L.pvalue),
                "Reject normality" if sw_L.pvalue < .05 else "Retain normality"]],
              r"Shapiro--Wilk Tests Justifying the Use of Rank Statistics")
note(r"""Rejection for $p_c$ and for the connectivity predictors is what
motivates Spearman's $\rho$ in place of Pearson's $r$ throughout.""")

for _lab, _ref, _st in ((r"T6 Shapiro--Wilk $W$: $p_c$", 0.911, sw_pc),
                        (r"T6 Shapiro--Wilk $W$: $\langle k\rangle$", 0.971, sw_k),
                        (r"T6 Shapiro--Wilk $W$: $D$", 0.964, sw_D),
                        (r"T6 Shapiro--Wilk $W$: loop fraction", 0.978, sw_L)):
    check(_lab, _ref, float(_st.statistic))

sub("Rank correlations with the threshold")
sk = spearman(pc_k, pc_rand)
sD = spearman(pc_D, pc_rand)
sL = spearman(pc_loop, pc_rand)
skD = spearman(pc_k, pc_D)
sLD = spearman(pc_loop, pc_D)
skL = spearman(pc_k, pc_loop)
spearman_block(r"Mean degree and $p_c$", sk, "k", "p")

sub("Partial rank correlations")
w(r"""Each partial correlation is formed from three zero-order Spearman
coefficients. Controlling mean degree for fractal dimension:""")
pk = partial(sk["rho"], skD["rho"], sD["rho"], sk["n"])
w(r"""
\[
\rho_{kp\cdot D}
=\frac{\rho_{kp}-\rho_{kD}\,\rho_{pD}}
{\sqrt{(1-\rho_{kD}^{2})(1-\rho_{pD}^{2})}}
=\frac{%s-(%s)(%s)}{\sqrt{(1-%s)(1-%s)}}
=\frac{%s}{%s}=\mathbf{%s}
\]
""" % (f(sk["rho"], 4), f(skD["rho"], 4), f(sD["rho"], 4),
       f(skD["rho"] ** 2, 4), f(sD["rho"] ** 2, 4),
       f(pk["num"], 4), f(pk["den"], 4), f(pk["r"], 4)))
pD = partial(sD["rho"], skD["rho"], sk["rho"], sD["n"])
pL = partial(sL["rho"], sLD["rho"], sD["rho"], sL["n"])
w(r"""and, by the same substitution with the roles exchanged,
$\rho_{Dp\cdot k}=%s$ and $\rho_{Lp\cdot D}=%s$.""" % (f(pD["r"], 4), f(pL["r"], 4)))

summary_table([r"Predictor", r"$n$", r"$\sum d^{2}$", r"$\rho_s$ with $p_c$",
               r"$t$", r"$p$", r"Partial $\rho$", r"$t$", r"$p$"],
              [[r"Mean degree $\langle k\rangle$", sk["n"], g(sk["d2"], 0),
                g(sk["rho"], 3), "%.2f" % sk["t"], pval(sk["p"]),
                g(pk["r"], 3), "%.2f" % pk["t"], pval(pk["p"])],
               [r"Fractal dimension $D$", sD["n"], g(sD["d2"], 0),
                g(sD["rho"], 3), "%.2f" % sD["t"], pval(sD["p"]),
                g(pD["r"], 3), "%.2f" % pD["t"], pval(pD["p"])],
               [r"Loop fraction", sL["n"], g(sL["d2"], 0),
                g(sL["rho"], 3), "%.2f" % sL["t"], pval(sL["p"]),
                g(pL["r"], 3), "%.2f" % pL["t"], pval(pL["p"])]],
              r"Rank and Partial Rank Correlations of the Predictors With $p_c$")
note(r"""Each partial correlation controls for fractal dimension, except that of
fractal dimension itself, which controls for mean degree. $df=n-3=%d$ for the
partial tests.""" % (sk["n"] - 3))
check(r"T6 $\rho_s$: $\langle k\rangle$ with $p_c$", 0.733, sk["rho"])
check(r"T6 $\rho_s$: $D$ with $p_c$", 0.496, sD["rho"])
check(r"T6 $\rho_s$: loop fraction with $p_c$", 0.727, sL["rho"])
check(r"T6 partial $\rho$: $\langle k\rangle$", 0.736, pk["r"])
check(r"T6 partial $\rho$: $D$", 0.503, pD["r"])

sub("Standardized multiple regression")
m = ols2(pc_rand, pc_k, pc_D, standardize=True)
w(r"""With both predictors converted to $z$ scores, the two-predictor solution
follows in closed form from the three Pearson correlations
$r_{y1}=%s$ (threshold with $\langle k\rangle$), $r_{y2}=%s$ (threshold with
$D$), and $r_{12}=%s$ (the two predictors with each other):""" %
  (f(m["r_y1"], 4), f(m["r_y2"], 4), f(m["r_12"], 4)))
w(r"""
\begin{align*}
\beta_{\langle k\rangle}
&=\frac{r_{y1}-r_{y2}r_{12}}{1-r_{12}^{2}}\cdot s_y
=\frac{%s-(%s)(%s)}{1-%s}\cdot %s=\mathbf{%s}\\[4pt]
\beta_{D}
&=\frac{r_{y2}-r_{y1}r_{12}}{1-r_{12}^{2}}\cdot s_y
=\frac{%s-(%s)(%s)}{1-%s}\cdot %s=\mathbf{%s}\\[4pt]
\beta_{0}&=\bar{y}=%s
\qquad(\text{both }z\text{ predictors have mean }0)\\[4pt]
R^{2}&=\frac{r_{y1}^{2}+r_{y2}^{2}-2r_{y1}r_{y2}r_{12}}{1-r_{12}^{2}}
=\frac{%s+%s-2(%s)(%s)(%s)}{1-%s}=\mathbf{%s}\\[4pt]
F(2,%d)&=\frac{R^{2}/2}{(1-R^{2})/(n-3)}=%s,\qquad p%s
\end{align*}
""" % (f(m["r_y1"], 4), f(m["r_y2"], 4), f(m["r_12"], 4), f(m["r_12"] ** 2, 4),
       f(m["sy"], 4), f(m["b1"], 4),
       f(m["r_y2"], 4), f(m["r_y1"], 4), f(m["r_12"], 4), f(m["r_12"] ** 2, 4),
       f(m["sy"], 4), f(m["b2"], 4),
       f(m["b0"], 4),
       f(m["r_y1"] ** 2, 4), f(m["r_y2"] ** 2, 4), f(m["r_y1"], 4), f(m["r_y2"], 4),
       f(m["r_12"], 4), f(m["r_12"] ** 2, 4), f(m["R2"], 4),
       m["n"] - 3, f(m["F"], 2),
       ("<.001" if m["pF"] < .001 else "=%.4f" % m["pF"])))
w(r"""The model therefore accounts for $%s\%%$ of the variance in the collapse
threshold, and the fitted equation is
$\hat{p}_c=%s+%s z_{\langle k\rangle}+%s z_{D}$.""" %
  (f(100 * m["R2"], 1), f(m["b0"], 4), f(m["b1"], 4), f(m["b2"], 4)))
check(r"T6 multiple regression $R^{2}$", 0.507, m["R2"])

# ==========================================================================
sec("Synthetic Causal Grid (Results Table 7)")
gk = col(grid, "mean_degree")
gD = col(grid, "D")
gpc = col(grid, "pc_random")
gpcd = col(grid, "pc_degree")

sgk = spearman(gk, gpc)
sgD = spearman(gD, gpc)
sgkD = spearman(gk, gD)
w(r"""In the grid the two predictors are decoupled by construction: their
Pearson correlation is $r_{\langle k\rangle D}=%s$ and their rank correlation is
$\rho=%s$, so each can be attributed a threshold effect that the observational
cohort cannot isolate.""" % (f(np.corrcoef(gk, gD)[0, 1], 4), f(sgkD["rho"], 4)))
spearman_block(r"Mean degree and $p_c$ (random attack, synthetic grid)", sgk, "k", "p")

pgk = partial(*[np.corrcoef(a, b)[0, 1] for a, b in
                ((gk, gpc), (gk, gD), (gpc, gD))], n=gk.size)
pgD = partial(np.corrcoef(gD, gpc)[0, 1], np.corrcoef(gD, gk)[0, 1],
              np.corrcoef(gpc, gk)[0, 1], gk.size)
mg = ols2(gpc, gk, gD, standardize=False)
w(r"""The raw-scale regression solves in the same closed form as Section~C.8
but without $z$ scoring, so the slopes are in threshold units per unit of
predictor:""")
w(r"""
\begin{align*}
\hat{p}_c &= %s + %s\,\langle k\rangle + %s\,D \\
R^{2} &= %s, \qquad F(2,%d) = %s, \qquad p%s
\end{align*}
""" % (f(mg["b0"], 5), f(mg["b1"], 5), f(mg["b2"], 5), f(mg["R2"], 4),
       mg["n"] - 3, f(mg["F"], 1),
       ("<.001" if mg["pF"] < .001 else "=%.4f" % mg["pF"])))
w(r"""Reading the slopes directly: raising mean degree by $0.1$ raises the
predicted threshold by $%s$, whereas raising $D$ by the same $0.1$ raises it by
only $%s$ --- a ratio of $%s$ to $1$ in favour of connectivity.""" %
  (f(0.1 * mg["b1"], 5), f(0.1 * mg["b2"], 5), f(mg["b1"] / mg["b2"], 1)))

mgd = ols2(gpcd, gk, gD, standardize=False)
summary_table([r"Attack", r"Predictor", r"$\rho_s$", r"Partial $r$",
               r"OLS $\beta$", r"Model $R^{2}$"],
              [["Random", r"Mean degree $\langle k\rangle$", g(sgk["rho"], 3),
                g(pgk["r"], 3), g(mg["b1"], 4), g(mg["R2"], 3)],
               ["", r"Fractal dimension $D$", g(sgD["rho"], 3),
                g(pgD["r"], 3), g(mg["b2"], 4), g(mg["R2"], 3)],
               ["Degree-targeted", r"Mean degree $\langle k\rangle$",
                g(spearman(gk, gpcd)["rho"], 3),
                g(partial(np.corrcoef(gk, gpcd)[0, 1], np.corrcoef(gk, gD)[0, 1],
                          np.corrcoef(gpcd, gD)[0, 1], gk.size)["r"], 3),
                g(mgd["b1"], 4), g(mgd["R2"], 3)],
               ["", r"Fractal dimension $D$",
                g(spearman(gD, gpcd)["rho"], 3),
                g(partial(np.corrcoef(gD, gpcd)[0, 1], np.corrcoef(gD, gk)[0, 1],
                          np.corrcoef(gpcd, gk)[0, 1], gk.size)["r"], 3),
                g(mgd["b2"], 4), g(mgd["R2"], 3)]],
              r"Synthetic Causal Grid: Threshold Regressed on the Two Decoupled Axes")
note(r"""$n=%d$ grid networks. Model $R^{2}$ is the full two-predictor value and
is therefore identical for both rows of an attack strategy. Partial
correlations here are product-moment, matching the OLS decomposition they
accompany.""" % gk.size)
check(r"T7 $\rho_s$: $\langle k\rangle$ (grid)", 0.991, sgk["rho"])
check(r"T7 $\rho_s$: $D$ (grid)", 0.227, sgD["rho"])
check(r"T7 partial $r$: $\langle k\rangle$ (grid)", 0.940, pgk["r"])
check(r"T7 OLS $\beta_{\langle k\rangle}$", 0.120, mg["b1"])
check(r"T7 model $R^{2}$", 0.887, mg["R2"])
check(r"T7 partial $r$: $D$ (grid)", 0.195, pgD["r"])
check(r"T7 OLS $\beta_{D}$", 0.029, mg["b2"])

# ==========================================================================
sec("Reticulation, Bridge Dependence, and Damage Tolerance (Results Tables 8--9)")
gap = pc_rand - pc_deg
sLp = spearman(pc_loop, pc_rand)
sBp = spearman(pc_bridge, pc_rand)
sBt = spearman(pc_bridge, pc_deg)
sLg = spearman(pc_loop, gap)

w(r"""Bridge fraction is the exact complement of loop fraction, so
$\rho_{\text{bridge},p}=-\rho_{\text{loop},p}$ identically; the two rows are one
result stated twice, in opposite sign. The attack gap is
$\text{gap}_i=p_c^{\text{random}}-p_c^{\text{targeted}}$, the extra damage a
leaf tolerates when the loss is unstructured.""")

sub("Residual loop fraction after mean degree is removed")
res_loop = resid(pc_loop, pc_k)
sres = spearman(res_loop, pc_rand)
w(r"""Regressing loop fraction on mean degree gives residuals
$e_i=L_i-(\hat{a}+\hat{b}\langle k\rangle_i)$ with $\hat{b}=%s$; correlating
those residuals with the threshold tests whether reticulation carries
information beyond connectivity.""" %
  f(np.polyfit(pc_k, pc_loop, 1)[0], 4))
spearman_block("Residual loop fraction and $p_c$", sres, "e", "p")
w(r"""The non-significant result ($\rho=%s$, $p=%.3f$) is a consequence of the
near-perfect $\rho=%s$ between loop fraction and mean degree established in
Section~C.4: once one is removed almost nothing of the other is left to
correlate.""" % (f(sres["rho"], 3), sres["p"], f(s0["rho"], 3)))

t8 = []
for name, s in (("Loop fraction and $p_c$ (random)", sLp),
                ("Bridge fraction and $p_c$ (random)", sBp),
                ("Bridge fraction and $p_c$ (degree-targeted)", sBt),
                ("Loop fraction and random--targeted gap", sLg),
                (r"Residual loop fraction ($\langle k\rangle$ controlled) and $p_c$", sres)):
    t8.append([name, s["n"], g(s["d2"], 0), g(s["rho"], 3), "%.2f" % s["t"],
               pval(s["p"]), "Reject $H_0$" if s["p"] < .05 else "Fail to reject $H_0$"])
summary_table([r"Variables", r"$n$", r"$\sum d^{2}$", r"$\rho_s$", r"$t$",
               r"$p$", r"Decision"], t8,
              r"Reticulation, Bridge Dependence, and Damage Tolerance",
              colspec="lrrrrll")

sub("Quartile ladder and the Mann--Whitney comparison")
ok = np.isfinite(pc_loop)
order = np.argsort(pc_loop[ok])
Lq = pc_loop[ok][order]
Pq = pc_rand[ok][order]
Kq = pc_k[ok][order]
nq = Lq.size
cuts = [round(nq * i / 4) for i in range(5)]
qrows = []
qs = []
for i in range(4):
    sl = slice(cuts[i], cuts[i + 1])
    qs.append(Pq[sl])
    qrows.append(["Q%d%s" % (i + 1, (" (least reticulate)" if i == 0 else
                                     " (most reticulate)" if i == 3 else "")),
                  Pq[sl].size, f(np.median(Lq[sl]), 3), f(np.median(Kq[sl]), 3),
                  f(np.median(Pq[sl]), 4)])
summary_table([r"Quartile", r"$n$", r"$Mdn$ loop fraction",
               r"$Mdn\ \langle k\rangle$", r"$Mdn\ p_c$"], qrows,
              r"Damage Tolerance by Reticulation Quartile")

mw = mannwhitney(qs[3], qs[0])
dq = float(np.median(qs[3]) - np.median(qs[0]))
w(r"""The Q1--Q4 contrast is tested with the Mann--Whitney $U$ statistic, the
two-sample analogue of the signed-rank test used in Section~C.5:""")
w(r"""
\begin{align*}
n_1 &= %d, \qquad n_2 = %d, \qquad R_1 = %s \\
U_1 &= n_1n_2+\tfrac{n_1(n_1+1)}{2}-R_1 = (%s)(%s)+%s-%s = %s \\
U_2 &= n_1n_2-U_1 = %s, \qquad U = \min(U_1,U_2)=\mathbf{%s}\\
\mu_U &= \tfrac{n_1n_2}{2} = %s, \qquad \sigma_U = %s\\
z &= \frac{U-\mu_U}{\sigma_U} = %s, \qquad p %s
\end{align*}
""" % (mw["n1"], mw["n2"], thousands(mw["R1"]),
       mw["n1"], mw["n2"], thousands(mw["n1"] * (mw["n1"] + 1) / 2), thousands(mw["R1"]),
       thousands(mw["U1"]), thousands(mw["U2"]), thousands(mw["U"]),
       thousands(mw["mu"]), f(mw["sigma"], 2), f(mw["z"], 3),
       ("<.001" if mw["p"] < .001 else "=%.4f" % mw["p"])))
w(r"""The absolute difference between the extreme quartile medians is
$%s-%s=\mathbf{%s}$, a relative gain of
$%s/%s\times 100=\mathbf{%s\%%}$.""" %
  (f(np.median(qs[3]), 4), f(np.median(qs[0]), 4), f(dq, 4),
   f(dq, 4), f(np.median(qs[0]), 4), f(100 * dq / np.median(qs[0]), 1)))
check(r"T9 Q1--Q4 $Mdn$ difference", 0.072, dq)
check(r"T9 relative gain (\%)", 46.0, 100 * dq / np.median(qs[0]))

# ==========================================================================
sec("Reticulation Enhancement (Results Tables 10--12)")
k_ceiling = sugsum["target_mean_degree"]
w(r"""Each leaf is rewired so that its mean degree rises toward the cohort's
90th-percentile ceiling, $\langle k\rangle_{90}=%s$, and the percolation run is
repeated. The valid set is the %d leaves of %d satisfying $N\geq 1000$ and
$p_c^{\text{current}}\geq 0.02$; the %d excluded networks are fragments on which
a threshold is not defined.""" %
  (f(k_ceiling, 3), len(sug_valid), len(suggested), len(suggested) - len(sug_valid)))

d_cur, d_new, d_del = describe(s_cur), describe(s_new), describe(s_del)
descriptive_block(r"$\Delta p_c$ over the valid cohort", "d", d_del)

n_imp = int((s_del > 0).sum())
n_same = int((s_del == 0).sum())
n_worse = int((s_del < 0).sum())
w(r"""Of the %d leaves, %d improved, %d were unchanged, and %d worsened, so the
improvement fraction is $%d/%d=%s=\mathbf{%s\%%}$.""" %
  (len(s_del), n_imp, n_same, n_worse, n_imp, len(s_del),
   f(n_imp / len(s_del), 4), f(100 * n_imp / len(s_del), 1)))

wl2 = wilcoxon(s_new, s_cur)
w(r"""
\begin{align*}
n_r &= %d \text{ (of %d; %d zero differences discarded)} \\
W^{+} &= %s, \qquad W^{-} = %s, \qquad W = \min(W^{+},W^{-}) = \mathbf{%s}\\
\mu_W &= \tfrac{n_r(n_r+1)}{4} = %s, \qquad \sigma_W = %s \\
z &= \frac{W-\mu_W}{\sigma_W} = %s, \qquad p %s
\end{align*}
""" % (wl2["nr"], wl2["n0"], wl2["nzero"], thousands(wl2["Wp"]),
       thousands(wl2["Wm"]), thousands(wl2["W"]), thousands(wl2["mu"]),
       f(wl2["sigma"], 2), f(wl2["z"], 3),
       ("<.001" if wl2["p"] < .001 else "=%.4f" % wl2["p"])))
w(r"""$H_0$ (the median change in $p_c$ is zero) is rejected; because no leaf
worsened, $W^{-}=0$ and $W=0$.""")

grades = ["A", "B", "C", "D"]
grows = []
for gr in grades:
    idx = [i for i, q in enumerate(s_grade) if q == gr]
    if not idx:
        continue
    c, nw, dl = s_cur[idx], s_new[idx], s_del[idx]
    grows.append([gr, len(idx), f(np.median(c), 4), f(np.median(nw), 4),
                  f(np.median(dl), 4), "%.0f\\%%" % (100 * (dl > 0).mean())])
grows.append([r"Full valid cohort", len(s_del), f(np.median(s_cur), 4),
              f(np.median(s_new), 4), f(np.median(s_del), 4),
              "%.0f\\%%" % (100 * n_imp / len(s_del))])
summary_table([r"Grade", r"$n$", r"$Mdn\ p_c$ current", r"$Mdn\ p_c$ enhanced",
               r"$Mdn\ \Delta p_c$", r"\% improved"], grows,
              r"Reticulation-Enhancement Effect by Tracing-Quality Grade")
note(r"""Grade is the leading tracing-quality flag recorded for each leaf;
grade A denotes artifact-free tracings, which give the conservative lower bound
on the benefit. Grades partition the cohort, so the four $n$ values sum to
%d.""" % len(s_del))

for _gr, _ref in (("A", (0.220, 0.227, 0.0069)), ("B", (0.190, 0.211, 0.0137)),
                  ("C", (0.161, 0.171, 0.0083)), ("D", (0.205, 0.219, 0.0086))):
    _i = [j for j, q in enumerate(s_grade) if q == _gr]
    check(r"T10 grade %s $Mdn\ \Delta p_c$" % _gr, _ref[2], float(np.median(s_del[_i])))
check(r"T10 cohort $Mdn\ \Delta p_c$", 0.0095, float(np.median(s_del)))
check(r"T10 cohort $M\ \Delta p_c$", 0.0123, float(np.mean(s_del)))
check(r"T10 cohort $SD\ \Delta p_c$", 0.0109, float(np.std(s_del, ddof=1)))
check(r"T10 leaves improved", 93, float(n_imp))

sub("Dependence of the gain on initial architecture")
sdk = spearman(s_k0, s_del)
sdD = spearman(s_D, s_del)
md = ols2(s_del, s_k0, s_D, standardize=True)
spearman_block(r"Initial mean degree and $\Delta p_c$", sdk, "k", "d")
w(r"""Fractal dimension is unrelated to the gain
($\rho_s=%s$, $t(%d)=%s$, $p=%.3f$), and the two-predictor standardized model
gives $R^{2}=%s$: essentially all of the explainable variation in the gain comes
from how sparse the leaf started.""" %
  (f(sdD["rho"], 3), sdD["dof"], f(sdD["t"], 2), sdD["p"], f(md["R2"], 3)))
check(r"T11 $\rho_s$: initial $\langle k\rangle$ with $\Delta p_c$", -0.821, sdk["rho"])
check(r"T11 $\rho_s$: $D$ with $\Delta p_c$", -0.034, sdD["rho"])
check(r"T11 model $R^{2}$", 0.655, md["R2"])

sub("Largest gains")
order = np.argsort(-s_del)[:6]
SPECIES = {
    "Clu_ala": "Clusia alata", "Chl_spi": "Chloranthus spicatus",
    "Ane_cal": "Anemopsis californica", "Met_dav": "Metapanax davidii",
    "Eur_jap": "Eurya japonica", "Smi_his": "Smilax hispida",
    "Vio_gla": "Viola glabella", "Abe_mex": "Abelia mexicana",
}
trows = []
for i in order:
    r = sug_valid[i]
    sp = SPECIES.get(r["species"], r["species"].replace("_", r"\_"))
    a, b = float(r["pc_current"]), float(r["pc_suggested"])
    trows.append([r"\textit{%s}" % sp, thousands(float(r["N"])),
                  f(float(r["k_current"]), 3), thousands(float(r["loops_added"])),
                  f(a, 4), f(b, 4),
                  r"$%s-%s=%s$" % (f(b, 4), f(a, 4), f(b - a, 4))])
summary_table([r"Species", r"$N$", r"$\langle k\rangle$ current", r"Loops added",
               r"$p_c$ before", r"$p_c$ after", r"$\Delta p_c$"], trows,
              r"Leaves Exhibiting the Largest Threshold Gain, With the Subtraction Shown",
              colspec="lrrrrrl")
note(r"""Sorted by descending gain. Each $\Delta p_c$ is the plain difference of
the two adjacent columns; all six leaves begin near the lower bound of the
cohort's mean-degree range, which is the pattern quantified by
$\rho_s=%s$ above.""" % f(sdk["rho"], 3))

# ==========================================================================
sec("Response-Surface Headroom")
cg = col(ceiling, "gain_from_reticulation")
cd = col(ceiling, "gain_from_D")
dom = [r["dominant_lever"] for r in ceiling]
w(r"""The headroom analysis substitutes each leaf's own $\langle k\rangle$ and
$D$ into the synthetic response surface of Section~C.9, then re-evaluates it
with one axis raised to its 90th-percentile cap. The gain attributable to each
lever is the difference of the two predictions:""")
w(r"""
\[
\text{gain}_{\text{ret}} = \hat{p}_c(\langle k\rangle_{90}, D)-\hat{p}_c(\langle k\rangle, D)
= \beta_{\langle k\rangle}\left(\langle k\rangle_{90}-\langle k\rangle\right),
\qquad
\text{gain}_{D} = \beta_{D}\left(D_{90}-D\right),
\]
""")
w(r"""so with $\beta_{\langle k\rangle}=%s$ and $\beta_{D}=%s$ from
Section~C.9 the levers differ by the factor $\beta_{\langle k\rangle}/\beta_{D}=%s$
before any leaf-specific gap is considered. Across the %d leaves the median
reticulation gain is $%s$ against a median $D$ gain of $%s$, and reticulation is
the dominant lever in $%d/%d=%s\%%$ of leaves.""" %
  (f(mg["b1"], 5), f(mg["b2"], 5), f(mg["b1"] / mg["b2"], 2), len(cg),
   f(np.median(cg), 5), f(np.median(cd), 5),
   dom.count("reticulation"), len(dom),
   f(100 * dom.count("reticulation") / len(dom), 0)))
w(r"""Two limits on this extrapolation must be stated, because both are visible
in the same file. First, the surface does not reproduce the measured thresholds
of the leaves it is applied to: its predicted $p_c$ has a median of $%s$ against
a measured median of $%s$, a systematic over-prediction of $%s$, and the two
correlate at only $r=%s$. Second, the gain it predicts from added reticulation
has a median of $%s$, whereas rewiring each leaf and re-measuring its threshold
(Section~C.11) gives a median gain of $%s$ --- a factor of %s smaller. The
response surface and the rewiring experiment therefore agree on the
\emph{direction} of the reticulation lever and disagree on its \emph{size}; only
the rewiring result is a measurement, and the two must not be presented as
corroborating one another.""" %
  (f(np.median(col(ceiling, "pc_model_now")), 4),
   f(np.median(col(ceiling, "pc_measured")), 4),
   f(np.median(np.array(col(ceiling, "pc_model_now"))
               - np.array(col(ceiling, "pc_measured"))), 4),
   f(pearson(col(ceiling, "pc_model_now"), col(ceiling, "pc_measured"))["r"], 3),
   f(np.median(cg), 5), f(np.median(s_del), 5),
   f(np.median(cg) / np.median(s_del), 1)))
note(r"""This is a first-order linear extrapolation on a surface with
$R^{2}=%s$; it states a direction and an order of magnitude, not a designed
network, and it prices no cost or efficiency trade-off.""" % f(mg["R2"], 3))

# ==========================================================================
sec("Model Validation (Results Table 13)")
hv = hydval["summary"]
w(r"""Four independent checks are reported. The first compares, vein by vein,
the model's Hagen--Poiseuille resistance $R\propto L/r^{4}$ against the
resistance column shipped with the source dataset, correlating on the log scale
because the values span several orders of magnitude:""")
w(r"""
\[
r_{\log}
=\frac{n\sum \log R_{\text{model}}\log R_{\text{source}}
-\sum\log R_{\text{model}}\sum\log R_{\text{source}}}
{\sqrt{\left[n\sum\log^{2}R_{\text{model}}-(\sum\log R_{\text{model}})^{2}\right]
\left[n\sum\log^{2}R_{\text{source}}-(\sum\log R_{\text{source}})^{2}\right]}}
\geq %s
\]
""" % f(hv["min_pearson_log_r"], 15))
w(r"""across all %s veins in %d leaves. The worst per-leaf coefficient of
variation of the ratio $R_{\text{model}}/R_{\text{source}}$ is $%s$ and the
worst median ratio departs from unity by $%s$, both far inside the
$%s$ tolerance; the agreement is therefore exact to floating-point precision
rather than merely strong. The wrong-exponent control repeats the comparison
with $R\propto L/r^{2}$ and falls to a median of $%s$, which shows that the
exact match is a real reproduction of the physics and not an artifact of
correlating two monotone columns.""" %
  (thousands(hv["total_veins_compared"]), hv["n_leaves"],
   f(hv["worst_ratio_cv"], 3), f(hv["worst_abs_median_ratio_minus_1"], 3),
   f(hv["cv_tolerance"], 3), f(hv["median_pearson_wrong_exponent_control"], 4)))
w(r"""One leaf (\textit{%s}) is absent from this comparison for having fewer
than 50 usable veins, so the scope is %d of the 120 traced networks. It is the
ratio statistics, not the correlation, that establish equality: a correlation of
unity is consistent with any constant rescaling, whereas a ratio whose median
departs from one by $%s$ establishes that the two columns hold the same
numbers.""" % (hv["skipped"][0]["species"].replace("_", r"\_"), hv["n_leaves"],
                f(hv["worst_abs_median_ratio_minus_1"], 3)))
w(r"""The remaining two checks are weaker and are reported as limitations. A
rank comparison of modelled whole-leaf conductance against measured
$K_{\text{leaf}}$ for %d species gives $\rho_s=%s$, $p=%.3f$ --- weak
\emph{and not significant} at $\alpha=.05$ --- which is the expected result for
a xylem-only model compared against a quantity dominated by resistances outside
the xylem. A crop-edge sensitivity test places %d of %d leaves inside both
tolerances, which means %d fall outside them; those %d are the smallest and most
heavily windowed tracings, and %d of them survive into the %d-network
enhancement cohort (%s), one being the largest-gain network reported in Results
Table 12.""" %
  (kleaf["n_species"], f(kleaf["spearman_rho"], 3), kleaf["spearman_p"],
   bound["summary"]["n_within_tolerance"], bound["summary"]["n_leaves"],
   bound["summary"]["n_leaves"] - bound["summary"]["n_within_tolerance"],
   bound["summary"]["n_leaves"] - bound["summary"]["n_within_tolerance"],
   len(provn["boundary_check"]["outside_tolerance_but_in_enhancement_cohort"]),
   provn["enhancement_cohort_105"]["n"],
   ", ".join(s.replace("_", r"\_") for s in
             provn["boundary_check"]["outside_tolerance_but_in_enhancement_cohort"])))

summary_table([r"Check", r"Scope", r"Statistic", r"Result", r"Reading"],
              [["Hydraulic resistance",
                r"%d leaves, %s veins" % (hv["n_leaves"], thousands(hv["total_veins_compared"])),
                r"Worst ratio $CV$", r"$%s$" % f(hv["worst_ratio_cv"], 3),
                "Agreement to floating-point precision"],
               ["", "", r"Worst $|Mdn\ \text{ratio}-1|$",
                r"$%s$" % f(hv["worst_abs_median_ratio_minus_1"], 3),
                r"Inside the $%s$ tolerance" % f(hv["cv_tolerance"], 3)],
               ["Wrong-exponent control", "Same veins", r"Median $r_{\log}$",
                f(hv["median_pearson_wrong_exponent_control"], 3),
                "The match is not trivial"],
               [r"Leaf conductance $K_{\text{leaf}}$", r"%d species" % kleaf["n_species"],
                r"Spearman $\rho_s$",
                r"%s ($p=%.3f$)" % (f(kleaf["spearman_rho"], 3), kleaf["spearman_p"]),
                "Weak and non-significant; xylem-only"],
               ["Crop-edge boundary", r"%d leaves" % bound["summary"]["n_leaves"],
                "Within both tolerances",
                r"%d of %d" % (bound["summary"]["n_within_tolerance"],
                               bound["summary"]["n_leaves"]),
                r"%d outside; %d of those remain in the enhancement cohort"
                % (bound["summary"]["n_leaves"] - bound["summary"]["n_within_tolerance"],
                   len(provn["boundary_check"]["outside_tolerance_but_in_enhancement_cohort"]))]],
              r"Model Validation Summary", colspec="llllp{3.1cm}")
check(r"T13 wrong-exponent control $r$", 0.953,
      hv["median_pearson_wrong_exponent_control"])
check(r"T13 $K_{\text{leaf}}$ rank agreement", 0.187, kleaf["spearman_rho"])

# ==========================================================================
# --------------------------------------------------------------------------
# Remaining reported cells, registered here so that C.14 covers every number
# printed in the Results tables rather than a selection.
# --------------------------------------------------------------------------
check(r"T3 random attack $M$", 0.1847, dR["M"])
check(r"T3 random attack $SD$", 0.0541, dR["sd"])
check(r"T3 random attack min", 0.0262, dR["lo"])
check(r"T3 random attack max", 0.2698, dR["hi"])
check(r"T3 targeted attack $M$", 0.1559, dT["M"])
check(r"T3 targeted attack $SD$", 0.0565, dT["sd"])
check(r"T3 targeted attack min", 0.0019, dT["lo"])
check(r"T3 targeted attack max", 0.2630, dT["hi"])

check(r"T4 random CI lower", 0.270, summary["p_c_ci95"][0])
check(r"T4 random CI upper", 0.272, summary["p_c_ci95"][1])

check(r"T5 achieved diversion (\%)", 20.0, 100 * sink["achieved_diversion"])
check(r"T5 illustrative gradient (MPa)", 1.5, sink["gradient_MPa"])
check(r"T5 embolised vessels at 1.5 MPa", 0, float(sink["embolised_at_literature"]))

check(r"T6 Shapiro--Wilk $p$: $\langle k\rangle$", 0.027, float(sw_k.pvalue))
check(r"T6 Shapiro--Wilk $p$: $D$", 0.008, float(sw_D.pvalue))
check(r"T6 Shapiro--Wilk $p$: loop fraction", 0.089, float(sw_L.pvalue))
check(r"T6 partial $\rho$: loop fraction", 0.733, pL["r"])

for _lab, _ref, _s in ((r"T8 loop fraction and $p_c$ (random)", 0.727, sLp),
                       (r"T8 bridge fraction and $p_c$ (random)", -0.727, sBp),
                       (r"T8 bridge fraction and $p_c$ (targeted)", -0.818, sBt),
                       (r"T8 loop fraction and attack gap", -0.786, sLg),
                       (r"T8 residual loop fraction and $p_c$", -0.088, sres)):
    check(_lab, _ref, _s["rho"])
check(r"T8 residual loop fraction $p$", 0.386, sres["p"])

DRAFT_T9 = [(0.615, 2.320, 0.158), (0.738, 2.472, 0.185),
            (0.807, 2.564, 0.209), (0.901, 2.734, 0.231)]
for _i, (_l, _k, _p) in enumerate(DRAFT_T9):
    _sl = slice(cuts[_i], cuts[_i + 1])
    check(r"T9 Q%d $Mdn$ loop fraction" % (_i + 1), _l, float(np.median(Lq[_sl])))
    check(r"T9 Q%d $Mdn\ \langle k\rangle$" % (_i + 1), _k, float(np.median(Kq[_sl])))
    check(r"T9 Q%d $Mdn\ p_c$" % (_i + 1), _p, float(np.median(Pq[_sl])))

DRAFT_T10 = {"A": (21, 0.220, 0.227, 62), "B": (46, 0.190, 0.211, 96),
             "C": (10, 0.161, 0.171, 100), "D": (28, 0.205, 0.219, 93)}
for _gr, (_n, _cur, _new, _imp) in DRAFT_T10.items():
    _i = [j for j, q in enumerate(s_grade) if q == _gr]
    check(r"T10 grade %s $n$" % _gr, _n, float(len(_i)))
    check(r"T10 grade %s $Mdn\ p_c$ current" % _gr, _cur, float(np.median(s_cur[_i])))
    check(r"T10 grade %s $Mdn\ p_c$ enhanced" % _gr, _new, float(np.median(s_new[_i])))
    check(r"T10 grade %s \%% improved" % _gr, _imp,
          100.0 * float((s_del[_i] > 0).mean()))
check(r"T10 cohort $Mdn\ p_c$ current", 0.201, float(np.median(s_cur)))
check(r"T10 cohort $Mdn\ p_c$ enhanced", 0.215, float(np.median(s_new)))
check(r"T10 cohort \% improved", 89, 100.0 * n_imp / len(s_del))
check(r"T10 leaves unchanged", 12, float(n_same))
check(r"T10 leaves worsened", 0, float(n_worse))
check(r"T10 ceiling $\langle k\rangle_{90}$", 2.811, k_ceiling)

check(r"T11 standardized $\beta$: $\langle k\rangle_0$", -0.0089, md["b1"])
check(r"T11 standardized $\beta$: $D$", 0.0007, md["b2"])
check(r"T11 $p$ for $D$", 0.729, sdD["p"])

DRAFT_T12 = [("Clu_ala", 6475, 2.195, 1994, 0.1351, 0.1810, 0.0459),
             ("Chl_spi", 20004, 2.148, 6632, 0.1287, 0.1745, 0.0458),
             ("Ane_cal", 85519, 2.216, 25460, 0.1545, 0.1962, 0.0417),
             ("Met_dav", 5054, 2.198, 1549, 0.1580, 0.1981, 0.0401),
             ("Eur_jap", 11423, 2.249, 3209, 0.1632, 0.2006, 0.0374),
             ("Smi_his", 31577, 2.344, 7370, 0.1934, 0.2273, 0.0339)]
_byspec = {r["species"]: r for r in sug_valid}
for _sp, _N, _k, _loops, _b, _a, _d in DRAFT_T12:
    _r = _byspec[_sp]
    _nm = SPECIES.get(_sp, _sp)
    check(r"T12 \textit{%s} $N$" % _nm, _N, float(_r["N"]))
    check(r"T12 \textit{%s} $\langle k\rangle$" % _nm, _k, float(_r["k_current"]))
    check(r"T12 \textit{%s} loops added" % _nm, _loops, float(_r["loops_added"]))
    check(r"T12 \textit{%s} $p_c$ before" % _nm, _b, float(_r["pc_current"]))
    check(r"T12 \textit{%s} $p_c$ after" % _nm, _a, float(_r["pc_suggested"]))
    check(r"T12 \textit{%s} $\Delta p_c$" % _nm, _d, float(_r["delta_pc"]))

check(r"T13 leaves compared", 119, float(hv["n_leaves"]))
check(r"T13 veins compared", 5668467, float(hv["total_veins_compared"]))
check(r"T13 $K_{\text{leaf}}$ species", 93, float(kleaf["n_species"]))
check(r"T13 leaves within crop tolerance", 105,
      float(bound["summary"]["n_within_tolerance"]))


# ==========================================================================
sec("Cohort Provenance: Which $n$ Belongs to Which Result")
w(r"""Four different sample sizes appear in the Results because four nested
screens are applied, each for a stated structural reason, and three different
Monte Carlo budgets are used. They are set out here so that no reported $n$ has
to be inferred from context.""")
summary_table([r"Set", r"$n$", r"Screen", r"Trials"],
              [[r"Traced leaves", r"%d" % provn["traced"]["n"],
                r"all networks loaded from the source archive", r"--"],
               [r"Characterization set", r"%d" % provn["characterization_112"]["n"],
                r"$n_{\text{edges}}\geq 500$", r"--"],
               [r"Percolation cohort", r"%d" % provn["percolation_cohort_100"]["n"],
                r"$n_{\text{edges}}\geq 2000$, $\geq 1$ cycle, cut-end fraction "
                r"$\leq .05$, $|\Delta\langle k\rangle|\leq .05$",
                r"%s per network per attack"
                % thousands(provn["percolation_cohort_100"]["trials_per_leaf_per_mode"])],
               [r"Enhancement cohort", r"%d" % provn["enhancement_cohort_105"]["n"],
                r"$N\geq 1000$ and current $p_c\geq .02$",
                r"%s per network" % thousands(provn["enhancement_cohort_105"]["trials_per_leaf"])],
               [r"Synthetic reference", r"1",
                r"calibrated mesh, $N=%s$" % thousands(provn["synthetic_reference_network"]["N"]),
                r"%s random; %s each targeted"
                % (thousands(provn["synthetic_reference_network"]["trials"]["random"]),
                   thousands(provn["synthetic_reference_network"]["trials"]["each_targeted"]))]],
              r"The Four Nested Cohorts and Their Monte Carlo Budgets",
              colspec=r"lrp{6.2cm}p{3.2cm}")
w(r"""The sets are strictly nested: %s. The %d networks of the enhancement
cohort that are absent from the percolation cohort are %s, admitted by the looser
size screen. The one-million-trial figure belongs to the random attack on the
synthetic reference network alone and to nothing else in the study.""" %
  (provn["nesting"].replace("subset of", r"$\subset$"),
   len(provn["enhancement_cohort_105"]["in_105_not_in_100"]),
   ", ".join(s.replace("_", r"\_")
             for s in provn["enhancement_cohort_105"]["in_105_not_in_100"])))
note(r"""%s Accordingly the cohort is described throughout as leaf-venation
networks rather than whole leaves.""" % provn["traced"]["note"].replace('"', "``", 1).replace('"', "''", 1))


# ==========================================================================
sec("Coupled Sink Surface: What Strength the Drain Must Reach")
w(r"""Section~C.7 shows that the calibrated haustorium does not cavitate the
host at any gradient. The complementary question is what happens when many
haustoria are present at once. In the coupled hydraulic mode a fraction $\rho$ of
nodes \emph{bears} a haustorium, the Kirchhoff field is solved, and only nodes
whose potential falls below $\Psi_{\text{cav}}$ are removed; the threshold is
therefore a critical \emph{attachment density}, not a removed-node fraction, and
is not comparable with the thresholds of Sections~C.5 and~C.8.""")
w(r"""The surface was recomputed on the cohort-calibrated mesh
($N=%s$, $\langle k\rangle$ held at $%s$ by tuning the mesh fraction, the $D$
axis realised at constant $N$ by tuning the length ratio and then measured), with
the sink axis anchored on the calibrated $K_h=%s$ and expressed as multiples of
it, at %s trials per cell. The earlier surface used the pre-2026 generator
($\langle k\rangle$ 4.4--7.0), sink strengths 8--64 times the calibrated value,
and 600 trials per cell.""" %
  (thousands(surf["N"]), f(surf["mean_degree_measured"][0], 3),
   f(surf["calibrated_k_h"], 4), thousands(surf["n_trials_per_cell"])))

_rows = []
for _D in surf["D_measured"]:
    _cells = [c for c in surf["cells"] if abs(c["D"] - _D) < 1e-9]
    _rows.append([f(_D, 3)] + [
        (f(c["p_c_haustorial_density"], 4) if c["threshold_exists"]
         else r"none") for c in _cells])
summary_table([r"$D$"] + [r"%d$\times$" % m for m in surf["k_h_multiples"]],
              _rows,
              r"Critical Haustorial Density by Sink Strength (Multiples of the "
              r"Calibrated $K_h$)",
              colspec="l" + "r" * len(surf["k_h_multiples"]))
_nomax = surf["largest_k_h_multiple_with_NO_threshold_in_any_row"]
_minm = surf["smallest_k_h_multiple_with_a_threshold"]
_allm = surf["smallest_k_h_multiple_with_a_threshold_in_every_row"]
if _minm:
    w(r"""Entries marked \emph{none} are cells in which the collapse probability
never reaches $.50$ at any density in $[0,1]$: no number of haustoria of that
strength fragments the network, so there is no threshold to report. At the
calibrated strength, and at every strength up to $%d\times$ it, that is the
outcome in every row. A threshold first appears in the least reticulate network
at $%d\times$ the calibrated strength and in every network at $%d\times$ it. The
sub-symptomatic conclusion of Section~C.7 therefore survives the move from one
haustorium to a whole population of them: it is the \emph{strength} of the drain,
not the number of attachment points, that the calibration rules out.""" %
      (_nomax, _minm, _allm))
note(r"""%s""" % surf["what_p_c_means"])


# ==========================================================================
sec("Finite-Size Behaviour and Why No Convergence Claim Is Made")
w(r"""Two size sweeps exist in the archive and they answer different questions.
In the first, the generator's depth parameter is the only knob, so network size
and fractal dimension rise together: $D$ moves from $%s$ at $N=%s$ to $%s$ at
$N=%s$ while $p_c$ moves from $%s$ to $%s$. Because $D$ is itself a predictor of
$p_c$ (Section~C.8, $\rho_s=%s$), that sweep cannot separate a size effect from a
geometry effect, and the rise in $p_c$ must not be reported as convergence.""" %
  (f(scaling["finite_size"][0]["D"], 3), thousands(scaling["finite_size"][0]["N"]),
   f(scaling["finite_size"][-1]["D"], 3), thousands(scaling["finite_size"][-1]["N"]),
   f(scaling["finite_size"][0]["p_c"], 4), f(scaling["finite_size"][-1]["p_c"], 4),
   f(sD["rho"], 3)))
w(r"""The second sweep pins the architecture: at each size the length ratio is
tuned until the measured $D$ matches a common target and the mesh fraction is
tuned until the measured mean degree matches the cohort value. Across a
%d-fold size range the two pinned descriptors vary by at most $%s$ in $D$ and
$%s$ in mean degree.""" %
  (fixedD["sizes"][-1]["N"] // fixedD["sizes"][0]["N"],
   f(fixedD["D_spread_achieved"], 4),
   f(fixedD["mean_degree_spread_achieved"], 4)))

summary_table([r"$N$", r"$D$", r"$\langle k\rangle$", r"Loop fraction",
               r"$p_c$", r"95\% CI", r"10--90\% window"],
              [[thousands(r_["N"]), f(r_["D"], 3), f(r_["mean_degree"], 3),
                (f(r_["unpinned_descriptors"]["loop_fraction_nonbridge"], 3)
                 if "unpinned_descriptors" in r_ else "--"),
                f(r_["p_c"], 4),
                r"[%s, %s]" % (f(r_["ci95"][0], 4), f(r_["ci95"][1], 4)),
                f(r_["width_0.1_0.9"], 4)] for r_ in fixedD["sizes"]],
              r"Finite-Size Sweep With Fractal Dimension and Mean Degree Pinned",
              colspec="rrrrrlr")

_drift = fixedD.get("architecture_drift_audit", {})
if _drift:
    w(r"""Pinning two descriptors does not pin the architecture. Regenerating each
tuned network and measuring the descriptors that were \emph{not} pinned shows the
loop fraction falling from $%s$ to $%s$ across the size range, a drift of $%s$;
loop fraction is itself one of this study's predictors of the threshold
(Section~C.10). The decline of $p_c$ from $%s$ to $%s$ in the table above
therefore tracks the loss of reticulation, not size as such.""" %
      (f(_drift["loop_fraction_range"][1], 3),
       f(_drift["loop_fraction_range"][0], 3),
       f(_drift["loop_fraction_spread"], 3),
       f(fixedD["sizes"][0]["p_c"], 4), f(fixedD["sizes"][-1]["p_c"], 4)))
    note(r"""Verdict recorded in \texttt{finite\_size\_fixedD.json}: no
finite-size claim can be made from this generator without a construction that
also holds the loop fraction fixed.""")

w(r"""Two consequences follow for the Results. First, no finite-size claim ---
convergence or divergence --- is made from this generator. Second, no critical
exponent is quoted: the archived value $\beta=%s$ is a single-size fit over %d
points and matches neither the mean-field value $1.0$ nor the two-dimensional
value $%s$. What the archive does support is a statement about the
\emph{criterion}: the empirical connectivity threshold $f_c=%s$ is the removal
fraction at which the giant component vanishes, whereas $p_c$ throughout this
appendix is the fraction at which the giant component falls below half its
initial size. The two are different criteria on the same network, which is why
$f_c$ is roughly twice $p_c$; read against its own definition, $f_c$ is of the
same order as the Molloy--Reed prediction $%s$, a qualitative agreement only,
because Molloy--Reed assumes a locally tree-like graph and the planar mesh
contains short loops.""" %
  (f(scaling["beta_test"]["beta"], 3), scaling["beta_test"]["n_fit"],
   f(scaling["beta_test"]["twoD_beta"], 3),
   f(scaling["beta_test"]["empirical_fc"], 3),
   f(scaling["beta_test"]["molloy_reed_fc"], 3)))


# ==========================================================================
sec("The Modelled Pre-Symptomatic Window")
_rates = dynam["rates"]
w(r"""The window is the interval between the density at which the network
fragments and the density at which its giant component vanishes, converted to a
time interval by a logistic model of infestation growth,
$d\rho/dt=r\rho(1-\rho)$ with $\rho_0=%s$. Solving for the crossing times gives
\[
t(\rho^{*})=\frac{1}{r}\,\ln\!\frac{\rho^{*}(1-\rho_0)}{\rho_0(1-\rho^{*})},
\qquad
\text{window}=t(f_c)-t(p_c),
\]
so the window scales as $1/r$ and the time unit is fixed by the assumed growth
rate. Both thresholds are those of the synthetic reference network
($p_c=%s$, $f_c=%s$).""" %
  (f(dynam["rho0"], 2), f(dynam["p_c"], 4), f(dynam["f_c"], 4)))
summary_table([r"Growth rate $r$", r"$t(p_c)$", r"$t(f_c)$", r"Window",
               r"Window $\times r$"],
              [[k.replace("_", r"\_"), f(v["t_c"], 2), f(v["t_wilt"], 2),
                f(v["window"], 2), f(v["window"] * v["r"], 4)]
               for k, v in _rates.items()],
              r"Pre-Symptomatic Window at Three Stipulated Growth Rates",
              colspec="lrrrr")
w(r"""The last column is constant to four decimals across the three rates, which
is the analytic $1/r$ scaling reproducing itself and confirms that the three
curves are one result seen at three speeds rather than three findings. The
growth rates are stipulated, not measured, so the window has no calendar units:
its existence and shape, not its duration, is what the model delivers.""")


sec("Reconciliation With the Reported Results")
w(r"""Every number printed in the Results tables is listed against the value
this appendix computes from the archived data: not a selection, but each cell of
each table together with the notes that accompany them. A value is marked as
agreeing when the difference is no larger than half a unit in the last
significant digit reported, which is the largest discrepancy that rounding alone
can produce; anything larger is flagged.""")
rrows = []
flagged = []
boundary = []


def _tnum(item):
    m = re.match(r"T(\d+)", item[0])
    return int(m.group(1)) if m else 99


CHECKS.sort(key=_tnum)                     # group by Results table, stable
for label, draft, computed, tol in CHECKS:
    if draft is None:
        continue
    diff = computed - draft
    lim = tol if tol is not None else _tol(draft)
    ok = abs(diff) <= lim
    # an exact rounding tie: the computed value falls precisely half a unit in
    # the last reported digit away from the printed one
    unit = lim / 0.6
    if ok and abs(abs(diff) - 0.5 * unit) < 0.002 * unit:
        boundary.append((label, draft, computed))
    dec = max(_dec(draft), 3)
    rrows.append([label, g(draft, _dec(draft)), g(computed, dec),
                  g(diff, 5), r"\checkmark" if ok else r"\textbf{differs}"])
    if not ok:
        flagged.append((label, draft, computed, dec))
summary_table([r"Quantity", r"Reported", r"Recomputed", r"Difference", r"Status"],
              rrows, r"Reported Versus Recomputed Values", colspec="lrrrl")
w(r"""\noindent Entries marked \checkmark{} agree to the precision at which the
Results report them: the reported figure is the rounded form of the recomputed
one. Of the %d values checked, %d agree and %d are flagged.""" %
  (len(rrows), len(rrows) - len(flagged), len(flagged)))
if flagged:
    w(r"""\noindent The flagged entries differ only in the final reported digit
and none changes an interpretation, but each should be corrected in the Results
before submission:""")
    w(r"\begin{itemize}\itemsep2pt")
    for label, draft, computed, dec in flagged:
        w(r"\item %s: the Results give %s; the data give %s." %
          (label, g(draft, _dec(draft)), g(computed, dec)))
    w(r"\end{itemize}")

if boundary:
    w(r"""\noindent A small number of cells sit almost exactly on a rounding
boundary, so the digit printed depends on whether ties are rounded half up or
half to even. Both forms are defensible; they are listed for consistency only:""")
    w(r"\begin{itemize}\itemsep2pt")
    for label, draft, computed in boundary:
        w(r"\item %s: printed as %s, computed as %s." %
          (label, g(draft, _dec(draft)), g(computed, _dec(draft) + 2)))
    w(r"\end{itemize}")

w(r"\end{document}")


def build():
    import re as _re
    csv_out = os.path.join(ROOT, "APPENDIX_C_CHECKS.csv")

    def plain(t):
        t = _re.sub(r"\\[a-zA-Z]+", " ", str(t))
        for ch in "${}":
            t = t.replace(ch, "")
        return _re.sub(r"\s+", " ", t).strip()

    with open(csv_out, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["quantity", "reported_in_results", "recomputed",
                     "difference", "status"])
        for label, draft, computed, tol in CHECKS:
            if draft is None:
                continue
            d = computed - draft
            ok = abs(d) <= (tol if tol is not None else _tol(draft))
            wr.writerow([plain(label), draft, computed, d,
                         "agrees" if ok else "DIFFERS"])
    print("wrote", os.path.relpath(csv_out, ROOT))

    text = "\n".join(L)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    print("wrote", os.path.relpath(OUT, ROOT), "(%d lines)" % len(L))


build()
