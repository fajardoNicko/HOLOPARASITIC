# -*- coding: utf-8 -*-
r"""Part 7 of the Appendix C builder: the haustorial sink, the coupled
haustorial-density surface, hydraulic verification, the crop-edge screen, the
connectivity criterion, and damage locality."""

from __future__ import annotations


def sink(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    cav = C["cav"]
    setup = cav["setup"]
    sweep = cav["gradient_sweep_at_calibrated_Kh"]
    law = cav["patch_depression_law"]
    md = cav["margin_decomposition"]
    base = cav["baseline_control"]["min_interior_psi_MPa"]
    psi_cav = setup["psi_cavitation_default_MPa"]

    w(r"\section{The Calibrated Haustorial Sink Across the Swept Gradient}"
      r"\label{sec:sink}")
    w()
    w(r"""The sink is a conductance $K_{h}$ tying a patch of %d host nodes to a
fixed parasite reservoir, entering the solve through
Equations~\eqref{eq:kirchhoff} and~\eqref{eq:kh}. It was calibrated so that the
haustorium withdraws 20\%% of leaf throughput at an illustrative %.1f MPa
host--parasite gradient:""" % (setup["patch_size"],
                               C["rv"]["T4_sink"]["gradient_MPa"]))
    w(r"\begin{equation}")
    w(r"K_{h} = %s \quad\Longrightarrow\quad \text{diversion} = %s = %s\%%"
      % (num(setup["calibrated_K_h"], 6), num(setup["achieved_diversion"], 5),
         "%.2f" % (100 * setup["achieved_diversion"])))
    w(r"\end{equation}")
    w(r"""an error of %s percentage points against the target. The gradient is
illustrative: no primary holoparasite measurement was located, and the largest
directly measured parasite--host leaf gradient in the literature is
approximately 0.5 MPa. The gradient was then swept over 0--12 MPa at %d sampled
values (0.1 MPa apart to 3 MPa, 0.5 MPa apart thereafter) with $K_{h}$
fixed.""" % ("%.3f" % abs(100 * setup["achieved_diversion"] - 20.0),
             len(sweep)))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Hydraulic Behaviour of the Calibrated Haustorial Sink}}"
      r"\label{tab:sink}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{cccccc}")
    w(r"\toprule")
    w(r"Gradient (MPa) & $\psi_{\text{parasite}}$ & Min $\psi$ & Margin & "
      r"Flow diverted & Vessels embolised \\")
    w(r"\midrule")
    keep = {0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,
            10.0, 11.0, 12.0}
    for row in sweep:
        g = row["gradient_MPa"]
        if not any(abs(g - k) < 1e-9 for k in keep):
            continue
        mn = row["min_interior_psi_MPa"]
        w(r"%.1f & $-$%s & $-$%s & %s & %.1f\%% & %d \\"
          % (g, num(abs(row["psi_parasite_MPa"])), num(abs(mn)),
             C["sgn"](abs(psi_cav) - abs(mn)),
             100 * row["diversion_fraction"],
             row["embolised_by_threshold"]["-2.00"]))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    r15 = [r for r in sweep if abs(r["gradient_MPa"] - 1.5) < 1e-9][0]
    w(r"""\noindent \textit{Note.} Cavitation threshold $-2.0$ MPa;
transpirational boundary condition $-1.0$ MPa. Margin is the distance from the
network minimum to the threshold. The first row is the no-parasite baseline: with
no draw the minimum interior potential is $%s$ MPa, set by the terminal Dirichlet
condition. The diverted fraction rises with the gradient because the reservoir
deepens while $K_{h}$ is fixed, so 20\%% is specific to the illustrative
gradient.""" % num(base))
    w()
    w(r"\subsection{The Three Threshold-Independent Quantities}")
    w()
    share = md["parasite_share_of_total_margin_pct"]
    gap = md["stipulated_gap_PSI_LEAF_minus_PSI_CAVITATION_MPa"]
    gr_req = law["gradient_required_to_reach_PSI_CAVITATION_MPa"]
    onset = cav["cavitation_onset_gradient_by_threshold"]["-2.00"]
    check("Cavitation onset gradient at -2.00 MPa", 6.0, onset, 0.05)
    w(r"""\emph{(i) The parasite's own contribution to the field.} Against the
no-parasite baseline, and as a share of the total margin:""")
    steps(
        r"\Delta\psi_{\min} &= \psi_{\min}^{\text{sink}}"
        r" - \psi_{\min}^{\text{baseline}} = (%s) - (%s) = %s\ \text{MPa}"
        % (num(r15["min_interior_psi_MPa"], 5), num(base, 5),
           num(md["parasite_contribution_at_calibrated_Kh_and_1.5MPa_MPa"], 5)),
        r"\text{share} &= \frac{\lvert %s\rvert}{%s}\times 100 = %s\%%"
        % (num(md["parasite_contribution_at_calibrated_Kh_and_1.5MPa_MPa"], 5),
           num(gap, 3), "%.2f" % share),
    )
    w(r"""so the remaining %.3f MPa is the stipulated separation between the
boundary condition and the threshold: the margin is a property of the boundary
conditions far more than of the parasite.""" % gap)
    w()
    w(r"""\emph{(ii) The depression at the contact patch.} Because $K_{h}$ is
relative to each node's incident conductance
(Equation~\eqref{eq:kh}), the tapped node sits at a conductance-weighted average
of its neighbours and the reservoir with the reservoir's weight fixed at
$K_{h}/(1+K_{h})$ regardless of calibre, so the depression is linear in the
gradient with a slope independent of leaf architecture. Fitting the sweep:""")
    steps(
        r"\Delta\psi_{\text{patch}} &= a\,g + b, \qquad"
        r"a = %s,\quad b = %s,\quad \max\lvert\text{resid}\rvert = %s"
        % (num(law["slope_MPa_per_MPa_of_gradient"], 5),
           num(law["intercept_MPa"], 6),
           num(law["max_abs_residual_MPa"], 6)),
        r"\Delta\psi_{\text{patch}}(1.5) &= (%s)(1.5) %s %s = %s\ \text{MPa}"
        % (num(law["slope_MPa_per_MPa_of_gradient"], 5),
           "-" if law["intercept_MPa"] < 0 else "+",
           num(abs(law["intercept_MPa"]), 6),
           num(r15["delta_patch_psi_vs_baseline_MPa"], 5)),
    )
    w(r"""an order of magnitude larger than the network-minimum depression above.
The linearity is an arithmetic consequence of the sink parameterisation, not an
emergent property of venation topology.""")
    w()
    w(r"""\emph{(iii) The gradient required to reach the threshold.}
Extrapolating the patch law from the local host potential at the contact patch,
$\psi_{\text{host,local}} = %s$ MPa:""" % num(setup["psi_host_local_MPa"], 5))
    steps(
        r"g^{*} &= \frac{\psi_{\text{cav}} - \psi_{\text{host,local}}}{a}"
        r" = \frac{(%s) - (%s)}{%s} = \frac{%s}{%s} \approx %s\ \text{MPa}"
        % (num(psi_cav, 2), num(setup["psi_host_local_MPa"], 5),
           num(law["slope_MPa_per_MPa_of_gradient"], 5),
           num(psi_cav - setup["psi_host_local_MPa"], 5),
           num(law["slope_MPa_per_MPa_of_gradient"], 5), "%.2f" % gr_req),
    )
    w(r"""The sweep itself locates the first embolism at %.1f MPa, the figure
quoted in the Results; the two agree to within one sweep step above 3 MPa. Either
way the requirement is more than an order of magnitude above the largest measured
gradient. Threshold sensitivity is in Section~\ref{sec:sensitivity}.""" % onset)
    w()


