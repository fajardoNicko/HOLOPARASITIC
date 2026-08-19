# DISCUSSION

## Structural and Modelled Hydraulic Characteristics of the Networks

The empirical networks are sparse. As shown in Table 1, median mean degree was 2.520 across the 112
characterised networks, with a median degree standard deviation of 0.848 and a maximum node degree of
four to five. A planar graph admits at most 3N − 6 edges, so mean degree could approach six; the
observed maximum of 2.989 sits at roughly half that, and the whole cohort spans only 0.84 units. That
narrow spread is why degree-weighted removal produces a modest effect rather than a dramatic one — there
is little variation in degree for a weighting scheme to exploit. Planar proximity graphs with
homogeneous degree distributions behave the same way (Mou & Hayashi, 2025).

Despite the low mean degree, the networks carry substantial redundancy. Refer again to Table 1, where a
median 77.6% of veins lay on at least one cycle, ranging from 0.320 to 0.995, leaving a median bridge
fraction of 0.224. Mean degree barely above the tree value of 2, yet three-quarters of edges on cycles:
the limited edge budget has been spent almost entirely on closing loops rather than extending branches.
Figure 2 shows a traced leaf reduced to the nodes and edges the analysis operates on. This is the
architecture Katifori et al. (2010) and Price and Weitz (2014) identify as the basis of resilience in
venation, and the one whose consequence Sack et al. (2008) measured directly: severing the midrib of a
pinnately veined leaf removes about three-quarters of its hydraulic conductance, while damage to second-
and higher-order veins is tolerated with no detectable penalty, because the minor-vein network supplies
parallel paths.

The networks were almost entirely connected before damage, with a median giant connected component
fraction of 1.000 and a mean of 0.998 in Table 1. The percolation analysis requires this, and the single
substantially fragmented tracing carries none of the results. Restricting the cohort to the 99 networks
with a baseline component fraction above .99 moved the connectivity association from ρ = .733 to
ρ = .731, and the enhancement outcome from 93 improved, 12 unchanged and 0 worsened to 91, 12 and 0;
both figures appear in the final row of Table 16.

Size and fractal dimension are entangled. Median network size was 15,404 nodes across a range of 421 to
300,633, and fractal dimension was rank-correlated with size at ρ = .880, with log size accounting for
73% of its variance, as the note to Table 6 and the size-control block of Table S3 record. Box-counting
dimension is estimated over a finite range of box sizes, and a larger traced region supports a longer
scaling range (Muraleedharan et al., 2023), so the correlation is partly a measurement property.
Fractal dimension is therefore reported with network size controlled throughout, not as an independent
readout of spatial complexity.

Modelled whole-network conductance had a median of 4.01 × 10⁻³ in normalised units across nearly five
orders of magnitude in Table 1. Turning to Table 13, the solver reproduced the source dataset's own
resistance column across 119 leaves and 5,668,467 vein segments to floating-point precision: the worst
per-leaf coefficient of variation was 1.1 × 10⁻⁷ and the worst departure of the median ratio from unity
6.1 × 10⁻⁸, both inside a pre-set tolerance of 1 × 10⁻⁶, while a deliberately wrong exponent dropped the
median correlation to 0.953. That is verification, not validation — the deposit defines its column as
ℓ/r⁴ and the solver implements ℓ/r⁴, so the comparison confirms correct re-implementation of a shared
convention, not that ℓ/r⁴ is the right physics for a leaf vein.

The one test against independent measurement was weak. The same table gives modelled conductance
tracking measured leaf hydraulic conductance at ρ = .187, p = .073, n = 93 species, with a 95%
confidence interval of −0.024 to 0.382. The interval spans zero, so the model is underpowered against
this benchmark rather than refuted by it. A xylem-only model should behave this way: outside-xylem
pathways through the mesophyll and bundle sheath carry a large share of static leaf resistance and most
of its dynamic decline during dehydration (Scoffoni et al., 2017), and the study that published these
networks reported weak architecture–efficiency coupling on the same material (Matos et al., 2024b). Nor
is it an artefact of the conductance convention. In Table 16, ℓ/r² gives ρ = .179 against ρ = .176 for
ℓ/r⁴ on the same 112 networks, even though Table S3 shows the two conventions producing conductances
that differ by a median factor of 0.064. The percolation analysis does not use the conductance layer at
all, so this weakness constrains the sink analysis and nothing else.

