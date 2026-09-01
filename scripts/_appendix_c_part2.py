# -*- coding: utf-8 -*-
r"""Part 2 of the Appendix C builder: the measurement and simulation engine."""

from __future__ import annotations


def engine(C):
    w, steps, num = C["w"], C["steps"], C["num"]
    w(r"\section{How Each Measured Quantity Is Produced}\label{sec:engine}")
    w()
    w(r"""Five quantities are produced by a procedure rather than read off the
data. Their definitions are given here because the arithmetic in later sections
takes their outputs as input.""")
    w()

    # ---- threshold engine -------------------------------------------------
    w(r"\subsection{Critical Removed Fraction}\label{sec:pcengine}")
    w()
    w(r"""\emph{Sweep.} Removal intensities $\rho$ are laid out on a grid over
$[0,\rho_{\max}]$, with a fixed number of independent trials at each. Under
uniform removal each node is deleted independently with probability $\rho$. Under
weighted removal each node carries a mean-preserving weight $w_{i}$ (its degree
or betweenness divided by the network mean of that quantity) and is deleted
with probability""")
    w(r"\begin{equation}\label{eq:clip}")
    w(r"p_{i} = \min(\rho\,w_{i},\,1)")
    w(r"\end{equation}")
    w(r"""The clip at unity makes the nominal $\rho$ and the realised removed
fraction diverge for heavy-tailed weights (Section~\ref{sec:concentration}); for
uniform and degree weights no node is clipped near the threshold, so the two
coincide there.""")
    w()
    w(r"""\emph{Collapse criterion.} The surviving subgraph is decomposed into
connected components and the trial scored as a collapse when""")
    w(r"\begin{equation}\label{eq:criterion}")
    w(r"\lvert \text{GCC} \rvert < 0.50 \times N_{0}")
    w(r"\end{equation}")
    w(r"""with $N_{0}$ the undamaged node count. The component is the largest
anywhere in the survivor set, not one anchored to a source vein; the
source-anchored alternative is scored on the same draws in
Section~\ref{sec:criterion}. This is a half-size criterion: the fraction at which
the giant component vanishes entirely, written $f_{c}$, is a larger and different
quantity used only in Sections~\ref{sec:size} and~\ref{sec:dynamics}.""")
    w()
    w(r"""\emph{Estimate.} A logistic regression is fitted to every individual
$(\rho,\,\text{outcome})$ pair rather than to the aggregated proportions,""")
    w(r"\begin{equation}\label{eq:logit}")
    w(r"P(\text{collapse}\mid\rho) = \frac{1}{1+e^{-(b+w\rho)}}")
    w(r"\end{equation}")
    w(r"""and the threshold is its inflection point,""")
    w(r"\begin{equation}\label{eq:pcdef}")
    w(r"P = 0.50 \iff b + w\,p_{c} = 0 \iff p_{c} = -\frac{b}{w}")
    w(r"\end{equation}")
    w(r"""Fitting at trial level lets the estimate fall between swept density
points and makes its precision a function of the trial budget rather than of the
grid spacing. Where the inflection falls outside $[0,1]$ the estimate is replaced
by the interpolated empirical crossing,""")
    w(r"\begin{equation}\label{eq:crossing}")
    w(r"p_{c} = \rho_{i-1} + (0.50-P_{i-1})\,"
      r"\frac{\rho_{i}-\rho_{i-1}}{P_{i}-P_{i-1}}")
    w(r"\end{equation}")
    w(r"""where $i$ indexes the first density at which the observed proportion
reaches one half. No threshold is reported when the proportion never reaches one
half in the swept range; that is what produces the empty cells of
Section~\ref{sec:surface}.""")
    w()
    w(r"""\emph{Interval.} Individual trials are resampled with replacement, the
sigmoid refitted, and the 2.5th and 97.5th percentiles reported. The construction
is audited in Section~\ref{sec:budgets}. Where two conditions are evaluated on
one network under a common sequence of draws, their Monte Carlo errors cancel
from the paired difference; this applies to Sections~\ref{sec:thresholds},
\ref{sec:enhancement}, \ref{sec:criterion} and~\ref{sec:locality}.""")
    w()

    # ---- fractal dimension ------------------------------------------------
    w(r"\subsection{Box-Counting Fractal Dimension}")
    w()
    w(r"""Points are sampled densely along every edge, normalised into the unit
square with aspect ratio preserved, and the number of occupied boxes $N(k)$
counted at each of twelve grid resolutions from 16 to 1{,}024 boxes per axis.
For a fractal object""")
    w(r"\begin{equation}\label{eq:box}")
    w(r"N(\varepsilon) \sim \varepsilon^{-D}, \qquad \varepsilon = 1/k")
    w(r"\end{equation}")
    w(r"""so $\log N = D\log k + \text{const}$ and $D$ is the least-squares slope
of $\log N$ on $\log k$. The coarse end of the ladder is excluded because on a
finite object it lies in the saturated regime, where the apparent dimension tends
to two. The same window is applied to empirical and synthetic networks. Two
limits follow: on a cropped tracing the estimator measures the window as much as
the leaf, which produces the $D$--size correlation of
Section~\ref{sec:predictors}; and on the generator it saturates near 1.81, which
bounds the coverage of Section~\ref{sec:grid}.""")
    w()

    # ---- loop fraction ----------------------------------------------------
    w(r"\subsection{Loop Fraction, Bridge Fraction, Cycle Rank, Mean Degree}")
    w()
    w(r"""An edge is a bridge when its removal increases the number of connected
components, that is, when it lies on no cycle.""")
    w(r"\begin{equation}\label{eq:loopfrac}")
    w(r"\text{loop fraction} = \frac{E - \lvert\text{bridges}\rvert}{E}, \qquad"
      r"\text{bridge fraction} = \frac{\lvert\text{bridges}\rvert}{E}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:cyclerank}")
    w(r"c = E - N + \#\text{components}")
    w(r"\end{equation}")
    w(r"\begin{equation}\label{eq:meandeg}")
    w(r"\langle k\rangle = \frac{2E}{N}")
    w(r"\end{equation}")
    w(r"""The two fractions sum to unity by construction. The definition is
construction-independent: an edge laid down in a spanning tree and later closed
into a circuit counts as a loop edge, whereas a tag-based count of added
anastomoses would not. Equation~\eqref{eq:cyclerank} enters only the
percolation-cohort inclusion rule. Equations~\eqref{eq:loopfrac}
and~\eqref{eq:meandeg} are two readings of one edge-to-node budget, which is why
they are near-perfectly rank-correlated (Section~\ref{sec:descassoc}) and why
only one of them enters the regression of Section~\ref{sec:predictors}.""")
    w()

    # ---- hydraulics -------------------------------------------------------
    w(r"\subsection{Hydraulic Model}")
    w()
    w(r"""Each vein segment is a cylindrical conduit obeying Hagen--Poiseuille
flow, with $\ell$ its length and $r$ its radius from the calibrated tracing:""")
    w(r"\begin{equation}\label{eq:hp}")
    w(r"R = \frac{8\eta \ell}{\pi r^{4}} \propto \frac{\ell}{r^{4}},"
      r" \qquad g = \frac{1}{R} \propto \frac{r^{4}}{\ell}")
    w(r"\end{equation}")
    w(r"""Conservation of volume at every interior node gives Kirchhoff's law on
the conductance-weighted graph, the first term network flow and the second the
haustorial leak:""")
    w(r"\begin{equation}\label{eq:kirchhoff}")
    w(r"\sum_{j} g_{ij}\,(\psi_{i}-\psi_{j})"
      r" + h_{i}\,(\psi_{i}-\psi_{\text{parasite}}) = 0")
    w(r"\end{equation}")
    w(r"""Collected over the free nodes this is the sparse system""")
    w(r"\begin{equation}\label{eq:laplacian}")
    w(r"\left(L_{ff} + \operatorname{diag}(h_{f})\right)\psi_{f}"
      r" = -L_{fd}\,\psi_{d} + h_{f}\,\psi_{\text{parasite}}")
    w(r"\end{equation}")
    w(r"""with $L$ the Laplacian of the conductances, $f$ the free nodes and $d$
the Dirichlet-fixed nodes: the root at the source potential, every terminal at
the transpirational leaf potential. The haustorial conductance is relative to the
tapped node's own incident conductance,""")
    w(r"\begin{equation}\label{eq:kh}")
    w(r"h_{i} = K_{h}\sum_{j} g_{ij}")
    w(r"\end{equation}")
    w(r"""so a haustorium taps a vessel in proportion to its calibre. This is what
makes the contact-patch depression linear in the host--parasite gradient with a
slope independent of leaf architecture (Section~\ref{sec:sink}). A node embolises
and is deleted when its solved potential falls below the cavitation threshold;
root and terminal nodes are held at their boundary values and are never scored as
embolised. Whole-network modelled conductance is the flow entering the root per
unit potential drop in the undamaged solve,""")
    w(r"\begin{equation}\label{eq:kleaf}")
    w(r"K_{\text{model}} = \frac{\sum_{j \in \mathcal{N}(\text{root})}"
      r" g_{\text{root},j}\,(\psi_{\text{root}}-\psi_{j})}"
      r"{\lvert\psi_{\text{source}}-\psi_{\text{leaf}}\rvert}")
    w(r"\end{equation}")
    w(r"""a xylem-only quantity containing no outside-xylem resistance.""")
    w()

    # ---- enhancement construction -----------------------------------------
    w(r"\subsection{Reticulation-Enhancement Construction}")
    w()
    w(r"""The enhanced arm is the same network with edges added. Candidate
connections are drawn from the network's own open vein endings and joined to
close areoles, until mean degree reaches the cohort ceiling
$\langle k\rangle = %.3f$, the 90th percentile of the percolation cohort's own
mean-degree distribution, so the manipulation interpolates within the measured
range. The node set is never altered, so no part of the threshold difference can
be a size effect, and both arms consume an identical sequence of removal draws.
By Equation~\eqref{eq:meandeg}, raising mean degree from
$\langle k\rangle_{0}$ to $\langle k\rangle^{*}$ on a fixed node set requires""" %
      C["T9"]["ceiling_mean_degree"])
    w(r"\begin{equation}\label{eq:loopsadded}")
    w(r"\Delta E = \frac{N}{2}\left(\langle k\rangle^{*}"
      r" - \langle k\rangle_{0}\right)")
    w(r"\end{equation}")
    w(r"""additional edges, which is the loops-added column of
Table~B9 of Appendix~B. A network already at or above the ceiling receives
none, its arms are identical, and its difference is exactly zero.""")
    w()
    tgt = C["by_name"].get("Met_dav")
    if tgt is not None:
        N_ = float(tgt["n_nodes"])
        k0 = float(tgt["mean_degree"])
        kc = float(C["T9"]["ceiling_mean_degree"])
        pred = 0.5 * N_ * (kc - k0)
        actual = float(tgt["loops_added"])
        w(r"""\noindent Worked instance, for the network shown as a
before-and-after pair in the Results:""")
        steps(
            r"\Delta E &= \frac{N}{2}\left(\langle k\rangle^{*}"
            r" - \langle k\rangle_{0}\right)",
            r"&= \frac{%s}{2}\left(%s - %s\right)"
            % (C["mint"](N_), num(kc, 3), num(k0, 4)),
            r"&= %s \times %s" % (C["mint"](round(N_ / 2.0)), num(kc - k0, 4)),
            r"&= %s" % C["mint"](round(pred)),
        )
        w(r"""against %s edges actually added, the shortfall being integer
rounding and the exhaustion of admissible areole closures in a planar tracing.
The construction adds only connections a planar leaf could physically make, which
is why the gain it produces is the smallest of the reticulation levers
examined.""" % "{:,}".format(int(actual)))
    w()
