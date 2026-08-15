## ATTACK LINES, RANKED BY SEVERITY

**Before the list — two corrections to the shared context, because one of them changes the whole shape of the defence.**

1. **Mrad et al. (2021) does NOT argue that connectivity speeds embolism contagion.** That is the *hypothesis it sets up and then resolves against*. Verbatim abstract: *"It is hypothesized that an increase in conduit connectivity brings improved resistance to embolism spread due to increased hydraulic pathway redundancy. However, an increase in conduit connectivity could also reduce resistance due to increased speed of embolism spread with respect to pressure… **Considering only species with vessels, increases in connectivity improve resistance to embolism spread without negatively affecting hydraulic conductivity.**"* Mrad is a **supporting** citation, not a contradicting one. The brief was wrong about this. The real danger from Mrad is **prior art**, not sign reversal — it already applies graph theory *and percolation theory* to xylem and already invokes the percolation threshold as *"an effective 'seal' against uninhibited embolism spread born out of vessel connectivity statistics."*
2. **Loepfe et al. (2007) is the genuine sign reversal**, and it is the only one: *"maximum hydraulic conductivity and vulnerability to embolism increase with the connectivity of the xylem network."* It is one paper, theoretical, at conduit scale, and now partially superseded by Mrad. It is a Moderate problem, not the Major one the brief assumed.

---

### Attack 1: The paper's own source dataset has already been analysed by its own authors, who concluded that venation architecture *weakly* predicts resilience — on the same 122 species.

- **Severity**: **Fatal** (to the novelty and to the headline claim simultaneously)
- **The objection in a reviewer's words**: "The authors take Matos et al.'s data and report that architecture strongly predicts a resilience-like quantity. Matos et al., analysing the same 122 species, concluded the opposite: architecture strongly predicts support and damage resistance but *weakly* predicts efficiency and resilience. The authors do not cite this disagreement, reconcile it, or explain why their resilience proxy should be believed over the one published with the data. Either they have found something the data providers missed, in which case they must demonstrate it against the original resilience metric, or they have relabelled a topological artefact as resilience."
- **Supporting literature**:
  - Matos, I. S., Boakye, M., Niewiadomski, I., Antonio, M., Carlos, S., Johnson, B. C., Chu, A., Echevarria, A., Fontao, A., Garcia, L., Kalantar, D., Madhavan, S., Mann, J., McDonough, S., Rohde, J., Scudder, M., Sharma, S., To, J., Tomaka, C., … Blonder, B. W. (2024). Leaf venation network architecture coordinates functional trade-offs across vein spatial scales: Evidence for multiple alternative designs. *New Phytologist, 244*(2), 407–425. https://doi.org/10.1111/nph.20037 — **paywalled; abstract verified verbatim.** Powering finding, verbatim: *"We found that generalized architecture–function trade-offs are weak. Architecture strongly predicts leaf support and damage resistance axes but weakly predicts efficiency and resilience axes."*
- **Is it correct?**: **Yes, and it is the single most dangerous thing in the reviewer's reach**, because it requires no outside expertise — it is on the first page of the paper's own data citation. Note the one genuine escape hatch: Matos's "resilience" axis was built from measured functional traits, not from a percolation simulation, so the two are not strictly the same quantity. But that escape hatch is also an admission — it concedes that the paper's "resilience" is a *simulation output*, not a measured function, which feeds Attacks 2 and 4.
- **Best available defence**: State plainly that Matos et al. operationalised resilience through measured trait proxies while this paper operationalises it as simulated topological robustness, cite Mander & Williams (2024) and Brodribb et al. (2016) as precedent that simulated network robustness is a legitimate and separately informative construct, and *report the correlation between this paper's p_c and Matos's own resilience axis*. If that correlation is decent, the paper has a result. If it is poor, the paper must say so.
- **What the paper must concede**: "Matos et al. (2024), analysing this same species set with trait-based functional axes, reported that architecture predicts resilience only weakly; our p_c is a simulated topological robustness measure rather than a measured functional resilience, and the two constructs should not be equated."

---

### Attack 2: In the mild-dehydration window the paper explicitly names "pre-symptomatic," xylem embolism is demonstrably *not* what drives leaf hydraulic decline.

- **Severity**: **Fatal** (to the premise, not the arithmetic)
- **The objection in a reviewer's words**: "The paper's entire framing is that a pre-symptomatic hydraulic collapse can be captured as a percolation event in the vein xylem network. Scoffoni et al. (2017) settled this with in vivo microCT: at turgor loss point only small fractions of leaf vein xylem conduits are embolised, and outside-xylem vulnerability explains 75–100% of the decline in leaf hydraulic conductance from mild stress through turgor loss. The physiological regime the authors claim to model is precisely the regime in which their chosen mechanism is not operating. Removing vein-network nodes is a model of *severe*, late-stage dehydration, which is by definition symptomatic."
- **Supporting literature**:
  - Scoffoni, C., Albuquerque, C., Brodersen, C. R., Townes, S. V., John, G. P., Bartlett, M. K., Buckley, T. N., McElrone, A. J., & Sack, L. (2017). Outside-xylem vulnerability, not xylem embolism, controls leaf hydraulic decline during dehydration. *Plant Physiology, 173*(2), 1197–1210. https://doi.org/10.1104/pp.16.01643 — **paywalled; abstract verified verbatim.** Verbatim: *"at the turgor loss point, only small fractions of leaf vein xylem conduits were embolized, and substantial xylem embolism arose only under severe dehydration… outside-xylem hydraulic vulnerability explained 75% to 100% of Kleaf decline across the range of dehydration from mild water stress to beyond turgor loss point."*
  - Scoffoni, C., et al. (2023). The dynamic multi-functionality of leaf water transport outside the xylem. *New Phytologist*. https://doi.org/10.1111/nph.19069 — **DOI verified from index; abstract not read in this pass.**
  - Supporting magnitude, **attribution not verified in this pass**: resistance outside the xylem is widely reported as ~57% of total leaf hydraulic resistance averaged across ~45 dicot species, ranging 11–74% across 10 tropical tree species. Verify the primary source (likely Sack & Holbrook's *Annual Review* or Scoffoni & Sack's JXB review) before citing this number.