Four descriptors are easily conflated and measure different things. Mean degree is how many veins meet
at a junction. Loop fraction is how much of that budget is closed into cycles. Bridge fraction, its
complement, is the proportion of edges whose individual loss disconnects a region. Fractal dimension is
how thoroughly the network fills the plane. None of them measures hydraulic function.

---

## Effect of Simulated Vascular Element Loss on Structural Integrity

Under uniform removal the cohort fragmented at a median removed fraction of 0.1998. Table 3 gives the
full distribution: a mean of 0.1847, a standard deviation of 0.0541, and a range of 0.0262 to 0.2698
across 100 networks at 2,400 trials per network per removal mode. A median leaf venation network loses
global connectivity after roughly one junction in five is disabled. In Figure 6 the giant component can
be seen breaking into islands as the threshold is crossed, and Figure 4 summarises the same process as a
collapse probability. The threshold is an operational criterion — the removed fraction at which the
largest surviving component falls below half its undamaged size with probability .50 — chosen because it
computes identically on networks spanning four and a half orders of magnitude. It is not a critical
point, and no universality or critical-exponent claim is made.

Weighting removal by node degree lowered the median threshold to 0.1685, a 15.7% reduction, with a
median paired difference of 0.0305, a mean of 0.0288 and a standard deviation of 0.0103, all in the same
table. The Wilcoxon signed-rank test rejected equality at W = 0, p < .001, and the matched-pairs
rank-biserial correlation was 1.00 because the uniform threshold exceeded the degree-weighted threshold
in 100 of 100 networks. Comparing Figure 5 with Figure 4 shows the collapse curve shifting left.

The rank-biserial value of 1.00 records direction, not magnitude. Magnitude is the median difference of
0.0305, about a sixth of the baseline threshold. Its standard deviation of 0.0103 is the standard
deviation of the 100 per-network differences and cannot be recovered from the two column standard
deviations, which describe between-network variation; the arms correlate at r = .984, so that variation
largely cancels in the difference.

Where loss falls therefore matters independently of how much is lost. A junction of degree four sits on
more paths than one of degree two, so removing it destroys more alternative routes per node removed. The
effect is real but small, which follows from the degree distribution. In Table S1 the degree weights of
the synthetic reference network have a Gini coefficient of 0.274, a maximum of 2.4 times the mean, and
only six distinct values, with 32% of nodes tied in one group. On such a weight vector, weighted removal
is often barely distinguishable from uniform removal.

That reference network, at N = 1,023, allowed a tighter comparison. Table 4 reports 0.2711 under uniform
removal at 1,000,000 trials, 0.2023 under degree weighting, and 0.1498 under betweenness weighting, so
weighting toward a global path property was more damaging than weighting toward a local one. This
reverses the ordering usually reported for scale-free networks but matches what this network class
predicts. In a planar graph with bounded degree, a degree ranking is largely a ranking of ties;
betweenness is continuously valued — Table S1 records 619 distinct weights against six for degree, a
Gini of 0.754, and a maximum 29.4 times the mean — and it concentrates on the sparse backbone and
articulation points, which are abundant in sparse near-tree-like graphs (Tian et al., 2017). At
⟨k⟩ = 2.520 with 22.4% of edges as bridges, the betweenness-weighted mode is structurally a
bridge-weighted mode.

Four qualifications attach. Betweenness weighting was run on the synthetic reference network only,
because exact betweenness is not tractable at 300,633 nodes across 100 networks at 2,400 trials each.
Both weighted modes are stochastic — each node removed with probability proportional to its centrality,
following the degree-dependent occupation formalism of Callaway et al. (2000) — not rank-ordered
deletion of the top-*k* nodes, so the literature on initial versus recalculated centrality does not
apply. Because removal probability is clipped at unity and betweenness weights are heavy-tailed, the
nominal parameter of 0.1889 overstates the realised removed fraction of 0.1498, and as the note to
Table 4 states, only the realised value shares an axis with the other modes. And neither weighted mode
models an organism; no pathogen or parasite computes centrality. They are bounding scenarios in the
sense used in robustness-envelope analysis (Trajanovski et al., 2013; Memmott et al., 2004). Uniform
removal is likewise a null structural scenario, not embolism, which nucleates in the largest veins and
propagates by vein size (Brodribb et al., 2016) and spreads between conduits only once most are
gas-filled (Avila et al., 2022).

