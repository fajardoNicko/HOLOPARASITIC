# Revised Manuscript Sections — Introduction, Materials and Methods, Results

**Source of authority:** `FINAL_RESOLUTION_PASS.md`, with `SECOND_PASS_AUDIT.md` and
`DEEP_RRL_EVIDENCE_PACK.md` behind it. No analysis was rerun and no numerical result was altered. The
title is unchanged. All numerical values are transcribed from the archived result files and the
existing `RESULTS_REVISED.docx`.

---

## Numbering crosswalk (read this first)

Figures are numbered continuously across the manuscript, so Figure 1 is the Methods pipeline figure
and the Results figures run 2–14. This is one higher than the internal numbering in
`RESULTS_REVISED.docx`, which numbered the Results figures 1–13 in isolation.

| New no. | Content | Source file | Old Results no. | Section |
|---|---|---|---|---|
| Figure 1 | Overall software pipeline | (Methods figure) | — | Methods |
| Figure 2 | Representative empirical host network | `figures/graph_real_Cis_ant.png` | 1 | Results §1 |
| Figure 3 | Representative calibrated synthetic mesh | `figures/graph_synthetic.png` | 2 | Results §1 |
| Figure 4 | Collapse curve, random removal | `figures/sigmoid.png` | 3 | Results §2 |
| Figure 5 | Collapse curve, degree-weighted removal | `figures/sigmoid_targeted.png` | 4 | Results §2 |
| Figure 6 | Progressive fragmentation of the GCC | `figures/collapse_montage.png` | 5 | Results §2 |
| Figure 7 | Host water-potential field under the calibrated sink | `figures/sink_demo.png` | 6 | Results §6 |
| Figure 8 | Threshold versus architectural predictors | `figures/cohort_pc_predictors.png` | 7 | Results §3 |
| Figure 9 | Coverage of the synthetic grid | `figures/calibration_grid.png` | 8 | Results §3 |
| Figure 10 | Change in threshold per network after enhancement | `figures/cohort_suggested.png` | 9 | Results §5 |
| Figure 11 | A representative network before and after enhancement | `figures/methodology/fig_realsuggested_Met_dav.png` | 10 | Results §5 |
| Figure 12 | Critical haustorial density surface | `figures/sink_surface.png` | 11 | Results §7 |
| Figure 13 | Size dependence of the threshold at fixed architecture | `figures/finite_size_fixedD.png` | 12 | Results §7 |
| Figure 14 | Modelled separation between fragmentation and total loss | `figures/dynamics.png` | 13 | **Supplementary** |

Tables 1–13 keep their existing numbers. Tables 14 and 15 are the two tables that appear unnumbered in
the current draft (the fixed-architecture size sweep and the modelled-separation table); they are given
numbers here. **Table 16 is new** and carries the final-pass robustness analyses; it introduces no new
experiment, only values already produced by `data/criterion_and_locality.json`,
`data/cavitation_sensitivity.json`, `data/second_pass_audit.json` and
`data/resistance_convention_sensitivity.json`.

