# DISCUSSION

This study asked whether the architecture of a leaf's venation network determines how much of that
network can be lost before it fragments, and whether that tolerance can be shifted by adding
reticulation. Across 100 traced venation networks the answer to both questions is yes, under a set of
scope conditions that the analyses themselves establish and that are stated here rather than deferred.
The discussion below is organised around the strength of the evidence rather than the order of the
Results, because the study's five lines of evidence — cross-sectional association, adjusted
association, controlled synthetic attribution, within-network perturbation, and an independent
hydraulic model — do not license conclusions of equal strength, and treating them as though they did
would be the single easiest way to overstate what was found.

Three distinctions are maintained throughout and are not rhetorical. First, **structural
fragmentation is not demonstrated hydraulic failure**: the critical removed fraction p_c is computed on
an unweighted adjacency matrix, and no water potential, conduit radius or modelled conductance enters
its calculation. Second, **simulated node removal is not embolism**: it is a generic representation of
loss of conducting function, and the literature is explicit that real embolism is neither uniform nor
independent (Brodribb et al., 2016; Pritzkow et al., 2022; Lu et al., 2025). Third, **p_c is not f_c**:
p_c is the removed fraction at which the giant connected component falls below half its undamaged size
with probability .50, whereas f_c is the removed fraction at which the giant component vanishes
altogether. These are two criteria applied to the same network, and the numerical gap between them is a
property of the criteria, not a second finding.

---

## 1. The Architecture of the Cohort, and Why It Is the Precondition for Everything That Follows

The empirical networks occupy a narrow and unusual region of graph space, and that position — not any
single descriptor — is what makes the damage-tolerance question tractable and what predicts most of
what the removal simulations subsequently found.

The cohort is **sparse** (Table 1). Median mean degree was 2.520 across the 112 characterised networks (M = 2.544,
SD = 0.200, range [2.148, 2.989]), with a median degree standard deviation of 0.848 and a maximum node
degree of four to five. A planar graph of N nodes admits at most 3N − 6 edges, so ⟨k⟩ could in
principle approach six; the observed ceiling of 2.989 sits at roughly half that, and the entire cohort
spans only 0.84 units of mean degree. This is a bounded, near-degenerate degree distribution in the
technical sense used in the network literature, and it is exactly the distribution class for which
degree-based ranking carries little discriminating information (Mou & Hayashi, 2025). The consequence
is anticipatory rather than retrospective: a cohort with this degree distribution *should* show only a
modest penalty when removal is weighted toward high-degree nodes, because the robust-yet-fragile
asymmetry described by Albert et al. (2000) is a property of heterogeneous, heavy-tailed degree
distributions, not of narrow ones. Section 2 reports precisely that.

At the same time the cohort is **highly redundant relative to its sparseness**. A median 77.6% of veins
lay on at least one cycle (range [0.320, 0.995]), leaving a median bridge fraction of 0.224 (Table 1).
Figure 2 shows a representative traced network reduced to the nodes and edges the analysis actually
operates on, and Figure 3 the calibrated synthetic mesh at the same reduction. Those two
facts together — ⟨k⟩ barely above the tree value of 2, yet three-quarters of edges on cycles — describe
a network that has spent its very limited edge budget almost entirely on closing loops rather than on
extending branches. This is the structural signature of the areolate minor-vein network described in
the Introduction, and it is what Katifori et al. (2010) and Price and Weitz (2014) identify as the
architecture that permits flow to be rerouted around a break. It is also why the loss of an individual
vein need not sever supply beyond it, which is the empirically measured behaviour: severing the midrib
of a pinnately veined leaf removes roughly three-quarters of its hydraulic conductance, whereas damage
to second- and higher-order veins is tolerated with no detectable hydraulic penalty because the
reticulate minor-vein network supplies parallel paths (Sack et al., 2008).

The networks are also **almost entirely connected before any damage is applied** (median GCC fraction
1.000, M = 0.998, minimum 0.850; Table 1). This is a methodological precondition rather than a biological
finding: a percolation threshold measured on a network that is already fragmented would be
uninterpretable. It also bounds a possible objection. Restricting the analysis to the 99 networks with
a baseline GCC fraction above .99 changed the connectivity association from ρ = .733 to ρ = .731 and
the enhancement result from 93/12/0 improved/unchanged/worsened to 91/12/0 (Table 16, final row), so the
single substantially fragmented tracing is not carrying any result.

**Network size and fractal dimension are not independent descriptors of this cohort, and must not be
interpreted as though they were.** Median network size was 15,404 nodes with a range of [421, 300,633]
across the characterised set (Table 1) — four and a half orders of magnitude — and fractal dimension was
rank-correlated with size at ρ = .880, with log size explaining 73% of the variance in D (Table 6 note;
Table S3). Box-counting
dimension is estimated over a finite range of box sizes, and a larger traced region supports a longer
scaling range (Muraleedharan et al., 2023); the correlation is therefore expected and is a measurement
property as much as a biological one. This does not make D uninformative, as Section 3 shows, but it
does mean that every statement about D in this study is reported with network size controlled, and that
the raw D–p_c correlation cannot be read as a pure geometry effect.

It is worth separating four terms that are frequently conflated and that this study measures
separately. **Connectivity** is ⟨k⟩, the mean number of veins meeting at a junction — an edge-budget
quantity. **Reticulation** is the closing of that budget into cycles, indexed here by loop fraction;
it is not the same construct as ⟨k⟩ even though, in these networks, it is nearly the same *measurement*
(ρ = .994; see Section 4). **Redundancy** is the functional consequence — the existence of more than
one path between two regions — and is what the bridge fraction inversely quantifies. **Geometric
complexity and spatial occupation** are D, how thoroughly the network fills the plane, which is
logically independent of how its edges are wired and is shown to be empirically separable in Section 3.
None of the four is **hydraulic function**, which is a conductance-weighted quantity that the
percolation analysis never touches and that Section 8 shows this model predicts only weakly.

---

## 2. Structural Damage Tolerance Under Uniform and Degree-Weighted Removal

Under uniform removal the cohort fragmented at a median removed fraction of 0.1998 (M = 0.1847,
SD = 0.0541, range [0.0262, 0.2698], n = 100, 2,400 Monte Carlo trials per network per mode; Table 3).
What that threshold measures is shown directly in Figure 6, where the giant component breaks into
disconnected islands as the removed fraction crosses it, and is summarised as a collapse probability in
Figure 4. The practical reading is that a median leaf venation network loses global connectivity after roughly one
junction in five is disabled. This is a per-network architectural index and is comparable across
species in a way that a collapse *curve* is not; it is the quantity that Mander and Williams (2024)
approach with a fixed-fraction criterion and that Price and Weitz (2014) approach through an
area-under-curve summary. It should not be read as a critical point in the statistical-physics sense.
A fixed-fraction criterion evaluated at P = .50 is an operational definition, chosen because it is
computable identically on every network in a cohort spanning four and a half orders of magnitude in
size; it is not a singularity, and no critical exponent or universality claim is made anywhere in this
study.

When removal probability was weighted by node degree, the median threshold fell to 0.1685 — a
reduction of 15.7% in the tolerable removed fraction, with a median paired difference of 0.0305
(M = 0.0288, SD = 0.0103). The Wilcoxon signed-rank test rejected equality (W = 0, p < .001), and the
matched-pairs rank-biserial correlation was 1.00 because **the uniform threshold exceeded the
degree-weighted threshold in 100 of 100 networks, with no exceptions and no ties** (Table 3). The
corresponding leftward shift of the collapse curve can be seen by comparing Figure 5 with Figure 4. It is worth being
precise about what the rank-biserial value of 1.00 records and what it does not. It records perfect
directional consistency: every network in the cohort responded in the same direction. It does not
record a large magnitude. The magnitude is the median paired difference of 0.0305, which is roughly a
sixth of the baseline threshold, and the standard deviation of that difference across networks is
0.0103 — computed as the standard deviation of the 100 per-network differences, not from the two
column standard deviations, which describe between-network variation rather than the within-network
effect. Because the two arms are correlated at r = .984 across networks, the between-network spread
largely cancels in the difference, which is the entire purpose of a paired design.

The mechanistic reading is that **where loss falls matters independently of how much is lost**. A
junction of degree four sits on more paths than a junction of degree two, so removing it destroys more
alternative routes per node removed. Biasing removal toward such junctions therefore reaches the
fragmentation criterion after fewer total removals. That the effect is real but modest is the
prediction that follows directly from Section 1: with degrees bounded at four to five and a standard
deviation of 0.848, the degree weighting has little to work with. In the synthetic reference network
the degree weights had a Gini coefficient of 0.274, a maximum of 2.4 times the mean, and only six
distinct values, with 32% of nodes tied in a single group (Table S1). A "targeted" removal on such a weight vector
is, in a substantial fraction of draws, barely distinguishable from a uniform one. The small gap is
therefore not a weakness of the finding but a confirmation that the cohort belongs to the network class
its architecture places it in.

The ordering was reproduced and extended on the calibrated synthetic reference network (N = 1,023),
where the trial budget permits far tighter intervals (Table 4): 0.2711 under uniform removal at 1,000,000 trials
(95% CI [0.2700, 0.2720]), 0.2023 under degree weighting at 100,000 trials, and 0.1498 under
betweenness weighting. **Weighting removal toward a global path property was more damaging than
weighting it toward a local one.** This ordering is the reverse of what is commonly reported for
scale-free networks, but it is the ordering expected for this network class. In a planar graph with
bounded degree, a degree ranking is largely a ranking of ties; betweenness is continuously valued —
619 distinct weights against six for degree, with a Gini of 0.754 and a maximum 29.4 times the mean —
and it concentrates on the sparse backbone and on articulation points, which are abundant in sparse,
near-tree-like graphs (Table S1; Tian et al., 2017). At ⟨k⟩ = 2.520 with 22.4% of edges as bridges, these
networks are firmly in the articulation-point-rich regime, and the betweenness-weighted mode is,
structurally, a bridge-weighted mode. The correspondence with the bridge-fraction correlations reported
in Section 4 is not a coincidence but the same structural fact measured twice.