def surface(C):
    w, num, check = C["w"], C["num"], C["check"]
    ss = C["ss"]
    w(r"\section{The Coupled Haustorial-Density Surface}\label{sec:surface}")
    w()
    w(r"""This surface reports a different quantity from every other threshold in
this appendix: the critical fraction of nodes \emph{bearing a haustorium} under
the coupled model, in which a node is removed only if the solve of
Equation~\eqref{eq:laplacian} puts its potential below the cavitation threshold.
It is not comparable with Table~\ref{tab:pcsummary}. Computed on the
cohort-calibrated mesh ($N = %s$, $\langle k\rangle$ held at %s by tuning mesh
fraction, the $D$ axis realised at constant $N$ by tuning length ratio and then
measured), at %s trials per cell over %d density points, with the sink axis
anchored on the calibrated $K_{h} = %s$.""" %
      (C["mint"](ss["N"]), num(ss["mean_degree_measured"][0], 4),
       "{:,}".format(ss["n_trials_per_cell"]), ss["n_densities"],
       num(ss["calibrated_k_h"], 4)))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Critical Haustorial Density by Sink Strength and "
      r"Fractal Dimension}}\label{tab:surface}")
    w(r"\small\setlength{\tabcolsep}{6pt}")
    cols = [1, 2, 3, 4, 6, 8]
    w(r"\begin{tabular}{c%s}" % ("c" * len(cols)))
    w(r"\toprule")
    w(r"$D$ & " + " & ".join(r"$%d\times K_{h}$" % m for m in cols) + r" \\")
    w(r"\midrule")
    for d in ss["D_measured"]:
        cells = []
        for m in cols:
            hit = [c for c in ss["cells"]
                   if abs(c["D"] - d) < 1e-9
                   and c["k_h_multiple_of_calibrated"] == m]
            cells.append("none" if not hit or hit[0]["p_c_haustorial_density"]
                         is None else num(hit[0]["p_c_haustorial_density"], 4))
        w(r"%s & %s \\" % (num(d, 4), " & ".join(cells)))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    tem = ss["threshold_exists_by_multiple"]
    check("Smallest Kh multiple with any threshold",
          ss["smallest_k_h_multiple_with_a_threshold"], 2, 0.5)
    w(r"""\noindent \textit{Note.} ``none'' records that the collapse probability
never reached .50 at any haustorial density in $[0,1]$, so
Equation~\eqref{eq:crossing} returns no value, not that the threshold is
large. That is the outcome in %d of %d rows at the calibrated strength: at the
strength the literature calibration implies, no network in the grid reaches the
collapse criterion at any density. A threshold first appears at $2\times$, and
only in the lowest-$D$ row; at $3\times$ it appears in every row, then falls
steeply (%s at $3\times$ to %s at $8\times$ in that row) as each haustorium
becomes strong enough to embolise its own neighbourhood.""" %
      (tem["1"]["n_rows"] - tem["1"]["n_rows_with_threshold"],
       tem["1"]["n_rows"],
       num([c for c in ss["cells"]
            if abs(c["D"] - ss["D_measured"][0]) < 1e-9
            and c["k_h_multiple_of_calibrated"] == 3][0]
           ["p_c_haustorial_density"], 4),
       num([c for c in ss["cells"]
            if abs(c["D"] - ss["D_measured"][0]) < 1e-9
            and c["k_h_multiple_of_calibrated"] == 8][0]
           ["p_c_haustorial_density"], 4)))
    w()


