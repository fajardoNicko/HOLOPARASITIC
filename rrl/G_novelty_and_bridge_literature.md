# G — Mander & Williams deconstruction, bridge literature, and the novelty audit

> Verified 2026-08-15. Full-text reads marked explicitly. Quotations below are verbatim from full texts actually opened.

---

## MANDER & WILLIAMS 2024 — FULL DECONSTRUCTION

**Mander, L., & Williams, H. T. P. (2024). The robustness of some Carboniferous fossil leaf venation networks to simulated damage. *Royal Society Open Science, 11*(5), 240086.** https://doi.org/10.1098/rsos.240086
**Access: FULL TEXT READ** (via PMC11076108; the publisher domain returns HTTP 403 to automated fetch).

### What the simulated damage actually did
Two attacks, both on **rasterised binary images**, not on an abstracted graph — the single most important methodological fact about the paper.

1. *Vein attack:* "Firstly, we attacked veins by randomly removing pixels from the venation network, then attached the structural vein of the leaf and counted the pixels in the connected region that remained attached to it." (verified)
2. *Blade attack:* "Secondly, we attacked leaf blades by making circular holes 60 pixels in area in the leaf blade, which removes vein segments from the venation network." (verified)

Replicates: "For each taxon, we repeated each attack 250 times, randomly varying the proportion of pixels removed between 0 and 1 (for vein attacks)" and "randomly varying the number of holes between 0 and 2000 (for leaf blade attacks)." (verified). **Removal is random only — no targeted or centrality-ranked attack anywhere.** 250 replicates per taxon is 3–4 orders of magnitude below this study's Monte Carlo effort.

### Robustness metric
"Our key output metric is the proportion of the venation network that remains after the attack relative to the proportion of the network that remains attached to the structural vein of the leaf by some continuous path in the venation network." (verified) They add: "This metric is a simple proxy for retention of a functional vascular transport system within the leaf." (verified) Scalarised by "we calculated the sum of the 20 mean values to approximate the integral of the trendline." (verified)

This is **connectivity-to-a-source (the midrib)**, not a giant-connected-component criterion, and the summary statistic is an **area under the curve**, not a threshold. Same family as Price & Weitz (2014); neither is this study's p_c.

### Taxa — 9 networks, 8 fossil + 1 extant
*Rhacopteris lindsaeformis* (Mississippian, branched); *Neuropteris heterophylla*, *N. jongmansi* (Pennsylvanian, branched); *Reticulopteris muensteri* and its small morphotype, *Lonchopteridium laxereticulosum*, *Lonchopteris bricei*, *Linopteris subbrongniartii* (Pennsylvanian, net); *Betula alba* (extant, hierarchical reticulate).

### Network extraction
Manual tracing, not automated segmentation: "Leaf venation images were manually traced using a vector graphics software package (Affinity Designer…) and a digital graphics tablet (Wacom One…)." (verified) Then "Tracings of the structural vein and the venation network of each leaf were rasterized and stored as separate binary GIF files…, and rescaled to a standard magnification, with one pixel representing 10 µm, and vein segments in each venation network measuring three pixels in width." (verified)

### Results, with actual numbers
Collapse-*onset* descriptions read off curves, not fitted thresholds:
- *R. lindsaeformis* (least robust): transition begins at ~0.95 of network remaining; retained function drops to ~0.05 when ~0.80 remains.
- *B. alba* (most robust): transition begins at ~0.75 remaining; drops to ~0.05 when ~0.60 remains.
- Pennsylvanian loopy networks: collapse begins at ~0.85 remaining; *L. subbrongniartii* at ~0.8.
- Ranking (verified): "branched venation networks were the least robust in our analysis, net-like architectures were more robust than branched networks, while the hierarchical reticulate network of *B. alba* was the most robust."
- "For all taxa, venation network robustness was greater under a leaf blade attack compared to a vein attack, and this was most pronounced for *L. bricei* and *B. alba*." (verified)

### Threshold / exponent / hydraulic model — CORRECTION TO THE PROJECT RECORD
The prior verification's "NO to all three" is right on substance but **wrong on one point of framing, and the difference matters.**