**One deviation from the section plan, flagged deliberately.** The plan assigned Figure 4 to Results
§1. By content, Figure 4 is the random-removal collapse curve, which belongs with §2 ("Percolation
Thresholds Under Simulated Vascular Damage") — §2 also cannot be written as instructed ("random and
degree-weighted removal") without it. Figure 4 has therefore been placed in §2, and §1 carries
Figures 2 and 3, the two representative-network panels. Nothing has been removed.

---
---

# CHAPTER I — INTRODUCTION

Vascular networks in plants are specialised transport systems composed of xylem and phloem tissues that
move water, minerals, and photosynthetic products throughout the organism (Prasad & Roy, 2020). The
xylem conducts water and dissolved minerals upward through dead, lignified conduits, while the phloem
distributes sugars and other organic compounds through living sieve elements. Beyond transport, these
networks display highly organised branching architectures that combine efficiency with resilience
against localised damage (Katifori et al., 2010). In a leaf, repeated branching produces a hierarchical
skeleton of major veins, while reticulation — the closing of minor veins into anastomosing loops —
overlays that skeleton with alternative routes. The functional consequence is that the loss of an
individual conduit need not sever supply to the tissue beyond it, because flow can be redirected around
the break. Cavitation, the abrupt formation of a gas void in xylem sap under tension, and the resulting
embolism that blocks the conduit (Liu et al., 2023; Bittencourt et al., 2018), remove conducting
elements one at a time; whether such losses accumulate into a system-level failure therefore depends
not only on how many elements are lost but on how the surviving elements are wired together.

Because the vascular system consists of conducting elements joined at discrete junctions, a leaf
venation network can be represented directly as a graph, with vein junctions as nodes and vein segments
as edges (Ronellenfitsch et al., 2015). This representation makes the architecture measurable. Mean
degree, ⟨k⟩ = 2E/N, gives the average number of vein segments meeting at a junction and, in a
predominantly planar venation, rises from near two in a sparsely reticulate leaf toward three as more
areoles close; it is the primary index of reticulation used here. The loop fraction, the proportion of
edges lying on at least one cycle, measures the same reticulation axis from the complementary
direction, its complement being the bridge fraction — the proportion of veins whose individual loss
would disconnect part of the network. The giant connected component (GCC) is the largest set of
junctions still mutually reachable through surviving segments, and its size is the natural order
parameter for describing how intact a damaged network remains. Fractal dimension D, estimated by
box-counting, describes how completely the venation fills space across scales and is treated here as a
coarse geometric descriptor complementary to, rather than a substitute for, the connectivity measures
(Muraleedharan et al., 2023).

Percolation theory provides the formal framework for asking how much element loss such a network can
absorb. It describes how large interconnected systems undergo an abrupt transition from a connected to
a fragmented state once the proportion of functioning elements falls below a critical value
(Dorogovtsev et al., 2008). Applied to a venation graph, junctions are removed and the surviving
network is examined for a spanning connected cluster. The quantity estimated in this study is the
**critical removed fraction, p_c** — the fraction of junctions removed at which the giant connected
component falls below half its undamaged size with probability 0.50. Because the threshold of a finite,
irregular network cannot be obtained in closed form, it is estimated by Monte Carlo simulation (Newman
& Ziff, 2001). Network-robustness theory further predicts that the answer depends on *where* loss
falls: systems can absorb uniformly scattered failure yet fragment sooner when loss is concentrated on
structurally important elements (Albert et al., 2000; Callaway et al., 2000). It is important to be
precise about what this quantity is. p_c is computed on the unweighted graph; it is a **structural
fragmentation threshold**, not a measurement of hydraulic conductance, water potential, or cavitation,
and it is not interconvertible with physiological indices such as percentage loss of conductivity or
P50.

Holoparasitic weeds provide a biologically concrete reason to ask how much vascular disruption a host
network can tolerate. Species of *Cuscuta* and related genera attach to host tissue and act as a
hydraulic sink, extracting water and solutes directly from host vascular pathways and contributing to
severe yield losses in susceptible dicotyledonous crops (Westwood et al., 2010; Casadesus &
Munné-Bosch, 2021). Field and glasshouse studies establish that host physiological decline under
parasitism can begin well before visible signs appear, with reported lead times ranging from
approximately twenty days in *Orobanche*-infected sunflower to roughly fifty days in
*Cuscuta*-infected hosts (Cochavi et al., 2017; Shen et al., 2007); the documented signatures of that
window, however, are optical, thermal, growth-related and carbon-related rather than hydraulic. The
parasite is therefore treated in this study as a biologically motivated example of localised hydraulic
withdrawal and distributed vascular disruption, and is modelled as a hydraulic boundary condition
analysed in parallel with the structural analysis. No claim is made that the present model demonstrates
a pre-symptomatic physiological window, predicts symptoms, or provides an early-warning signal.

Damage tolerance of leaf venation has been examined before, and the relevant prior work must be stated
plainly. Katifori et al. (2010) showed theoretically that loops become the optimal configuration for a
transport network precisely when it must tolerate damage or fluctuating load, so reticulation is
expected on first principles to buy robustness. Price and Weitz (2014), analysing 339 cleared leaves,
removed vein segments at random and found that structural redundancy indices — meshedness in
particular — predicted the fraction of the network remaining connected to the petiole, at only a modest
material and conductance cost. Mander and Williams (2024) removed elements from real fossil and extant
venation networks, framed the analysis explicitly in percolation terms, and found reticulate
architectures more damage-tolerant than branched ones; they report no critical threshold, implement no
flow model, and identify fluid-flow modelling as the required next step. Separately, Hagen–Poiseuille
flow with a Kirchhoff solve has been implemented on real traced venation without any damage analysis
(Skjegstad & Kirkegaard, 2025), while the coupling of percolation to solved xylem hydraulics exists
only for stem conduit networks, where connectivity has been treated as accelerating embolism spread
(Loepfe et al., 2007; Mrad et al., 2021). What is missing is a quantitative percolation framework
applied across many real leaf networks that estimates a per-network fragmentation threshold, separates
connectivity from the geometric traits it covaries with, and tests by direct manipulation whether
reticulation itself raises that threshold.

The present study addresses that gap. It combines empirical leaf venation networks obtained from Matos
et al. (2024), graph-theoretic characterisation, Monte Carlo percolation analysis under random and
centrality-weighted removal, a set of biologically constrained synthetic networks in which connectivity
and fractal dimension are varied independently, a within-leaf reticulation-enhancement manipulation,
and a literature-calibrated hydraulic haustorial sink model. The structural and hydraulic analyses are
reported as two complementary lenses on the same networks rather than as cause and effect. The primary
contribution is the identification of **reticulation, expressed as network connectivity, as a
structural determinant of tolerance to dispersed simulated vascular damage**: connectivity predicts the
fragmentation threshold across real leaves, carries the effect when experimentally decoupled from
spatial complexity, and raises the threshold when added to a leaf's own architecture within its
observed range.

---
---

# MATERIALS AND METHODS

## 1. Dataset and Network Preparation

This study was entirely computational and required no biological sampling or cultivation. All vascular
data were obtained from the publicly available repository of Matos et al. (2024), *Leaf Architecture
and Functional Traits for 122 Species at the University of California at Berkeley Botanical Garden*,
retrieved from the Dryad Digital Repository. The repository contains spatially calibrated
high-resolution venation images, anatomical cross-sections, and pre-extracted network tables for 122
phylogenetically diverse species. It was selected because it supplies calibrated vascular geometry that
would otherwise require extensive microscopic preparation and image segmentation, and because its
networks were extracted with the LeafVeinCNN framework (Xu et al., 2020), an ensemble of convolutional
neural networks that preserves the geometry of minor veins and areoles. Working from these extractions
allowed the analysis to proceed directly on network topology rather than on preliminary segmentation.

One hundred and twenty traced venation networks were usable. **One hundred of the 120 source files are
calibrated crop windows rather than entire laminae**, so network extent is bounded by the traced window
and the cohort is described throughout as leaf-venation networks rather than whole leaves. No leaf in
the deposit carries a petiole flag (`node_Type` is 'E' throughout), a fact that governs the choice of
source node described in §2.

Three nested analysis sets are used and are identified wherever they appear.

- **Characterisation set (n = 112).** Networks passing a minimum-size screen of at least 500 veins.
- **Percolation cohort (n = 100).** The subset meeting a network-resolvability screen: at least 2,000
  vein segments, at least one independent cycle, no more than 5% of terminals at the window edge, and a
  mean-degree shift of at most 0.05 when window cut-ends are stripped. Quality flags do not gate
  inclusion. This is the primary unit for all host-level results.
- **Enhancement cohort (n = 105).** Networks meeting a separate screen of N ≥ 1,000 nodes and a current
  threshold of at least 0.02, evaluated at a higher trial budget because the estimand is a paired
  difference.

A fourth unit, the **synthetic reference network**, is a single calibrated planar mesh (N = 1,023)
used only where a high-precision threshold is required, and identified as synthetic wherever reported.
A further **synthetic grid** of 42 networks is used for the decoupling experiment (§3).

Each source network carries an extraction-quality code from the deposit. The scale is **six-tier and
non-ordinal**: A, all veins correctly segmented; B, more than 80% correctly segmented
(under-segmentation); C, spurious minor veins segmented (over-segmentation); D, physical damage
covering less than 25% of leaf area; E, less than 80% segmented; F, damage covering more than 25%. The
retained networks span grades A–D only. Because B, C and D denote different *kinds* of defect with
opposite effects on apparent connectivity, the codes are treated as categorical strata for sensitivity
analysis and never as an ordered quality gradient. Codes are comma-separated and a network may carry
more than one; sensitivity analyses reported in §8 use flag **presence** rather than the leading flag.

## 2. Computational Framework

The software environment was Python 3.13 with NetworkX (Hagberg et al., 2008), NumPy (Harris et al.,
2020), SciPy (Virtanen et al., 2020), scikit-learn (Pedregosa et al., 2011), Matplotlib (Hunter, 2007)
and Pillow (Clark, 2015). Tabular data were exchanged as CSV and JSON.

**Figure 1**
*Overall software pipeline.*

The framework proceeds in three stages. The first imports the empirical vascular tables and
reconstructs them into graphs. The second applies the analytical engine — network characterisation,
reticulation enhancement, removal simulation, Monte Carlo percolation, and hydraulic sink modelling.
The third exports measurements as tables and figures. Two complementary lenses share the single engine:
a structural percolation analysis and a hydraulic analysis. Because every stage is executed by one
unified framework, all simulations are reproducible and internally consistent.

**Graph reconstruction.** The node table is read with `csv.DictReader`, supplying for each junction its
identifier, pixel coordinates, calibration in millimetres per pixel, type, and recorded degree. The
vein table supplies each segment's two endpoints, width in millimetres, length in millimetres, and type.
Rows are validated on load: a vein is rejected if it is a self-loop or if its width or length is
non-finite or non-positive, and the number rejected is recorded. Vertices are created implicitly from
the edges, after which each surviving node receives its position and type. Where two veins connect the
same pair of junctions the wider is retained, because radius enters conductance as the fourth power.
Pixel coordinates are multiplied by the leaf's calibration factor to give positions in millimetres;
this affects only box-counting normalisation and plotting, since both the percolation threshold and the
hydraulic solve are scale-invariant. Segment length is taken directly from the table and radius is half
the recorded width.

**Source node.** Because the crop windows carry no petiole flag, the source is selected on hydraulic
grounds by a documented rule hierarchy, and the rule that fired is stored with the graph for
auditability. The operative rule for every network in this study was **widest vein**: the endpoint of
the largest-calibre segment in the window, this being the hydraulically most proximal point at which
water enters the traced patch. Connectivity is established by breadth-first search from the source;
nodes it cannot reach are assigned a generation beyond the graph maximum.

**Conductance.** Edge conductance is assigned by the Hagen–Poiseuille relation, normalised by the
maximum radius and the mean length,

    g ∝ (r / r_max)⁴ / (L / L̄),

the normalisation being necessary because a real leaf spans roughly a hundredfold calibre range, which
would otherwise render the sparse potential solve ill-conditioned. **Conductance enters the hydraulic
analysis only.** The percolation engine operates on the unweighted adjacency matrix and on unweighted
degree and betweenness, so no radius, conductance, water potential, or cavitation threshold enters any
value of p_c reported in this study.

## 3. Network Characterization

**Mean degree.** For an undirected graph, ⟨k⟩ = 2E/N, since every edge contributes to the degree of the
two nodes it joins (Newman, 2003). In a largely planar venation, ⟨k⟩ lies close to two for sparsely
reticulate leaves and rises toward three as areoles close, and it is this study's primary index of
reticulation.

**Degree distribution.** P(k) is the probability that a randomly chosen node has degree k (Newman,
2003). For each network the degree distribution is summarised by its mean, standard deviation and
maximum. Leaf venation networks are not scale-free: planarity bounds node degree, so P(k) is narrow.
This is a structural contrast with the scale-free case of Barabási and Albert (1999) and is directly
relevant to how these networks respond to centrality-weighted removal.

**Reticulation density.** Reticulation is quantified as the **loop fraction**, the proportion of edges
lying on at least one cycle — equivalently, the non-bridge edge fraction — and as the cyclomatic number
of independent loops, E − N + C. The loop fraction is used with this definition throughout; its
complement is the bridge fraction. Note that the loop fraction as defined here is *not* algebraically
determined by mean degree: the identity 1 − 2/⟨k⟩ + C/E describes the cyclomatic fraction, not the
non-bridge fraction. The two nonetheless proved almost perfectly rank-correlated across this cohort
(Results §1), an empirical rather than algebraic relationship, and are consequently treated as one
connectivity axis represented by ⟨k⟩.

**Betweenness centrality.** Betweenness measures the extent to which a node lies on shortest paths
between other pairs of nodes (Freeman, 1977; Newman, 2003). Because exact computation is O(VE) and the
largest networks contain of the order of 10⁵ junctions, betweenness is reported for the synthetic
reference network and for a subset of smaller representative networks rather than cohort-wide.

**Giant connected component.** The GCC is the largest set of nodes mutually reachable through surviving
edges; in percolation theory its disappearance marks a structural transition (Dorogovtsev et al., 2008;
Callaway et al., 2000). The fraction of nodes remaining in the GCC as removal proceeds is the order
parameter tracked by the Monte Carlo simulation.

**Fractal dimension.** D is estimated by box-counting over a bounded range of box sizes across which
the venation is genuinely scale-invariant, following the caution of Muraleedharan et al. (2023) that
self-similarity in real leaves holds only over a limited range of scales and that a regression fitted
across all scales returns a biased estimate. D is treated as one coarse architectural descriptor
complementary to the connectivity measures. Because box-counting is area-dependent, the association of
D with network size is reported and controlled for in the analysis (Results §3).

## 4. Percolation and Damage Simulation

Vascular element loss is modelled as the removal of vein junctions, that is, **site (node)
percolation**. Site removal represents loss of conducting function at a junction from any cause and is
not a claim that a haustorium physically deletes host vein junctions.

Three removal modes are used, all **stochastic and weighted** rather than rank-ordered. Each junction
is removed independently with probability min(ρ·w, 1), where ρ is the control parameter and w is a
mean-normalised weight:

- **Random (uniform) removal.** w = 1 for every node, so each junction is removed independently with
  probability ρ. This is the primary case and represents spatially distributed, tension-driven loss of
  conducting elements.
- **Degree-weighted removal.** w is proportional to node degree, so higher-degree junctions are removed
  more often. This is the formal degree-dependent occupation model of Callaway et al. (2000), not a
  deletion of the top-ranked nodes.
- **Betweenness-weighted removal.** w is proportional to node betweenness. Run on the synthetic
  reference network only, for the reason given in §3.

Because the removal probability is clipped at unity, the control parameter ρ and the **realised removed
fraction** coincide for uniform and degree weights in the range of interest but diverge for the
heavy-tailed betweenness weights. Both quantities are reported for the betweenness mode, and thresholds
from different modes are compared only on the realised-fraction axis.

Neither centrality-weighted mode is a model of any biological process. They are structural bounding
scenarios in the sense of the robustness-envelope framework: uniform removal characterises the expected
structural response and centrality-weighted removal approximates its pessimistic edge. No claim is made
that any organism computes or acts upon a centrality measure.

For each network, ρ is swept across a grid of 40 densities concentrated below ρ = 0.6, with 60
independent trials at each density, giving 2,400 trials per network per removal mode for the
percolation cohort; the enhancement cohort was evaluated at 10,000 trials per network per arm, and the
synthetic reference at 1,000,000 trials under uniform removal and 100,000 under each weighted mode.
Each trial records whether the giant connected component has fallen below half its undamaged size. A
logistic function is fitted to the resulting collapse-probability curve and the **critical removed
fraction** is taken as its inflection point, p_c = −b/w; where the inflection falls outside the swept
range, the direct 0.5-crossing of the empirical curve is used instead.

## 5. Reticulation Enhancement

To test reticulation as a manipulable determinant of tolerance rather than only a correlate, each real
network is compared against a more reticulate counterpart generated from its own geometry. Candidate
new veins are drawn from the Delaunay triangulation of the leaf's own node coordinates, a
parameter-free construction connecting a planar point set such that the circumcircle of every triangle
contains no other point (Newby et al., 2025). Candidates that already exist as veins are discarded, and
the remainder are added shortest-first — closing the leaf's smallest open areoles first — until mean
degree reaches ⟨k⟩ = 2.811, the 90th percentile of the percolation cohort's own mean degree. No network
is therefore made denser than the most reticulate networks actually observed. **Loop addition modifies
only the edge set; the node set is unchanged.** A sparse network gains many loops and an already
reticulate one few, and the threshold is re-measured on the enhanced network for direct comparison with
the original.

**Common random numbers.** The paired simulations used common random numbers. Both arms of every pair
were evaluated with a single seeded parameter instance, and because loop addition modifies only the
edge set the two arms share an identical node ordering and therefore an identical sequence of removal
draws. Δp_c is consequently a within-network paired difference in which the Monte Carlo error is common
to both arms.

## 6. Hydraulic Haustorial Sink Model

In parallel with, and not coupled to, the structural analysis, the haustorium is represented
hydraulically as a conductance sink connected to a reservoir of lower water potential. Flow through
each vein is Hagen–Poiseuille, and the steady-state water potential at every junction is obtained by
solving the equivalent resistor network under Kirchhoff's current law — the approach used for xylem and
leaf hydraulics by Loepfe et al. (2007) and Mrad et al. (2018), and extended to conduit connectivity by
Mrad et al. (2021). Boundary conditions are Dirichlet: the source node is held at ψ = 0 MPa and the
free vein endings at ψ = −1.0 MPa, representing transpirational pull. The haustorial draw is a leak
conductance K_h between the host xylem and the reservoir, giving a diverted flow of
Q = K_h(ψ_host − ψ_parasite).

**K_h is specified relative to each tapped node's own incident conductance**, so that a haustorium taps
a vein in proportion to its calibre; this choice is consistent with comparative evidence that the
parasite's own xylem is the narrower, higher-resistance element at the interface, and it prevents
sinks placed on thin terminal veins from dominating the solution.

Rather than being swept, K_h is fixed to a literature-anchored constant, solved so that the sink diverts
approximately the fraction of host water reported for parasitic associations — 18–20%, a hemiparasite
floor taken from Jiang et al. (2003) — across an illustrative host–parasite gradient of the order of
1.5 MPa. Nutrient-flow relationships for a true holoparasite are drawn from Jeschke et al. (1994).
Because no primary holoparasite measurement of either the diverted fraction or the driving gradient
could be located, both are treated as literature-anchored constraints and a stated delimitation rather
than measured inputs. A modelled cavitation threshold of −2.0 MPa is applied, and its influence on the
reported outcome is examined by sensitivity analysis (§8).

**The haustorial sink is a hydraulic boundary condition analysed alongside the percolation threshold,
not a driver of it.** The two analyses share a graph but not a state variable: the percolation analysis
is posed in removed-node fractions, the hydraulic analysis in megapascals.

## 7. Statistical Analysis

All procedures were performed in Python using NumPy, SciPy and scikit-learn.

**Descriptive characterisation.** Each structural and hydraulic metric is summarised across cohorts by
mean, standard deviation, median and range.

**Threshold estimation.** The collapse probability is estimated as P(collapse) = m_collapse / N_trials.
A logistic model P(collapse) = 1/(1 + exp[−(wρ + b)]) is fitted and p_c = −b/w taken as its inflection
point. **Confidence intervals are percentile bootstrap intervals with B = 200 resamples and seed 7, the
resampling unit being the individual Monte Carlo trial**, drawn with replacement. Where the number of
trials exceeds the implementation's resampling cap of 50,000, each bootstrap replicate is smaller than
the dataset and the resulting interval is conservative — approximately 1.6 times wider than a
full-size replicate at 100,000 trials, as measured directly. No interval is anti-conservative.

**Paired comparisons.** Removal modes are compared on identical networks with the Wilcoxon signed-rank
test (Wilcoxon, 1945), a paired distribution-free test appropriate because the thresholds are measured
on the same networks. Effect sizes are reported as the matched-pairs rank-biserial correlation
alongside the median paired difference, since at W = 0 the p-value is a function of sample size alone
and carries no magnitude information. Zero differences in the enhancement comparison are handled by
Wilcoxon's exclusion convention, with the more conservative Pratt treatment reported as a check.

**Architecture–threshold relationships.** Normality is assessed by Shapiro–Wilk (Shapiro & Wilk, 1965).
Because normality was rejected for the outcome, a pre-specified rule applied the rank-based Spearman
coefficient **uniformly to all association tests**, rather than selecting a coefficient per variable.
Unique contributions are isolated by partial correlation and by standardised multiple regression, with
multicollinearity assessed by the variance inflation factor. Because box-counting fractal dimension is
area-dependent, every architecture–threshold association is additionally reported controlling for
log network size. Group comparisons across categorical quality strata use the Kruskal–Wallis test.

**Reticulation enhancement.** The change in threshold is the paired difference
Δp_c = p_c(enhanced) − p_c(current), tested against zero and reported with the proportion of networks
improved, unchanged, and worsened. Its dependence on initial architecture is examined by regression on
initial mean degree and fractal dimension.

## 8. Model Validation and Sensitivity Analyses

**Solver verification.** The modelled Hagen–Poiseuille resistance was compared vein by vein against the
resistance column shipped with the source dataset. Because that column is itself defined as ℓ/r⁴ — the
same convention the solver implements — the comparison **verifies** correct implementation of a shared
geometric formula, including geometry parsing, unit conversion, exponent and numerical conditioning at
scale. It is not an independent test of physical validity, and the term *validation* is not used for
it. A control repeating the comparison with a deliberately incorrect radius exponent is reported
alongside.

**Independent physical comparison.** Modelled whole-network conductance was compared with measured
maximum leaf hydraulic conductance for the species in the percolation cohort with a measured value
available. The cohort screen applied is the network-resolvability screen of §1 and conditions on no
outcome; results for the unscreened set of all traced networks with a measured value are reported
alongside.

**Sensitivity analyses.** Four sensitivity analyses are reported: the dependence of the sink outcome on
the modelled cavitation threshold and on the host operating potential; the effect of substituting the
deposit's alternative ℓ/r² resistance convention; the effect of scoring connectivity to the source node
rather than as the giant connected component; and the effect of applying damage as a spatially
contiguous lesion rather than dispersing it. Quality-stratified sensitivity analyses of the enhancement
result are reported by flag presence, and every architecture–threshold association is additionally
reported excluding all over-segmented (C-flagged) networks and controlling for network size.

---
---

# RESULTS

All thresholds are expressed as the fraction of nodes removed at giant-connected-component
fragmentation, so a higher threshold indicates that the network tolerates more loss before it
fragments. The three experimental units are identified wherever used: the **percolation cohort** of 100
leaf-venation networks at 2,400 Monte Carlo trials per network per removal mode, the primary unit for
host-level results; the **enhancement cohort** of 105 networks at 10,000 trials each under the separate
screen given with its table; and the **synthetic reference network**, a single calibrated mesh
(N = 1,023) at 1,000,000 trials under uniform removal and 100,000 under each weighted mode, reported
only where a high-precision threshold is required and identified as synthetic wherever it appears. The
three sets are nested within the 112 networks passing the characterisation screen, drawn from 120
traced networks. Non-normal quantities are summarised by median and range alongside mean and standard
deviation; all inferential tests were evaluated at α = .05. Throughout, p_c denotes the critical removed
fraction and p denotes a significance value.

## 1. Structural and Hydraulic Characterization of the Empirical Networks

**Table 1**
*Structural and Hydraulic Characterization of the Empirical and Synthetic Networks*

| Characteristic | Empirical M (SD) | Empirical Mdn [range] | Synthetic M (SD) | Synthetic Mdn [range] |
|---|---|---|---|---|
| Fractal dimension D | 1.658 (0.162) | 1.676 [1.148, 1.913] | 1.599 (0.192) | 1.640 [1.262, 1.810] |
| Modelled hydraulic conductance | 2.79e-02 (1.48e-01) | 4.01e-03 [3.9e-05, 1.5e+00] | 8.62e-03 (9.46e-03) | 4.04e-03 [5.3e-04, 3.5e-02] |
| Mean degree ⟨k⟩ | 2.544 (0.200) | 2.520 [2.148, 2.989] | 2.924 (0.637) | 2.796 [2.086, 3.998] |
| Degree standard deviation | 0.795 (0.164) | 0.848 [0.201, 0.989] | 1.362 (0.213) | 1.350 [1.046, 1.731] |
| Loop fraction | 0.769 (0.137) | 0.776 [0.320, 0.995] | 0.739 (0.224) | 0.806 [0.289, 0.961] |
| Bridge fraction | 0.231 (0.137) | 0.224 [0.005, 0.680] | 0.261 (0.224) | 0.194 [0.039, 0.711] |
| GCC fraction | 0.998 (0.014) | 1.000 [0.850, 1.000] | 1.000 (0.000) | 1.000 [1.000, 1.000] |
| Network size N (nodes) | 39,755 (57,277) | 15,404 [421, 300,633] | 9,288 (11,005) | 4,095 [511, 32,767] |

*Note.* Empirical n = 112 leaf-venation networks passing the characterisation screen (at least 500
veins), drawn from 120 traced; synthetic n = 42. One hundred of the source networks are calibrated crop
windows rather than entire laminae, so network extent is bounded by the traced window. Loop fraction is
the proportion of edges lying on at least one cycle (non-bridge edges), computed identically for both
cohorts and used with this definition throughout; bridge fraction is its complement and represents the
proportion of veins whose individual loss disconnects part of the network. Conductance is modelled from
segment geometry and is reported in normalised units.

The empirical networks were sparse and close to tree-like (Mdn ⟨k⟩ = 2.520), spanned a wide
fractal-dimension range [1.148, 1.913], and were almost entirely connected (Mdn GCC fraction = 1.000).
A median of 77.6% of veins lay on at least one cycle, so the median network still carried 22.4% of its
veins as bridges. Maximum node degree across the cohort was four to five, confirming the
planarity-bounded, narrow degree distribution anticipated in the Methods. The synthetic networks
bracketed the empirical envelope in mean degree and fractal dimension.

**Table 2**
*Spearman Rank-Order Correlations Among Architectural Descriptors of the Empirical Networks*

| Variables correlated | ρ | p | Decision on H₀ | Interpretation |
|---|---|---|---|---|
| Mean degree and loop fraction | .994 | < .001 | Reject | very strong positive |
| Loop fraction and terminal fraction | −.973 | < .001 | Reject | very strong negative |
| Loop fraction and GCC fraction | .311 | < .001 | Reject | weak positive |
| Mean degree and fractal dimension | .170 | = .074 | Fail to reject | very weak positive |
| Loop fraction and fractal dimension | .156 | = .100 | Fail to reject | very weak positive |
| Loop fraction and network size | −.047 | = .625 | Fail to reject | very weak negative |

*Note.* n = 112. H₀: there is no monotone relationship between the paired descriptors. Strength bands:
< .20 very weak, .20–.39 weak, .40–.59 moderate, .60–.79 strong, ≥ .80 very strong.

Mean degree and loop fraction were almost perfectly rank-correlated (ρ = .994). This relationship is
empirical rather than algebraic — the graph identity applies to the cyclomatic fraction, not to the
non-bridge fraction reported here — but its magnitude means the two descriptors index a single
connectivity axis in these networks, and only mean degree and fractal dimension are entered jointly in
the analyses that follow. Loop fraction was the near-inverse of the terminal fraction (ρ = −.973).
Fractal dimension was weakly and non-significantly related to either connectivity measure (ρ = .170 and
.156), and neither connectivity measure was related to network size (ρ = −.047, p = .625).

**Figure 2**
*Representative empirical host network.*

*Note.* The traced venation of one leaf reduced to nodes (vein junctions) and edges (vein segments),
which is the only representation the percolation analysis uses.

**Figure 3**
*Representative calibrated synthetic mesh.*

*Note.* The generator tuned to the cohort medians, shown at the same reduction. Its branching geometry,
mean degree and loop fraction are set from the measured cohort; its fractal dimension is left to emerge
and is then measured.

## 2. Percolation Thresholds Under Simulated Vascular Damage

**Table 3**
*Critical Removed Fraction of the Empirical Cohort Under Uniform and Degree-Weighted Removal*

| Removal mode | M | SD | Mdn | Range |
|---|---|---|---|---|
| Random, uniform (primary) | 0.1847 | 0.0541 | 0.1998 | [0.0262, 0.2698] |
| Degree-weighted | 0.1559 | 0.0565 | 0.1685 | [0.0019, 0.2630] |

*Note.* n = 100 empirical leaf-venation networks, 2,400 Monte Carlo trials per network per removal
mode. The cohort is the subset of the 112 characterised networks meeting the resolvability screen (at
least 2,000 veins, at least one cycle, no more than 5% of terminals at the window edge, and a
mean-degree shift of at most 0.05 when window cut-ends are stripped). H₀: the two removal modes give
the same threshold. Wilcoxon signed-rank test (paired, distribution-free): W = 0, p < .001; H₀
rejected. Matched-pairs rank-biserial correlation r = 1.00. The uniform threshold exceeded the
degree-weighted threshold in 100 of 100 networks (M difference = 0.0288, SD = 0.0103; Mdn
difference = 0.0305).

Uniform removal fragmented the networks at a median threshold of 0.1998, whereas degree-weighted
removal fragmented them after removing fewer nodes (Mdn = 0.1685), a reduction of 15.7% in the
tolerable removal fraction. The ordering held in every one of the 100 networks examined, and the
rank-biserial correlation of 1.00 records that directional consistency; the magnitude of the effect is
the median paired difference of 0.0305. The modest size of this separation is consistent with the
narrow degree distribution reported in Table 1, since the robustness-versus-fragility asymmetry
described by Albert et al. (2000) is a property of heterogeneous degree distributions.

**Table 4**
*High-Precision Threshold Estimates From the Calibrated Synthetic Reference Network*

| Removal mode | p_c (control parameter) | Realised removed fraction | 95% CI | Trials |
|---|---|---|---|---|
| Random, uniform | 0.2711 | 0.2711 | [0.2700, 0.2720] | 1,000,000 |
| Degree-weighted | 0.2023 | 0.2023 | [0.2014, 0.2033] | 100,000 |
| Betweenness-weighted | 0.1889 | **0.1498** | [0.1879, 0.1902] | 100,000 |

*Note.* Calibrated synthetic mesh, N = 1,023, E = 1,273, ⟨k⟩ = 2.4888, D = 1.3868. This network is not
an empirical leaf. It is retained because its trial budget yields intervals about two orders of
magnitude tighter than the cohort estimates and because the supplementary scaling analyses were
performed on it. Because removal probability is clipped at unity, the control parameter and the
realised removed fraction coincide for uniform and degree weights but diverge for the heavy-tailed
betweenness weights (weight Gini = 0.754, maximum 29.4); the realised column is the one on which modes
are comparable. All intervals are percentile bootstrap intervals on the control parameter (B = 200,
seed 7) and are conservative for the reason given in the Methods.

The ordering observed in the cohort was reproduced on the reference network, and extended: on the
realised-removal axis the mesh fragmented at 0.2711 under uniform removal, 0.2023 under degree-weighted
removal, and 0.1498 under betweenness-weighted removal. Weighting removal toward a global path property
was therefore more damaging than weighting it toward a local one. Because this network is far smaller
than the typical empirical network (Mdn N = 15,404), its absolute threshold is not comparable with the
cohort medians.

**Figure 4**
*Collapse curve under uniform random removal.*

*Note.* Collapse probability and surviving giant-component fraction against the removed fraction, on
the synthetic reference network at 1,000,000 trials. The logistic inflection locates p_c.

**Figure 5**
*Collapse curve under degree-weighted removal.*

*Note.* The same construction with removal probability weighted by node degree. The curve shifts left:
the network fragments after fewer removals.

**Figure 6**
*Progressive fragmentation of the giant connected component.*

*Note.* The giant component breaking into disconnected islands as the removed fraction crosses the
threshold. This is what the threshold measures; the curves in Figures 4 and 5 summarise it as a
probability.

## 3. Association Between Network Architecture and Damage Tolerance

**Table 6**
*Normality Tests and Rank-Order Correlations of the Architectural Predictors With p_c*

| Predictor | Shapiro–Wilk W | p | ρ with p_c | p | Partial ρ | ρ controlling log N |
|---|---|---|---|---|---|---|
| Mean degree ⟨k⟩ | 0.971 | = .027 | .733 | < .001 | .736 | **.745** |
| Fractal dimension D | 0.964 | = .008 | .496 | < .001 | .502 | **.633** |
| Loop fraction | 0.978 | = .089 | .727 | < .001 | .733 | **.740** |

*Note.* n = 100. Shapiro–Wilk rejected normality for p_c (W = 0.911, p < .001) and for both
connectivity predictors, so a pre-specified rule applied Spearman's ρ uniformly to all association
tests. Each partial correlation controls for fractal dimension, except that of fractal dimension
itself, which controls for mean degree. The final column controls for log network size, reported
because box-counting fractal dimension is area-dependent.

All three architectural measures were positively and significantly associated with the threshold, the
connectivity measures most strongly. Mean degree and fractal dimension each remained significant with
the other partialled out (ρ = .736 and .502), and every association strengthened rather than weakened
when network size was controlled. A multiple regression of p_c on the two z-scored predictors gave
p_c = 0.1847 + 0.0285 z⟨k⟩ + 0.0221 zD, R² = .507, F(2, 97) = 49.93, p < .001; the coefficients are in
threshold units per standard deviation of the predictor, so a one-standard-deviation increase in mean
degree corresponds to an increase of 0.0285 in p_c. The corresponding fully standardised coefficients
are .526 and .408. The two predictors were near-orthogonal in this cohort (Pearson r = .148,
VIF = 1.02), so the regression is not affected by collinearity. Roughly half the variance in the
threshold lies outside the descriptors measured here.

Fractal dimension requires one qualification. D was strongly rank-correlated with network size
(ρ = .880), and 73% of its variance is explained by log network size, so it is in part a size readout.
Its association with the threshold nonetheless survived that control and in fact strengthened, from
ρ = .496 raw to ρ = .633 with log size partialled out.

**Figure 8**
*Critical removed fraction versus the architectural predictors.*

*Note.* Each point is one network of the percolation cohort, plotted against mean degree (left) and
fractal dimension (right), with the artifact-free grade-A tracings distinguished. The coefficients
printed on the panels are product-moment; the rank statistics of Table 6 are the ones reported, because
the distributions are not normal.

**Table 7**
*Synthetic Causal Grid: Threshold Regressed on Two Decoupled Architectural Axes*

| Removal mode | Predictor | ρ | OLS b (raw units) | Standardised β | Model R² |
|---|---|---|---|---|---|
| Random, uniform | Mean degree ⟨k⟩ | .991 | 0.1202 | .933 | .887 |
| | Fractal dimension D | .227 | 0.0287 | .067 | .887 |
| Degree-weighted | Mean degree ⟨k⟩ | .993 | 0.1290 | .960 | .938 |
| | Fractal dimension D | .206 | 0.0317 | .071 | .938 |

*Note.* n = 42 synthetic networks in which mean degree and fractal dimension were varied independently
by construction (Pearson r = .086; Spearman ρ = .222). The raw coefficients are in threshold units per
unit of each predictor and are not comparable with one another, because mean degree spans 1.91 units
across the grid and fractal dimension spans 0.55; the standardised coefficients are comparable. Model
R² refers to the full two-predictor model and is therefore identical for both rows of a removal mode.

With the two axes decoupled by construction, the threshold tracked connectivity almost
deterministically (ρ = .991) and fractal dimension only weakly (ρ = .227). The fitted surface was
p_c = −0.0907 + 0.1202 ⟨k⟩ + 0.0287 D, R² = .887, F(2, 39) = 152.61, p < .001. Expressed per standard
deviation, the connectivity coefficient is about 14 times the geometry coefficient across the full
grid.

The grid's connectivity axis extends to ⟨k⟩ = 4.00 against an empirical maximum of 2.99, so its upper
portion is an extrapolation relative to the measured cohort. Restricting the fit to the 24 grid
networks lying inside the empirical range gives a stronger fit and a smaller, more defensible dominance
ratio: standardised β = .981 for mean degree against .125 for fractal dimension, a ratio of
approximately 7.8 to 1, with R² = .940, F(2, 21) = 164.12. The corresponding partial correlations
within the empirical range are r = .970 for mean degree controlling for fractal dimension, and r = .451
for fractal dimension controlling for mean degree — the latter more than double its full-grid value of
.195. Connectivity remains the dominant architectural axis inside the range real leaves occupy;
geometry is secondary rather than negligible.

**Figure 9**
*Coverage of the synthetic grid over the measured architectural region.*

*Note.* The grid networks plotted against the percolation cohort in the mean-degree/fractal-dimension
plane. The grid is laid out on two independent knobs, which is what makes the attribution in Table 7
possible; it also shows the extrapolation, since the grid's connectivity axis extends past the densest
network measured.

## 4. Vein Reticulation as a Structural Basis for Damage Tolerance

**Table 8**
*Reticulation, Bridge Dependence, and Damage Tolerance*

| Variables correlated | ρ | t | p | Decision on H₀ |
|---|---|---|---|---|
| Loop fraction and p_c (uniform) | .727 | 10.48 | < .001 | Reject |
| Bridge fraction and p_c (uniform) | −.727 | −10.48 | < .001 | Reject |
| Loop fraction and p_c (degree-weighted) | .818 | 14.06 | < .001 | Reject |
| Bridge fraction and p_c (degree-weighted) | −.818 | −14.06 | < .001 | Reject |
| Loop fraction and the uniform-minus-weighted gap | −.786 | −12.58 | < .001 | Reject |
| Residual loop fraction (⟨k⟩ controlled) and p_c | −.088 | −0.87 | = .386 | Fail to reject |

*Note.* n = 100; df = 98. Bridge fraction is the exact complement of loop fraction, so the two carry the
same information with opposite sign. The final row tests whether loop fraction predicts the threshold
beyond mean degree; the non-significant result follows from the near-collinearity reported in Table 2
and is not evidence that reticulation is unimportant.

Loop fraction was positively associated with the threshold under both removal modes, and more strongly
under the weighted mode (ρ = .818) than the uniform one (ρ = .727). The gap between the two thresholds
narrowed as reticulation increased (ρ = −.786), so more reticulate networks lost less of their
tolerance when removal was concentrated rather than distributed. This gap relationship was unchanged
when network size was controlled (ρ = −.789), and the gap itself was uncorrelated with network size
(ρ = .046, p = .647).

**Table 9**
*Damage Tolerance by Reticulation Quartile*

| Quartile | n | Mdn loop fraction | Mdn ⟨k⟩ | Mdn p_c |
|---|---|---|---|---|
| Q1 (least reticulate) | 25 | 0.616 | 2.320 | 0.1584 |
| Q2 | 25 | 0.738 | 2.472 | 0.1850 |
| Q3 | 25 | 0.807 | 2.564 | 0.2087 |
| Q4 (most reticulate) | 25 | 0.901 | 2.734 | 0.2308 |

*Note.* H₀: the least- and most-reticulate quartiles do not differ in p_c. Mann–Whitney U = 4, p < .001,
n = 25 per quartile; Cliff's δ = 0.987, indicating near-complete separation of the two distributions;
H₀ rejected.

More highly reticulated networks tolerated more structural loss before fragmenting. The median
threshold rose monotonically across reticulation quartiles, from 0.1584 in the least reticulate
quartile to 0.2308 in the most reticulate. The most reticulate quartile withstood the removal of an
additional 7.2% of its nodes, a relative gain of 45.7%.

Taken together with Tables 6 and 7, these results identify reticulate connectivity as the dominant
architectural determinant of how much **dispersed** vascular element loss a leaf venation network
absorbs before fragmenting. The dispersed-damage qualifier is load-bearing and is quantified in §7.2.

## 5. Effect of Reticulation Enhancement on Network Damage Tolerance

**Table 10**
*Reticulation-Enhancement Effect by Tracing-Quality Grade*

| Grade | n | Mdn p_c current | Mdn p_c enhanced | Mdn Δp_c | % improved |
|---|---|---|---|---|---|
| A | 21 | 0.2198 | 0.2267 | 0.0069 | 62% |
| B | 46 | 0.1899 | 0.2107 | 0.0137 | 96% |
| C | 10 | 0.1610 | 0.1711 | 0.0083 | 100% |
| D | 28 | 0.2048 | 0.2195 | 0.0086 | 93% |
| Full valid cohort | 105 | 0.2010 | 0.2150 | 0.0095 | 89% |

*Note.* n = 105 networks meeting the enhancement screen (N ≥ 1,000 and current p_c ≥ 0.02), evaluated
at 10,000 trials each with common random numbers across the paired arms. Grade is the leading flag of
the source dataset's comma-separated extraction-quality code and is a defect **type**, not a severity
level; grades are therefore reported as categorical strata and no ordering among B, C and D is implied.
H₀: the median change in p_c is zero. Wilcoxon signed-rank test on the 93 non-zero differences (12 ties
discarded): W = 0, p < .001; the more conservative Pratt treatment across all 105 gives the same
conclusion (p < .001); H₀ rejected. Matched-pairs rank-biserial correlation ≈ 1.00. Of the 105
networks, 93 improved, 12 were unchanged and none worsened (M Δp_c = 0.0123, SD = 0.0109, range
[0.0000, 0.0459]; median relative gain 5.5%).

Raising each network's connectivity toward the reticulation ceiling ⟨k⟩ = 2.811 — the 90th percentile of
the percolation cohort's own mean degree, so that no network is made denser than the most looped
networks observed — raised the fragmentation threshold in 89% of the 105 networks and lowered it in
none. Because loop addition modifies only the edge set and both arms consumed an identical sequence of
removal draws, each network served as its own control under common random numbers, and the Monte Carlo
error is common to the two arms.

Differences among quality grades in the raw change were **not statistically significant**
(Kruskal–Wallis p = .073), so the grades are reported for transparency rather than as a detected
effect. Grade-A networks began at the highest median initial connectivity of any grade (⟨k⟩ = 2.665
against 2.472 for grade B), which is the relevant covariate given the dependence reported in Table 11.
Considered alone, the artifact-free grade-A subset was still significant: of its 21 networks, 13
improved, 8 were unchanged and none worsened, so every network that changed at all changed in the same
direction (sign test p < .001).

**Table 11**
*Dependence of the Threshold Gain on Initial Architecture*

| Initial trait | ρ with Δp_c | p | b (Δp_c per 1 SD) | Standardised β |
|---|---|---|---|---|
| Initial mean degree ⟨k⟩ | −.821 | < .001 | −0.00887 | −.816 |
| Fractal dimension D | −.034 | = .729 | 0.00072 | .066 |

*Note.* n = 105. Both regression columns come from the same model, in which the predictors are
z-scored; the fourth column leaves the outcome in its own units (change in p_c per standard deviation
of the predictor) and the fifth standardises it. R² = .655.

The gain depended strongly and negatively on the network's initial mean degree (ρ = −.821): the sparser
the starting network, the larger the improvement. Fractal dimension was unrelated to the gain
(ρ = −.034, p = .729), and the two-predictor model explained R² = .655 of the variance in Δp_c. Initial
connectivity accounts for essentially all of the explained variance, and it is also the covariate that
differs across quality grades.

**Table 12**
*Networks Exhibiting the Largest Threshold Gain From Added Reticulation*

| Species | N (nodes) | ⟨k⟩ current | Loops added | p_c before | p_c after | Δp_c |
|---|---|---|---|---|---|---|
| *Clusia alata* | 6,475 | 2.195 | 1,994 | 0.1351 | 0.1810 | 0.0459 |
| *Chloranthus spicatus* | 20,004 | 2.148 | 6,632 | 0.1287 | 0.1745 | 0.0458 |
| *Anemopsis californica* | 85,519 | 2.216 | 25,460 | 0.1545 | 0.1962 | 0.0417 |
| *Metapanax davidii* | 5,054 | 2.198 | 1,549 | 0.1580 | 0.1981 | 0.0401 |
| *Eurya japonica* | 11,423 | 2.249 | 3,209 | 0.1632 | 0.2006 | 0.0374 |
| *Smilax hispida* | 31,577 | 2.344 | 7,370 | 0.1934 | 0.2273 | 0.0339 |

*Note.* Sorted by descending gain. Each network began with a mean degree near the lower bound of the
cohort range. One caveat applies to this table: *Clusia alata* falls outside the crop-edge tolerance
reported in Table 13 (boundary terminal fraction 0.061 against a 0.05 tolerance), so its extent is more
strongly bounded by the traced window than the rest of the cohort.

**Figure 10**
*Change in fragmentation threshold per network following reticulation enhancement.*

*Note.* Left: each network's enhanced threshold against its own current threshold; every point lies on
or above the diagonal. Right: the distribution of the change. The pairing is within-network under
common random numbers, so each network is its own control.

**Figure 11**
*A representative network before and after reticulation enhancement.*

*Note.* *Metapanax davidii*, the fourth-largest gainer in Table 12. Added areole closures (blue) shorten
the open vein endings into redundant circuits without altering the major-vein skeleton: mean degree
rises from 2.20 to the 2.81 ceiling through 1,549 added loops, and the measured threshold rises from
.158 to .198.

## 6. Hydraulic Response to a Calibrated Haustorial Sink

**Table 5**
*Hydraulic Behaviour of the Literature-Calibrated Haustorial Sink Across the Swept Gradient*

| Host–parasite gradient (MPa) | Minimum ψ (MPa) | Margin to modelled threshold (MPa) | Flow diverted | Vessels embolised |
|---|---|---|---|---|
| 0.0 (no effective draw) | −0.9963 | 1.0037 | 0.2% | 0 |
| 0.5 | −0.9963 | 1.0037 | 7.4% | 0 |
| 1.0 | −0.9963 | 1.0037 | 14.0% | 0 |
| 1.5 (illustrative) | −1.0224 | 0.9776 | 20.0% | 0 |
| 2.0 | −1.0940 | 0.9060 | 25.5% | 0 |
| 2.5 | −1.2081 | 0.7919 | 30.5% | 0 |
| 3.0 | −1.3221 | 0.6779 | 35.1% | 0 |

*Note.* Sink strength K_h = 0.0392, calibrated so that the haustorium withdraws 20.0% of leaf
throughput at the illustrative 1.5 MPa gradient; the modelled cavitation threshold is −2.0 MPa. Every
fifth point of the 31-point sweep is shown. The diverted fraction rises with the gradient because the
parasite reservoir deepens while K_h is held fixed, so the 20% figure is specific to the illustrative
gradient. The first row is effectively the no-parasite baseline: with no draw the minimum interior
potential is −0.9963 MPa, set by the −1.0 MPa transpirational boundary condition. Outcomes at other
cavitation thresholds and other host operating potentials are given in Table 16.

At the calibrated strength the minimum host leaf water potential was −1.0224 MPa at the illustrative
gradient, and the sink embolised no vessels at the modelled −2.0 MPa threshold. Sweeping the
host–parasite gradient from 0.0 to 3.0 MPa left that margin positive throughout, its smallest value
being 0.6779 MPa.

Three quantities place that result in context, and all three are independent of the choice of
threshold. First, the parasite's own contribution to the potential field is small: relative to the
no-parasite baseline of −0.9963 MPa, the calibrated sink depressed the network's minimum potential by
0.0262 MPa at the illustrative gradient, so approximately 2.6% of the reported margin is attributable
to the parasite and the remainder is the stipulated separation between the transpirational boundary
condition and the modelled cavitation threshold. Second, the depression at the haustorial contact
patch — the quantity the parasite actually controls — was 0.402 MPa at the illustrative gradient and
was **exactly linear** in the host–parasite gradient, at 0.2682 MPa per MPa (intercept ≈ 0, maximum
residual 0.017 MPa across 0–12 MPa). Third, extrapolating that relationship, reaching the modelled
−2.0 MPa threshold would require a host–parasite gradient of approximately **6.0 MPa**, against a
largest directly measured parasite–host leaf gradient of approximately 0.5 MPa in the published
literature.

Under the modelled conditions the calibrated haustorial sink is therefore **largely decoupled from the
structural fragmentation threshold**: it withdraws a substantial fraction of leaf throughput while
perturbing the potential field only slightly, and it does not approach the modelled cavitation
threshold within the swept range. This is a statement about the modelled sink at the calibrated
strength and gradient, not a demonstration that holoparasitic withdrawal is universally sub-symptomatic.

**Figure 7**
*Host water-potential field and margin to the modelled cavitation threshold under the calibrated
haustorial sink.*

*Note.* The solved potential field across the host network with the haustorium attached. The minimum
potential anywhere in the field remains above the modelled cavitation threshold, which is the result
tabulated in Table 5.

## 7. Model Validation and Sensitivity Analyses

The analyses in this section establish the verification status of the model and the robustness of the
principal results. They are reported separately from the biological findings above.

**Table 13**
*Model Verification and Comparison Summary*

| Check | Scope | Statistic | Result | Reading |
|---|---|---|---|---|
| Hydraulic resistance | 119 leaves, 5,668,467 veins | Worst per-leaf ratio CV | 1.1e-07 | Agreement to floating-point precision |
| | | Worst \|median ratio − 1\| | 6.1e-08 | Inside the 1e-06 tolerance |
| Wrong-exponent control | Same veins | Median Pearson r (log) | 0.953 | The match is not trivial |
| Leaf conductance K_leaf | 93 species | Spearman ρ | .187 (p = .073) | Weak and non-significant; xylem-only |
| Crop-edge boundary | 120 leaves | Within both tolerances | 105 of 120 | 15 outside; 3 of those remain in the enhancement cohort |

*Note.* One leaf was excluded from the resistance comparison for having fewer than 50 usable veins,
hence 119 rather than 120. The resistance check compares the model's Hagen–Poiseuille resistance vein
by vein against the resistance column shipped with the source dataset. Because that column is itself
defined as ℓ/r⁴, the same convention the solver implements, the comparison **verifies** correct
implementation rather than validating the physical model.

The hydraulic solver reproduced the source dataset's own resistance column across 119 leaves and
5,668,467 veins to floating-point precision: the ratio of modelled to source resistance had a worst-case
per-leaf coefficient of variation of 1.1e-07 and a worst-case median departure from unity of 6.1e-08,
both inside the pre-set 1e-06 tolerance. Repeating the comparison with a deliberately wrong exponent
dropped the median correlation to 0.953. This establishes correct re-implementation of a shared
geometric convention, not independent physical validity.

The one comparison against an independent physical measurement was weak. Modelled whole-network
conductance tracked measured leaf conductance only weakly and non-significantly (ρ = .187, p = .073,
n = 93 species, 95% CI [−0.024, 0.382]), as expected of a xylem-only model compared with a quantity
dominated by resistances outside the xylem. The interval spans zero, so the check is underpowered
rather than negative. It is unchanged by the choice of resistance convention: repeating it under the
deposit's alternative ℓ/r² convention gives ρ = .179, p = .059 (n = 112). The species set is the
percolation cohort intersected with those having a measured value; relaxing the cohort screen to all
112 traced networks with a measured value gives ρ = .176, p = .063. In the crop-edge sensitivity test,
105 of 120 leaves fell inside both tolerances; the 15 that did not are the smallest and most heavily
windowed tracings, and 3 of them remain in the enhancement cohort.

**Figure 12**
*Critical haustorial density across sink strength and fractal dimension.*

*Note.* The vertical axis of this surface is the critical fraction of nodes **bearing a haustorium**
under the coupled hydraulic model, in which a node is removed only if its solved water potential falls
below the −2.0 MPa cavitation threshold. It is therefore a different quantity from the removed-node
threshold reported in Tables 3 to 9 and is not comparable with those values. The surface was computed
on the cohort-calibrated mesh (N = 1,023, ⟨k⟩ held at 2.49) with the sink axis anchored on the
calibrated K_h = 0.0392 and expressed as multiples of it, at 6,000 trials per cell with bootstrap
intervals.

At the calibrated sink strength, no network reached the collapse criterion at any haustorial density:
the collapse probability never reached .50 at any density between 0 and 1, so there is no threshold to
report. A threshold first appeared in the least reticulate network at two times the calibrated strength
and in every network at three times it, after which it fell steeply as the sink was strengthened
further.

**Figure 13**
*Size dependence of the threshold at fixed architecture.*

**Table 14**
*Fixed-Architecture Size Sweep*

| N | D | ⟨k⟩ | Loop fraction | p_c | 95% CI | 10–90% window |
|---|---|---|---|---|---|---|
| 1,023 | 1.385 | 2.489 | 0.692 | 0.2701 | [0.2690, 0.2711] | 0.0646 |
| 2,047 | 1.391 | 2.487 | 0.681 | 0.2295 | [0.2285, 0.2313] | 0.0827 |
| 4,095 | 1.388 | 2.493 | 0.652 | 0.1271 | [0.1249, 0.1289] | 0.1609 |
| 8,191 | 1.387 | 2.487 | 0.580 | 0.1008 | [0.0995, 0.1025] | 0.1187 |
| 16,383 | 1.384 | 2.488 | 0.561 | 0.0772 | [0.0762, 0.0788] | 0.0852 |

*Note.* Two size sweeps were run. In the first the generator's depth parameter raises network size and
fractal dimension together, from D = 1.267 at N = 511 to D = 1.741 at N = 8,191, so the accompanying
rise in p_c from 0.2531 to 0.2857 mixes the two and cannot be read as a size effect. The second sweep,
tabulated here, pinned fractal dimension and mean degree by tuning the generator's length ratio and
mesh fraction at each size. Pinning those two descriptors does not pin the architecture: loop fraction
drifts by 0.131 across the size range, and loop fraction is itself one of this study's predictors of
the threshold. **No finite-size claim — convergence or divergence — is made from this generator.**

Across the fixed-architecture sweep the threshold moved from 0.2701 at N = 1,023 to 0.0772 at
N = 16,383 while the pinned descriptors varied by no more than 0.0070 in D and 0.0059 in mean degree.
That decline cannot be attributed to size, because the loop fraction of the same networks fell from
0.692 to 0.561 over the sweep, so the threshold tracks the loss of reticulation rather than the growth
in size. Because a definitive statement about the transition's universality class requires a multi-size
scaling collapse at genuinely constant architecture, no critical exponent is reported. The connectivity
threshold located on the largest network (f_c = 0.524) is the removal fraction at which the giant
component vanishes, a different criterion from the p_c reported elsewhere; read against that definition
it is of the same order as the Molloy–Reed prediction for this network (0.531), a qualitative
correspondence only, since both are generating-function calculations that assume a locally tree-like
graph while the planar mesh contains short loops.

Importantly, this size dependence does not propagate into the empirical results. Across the percolation
cohort the threshold rose only weakly with network size (ρ = .232, p = .020) — the opposite sign to the
synthetic sweep — while mean degree and loop fraction were unrelated to size (ρ = .037 and .030), and
every architecture–threshold association strengthened rather than weakened under size control
(Table 6).

**Table 16**
*Summary of Sensitivity and Robustness Analyses*

| Analysis | Comparison | Result | Effect on conclusions |
|---|---|---|---|
| Cavitation threshold | −1.00 to −3.00 MPa, calibrated sink | Onset gradient rises from 1.1 MPa (at −1.00) to 6.0 MPa (at −2.00) and 9.5 MPa (at −3.00) | The absence of embolism is specific to thresholds at or below −1.10 MPa within the 0–3 MPa sweep; reported as threshold-dependent |
| Host operating potential | ψ_leaf from −0.5 to −2.5 MPa | At ψ_leaf = −2.5 MPa, 91 vessels embolise with no parasite present | The margin is governed by the boundary condition, not by the parasite |
| Resistance convention | ℓ/r⁴ versus ℓ/r² | K_leaf: ρ = .176 versus ρ = .179 (n = 112) | None; the K_leaf outcome is convention-independent |
| Connectivity criterion | GCC versus source-anchored, identical draws | Spearman ρ = .910; median paired difference −0.011; source lower in 99 of 99 | None (§7.1) |
| Damage locality | Dispersed versus contiguous-disc removal | Single lesion 0.4949, ten lesions 0.4494, versus dispersed 0.1997 | Dispersed removal is conservative; connectivity result is scope-limited (§7.2) |
| Over-segmentation | Excluding all C-flagged networks | p_c ~ ⟨k⟩ rises from .733 to .789; median Δp_c rises from 0.0095 to 0.0108 | None; both principal results strengthen |
| Baseline fragmentation | Excluding networks with baseline GCC fraction ≤ .99 | p_c ~ ⟨k⟩ = .731 (n = 99); Δp_c median 0.0094, 91 improved / 12 unchanged / 0 worsened (n = 103) | None |

*Note.* Source-anchored and locality analyses were computed on 99 of the 100 cohort networks under the
engine settings of Table 3, with both criteria scored on identical removal draws. The re-implementation
used for those analyses reproduced the archived thresholds at Spearman ρ = .999 (median absolute
difference 0.0011, n = 99).

### 7.1 Robustness to the Connectivity Criterion

The threshold reported throughout is defined on the giant connected component. Prior venation-robustness
analyses instead score connectivity to a source — the structural vein in Mander and Williams (2024),
the petiole in Price and Weitz (2014). Because no network in this dataset carries a petiole flag, the
source used here is the documented widest-vein rule described in the Methods, and the source node is
protected from removal, matching the treatment of the structural vein as an un-attacked layer.

Scoring both criteria on identical removal draws across 99 cohort networks, the source-anchored
threshold was systematically lower than the GCC threshold, by a median of 0.011, and was lower in every
one of the 99 networks. The two nevertheless ranked networks almost identically (Spearman ρ = .910,
Pearson r = .935; medians 0.1832 against 0.1997). Every substantive association was preserved:
connectivity remained the leading predictor (ρ = .649 against .733 under the GCC criterion) and fractal
dimension remained secondary (ρ = .451 against .490). **The choice of connectivity criterion does not
change the substantive conclusions of this study.**

### 7.2 Effect of Localised Damage

Uniform removal disperses damage across the lamina, whereas a haustorial lesion, a bite, or a necrotic
patch is spatially contiguous. Two localised protocols were run at matched realised removed fractions,
so that the horizontal axis is identical to the dispersed case: a single lesion, removing the nodes
nearest a randomly chosen centre, and ten simultaneous lesions grown from ten random centres.

Localised damage was substantially **less** damaging than dispersed damage. The median critical removed
fraction rose from 0.1997 under dispersed removal to 0.4949 under a single lesion and 0.4494 under ten
lesions — increases of 0.291 and 0.251, or factors of 2.46 and 2.27. A localised lesion was less
damaging than dispersed removal in **99 of 99 networks for both protocols, without exception**
(Wilcoxon p < .001 for both). Uniform removal is therefore a conservative abstraction, and the
thresholds reported in Tables 3 and 4 are lower bounds on the loss a network can absorb.

The architectural relationship, however, did not survive the change in damage geometry. Under a single
lesion the association between connectivity and the threshold vanished (ρ = −.011, p = .91), and under
ten lesions it was weak and non-significant (ρ = .138, p = .17), against ρ = .733 under dispersed
removal. Fractal dimension behaved oppositely, retaining a moderate and significant association under
the multi-lesion protocol (ρ = .511, p < .001). A compact lesion removes a spatially bounded region and
leaves the remainder connected, so the network routes around the hole; the alternative routes that
reticulation supplies between regions are what dispersed removal destroys and what a single hole does
not.

**The principal architectural result of this study is therefore specific in scope: reticulate
connectivity governs tolerance to dispersed simulated vascular damage. Under spatially contiguous
damage all networks tolerated substantially more loss, and connectivity ceased to differentiate them.**

## 8. Supplementary Exploratory Analysis: Modelled Separation Between Fragmentation and Total Loss

The following analysis is exploratory and is reported in the Supplementary Materials. It is not a
biological finding of this study.

**Figure 14** *(Supplementary)*
*Modelled separation between fragmentation and complete loss of the giant component across infestation
growth rates.*

**Table 15** *(Supplementary)*
*Modelled Separation Interval Across Stipulated Growth Rates*

| Growth rate | Time to fragmentation threshold | Time to complete loss | Separation |
|---|---|---|---|
| Slow (r = 0.15) | 19.35 | 26.60 | 7.25 |
| Moderate (r = 0.25) | 11.61 | 15.96 | 4.35 |
| Aggressive (r = 0.40) | 7.26 | 9.98 | 2.72 |

*Note.* Infestation is modelled as logistic growth in the affected node fraction (ρ₀ = 0.02) at three
stipulated rates. The interval is bounded by the fragmentation threshold (p_c = 0.271) and the point at
which the giant component vanishes (f_c = 0.525), both evaluated on the **synthetic reference network**
rather than the empirical cohort. **The time unit is set by the assumed growth rate and is not
calibrated to any measured infestation time-course; the values carry no calendar units.** The model
contains no symptom variable, and this analysis does not demonstrate, predict, or estimate a
physiological pre-symptomatic window.

A separation between fragmentation and complete loss of the giant component was present at every
stipulated growth rate, spanning 7.25 growth-time units at the slowest rate and 2.72 at the fastest.
The existence of that separation is a property of the two collapse criteria; its duration is a function
of the stipulated growth rate and carries no biological time-scale.

---
---

# Notes for the writer

**Terminology applied throughout.** *critical removed fraction / fragmentation threshold* (never
hydraulic collapse threshold) · *simulated vascular damage / removal simulation* (never attack
simulation) · *degree-weighted removal* and *betweenness-weighted removal* (never targeted attack) ·
*verified* (never validated, for the resistance-column comparison) · *modelled conductance* ·
*hydraulic boundary condition analysed in parallel with* (never driven by) · *dispersed* versus
*localised* removal.

**Two source statements were corrected as factual errors, not stylistic edits.**
(1) The Methods previously stated that 105 of the traced networks were "whole-leaf networks" and that
networks under 1,000 nodes were excluded as cropped fragments. In fact 100 of the 120 source files are
crop windows, and the three analysis sets use three different documented screens; these are now stated
explicitly in Methods §1.
(2) The Methods previously gave a single Monte Carlo budget of "10,000 per network". The percolation
cohort used 2,400 trials per network per mode and the enhancement cohort 10,000 per arm; both are now
stated where they apply.

**Items requiring the author's action before submission.** The reference list needs the corrections
identified in the audit: the two Matos et al. (2024) papers must be cited separately (*Ecology*,
105(12), e4436 for the dataset; *New Phytologist*, 244(2), 407–425 for the analysis); Sack et al.
(2008) is *PNAS*, 105(5), 1567–1572; Ronellenfitsch and Katifori (2019) is *Physical Review Letters*,
123(24), 248101; the Mrad et al. (2021) author list is Mrad, Johnson, Love and Domec; Xu et al. is
2020; and the Albert et al. (2000) erratum (*Nature*, 409(6819), 542) should be cited alongside.
Skjegstad and Kirkegaard (2025), Shen et al. (2007) and Cochavi et al. (2017), newly cited in the
Introduction, must be added.

**SOP alignment.** The Results are now organised thematically rather than by specific question. If the
Statement of the Problem is retained in its current form, SOP 2 should read *simulated vascular element
loss* rather than *haustorial and structural loss*, its sub-item 2.1 should name uniform and
degree-weighted removal, and SOP 4 should carry the dispersed-damage scope condition established in
§7.2. SOP 1 and SOP 3 stand as written.