def verification(C):
    w, num, check = C["w"], C["num"], C["check"]
    rho_, pval = C["rho"], C["pval"]
    T11 = C["T11"]
    hr = T11["hydraulic_resistance"]
    kl = C["frc"]["kleaf_cohorts"]
    rcs = C["rcs"]

    w(r"\section{Hydraulic Verification and the Independent Comparison}"
      r"\label{sec:verification}")
    w()
    w(r"""Two distinct things are established. That the solver implements
Equation~\eqref{eq:hp} correctly is a \emph{verification}; whether the model
predicts an independently measured quantity is a \emph{validation}, which the
data support only weakly.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Model Verification and Comparison Summary}}"
      r"\label{tab:verification}")
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
    w(r"Worst $|$median ratio $-\,1|$ & $%.1f \times 10^{-8}$ & "
      r"$1\times10^{-6}$ \\" % (hr["worst_abs_median_ratio_minus_1"] * 1e8))
    w(r"Minimum per-leaf Pearson $r$ on logs & %s & --- \\"
      % num(hr["min_pearson_log_r"], 6))
    w(r"Wrong-exponent control, median $r$ & %s & --- \\"
      % num(T11["wrong_exponent_control"], 4))
    w(r"Measured $K_{\text{leaf}}$, Spearman $\rho$ & %s ($p$ %s) & --- \\"
      % (rho_(T11["kleaf"]["rho"]), pval(T11["kleaf"]["p"])))
    w(r"Crop-edge screen, leaves within tolerance & %d of %d & --- \\"
      % (T11["boundary"]["n_within"], T11["boundary"]["n"]))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Kleaf rho", T11["kleaf"]["rho"],
          kl["manuscript_cohort"]["spearman_r4"][0])
    w(r"""\noindent \textit{Note.} One leaf was excluded from the resistance
comparison for carrying fewer than 50 usable veins, hence %d rather than 120.
Because the deposit's resistance column is itself defined as $\ell/r^{4}$ (the
convention Equation~\eqref{eq:hp} implements), the comparison verifies
implementation rather than validating physics. Agreement is to roughly one part
in $10^{7}$, tighter than any physical measurement; and a deliberately wrong
exponent still gives a median correlation of %s, so it is the tightness and not
the correlation that carries the verification.""" %
      (hr["n_leaves"], num(T11["wrong_exponent_control"], 4)))
    w()
    mc, al = kl["manuscript_cohort"], kl["all_leaves_cohort"]
    w(r"""Modelled whole-network conductance from