- *Percolation:* they **do** invoke it explicitly — "This approach is similar to analyses of network robustness based on percolation that show how the size of the largest component of a network changes as elements of the network are removed." (verified). **So it is NOT true that no one has framed venation damage in percolation terms. Do not write that sentence.**
- *Threshold value:* **none reported.** Correct.
- *Critical exponent:* **none reported.** Correct. Qualitative critical language only: "the venation networks of *L. bricei* and *L. subbrongniartii* may show critical behaviour, with increased variability when ~0.80–0.60 of their venation networks remain after damage." (verified)
- *Hydraulic model:* **none.** Correct.

### The two quotations the project relies on — both VERIFIED, verbatim
> "This attack is intended to represent some form of damage at the level of the vein itself, as might be produced by embolism or vein blockage by bacterial colonization, but we do not simulate any processes directly." (verified)

> "For example, in order to specifically measure how water transport capacity is affected by damage to the venation network, a model of fluid flow through the leaf would be needed." (verified)

**Two further quotations that are worth more to this paper than either of the above:**

> "Such a model could be based either on Ohm's Law and the analogy between the flow of current through an electrical circuit and the flow of water through a conduit or on Hagen–Poiseuille calculations of flow rates in hollow tubes, in conjunction with the results of anatomical work reconstructing the hydraulic architecture of fossil leaves." (verified)

> "A more appropriate approach may be that of Mrad et al. who studied xylem hydraulics in *Acer* wood, and modelled flow through vessel lumens using the Hagen–Poiseuille equation… Instead, our simulations are designed to explore the potential nature and range of damage responses in the taxa we have analysed, and also to inform the design of future computational and experimental work in this area." (verified)

**This is the strongest single citation available to the paper.** Mander & Williams, having framed venation damage as percolation, **name the exact method of the present paper — Ohm's-law resistor network / Hagen–Poiseuille — as the missing piece and as future work, and nominate Mrad et al. as the template.** The present paper is the paper they asked for. Put this in the Introduction's closing gap paragraph and in the Discussion.

### What it supports here
(a) Venation-damage robustness is a live question in a Royal Society journal, 2024 — currency of the problem. (b) Reticulate architecture is more damage-robust than branched, across 200+ Myr of leaf evolution — independent, non-circular, deep-time support for the reticulation-enhancement counterfactual. (c) An explicit, quotable statement that the hydraulic-flow layer is absent from the venation-robustness literature and is needed.

### What it does NOT support
Cannot corroborate any p_c value — no threshold reported. Cannot corroborate targeted-attack results — all removal is random. Cannot corroborate anything hydraulic, K_leaf or embolism-related. Cannot support a claim that percolation framing of venation is new. **Their pixel-removal-on-a-raster protocol is not commensurable with site percolation on a junction/segment graph: their "proportion of pixels removed" is not this paper's removed-node fraction, so do NOT place their ~0.85 or ~0.75 collapse-onset values on the same axis as p_c = 0.200.** A referee will catch that.

---

## THE VENATION-ROBUSTNESS LINEAGE

**Price, C. A., & Weitz, J. S. (2014). Costs and benefits of reticulate leaf venation. *BMC Plant Biology, 14*, 234.** | 10.1186/s12870-014-0234-2 | **FULL TEXT READ** (PMC4177576) | 339 leaves, 324 species, 72 angiosperm families, 3,934,626 vein segments, National Cleared Leaf Collection (Smithsonian).
Iterative random removal of vein segments, 1000 iterations: "we iteratively pruned each vein network graph removing from one vein segment up to *N*_vein" (verified). Robustness = integral of "the mean fraction of nodes connected to the root node (the node closest to the point of petiole attachment) vs. the fraction of vein segments removed" (verified), by Riemann sums; robustness range 0.026–0.150; meshedness M = (m−n+1)/(2n−5), range 0.06–0.26, mean 0.14, SD 0.04; reticulate vs MST costs +6.3% length, +12% width, +5.6% surface area, +3.3% volume, **+0.51% theoretical conductance**; "meshedness being the best predictor of robustness" (verified).
**Critical:** the words "percolation", "threshold", "critical", "phase transition" do **not** appear in the text (verified by full-text search).