Betweenness does carry partial hydraulic meaning. Across the four networks in Table S1 it correlated
with solved Kirchhoff flux at ρ = .184, .495, .511 and .629, against .078, .255, .178 and .342 for
degree — a moderate flux proxy, two to three times stronger than degree, but not equivalent to it.

Damage geometry proved more consequential than damage weighting. Uniform removal disperses damage across
the lamina, while a haustorial lesion, a bite, or a necrotic patch is spatially contiguous. Two
localised protocols run at matched realised removed fractions raised the median threshold from 0.1998 to
0.4951 under a single lesion and 0.4511 under ten lesions, factors of 2.46 and 2.27, with the localised
protocols less damaging in 100 of 100 networks for both. These appear in Table 16 and are worked through
in Results §7.2, with the interquartile ranges given in Table S3. Uniform removal is therefore a
conservative abstraction, and every threshold reported here is a lower bound. A contiguous disc removes
a compact region and leaves the remainder connected, so the network routes around the hole — the
behaviour expected of a single spatially embedded network, in which a finite localised hole does not
propagate (Berezin et al., 2015; Shao et al., 2015).

Connectivity does not predict tolerance to localised damage. Under a single lesion the association
between mean degree and the threshold vanished at ρ = −.000, p = 1.00, as did the loop-fraction
association at ρ = .007, p = .942; under ten lesions both were weak and non-significant at ρ = .151 and
.151, p = .13, against ρ = .737 and .731 under dispersed removal on identical draws. Fractal dimension
behaved oppositely, holding a moderate association under the multi-lesion protocol at ρ = .523, p < .001,
while remaining non-significant under a single lesion at ρ = .142, p = .159. Table S3 sets all four
scenarios side by side.

The contrast is mechanically coherent. Reticulation supplies alternative routes *between* regions, which
dispersed removal destroys and a single compact hole does not. A compact hole is defeated instead by how
thoroughly the network fills the plane — whether material outside the lesion is positioned to carry
rerouted flow — which is what fractal dimension measures. The result narrows the study's main claim and
rescues its secondary predictor.

Criterion choice was immaterial. Scoring both criteria on identical draws, the source-anchored threshold
was systematically lower than the giant-component threshold, a median of 0.1837 against 0.1998 and lower
in 100 of 100 networks, as expected when requiring connection to one designated node rather than
counting the largest surviving component. The two nevertheless ranked networks almost identically at
ρ = .912, and every association was preserved; Table 16 summarises this and Results §7.1 gives the
detail.

---

## Influence of Venation Architecture on the Critical Removed Fraction Under Dispersed Loss

Everything in this section applies to dispersed loss only.

All three descriptors were positively and significantly associated with the threshold. Table 6 gives
mean degree at ρ = .733, loop fraction at ρ = .727 and fractal dimension at ρ = .496, all at p < .001
across 100 networks, and Figure 8 plots each network against the two predictors. Each connectivity
measure held with the other axis partialled out, at ρ = .736 for mean degree given fractal dimension and
ρ = .502 for fractal dimension given mean degree, and the final column of the same table shows every
association strengthening under log network-size control, to ρ = .745, .740 and .633.

That strengthening is not what a size confound produces. If connectivity were tracking size, partialling
out log N would attenuate it. In Table S3 mean degree and loop fraction are unrelated to size at
ρ = .037 and .030, while the threshold rises weakly with it at ρ = .232, p = .020, so size is noise in
the outcome rather than a common cause. A two-predictor regression gave R² = .507, F(2, 97) = 49.93,
p < .001, with fully standardised coefficients of .526 for mean degree and .408 for fractal dimension,
and the two predictors were near-orthogonal at r = .148, p = .141, with a variance inflation factor of
1.02.

The empirical associations cannot establish causality. These are 100 species measured once each, and
leaf size, thickness, phylogeny, habitat, developmental history and tracing quality all covary without
all being measured. The regression leaves roughly half the between-network variance unexplained. No
phylogenetic correction was applied, so species are treated as independent across a sample spanning
ferns and angiosperms — a violation that affects the significance values though not the point estimates.