Equation~\eqref{eq:kleaf} against the deposit's measured leaf hydraulic
conductance is weak and non-significant:""")
    w(r"\begin{equation}")
    w(r"\rho = %s,\quad p = %s,\quad n = %d,\quad "
      r"95\%%\ \text{CI}\ [%s,\ %s]"
      % (num(mc["spearman_r4"][0], 4), num(mc["spearman_r4"][1], 4),
         mc["n"], num(mc["ci95_r4"][0], 4), num(mc["ci95_r4"][1], 4)))
    w(r"\end{equation}")
    w(r"""The interval spans zero, so the check is underpowered rather than
negative. Three variants give the same answer: unscreened, $\rho = %s$,
$p = %s$, $n = %d$; under the alternative $\ell/r^{2}$ convention,
$\rho = %s$ on %d leaves; and the two conventions agree at $\rho = %s$ across %d
leaves despite a median ratio of %s between them. The percolation results are
untouched, because the removal simulation operates on the unweighted adjacency
and unweighted centralities, so no threshold in this appendix depends on the
conductance convention.""" %
      (num(al["spearman_r4"][0], 4), num(al["spearman_r4"][1], 4), al["n"],
       num(rcs["kleaf_validation"]["spearman_r2_vs_measured"][0], 4),
       rcs["kleaf_validation"]["n"],
       num(rcs["agreement_between_conventions"]["spearman_r4_vs_r2"], 4),
       rcs["n_leaves"],
       num(rcs["agreement_between_conventions"]["median_ratio_r4_over_r2"], 5)))
    w()


def boundary(C):
    w, num, check = C["w"], C["num"], C["check"]
    b = C["prov"]["boundary_check"]
    w(r"\section{The Crop-Edge Boundary Screen}\label{sec:boundary}")
    w()
    check("Boundary within tolerance", 105, b["n_within_tolerance"], 0.5)
    w(r"""Because most source files are crop windows, a tracing can be cut by the
window edge, severing veins and lowering mean degree artificially. Two tolerances
were applied to all %d traced networks: the fraction of terminals on the window
edge must not exceed %s, and the mean-degree shift when window cut-ends are
stripped must not exceed %s. Of the %d, %d fell inside both and %d did not; the
%d outside are the smallest and most heavily windowed tracings. None is in the
percolation cohort, whose inclusion rule contains both tolerances; %d remain in
the looser enhancement cohort (%s), one of which, %s, is the largest-gain entry
of Table~\ref{tab:gainers}.""" %
      (b["n"], num(b["tolerances"]["boundary_terminal_frac"], 2),
       num(b["tolerances"]["mean_degree_shift"], 2), b["n"],
       b["n_within_tolerance"], b["n_outside_tolerance"],
       b["n_outside_tolerance"],
       len(b["outside_tolerance_but_in_enhancement_cohort"]),
       ", ".join(C["esc"](x) for x
                 in b["outside_tolerance_but_in_enhancement_cohort"]),
       C["esc"](b["outside_tolerance_but_in_enhancement_cohort"][1])))
    w()


def criterion(C):
    w, num, check = C["w"], C["num"], C["check"]
    rho_ = C["rho"]
    cl = C["cl"]
    crit = cl["criterion_comparison"]
    assoc = cl["associations_under_each_criterion"]
    rc = cl["replication_check_vs_archive"]

    w(r"\section{Robustness to the Connectivity Criterion}\label{sec:criterion}")
    w()
    w(r"""Earlier venation-robustness work scores connectivity to a source vein