**Skjegstad, L. E. J., & Kirkegaard, J. B. (2025). Modeling full-scale leaf venation networks. *PLOS Computational Biology, 21*(7), e1013292.** | 10.1371/journal.pcbi.1013292 | **FULL TEXT READ** (PMC12303385) | *Symphoricarpos albus*, *Lonicera xylosteum*, *Crataegus monogyna*; deep-learning segmentation + custom network extraction.
"flux f_i over an edge i is given by the Hagen-Poiseuille law" combined with "Kirchhoff's law", solved via a weighted graph Laplacian for pressures and fluxes across the whole extracted topology; Murray's-law exponent α ≈ 3.0–3.03 in loopy networks.
**The most dangerous paper in this audit for the novelty claim.** Contains **no** percolation, damage, node removal, robustness or resilience analysis anywhere (verified by full-text search); 3 species; no parasite.

**Katifori, E., Szöllősi, G. J., & Magnasco, M. O. (2010). *PRL, 104*(4), 048704.** | 10.1103/PhysRevLett.104.048704 | ABSTRACT ONLY here (see dossier A for a full-text read). Optimal networks are loopless trees under pure efficiency; damage resilience *or* load fluctuation makes loops optimal. Supplies the "why" behind the reticulation-enhancement experiment.

**Ronellenfitsch, H., Lasser, J., Daly, D. C., & Katifori, E. (2015). *PLOS Comput Biol, 11*(12), e1004680.** | 10.1371/journal.pcbi.1004680 | Nested-loop topology encodes information *orthogonal* to standard geometric traits. Directly relevant to the ⟨k⟩ vs D decoupling argument.

**Mileyko, Y., Edelsbrunner, H., Price, C. A., & Weitz, J. S. (2012). *PLOS ONE, 7*(6), e36715.** | 10.1371/journal.pone.0036715 | Generalises Horton–Strahler ordering to weighted planar reticular networks; separates "reticular edges" (loop-forming) from "tree edges" — conceptually the quantity the reticulation-enhancement experiment manipulates.

**Ronellenfitsch, H., & Katifori, E. (2016). *PRL, 117*(13), 138301.** | 10.1103/PhysRevLett.117.138301 | Growth coupled to network development drives the system toward a markedly improved optimum. Contextual. **NOTE:** the manuscript's "Ronellenfitsch & Katifori 2019 PRL 123:038301" is a wrong article number — see dossier A; the correct 2019 paper is PRL 123(24), 248101.

---

## HOW MUCH DOES PRICE & WEITZ 2014 ALREADY ESTABLISH?

Bluntly: **most of the structural core.** Treating this as a minor antecedent would be the most likely single cause of a hostile review.

**What they already have that this paper also has**
1. *The percolation curve itself.* Fraction of nodes connected to the petiole vs fraction of vein segments removed, 1000 iterations, 339 real leaves. They simply declined to call it percolation or extract a threshold.
2. *A larger and cleaner cohort.* 339 **whole cleared leaves** vs this paper's 100 **crop windows** with no petioles. This paper *cannot* compute their metric, because the crop windows contain no petiole. **State this openly as the reason for the GCC criterion rather than letting a referee find it.**
3. *The connectivity-predicts-robustness result.* "meshedness being the best predictor of robustness" (verified). **This is the same finding as this paper's headline.** For a planar graph, meshedness α = (E − N + 1)/(2N − 5) and ⟨k⟩ = 2E/N, so α → (⟨k⟩ − 2)/4 as N grows: **they are the same variable under an affine transform.** The ⟨k⟩→p_c result is therefore best presented as *a sharpened, causally-controlled confirmation of Price & Weitz on a threshold response variable*, not as a discovery. Claiming it as new is the one move that would genuinely damage credibility.
4. *A reticulation counterfactual.* Their reticulate-vs-MST comparison is a de-reticulation counterfactual — the mirror image of the P90 ⟨k⟩ enhancement. The direction is new; the logical move is not.
5. *Cheapness of redundancy.* +0.51% conductance cost — the quantitative backing for "reticulation is nearly free", which the enhancement experiment needs and should cite rather than re-argue.