The synthetic grid addresses that limitation. Forty-two networks were generated with mean degree and
fractal dimension set by separate construction parameters, achieving near-independence of the two axes
at r = .086, a decoupling unavailable in a comparative sample and identified by Ronellenfitsch et al.
(2015) as necessary if topology and geometry are to be separated. Figure 9 plots the grid's coverage
against the measured cohort. With the axes decoupled, Table 7 shows the threshold tracking connectivity
almost deterministically at ρ = .991 and geometry only weakly at ρ = .227, with R² = .887.

The full-grid dominance ratio overstates the case. The grid's connectivity axis reaches ⟨k⟩ = 4.00
against an empirical maximum of 2.99, so 18 of its 42 cells lie outside the region real leaves occupy,
visible as the unmatched upper region of Figure 9. Restricting to the 24 cells inside the empirical
range gives a better fit and a smaller dominance, and the lower block of Table 7 reports β = .981 for
mean degree against .125 for fractal dimension, R² = .940, with partial correlations of .970 and .451.
Inside the region real leaves occupy, connectivity dominates and geometry is secondary rather than
negligible.

The grid establishes controlled attribution within the model: when the axes vary independently by
construction, essentially all threshold variation follows connectivity. It does not establish that the
effect size transfers to real leaves, since the grid networks have a degree standard deviation of 1.350
against the empirical 0.848 in Table 1 and their absolute thresholds are not comparable. It does not
establish causation *in planta*. And it does not remove geometry from the account, given the in-range
partial of .451 and the localised-damage result above.

Fractal dimension is 73% explained by log network size, so much of what it measures here is extent
rather than shape. Its association with the threshold nonetheless survives and strengthens under that
control, from ρ = .496 raw to ρ = .633 partial in Table 6, and residualising on log N gives ρ = .577 in
Table S3. It is a real, secondary, size-entangled predictor.

Loop fraction was positively associated with the threshold under both removal modes and more strongly
under degree weighting, at ρ = .727 and .818 in Table 8. Sorting the cohort into reticulation quartiles
gave a monotone gradient: Table 9 shows the median threshold rising from 0.1584 in the least reticulate
quartile to 0.2308 in the most, 7.2 percentage points more of its nodes and a relative gain of 45.7%,
with the extreme quartiles nearly disjoint at Mann–Whitney U = 4, p < .001 and Cliff's δ = 0.987. Yet
the final row of Table 8 shows the residual of loop fraction, after mean degree is partialled out,
having no association with the threshold at all: ρ = −.088, p = .386.

This does not mean loops are unimportant. Table 2 gives mean degree and loop fraction rank-correlated at
ρ = .994 across the characterised cohort. In a sparse planar graph they are close to the same
measurement — adding an edge between two existing junctions simultaneously raises mean degree and
converts bridges into cycle edges — and in Table S3 a cubic fit of loop fraction on mean degree recovers
R² = .917 with a residual standard deviation of 0.047. The residual against which the null test runs is
a small, noisy quantity, so finding no signal in it describes near-degeneracy of the two descriptors,
not irrelevance of loops. The relationship is not the graph identity loop fraction ≈ 1 − 2/⟨k⟩. That
holds for the cyclomatic fraction, exact to floating-point precision across all 120 traced networks,
while for the non-bridge loop fraction reported here the same table records it failing with a mean
absolute departure of 0.564. The collinearity is empirical, a property of sparse planar venation.

Mean degree and loop fraction therefore index one connectivity axis, and only mean degree enters the
regressions. Loop fraction is retained descriptively and where it carries mechanism. It does so in one
place: in Table 8 loop fraction's association is stronger under degree-weighted removal than uniform
removal, and bridge fraction correspondingly more negative. That asymmetry is the articulation-point
mechanism appearing in the data. A bridge-rich network has many single edges whose loss disconnects a
region, and those edges terminate on precisely the junctions centrality weighting removes (Tian et al.,
2017). Reticulation removes them.

Structural tolerance to dispersed element loss is a function of how many alternative routes survive an
average removal, and in a sparse planar network that number is set by how much of the edge budget has
been spent closing loops rather than extending branches.

---

## Raising Structural Tolerance Through Increased Reticulation