- **Is it correct?**: **Yes, and it is unanswerable on the mechanism.** The only honest defence is to change what the paper claims to be modelling. This attack also independently explains why the paper's own K_leaf validation failed at ρ = 0.187, p = 0.073: if more than half of leaf hydraulic resistance sits outside the xylem, a pure xylem-topology model *should not* predict whole-leaf K_leaf, and the null result is the expected result.
- **Best available defence**: Reframe from "pre-symptomatic hydraulic collapse" to "the topological reserve of the vein network against conduit loss" — an upper bound on structural, not physiological, tolerance. Then turn the failed K_leaf test from an embarrassment into a *finding*: cite Scoffoni et al. (2017) to argue that the weak K_leaf correlation is quantitatively consistent with outside-xylem resistance dominating, and that the model isolates the xylem-topological component specifically.
- **What the paper must concede**: "Because outside-xylem pathways account for 75–100% of leaf hydraulic decline from mild stress to turgor loss (Scoffoni et al., 2017), our node-removal model represents a structural bound on xylem network connectivity rather than a model of physiological hydraulic decline, and it is least applicable in the mild-stress regime."

---

### Attack 3: The parasite does not remove host vein junctions — it *adds* xylem connections — and the paper's own results show the sink and the percolation are causally disconnected.

- **Severity**: **Fatal** (to the title and framing; the brief calls this the softest joint and it is)
- **The objection in a reviewer's words**: "The title promises haustorial sink stress driving vascular collapse. The model delivers uniform random node deletion. A *Cuscuta* haustorium does not delete host vein junctions; its searching hyphae contact host xylem and differentiate into xylic hyphae forming a *xylem bridge* — topologically an edge *addition* with an imposed sink, not a node deletion. The authors' own simulation confirms this: minimum host ψ reaches −1.02 MPa against a −2.0 MPa cavitation threshold, giving **zero** embolised vessels across all 31 gradients spanning 0–3.0 MPa. The parasite mechanism does not produce a single removed node anywhere in this paper. It is decoration on an abstract percolation study."
- **Supporting literature**:
  - Kaga, Y., et al. (2020). Interspecific signaling between the parasitic plant and the host plants regulate xylem vessel cell differentiation in haustoria of *Cuscuta campestris*. *Frontiers in Plant Science, 11*, 193. https://doi.org/10.3389/fpls.2020.00193 — **open access.** Establishes that haustorial searching hyphae reaching host xylem acquire xylem identity and form a continuous xylem bridge — an additive vascular connection.
  - Jiang et al. (2003), the calibration source, is a **hemiparasite whole-plant** study; the paper concedes no primary holoparasite measurement exists. Also note the *Cuscuta* literature reports parasitised hosts showing **increased** stomatal opening and transpiration (sink-stimulated), not the passive water withdrawal the model assumes.
  - Scale mismatch, **reasoning-level**: *Cuscuta* attaches to **stems and petioles**. The Matos networks are lamina **crop windows with no petioles at all**. There is no petiole in the dataset for a haustorium to attach to.
- **Is it correct?**: **Yes, completely.** There is no version of this where the biology supplies node removal. The 20% diversion figure is borrowed from a hemiparasite, applied at an admittedly "illustrative" gradient, and produces zero embolism. The honest description is: this is a percolation study of leaf venation networks with an uncoupled hydraulic sink module attached.
- **Best available defence**: Demote the parasite from mechanism to *motivating scenario*, and be explicit that the sink model and the percolation model are two separate contributions reported in one paper. Alternatively — and this is the stronger scientific move — **report the zero-embolism result as a finding**: under a literature-calibrated sink at realistic gradients, holoparasitic water diversion is insufficient to induce cavitation in host leaf veins. That is a real, defensible, negative result.
- **What the paper must concede**: "Haustorial connection is topologically additive rather than subtractive, and our calibrated sink produced no vessel embolism at any tested gradient; node removal is therefore a generic damage abstraction and is not mechanistically derived from parasitism." **The title should change.** Keep the alternative framing ("Vein Reticulation as a Host-Resistance Trait…") only if the parasite is likewise demoted there.

---

### Attack 4: The giant connected component is the wrong observable — both prior studies of leaf-network robustness use *source-anchored* connectivity, and this dataset has no source.

- **Severity**: **Major**, verging on Fatal
- **The objection in a reviewer's words**: "A leaf does not care whether its veins form one large mutually-connected blob. It cares whether water can reach a given mesophyll region *from the petiole*. Both prior treatments of this exact problem got this right: Brodribb et al. (2016) scored the fraction of the network 'still connected to the petiole,' and Mander & Williams (2024) scored 'the proportion of the network that remains attached to the structural vein.' This paper scores the largest mutually-connected component in a **crop window that contains no petiole and no major structural vein**, with — by the authors' own code documentation — no root attachment enforced. Two disconnected halves of a leaf both still fed by the midrib would register as catastrophic failure here and as no failure at all in the plant."
- **Supporting literature**:
  - Brodribb, T. J., Bienaimé, D., & Marmottant, P. (2016). Revealing catastrophic failure of leaf networks under stress. *PNAS*. https://doi.org/10.1073/pnas.1522569113 — **DOI verified; volume/pages not verified.** Reticulate *Quercus* and *Eucalyptus* degrade gradually "because the loops allowed some parts of the venation network to remain connected to the petiole," while branching *Adiantum* fails catastrophically.
  - Mander, L., & Williams, H. T. P. (2024). The robustness of some Carboniferous fossil leaf venation networks to simulated damage. *Royal Society Open Science, 11*(5), 240086. https://doi.org/10.1098/rsos.240086 — **open access; verified.** Nine taxa, random removal plus localised blade excision, robustness scored as the fraction remaining attached to the structural vein.
  - Sack, L., et al. (2008). Leaf palmate venation and vascular redundancy confer tolerance of hydraulic disruption. *PNAS*. https://doi.org/10.1073/pnas.0709333105 — **DOI verified; volume/pages not verified.** Empirically, **all** leaves tested showed *complete* tolerance of damage to second- and higher-order veins; only midrib severance in pinnate leaves caused measurable decline.