**What this paper genuinely adds**
1. **Site (node) percolation** rather than bond (segment) removal.
2. **Targeted attacks.** P&W is random-only. Degree- and betweenness-targeted removal on a real leaf cohort is new, and the ordering random > degree > betweenness is a genuinely new empirical statement about leaf venation.
3. **An explicit threshold with a stated criterion**, where P&W deliberately used an AUC scalar and avoided threshold language entirely.
4. **A real flow solve.** P&W's conductance is a per-segment scalar summed, explicitly **not** a network flow solution ("No flow equations solved on networks", verified). The Kirchhoff solve is a categorical methodological advance over P&W and the strongest defensible increment in the comparison.
5. **The fractal-dimension axis and the ⟨k⟩/D decoupling experiment** — absent from P&W.
6. **The haustorial sink** — wholly absent from P&W.

**Honest verdict.** Roughly 60% of the structural claim is pre-existing; the increments are real but incremental, and the paper should say so in its own voice before a referee says it first.

---

## BRIDGE LITERATURE

**Mrad, A., Johnson, D. M., Love, D. M., & Domec, J.-C. (2021). *New Phytologist, 231*(3), 996–1007.** | 10.1111/nph.17429 | ABSTRACT/RECORD ONLY (Wiley 403). **Bridges: percolation ↔ plant hydraulics; topology ↔ embolism resistance; network science ↔ plant biology.** *Acer* stem xylem conduits. Graph theory + percolation theory + computational xylem modelling; treats the percolation threshold as an effective "seal" against uninhibited embolism spread. **Integrated argument enabled:** makes the sign interesting. Reconcilable because different failure processes — contagion along conduits (Mrad) vs structural fragmentation of a junction network (here). It is also the paper Mander & Williams nominate as the right template. **Do not quote it verbatim; the full text was not opened.**

**Brodribb, T. J., Bienaimé, D., & Marmottant, P. (2016). *PNAS, 113*(17), 4865–4869.** | 10.1073/pnas.1522569113 | ABSTRACT ONLY. **Bridges: venation ↔ hydraulic function; topology ↔ embolism; percolation-like cascade ↔ biological failure.** Susceptibility to embolism increases proportionally with vein size; nucleation always in the largest vein. **Integrated argument enabled:** empirical grounding that leaf hydraulic failure really is a network-level, spatially propagating event — and the strongest caution against random removal, since real embolism is *size-ordered*, i.e. targeted toward large veins which are the high-degree, high-betweenness nodes. **This reframes the targeted-attack results as the biologically realistic case and the random result as a conservative upper bound.**

**Loepfe, L., Martinez-Vilalta, J., Piñol, J., & Mencuccini, M. (2007). *J. Theor. Biol., 247*(4), 788–803.** | 10.1016/j.jtbi.2007.03.036 | ABSTRACT ONLY. The founding statement of the connectivity efficiency-vs-safety trade-off and the 14-year antecedent of Mrad. Cite alongside Mrad to show the "connectivity is a liability" tradition is long established, so the opposite-sign result here is presented as process-dependence rather than novelty-by-omission.

**Lu, D., Smith-Martin, C. M., Muscarella, R., Uriarte, M., & Zheng, T. (2025). *AoB PLANTS, 17*(4), plaf020.** | 10.1093/aobpla/plaf020 | **FULL TEXT READ.** Spatial survival modelling of cavitation on vein networks from optical vulnerability imaging, eight tropical tree species; mean C-index 0.542 (SD 0.151); 47 of 53 samples positive vein-thickness coefficients; significant positive correlation between the vein-thickness coefficient and **network connectivity**. The closest 2025 work on real leaf vein networks and hydraulic failure, and it independently implicates *connectivity* from a completely different (survival-analytic) direction. Contains **none** of "percolation", "threshold", "critical", "Kirchhoff", "Hagen-Poiseuille", "giant component", "node removal", "targeted attack" (verified by full-text search). **Omitting it would look like an incomplete search.**

---