Raising each network's connectivity toward ⟨k⟩ = 2.811 — the 90th percentile of the percolation cohort's
own mean degree, so that no network was made denser than the most reticulate networks observed — raised
the median threshold from 0.2010 to 0.2150 across the 105-network enhancement cohort at 10,000 trials
per arm. Table 10 records that 93 networks improved, 12 were unchanged and none worsened, with a median
change of 0.0095, a range of 0.0000 to 0.0459 and a median relative gain of 5.5%; the Wilcoxon
signed-rank test on the 93 non-zero differences gave W = 0, p < .001, and the conservative Pratt
treatment across all 105 gave the same conclusion. In Figure 10 every network lies on or above the
diagonal, and Figure 11 shows the manipulation in one leaf, closing open vein endings into circuits
without altering the major-vein skeleton.

Each network serves as its own control. Loop addition modifies only the edge set, the node set is
unchanged, and both arms consumed an identical sequence of removal draws under common random numbers, so
Monte Carlo error is common to the arms rather than inflating the difference. Species identity, tracing
quality, network size, leaf shape, crop-window geometry and phylogeny are held exactly constant, being
properties of the same network in both arms. This is why the enhancement outranks the synthetic grid as
evidence about real leaves: the grid gives controlled attribution on artificial architecture, the
enhancement gives perturbational evidence on real architecture.

The gain depended strongly and negatively on initial connectivity. Table 11 gives ρ = −.821, p < .001,
with R² = .655, while fractal dimension was unrelated to the gain at ρ = −.034, p = .729. The sparser
the starting network, the larger the improvement. The six largest gainers, listed in Table 12, all began
near the lower bound of the cohort's connectivity range: *Clusia alata* at ⟨k⟩ = 2.195 with a gain of
0.0459, *Chloranthus spicatus* at 2.148 and 0.0458, *Anemopsis californica* at 2.216 and 0.0417,
*Metapanax davidii* at 2.198 and 0.0401, *Eurya japonica* at 2.249 and 0.0374, and *Smilax hispida* at
2.344 and 0.0339. At the other end, Table S2 records that all 12 networks which did not move had already
exceeded the ceiling, with initial mean degree from 2.8352 to 2.9893. Vein addition saturates once
inter-vein spacing falls below the relevant transport length scale (Noblin et al., 2008), so the twelve
unchanged networks are that prediction realised, not failures.

That dependence also disposes of the artefact explanation, that poorly traced leaves have spuriously low
mean degree and enhancement merely recovers missed veins. Raw differences among tracing-quality grades
were not significant at Kruskal–Wallis H = 6.981, p = .072, reported in Table 10 and again in Table S2,
so the premise fails at the outset. The artefact hypothesis also predicts the wrong sign: grade-A
networks started at the highest median initial connectivity of any grade, ⟨k⟩ = 2.665 against 2.472 for
grade B, so their smaller raw gain is what diminishing returns predicts, and Table S2 shows that after
controlling for baseline connectivity grade A carries the largest positive residual gain at +0.00201,
against −0.00019 for B, −0.00522 for C and −0.00062 for D.

Every quality partition holds, with no reversals anywhere. Reading down Table S2: the full cohort at
93 improved, 12 unchanged and 0 worsened; excluding all C-flagged networks, 79, 12 and 0 across 91
networks with a median gain of 0.0108; excluding all D-flagged networks, 40, 9 and 0 across 49;
retaining only A or B with no C and no D, 31, 9 and 0 across 40; the grade-A subset alone, 13, 8 and 0
across 21 with a sign test at p < .001; and the crop-edge-compliant subset, 92, 10 and 0 across 102.
Excluding over-segmented networks raises the median gain from 0.0095 to 0.0108 and the connectivity
association from ρ = .733 to ρ = .789, both in Table 16 — the opposite of an over-segmentation artefact,
since spurious minor veins inflate both mean degree and loop fraction and should dilute the result. The
grades are orthogonal defect types rather than a severity gradient: B is under-segmentation, C
over-segmentation, and D physical damage under 25% of the lamina.