- **Is it correct?**: **Yes.** The GCC criterion is a defensible network-science observable but a poor physiological one, and the paper is on record (its own code/prose mismatch log) as not enforcing root attachment. Sack et al. (2008) makes it worse: real leaves absorb minor-vein damage with *no measurable* hydraulic penalty, so any threshold located at 20% minor-vein-node loss has no empirical functional correlate.
- **Best available defence**: Run the source-anchored variant. Designate the highest-order vein present in each crop window as a pseudo-source and report connectivity-to-source alongside GCC; if the two rank leaves similarly, the objection is defused cheaply. Cite Mander & Williams (2024) as methodological precedent either way.
- **What the paper must concede**: "Because the traced networks are lamina crop windows lacking petioles and primary veins, we score the giant connected component rather than connectivity to a hydraulic source; this is a weaker functional criterion than the petiole-anchored measures used by Brodribb et al. (2016) and Mander & Williams (2024)."

---

### Attack 5: 100–122 species spanning ferns and angiosperms are treated as independent observations, and the headline predictor is exactly the trait that separates those two clades.

- **Severity**: **Major**
- **The objection in a reviewer's words**: "Every correlation in this paper — ⟨k⟩ vs p_c at ρ = 0.733, loop fraction at 0.727 — is computed across species as if they were independent draws. They are not; this has been standard knowledge since Felsenstein (1985), and venation traits are known to carry significant phylogenetic signal. Worse, the dataset spans ferns and angiosperms, and open dichotomous versus reticulate venation is close to a clade label. The reported ⟨k⟩–p_c relationship may be a single two-clade contrast with an effective sample size near two, dressed up as n = 100. No phylogenetic correction is applied and no clade is reported as a covariate."
- **Supporting literature**:
  - Felsenstein, J. (1985). Phylogenies and the comparative method. *The American Naturalist, 125*(1), 1–15. https://doi.org/10.1086/284325 — **DOI from memory, not verified in this pass; verify before citing.** The foundational statement that species values are not independent data points.
  - Matos, I. S., Vu, B., Mann, J., … Blonder, B. W. (2025). Leaf venation network evolution across clades and scales. *Nature Plants, 11*(6), 1127–1141. https://doi.org/10.1038/s41477-025-02011-y — **paywalled; abstract verified.** Same research group, ~1,000 extant and fossil plants; networks evolved toward increased vein density and smoother loops, with architecture diversity structured across clades and 400 Myr — i.e., loopiness is an evolutionarily structured trait, not an independent draw.
  - Additional support from the index (**not read in full**): minor vein density and primary vein type are reported to carry significant phylogenetic signal and strong clade concentration at global scales (e.g. 22 of 48 parallel-veined species being grasses).
- **Is it correct?**: **Yes, and it is cheap for a reviewer to raise and expensive to ignore.** The specific fern/angiosperm version is the sharp one — a reviewer can ask for a single scatter plot coloured by clade and the answer will be visible immediately. Mitigating factor: the synthetic causal grid (ρ = 0.991, n = 42) is phylogeny-free by construction and carries the causal claim, so the empirical correlation is not the only leg the argument stands on.
- **Best available defence**: Fit PGLS or independent contrasts using an available megatree; if unavailable, at minimum report the relationship *within* angiosperms alone and colour all scatter plots by clade. Lean explicitly on the synthetic grid as the causal evidence and demote the cross-species correlations to descriptive.
- **What the paper must concede**: "Cross-species correlations are reported without phylogenetic correction; given significant phylogenetic signal in venation traits and the fern–angiosperm span of this sample, their effective degrees of freedom are lower than n and they should be read as descriptive rather than as evidence of adaptive association."

---

### Attack 6: The reticulation benefit is largest in the *worst* tracings, which is the signature of an artefact.

- **Severity**: **Major** (internal; no literature needed and none exists to rescue it)
- **The objection in a reviewer's words**: "Grade B tracings — those the data providers flagged as *missing minor veins* — show a reticulation benefit of Δ = 0.0137 with 96% of leaves improving. Grade A tracings, the artefact-free ones, show Δ = 0.0069 with only 62% improving. The effect is twice as large and far more consistent in the data known to be defective. The parsimonious reading is that rewiring toward higher ⟨k⟩ is partially *restoring veins the tracing pipeline dropped*, and the 'benefit' is measurement recovery, not biology. On the clean subset the effect is barely distinguishable from a coin flip."
- **Supporting literature**: **No literature found; this is a reasoning-level objection** — and it is the strongest one in the paper's internals, because it comes from the paper's own stratified table.
- **Is it correct?**: **Yes.** A 62% improvement rate on n = 21 clean leaves is not significantly different from 50% by any test the authors could run. The quality-grade gradient runs in exactly the direction an artefact would.
- **Best available defence**: There is one, and it is decent: if grade B leaves systematically have *lower* baseline ⟨k⟩ (because minor veins are missing), then a larger response to ⟨k⟩ enhancement is the *predicted* behaviour of a monotone saturating response, not an artefact. **Test this**: regress Δ on baseline ⟨k⟩ and check whether quality grade retains any effect after conditioning on it. If it does not, the objection dissolves cleanly.
- **What the paper must concede**: "The reticulation benefit is largest in tracings graded as missing minor veins (Δ = 0.0137, 96% improved) and weakest in artefact-free tracings (Δ = 0.0069, 62% improved, n = 21); we cannot fully separate a genuine topological effect from recovery of vein segments lost during extraction, and the artefact-free subset provides only weak support."

---

### Attack 7: p_c is not a percolation threshold — it is an arbitrary-criterion crossing that changes by a factor of 3.5 with system size.