## NOVELTY AUDIT

### Prior art that comes closest (ranked)
1. **Price & Weitz (2014)** — percolation curve on 339 real leaves, connectivity metric as best predictor, plus a reticulation counterfactual. Closest on *structure and conclusion*. Missing: threshold, targeted attack, flow solve, parasite.
2. **Skjegstad & Kirkegaard (2025)** — Hagen–Poiseuille + Kirchhoff (graph Laplacian) on real traced leaf venation. Closest on *hydraulic method*. Missing: any damage/removal/robustness/percolation analysis whatsoever.
3. **Mrad et al. (2021)** — percolation theory + graph theory + Hagen–Poiseuille flow in one plant-vascular study. Closest on *the coupling itself*. Missing: leaf venation (it is stem xylem).
4. **Mander & Williams (2024)** — venation damage explicitly framed as percolation, real (fossil) leaf networks, reticulation-robustness conclusion. Missing: threshold, targeted attack, hydraulics, graph abstraction (pixels only), n = 9.
5. **Lu et al. (2025)** — embolism failure modelled on real leaf vein networks, connectivity implicated. Missing: percolation, threshold, flow solve.
6. **Loepfe et al. (2007)** — Monte Carlo over xylem network topology, connectivity ↔ safety/efficiency.
7. **Katifori et al. (2010)** — damage resilience as the origin of loops. Theory only.

### Attempts to break the hedged novelty claim — result
Claim under test: *"no prior study couples a Hagen-Poiseuille resistor network and a Kirchhoff solve to a percolation threshold on a real leaf-venation cohort, driven by a holoparasitic haustorial sink."*
Attacked clause by clause. **Every clause except one is individually broken:**

- *"Hagen-Poiseuille resistor network and a Kirchhoff solve … on a real leaf-venation cohort"* — **BROKEN.** Skjegstad & Kirkegaard (2025) do exactly this. Additionally the paper's own source dataset (Matos et al. 2024) computes an ℓ/r⁴ resistance column on these very leaves — which is why the solver validates to ~1e-7 against it. **This clause is broken by the paper's own data provenance.**
- *"percolation threshold on a real leaf-venation cohort"* — **BROKEN as framing, INTACT as a specific quantity.** Price & Weitz produced the curve on 339 real leaves; Mander & Williams explicitly named the approach percolation. Neither extracted a numerical p_c under a stated criterion.
- *"couples [hydraulics] to [percolation]"* — **BROKEN in plant vasculature generally, INTACT for leaf venation.** Mrad et al. (2021) already couple HP flow modelling and percolation theory in *Acer* stem xylem.
- *"driven by a holoparasitic haustorial sink"* — **NOT BROKEN.** Searched parasitic-plant × network modelling, *Cuscuta* × hydraulic model, haustorium × sink × host xylem flux, mistletoe/dodder × percolation, parasite × pre-symptomatic vascular collapse. The parasitic-plant literature that exists is developmental, anatomical, molecular, or ecological-network (mistletoe–host bipartite *species interaction* networks, not vascular ones). **No study models a haustorial sink as a boundary condition on a host vascular flow network.**

**Result: the claim survives only as a conjunction, and it is carried by a single clause.**

### Which clauses are load-bearing
- **"driven by a holoparasitic haustorial sink" — primary and effectively sole load-bearing clause.**
- **"on a real leaf-venation cohort" — secondary load-bearing.** Without it, Mrad breaks the claim outright.
- **"Hagen-Poiseuille resistor network and a Kirchhoff solve" — NOT load-bearing.** Broken by Skjegstad & Kirkegaard 2025 and by Matos 2024. Keep it as a *description of method*, never as a *novelty warrant*.
- **"percolation threshold" — weakly load-bearing.** Only the numerical threshold-with-criterion is new; the percolation framing is not.