Four caveats attach to the betweenness result and none is optional. First, it was computed on the
**synthetic reference network only**; exact betweenness centrality requires a single-source shortest-path
computation from every node, which is not tractable at 300,633 nodes across a 100-network cohort at
2,400 trials per network, so the empirical cohort was run under uniform and degree-weighted removal
only. Second, the removal modes here are **weighted stochastic removal**, in which each node is removed
with probability proportional to its centrality — the degree-dependent occupation formalism of Callaway
et al. (2000) — and not rank-ordered deletion of the top-k nodes. The literature on initial versus
recalculated centrality therefore does not apply. Third, because removal probability is clipped at
unity and the betweenness weights are heavy-tailed, the nominal control parameter overstates the
realised removed fraction: the betweenness threshold is 0.1889 as a control parameter but 0.1498 as a
realised removed fraction, and only the latter is on the same axis as the uniform and degree-weighted
values (Table 4; Table S1). The 95% confidence interval reported for that mode, [0.1879, 0.1902], is on the nominal axis;
no interval is available on the realised axis, and the two must not be quoted together as though they
were. Fourth, and most important biologically, **neither weighted mode is a model of any organism's
behaviour.** No pathogen, herbivore or parasite computes centrality. They are structural bounding
scenarios in the sense used in robustness-envelope analysis (Trajanovski et al., 2013), and the use of
connectivity-ordered removal as a bounding device rather than a mechanistic hypothesis has precedent in
biological network analysis (Memmott et al., 2004). Uniform removal is likewise a null structural
scenario, not a model of embolism: optical imaging of dehydrating leaves shows that embolism nucleates
in the largest veins and propagates in a sequence set by vein size (Brodribb et al., 2016), and spread
between conduits is largely prevented by interconduit pit membranes until the majority of conduits are
already gas-filled (Avila et al., 2022). Uniform removal is neither size-ordered nor spatially
correlated, and so it reproduces neither property of real embolism.

Whether betweenness weighting has any hydraulic meaning was tested directly rather than assumed. Across
four networks, node betweenness correlated with solved Kirchhoff flux at Spearman ρ = .184, .495, .511
and .629, against ρ = .078, .255, .178 and .342 for degree (Table S1). Betweenness is therefore a **moderate**
flux proxy, two to three times stronger than degree, and clearly not equivalent to flux. That result
converts a design choice into a measured property and bounds its interpretation: betweenness-weighted
removal preferentially removes higher-flux junctions, but it is not a simulation of flux-ordered
failure.

---

## 3. Connectivity Versus Fractal Dimension: From Association to Controlled Attribution

Across the percolation cohort all three architectural descriptors were positively and significantly
associated with the threshold: mean degree ρ = .733, loop fraction ρ = .727 and fractal dimension
ρ = .496 (all p < .001, n = 100; Table 6, plotted in Figure 8). Each connectivity measure retained its association with the other
axis partialled out (partial ρ = .736 for ⟨k⟩ given D; ρ = .502 for D given ⟨k⟩), and — importantly —
**every association strengthened rather than weakened when log network size was controlled**, to ρ =
.745, .740 and .633 respectively (Table 6, final column). A two-predictor regression on z-scored
predictors gave
p_c = 0.1847 + 0.0285 z⟨k⟩ + 0.0221 zD, R² = .507, F(2, 97) = 49.93, p < .001, with fully standardised
coefficients of .526 and .408. The two predictors were near-orthogonal in this cohort (Pearson r = .148,
p = .141; VIF = 1.02), so the regression is not distorted by collinearity between them.

That the associations *strengthen* under size control matters more than their raw magnitude, because it
is the pattern a confound would not produce. If the connectivity result were an artefact of network
size — larger tracings being both denser and more tolerant — partialling out log N would attenuate it.
It does the opposite. The reason is visible in the underlying correlations (Table S3): mean degree and loop
fraction are uncorrelated with size (ρ = .037, p = .717 and ρ = .030, p = .766), whereas the threshold
itself rises weakly with size (ρ = .232, p = .020), so size is a source of noise in the outcome rather
than a common cause of both variables. Removing it sharpens the signal.

None of this establishes that connectivity is the unique causal determinant, and it is worth being
explicit about why not. These are 100 species measured once each. Mean degree, loop fraction, fractal
dimension, network size, leaf size, leaf thickness, phylogenetic position, habitat and tracing quality
all covary in a comparative dataset, and only some of them were measured. The regression explains
R² = .507 of the variance, so **roughly half the between-network variance in the threshold lies outside
the descriptors measured here**, and any of that unmeasured half could in principle be the operative
variable. No phylogenetic correction was applied and species are treated as statistically independent
across a sample spanning ferns and angiosperms, which is a real violation of the independence
assumption underlying the significance values, even though it does not affect the point estimates.

This is exactly the limitation the synthetic grid was built to address. Forty-two networks were
generated in which mean degree and fractal dimension were set by two separate construction parameters,
achieving near-independence of the two axes (Pearson r = .086, Spearman ρ = .222; Table 7, with the
coverage of the two axes plotted against the measured cohort in Figure 9) — a decoupling that
cannot be arranged in a comparative sample and that Ronellenfitsch et al. (2015) identify as necessary
if topology and geometry are to be separated. With the axes decoupled, the threshold tracked
connectivity almost deterministically (ρ = .991) and geometry only weakly (ρ = .227), and the fitted
surface was p_c = −0.0907 + 0.1202 ⟨k⟩ + 0.0287 D, R² = .887, F(2, 39) = 152.61, p < .001. The
degree-weighted mode gave the same picture more sharply still (ρ = .993 and .206; R² = .938).

The full-grid dominance ratio of approximately 14 to 1 in standardised units (β = .933 against .067)
should not be the number that is quoted, and the reason is a design limitation rather than a
statistical one. **The grid's connectivity axis extends to ⟨k⟩ = 4.00 against an empirical maximum of
2.99**, so 18 of its 42 cells lie outside the region any real leaf in this cohort occupies — the
extrapolation is visible as the unmatched upper region of Figure 9 — and a
dominance ratio computed partly on extrapolated architecture is not a claim about leaves. Restricting
the fit to the 24 cells inside the empirical range gives a **better** fit and a **smaller**, more
defensible ratio: standardised β = .981 for mean degree against .125 for fractal dimension, a ratio of
7.8 to 1, with R² = .940, F(2, 21) = 164.12. The corresponding partial correlations are r = .970 for
mean degree controlling for fractal dimension and r = .451 for fractal dimension controlling for mean
degree — the latter **more than double** its full-grid value of .195. The honest summary is therefore
the restricted one: inside the architectural region real leaves occupy, connectivity is the dominant
axis and geometry is secondary rather than negligible.

What this experiment establishes is a **controlled attribution within the model**: when the two axes
are varied independently by construction, essentially all of the variation in the threshold follows the
connectivity axis. What it does not establish is threefold. It does not establish that the *effect
size* transfers to real leaves; the grid networks are generated meshes with a degree standard deviation
of 1.350, considerably more heterogeneous than the empirical 0.848, and their absolute thresholds are
not comparable with the cohort's. It does not establish that connectivity is causal *in planta*, since
no real leaf was rewired by the experimenter and no developmental mechanism is implicated. And it does
not license the removal of geometry from the account: the in-range partial of .451 for D is a
substantial adjusted association, and Section 6 reports the one damage geometry under which fractal
dimension is the *only* surviving predictor.

Fractal dimension deserves a specific verdict rather than a hedge. It is 73% explained by log network
size, so a substantial part of what it measures in this cohort is extent rather than shape. Its
association with the threshold nonetheless **survives and strengthens** under that control, from
ρ = .496 raw to ρ = .633 partial (Table 6), and residualising D on log N gives ρ = .577 (Table S3). It is a real, secondary,
size-entangled predictor. It should be reported residualised, it should not lead the account, and it
should not be dismissed.

---

## 4. Reticulation, Bridge Dependence, and the Collinearity That Bounds the Claim