- **Severity**: **Major**
- **The objection in a reviewer's words**: "The authors call their quantity p_c and place it in a percolation framework, but they report that with D and ⟨k⟩ held fixed, it falls from 0.2701 to 0.0772 as N goes from 1,023 to 16,383 — a factor of 3.5, with no sign of convergence. That is not a threshold; it is a system-size-dependent readout of an arbitrary 'GCC < 50% of N₀' rule. Since empirical leaves vary in N (median 15,404, but they are crop windows of varying extent), a large part of the between-leaf variance in p_c may simply be variance in window size. No finite-size scaling collapse, no β, no universality class is offered — so on what basis is this called percolation at all?"
- **Supporting literature**: **No literature needed; this is internal.** For context on what a proper treatment looks like, Mrad et al. (2021) does derive a genuine percolation threshold for xylem, which sets the bar a reviewer will hold this to.
- **Is it correct?**: **Yes, and this is the attack a physics-trained panellist will lead with.** The most damaging consequence is the confound: **the paper must show that empirical p_c is not correlated with N across the 100 leaves.** If it is, the headline ⟨k⟩–p_c relationship is partly a window-size effect. This appears not to have been checked.
- **Best available defence**: (a) Report the p_c–N correlation across empirical leaves immediately; if null, say so prominently and the objection largely dies. (b) Rename the quantity — "critical removal fraction f₅₀" or similar — and drop the p_c notation and the implied threshold semantics. (c) Present the finite-size sweep as an explicit scope limitation rather than burying it. The paper already correctly declines to make a finite-size claim; it should say why, loudly.
- **What the paper must concede**: "Our critical removal fraction is defined by a fixed GCC-halving criterion and is strongly system-size dependent (0.2701 → 0.0772 for N = 1,023 → 16,383); it is a comparative index across networks of similar size, not a percolation threshold in the statistical-physics sense, and we make no finite-size scaling or universality claim."

---

### Attack 8: ⟨k⟩ and loop fraction correlate at ρ = 0.994 and are reported as two predictors; the causal grid then extrapolates a third beyond all empirical data; the response surface over-predicts the actual effect by 3.7×.

- **Severity**: **Major** (internal, three-in-one)
- **The objection in a reviewer's words**: "Two 'predictors' correlating at 0.994 are one predictor. Reporting Spearman 0.733 and 0.727 as if they were independent lines of evidence inflates the apparent support. Separately, the synthetic grid that carries the causal claim runs ⟨k⟩ to 4.00 against an empirical maximum of 2.99 — its entire upper third is outside the space any leaf occupies, and the 14:1 dominance of ⟨k⟩ over D is estimated partly from that void. Finally, the authors' own headroom diagnostic shows the response surface over-predicting measured p_c (0.2595 vs 0.1998) and over-predicting the reticulation gain by 3.7× relative to direct rewiring. A model that misses the effect size by nearly fourfold is not a quantitative model."
- **Supporting literature**: **No literature found; reasoning-level.**
- **Is it correct?**: **Yes on all three.** The collinearity point is the most straightforwardly damaging because it is arithmetic. Note one thing in the paper's favour that it should exploit: the 3.7× over-prediction is *reported by the authors themselves*, and a reviewer who sees it disclosed and quantified will treat it very differently from one who discovers it.
- **Best available defence**: Collapse ⟨k⟩ and loop fraction into a single named axis ("reticulation") and say explicitly that they are one construct measured two ways — this is honest and actually *strengthens* the narrative. Truncate the causal grid to the empirical ⟨k⟩ range (≤ 2.99) and re-report the ⟨k⟩:D dominance ratio on the truncated grid; if it survives, that number is far more defensible. Present the 3.7× gap as a deliberate validity check that establishes the response surface as qualitative only.
- **What the paper must concede**: "⟨k⟩ and loop fraction are collinear at ρ = 0.994 and constitute a single reticulation axis rather than independent predictors; the synthetic grid's upper ⟨k⟩ range has no empirical counterpart; and because the response surface over-predicts the measured reticulation gain by 3.7×, it should be interpreted as directional rather than quantitative."

---

### Attack 9: The headline validation is a re-implementation check, not a physical validation — and the one genuine physical test failed.

- **Severity**: **Major**
- **The objection in a reviewer's words**: "The abstract will presumably advertise agreement to 1×10⁻⁷ across 5.67 million veins. That number validates nothing physical: the source column is itself an ℓ/r⁴ construct from segmented vein width, so the authors have confirmed they can reproduce Hagen–Poiseuille arithmetic that someone else already did. The one test against an independent physical measurement — K_leaf against measured whole-leaf conductance — returned ρ = 0.187, p = 0.073, n = 93. That is a null result. A paper cannot foreground a tautology as validation while its actual validation fails."
- **Supporting literature**: The null result is *explicable* rather than fatal, via Scoffoni et al. (2017) — see Attack 2. Also relevant, and honest to cite against oneself: the Kleaf–vein density literature reports "positive, negative or even no correlations" across studies, so a weak topology→K_leaf link is the field's normal state, not this paper's failure alone.
- **Is it correct?**: **Yes on the characterisation.** The 1e-7 agreement is a unit test. Whether it is fatal depends entirely on how it is labelled — this is a *presentation* problem that becomes an *integrity* problem if the paper calls it validation without qualification.
- **Best available defence**: Relabel it: "numerical verification of the solver against the source dataset's own resistance computation." Then present the K_leaf null with Scoffoni et al. (2017) as the explanation, and frame it as evidence that xylem topology alone is insufficient to predict whole-leaf conductance — which is a genuine contribution to state.
- **What the paper must concede**: "Agreement with the source dataset's resistance column verifies our solver implementation rather than the physical model, since that column is itself constructed as ℓ/r⁴; our only test against independent measurement, K_leaf versus measured whole-leaf conductance, was non-significant (ρ = 0.187, p = 0.073, n = 93)."

---

### Attack 10: Prior art — percolation-based robustness analysis of leaf venation networks already exists, and so does percolation analysis of xylem.