The manipulation does not isolate loop topology. Adding an edge between two existing junctions raises
mean degree and loop fraction while lowering bridge fraction, terminal fraction and path length. The
experiment shows that this bundle raises structural tolerance; it cannot attribute the gain to loop
closure as distinct from degree increase, and given ρ = .994 no manipulation on real planar venation
could. The claim supported is that structural tolerance is manipulable rather than merely correlated —
connectivity is a lever, not only a marker.

The model has no cost term. Added veins carry construction cost, mechanical consequences and a
photosynthetic opportunity cost, none of them represented, so zero networks worsening is
single-objective optimisation against a structural criterion. Venation sits on a trade-off surface among
transport efficiency, cost and robustness (Ronellenfitsch & Katifori, 2019), and greater hydraulic
safety in real leaves comes with higher leaf mass per area and smaller leaf area (Nardini et al., 2012).
The enhancement cohort is also not the percolation cohort: it applies a weaker screen and contains 105
networks forming a superset of the 100, so its baseline median of 0.2010 is not the 0.1998 of Table 3.

A linear response surface fitted across networks predicts a median achievable gain of 0.0355 against the
0.0095 measured by rewiring, a factor of 3.74, and it over-predicts the baseline threshold itself at
0.2595 against 0.1998; Table S2 sets the two side by side. The surface extrapolates a between-network
regression to a counterfactual architecture and inherits every covariate that regression omits, while
the enhancement measures a within-network perturbation with those covariates fixed. They are not
mutually corroborating and must not be averaged. Where they disagree, the intervention is the result.

---

## Effect of a Literature-Calibrated Haustorial Sink on the Host Network

The sink was imposed as a hydraulic boundary condition on the solved potential field. It removes
nothing, and the percolation engine never reads a potential.

Calibrated to withdraw 20.0% of leaf throughput at an illustrative 1.5 MPa host–parasite gradient, at
K_h = 0.0392 and anchored on the roughly 18% hemiparasite floor of Jiang et al. (2003), the sink
depressed the minimum host leaf water potential to −1.0224 MPa and embolised no vessels at the modelled
−2.0 MPa threshold. Sweeping the gradient from 0.0 to 3.0 MPa in Table 5 left the margin positive
throughout, its smallest value 0.6779 MPa at 35.1% diversion, and Figure 7 shows the solved field with
the haustorium attached. Under the coupled model, in which a node is removed only if its potential falls
below the cavitation threshold, no network reached the collapse criterion at any haustorial attachment
density at the calibrated strength, as Figure 12 and Table S4 both show. The vertical axis of that
surface is the fraction of nodes *bearing a haustorium*, not the removed-node fraction of Tables 3, 4
and 9.

Three threshold-independent quantities explain the null. First, against a no-parasite baseline minimum
of −0.9963 MPa the sink depressed the network minimum by 0.0262 MPa, so 2.6% of the reported 0.978 MPa
margin is attributable to the parasite and the remaining 1.000 MPa is the stipulated gap between the
transpirational boundary condition and the cavitation threshold; the first row of Table 5 is effectively
the no-parasite baseline, and Table S4 gives the decomposition. Second, the depression at the haustorial
contact patch was 0.402 MPa at the illustrative gradient and exactly linear in the gradient at
0.2682 MPa per MPa across 0 to 12 MPa, with an intercept of approximately zero and a maximum residual of
0.017 MPa. Because K_h is specified relative to each node's own incident conductance, the reservoir's
weight in a tapped node's potential is fixed at K_h/(1 + K_h) = 0.0377 per node, independent of the
network, so the absence of embolism is an arithmetic consequence of the parameterisation rather than an
emergent property of venation topology. Third, reaching the −2.0 MPa threshold requires a gradient of
about 6.0 MPa, or a sink strength beyond 256 times the calibrated value, both of which Table S4 reports,
against a largest measured parasite–host leaf gradient of approximately 0.5 MPa (Griebel et al., 2022,
who recorded a host trunk depression of 0.60 MPa under mistletoe infection and 11 points of modelled
conductivity loss without hydraulic failure). The requirement is roughly twelve times the largest
measured value.

The null agrees with independent physiology. Scoffoni et al. (2017) report that outside-xylem
vulnerability explains most of the decline in whole-leaf conductance during dehydration, with no
minor-vein conduits embolised above turgor loss, and Avila et al. (2022) show connectivity-mediated
spread engaging only once most conduits are gas-filled. Minor-vein xylem is hard to embolise. Within
this model, haustorial harm is a resource drain rather than a rupture: the sink withdraws a fifth of
leaf throughput while moving the potential field by hundredths of a megapascal.