Loop fraction was positively associated with the threshold under uniform removal (ρ = .727) and more
strongly under degree-weighted removal (ρ = .818), with bridge fraction — its exact complement —
carrying the identical associations with reversed sign (Table 8). Sorting the cohort into reticulation quartiles
produced a monotone gradient in tolerance: median p_c rose from 0.1584 in the least reticulate quartile
(median loop fraction 0.616, median ⟨k⟩ 2.320) to 0.2308 in the most reticulate (median loop fraction
0.901, median ⟨k⟩ 2.734; Table 9). The most reticulate quartile tolerated the removal of
7.2 percentage points more of its nodes, a relative gain of 45.7% — and the two extreme quartiles were nearly
disjoint distributions (Mann–Whitney U = 4, p < .001, n = 25 per group; Cliff's δ = 0.987).

Against that, one result must be reported and interpreted rather than buried: **the residual of loop
fraction after mean degree is partialled out has no association with the threshold** (ρ = −.088,
p = .386; Table 8, final row). Loop fraction does not predict tolerance beyond ⟨k⟩. It would be a straightforward
misreading of this study to write that reticulation independently causes damage tolerance, and that
sentence does not appear anywhere in it.

The correct interpretation follows from the measurement relationship rather than from a substantive
one. Mean degree and loop fraction are rank-correlated at ρ = .994 across the characterised cohort
(Table 2; Pearson r = .972, Table S3). In a sparse planar graph the two are close to being the same measurement: adding an
edge between two existing junctions simultaneously raises ⟨k⟩ and converts bridge edges into cycle
edges, and there is very little room for a network to have one without the other. A cubic fit of loop
fraction on mean degree recovers R² = .917 with a residual standard deviation of only 0.047
(Table S3). The
residual against which the null test is run is therefore a small, noisy quantity, and finding no signal
in it is a statement about the **near-degeneracy of the two descriptors**, not about the irrelevance of
loops. This point is worth making explicitly because a plausible-sounding but false version of it
circulates: the relationship is *not* the graph identity loop fraction ≈ 1 − 2/⟨k⟩. That identity holds
for the cyclomatic (cycle-rank) fraction, where it holds to floating-point precision across all 120
traced networks (maximum |difference| = 2.5 × 10⁻¹⁶, Table S3); for the
non-bridge loop fraction actually reported here it fails badly, with a mean absolute departure of 0.564
and a non-bridge fraction 3.63 times the cycle-rank fraction on average (Table S3). The collinearity is empirical
and is a property of sparse planar venation, not an algebraic tautology.

The operational conclusion is that **⟨k⟩ and loop fraction index one connectivity axis and only one
should be entered as a predictor**, which is why mean degree and fractal dimension — and not loop
fraction — are the two variables in every regression reported. Loop fraction is retained as a
descriptive quantity and as the natural language in which the mechanism is stated, and the bridge
decomposition is retained where it carries mechanism, because it does carry mechanism in one specific
place. Loop fraction's association with the threshold is *stronger* under degree-weighted removal
(.818) than under uniform removal (.727), and bridge fraction correspondingly more negative (Table 8).
That asymmetry is not a restatement of the connectivity result; it is the articulation-point mechanism
appearing in the data. A bridge-rich network has many single edges whose loss disconnects a region, and
those edges terminate on precisely the junctions that centrality weighting preferentially removes
(Tian et al., 2017). Reticulation is what removes them from the network.

The mechanism, stated without overclaiming, is this: **a leaf's structural tolerance to dispersed
element loss is a function of how many alternative routes survive around an average removal, and
in a sparse planar network the number of surviving alternative routes is set by how much of the edge
budget has been spent on closing loops rather than on extending branches.** This is the structural
substrate for the hydraulic behaviour Sack et al. (2008) measured directly, and it is the same
architectural property that Katifori et al. (2010) and Price and Weitz (2014) identify as the basis of
resilience in venation. What this study adds is a per-network quantification of it across a large real
cohort, and — in Section 5 — an intervention on it.

---

## 5. Reticulation Enhancement: The Perturbational Test, and Its One Real Confound

Raising each network's connectivity toward a ceiling of ⟨k⟩ = 2.811 — the 90th percentile of the
percolation cohort's own mean degree, so that no network was made denser than the most reticulate
networks actually observed — raised the median threshold from 0.2010 to 0.2150 across the 105-network
enhancement cohort at 10,000 trials per arm (Table 10). Figure 10 shows that every network lies on or
above the diagonal, and Figure 11 shows what the manipulation does structurally in one network:
added areole closures shorten open vein endings into redundant circuits without altering the
major-vein skeleton. **Ninety-three networks improved, 12 were unchanged, and
none worsened** (median Δp_c = 0.0095, M = 0.0123, SD = 0.0109, range [0.0000, 0.0459]; median relative
gain 5.5%). The Wilcoxon signed-rank test on the 93 non-zero differences gave W = 0, p < .001, and the
more conservative Pratt treatment across all 105 networks — which retains rather than discards the
ties — gave the same conclusion (p < .001), with a matched-pairs rank-biserial correlation of
approximately 1.00.

This is the strongest evidence in the study, and the reason is structural rather than statistical.
A cross-sectional correlation between ⟨k⟩ and p_c compares different species, and every unmeasured
difference between those species is a candidate explanation. The enhancement compares **each network
with itself**: loop addition modifies only the edge set, the node set is unchanged, and both arms
consumed an identical sequence of removal draws under common random numbers, so the Monte Carlo error
is common to the two arms and the difference is not inflated by simulation noise. Species identity,
tracing quality, network size, leaf shape, crop-window geometry and phylogeny are all held exactly
constant by construction, because they are properties of the same network in both arms. That is why the
enhancement sits above the synthetic grid in the evidence hierarchy for *real* leaves: the grid gives
controlled attribution on artificial architecture, the enhancement gives perturbational evidence on
real architecture.

The magnitude is small and its smallness is explicable rather than embarrassing. The gain depended
strongly and negatively on each network's initial connectivity (ρ = −.821, p < .001; R² = .655 for the
two-predictor model), while fractal dimension was unrelated to it (ρ = −.034, p = .729; standardised
β = −.816 against .066; Table 11). **The sparser the starting network, the larger the improvement.** The six
largest gainers all began near the lower bound of the cohort's connectivity range — *Clusia alata*
(⟨k⟩ = 2.195, Δp_c = 0.0459), *Chloranthus spicatus* (2.148, 0.0458), *Anemopsis californica* (2.216,
0.0417), *Metapanax davidii* (2.198, 0.0401), *Eurya japonica* (2.249, 0.0374) and *Smilax hispida*
(2.344, 0.0339; Table 12) — while **all 12 networks that did not move at all had already exceeded the
ceiling before the manipulation**, with initial ⟨k⟩ ranging from 2.8352 to 2.9893 (Table S2). The mechanism is saturation:
vein addition has a
diminishing return once inter-vein spacing falls below the relevant transport length scale, which is
the physical result Noblin et al. (2008) established for vein density and hydraulic efficiency. A leaf
already near its own reticulation plateau has little left to gain, and the twelve unchanged networks
are that prediction realised rather than a set of failures.

That dependence also disposes of the most obvious artefactual explanation. It is reasonable to worry
that the gain is an artefact of imperfect tracing — that poorly traced leaves have spuriously low ⟨k⟩
and that "enhancement" is recovering veins the tracing missed. **The raw differences among tracing-
quality grades were not statistically significant** (Kruskal–Wallis H = 6.981, p = .072; Table 10 and
Table S2), so the
premise of that objection is not established in the first place. More decisively, the artefact
hypothesis predicts the wrong sign. Grade-A networks — those with no recorded vein-level defect —
started at the *highest* median initial connectivity of any grade (⟨k⟩ = 2.665 against 2.472 for
grade B), so the smaller raw grade-A gain is exactly what the diminishing-returns relationship
predicts. After controlling for baseline ⟨k⟩, grade A has the **largest positive residual gain**
(+0.00201, against −0.00019 for B, −0.00522 for C and −0.00062 for D; Table S2). The grade effect on the raw
gain is mediated by baseline connectivity, and the residual test that remains significant
(H = 19.266, p < .001) points in the direction opposite to measurement recovery.

The result survives every quality partition attempted, with zero reversals anywhere (Table S2): the full cohort
(n = 105; 93 improved, 12 unchanged, 0 worsened; median 0.0095), excluding every network carrying a
C flag (n = 91; 79/12/0; median 0.0108), excluding every network carrying a D flag (n = 49; 40/9/0;
median 0.0070), retaining only networks flagged A or B with no C and no D (n = 40; 31/9/0; median
0.0079), the artefact-free grade-A subset alone (n = 21; 13/8/0; median 0.0069; sign test p < .001;
Pratt p < .001), and the crop-edge-compliant subset (n = 102; 92/10/0; median 0.00995). Excluding all
over-segmented networks *raises* the median gain from 0.0095 to 0.0108 and *raises* the connectivity
association from ρ = .733 to ρ = .789 (Table 16). This is the opposite pattern from what an over-segmentation
artefact would produce, since spurious minor veins inflate both ⟨k⟩ and loop fraction and should
therefore be diluting the result rather than creating it. The quality grades themselves must not be
treated as a severity gradient: the source deposit defines them as orthogonal defect *types* — B is
under-segmentation, C is over-segmentation, D is physical damage to under 25% of the lamina — with
opposite effects on connectivity, and the archive retains only the leading flag of a comma-separated
code, hiding 4 over-segmented and 28 damaged networks inside other leading grades. Any statement of the
form "A > B > C > D" would be invalid, and none is made.

**The confound that does apply, and that is not disposed of, is that the manipulation is not a clean
isolation of loop topology.** Adding an edge between two existing junctions raises mean degree, raises
loop fraction, lowers bridge fraction, lowers terminal fraction and shortens path lengths, all at once.
The experiment therefore demonstrates that *this bundle* of connectivity changes raises structural
tolerance; it cannot attribute the gain to loop closure as distinct from degree increase, and given the
ρ = .994 collinearity documented in Section 4, no manipulation performed on real planar venation could
separate them. The claim the study is entitled to make is that **structural tolerance is manipulable,
not merely correlated** — that connectivity is a lever and not only a marker. It is not entitled to
decompose that lever into independent components.

Two further limits are worth stating plainly. First, **the model contains no cost term.** Added veins
carry construction cost, mechanical consequences and a photosynthetic opportunity cost, none of which
is represented, so "zero networks worsened" is a statement about single-objective optimisation against
a purely structural criterion. Venation architecture is understood to sit on a trade-off surface among
transport efficiency, construction cost and damage robustness (Ronellenfitsch & Katifori, 2019), and
in real leaves greater hydraulic safety is associated with higher leaf mass per area, thicker conduit
walls and smaller leaf area (Nardini et al., 2012). The direction of the result is a robustness
statement, not a design recommendation. Second, **the enhancement cohort is not the percolation
cohort.** It applies a weaker screen (N ≥ 1,000 and current p_c ≥ 0.02) and contains 105 networks that
form a superset of the 100-network percolation cohort, adding *Carex pensylvanica*, *Clusia alata*,
*Dichondra febrilis*, *Parthenocissus tricuspidata* and *Ribes viburnifolium*. Its baseline median of
0.2010 is therefore not the 0.1998 of Table 3 and the two must not be quoted interchangeably. Three of
the five additions fall outside the crop-edge tolerance, and one of those, *Clusia alata*, is the
largest single gainer in the study.

