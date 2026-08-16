# Final Resolution Pass — Every Open Flag Closed

**Generated 2026-08-15.** Third and final pass, following `DEEP_RRL_EVIDENCE_PACK.md` (literature) and
`SECOND_PASS_AUDIT.md` (stress test). No manuscript prose was rewritten. Every number below is
produced by a script in this repository and is reproducible.

**New analyses run for this pass**

| Script | Output | Resolves |
|---|---|---|
| `scripts/run_criterion_and_locality.py` | `data/criterion_and_locality.{csv,json}` | §2 source-anchored connectivity · §3 localised contiguous-disc removal |
| `scripts/run_final_resolution_checks.py` | `data/final_resolution_checks.json` | §5 bootstrap · §6 K_leaf cohort · §7 betweenness vs flux · §8 high-GCC subcohort |
| `scripts/run_cavitation_sensitivity.py` (pass 2) | `data/cavitation_sensitivity.json` | §9 threshold-independent sink |

**Headline outcome of this pass.** Two of the three open questions resolved *in the paper's favour* and
one resolved *against a part of it*. The criterion choice barely matters (rank ρ = 0.91, n = 100, thresholds
shift by 0.011). Localised damage is **far less** damaging than dispersed damage, so random removal is
a conservative abstraction — but **connectivity ceases to predict tolerance under localised damage**,
which is a real scope limitation that must be stated. Everything else — CRN, bootstrap, K_leaf cohort,
betweenness interpretation, high-GCC subcohort — is now settled and documented.

---

# §2 — SOURCE-ANCHORED CONNECTIVITY

**Design.** The locked 100-leaf percolation cohort, identical engine settings to the archived run
(`n_densities = 40`, `trials_per_density = 60` → 2,400 trials/leaf, `rho_max = 0.6`, `mode = random`,
seed 1, collapse criterion "component < 0.5·N₀ at P = 0.50"). Source assignment is
`realleaf` `G.graph['root_rule']`, which fired as **`widest_vein` for 100/100 leaves** (no Matos leaf
carries a petiole flag; `node_Type` is 'E' throughout). **Both criteria are scored on the same removal
draws**, so the comparison is exactly paired. The source node is protected from removal, matching
Mander & Williams (2024), where the structural vein is a separate, un-attacked layer; protecting one
node of N ≥ 1,436 shifts the removed fraction by < 0.07%.

**Internal validation first.** Re-implemented GCC threshold vs the archived `pc_random`:
**Spearman = 0.9988**, median |difference| = **0.0011**, median **0.1998 vs 0.1998**. The
re-implementation reproduces the archived cohort exactly at the median; everything below is therefore a
like-for-like comparison, not a new pipeline.

| Metric | GCC | Source-anchored |
|---|---:|---:|
| n | **100** (the complete cohort) | 100 |
| median threshold | **0.1998** | **0.1837** |
| IQR | 0.1572 – 0.2207 | 0.1487 – 0.2041 |
| Spearman correlation between them | **0.9117** | (Pearson 0.9352) |
| median paired difference (source − GCC) | — | **−0.0105** |
| Wilcoxon (paired) | — | p = 3.9 × 10⁻¹⁸ |
| source lower in | — | **100 of 100 leaves** |
| conclusion changes? | — | **No** |

**Associations under each criterion (n = 100)**

| criterion | p_c ~ ⟨k⟩ | p_c ~ loop fraction | p_c ~ D |
|---|---|---|---|
| GCC | **+0.7367** (p = 2.4 × 10⁻¹⁸) | +0.7307 | +0.5008 (p = 1.1 × 10⁻⁷) |
| source-anchored | **+0.6541** (p = 1.6 × 10⁻¹³) | +0.6503 | +0.4651 (p = 1.1 × 10⁻⁶) |

*(The GCC row reproduces the archived cohort values of 0.733 / 0.727 / 0.496 to within 0.005 — a further
confirmation that the re-implementation is faithful.)*

### Answer

> **Does the choice of GCC versus source-anchored connectivity materially affect the interpretation?
> No.** The source-anchored threshold is systematically lower — by a median of 0.0106, in every one of
> 100 leaves — because requiring connection to one designated source is strictly stricter than counting
> the largest surviving component. But the two rank leaves almost identically (ρ = 0.91), and every
> substantive association survives: connectivity remains the leading predictor (ρ = 0.65 vs 0.74) and
> fractal dimension remains secondary (0.47 vs 0.50). No conclusion in the manuscript changes.

**Manuscript treatment.** Report the GCC threshold as primary (it is the one that is defined without
choosing a source, and the source here is a *rule*, not an anatomical petiole), and report the
source-anchored comparison as a one-paragraph robustness result citing Mander & Williams (2024) and
Price & Weitz (2014) as the precedents that use source anchoring. State the `widest_vein` rule
explicitly and note that no leaf in the deposit carries a petiole flag.

---

# §3 — LOCALISED CONTIGUOUS-DISC REMOVAL

**Design.** Same leaves, same engine, same collapse criterion, **matched realised removed fractions**
(the x-axis is the true fraction of nodes removed, identical to the random case, so the thresholds are
directly comparable). Two localised protocols, each replicate drawing its centres once and growing the
lesion across the sweep so the removed sets are nested — a growing patch, which is both the realistic
damage progression and the analogue of Mander & Williams' "varying the proportion removed":