- **Severity**: **Major** (to novelty specifically; the memory notes already flag "hedge novelty claim" as a to-do, correctly)
- **The objection in a reviewer's words**: "Mander & Williams (2024) performed random-removal robustness analysis on leaf venation networks with connected-component tracking and reported collapse transitions, including a modern angiosperm. Mrad et al. (2021) applied graph theory and percolation theory to xylem and explicitly identified a percolation threshold as a seal against embolism spread. Brodribb et al. (2016) established the reticulate-versus-branching robustness contrast experimentally. What, precisely, is new here?"
- **Supporting literature**: Mander & Williams (2024), *R. Soc. Open Sci. 11*(5), 240086, https://doi.org/10.1098/rsos.240086 — **open access.** Mrad et al. (2021), *New Phytologist 231*(3), 996–1007, https://doi.org/10.1111/nph.17429 — **paywalled; abstract verified.** Brodribb et al. (2016), https://doi.org/10.1073/pnas.1522569113.
- **Is it correct?**: **Partly.** There is real remaining novelty: scale (100+ species vs 9 taxa), the Hagen–Poiseuille/Kirchhoff coupling, degree-targeted removal, and the synthetic causal grid decoupling ⟨k⟩ from D. But a novelty claim phrased as "first to apply percolation to leaf venation networks" is false and would be caught immediately.
- **Best available defence**: Cite all three prominently and position the contribution as *comparative scale plus causal decoupling*: prior work established that loops help; this work quantifies how much, across a large species sample, and isolates ⟨k⟩ from D as the operative axis. That is a defensible and honest claim.
- **What the paper must concede**: "Percolation-style robustness analysis of leaf venation networks (Mander & Williams, 2024) and of xylem conduit networks (Mrad et al., 2021) precede this work; our contribution is comparative scale and the experimental decoupling of mean degree from fractal dimension."

---

### Attack 11: A haustorium is a spatially localised disturbance; uniform random node removal is the wrong attack model, and the paper cannot say in which direction the error runs.

- **Severity**: **Moderate**
- **The objection in a reviewer's words**: "No parasite computes betweenness centrality, and a haustorium is a point disturbance, not a uniform sprinkle. The localised-attack literature shows the threshold depends strongly on both attack geometry and network class — and leaf venation is spatially embedded and near-planar, exactly the regime where these differences are largest. The authors report random and degree-targeted removal and neither corresponds to the disturbance they invoke."
- **Supporting literature**:
  - Shao, S., Huang, X., Stanley, H. E., & Havlin, S. (2015). Percolation of localized attack on complex networks. *New Journal of Physics, 17*(2), 023049. https://doi.org/10.1088/1367-2630/17/2/023049 — **open access; abstract partially verified.** Key finding from the index: random-regular networks are *more robust* to localised than random attack, while scale-free networks are *much more damaged* by localised attack; ER networks are intermediate.
  - Berezin, Y., Bashan, A., Danziger, M. M., Li, D., & Havlin, S. (2015). Localized attacks on spatially embedded networks with dependencies. *Scientific Reports, 5*, 8934. https://doi.org/10.1038/srep08934 — **open access.** Localised attack above a critical size *independent of system size* triggers cascading collapse in spatially embedded networks. **Caveat the authors should note honestly: this result requires dependency links, which a leaf vein network does not obviously have** — so it bounds the concern rather than proving it.
  - Mander & Williams (2024) is directly relevant here too: they ran *both* random vein removal and localised blade excision on leaf networks, and found branched networks failed catastrophically under blade attack via "lucky strikes."
- **Is it correct?**: **The objection is correct that random removal is unmotivated; it is *not* correct that the paper is necessarily anti-conservative.** With ⟨k⟩ = 2.520 and degree SD = 0.848, this is a narrow, near-regular, near-planar network — the Shao et al. class that is *more* robust to localised attack than to random. So the paper's random-removal p_c may be conservative. The real damage is that the paper **does not know**, and has not run the test that would tell it.
- **Best available defence**: Run localised (spatially contiguous) node removal on a subset — Mander & Williams (2024) supply the protocol, and this is cheap. Then cite Shao et al. (2015) to argue that for a near-regular spatial network, random removal is a reasonable and likely conservative proxy.
- **What the paper must concede**: "Random and degree-targeted removal are generic damage models; a haustorial disturbance is spatially localised, and the localised-attack literature shows thresholds are attack-geometry dependent in a network-class-specific way (Shao et al., 2015). We do not simulate localised attack and cannot state the direction of the resulting bias."

---

### Attack 12: Box-counting D is a weak and partly artefactual descriptor, and here it is also the loser in the paper's own analysis.

- **Severity**: **Moderate**
- **The objection in a reviewer's words**: "Box-counting fractal dimension on leaf images is known to be area-dependent, valid only over a restricted scale range, and blind to lacunarity; across 61 species it failed to discriminate leaf forms at all. On crop windows of varying extent and varying tracing quality, D is likely tracking window size, vein density and image resolution as much as biology. Why is it in the paper?"
- **Supporting literature**:
  - Muraleedharan, V., Rajan, R., & Jaishanker, R. (2023). Determining the limits of traditional box-counting fractal analysis in leaf complexity studies. *Flora, 304*, 152300. https://doi.org/10.1016/j.flora.2023.152300 — **DOI inferred from the article number; verify the DOI string before citing.** Paywalled (ScienceDirect); findings taken from the abstract/index. Key points: fractal properties of leaves hold only over a limited scale range, causing linear-regression D estimates to fail; box-counting is area-dependent and fails to capture lacunarity; across 61 species no significant variation in D distinguished leaf forms.
- **Is it correct?**: **Yes on the critique of D as a construct**, but this attack is **largely self-neutralising**, because the paper's own conclusion is that D *loses* — 14:1 standardised dominance of ⟨k⟩ over D in the causal grid, partial ρ dropping from 0.496 to 0.503 vs ⟨k⟩'s 0.736. The paper is not resting weight on D. The residual risk is the crop-window confound: D and window size may covary.
- **Best available defence**: Cite Muraleedharan et al. (2023) *pre-emptively*, report D's scaling range explicitly, check D against window area, and frame the result as "even granting D generous treatment, it is dominated 14:1 by mean degree" — which converts a weakness into a robustness argument.
- **What the paper must concede**: "Box-counting D is scale-range-limited and area-dependent (Muraleedharan et al., 2023) and, on crop windows of varying extent, may partly reflect image geometry; we report it because it is dominated by mean degree in our causal analysis, not because we regard it as a robust functional descriptor."

---

### Attack 13: Connectivity has been argued to *increase* embolism vulnerability, and the paper does not engage with it.