A final quantitative reconciliation belongs here rather than being left for a reviewer to find. A
linear response surface fitted across networks predicts a median achievable reticulation gain of 0.0355,
against the 0.0095 actually measured by rewiring each network — a factor of **3.74** (Table S2). The surface also
over-predicts the baseline threshold itself, giving a median of 0.2595 against the measured 0.1998.
These two analyses answer different questions: the surface extrapolates a *between-network* regression
to a counterfactual architecture and inherits every covariate that regression omits, whereas the
enhancement measures a *within-network* perturbation with those covariates held fixed. They are not
mutually corroborating and must never be averaged. **Where they disagree, the intervention is the
result and the surface is the extrapolation.**

---

## 6. The Geometry of Damage: Differential Exposure, and the Scope Condition on the Whole Result

Reticulation does not only raise the threshold; it changes how much the threshold depends on *where*
loss falls. The gap between the uniform and degree-weighted thresholds narrowed as reticulation
increased (loop fraction × gap, ρ = −.786, p < .001, Table 8; ⟨k⟩ × gap, ρ = −.793, Table S3), and this
relationship was essentially unchanged under log-size control (ρ = −.789) with the gap itself
uncorrelated with network size (ρ = .046, p = .647; Table S3). More reticulate networks lost proportionately less of their tolerance when
removal was concentrated on structurally important junctions rather than distributed at random.

The structural interpretation is a direct consequence of Section 4's mechanism. What degree weighting
exploits is dependence on particular junctions; what a bridge is, is a dependence on a particular edge.
A network in which three-quarters of edges lie on cycles simply has fewer such dependencies to exploit,
so biasing removal toward high-centrality nodes buys the removal process less advantage. Reticulation
therefore purchases two distinguishable things: a higher absolute tolerance, and a **narrower spread of
outcomes across damage patterns**. The second is arguably the more interesting property, because it is
a statement about the variance of the response and not only its mean, and no precedent for it in
venation was located in this study's literature passes. It should be stated as a novel structural
finding with a mechanism (Tian et al., 2017), not as a literature-supported one.

That said, the same analysis exposes the study's most consequential scope condition, and it is
reported here rather than in the limitations because it qualifies the principal claim rather than
merely attending it. Uniform removal disperses damage across the entire lamina, whereas a haustorial
lesion, a bite mark or a necrotic patch is spatially contiguous. Two localised protocols were run at
**matched realised removed fractions**, so the horizontal axis is identical to the dispersed case: a
single growing lesion removing the nodes nearest a random centre, and ten simultaneous lesions grown
round-robin from ten random centres, each replicate drawing its centres once and growing nested lesions
across the sweep.

**Localised damage was far less damaging than dispersed damage.** The median critical removed fraction
rose from 0.1998 under dispersed removal to 0.4951 under a single lesion and 0.4511 under ten lesions
(Table 16 and Results §7.2; interquartile ranges [0.4620, 0.5069] and [0.4247, 0.4687] in Table S3) — increases of 0.291 and 0.251, factors of 2.46 and
2.27. The localised protocols were less damaging in **100 of 100 networks for both protocols, without a
single exception** (Wilcoxon p < .001 for both). This answers, in the study's own data rather than by
analogy, the most obvious objection to the whole framework: that a parasite or a lesion is a local
event, not a uniform sprinkle. It answers it in the study's favour. Uniform removal is a **conservative**
abstraction, and every threshold reported in this paper is a lower bound on the loss a network can
absorb. The mechanism is that a contiguous disc removes a spatially compact region and leaves the
remainder intact and connected, so the network routes around the hole; this is the behaviour expected
of a single spatially embedded network, in which a finite localised hole does not propagate, in
contrast to interdependent systems (Berezin et al., 2015), and degree-homogeneous networks are likewise
no more vulnerable to localised than to dispersed removal (Shao et al., 2015).

**Against the paper, and equally without exception: connectivity does not predict tolerance to
localised damage.** Under a single lesion the ⟨k⟩–threshold association vanished entirely (ρ = −.000,
p = 1.00), as did the loop-fraction association (ρ = .007, p = .942); under ten lesions both were weak
and non-significant (ρ = .151 and .151, p = .13), against ρ = .737 and .731 under dispersed removal on
the identical draws. Fractal dimension behaved oppositely, retaining a moderate and highly significant
association under the multi-lesion protocol (ρ = .523, p < .001) while itself being non-significant
under a single lesion (ρ = .142, p = .159). All four damage scenarios are set side by side, with their
dispersion, in Table S3.

That contrast is mechanistically coherent rather than anomalous, and it is the clearest evidence in the
study that the two architectural axes are doing different work. Reticulation supplies alternative routes
**between** regions, which is what dispersed removal destroys and what a single compact hole does not.
A compact hole is defeated instead by how thoroughly the network fills the plane — by whether there is
material outside the lesion positioned to carry the rerouted flow — which is what fractal dimension
measures. The result therefore both narrows the paper's main claim and rescues its secondary predictor:
under the one damage geometry where connectivity stops discriminating, geometry is the only descriptor
that still does.

**The principal architectural result of this study is consequently scope-limited, and the qualifier is
load-bearing: reticulate connectivity governs structural tolerance to *dispersed* simulated vascular
damage.** Under spatially contiguous damage all networks tolerated substantially more loss and
connectivity ceased to differentiate them. The claim should not be stated without the qualifier, and it
is not stated without it anywhere in this paper.

A related robustness question resolves in the paper's favour and can be dealt with briefly. The
threshold reported throughout is defined on the giant connected component, whereas prior venation
analyses score connectivity to a source — the structural vein in Mander and Williams (2024), the
petiole in Price and Weitz (2014). Because no network in this deposit carries a petiole flag, a
documented widest-vein rule supplied the source, which fired for 100 of 100 networks, and the source
node was protected from removal. Scoring both criteria on identical removal draws, the source-anchored
threshold was systematically lower — median 0.1837 against 0.1998, a median paired difference of
−0.011, lower in 100 of 100 networks (Table 16 and Results §7.1) — which is expected, since requiring connection to one designated
node is strictly stricter than counting the largest surviving component. But the two criteria ranked
networks almost identically (ρ = .912, Pearson r = .935) and every association was preserved:
connectivity remained the leading predictor (ρ = .654 against .737) and fractal dimension remained
secondary (ρ = .465 against .501). **The criterion choice shifts the level of the threshold and changes
none of the conclusions.**

---

## 7. The Haustorial Sink: A Decoupled Hydraulic Lens

The haustorial sink was imposed as a hydraulic boundary condition on the solved potential field, not as
a driver of the structural analysis, and the two are reported as independent lenses on the same network
because that is what the results show them to be.

Calibrated to withdraw 20.0% of leaf throughput at an illustrative 1.5 MPa host–parasite gradient — a
strength of K_h = 0.0392, anchored on the ~18% figure that Jiang et al. (2003) report as a hemiparasite
floor — the sink depressed the minimum host leaf water potential to −1.0224 MPa and embolised no
vessels at the modelled −2.0 MPa cavitation threshold. Sweeping the gradient from 0.0 to 3.0 MPa left
that margin positive throughout, its smallest value being 0.6779 MPa at a diverted fraction of 35.1%
(Table 5). Figure 7 shows the solved potential field with the haustorium attached, in which the minimum
potential anywhere in the field remains above the modelled threshold.
Under the coupled model in which a node is removed only when its solved potential falls below the
cavitation threshold, no network reached the collapse criterion at **any** haustorial attachment
density at the calibrated strength: the collapse probability never reached .50 anywhere between 0 and 1
(Figure 12; Table S4). Note that the vertical axis of that surface is the fraction of nodes **bearing a
haustorium**, which is a different quantity from the removed-node fraction of Tables 3, 4 and 9 and is
not comparable with those values.

The correct reading of that null is neither "the parasite is harmless" nor "0 vessels embolise". It is
that **under this parameterisation, hydraulic withdrawal does not approach the modelled cavitation
threshold**, and three threshold-independent quantities establish why, all of which should be reported
in preference to the embolism count.

First, **the parasite's contribution to the potential field is small and separable from the stipulated
one.** Against a no-parasite baseline minimum of −0.9963 MPa — set entirely by the −1.0 MPa
transpirational boundary condition — the calibrated sink depressed the network minimum by 0.0262 MPa.
Approximately **2.6%** of the reported 0.978 MPa "margin to cavitation" is attributable to the
parasite (Table 5, first row, is effectively the no-parasite baseline; the decomposition is in Table S4); the remaining 1.000 MPa is the stipulated separation between the transpirational boundary
condition and the modelled cavitation threshold. Reporting the margin without that decomposition would
credit the parameterisation to the biology.

Second, **the depression at the haustorial contact patch is exactly linear and derivable.** It was
0.402 MPa at the illustrative gradient, and across 0 to 12 MPa it tracked the gradient at
−0.2682 MPa per MPa with an intercept of approximately zero and a maximum residual of 0.017 MPa.
That linearity is a consequence of the parameterisation rather than of leaf architecture (Table S4): because K_h
is specified *relative* to each node's own incident conductance — so that a haustorium taps a vessel in
proportion to its calibre — the reservoir's weight in a tapped node's potential is fixed at
K_h/(1 + K_h) = 0.0377 per node, independent of the network. **The absence of embolism is therefore an
arithmetic consequence of the sink parameterisation, not an emergent property of venation topology**,
and it should be presented as such.