### THE SEVERE PROBLEM THIS CREATES
The one clause holding the novelty claim up is the haustorial sink — and the paper's own verified results state that the calibrated sink diverts ~20% of flow yet embolises **zero** vessels at all 31 gradients from 0–3.0 MPa, and that hydraulic sink and structural percolation are **decoupled** lenses. **The novelty therefore rests entirely on a coupling the paper itself reports as absent.** As currently worded, "driven by" asserts a causal link the results contradict, and a referee who reads the results before the claim will find the central novelty statement inconsistent with its own findings. This is a wording-and-framing problem, not a results problem — the results are fine, and are arguably more interesting as a negative result.

### The defensible novelty gap statement
> Leaf-venation robustness to simulated damage has been quantified by random removal of vein segments on large cleared-leaf cohorts (Price & Weitz, 2014) and, in percolation terms, on fossil and extant venation networks (Mander & Williams, 2024), but neither extracted a percolation threshold, and neither analysis included targeted attack or a solved hydraulic layer. Conversely, Hagen–Poiseuille flow with a Kirchhoff solve has been implemented on real traced leaf venation networks (Skjegstad & Kirkegaard, 2025) without any damage or connectivity-failure analysis, while the coupling of percolation theory to solved xylem hydraulics exists only for stem conduit networks (Loepfe et al., 2007; Mrad et al., 2021). Mander and Williams explicitly identify fluid-flow modelling of damaged venation as the required next step and nominate the Mrad approach as the template. We take that step for leaf venation, add degree- and betweenness-targeted attack, and impose a calibrated holoparasitic haustorial sink as a boundary condition — a driver that, to our knowledge, has not previously been represented in any host vascular-network model.

Note this version (a) concedes Price & Weitz and Skjegstad up front, (b) uses Mander & Williams' own invitation as the warrant, (c) says "impose … as a boundary condition" rather than "driven by", (d) hedges the parasite clause with "to our knowledge".

### What must be framed cautiously or dropped
- **DROP "driven by a holoparasitic haustorial sink"** in its causal sense. Replace with "with a calibrated holoparasitic haustorial sink imposed as a boundary condition."
- **PROMOTE the decoupling to a finding.** "A sink strong enough to divert ~20% of leaf flow produces no embolism across 0–3.0 MPa; structural fragmentation and hydraulic sink stress are independent failure lenses in leaf venation" is a clean, honest, publishable negative result. It also *explains* the weak K_leaf validation rather than leaving it as an embarrassment.
- **DROP any claim that percolation framing of venation is new.** Mander & Williams used it explicitly; the quoted sentence is on record.
- **DROP any novelty claim for HP + Kirchhoff on leaf networks.** Skjegstad & Kirkegaard 2025 and Matos 2024 both preempt it.
- **REFRAME the mean-degree result** as a causally-controlled confirmation and sharpening of Price & Weitz's meshedness finding, noting the affine relation between meshedness and ⟨k⟩ in planar graphs.
- **CAUTION on the targeted-attack framing.** Brodribb et al. (2016) show real embolism is size-ordered. Use this to argue the targeted results are the biologically realistic case — but note it also means random-removal p_c = 0.200 is not the biologically relevant number.
- **CAUTION on cohort quality.** Price & Weitz used 339 whole cleared leaves; this paper uses 100 crop windows without petioles. State this and use it to justify the GCC criterion.
- **NEVER place Mander & Williams' ~0.75–0.95 "network remaining" values on the same axis as p_c.**

---

## WHAT I COULD NOT FIND
- **Corson (2010) PRL** — not retrieved in this pass (but full-text read in dossier A; see there for verified content).
- **Mrad et al. (2021) full text** — Wiley 403. Abstract-level plus Mander & Williams' verbatim description of Mrad's method. **No verbatim quotation from Mrad should be used, and its percolation-threshold values are unverified.** This is the most important remaining gap.
- **Brodribb et al. (2016) PNAS full text** — 403.
- **Price & Weitz's regression statistics for meshedness vs robustness** — in "Additional file 2: Table S2", not opened.
- **Any study modelling a parasitic plant's haustorium as a hydraulic boundary condition on a host vascular network.** Searched from four directions; found nothing. Genuine absence, but hedge with "to our knowledge."
- **Any 2024–2026 study computing a percolation threshold on real leaf venation graphs.** Nothing found. The nearest 2025 works each hold one half of the combination. **The gap appears open as of this search.**