- **Severity**: **Moderate** (downgraded from the brief's assumption — see the corrections above)
- **The objection in a reviewer's words**: "Loepfe et al. (2007) showed with an explicit 3D network model that vulnerability to embolism *increases* with xylem network connectivity, because connectivity determines the fraction of paths available for both water transport and embolism spread. The paper asserts the opposite sign as though it were uncontested. Failing to cite the one modelling study that reaches the opposite conclusion is a citation-selection problem."
- **Supporting literature**:
  - Loepfe, L., Martinez-Vilalta, J., Piñol, J., & Mencuccini, M. (2007). The relevance of xylem network structure for plant hydraulic efficiency and safety. *Journal of Theoretical Biology, 247*(4), 788–803. https://doi.org/10.1016/j.jtbi.2007.03.036 — **paywalled; abstract verified.** Verbatim: *"maximum hydraulic conductivity and vulnerability to embolism increase with the connectivity of the xylem network,"* because connectivity determines *"the fraction of all the potential paths or conduits actually available for water transport and spread of embolism."*
  - **Countervailing, and it is decisive**: Mrad et al. (2021) tested exactly this trade-off with graph and percolation theory validated against *Acer* anatomy and concluded that for vessel-bearing species, connectivity *improves* resistance to embolism spread without cost to conductivity. Brodribb et al. (2016) supports the same sign experimentally at leaf scale.
- **Is it correct?**: **The citation gap is a real fault; the scientific threat is modest.** Loepfe models *air-seeding contagion between adjacent conduits*, where connectivity is a transmission channel. This paper models *node removal and connectivity loss*, where connectivity is redundancy. These are different processes and the opposite signs are not actually in conflict — but the paper must say so rather than leave the reader to notice.
- **Best available defence**: Cite Loepfe explicitly, then resolve it with Mrad et al. (2021) and Brodribb et al. (2016). Make the mechanism distinction plainly: in contagion-driven failure connectivity is a liability; in removal-driven failure it is redundancy. This is a *strengthening* paragraph, not a defensive one.
- **What the paper must concede**: "Connectivity has opposite effects depending on failure mode: it accelerates air-seeding contagion (Loepfe et al., 2007) while providing redundancy against conduit loss (Mrad et al., 2021). Our model represents the latter only, and therefore cannot describe contagion-dominated failure."

---

### Attack 14: A vein segment is not a conduit, and the model silently equates them.

- **Severity**: **Moderate**
- **The objection in a reviewer's words**: "Percolation is being run on a graph whose nodes are *vein junctions* and edges are *vein segments*. But a single vein segment contains many xylem conduits in parallel, and the number varies by an order of magnitude between major and minor vein orders. Removing a 'node' therefore means something completely different in a midrib than in a fourth-order veinlet, and the model treats them identically. Embolism, the process being invoked, occurs at conduit scale, one conduit at a time — it does not delete vein junctions."
- **Supporting literature**:
  - Scoffoni, C., et al. (2017). Leaf vein xylem conduit diameter influences susceptibility to embolism and hydraulic decline. *New Phytologist*. https://doi.org/10.1111/nph.14256 — **DOI verified from index; abstract not read in this pass.** Establishes conduit-diameter-level control of embolism susceptibility, i.e. sub-segment scale.
  - Jacobsen, A. L., et al. (2024). Sap flow through partially embolized xylem vessel networks. *Plant, Cell & Environment*. https://doi.org/10.1111/pce.14990 — **DOI verified from index; abstract not read.** Directly relevant: flow persists through *partially* embolised networks, i.e. binary node presence/absence is the wrong state space.
  - Also relevant: the Plant Physiology finding that *"xylem embolism spreads by single-conduit events"* in dry-forest angiosperm stems (title verified from index; citation not fully captured — verify before use).
- **Is it correct?**: **Yes, and the "partially embolised" point is the sharp end.** Site percolation imposes a binary node state, but a vein segment losing 3 of 30 conduits is neither present nor absent. The paper's use of Murray's Law where radii are unavailable compounds this by assuming an idealised branching relation that the crop-window data cannot check.
- **Best available defence**: State the scale explicitly and own it: this is a *vein-network-scale* model of connectivity loss, an abstraction one level above conduit-scale embolism, appropriate for asking how network layout bounds damage tolerance and inappropriate for predicting embolism dynamics. Cite Mrad et al. (2021) as the conduit-scale complement.
- **What the paper must concede**: "Nodes represent vein junctions, not xylem conduits; since a vein segment contains many conduits in parallel and can be partially embolised while still conducting (Jacobsen et al., 2024), binary node removal is a coarse abstraction of conduit-level embolism and overstates the functional consequence of any single removal."

---

### Attack 15: A static topological model cannot represent a regulated, dynamic, capacitive system.

- **Severity**: **Minor to Moderate** (predictable, and every modelling paper faces it)
- **The objection in a reviewer's words**: "The leaf is not a static resistor network. Stomata close and change the boundary condition before most of this damage could accumulate; capacitance buffers transients; some species refill; leaves grow. A steady-state Kirchhoff solve on a frozen graph has no way to represent any of it, and the 'pre-symptomatic window' is computed in arbitrary time units with no time constants from any measured infestation."
- **Supporting literature**: Scoffoni et al. (2017), https://doi.org/10.1104/pp.16.01643, does the real damage here rather than any dedicated source — the dominant outside-xylem resistance it identifies is itself *dynamic and turgor-dependent*, so the static-network idealisation omits the controlling variable, not merely a refinement. Otherwise: **no dedicated literature found; largely a reasoning-level objection.**
- **Is it correct?**: **Yes but bounded.** Every network model makes this trade. The genuinely weak piece is the pre-symptomatic window calculation: it is analytic, in arbitrary time units, built on the *synthetic* p_c = 0.271 and f_c = 0.524 rather than the empirical values, and calibrated to nothing. That is the part a reviewer will single out.
- **Best available defence**: Keep the static model and defend it as a structural-bound analysis. **Consider cutting the pre-symptomatic window section entirely** — it is the lowest-value, highest-risk component in the paper, it uses synthetic rather than empirical thresholds, and it invites exactly the dynamics objection the rest of the paper can otherwise sidestep.
- **What the paper must concede**: "Our model is static and steady-state, omitting stomatal regulation, capacitance, refilling and growth; the pre-symptomatic window is an analytic illustration in arbitrary time units based on synthetic threshold values and is not calibrated to any measured infestation time course."

---

## LITERATURE THAT DIRECTLY CONTRADICTS A PAPER CLAIM

**Card 1 — Scoffoni et al. (2017). The premise-killer.**
Scoffoni, C., Albuquerque, C., Brodersen, C. R., Townes, S. V., John, G. P., Bartlett, M. K., Buckley, T. N., McElrone, A. J., & Sack, L. (2017). Outside-xylem vulnerability, not xylem embolism, controls leaf hydraulic decline during dehydration. *Plant Physiology, 173*(2), 1197–1210. https://doi.org/10.1104/pp.16.01643 — **paywalled; abstract verified verbatim.**
*Contradicts*: that pre-symptomatic leaf hydraulic decline is a xylem-network connectivity phenomenon.
*Evidence*: In vivo x-ray microCT across four angiosperms — at turgor loss point only small fractions of vein xylem conduits were embolised, and substantial embolism arose only under severe dehydration. Across eight species, outside-xylem vulnerability explained **75–100%** of K_leaf decline from mild stress to beyond turgor loss.
*Damage*: Removes the mechanistic basis for the title's "pre-symptomatic." Also independently explains the paper's failed K_leaf validation, which converts it from a contradiction into a partial alibi if handled well.

**Card 2 — Matos et al. (2024). The same-data contradiction.**
Matos, I. S., et al. (2024). Leaf venation network architecture coordinates functional trade-offs across vein spatial scales: Evidence for multiple alternative designs. *New Phytologist, 244*(2), 407–425. https://doi.org/10.1111/nph.20037 — **paywalled; abstract verified verbatim.**
*Contradicts*: that venation architecture strongly predicts resilience.
*Evidence*: Verbatim — *"generalized architecture–function trade-offs are weak. Architecture strongly predicts leaf support and damage resistance axes but weakly predicts efficiency and resilience axes."* Same 122 species, same networks.
*Damage*: Maximum, because it is the paper's own data source and requires zero specialist knowledge to raise. Partial escape: their "resilience" is trait-derived, ours is simulation-derived — but that escape concedes the simulation is unvalidated against measured function.

**Card 3 — Sack et al. (2008). The no-functional-threshold result.**
Sack, L., et al. (2008). Leaf palmate venation and vascular redundancy confer tolerance of hydraulic disruption. *PNAS*. https://doi.org/10.1073/pnas.0709333105 — **DOI verified; volume/pages NOT verified — check before citing.**
*Contradicts*: that a ~20% node-removal threshold has functional meaning.
*Evidence*: In vivo severing experiments — **all** leaves tested showed *complete* tolerance of damage to second- and higher-order veins. Only midrib severance in pinnately veined leaves reduced K_leaf, g_s and photosynthesis; palmate leaves were minimally affected.
*Damage*: Cuts both ways. It contradicts the existence of a functionally meaningful minor-vein percolation threshold, but it is simultaneously the **best empirical support in existence** for the paper's central thesis that redundant reticulate networks confer damage tolerance. Cite it; do not let a reviewer introduce it first.

**Card 4 — Loepfe et al. (2007). The sign reversal.**
Loepfe, L., Martinez-Vilalta, J., Piñol, J., & Mencuccini, M. (2007). The relevance of xylem network structure for plant hydraulic efficiency and safety. *Journal of Theoretical Biology, 247*(4), 788–803. https://doi.org/10.1016/j.jtbi.2007.03.036 — **paywalled; abstract verified.**
*Contradicts*: connectivity → safety.
*Evidence*: *"maximum hydraulic conductivity and vulnerability to embolism increase with the connectivity of the xylem network."*
*Damage*: Moderate and answerable — different failure mode (contagion vs removal), different scale (conduit vs vein), and effectively superseded for vessel-bearing species by Mrad et al. (2021).

**Card 5 — Mander & Williams (2024). The novelty threat (open access).**
Mander, L., & Williams, H. T. P. (2024). The robustness of some Carboniferous fossil leaf venation networks to simulated damage. *Royal Society Open Science, 11*(5), 240086. https://doi.org/10.1098/rsos.240086 — **open access; verified.**
*Contradicts*: any "first to apply percolation-style robustness analysis to leaf venation" claim.
*Evidence*: Nine taxa (five Pennsylvanian pteridosperms, two branched forms, modern *Betula alba*); random vein-pixel removal plus localised blade excision; connected-component robustness scored as fraction remaining attached to the structural vein; collapse transitions reported (*Rhacopteris lindsaeformis* collapsing at ~95% remaining vs *Betula alba* tolerating down to ~60%).
*Damage*: Kills a strong novelty claim, and its source-anchored metric shows up this paper's rootless GCC. But it is also a methodological ally and a precedent to cite.

**Card 6 — Mrad et al. (2021). Reclassified: ALLY, plus prior art.**
Mrad, A., Johnson, D. M., Love, D. M., & Domec, J.-C. (2021). The roles of conduit redundancy and connectivity in xylem hydraulic functions. *New Phytologist, 231*(3), 996–1007. https://doi.org/10.1111/nph.17429 — **paywalled; abstract verified verbatim.**
*Supports*: connectivity → safety. Verbatim: *"Considering only species with vessels, increases in connectivity improve resistance to embolism spread without negatively affecting hydraulic conductivity."* Uses graph theory, percolation theory and computational xylem modelling, validated on *Acer* branch anatomy, and describes the percolation threshold as *"an effective 'seal' against uninhibited embolism spread."*
*Note*: The shared context had this paper's conclusion backwards. It is the single best citation available for the paper's core claim, and it should be moved from a "threats" list into the Introduction.

**Card 7 — Brodribb et al. (2016). Ally, plus the petiole-anchoring problem.**
Brodribb, T. J., Bienaimé, D., & Marmottant, P. (2016). Revealing catastrophic failure of leaf networks under stress. *PNAS*. https://doi.org/10.1073/pnas.1522569113 — **DOI verified; volume/pages not verified.** Companion method: Brodribb et al. (2016), *New Phytologist*, https://doi.org/10.1111/nph.13846.
*Supports*: reticulate networks degrade gracefully, branching networks fail catastrophically — direct experimental support for the paper's central thesis.
*Complicates*: their functional criterion is connectivity *to the petiole*, not GCC. See Attack 4.

**Card 8 — Kaga et al. (2020). The haustorium is additive.**
Kaga, Y., et al. (2020). Interspecific signaling between the parasitic plant and the host plants regulate xylem vessel cell differentiation in haustoria of *Cuscuta campestris*. *Frontiers in Plant Science, 11*, 193. https://doi.org/10.3389/fpls.2020.00193 — **open access.**
*Contradicts*: that haustorial infection corresponds to host vein-junction removal.
*Evidence*: Searching hyphae contacting host xylem acquire xylem identity and form a continuous xylem bridge between parasite and host.
*Damage*: Total, to the mechanistic link between parasitism and node deletion.

---

## CLAIMS THAT SHOULD BE SOFTENED RATHER THAN DEFENDED

| Current claim | Softened form |
|---|---|
| "Pre-symptomatic vascular collapse under holoparasitic haustorial sink stress" (title) | "Topological robustness of leaf venation networks to vein loss, with an illustrative haustorial sink model." **Remove the parasite from the title.** Scoffoni et al. (2017) makes "pre-symptomatic" indefensible for a xylem-topology model, and the sink produced zero embolism. |
| "p_c" as a percolation threshold | "f₅₀, the critical removal fraction at a fixed GCC-halving criterion" — a comparative index for same-sized networks. Report the empirical p_c vs N correlation to rule out the window-size confound. |
| ⟨k⟩ (ρ = 0.733) and loop fraction (ρ = 0.727) as two predictors | One reticulation axis measured two ways (ρ = 0.994 between them). Report a single coefficient. |
| "⟨k⟩ dominates D 14:1" | "⟨k⟩ dominates D by an order of magnitude within the empirically observed range (⟨k⟩ ≤ 2.99)" — recompute on the truncated grid and report that number instead. |
| "Reticulation enhancement improves p_c in 93/105 leaves" | "…in 96% of grade-B tracings but only 62% of artefact-free grade-A tracings (n = 21); the effect is not clearly established on the clean subset." |
| "Validated to 1e-7 across 5.67M veins" | "Solver numerically verified against the source dataset's own ℓ/r⁴ resistance column" — explicitly a re-implementation check. |
| "Reticulation is a host-resistance trait" | "Network topology bounds structural tolerance to vein loss; whether this translates into resistance in planta is untested, and measured whole-leaf conductance did not correlate with our topological prediction (ρ = 0.187, p = 0.073)." |
| Any "first to apply percolation to leaf venation" claim | "Extends percolation-based robustness analysis of leaf venation (Mander & Williams, 2024) and of xylem (Mrad et al., 2021) to a large comparative species sample with experimental decoupling of ⟨k⟩ and D." |
| Cross-species Spearman correlations | Descriptive only, pending phylogenetic correction; report clade-coloured and within-angiosperm. |
| The pre-symptomatic window section | **Cut it**, or reduce to a clearly labelled dimensionless illustration. It uses synthetic rather than empirical thresholds, is in arbitrary time units, and is uncalibrated. |

---

## CLAIMS THAT ARE SAFE

Put the weight here.

1. **The synthetic causal grid result: mean degree, not fractal dimension, controls topological robustness.** n = 42, ⟨k⟩ and D decoupled by construction (Pearson 0.086), ρ = 0.991, R² = 0.887. This is phylogeny-free, artefact-free, quality-grade-free, and internally generated. It is the paper's strongest and most defensible finding. **Truncate it to ⟨k⟩ ≤ 2.99 and it becomes close to unassailable.**
2. **Degree-targeted removal reduces p_c relative to random (0.200 → 0.169, 15.7%, 100/100 leaves).** A within-leaf comparison, so most confounds (window size, tracing quality, phylogeny, N) cancel. 100/100 consistency is very hard to attack.
3. **Leaf venation networks are not scale-free.** ⟨k⟩ = 2.520, degree SD = 0.848 — narrow. Well-supported, correctly stated, and useful because it rules out the hub-vulnerability story a reviewer might otherwise assume.
4. **The reticulation-confers-damage-tolerance mechanism in general.** Backed by three independent strands the paper should cite prominently: Sack et al. (2008) experimentally (complete tolerance of higher-order vein damage; palmate > pinnate under midrib severance), Brodribb et al. (2016) experimentally (graceful vs catastrophic), Mrad et al. (2021) theoretically at conduit scale. The *direction* of the paper's claim is well supported even where its *magnitude and mechanism* are not.
5. **Solver correctness.** The 1e-7 agreement over 5,668,467 veins genuinely establishes the implementation is right — just label it verification, not validation.
6. **The zero-embolism sink result, if reported as a finding.** Under a literature-calibrated diversion at gradients spanning 0–3.0 MPa, host minimum ψ reached −1.02 MPa against a −2.0 MPa threshold and no vessels cavitated. Presented as a negative result about holoparasitic water diversion, this is defensible, novel, and honest. Presented as a mechanism that drives the headline, it is Attack 3.
7. **The paper's own self-diagnostics.** The headroom check (3.7× over-prediction), the finite-size sweep, the quality-grade stratification, and the K_leaf null are all things the authors found and reported themselves. Foregrounded as deliberate validity checks rather than buried, they are a substantial credibility asset — a reviewer who sees them disclosed reads the paper very differently from one who discovers them.

**Two immediate action items before submission**, both cheap and both closing a Major attack: (a) report the correlation between empirical p_c and network size N across the 100 leaves — this closes the finite-size confound in Attack 7; (b) regress the reticulation gain Δ on baseline ⟨k⟩ and test whether quality grade survives — this closes Attack 6. And correct the Mrad citation direction wherever the draft currently treats it as contrary evidence.
agentId: aac198684eabca858 (use SendMessage with to: 'aac198684eabca858', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 87031
tool_uses: 33
duration_ms: 548469</usage>