Third, **the requirement is quantifiable and far outside the measured range.** Extrapolating the
depression law, reaching the modelled −2.0 MPa threshold would require a host–parasite gradient of
approximately 6.0 MPa (6.26 predicted analytically), or a sink strength beyond 256 times the calibrated
value at the illustrative gradient (Table S4). The largest directly measured parasite–host leaf gradient located
in this study's literature passes is approximately 0.5 MPa (Griebel et al., 2022, who recorded a host
trunk water-potential depression of 0.60 MPa under mistletoe infection and a modelled increase in
percent loss of conductivity of 11 points without hydraulic failure). The requirement is thus roughly
twelve times the largest measured value and four times the illustrative one.

This null is genuinely consistent with independent physiology rather than merely unfalsified by it.
Scoffoni et al. (2017) report that outside-xylem vulnerability explains the great majority of the
decline in whole-leaf conductance during dehydration, with **no minor-vein conduits embolised above
turgor loss**, and Avila et al. (2022) show that connectivity-mediated embolism spread engages only
once a majority of conduits are already gas-filled. Minor-vein xylem is hard to embolise. A model in
which a modest haustorial draw fails to embolise minor veins is agreeing with the measurement
literature, not contradicting it. Within this model, therefore, **haustorial harm is a resource drain
rather than a rupture**: the sink withdraws a fifth of leaf throughput — a substantial carbon and water
cost — while perturbing the potential field by hundredths of a megapascal.

Four constraints bound how far this can be taken, and the first is decisive. **The null is
threshold-dependent, and it inverts.** The gradient required for the first embolised vessel rises from
1.1 MPa at a −1.00 MPa threshold, through 2.1 at −1.10, 2.7 at −1.25, 4.0 at −1.50 and 6.0 at −2.00, to
9.5 MPa at −3.00 (Table 16, first row; the full eight-threshold sweep is Table S4). At a −1.00 MPa threshold the calibrated sink already embolises one vessel at the
illustrative gradient. The statement "no vessels embolise" is true only for thresholds at or below
−1.10 MPa and only inside the truncated 0–3 MPa sweep, and it must never be stated unqualified. Second,
**the host's operating point matters far more than the parasite does.** Sweeping the transpirational
boundary condition from −0.5 to −2.5 MPa shows that at a realistic midday potential of −2.5 MPa,
**91 vessels embolise with no parasite present at all**, rising only to 93 with the calibrated sink
attached (Table 16, second row; Table S4). The margin is governed by the boundary condition, not by the haustorium. Third, the sink was
strengthened deliberately to locate where coupling would begin: a critical haustorial attachment
density first exists at **two times** the calibrated strength — and then only in the lowest-fractal-
dimension network, at a density of 0.9384, meaning 94% of nodes would need to bear a haustorium — and
exists in every network at **three times** it, after which it falls steeply (Figure 12; Table S4). Coupling is therefore not
impossible within the model; it is simply far from where the literature places the parameters. Fourth,
and underlying all of the above, **the parameters are literature-constrained rather than measured.**
The 1.5 MPa gradient is a review-level order-of-magnitude value, not a primary measurement, and no
measurement of total water potential, osmotic potential or turgor has been published for any
*Cuscuta*–host interaction at all (Balios et al., 2025). The diversion anchor is a hemiparasite floor
(Jiang et al., 2003), not a holoparasite value.

**None of this supports the claim that real holoparasitism cannot cause hydraulic failure.** It
supports a much narrower and more useful statement: within a model parameterised from the best
available literature, hydraulic withdrawal alone did not bring the host network near the modelled
cavitation threshold, and structural fragmentation and hydraulic sink stress are therefore independent
lenses on the same network rather than two descriptions of one process. Given that the percolation
engine never reads a potential and the hydraulic solver never removes a node, that independence is in
part a property of the model architecture — which is exactly why it is reported as a decoupling rather
than as a discovery about parasitism. It is also worth recording that node deletion is not what a
haustorium does. *Cuscuta* searching hyphae acquire xylem identity and form a continuous xylem bridge
with the host, which is topologically an edge **addition** (Kaga et al., 2020). The removal simulations
in this study represent loss of conducting function from any cause; they do not represent haustorial
anatomy, and no anatomical warrant exists for parasite-driven node deletion.

---

## 8. Verification, Validation, and What Each Establishes

The hydraulic implementation was checked against the source dataset's own resistance column across
**119 leaves and 5,668,467 individual vein segments** (Table 13). Agreement was at floating-point precision: the
worst per-leaf coefficient of variation in the ratio of modelled to source resistance was
1.1 × 10⁻⁷ and the worst departure of the median ratio from unity was 6.1 × 10⁻⁸, both inside a
pre-set tolerance of 1 × 10⁻⁶, with all 119 leaves classified as exact. Repeating the comparison with a
deliberately wrong exponent dropped the median log-correlation to 0.953, which establishes that the
match is not a trivial consequence of resistance and geometry being monotonically related.

This is **verification, not validation**, and the distinction is not pedantry. The deposit defines its
resistance column as ℓ/r⁴ and the solver implements ℓ/r⁴; the comparison therefore confirms that a
shared geometric convention was correctly re-implemented across 5.7 million segments, and it confirms
that at a level of precision that leaves no room for an undetected indexing, unit or scaling error
anywhere in the geometry pipeline. It says nothing whatever about whether ℓ/r⁴ is the right physics for
a leaf vein. The manuscript therefore uses "verified" for this check and never "validated".

The one comparison against an independent physical measurement was weak. Modelled whole-network
conductance tracked measured leaf hydraulic conductance at Spearman ρ = .187, p = .073, n = 93 species,
95% CI [−0.024, 0.382] (Table 13). The interval spans zero and extends to a moderate positive value, so the
correct description is **underpowered rather than negative**: the data are compatible with anything
from no relationship to a moderate one, and reporting this as a failed validation would overstate the
evidence as badly as reporting it as a success.

Three things follow, and the order matters. First, the result is **exactly what a xylem-only model
should produce.** K_leaf is a whole-leaf quantity in which outside-xylem pathways — the mesophyll and
bundle-sheath routes water takes after leaving the vein — carry a large share of static resistance and
account for the great majority of the dynamic decline during dehydration (Scoffoni et al., 2017). The
model represents the xylem network and nothing else. Independently, the study that published these
networks reported that venation architecture predicts hydraulic efficiency only weakly on this same
material (Matos et al., 2024b), so the weak association is a property of the trait relationship and
not solely of this implementation. Second, it is **not an artefact of the conductance convention.**
Repeating the comparison under the deposit's alternative ℓ/r² convention gives ρ = .179, p = .059
(n = 112), against ρ = .176, p = .063 for ℓ/r⁴ on the same 112 networks (Table 16, third row), despite
the two conventions producing conductances differing by a median factor of 0.064 (Table S3). Relaxing the cohort screen from the
93-species percolation-cohort intersection to all 112 traced networks with a measured value changes
nothing. Third, and most important for how the paper should be read, **the percolation results do not
depend on this test at all.** The percolation engine operates on an unweighted adjacency matrix and
never reads a conductance, a radius or a potential. A failure of the conductance layer would invalidate
the sink analysis of Section 7 and would leave every result in Sections 2 through 6 untouched. Partitioning
the dependency in this way is the honest response to a weak validation, and it is more informative than
either defending or disowning the test.

A boundary sensitivity check completes the methodological picture and identifies where the dataset is
weakest. Of 120 traced networks, **105 fell inside both crop-edge tolerances** (Table 13, final row) — no more
than 5% of terminals within a 2% margin of the window edge, and a mean-degree shift of no more than
0.05 when window cut-ends are stripped — with a median boundary-terminal fraction of 0.0087 and a
median absolute mean-degree shift of 0.0011 (Table S3). The 15 that failed are systematically the smallest tracings: the boundary
fraction correlates with log edge count at ρ = −.347 (p < .001) and the absolute mean-degree shift at
ρ = −.373 (p < .001). None of the 15 entered the percolation cohort, whose screen enforces these
tolerances directly, so **Sections 2, 3, 4 and 6 are unaffected.** Three of the 15 do remain in the
enhancement cohort, which applies the weaker N ≥ 1,000 screen, and one of them — *Clusia alata*,
boundary terminal fraction 0.061 against the 0.05 tolerance — is the largest single gainer reported.
Excluding all crop-edge failures from the enhancement analysis leaves the conclusion intact
(n = 102; 92 improved, 10 unchanged, 0 worsened; median 0.00995 against 0.0095; Table S2), so the affected result
is the identity of the top gainer rather than the finding.

One further methodological property should be stated because it runs in the conservative direction.
Confidence intervals throughout are percentile bootstrap intervals with B = 200 resamples and seed 7,
the resampling unit being the individual Monte Carlo trial. The implementation caps each bootstrap
replicate at 50,000 trials, so where a run exceeds that budget the replicate is smaller than the
dataset and the interval is **too wide** by approximately √(n/50,000). Measured directly on the
reference network, a capped replicate gave a 95% interval of width 0.001684 against 0.001053 for a
full-size replicate, a ratio of 1.599 against the 1.414 expected (Table S3). The reported intervals for the
100,000-trial weighted runs are therefore conservative by roughly 1.4×, and those for the
1,000,000-trial uniform run by roughly 4.5×. No reported interval is anti-conservative, and no
conclusion in this paper depends on an interval being narrower than it is stated to be.

---

## 9. Network Size, the Synthetic Sweeps, and What They Cannot Settle