Four constraints bound that reading. The null is threshold-dependent and inverts. In Table 16 the
gradient required for the first embolised vessel rises from 1.1 MPa at a −1.00 MPa threshold, through
2.7 at −1.25 and 4.0 at −1.50, to 6.0 at −2.00 and 9.5 MPa at −3.00, with the full eight-threshold sweep
in Table S4; at −1.00 MPa the calibrated sink already embolises one vessel at the illustrative gradient.
The host's operating point matters more than the parasite: the same table shows that at a midday
potential of −2.5 MPa, 91 vessels embolise with no parasite present, rising only to 93 with the sink
attached. Coupling is not impossible, only distant, since a critical haustorial density first exists at
twice the calibrated strength and then only in the lowest-fractal-dimension row, at a density of 0.9384
meaning 94% of nodes would need a haustorium, and in every row at three times it. And the parameters are
literature-constrained rather than measured: the 1.5 MPa gradient is a review-level order-of-magnitude
value, no measurement of total water potential, osmotic potential or turgor has been published for any
*Cuscuta*–host interaction (Balios et al., 2025), and the diversion anchor is a hemiparasite floor
applied to a holoparasite.

None of this shows that real holoparasitism cannot cause hydraulic failure. It shows that within a model
parameterised from the available literature, hydraulic withdrawal alone did not bring the network near
the modelled cavitation threshold, so structural fragmentation and hydraulic sink stress are independent
lenses rather than two descriptions of one process. That independence is partly a property of the model
architecture, which is why it is reported as a decoupling and not as a discovery about parasitism. Node
deletion is also not what a haustorium does: *Cuscuta* searching hyphae acquire xylem identity and form
a continuous xylem bridge with the host, topologically an edge addition (Kaga et al., 2020). The removal
simulations represent loss of conducting function from any cause.

---

## Synthesis and Limitations

In sparse planar venation networks, the fraction of the edge budget committed to closing loops rather
than extending branches is the dominant architectural determinant of how much dispersed element loss the
network absorbs before its transport skeleton fragments. Four levels of evidence support this and should
not be collapsed: the association across 100 species in Table 6, at ρ = .733; the adjusted association
that strengthens under size control and under exclusion of over-segmented tracings, at ρ = .745 and .789
in Tables 6 and 16; the controlled attribution when the two axes are decoupled inside the observed
range, at β = .981 against .125 with R² = .940 in Table 7; and the within-network perturbation of
Table 10, in which 93 of 105 real networks improved and none worsened. Only the last two exceed
correlation, and only the last concerns real leaves.

A sparse network can be a tolerant one. Mean degree of 2.520 is barely above a tree, but the small
excess is spent almost entirely on cycles: as Table 1 shows, 77.6% of edges lie on at least one, leaving
22.4% as bridges. Tolerance depends not on edge count but on how many alternative routes survive an
average removal, and closing an areole converts two dead-end paths into one circuit at the cost of a
single edge. Reticulation is the cheapest available form of redundancy, a plausible reason for its
prevalence in angiosperm venation, and it connects this result to Katifori et al. (2010), Price and
Weitz (2014) and the direct measurement of Sack et al. (2008).

Two implications extend beyond leaves. Reticulation buys uniformity of risk as well as robustness: the
gap between uniform and degree-weighted thresholds narrows as reticulation rises, at ρ = −.786 for loop
fraction in Table 8 and ρ = −.793 for mean degree in Table S3, size-clean and unchanged under log-size
control, so more reticulate networks are less differentially exposed to the pattern of damage as well as
more tolerant of its amount. No precedent for this in venation was located. And damage geometry is a
first-order variable rather than a robustness check: holding the removed fraction identical and changing
only the spatial correlation of removals moved the threshold by a factor of 2.3 to 2.5 in 100 of 100
networks and inverted which descriptor predicts it, as Table 16 and Results §7.2 show.