- **disc1** — one lesion: remove the f·N non-source nodes nearest a random centre (Euclidean, on the
  leaf's own calibrated coordinates).
- **disc10** — ten lesions: round-robin from ten random centres until f·N nodes are removed (the closer
  analogue of Mander & Williams' many small circular blade holes).

60 replicates × 40 densities per protocol per leaf.

| Scenario | n | Median critical removed fraction | IQR | Effect vs random |
|---|---:|---:|---|---|
| Random (dispersed) | 100 | **0.1998** | 0.1572 – 0.2207 | — |
| **Localised, 1 disc** | 100 | **0.4951** | 0.4620 – 0.5069 | **+0.2910; 2.46× more tolerant** |
| **Localised, 10 discs** | 100 | **0.4511** | 0.4247 – 0.4687 | **+0.2512; 2.27× more tolerant** |

Wilcoxon paired, both protocols: p = 3.9 × 10⁻¹⁸. **A localised lesion was less damaging than dispersed
removal in 100 of 100 leaves for both protocols — zero exceptions.**

**Associations under localised damage (n = 100) — the finding that must be reported honestly**

| criterion | p_c ~ ⟨k⟩ | p_c ~ loop fraction | p_c ~ D |
|---|---|---|---|
| random (dispersed) | **+0.7367** (p = 2.4 × 10⁻¹⁸) | +0.7307 | +0.5008 |
| disc1 | **−0.0000 (p = 1.00, n.s.)** | +0.0074 (n.s.) | +0.1420 (p = 0.16, n.s.) |
| disc10 | **+0.1507 (p = 0.13, n.s.)** | +0.1508 (n.s.) | **+0.5234** (p = 2.3 × 10⁻⁸) |

### Answer

> **Does the conclusion depend on treating damage as spatially dispersed? Partly — and this must be
> stated as a scope condition, not buried.**
>
> Two things are true simultaneously. First, **random removal is a strongly conservative abstraction**:
> a contiguous lesion of the same size is 2.3–2.5× less likely to fragment the network, without
> exception across 100 leaves. The reported thresholds are therefore lower bounds on tolerance, and the
> "a haustorium is a local lesion, not a uniform sprinkle" objection is answered — in the paper's
> favour, and empirically in the paper's own data rather than by analogy to Shao et al. (2015) and
> Berezin et al. (2015).
>
> Second, and against the paper: **connectivity does not predict tolerance to localised damage.**
> Under a single lesion the ⟨k⟩–threshold association vanishes entirely (ρ = −0.0000, p = 1.00); under
> ten lesions it is weak and non-significant (ρ = 0.15). Only under dispersed damage does reticulation
> differentiate leaves (ρ = 0.73). Interestingly, fractal dimension *survives* under multi-lesion
> damage (ρ = 0.52, p = 2.3 × 10⁻⁸), which is mechanistically coherent: a compact hole is defeated by
> how the network fills space, not by how many alternative routes exist elsewhere.

**Mechanism.** A contiguous disc removes a spatially compact region and leaves the remainder intact and
connected — the network simply routes around the hole. Reticulation buys alternative routes *between*
regions, which is what dispersed removal destroys and what a single hole does not. This is precisely
the single-network result of Berezin et al. (2015): in one spatially embedded network a finite hole
does not propagate.

**Manuscript treatment (required).** Add this as a Results subsection and a Discussion paragraph.
The claim must become: *reticulation governs tolerance to **dispersed** vascular damage; under
spatially contiguous damage all leaves tolerate substantially more loss and connectivity ceases to
differentiate them.* Do not state the connectivity result without the dispersed-damage qualifier.

---

# §4 — COMMON RANDOM NUMBERS

**Resolved from the code, not inferred.**

1. **Were identical random seeds / realisations used? YES.**
   `scripts/run_cohort_suggested.py` line 34 constructs **one** `PercolationParams` object,
   `PP = config.PercolationParams(mode="random", n_densities=40, n_trials=10000)`, carrying the
   dataclass default `seed = 1`. Line 53's `measure()` calls `percolation.find_pc(G, PP, ...)`, and
   `percolation.density_response` begins with `rng = config.new_rng(p.seed)` — the generator is
   **re-created from the same seed on every call**. Both arms of every pair therefore consume an
   identical random stream.

2. **How were the simulations paired?** Within one loop iteration per leaf: `pc0 = measure(G)` on the
   observed graph, then `G2, nadd = add_loops(G, TARGET_K)` and `pc1 = measure(G2)`. `add_loops`
   (`scripts/make_real_suggested.py`) only ever calls `G2.add_edge(na, nb, ...)` between **existing**
   nodes — verified — so **the node set and node count are identical between arms**. Since removal is
   `rng.random(n) < rho` over an identically-sized node array from an identically-seeded generator,
   the two arms receive the **same removal mask on the same nodes in the same order**. This is exact
   common random numbers with perfect pairing, not merely a shared seed.

3. **Monte Carlo noise.** No CRN rerun is needed. Two independent lines confirm the effect clears the
   noise floor: (a) the paired design cancels the shared component of the error by construction;
   (b) if per-leaf p_c carried ±0.01 of *independent* noise against a true effect of ~0.0095, a
   substantial number of negative differences would appear by chance — **zero of 105 leaves worsened**,
   and zero of 103 in the high-GCC subcohort, and zero in every quality subset. That pattern is only
   consistent with low-noise paired estimation.

**Methods-ready statement:**

> "Paired simulations **used common random numbers**: baseline and reticulation-enhanced networks were
> evaluated with a single seeded `PercolationParams` instance (seed 1, 40 densities × 250 trials),
> and because loop addition modifies only the edge set the two arms share an identical node ordering
> and therefore an identical sequence of removal draws. Δp_c is consequently a within-leaf paired
> difference in which the Monte Carlo error is common to both arms."

*(Note for accuracy: `n_trials = 10000` over `n_densities = 40` gives 250 trials per density,
10,000 trials per network per arm.)*

---

# §5 — BOOTSTRAP

**Resolved from the code and measured empirically.**

| Quantity | Method | B | Resampling unit | Seed | Appropriate? |
|---|---|---:|---|---|---|
| p_c 95% CI (all reported intervals) | **Percentile** (not BCa) | **200** | individual (ρ, collapse-outcome) Monte Carlo **trials**, drawn with replacement | **7** | **Unit: yes. Replicate size: no — see below.** |

**The defect, measured not asserted.** `percolation.bootstrap_pc` sets `take = min(n, sample_cap)` with
`sample_cap = 50_000`. Whenever the run exceeds 50,000 trials each bootstrap replicate is *smaller than
the dataset*, which inflates the interval by approximately √(n / 50,000). Measured on the hero mesh at
100,000 trials:

| replicate size | 95% CI width |
|---|---|
| capped at 50,000 (shipped default) | **0.001684** |
| full size (100,000) | **0.001053** |
| **ratio** | **1.599** (√2 = 1.414 expected) |

**Every reported interval is therefore CONSERVATIVE (too wide)** — by ≈1.4–1.6× for the
100,000-trial targeted runs and ≈4.5× for the 1,000,000-trial random run. No interval is
anti-conservative, so no reported conclusion is affected.

**Recommendation.** Either (a) raise `sample_cap` to `n` and re-report the narrower intervals, or
(b) keep them and state in Methods that the intervals are conservative by a known factor. Option (a)
costs minutes and makes the CIs honest; option (b) is acceptable if compute is constrained.
The resampling unit is correct: trials are the unit of Monte Carlo uncertainty, which is exactly the
claim the interval makes. Percentile rather than BCa is defensible at these widths — at 10⁶ trials the
half-width is ~0.001 and the method choice is immaterial — but **name the method and B in Methods**,
which the manuscript currently does not.

---

# §6 — K_leaf COHORT DISCREPANCY — RESOLVED EXACTLY

**Cause, read out of the code.** `run_kleaf_validate.cohort_species()` reads `data/cohort.csv` and
keeps only `include == True` — i.e. the **locked 100-leaf percolation cohort** — then intersects with
species having a measured K_leaf. The second pass applied **no cohort screen** and used every traced
leaf. The screen is recorded in `data/cohort.json`:

```
min_edges >= 2000 · n_cycles >= 1 · cut_end_frac <= 0.05 ·
|mean_degree_shift| <= 0.05 · quality flags do NOT gate inclusion
```
100 of 120 leaves pass; the 20 exclusions are almost all small windows (E < 2,000), and **15 of the 20
are grade A** — the screen is a resolvability screen, not a quality screen.

| Cohort | n | Inclusion rule | ρ | p | 95% CI | Recommendation |
|---|---:|---|---:|---:|---|---|
| **Manuscript** | **93** | percolation cohort (`cohort.csv include == True`) ∩ measured K_leaf | **0.1871** | **0.0726** | **[−0.024, +0.382]** | **Use this** |
| All leaves | 112 | no cohort screen ∩ measured K_leaf | 0.1764 | 0.0628 | [−0.015, +0.355] | report alongside |

The manuscript's n = 93, ρ = 0.187, p = 0.073 is **reproduced exactly**. The 19 additional leaves change
nothing: both are weak, both are non-significant, both intervals span zero, and the ℓ/r² convention
gives the same answer again (ρ = 0.179, p = 0.059 at n = 112).

**Exact Methods wording:**

> "Modelled xylem conductance was compared with measured maximum leaf hydraulic conductance for the
> 93 species in the percolation cohort for which a measured value was available (Spearman ρ = 0.187,
> p = 0.073, 95% CI [−0.024, 0.382]). The cohort screen is a network-resolvability screen (≥ 2,000
> edges, ≥ 1 independent cycle, crop-edge fraction ≤ 0.05, |mean-degree shift| ≤ 0.05) and does not
> condition on any outcome; relaxing it to all 112 traced leaves with a measured value gives
> ρ = 0.176, p = 0.063. The check is underpowered rather than negative, and it is unchanged by the
> choice of resistance convention (ℓ/r² : ρ = 0.179, p = 0.059)."

---

# §7 — BETWEENNESS vs HYDRAULIC FLUX

**Design.** Unweighted node betweenness — exactly the vector `percolation.importance_weights` builds —
rank-correlated against node hydraulic throughput (½ Σ |Q| over incident edges) from the baseline
Kirchhoff solve, over free (non-Dirichlet) nodes.

| Network | N | ρ(betweenness, flux) | ρ(degree, flux) |
|---|---:|---:|---:|
| Synthetic hero mesh (`config.DEFAULT_NETWORK`) | 1,023 | **+0.5107** | +0.1780 |
| Real leaf `Tri_lan` | 1,436 | +0.1840 | +0.0776 |
| Real leaf `Tod_bar` | 2,129 | **+0.6292** | +0.3417 |
| Real leaf `Tas_lan` | 2,192 | **+0.4953** | +0.2545 |

### Interpretation

Betweenness is a **moderate** proxy for hydraulic throughput — ρ = 0.18 to 0.63, consistently **2–3×
stronger than degree** on the same networks — but it is nowhere near equivalent. Betweenness-weighted
removal therefore has a *partial* hydraulic reading (it preferentially removes higher-flux junctions
more often than a degree rule would) while remaining primarily a topological stress test.

**Allowed manuscript wording:**

> "Node betweenness is a moderate rank proxy for solved hydraulic throughput in these networks
> (Spearman 0.18–0.63 across the reference mesh and three leaves), roughly two- to threefold stronger
> than degree, so betweenness-weighted removal preferentially disables higher-flux junctions. It is
> not equivalent to a flux ranking and is reported as a structural stress-test scenario, not as a
> model of any biological process."

**Forbidden:** "betweenness measures hydraulic load", "the betweenness scenario removes the highest-flux
vessels", any claim of equivalence.

---

# §8 — HIGH-GCC SUBCOHORT (baseline `gcc_fraction` > 0.99)

Dropping the leaves that are already fragmented before any removal (1 leaf from the percolation cohort,
2 from the enhancement cohort — the extreme case has 4,477 baseline components):

| Association | all 100 | high-GCC (n = 99) |
|---|---|---|
| p_c ~ ⟨k⟩ | +0.7328 | **+0.7313** |
| p_c ~ D | +0.4960 | **+0.5064** |
| p_c ~ D given log N | +0.6327 | **+0.6255** |

| Enhancement | all 105 | high-GCC (n = 103) |
|---|---|---|
| median Δp_c | 0.00950 | **0.00940** |
| improved / unchanged / worsened | 93 / 12 / 0 | **91 / 12 / 0** |
| sign test | p = 2.0 × 10⁻²⁸ | **p = 8.1 × 10⁻²⁸** |

**Nothing changes.** Baseline fragmentation is not a confound. Report one sentence and move on.

---

# §9 — FINAL THRESHOLD-INDEPENDENT SINK ANALYSIS

All from `data/cavitation_sensitivity.json`. Calibrated K_h = 0.0392 (20.0% diversion at the
illustrative 1.5 MPa gradient), 10-node contact patch, hero mesh N = 1,023.

**1. Patch water-potential depression.** ΔΨ at the haustorial patch = **−0.402 MPa** at the
illustrative gradient. ΔΨ at the network's global minimum = **−0.0262 MPa**.

**2. Threshold-independent gradient relationship.** The patch depression is **exactly linear** in the
host→parasite gradient: slope **−0.2682 MPa per MPa**, intercept ≈ 0, maximum residual 0.017 MPa across
0–12 MPa. This is a consequence of the parameterisation, not of leaf architecture: K_h is applied
*relative* to each node's own incident conductance, so the reservoir's weight in a tapped node's
potential is fixed at K_h/(1+K_h) = 0.0377 per node, independent of the network.

**3. Gradient required to reach each threshold** (onset of the first embolised vessel):

| threshold | required gradient | required K_h multiple at 1.5 MPa |
|---|---:|---:|
| −1.00 MPa | **1.1 MPa** | 1× (already exceeded at the calibrated strength) |
| −1.50 MPa | 4.0 MPa | 8× |
| −2.00 MPa (manuscript) | **6.0 MPa** (6.26 predicted) | none up to 256× |
| −3.00 MPa | 9.5 MPa | none |

**4. Comparison with measured physiology.** The largest *measured* parasite–host leaf water-potential
gradient located in two literature passes is **≈0.5 MPa** (Griebel et al. 2022, mistletoe/*Eucalyptus*,
which depressed host trunk Ψ by 0.60 MPa and raised modelled PLC by 11 points without hydraulic
failure). No primary holoparasite gradient measurement exists at all (Balios et al. 2025, explicit).
The 6.0 MPa required here is therefore **~12× the largest measured value** and 4× the illustrative one.

**5. Healthy / no-parasite baseline.** Minimum interior Ψ with no parasite = **−0.9963 MPa**, set by the
terminal Dirichlet condition `PSI_LEAF = −1.0`. Zero vessels embolise at every threshold from −1.00 to
−3.00 MPa. At a realistic midday operating potential of `PSI_LEAF = −2.5`, **91 vessels embolise with
no parasite at all**.

**6. Parasite contribution as a fraction of the modelled margin.**

```
reported margin      = 2.000 - 1.022  = 0.978 MPa
stipulated component = 2.000 - 1.000  = 1.000 MPa   (PSI_LEAF - PSI_CAVITATION)
parasite component   = -1.0224 - (-0.9963) = -0.026 MPa
parasite share                              =  2.6 %
```

### Placement decision

**Keep the sink in the main Results, as a clearly-labelled independent hydraulic subsection, and move
the threshold sweep to the Supplement.** Reasons: (a) the haustorial boundary condition is the *only*
clause of the novelty claim that survives (Part IV of the second pass), so removing it removes the
paper's parasite contribution entirely; (b) the decoupling is a genuine, quantified, derivable negative
result and is more interesting than the original positive framing; (c) it is what licenses the honest
statement that harm is resource drain rather than rupture.

**Report it as:** ΔΨ (threshold-independent), the linear depression law, the 6.0 MPa requirement
against a ≈0.5 MPa measured maximum, and the no-parasite baseline beside every sink number. **Never**
as "0 vessels embolised", which is true only at −1.1 MPa and below and only inside the truncated
0–3 MPa sweep.

---

# §10 — TITLE DECISION

**Selected title:**

> ## Vein Reticulation as a Structural Basis for Damage Tolerance in Leaf Venation Networks: Fragmentation Thresholds across 100 Species under Simulated Vascular Damage and a Calibrated Holoparasitic Sink

Every clause is audited: *"Vein Reticulation"* — measured and manipulated **[A]**; *"Structural Basis
for Damage Tolerance"* — the strongest formulation the evidence permits, and it survives the localised-
damage finding because it does not assert universality **[A/C]**; *"Fragmentation Thresholds"* — exactly
what p_c is, with no hydraulic implication **[A]**; *"across 100 Species"* — the cohort **[A]**;
*"Simulated Vascular Damage"* — neutral as to agent and geometry **[A]**; *"a Calibrated Holoparasitic
Sink"* — present as a component, not a driver **[A]**.

**Shorter fallbacks, if a venue caps title length:**

1. **Vein Reticulation Governs Fragmentation Thresholds of Leaf Venation Networks under Simulated
   Vascular Damage** — drops the parasite; safest, and accurate.
2. **Connectivity, Not Spatial Complexity, Governs Damage Tolerance in Leaf Venation Networks** — leads
   with the causally-controlled result; note it must then be qualified to *dispersed* damage in the
   abstract.

**Rejected:** every variant containing "pre-symptomatic", "hydraulic collapse", "host resistance"
unqualified, "driven by", or "attack/targeting".

---

# §11 — PRE-SYMPTOMATIC SECTION: FINAL DECISION

## **A — CUT.**

Remove the modelled pre-symptomatic time-window section from Results and from the Conclusion.

**Grounds.** It is computed in arbitrary time units from the **synthetic** p_c = 0.271 and f_c = 0.524
(not the empirical median 0.200), with stipulated growth rates, and is calibrated to no measured
infestation time-course. The model contains no symptom variable of any kind. And in the mild-stress
regime the term denotes, the modelled mechanism is the one that is *not* operating: Scoffoni et al.
(2017) show outside-xylem vulnerability explains 86–100% of K_leaf decline at turgor loss with **no**
minor-vein conduits embolised, and Avila et al. (2022) show connectivity-mediated spread engages only
once a majority of conduits are already gas-filled.

No defensible biological time mapping can be established from this study, so option B does not apply.

**What to keep.** One Introduction paragraph, on literature only, establishing that a pre-symptomatic
window under parasitism is empirically real with lead times from ~20 days to three decades
(Shen et al. 2007 ~50 d; Cochavi et al. 2017 ~20 d; Ortiz-Bustos et al. 2017; González de Andrés et al.
2024) — and stating plainly that its documented signature is optical, thermal, growth- and carbon-based,
**not hydraulic**. That motivates the study without claiming the study measures it.

**Delete "early warning" entirely** — no source located in three passes supports it.

---

# §12 — FINAL TERMINOLOGY

| Avoid | Use |
|---|---|
| p_c as an unqualified threshold | **critical removed fraction (f₅₀)**, defined inline as "the removed-node fraction at which the largest component falls below half its undamaged size with probability 0.50" |
| hydraulic collapse | **network fragmentation** / structural collapse |
| host resistance (bare) | **structural tolerance** / structural basis for resistance / candidate resistance trait |
| pre-symptomatic | **sub-critical** / pre-fragmentation / modelled sub-threshold |
| attack, targeted attack | **degree-weighted removal**, **betweenness-weighted removal**, **dispersed** vs **localised** removal |
| validated (of the resistance-column check) | **verified** |
| conductance | **modelled conductance** |
| driven by a haustorial sink | **with a haustorial sink imposed as a hydraulic boundary condition** |
| the parasite targets high-centrality nodes | a stress-test scenario using centrality-weighted removal |
| reticulation improves robustness | reticulation raises tolerance **to dispersed damage** |
| 0 vessels embolise | the sink does not approach the modelled cavitation threshold; onset requires a 6.0 MPa gradient |

---

# §13 — FINAL CLAIM AUDIT

**A** directly demonstrated · **B** directly supported by literature · **C** supported inference ·
**D** plausible/speculative · **E** unsupported

| # | Claim | Class | Note |
|---|---|:--:|---|
| 1 | Leaf venation networks have measurable structural fragmentation thresholds | **A** | median f₅₀ = 0.200; reproduced independently this pass at ρ = 0.9987 against the archive (n = 100) |
| 2 | Degree-weighted removal lowers tolerance relative to random | **A** | 0.200 → 0.169, 100/100 leaves, r_rb = 1.00 |
| 3 | Betweenness-weighted removal lowers tolerance relative to random | **A**, axis caveat | synthetic reference only; 0.1889 is a *nominal* removal intensity, 0.1498 realised |
| 4 | Connectivity is the dominant architectural predictor | **A**, scope-limited | ρ = 0.733 (0.745 size-controlled, 0.789 excluding over-segmented leaves); **holds for dispersed damage only** (§3) |
| 5 | D has an independent, secondary relationship after size control | **A** | raw 0.496 → 0.633 partial on log N; in-range grid partial 0.451; and D is the *only* predictor surviving multi-lesion damage (0.523) |
| 6 | Reticulation enhancement increases structural tolerance | **A** | 0.201 → 0.215; 93/105 improved, 0 worsened; Pratt p = 1.7 × 10⁻¹⁸; CRN-paired (§4) |
| 7 | The enhancement survives quality subsetting | **A** | 6 subsets, zero reversals in any; no-C median gain *rises* to 0.0108 |
| 8 | The sink produces meaningful physiological embolism | **E** | ΔΨ = −0.026 MPa; onset needs 6.0 MPa vs ≈0.5 MPa measured maximum |
| 9 | The sink is coupled to p_c | **E** | no collapse at any haustorial density at calibrated K_h; percolation never reads a potential |
| 10 | A pre-symptomatic physiological window is demonstrated | **E** (as a model result); **B** (as literature) | cut from Results; retain the literature framing in the Introduction |
| 11 | The hydraulic implementation is independently validated | **E** | it is **verified** — the source column is ℓ/r⁴ by definition |
| 12 | Modelled conductance relates to measured K_leaf | **C**, weak | ρ = 0.187, p = 0.073, CI [−0.024, 0.382]; underpowered, convention-independent |
| 13 | Vein reticulation is a host-resistance trait | **C** | permitted only as "structural basis for" / "candidate"; resistance is never measured |
| 14 | The study is the first of its claimed kind | **E** as previously worded; **C** for the haustorial-boundary-condition clause alone | see §14 and the second pass's Part IV gap statement |
| 15 | Localised damage is less damaging than dispersed damage | **A** (new) | 2.46× (1 disc) and 2.27× (10 discs); 100/100 leaves, zero exceptions |
| 16 | The criterion choice (GCC vs source-anchored) does not change conclusions | **A** (new) | ρ = 0.912 between criteria; every association preserved |

---

# §14 — WHAT ACTUALLY CHANGED

| Issue | Old interpretation | Correct interpretation | Manuscript consequence |
|---|---|---|---|
| p_c | hydraulic collapse threshold | topological fragmentation threshold; the engine never reads a conductance | Title, Abstract, Results, Discussion |
| loop fraction vs ⟨k⟩ | graph identity | **empirical** collinearity (ρ = 0.994); the identity holds for cycle rank, not the non-bridge fraction | Methods, Results (report ⟨k⟩ as the single axis) |
| targeted modes | rank-ordered attacks | stochastic **weighted removal** (Callaway-style degree-dependent occupation) | Methods, Results |
| betweenness threshold | 0.1889 removal fraction | 0.1889 **nominal**; **0.1498 realised** | Results Table 2 |
| sink | driver of collapse | independent hydraulic boundary condition, decoupled; ΔΨ = −0.026 MPa | Results, Discussion, Conclusion |
| "0 vessels embolise" | robust null | threshold-dependent (inverts at −1.0 MPa) and derivable from the K_h/(1+K_h) clamp | Results Table 3, Supplement |
| pre-symptomatic window | demonstrated prediction | unsupported temporal mapping; no symptom variable exists | **cut** from Results/Conclusion |
| validation | validated | **verified** (shared ℓ/r⁴ convention) | Methods, Results |
| Grade-A artefact story | artefacts overstate headroom | **artefact narrative unsupported** — raw grade difference n.s. (Kruskal p = 0.0725) | delete the sentence |
| Grade C | possible contaminant | **exclusion strengthens** the result (0.733 → 0.789) | sensitivity block |
| D | possibly size-only | size-confounded (73%) **but still informative** (partial 0.633) and the only survivor under multi-lesion damage | Results, Discussion, Limitations |
| K_leaf n | 93 vs 112 unexplained | **resolved**: 93 = percolation-cohort screen ∩ measured; both give the same answer | Methods |
| Criterion (GCC vs source) | untested | **tested**: ρ = 0.912, median shift −0.011, no conclusion changes | Results robustness paragraph |
| Localised damage | untested | **tested**: 2.3–2.5× *less* damaging, 100/100 leaves — but connectivity stops predicting | Results + Limitations (**new, required**) |
| CRN | unknown | **confirmed exact** — same seed, identical node set, identical draws | Methods |
| Bootstrap | unspecified | percentile, B = 200, seed 7, trials as the unit, capped at 50k → intervals **conservative** by ~1.6× | Methods |
| Betweenness meaning | unclear | **moderate** flux proxy (ρ 0.18–0.63), 2–3× stronger than degree, not equivalent | Methods, Discussion |

---

# §15 — FINAL WRITING HANDOFF

## A. Final title
**Vein Reticulation as a Structural Basis for Damage Tolerance in Leaf Venation Networks: Fragmentation
Thresholds across 100 Species under Simulated Vascular Damage and a Calibrated Holoparasitic Sink**

## B. Final central claim
Reticulate connectivity is the dominant architectural determinant of how much dispersed vascular
element loss a leaf venation network can absorb before it fragments, and raising reticulation within a
leaf's own observed range raises that tolerance in essentially every leaf tested.

## C. Final research question
Does venation connectivity determine the fraction of vascular elements a leaf's network can lose before
losing global connectivity — and can that tolerance be shifted by adding reticulation?

## D. Final hypothesis / expectation
More reticulate networks fragment only after a larger fraction of junctions is lost, and the effect is
attributable to connectivity rather than to the spatial complexity it covaries with.

## E. Strongest 5–8 results

1. **Reticulation enhancement.** ⟨k⟩ → cohort P90 = 2.811 raises median f₅₀ from **0.201 to 0.215**;
   **93 of 105 improved, 12 unchanged, 0 worsened**; Wilcoxon (Pratt) **p = 1.7 × 10⁻¹⁸**;
   rank-biserial ≈ 1.00. Common-random-number paired (§4).
2. **Causal decoupling, inside the empirical range.** On the 24 synthetic grid cells with
   ⟨k⟩ ≤ 2.99: partial r(f₅₀, ⟨k⟩ | D) = **0.970** vs r(f₅₀, D | ⟨k⟩) = **0.451**; standardised
   β = 0.981 vs 0.125 (**7.8 : 1**); R² = **0.940**.
3. **Connectivity predicts tolerance across the real cohort.** Spearman **0.733** raw, **0.745**
   controlling log N, **0.789** excluding all over-segmented tracings. R² = 0.507 for the two-predictor
   model (F(2,97) = 49.93).
4. **Dispersed structurally-biased loss is more damaging than uniform loss in 100 of 100 leaves.**
   Median f₅₀ 0.200 → 0.169 (15.7%), median paired difference 0.0305, **r_rb = 1.00**.
5. **Localised damage is 2.3–2.5× less damaging than dispersed damage, in 100 of 100 leaves**
   (disc1 0.495 vs random 0.200; disc10 0.451). Random removal is a conservative abstraction —
   but connectivity ceases to predict tolerance under localised damage. **[NEW]**
6. **The criterion choice does not matter.** Source-anchored vs GCC: ρ = **0.912**, median paired
   difference −0.011 (n = 100), every association preserved. **[NEW]**
7. **Reticulation narrows differential exposure.** Loop fraction × (random − targeted) gap = **−0.786**
   (−0.789 size-controlled); the gap is size-clean (ρ with N = +0.046, n.s.).
8. **The calibrated haustorial sink is decoupled from the structural threshold.** ΔΨ at the patch
   = −0.402 MPa (−0.268 MPa per MPa of gradient, exactly linear); reaching the modelled cavitation
   threshold requires **6.0 MPa** against a largest measured value of ≈0.5 MPa; the parasite
   contributes **2.6%** of the reported margin.

## F. Strongest robustness checks

- **Independent re-implementation** of the percolation engine reproduces the archived cohort at
  Spearman **0.9988**, median |difference| **0.0011** (n = 100).
- **Zero reversals in every quality subset** (full, no-C, no-D, no-C-and-no-D, grade-A, boundary-pass).
- **Grade-C exclusion strengthens** the connectivity result (0.733 → 0.789) and raises the enhancement
  gain (0.0095 → 0.0108).
- **All associations strengthen under size control**; D 0.496 → 0.633.
- **High-GCC subcohort (n = 99/103) changes nothing** (0.7313 vs 0.7328; 91/12/0).
- **Resistance convention is immaterial**: ℓ/r⁴ ρ = 0.176 vs ℓ/r² ρ = 0.179 (n = 112).
- **Restricted synthetic grid fits better** than the extrapolated one (R² 0.940 vs 0.887).
- **Grade artefact hypothesis unsupported**: raw Kruskal p = 0.0725.

## G. Main biological interpretation

Leaf venation networks are sparse, planar and near-tree-like (median ⟨k⟩ 2.520, degree SD 0.848,
maximum degree 4–5), yet three-quarters of their edges lie on cycles. That reticulation is what
determines how much dispersed loss the network absorbs before its transport skeleton fragments:
connectivity predicts the threshold observationally, carries the effect when experimentally decoupled
from spatial complexity, and raises the threshold when added to real leaves — in essentially every leaf,
and never lowering it. The effect is strongly diminishing (gain versus baseline ⟨k⟩, ρ = −0.821), which
is why real leaves sitting near their own reticulation ceiling have little left to gain, and it is
bounded by trade-offs the model does not represent. Crucially, this tolerance is specific to *dispersed*
damage: a spatially contiguous lesion of the same size is 2.3–2.5× less likely to fragment the network,
and under such damage connectivity ceases to differentiate leaves at all. The parasitic sink that
motivates the analysis proves to act on a different axis entirely — it withdraws a fifth of leaf flow
while depressing the tissue's water potential by hundredths of a megapascal, so within this model
haustorial harm is a resource drain rather than a rupture, and structural fragmentation and hydraulic
sink stress are independent lenses on the same network.

## H. Main limitations, ranked

1. **Topology, not physiology.** f₅₀ is computed on an unweighted adjacency matrix; no hydraulic
   quantity enters it. It cannot be converted to PLC, P50 or Ψ.
2. **Connectivity predicts tolerance to dispersed damage only** (§3). Under localised lesions the
   association vanishes.
3. **The parasite abstraction has no anatomical warrant for node deletion** — haustorial connection is
   topologically *additive* (Kaga et al. 2020); site removal represents loss of conducting function
   from any cause.
4. **The only independent physical test is underpowered** (K_leaf ρ = 0.187, CI [−0.024, 0.382]) and
   the model is xylem-only, while outside-xylem pathways carry 26–39% of static leaf resistance and
   86–100% of its dynamic decline.
5. **Crop windows without petioles.** 100 of 120 networks; the source is a `widest_vein` rule, not an
   anatomical petiole, and embolism is empirically observed to initiate in the petiole/midrib the
   windows exclude.
6. **The sink null is threshold-dependent and derivable** from the relative-K_h parameterisation, not
   an emergent property of venation.
7. **No cost term** in the enhancement; "0 worsened" reflects single-objective optimisation.
8. **D is 73% explained by log network size**, though it survives the control.
9. **No phylogenetic correction**; species treated as independent across ferns and angiosperms.
10. **Quality grades are non-ordinal defect types**, and the archive keeps only the leading flag
    (hiding 4 over-segmented and 28 damaged leaves).

## I. Terminology to use
f₅₀ / critical removed fraction · network fragmentation · structural tolerance · structural basis for
resistance · dispersed vs localised removal · degree-weighted / betweenness-weighted removal · modelled
conductance · verified · imposed as a hydraulic boundary condition · sub-critical · nominal vs realised
removed fraction · reticulation (as ⟨k⟩, the single connectivity axis).

## J. Terminology to avoid
pre-symptomatic · hydraulic collapse · early warning · attack / targeted attack · validated (for the
resistance-column check) · driven by · host resistance (bare) · "0 vessels embolise" · "first
percolation analysis of leaf venation" · "mean degree and loop fraction are independent predictors" ·
"A > B > C > D quality gradient" · any β / universality-class / phase-transition claim.

## K. Required manuscript changes

- **Title** — replace with §10.
- **SOP** — SOP 2 must say *simulated vascular element loss*, not "haustorial attack"; SOP 4 should
  state the dispersed-damage scope. SOP 1 and 3 stand.
- **Abstract** — remove hydraulic-collapse and pre-symptomatic framing; add the localised-damage scope
  condition; state the sink as decoupled.
- **Introduction** — lead with the biological question, not percolation; concede Price & Weitz (2014)
  and Mander & Williams (2024) in the paper's own voice; keep one literature-only pre-symptomatic
  paragraph; use the second pass's Part IV gap statement verbatim.
- **RRL** — reposition Mrad et al. (2021) as **support**, not contrast; add Skjegstad & Kirkegaard
  (2025); add the localised-attack literature (Shao 2015; Berezin 2015) now that it is confirmed
  empirically here.
- **Methods** — rename p_c → f₅₀ with the criterion inline; describe the removal modes as *weighted
  stochastic removal* and distinguish nominal from realised fractions; state the CRN sentence (§4);
  name the bootstrap method, B and seed (§5); state the K_leaf cohort rule (§6); state the
  `widest_vein` source rule; describe the sink as a boundary condition and state the relative-K_h
  convention; state the six-tier non-ordinal grade scale and that flag *presence* is used.
- **Results** — Table 2: relabel the betweenness threshold (nominal 0.1889 / realised 0.1498);
  Table 3: replace with the threshold-independent sink numbers and the no-parasite baseline;
  Table 4: report the size-controlled D; Table 6: delete the artefact sentence and add the subset
  table; **add two new subsections** — criterion robustness (§2) and localised damage (§3); add the
  three effect sizes; relabel verification.
- **Discussion** — restructure to the 14-paragraph blueprint in `SECOND_PASS_AUDIT.md` Part XI, with
  two additions: a localised-damage paragraph (scope condition) and a criterion-robustness sentence.
- **Conclusion** — remove the pre-symptomatic sentence; state the dispersed-damage scope; state the
  decoupling as a finding.
- **References** — fix the two Matos papers (*Ecology* 105:e4436 for data; *New Phytol* 244:407 for the
  analysis), Ronellenfitsch & Katifori PRL **123:248101**, Sack et al. **PNAS 105:1567–1572**, Mrad et
  al. 2021 author list, Xu et al. **2020**, add the Albert et al. erratum (*Nature* 409:542).

## L. Analyses still unresolved

**None.** Every item flagged by the first and second passes has been run, resolved, or given a stated
manuscript treatment. Three optional improvements remain, none blocking:

1. **Raise `sample_cap` to `n` and re-report the CIs** — they are currently conservative by ~1.6×
   (100k runs) and ~4.5× (1M run). Minutes of compute; strictly improves the paper.
2. **Compute ε² for the non-significant grade comparison** — only if a reviewer asks for an effect size
   on a null.
3. **Pagel's λ on the regression residuals** — per Revell (2010) a λ ≈ 0 result would *justify* the OLS
   already reported rather than force a refit. ~1 hour.

**One judgement call is deliberately left to the authors** and is flagged rather than decided: whether
to lead the paper on the structural result (safest, and what the evidence best supports) or on the
sink decoupling (more novel, but a negative result). §10's selected title accommodates either.