Two size sweeps were run on the generator and neither supports a finite-size claim. Both are tabulated in full, with the descriptors that were not pinned, in Table S5. In the first, the
generator's depth parameter raises size and fractal dimension together, taking D from 1.267 at N = 511
to 1.741 at N = 8,191; the accompanying rise in p_c from 0.2531 to 0.2857 mixes a size effect with a
geometry effect and cannot be read as either. In the second, fractal dimension and mean degree were
pinned by tuning the generator's length ratio and mesh fraction at each size, holding D within 0.0070
and ⟨k⟩ within 0.0059 across the whole range, and the threshold fell from 0.2701 at N = 1,023 to 0.0772
at N = 16,383 — a slope of −0.0514 per doubling (Table 14, plotted in Figure 13).

**That decline should not be called a finite-size effect, because pinning two descriptors does not pin
the architecture.** Loop fraction drifted from 0.692 to 0.561 across the same sweep, a spread of 0.131,
and bridge fraction correspondingly rose from 0.3079 to 0.4390 (Table 14; Table S5). Loop fraction is itself one of this
study's predictors of the threshold, and across the five sweep points it correlates with p_c at
Pearson r = .913. **The threshold tracks the loss of reticulation at least as well as it tracks the
growth in size**, and with five points and two moving variables the two explanations cannot be
separated. No finite-size claim — convergence or divergence — is made from this generator, and none
should be read into the sweep. Settling the question would require a construction that holds loop
fraction fixed as well, which this generator cannot do.

The important point is that **the synthetic size dependence does not propagate into the empirical
results**, and this can be checked directly rather than assumed. Across the percolation cohort the
threshold rises weakly *with* size (ρ = .232, p = .020) — the **opposite sign** to the synthetic sweep —
while mean degree and loop fraction are unrelated to size (ρ = .037 and .030) and every
architecture–threshold association strengthens under log-size control (Table 6; Table S3 and Table S5). The empirical cohort spans
1,436 to 300,633 nodes, an order of magnitude beyond the synthetic sweep, and shows no sign of the
synthetic behaviour. Whatever the generator is doing, real venation is not doing it.

Because no scaling collapse at genuinely constant architecture was performed, **no critical exponent is
reported and no universality-class claim is made anywhere in this study.** A β value was obtained from
a single-size log–log fit during development; it matches neither the mean-field nor the
two-dimensional value, it is sensitive to the fitting window and to the f_c estimate, and it is
therefore not quoted.

The comparison with the Molloy–Reed criterion requires the same discipline and one additional
clarification. On the largest network of the *confounded* sweep (N = 8,191, κ = ⟨k²⟩/⟨k⟩ = 3.131), the
removal fraction at which the giant component vanishes was located empirically at f_c = 0.524 against
a Molloy–Reed prediction of 0.531 (Table S5). That correspondence is **qualitative and nothing more**. Molloy–Reed
is a generating-function result that assumes a locally tree-like graph, and a planar mesh is dense in
short loops, so agreement at the same order is the most that can be expected and the numerical
closeness is not a 1.3% validation. It certainly does not establish a universality class. On a
separately generated mesh of N = 4,095 (κ = 3.119) the same criterion predicts f_c = 0.5281 while the
half-size threshold measured on that network is p_c = 0.2852, which illustrates the point that matters
most here: **f_c and p_c are different criteria and produce different numbers on the same network.** f_c is the removal fraction at which the
giant component vanishes; p_c is the fraction at which it falls below half its undamaged size with
probability .50. Quoting them side by side without that label would make the Results appear to give two
incompatible thresholds for one network.

---

## 10. The Modelled Separation Between Two Collapse Criteria

Because fragmentation and complete loss of the giant component are two criteria on the same collapse
process, a network that is losing nodes progressively must cross the first before the second, and a
model of progressive loss can be used to ask how far apart the two crossings are. Modelling infestation
as logistic growth in the affected node fraction from ρ₀ = 0.02 on the **synthetic reference network**,
the separation between the fragmentation threshold (p_c = 0.271) and the point at which the giant
component vanishes (f_c = 0.525) was 7.25 growth-time units at a slow stipulated rate (r = 0.15,
crossings at 19.35 and 26.60), 4.35 at a moderate rate (r = 0.25, crossings at 11.61 and 15.96), and
2.72 at an aggressive rate (r = 0.40, crossings at 7.26 and 9.98). These are Supplementary Table 15 and
Supplementary Figure 14, and they are placed there rather than in the main Results for the reasons
below.

**The meaningful computational result is the existence and the shape of the separation, not its
numerical size.** A separation is present at every stipulated rate, and it contracts monotonically as
the growth rate rises — an interval of 7.25 units at the slow rate against 2.72 at the fastest,
compressing by roughly a factor of 2.7 for a 2.7-fold increase in rate, as the logistic form requires.
That is a property of the two collapse criteria under monotone progressive loss, and it is
reproducible.

**The numerical values are not calendar times and must never be reported as though they were.** The
time unit is set entirely by the assumed growth rate, which was stipulated rather than fitted to any
measured infestation time-course; the underlying thresholds are those of the synthetic reference
network (p_c = 0.271) rather than of the empirical cohort (median 0.1998), so the values do not even
describe a real leaf; and **the model contains no symptom variable of any kind.** Consequently this
analysis does not demonstrate, predict, estimate or bound a physiological pre-symptomatic window, and
it is reported in the Supplementary Materials as an exploratory result for exactly that reason.

The point is worth making sharply because the temptation to over-read it is obvious and the literature
argues against the over-reading rather than for it. A pre-symptomatic window under parasitism is
empirically real, with documented lead times ranging from roughly 20 days to considerably longer
(Cochavi et al., 2017; Shen et al., 2007), but its documented signature is optical, thermal,
growth-related and carbon-related — not hydraulic. And in precisely the mild-stress regime such a
window would occupy, the mechanism this model represents is the one not yet operating: outside-xylem
pathways dominate the conductance decline with no minor-vein conduits embolised above turgor loss
(Scoffoni et al., 2017), and connectivity-mediated spread engages only once most conduits are already
gas-filled (Avila et al., 2022). A connectivity-driven cascade in leaf venation is a **late**-stage
phenomenon. The separation reported here is a property of two graph criteria; converting it into a
biological warning interval would require a symptom variable, a fitted infestation time-course and a
demonstrated mapping from removed node fraction to physiological state, and this study supplies none of
the three.

---

## 11. Biological and Theoretical Implications

Taken together, the results support a single structural proposition with a well-defined scope: **in
sparse planar venation networks, the fraction of the edge budget committed to closing loops rather than
extending branches is the dominant architectural determinant of how much dispersed element loss the
network absorbs before its transport skeleton fragments.** That proposition is supported at four levels
of evidential strength, and the levels should not be collapsed. It is an association across 100 species
(ρ = .733; Table 6); an adjusted association that strengthens under size control and under exclusion of
over-segmented tracings (ρ = .745 and .789; Table 6 and Table 16); a controlled attribution when the two
architectural axes are decoupled by construction inside the empirically observed range (β = .981 against
.125; partial r = .970 against .451; R² = .940; Table 7); and a within-network perturbation in which 93
of 105 real networks improved and none worsened (Table 10; Table S2). Only the last two speak to anything more than correlation, and only the
last speaks to real leaves.

The most counter-intuitive implication is that a **sparse** network can be a **tolerant** one. Mean
degree of 2.520 is barely above the value of a tree, and the naive reading of that number is fragility.
The cohort is nevertheless tolerant because the small excess over 2 is spent almost entirely on cycles:
77.6% of edges lie on at least one, leaving only 22.4% as bridges whose individual loss disconnects a
region (Table 1). Tolerance in a transport network is not a function of edge count but of how many alternative
routes survive an average removal, and closing an areole converts two dead-end paths into one circuit
at the cost of a single edge. Reticulation is, in this precise sense, the cheapest available form of
redundancy — which is a plausible reason for it to be so widespread a feature of angiosperm venation,
and which connects the graph-theoretic result to the optimality arguments of Katifori et al. (2010) and
Price and Weitz (2014) and to the direct hydraulic measurement of Sack et al. (2008), who found
higher-order vein damage tolerated with no detectable penalty precisely because the minor-vein network
supplies parallel paths.

The study also demonstrates that **structural tolerance is a manipulable network property and not only
an observable correlate.** That is what the enhancement establishes, and it is what distinguishes this
result from the existing comparative literature on venation robustness. It comes with an equally firm
boundary: the manipulation carries no construction, mechanical or photosynthetic cost, so it identifies
the direction of a network-level relationship rather than an optimum. Real venation sits on a
trade-off surface among transport efficiency, cost and robustness (Ronellenfitsch & Katifori, 2019),
and the diminishing-return relationship measured here (ρ = −.821 of gain on baseline connectivity;
Table 11)
suggests that many of these leaves are already near the point where further reticulation buys little
structural tolerance — which is what a cost-constrained optimum would look like from the inside, and
what the vein-density saturation described by Noblin et al. (2008) would predict physically.

Two theoretical points follow that are not specific to leaves. First, **reticulation buys uniformity of
risk and not only robustness.** The negative association between reticulation and the uniform-minus-
weighted threshold gap (ρ = −.786, size-clean) means that more reticulate networks are less
*differentially* exposed to the pattern of damage as well as more tolerant of its amount. For a network
class this sparse and this planar — where degree is bounded and centrality concentrates on articulation
points (Tian et al., 2017) — that is a substantive statement about the variance of the response, and
no precedent for it in venation was located here. Second, **damage geometry is a first-order variable,
not a robustness check.** Holding the removed fraction identical and changing only the spatial
correlation of the removals moved the threshold by a factor of 2.3 to 2.5 in 100 of 100 networks and
inverted which architectural descriptor predicts it (Table 16 and Results §7.2; Table S3). Studies of spatially embedded transport networks
that report a single removal geometry are reporting one point on a wide surface, and this study's own
principal claim required the qualifier that the second geometry supplied.