rather than on the giant component of Equation~\eqref{eq:criterion}. Both were
scored here on identical removal draws across all %d cohort networks, so the
comparison is exactly paired. The re-implementation reproduces the archived
thresholds at $\rho = %s$ with a median absolute difference of %s.""" %
      (cl["n"], num(rc["spearman_gcc_vs_archived"], 4),
       num(rc["median_abs_difference"], 4)))
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Threshold and Associations Under Two Connectivity "
      r"Criteria}}\label{tab:criterion}")
    w(r"\small\setlength{\tabcolsep}{5pt}")
    w(r"\begin{tabular}{lccccc}")
    w(r"\toprule")
    w(r"Criterion & $Mdn$ $p_{c}$ & $IQR$ & $\rho$ with $\langle k\rangle$ & "
      r"$\rho$ with loop fraction & $\rho$ with $D$ \\")
    w(r"\midrule")
    w(r"Giant component & %s & %s--%s & %s & %s & %s \\"
      % (num(crit["median_gcc"]), num(crit["iqr_gcc"][0]),
         num(crit["iqr_gcc"][1]),
         rho_(assoc["gcc"]["spearman_x_mean_degree"][0]),
         rho_(assoc["gcc"]["spearman_x_loop_fraction"][0]),
         rho_(assoc["gcc"]["spearman_x_D"][0])))
    w(r"Source-anchored & %s & %s--%s & %s & %s & %s \\"
      % (num(crit["median_source"]), num(crit["iqr_source"][0]),
         num(crit["iqr_source"][1]),
         rho_(assoc["source_anchored"]["spearman_x_mean_degree"][0]),
         rho_(assoc["source_anchored"]["spearman_x_loop_fraction"][0]),
         rho_(assoc["source_anchored"]["spearman_x_D"][0])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Criterion Spearman agreement", 0.912, crit["spearman"], 0.001)
    w(r"""\noindent \textit{Note.} $n = %d$, identical draws; the source node is
the documented widest-vein rule and is protected from removal. The
source-anchored threshold is lower by a median paired difference of %s and is
lower in %d of %d networks, as expected, since requiring connection to a specific
node is strictly stronger than requiring a large component anywhere. The two
nevertheless rank networks almost identically ($\rho = %s$, $r = %s$) and every
substantive association is preserved, so the choice of criterion does not change
the conclusions.""" %
      (cl["n"], C["sgn"](crit["median_paired_difference_source_minus_gcc"]),
       crit["n_source_lower"], cl["n"], num(crit["spearman"], 4),
       num(crit["pearson"], 4)))
    w()


def locality(C):
    w, steps, num, check = C["w"], C["steps"], C["num"], C["check"]
    rho_, pval = C["rho"], C["pval"]
    cl = C["cl"]
    loc = cl["locality_comparison"]
    assoc = cl["associations_under_each_criterion"]

    w(r"\section{Effect of Localised Damage}\label{sec:locality}")
    w()
    w(r"""Uniform removal disperses damage; a haustorial lesion or necrotic patch