As a comparative trait the critical removed fraction behaves well. It computes identically from 1,436 to
300,633 nodes, is near-invariant to the connectivity criterion at ρ = .912, and reproduces across an
independent re-implementation at ρ = .999 with a median absolute difference of 0.0011, per the note to
Table 16. It is not a physiological quantity and cannot be converted to percent loss of conductivity,
P50 or water potential. What makes it functionally meaningful is that severance of the water-supply path
within leaf veins causes immediate irreversible local tissue damage (Brodribb et al., 2021); this study
quantifies the structural conditions under which such severance becomes widespread, not the water
potentials that initiate it.

The limitations, ranked by how much they constrain interpretation, are as follows.

The critical removed fraction is computed on an unweighted adjacency matrix, so it is topological and no
hydraulic quantity enters it. The same independence that forbids a physiological reading immunises every
structural result against objections to the conductance model.

Simulated removal is not embolism. Real failure nucleates in the largest veins and propagates by size
(Brodribb et al., 2016), is spatially clustered (Pritzkow et al., 2022; Lu et al., 2025), and spreads
between conduits only once most are gas-filled (Avila et al., 2022). Uniform removal reproduces none of
these.

The main result is scope-limited to dispersed damage; under a single contiguous lesion the connectivity
association vanishes entirely.

The parasite model has no anatomical warrant for node deletion (Kaga et al., 2020), its parameters are
literature-constrained, and its central null is threshold-dependent and derivable from the relative-K_h
convention.

The only independent physical test is underpowered and the model is xylem-only, at ρ = .187 with a
confidence interval of −0.024 to 0.382 across 93 species.

One hundred of the 120 source networks are crop windows without petioles, and the source is a
widest-vein rule rather than an anatomical petiole, which matters because embolism initiates in
precisely the structures the windows exclude. Table 13 bounds this, with 105 of 120 networks inside both
tolerances, none of the failures entering the percolation cohort and three remaining in the enhancement
cohort including the largest gainer; but it cannot restore untraced material.

Mean degree and loop fraction are one axis at ρ = .994, so the effect cannot be attributed to loop
closure as distinct from degree increase — a limitation the enhancement inherits.

Fractal dimension is 73% log network size and must be reported residualised.

The enhancement has no cost term.

The synthetic grid extrapolates beyond the empirical range in 18 of 42 cells, which is why the
restricted 24-cell fit is the one reported; even restricted, its degree heterogeneity exceeds the
cohort's, so the attribution transfers but the effect size does not.

The finite-size sweep does not hold architecture constant. Table 14 shows that pinning fractal dimension
and mean degree still allowed loop fraction to drift from 0.692 to 0.561 across the size range, and loop
fraction is itself a predictor, so no finite-size claim is made in either direction; the empirical cohort
behaves in the opposite direction at ρ = .232. For the same reason the correspondence between the
observed giant-component-vanishing fraction of 0.524 and the Molloy–Reed prediction of 0.531 is an
order-of-magnitude check only, since that framework assumes a locally tree-like graph while a planar mesh
is dense in short loops, and the two are in any case different criteria from the fragmentation threshold.

Betweenness-weighted removal was run on the synthetic reference network only.

Giant-component fragmentation is a structural proxy for transport continuity, not a measurement of it.
It treats all surviving nodes as equivalent regardless of position or calibre and does not distinguish a
network that has lost half its area from one split into functional halves. The alternative criterion
shifted the level and changed no conclusion, at ρ = .912.

No phylogenetic correction was applied, and tracing-quality grades are non-ordinal defect types
incompletely recorded in the archive.

Roughly half the between-network variance in the threshold is unexplained, at R² = .507, so no claim of
a complete architectural account is defensible.

One supplementary result requires its status fixed. Because fragmentation and complete loss of the giant
component are two criteria on the same removal process, a network losing nodes progressively crosses the
first before the second, and modelling infestation as logistic growth on the synthetic reference network
produced separations of 7.25, 4.35 and 2.72 growth-time units at slow, moderate and aggressive
stipulated rates, tabulated in Table 15 and plotted in Figure 14 of the Supplementary Materials. The
existence and contraction of that separation is a property of the two criteria. The numerical values are
not calendar times: the growth rate was stipulated rather than fitted to a measured infestation
time-course, the thresholds are the synthetic network's rather than the cohort's, and the model contains
no symptom variable. The analysis does not demonstrate or bound a physiological pre-symptomatic window.