For **computational phenotyping**, the contribution is that p_c behaves as a per-network architectural
index: it is computable identically on networks spanning 1,436 to 300,633 nodes, it is essentially
invariant to the connectivity criterion used to define it (ρ = .912 between criteria), it reproduces
across an independent re-implementation at ρ = .999 with a median absolute difference of 0.0011
(Table 16, note), and it is not confounded with network size in real cohorts (Table S3). It is therefore a usable comparative trait. What
it is not is a physiological quantity. It cannot be converted to percent loss of conductivity, to P50,
or to a water potential, and no such conversion is attempted here.

Finally, the parasitological motivation of the study is answered by a **negative result that is more
informative than the positive one would have been.** A haustorial sink calibrated to the best available
literature withdraws a fifth of leaf throughput while depressing the network's minimum water potential
by 0.0262 MPa, and reaching the modelled cavitation threshold would require a gradient roughly twelve
times the largest ever measured for a parasite–host pair. Within this model, holoparasitic harm is a
resource drain rather than a rupture, and structural fragmentation and hydraulic sink stress are
independent lenses on the same network. That is consistent with the finding that mistletoe infection
depresses host water potential by 0.60 MPa and raises modelled conductivity loss by 11 points without
producing hydraulic failure (Griebel et al., 2022), and with the observation that minor-vein conduits
are hard to embolise in the first place (Scoffoni et al., 2017).

---

## 12. Limitations

The limitations below are ordered by how much they constrain the interpretation, and each is stated
with its consequence rather than merely listed.

**1. This is a computational study of network structure, and its central quantity is topological.**
p_c is computed on an unweighted adjacency matrix; no conductance, radius or water potential enters its
calculation at any point. It quantifies when the loss of conducting elements becomes widespread enough
to sever the network, not the water potentials at which such loss is initiated. It cannot be converted
to percent loss of conductivity, to a vulnerability curve parameter, or to a leaf water potential, and
no result in this paper should be read as a demonstration of hydraulic failure. The one consolation is
that the same independence immunises Sections 2 through 6 against any objection to the conductance
model, including the weak K_leaf comparison of Section 8.

**2. Simulated node removal is not embolism.** Real vascular failure is neither uniform nor
independent: it nucleates in the largest veins and propagates in a sequence set by vein size (Brodribb
et al., 2016), is spatially clustered (Pritzkow et al., 2022; Lu et al., 2025), and spreads between
conduits only once most are already gas-filled (Avila et al., 2022). Uniform removal reproduces none of
these properties and is used here as a **null structural scenario**; the centrality-weighted modes are
bounding scenarios (Trajanovski et al., 2013; Memmott et al., 2004) and represent no organism's
behaviour. The removal simulations represent loss of conducting function from any cause, and the
thresholds are architectural indices rather than predictions of physiological damage.

**3. The principal architectural result holds for dispersed damage only.** This is the sharpest
constraint and it is quantified in Section 6: under a single contiguous lesion the connectivity
association vanishes entirely (ρ = −.000, p = 1.00) and under ten lesions it is weak and
non-significant (ρ = .151, p = .13). Any statement that reticulation governs damage tolerance without
the dispersed-damage qualifier is unsupported by this study's own data.

**4. The haustorial model has no anatomical warrant for node deletion, and its parameters are
literature-constrained rather than measured.** *Cuscuta* haustoria form a continuous xylem bridge and
are topologically **additive** (Kaga et al., 2020). The sink's gradient of 1.5 MPa is a review-level
order-of-magnitude value rather than a primary measurement; the ~20% diversion anchor is a hemiparasite
floor (Jiang et al., 2003) applied to a holoparasite; and no measurement of total water potential,
osmotic potential or turgor has been published for any *Cuscuta*–host interaction (Balios et al., 2025).
The sink result is a statement about a plausibly parameterised model, and its central null is
threshold-dependent — it inverts at a −1.00 MPa cavitation threshold — and derivable in closed form
from the relative-K_h convention rather than emergent from venation structure.

**5. The only independent physical test is underpowered, and the model is xylem-only.** Modelled
conductance tracked measured K_leaf at ρ = .187, 95% CI [−0.024, 0.382], n = 93 species. The interval
spans zero. Outside-xylem pathways dominate the dynamic decline of whole-leaf conductance (Scoffoni
et al., 2017) and the source study reports weak architecture–efficiency coupling on this same material
(Matos et al., 2024b), so the result is expected; but "expected" is not "validated", and the
conductance layer of this model should be treated as unvalidated against physiology. The resistance
comparison of Section 8 is **verification** of a shared ℓ/r⁴ convention, not independent validation.

**6. One hundred of the 120 source networks are calibrated crop windows rather than entire laminae, and
none carries a petiole.** Network extent is bounded by the traced window, the source node is a
documented widest-vein rule rather than an anatomical petiole, and no source attachment is enforced
during removal. This matters more than a sampling caveat would, because embolism is empirically
observed to initiate in the petiole and midrib — precisely the structures the windows exclude. The
crop-edge check bounds the damage (105 of 120 within tolerance; none of the 15 failures in the
percolation cohort; 3 in the enhancement cohort, one of them the largest gainer), but it cannot restore
what was never traced.

**7. Fractal dimension is 73% explained by log network size.** Box-counting dimension is estimated over
a finite range of box sizes and a larger traced region supports a longer scaling range (Muraleedharan
et al., 2023), so D is in part a size readout in this cohort (ρ with N = .880). Its association with
the threshold survives and strengthens under that control (ρ = .496 → .633), so it is a real secondary
predictor, but it must be reported residualised and must not lead the account.

**8. Mean degree and loop fraction are one axis, not two.** They are rank-correlated at ρ = .994, so
the study cannot attribute its effect to loop closure as distinct from degree increase, and the
residual loop-fraction test is uninformative for that reason rather than because loops are unimportant
(Section 4). The reticulation enhancement inherits this limitation directly: it moves ⟨k⟩, loop
fraction, bridge fraction, terminal fraction and path length simultaneously, so it demonstrates that
the connectivity bundle is a lever without decomposing it.

**9. The enhancement contains no cost term.** "Zero networks worsened" is a single-objective result
against a purely structural criterion. Construction cost, mechanical constraint, photosynthetic
opportunity cost and the documented ecological costs of increased hydraulic safety (Nardini et al.,
2012) are all absent, and the trade-off surface on which real venation sits (Ronellenfitsch & Katifori,
2019) is not represented. The result gives a direction, not a design.

**10. The synthetic grid extrapolates beyond the empirical architectural range, and the synthetic
networks are not leaves.** Eighteen of its 42 cells exceed the empirical maximum of ⟨k⟩ = 2.99, which
is why the restricted 24-cell fit is the one reported (β = .981 against .125; R² = .940) and the
full-grid dominance ratio of approximately 14 to 1 is not. Even restricted, the grid networks have a
degree standard deviation of 1.350 against the empirical 0.848, so the attribution transfers but the
effect size does not.

**11. The finite-size sweep does not hold architecture constant.** Pinning D within 0.0070 and ⟨k⟩
within 0.0059 still allowed loop fraction to drift by 0.131 across the size range, correlating with the
threshold at r = .913, so no finite-size claim is made in either direction (Section 9). The empirical
cohort's size behaviour is opposite in sign to the generator's and is reported instead.

**12. Betweenness-weighted removal was run on the synthetic reference network only.** Exact betweenness
centrality is computationally infeasible at 300,633 nodes across a 100-network cohort at 2,400 trials
per network, so the empirical cohort carries uniform and degree-weighted results only, and the
betweenness ordering is a single-network finding on a network that is not a leaf. Its threshold is also
quoted on two different axes — nominal 0.1889 with a 95% CI of [0.1879, 0.1902], realised 0.1498 — and
only the realised value is comparable with the other modes.

**13. GCC fragmentation is a structural proxy for transport continuity, not a measurement of it.**
The criterion "largest component below half its undamaged size at P = .50" is operational, chosen for
comparability across four and a half orders of magnitude in network size. It is not a critical point,
it treats all surviving nodes as equivalent regardless of position or calibre, and it does not
distinguish a network that has lost half its area from one that has split into two functional halves.
Its justification is that severance of the water-supply path within leaf veins causes immediate and
irreversible local tissue damage (Brodribb et al., 2021), so the loss of global connectivity is
functionally meaningful; but the study quantifies the structural conditions under which such severance
becomes widespread, not the physiological consequences of it. The alternative criterion tested —
connectivity to a designated source — shifted the threshold level but changed no conclusion (ρ = .912
between criteria), which bounds this concern without eliminating it.

**14. No phylogenetic correction was applied.** The 100 species are treated as statistically
independent across a sample spanning ferns and angiosperms. Point estimates are unaffected, but the
significance values assume an independence that a comparative sample does not possess, and a formal
test of phylogenetic signal in the regression residuals was not performed.

**15. Tracing-quality grades are non-ordinal defect types and are incompletely recorded.** The source
deposit's scale distinguishes under-segmentation, over-segmentation and physical damage — defects with
*opposite* effects on measured connectivity — and the archive retains only the leading flag of a
comma-separated code, so 4 over-segmented and 28 damaged networks are hidden inside other leading
grades. No severity ordering among grades is valid or claimed. The sensitivity analyses were run on
flag *presence* rather than the leading flag for this reason, and every principal result strengthened
under exclusion of over-segmented networks rather than weakening.

**16. Roughly half the between-network variance in the threshold is unexplained.** The two-predictor
model reaches R² = .507 on the empirical cohort. The descriptors measured here — connectivity,
reticulation, geometry and size — do not exhaust the architectural determinants of structural
tolerance, and the unmeasured remainder is large enough that no claim of a complete architectural
account is defensible.