is spatially contiguous. Two localised protocols were run at \emph{matched
realised removed fractions}, so the horizontal axis is identical to the dispersed
case: a single lesion removing the nodes nearest a random centre, and ten
simultaneous lesions from ten random centres.""")
    w()
    w(r"\begin{table}[H]")
    w(r"\centering")
    w(r"\caption{\textit{Fragmentation Threshold Under Alternative Damage "
      r"Geometries}}\label{tab:locality}")
    w(r"\small\setlength{\tabcolsep}{4pt}")
    w(r"\begin{tabular}{lccccccc}")
    w(r"\toprule")
    w(r"Damage geometry & $Mdn$ $p_{c}$ & $IQR$ & Paired diff. & Ratio & "
      r"$\rho$ with $\langle k\rangle$ & $p$ & $\rho$ with $D$ \\")
    w(r"\midrule")
    f1 = loc["median_disc1"] / loc["median_random_gcc"]
    f10 = loc["median_disc10"] / loc["median_random_gcc"]
    w(r"Dispersed & %s & %s--%s & --- & 1.00 & %s & %s & %s \\"
      % (num(loc["median_random_gcc"]),
         num(cl["criterion_comparison"]["iqr_gcc"][0]),
         num(cl["criterion_comparison"]["iqr_gcc"][1]),
         rho_(assoc["gcc"]["spearman_x_mean_degree"][0]),
         pval(assoc["gcc"]["spearman_x_mean_degree"][1]),
         rho_(assoc["gcc"]["spearman_x_D"][0])))
    w(r"One lesion & %s & %s--%s & $+$%s & %s & %s & %s & %s \\"
      % (num(loc["median_disc1"]), num(loc["iqr_disc1"][0]),
         num(loc["iqr_disc1"][1]),
         num(loc["median_paired_difference_disc1_minus_random"], 3),
         "%.2f" % f1, rho_(assoc["disc1"]["spearman_x_mean_degree"][0]),
         pval(assoc["disc1"]["spearman_x_mean_degree"][1]),
         rho_(assoc["disc1"]["spearman_x_D"][0])))
    w(r"Ten lesions & %s & %s--%s & $+$%s & %s & %s & %s & %s \\"
      % (num(loc["median_disc10"]), num(loc["iqr_disc10"][0]),
         num(loc["iqr_disc10"][1]),
         num(loc["median_paired_difference_disc10_minus_random"], 3),
         "%.2f" % f10, rho_(assoc["disc10"]["spearman_x_mean_degree"][0]),
         pval(assoc["disc10"]["spearman_x_mean_degree"][1]),
         rho_(assoc["disc10"]["spearman_x_D"][0])))
    w(r"\bottomrule")
    w(r"\end{tabular}")
    w(r"\end{table}")
    w()
    check("Locality median disc1", 0.4951, loc["median_disc1"])
    check("Locality median disc10", 0.4511, loc["median_disc10"])
    steps(
        r"\frac{\tilde{p}_{\text{1 lesion}}}{\tilde{p}_{\text{dispersed}}}"
        r" &= \frac{%s}{%s} = %s, \qquad"
        r"\frac{\tilde{p}_{\text{10 lesions}}}{\tilde{p}_{\text{dispersed}}}"
        r" = \frac{%s}{%s} = %s"
        % (num(loc["median_disc1"]), num(loc["median_random_gcc"]),
           "%.2f" % f1, num(loc["median_disc10"]),
           num(loc["median_random_gcc"]), "%.2f" % f10),
    )
    w(r"""\noindent \textit{Note.} $n = %d$, identical draws, matched realised
fractions. The paired-difference column is the median of the per-network
differences and is therefore not the difference of the two medians (%s against %s
for the single lesion); the paired form is the one the Wilcoxon test of
Section~\ref{sec:comparisons} operates on. A localised lesion was less damaging
than dispersed removal in %d of %d networks for both protocols, so uniform
removal is a conservative abstraction and every threshold in
Tables~\ref{tab:pcsummary} and~\ref{tab:reference} is a lower bound. The
architectural relationship, however, does not survive the change in geometry:
connectivity ceases to predict the threshold under a single lesion and is weak
and non-significant under ten, while $D$ retains a moderate association under the
multi-lesion protocol. The principal architectural result is therefore specific
in scope to \emph{dispersed} damage.""" %
      (cl["n"], num(loc["median_paired_difference_disc1_minus_random"], 4),
       num(loc["median_disc1"] - loc["median_random_gcc"], 4),
       cl["n"] - loc["n_disc1_lower_than_random"], cl["n"]))
    w()