---
---

# Notes for the writer (not part of the Discussion)

**Cross-referencing.** Every quantitative claim in the Discussion points to where its evidence is
tabulated. All 16 main tables and all 13 Results figures are cited, together with Supplementary
Tables S1–S5 (`SUPPLEMENTARY_TABLES.md`, generated by `scripts/make_supplementary_tables.py`). **Those
five supplementary tables were created because an audit found that roughly sixty quantities the
Discussion relies on had been computed and archived but had no home in the manuscript.** They report no
new analysis; every value in them comes from a file listed below. After that addition, only eight
numeric tokens in the Discussion are not printed in either the main sections or the supplement, and all
eight are either arithmetic performed in the sentence itself (0.84 units of mean degree from the Table 1
range; a 2.3–2.5× factor from the 2.27 and 2.46 of Results §7.2; 5.7 million from 5,668,467; the ~1.4×
and ~4.5× bootstrap inflations from √(n/50,000); the 1.3% figure from 0.524 against 0.531) or a
literature value belonging to a cited source rather than to this study (Griebel et al.'s 0.60 MPa).

**Numerical provenance.** Every value above was transcribed from the archived result files, never from
a previous manuscript version: `data/results_verified.json` (Tables 1–14 quantities),
`data/criterion_and_locality.json` (§§6 criterion and locality), `data/cavitation_sensitivity.json`
(§7 sink), `data/second_pass_audit.json` and `data/rrl_diagnostics.json` (§§3, 5 subsets and effect
sizes), `data/final_resolution_checks.json` (§8 bootstrap, high-GCC subcohort, betweenness–flux),
`data/resistance_convention_sensitivity.json` (§8 convention), `data/graph_metric_audit.json` (§§2, 4
weight distributions and the loop-fraction identity test), `data/finite_size_fixedD.json` and
`data/scaling_mesh.json` (§9), `data/dynamics.json` (§10), `data/boundary_check.json` and
`data/hydraulic_validation.json` (§8), `data/sink_surface.json` (§7 haustorial-density surface),
`data/cohort_provenance.json` (cohort definitions and nesting), and
`data/robustness_ceiling_summary.json` (§5 response-surface reconciliation).

**Five discrepancies were found during the audit. None is resolved silently.**

1. **`f_c = 0.524` versus `f_c = 0.525` are two different networks, not a rounding disagreement.**
   Results Table 14's prose value of 0.524 comes from `data/scaling_mesh.json`, where it is the
   empirically located giant-component-vanishing fraction of the **N = 8,191** network of the
   *confounded* sweep (κ = 3.131, Molloy–Reed prediction 0.531). Supplementary Table 15's value of 0.525
   comes from `data/dynamics.json`, where the full-precision value is 0.5246452576549665 on the
   **N = 1,023 synthetic reference network** (κ = 3.104). The Discussion attributes each to its own
   network. **Action for the author:** Table 14's phrase "the largest network" is inaccurate — the
   largest network in Table 14 is N = 16,383, which was never given an f_c calculation. Recommend
   "the largest network of the confounded sweep (N = 8,191)".

2. **Results §7 describes the sink-surface row that first develops a threshold as "the least reticulate
   network"; it is in fact the lowest-fractal-dimension row.** `data/sink_surface.json` holds mean
   degree constant across the surface (2.4927, 2.4927, 2.4927, 2.4907) and varies only D
   (1.228, 1.391, 1.498, 1.544). The row acquiring a threshold at 2× calibrated K_h is D = 1.228, at a
   critical haustorial density of 0.938. The Discussion uses "lowest-fractal-dimension". **Action:**
   correct the Results sentence.

3. **The semi-standardised regression coefficients differ in the fourth decimal between two archive
   files.** `data/results_verified.json` (canonical, generated by `build_analysis_master.py`,
   2026-08-14) gives β = 0.02848 and 0.02209; the superseded `data/cohort_pc_analysis.json`
   (2026-07-25) gives 0.028333 and 0.021983. The manuscript's 0.0285 and 0.0221 follow the canonical
   file and the Discussion does the same. No action needed; noted for completeness. Note also that
   `cohort_pc_analysis.json` reports **Pearson** partials (.596 and .499) whereas Table 6 reports
   **Spearman** partials (.736 and .502) — different statistics, not a conflict, and they must not be
   mixed.

4. **`data/graph_metric_audit.json` contains an erroneous field, and it is superseded here.** Its
   `empirical_120_leaves.cycle_rank_fraction_vs_identity` reports a mean |difference| of 0.0147 with a
   maximum of 1.0 against the identity (E − N + c)/E = 1 − 2/⟨k⟩ + c/E, which would mean the identity
   fails. `SECOND_PASS_AUDIT.md` (lines 91 and 494) instead states that it holds to 1.4 × 10⁻¹⁶. The two
   cannot both be right, so the identity was **recomputed directly from `data/analysis_master.csv`**:
   the maximum absolute departure across all 120 traced networks is **2.5 × 10⁻¹⁶** using the stored
   mean-degree column and 1.4 × 10⁻¹⁶ using ⟨k⟩ = 2E/N, i.e. floating-point precision either way. The
   audit prose is correct and the JSON field is wrong, because the script that wrote it omitted the
   components correction c/E while **61 of the 120 networks have more than one component** (up to
   4,477). Table S3 carries the recomputed value and states the supersession in its note. **Action for
   the author:** regenerate `data/graph_metric_audit.json` with the correction, or annotate the field
   as superseded. Nothing else in the manuscript depends on it — the substantive point, that the
   identity holds for the **cycle-rank** fraction and *not* for the non-bridge loop fraction reported
   throughout (mean absolute departure 0.564, a factor of 3.63), is unaffected and is independently
   confirmed by the synthetic-grid row, which the same script computed correctly.

5. **Terminology.** The user's brief refers to "random versus targeted attack". Per
   `FINAL_RESOLUTION_PASS.md` §12 the manuscript's controlled vocabulary forbids "attack"/"targeting",
   so the Discussion uses **uniform** and **degree-/betweenness-weighted removal**, and **dispersed**
   versus **localised** removal, throughout. It also uses **verified** (never validated) for the
   resistance-column check, **critical removed fraction / fragmentation threshold** (never hydraulic
   collapse threshold), **modelled conductance**, and **imposed as a hydraulic boundary condition**
   (never driven by). "Pre-symptomatic" appears nowhere as a claim; §10 is titled and framed as the
   modelled separation between two collapse criteria, per `FINAL_RESOLUTION_PASS.md` §11.

**References cited in the Discussion that are not yet cited in the revised Introduction, Methods or
Results.** All six are carded with verified DOIs in `rrl/A`–`rrl/J` and appear in the Part XI Discussion
blueprint of `SECOND_PASS_AUDIT.md`; they must be added to the reference list.

- **Tian, L., Bashan, A., Shi, D.-N., & Liu, Y.-Y. (2017).** Articulation points in complex networks.
  *Nature Communications, 8*, 14223. — The articulation-point mechanism linking bridge fraction to
  centrality-weighted vulnerability (§§2, 4, 6, 11).
- **Noblin, X., Mahadevan, L., Coomaraswamy, I. A., Weitz, D. A., Holbrook, N. M., & Zwieniecki, M. A.
  (2008).** Optimal vein density in artificial and real leaves. *Proceedings of the National Academy of
  Sciences, 105*(27), 9140–9144. — The saturation mechanism behind the −.821 diminishing-return
  relationship (§§5, 11).
- **Brodribb, T. J., Brodersen, C. R., Carriqui, M., Tonet, V., Rodriguez Dominguez, C., & McAdam, S.
  (2021).** Linking xylem network failure with leaf tissue death. *New Phytologist, 232*(1), 68–79.
  — The authorisation for treating loss of a connected supply path as functionally meaningful (§12,
  limitation 13).
- **Avila, R. T., Guan, X., Kane, C. N., Cardoso, A. A., Batz, T. A., DaMatta, F. M., Jansen, S., &
  McAdam, S. A. M. (2022).** Xylem embolism spread is largely prevented by interconduit pit membranes
  until the majority of conduits are gas-filled. *Plant, Cell & Environment, 45*(4), 1204–1215.
  https://doi.org/10.1111/pce.14253 — Connectivity-mediated spread is a late-stage phenomenon (§§2, 7,
  10, 12).
- **Kaga, Y., et al. (2020).** Interspecific signaling between the parasitic plant and the host plants
  regulate xylem vessel cell differentiation in haustoria of *Cuscuta campestris*. *Frontiers in Plant
  Science, 11*, 193. https://doi.org/10.3389/fpls.2020.00193 — The haustorial connection is
  topologically additive (§§7, 12). *Full author list must be completed from the source before
  submission.*
- **Mou, Y., & Hayashi, Y. (2025).** [Planar proximity-graph degree distribution.] *PLOS ONE.* — Planar
  degree is bounded and near-degenerate, ⟨k⟩ ≈ 2.50 for uniform proximity graphs (§§1, 2). *Full
  citation must be completed from `rrl/D_attack_strategies_centrality.md` before submission.*

**Claims deliberately not made, per `SECOND_PASS_AUDIT.md` Part XIII and `FINAL_RESOLUTION_PASS.md`
§13.** No universality class, critical exponent or phase-transition claim; no conversion of p_c to any
physiological quantity; no "early warning" or pre-symptomatic prediction; no claim that the parasite
causes embolism or that reticulation causes host resistance; no priority claim of the form "first
percolation analysis of leaf venation"; no ordinal reading of the tracing-quality grades; no claim that
loop fraction predicts tolerance independently of mean degree; and no statement that the reticulation
enhancement is beneficial without its cost caveat.
