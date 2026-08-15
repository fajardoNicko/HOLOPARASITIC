# Second-Pass Scientific Stress Test & Paper Repair

**Generated 2026-08-15.** Second pass, following `DEEP_RRL_EVIDENCE_PACK.md` and `rrl/A…J`.
No manuscript prose was rewritten (Rule 1). Every conclusion below is traceable to the dataset, to a
reproducible script, or to a named source.

**New reproducible analyses written for this pass**

| Script | Output | Answers |
|---|---|---|
| `scripts/run_cavitation_sensitivity.py` | `data/cavitation_sensitivity.json` | P0-1 threshold sensitivity, baseline control, margin decomposition |
| `scripts/run_graph_metric_audit.py` | `data/graph_metric_audit.json` | ⟨k⟩/loop-fraction dependence; targeted-attack axis |
| `scripts/run_second_pass_audit.py` | `data/second_pass_audit.json` | grade structure, C-contamination, D-vs-size, enhancement robustness, size controls |
| `scripts/run_resistance_convention_sensitivity.py` | `data/resistance_convention_sensitivity.{csv,json}` | ℓ/r⁴ vs ℓ/r² (P1 item 8) |
| `scripts/run_rrl_diagnostics.py` (first pass) | `data/rrl_diagnostics.json` | size confound, effect sizes, collinearity |

**Evidence grading used throughout:** **[DEM]** directly demonstrated by this study · **[LIT]** directly
supported by literature · **[INF]** supported inference · **[MOD]** model assumption/abstraction ·
**[SPEC]** speculative.

---

# PART I — SCIENTIFIC RISK ASSESSMENT

## CRITICAL

**C1. The title's causal chain is not what the model computes.**
The percolation engine is **purely topological**. `percolation.py` operates on the unweighted CSR
adjacency (`network.to_csr`) and on unweighted degree/betweenness; conductance, radius, water
potential and the cavitation threshold never enter any p_c calculation. The hydraulic solver is a
*separate* module invoked only in the unused `hydraulic` mode, in the sink demonstration, and in the
K_leaf check. **[DEM]** Therefore "hydraulic collapse under parasite-induced water stress" describes
nothing the headline result measures. This is not a framing preference; it is a structural fact about
the code.
*This cuts both ways and the paper should exploit the upside:* because p_c is independent of the
conductance model, **every radius-inference, Murray's-law, pit-resistance and ℓ/r⁴-vs-ℓ/r² objection
is irrelevant to the percolation results.** The first pass listed radius inference as the "deepest
vulnerability"; it is not — it cannot touch p_c.

**C2. The "0 vessels embolise" result is threshold-dependent and it inverts at −1.0 MPa.**
At the calibrated sink and the illustrative 1.5 MPa gradient, embolised counts are **1** at a −1.00 MPa
threshold and **0** at −1.10 MPa and below. Cavitation onset gradient rises monotonically with the
threshold: −1.00 → 1.1 MPa, −1.10 → 2.1, −1.25 → 2.7, −1.50 → 4.0, −1.75 → 5.0, **−2.00 → 6.0**,
−2.50 → 8.0, −3.00 → 9.5 MPa. **[DEM]** The manuscript's sweep stops at 3.0 MPa, which is below the
onset for every threshold at or beyond −1.5 MPa — so "0 embolised at all 31 gradients" is a statement
about where the sweep was truncated as much as about the physics.

**C3. The margin to cavitation is 97.4% stipulated.**
Baseline (no parasite) minimum interior potential = **−0.9963 MPa**, set by the terminal Dirichlet
condition `PSI_LEAF = −1.0`. With the calibrated sink at 1.5 MPa it is **−1.0224 MPa**. The parasite
therefore contributes **ΔΨ = −0.0262 MPa** of the reported ~0.98 MPa margin; the remaining 0.974 MPa
is the stipulated gap `PSI_LEAF − PSI_CAVITATION`. **[DEM]** Reporting "minimum host water potential
−1.02 MPa against a −2.0 MPa threshold" therefore reports the boundary conditions, not the parasite.

**C4. The absence of embolism is derivable from the sink parameterisation, not from leaf architecture.**
`K_h` is applied *relative* to each node's own incident conductance (`hydraulics.solve(relative=True)`),
so the parasite reservoir's weight in the tapped node's potential is fixed at `K_h/(1+K_h)` = **0.0377**
per node, independent of the network. Measured across the patch, the depression is **exactly linear**
in the gradient: slope **−0.2682 MPa per MPa**, intercept ≈ 0, maximum residual 0.017 MPa over 0–12 MPa.
Reaching −2.0 MPa requires a **6.26 MPa** host→parasite gradient. **[DEM]** The null is arithmetic.
The paper must not present it as evidence that venation architecture resists haustorial sinks.

**C5. The novelty claim's only surviving clause contradicts the paper's own result.** (Carried forward
from the first pass, unchanged and still unresolved.) Every clause except "driven by a holoparasitic
haustorial sink" is independently broken; that clause asserts a causal link the decoupling result
denies. See Part IV.

## MAJOR

**M1. The reported betweenness threshold is quoted on a different axis from the random threshold.**
`_trial_weighted` removes node *i* with probability `clip(rho·w_i, 0, 1)`. Betweenness weights on the
hero mesh have Gini 0.754 and maximum 29.4, so the clip binds early: nominal ρ = 0.2023 realises a
**0.1578** expected removed fraction, and the reported betweenness threshold of **0.1889 nominal
corresponds to 0.1498 realised** — a 21% overstatement. **[DEM]** Degree weights (6 distinct values,
maximum 2.4) do not clip in the relevant range, so `pc_degree` is unaffected. The qualitative ordering
survives and in fact strengthens; the *number* 0.1889 is not comparable to 0.271.

**M2. The targeted modes are not rank-ordered attacks, and the first pass mis-analysed them.**
They are **weighted stochastic removal** with removal probability proportional to centrality — exactly
Callaway et al. (2000)'s degree-dependent occupation formalism, not Albert et al. (2000) / Holme et al.
(2002) rank-ordered deletion. **[DEM]** Consequences: (i) the entire "initial vs recalculated
centrality" concern in `rrl/D` **does not apply**; (ii) the "degree ranking is mostly ties" mechanism
in `rrl/D` **does not apply** either (ties are irrelevant under probabilistic removal — though the
degree weight vector does take only 6 distinct values, which limits how much targeting information
exists); (iii) the correct primary citation changes.

**M3. `loop_fraction ≈ 1 − 2/⟨k⟩` is NOT a graph identity under the definition actually used.**
`characterize.py` computes `loop_fraction = (E − |bridges|)/E`, the **non-bridge edge fraction**. The
identity `1 − 2/⟨k⟩ + c/E` describes the **cycle-rank fraction** `(E − N + c)/E`, which the archive
also stores as `n_cycles`. Verified on all 120 leaves: cycle-rank fraction matches the identity to
**1.4 × 10⁻¹⁶** (floating point), while non-bridge loop fraction differs from it by a mean of **0.564**
and is **3.63×** larger on average. **[DEM]** The first pass's §0.3 claim was wrong and must not be
written into the manuscript.

**M4. Fractal dimension is 73% explained by log network size.** Spearman(N, D) = **+0.880** across the
100-leaf cohort and **+0.990** in the synthetic grid (where the D axis was realised by varying
generations). **[DEM]** D cannot be presented as an independent geometric descriptor without this
control. *But see S3 — D survives the control better than expected.*

**M5. The quality grades are not ordinal, and the leading-flag reduction discards most of the
information.** 31 of 120 leaves (25.8%) carry multiple flags. **15 leaves carry a C (spurious minor
veins) flag but only 11 are leading-grade C — 4 are hidden. 57 leaves carry a D (physical damage) flag
but only 29 are leading-grade D — 28 are hidden.** **[DEM]** So nearly half the cohort has physical
damage while only a quarter is labelled as such, and the paper's grade-A/grade-B narrative rests on a
letter chosen by position in a comma-separated string.

**M6. The manuscript's grade narrative describes a non-significant difference.** Kruskal–Wallis on the
**raw** Δp_c across grades gives **p = 0.0725** — not significant. **[DEM]** The Discussion's claim
that the effect is "smallest and most conservative in the artifact-free grade-A tracings and largest
in grade B, consistent with missing-vein artifacts overstating the reticulation headroom" is an
interpretation of noise. It should be deleted, not defended.

## MODERATE

**Mo1. One cohort leaf is catastrophically fragmented at baseline.** `n_components` in the percolation
cohort: median 2, P90 9, **maximum 4,477**. Baseline `gcc_fraction` correlates with p_c at Spearman
**+0.389** (p = 6 × 10⁻⁵). **[DEM]** A leaf that starts in thousands of pieces has a different p_c for
reasons unrelated to reticulation.

**Mo2. The synthetic grid's 14:1 dominance is inflated by extrapolation.** 18 of 42 cells exceed the
empirical maximum ⟨k⟩ = 2.9893. Restricted to the empirical range (n = 24): standardised β 0.981 vs
0.125 (**7.8:1**, not 13.9:1), R² 0.940, and the partial correlations become **r(p_c, ⟨k⟩|D) = 0.970**
and **r(p_c, D|⟨k⟩) = 0.451** — the latter more than double the full-grid 0.195. **[DEM]** D is not
negligible inside the range real leaves occupy.

**Mo3. A stale code comment contradicts the results.** `percolation.importance_weights` documents:
"in a vascular tree this DISAGREES with betweenness — high-degree nodes are the redundant reticulated
periphery, so a *degree* attack is *weaker* than random." The empirical cohort finds degree-targeted
**more** damaging than random in 100 of 100 leaves. The comment predates the mesh calibration
(`HERO_NUMBERS.md` records the same reversal) and will mislead any reader of the code.

**Mo4. Effect sizes for the paired comparisons are saturated and uninformative on their own.** Both
Wilcoxon statistics are W = 0, so their p-values are functions of n alone; rank-biserial r = 1.00 is a
directional-consistency statement, not a magnitude. Must always be reported beside the median
difference.

## MINOR

Bootstrap method unnamed; `Resistance_2` alternative convention not reported; the pre-symptomatic
window uses the synthetic threshold in arbitrary time units; no phylogenetic correction; no
multiple-comparison statement.

## STRENGTHS — put the weight here

**S1. The reticulation gain survives every quality subsetting, with zero reversals.** **[DEM]**

| subset | n | median Δp_c | improved/unchanged/worsened | sign-test p |
|---|---|---|---|---|
| full cohort | 105 | 0.00950 | 93 / 12 / **0** | 2.0 × 10⁻²⁸ |
| excluding any C flag | 91 | 0.01080 | 79 / 12 / **0** | 3.3 × 10⁻²⁴ |
| excluding any D flag | 49 | 0.00700 | 40 / 9 / **0** | 1.8 × 10⁻¹² |
| no C and no D flag | 40 | 0.00790 | 31 / 9 / **0** | 9.3 × 10⁻¹⁰ |
| leading grade A | 21 | 0.00690 | 13 / 8 / **0** | 2.4 × 10⁻⁴ |
| boundary-check pass only | 102 | 0.00995 | 92 / 10 / **0** | 4.0 × 10⁻²⁸ |

Not one leaf in any subset was made more fragile by added reticulation.

**S2. Over-segmentation is diluting the connectivity result, not creating it.** Excluding all
C-flagged leaves *strengthens* every connectivity association: p_c ~ ⟨k⟩ rises 0.733 → **0.789**
(partial | log N: 0.745 → **0.800**), while p_c ~ D *falls* 0.496 → 0.427. **[DEM]** This is the
cleanest available refutation of the "spurious veins inflate connectivity" objection.

**S3. Every headline association strengthens under size control.** p_c ~ ⟨k⟩ 0.733 → **0.745**;
p_c ~ loop fraction 0.727 → **0.740**; p_c ~ D 0.496 → **0.633** (residualised on log N: **0.577**).
The attack-gap result is size-clean outright: attack gap ~ N = +0.046 (p = 0.65). **[DEM]**

**S4. p_c is independent of the entire hydraulic model.** See C1. This immunises the percolation
results from the radius-inference, Murray's-law and pit-resistance criticisms.

**S5. The K_leaf failure is not a modelling-convention artefact.** Solving all 120 leaves under both
of the deposit's conventions gives ρ = 0.176 (ℓ/r⁴) and ρ = 0.179 (ℓ/r²) against measured K_leaf
(n = 112) — indistinguishable. **[DEM]** The obvious "you picked the wrong radius exponent" objection
is empirically closed.

**S6. Self-diagnostics already in the manuscript.** The headroom check (3.7×), the withdrawn
finite-size claim, the grade stratification and the K_leaf null were all found and reported by the
authors. Foregrounded as deliberate validity checks, they are a substantial credibility asset.

---

# PART II — CAVITATION THRESHOLD SENSITIVITY

Full numbers in `data/cavitation_sensitivity.json`. Network: `config.DEFAULT_NETWORK`, N = 1023,
10-node haustorial patch, K_h = 0.0392 (reproduced exactly), 20.0% diversion at 1.5 MPa.

### II.1 The control the original demonstration omits

| | min interior ψ | embolised at −1.00 | −1.25 | −1.50 | −2.00 | −3.00 |
|---|---|---|---|---|---|---|
| **no parasite (baseline)** | −0.9963 | 0 | 0 | 0 | 0 | 0 |
| calibrated sink, 1.5 MPa | −1.0224 | **1** | 0 | 0 | 0 | 0 |
| calibrated sink, 3.0 MPa | −1.3221 | 6 | 3 | 0 | 0 | 0 |

The baseline column is the essential control: a healthy leaf in this model already sits at −0.996 MPa
because `PSI_LEAF = −1.0`. **Any threshold at or above −1.0 MPa makes the uninfected leaf embolise,**
so the threshold is not freely choosable — it is bounded below by the transpirational boundary
condition.

### II.2 Onset by threshold

| PSI_CAVITATION | onset gradient (MPa) | onset K_h multiple at 1.5 MPa |
|---|---|---|
| −1.00 | **1.1** | **1× (i.e. at the calibrated strength)** |
| −1.10 | 2.1 | 2× |
| −1.25 | 2.7 | 4× |
| −1.50 | 4.0 | 8× |
| −1.75 | 5.0 | 32× |
| **−2.00 (manuscript)** | **6.0** | none up to 256× |
| −2.50 | 8.0 | none |
| −3.00 | 9.5 | none |

**Direction reversal:** at −1.00 MPa the null inverts — the calibrated sink at the illustrative
gradient embolises a vessel, and onset occurs *below* the 1.5 MPa illustrative value.
At −1.10 MPa and beyond the null holds within the manuscript's 0–3 MPa sweep. **Significance and
effect size are not at issue** — the quantity is a count, and it is 0 or small-integer throughout.

### II.3 The margin decomposition

```
reported margin            = |PSI_CAVITATION| - |min psi with sink| = 2.000 - 1.022 = 0.978 MPa
stipulated component       = |PSI_CAVITATION| - |PSI_LEAF|          = 2.000 - 1.000 = 1.000 MPa
parasite component         = min psi(sink) - min psi(baseline)      =              -0.026 MPa
parasite share of margin                                            =                 2.6 %
```

### II.4 The depression law — why the null is derivable

Patch-local depression is linear in the gradient with slope **−0.2682 MPa per MPa** (intercept ≈ 0,
max residual 0.017 MPa across 0–12 MPa). Because K_h is specified *relative* to each node's own
incident conductance, the reservoir's weight in a tapped node's potential is `K_h/(1+K_h)` = 0.0377,
independent of leaf architecture; the patch of 10 nodes compounds this to the observed 0.268. Solving
for the cavitation threshold gives a required gradient of **6.26 MPa** — 4× the illustrative value and
2× the sweep maximum. Largest *measured* parasite–host leaf gradient in the literature: ≈0.5 MPa
(Griebel et al. 2022, mistletoe/eucalypt) **[LIT]**.

### II.5 The host operating point is the variable that actually matters

| PSI_LEAF | baseline min ψ | with sink | ΔΨ | baseline embolised at −2.0 | with sink |
|---|---|---|---|---|---|
| −0.5 | −0.498 | −0.661 | **−0.163** | 0 | 0 |
| −1.0 (default) | −0.996 | −1.022 | −0.026 | 0 | 0 |
| −1.5 | −1.494 | −1.494 | −0.000 | 0 | 0 |
| −2.0 | −1.993 | −1.993 | −0.000 | 0 | 0 |
| −2.5 | −2.491 | −2.491 | −0.000 | **91** | 93 |

Two findings. (a) At a realistic midday operating potential of −2.5 MPa, **91 vessels embolise with no
parasite at all** — the −2.0 MPa threshold is incompatible with realistic operating potentials, and
the "sub-cavitation sink" result lives in a narrow stipulated corner. (b) The parasite's measurable
effect on the *global minimum* vanishes once |PSI_LEAF| exceeds the sink's local pull, because the
global minimum is then set entirely by terminal-adjacent nodes. **The global minimum is the wrong
statistic; the patch-local depression is the right one.**

### II.6 Recommendation

**Adopt a threshold-independent framing.** Report:

1. **ΔΨ at the haustorial patch** = −0.402 MPa at the illustrative gradient (−0.268 MPa per MPa of
   gradient) — invariant to `PSI_CAVITATION`, invariant to `PSI_LEAF`, and the quantity the parasite
   actually controls.
2. **The gradient required to cavitate**: 6.26 MPa, against a largest measured value of ≈0.5 MPa.
3. **The threshold sensitivity table** (II.2) in the Supplement, stating the −1.0 MPa reversal openly.
4. **The baseline control** (II.1) beside every sink result.

**Claims affected:** Results Table 3 and every sentence containing "0 vessels embolised", "−1.02 MPa",
"0.98 MPa", "sub-cavitation", "sub-symptomatic", and the Conclusion's "the haustorial sink is
sub-symptomatic — it does not itself cavitate the host".

---

# PART III — "PRE-SYMPTOMATIC" CLAIM AUDIT

### What the model contains
No symptom variable of any kind. No wilting criterion, no leaf-area loss, no gas exchange, no
time-calibrated infestation course. The dynamics module produces a window in **arbitrary time units**
from the **synthetic** p_c = 0.271 and f_c = 0.524, with growth rates stipulated. **[MOD]**

### The five things "pre-symptomatic" could mean, and which the study supports

| Reading | Supported? |
|---|---|
| Physiological pre-symptomatic disease (host impaired before visible signs) | **[LIT] yes, richly** — Shen et al. 2007: *Cuscuta*/*Mikania*, photosynthetic decline ~50 days before withering; Cochavi et al. 2017: *Orobanche*/sunflower, detectable ~20 days before emergence *while A, g_s and E are statistically unchanged*. **But neither window is hydraulic.** |
| Modelled subcritical deterioration | **[MOD]** yes — this is what the percolation curve below p_c is |
| Incipient hydraulic failure | **[DEM] no** — the sink produces ΔΨ = −0.026 MPa and no embolism |
| Mathematical network collapse | **[DEM]** yes — but that is p_c, not a symptom |
| Observed physiological symptoms | **not modelled at all** |

### The mechanistic objection, which is unanswerable as currently framed
Scoffoni et al. (2017, *Plant Physiol* 173:1197) show outside-xylem vulnerability explains **86–100%**
of K_leaf decline at turgor loss and **75–100%** through P88, with only 5–8.5% of midrib conduits and
**no minor-vein conduits** embolised above turgor loss. Avila et al. (2022) add that connectivity-
mediated spread engages only once a *majority* of conduits are gas-filled. **[LIT]** In the mild-stress
window the paper calls pre-symptomatic, the mechanism it models is the one not yet operating.

### Recommendation: **REMOVE from the title; RETAIN in the Introduction with an operational definition.**

- **Remove** from the title and from every results sentence.
- **Retain** one Introduction paragraph establishing, on Shen 2007 / Cochavi 2017 / Ortiz-Bustos 2017 /
  González de Andrés 2024, that a pre-symptomatic window under parasitism is empirically real with
  lead times from ~20 days to three decades — and stating plainly that its documented signature is
  optical, thermal, growth- and carbon-based, **not hydraulic**. This motivates the study without
  claiming the study measures it.
- **If a term is needed for the sub-threshold regime**, use *sub-critical* or *pre-fragmentation*,
  defined operationally as "removed fraction below p_c". Both are honest and neither imports physiology.
- **Delete "early warning" entirely** — no source found in either pass supports it.

---

---

# PART III-B — TITLE AUDIT

> **Vein Reticulation as a Host-Resistance Trait Against Pre-Symptomatic Hydraulic Collapse Under
> Parasite-Induced Water Stress**

| Component | Verdict | Reason |
|---|---|---|
| **"Vein Reticulation"** | **KEEP** | Measured (loop fraction, ⟨k⟩), manipulated by intervention, and the intervention is the paper's strongest result. **[DEM]** |
| **"Host-Resistance Trait"** | **SOFTEN** | Resistance is never measured. Only structural tolerance to simulated element loss is. Strongest defensible form is "structural basis for resistance" or "candidate resistance trait" (Part V.6). **[INF]** |
| **"Pre-Symptomatic"** | **REMOVE** | The model contains no symptom variable, and in the mild-stress regime the modelled mechanism is the one *not* operating (Scoffoni 2017; Avila 2022). **[SPEC]** |
| **"Hydraulic Collapse"** | **REMOVE** | The collapse measured is topological. `percolation.py` never reads a conductance, a radius or a water potential. **[DEM]** |
| **"Parasite-Induced Water Stress"** | **REMOVE as the driver** | The sink is decoupled from the threshold, contributes ΔΨ = −0.026 MPa, and embolises nothing at the calibrated strength. **[DEM]** |

**Verdict: the title does not survive.** Three of five components describe something the study does not
demonstrate, and one of those three (hydraulic collapse) is contradicted by the architecture of the
code itself.

### Proposed alternatives, in descending order of how much they claim

1. **Vein Reticulation Governs the Structural Collapse Threshold of Leaf Venation Networks: A
   Percolation Analysis of 100 Species with a Haustorial Sink Model**
   *Claims exactly what is demonstrated; names the cohort; keeps the parasite as a component, not a driver.*
2. **Connectivity, Not Spatial Complexity, Determines How Much Vein Loss a Leaf Venation Network Can
   Tolerate**
   *Leads with the causally-controlled result — the paper's most defensible finding. Drops the parasite entirely.*
3. **Reticulate Venation as a Structural Basis for Damage Tolerance in Leaf Vascular Networks:
   Percolation Thresholds Across 100 Species and Their Response to Simulated Reticulation Enhancement**
   *Retains the "resistance trait" framing at the strength the evidence permits.*
4. **Structural Tolerance of Leaf Venation Networks to Vascular Element Loss, and the Decoupling of a
   Calibrated Holoparasitic Sink from the Collapse Threshold**
   *Promotes the negative result to the title — the most honest option, and the one that best matches
   what is actually novel.*
5. **Architectural Determinants of Collapse Thresholds in Real Leaf Venation Networks under Random and
   Structurally Biased Vein Loss**
   *Most conservative; safest for a network-science or plant-methods venue.*

**Recommendation: (1) or (4).** (1) preserves the study's narrative arc and the parasite motivation
while removing every indefensible clause; (4) is the most scientifically candid and makes the
decoupling — a genuinely novel, genuinely publishable negative result — the headline.

---

# PART IV — NOVELTY REPAIR

### Already established (cannot be claimed)

| Component | Prior art |
|---|---|
| Percolation-style robustness of real leaf venation | Mander & Williams 2024 (uses the word "percolation"); Price & Weitz 2014 (the curve, on 339 whole leaves, 1000 iterations) |
| Connectivity predicts venation damage robustness | Price & Weitz 2014: "meshedness being the best predictor of robustness" — and for a planar graph meshedness is an affine transform of ⟨k⟩ |
| Hagen–Poiseuille + Kirchhoff on real traced leaf venation | Skjegstad & Kirkegaard 2025 (graph Laplacian, α ≈ 3.0); **and the source deposit's own `Resistance_4` column** |
| Percolation coupled to solved xylem hydraulics | Mrad et al. 2021 (stem conduits; percolation threshold as a "seal") |
| Reticulation confers damage tolerance | Sack et al. 2008; Brodribb et al. 2016; Katifori et al. 2010 (theory) |

### Reproduced / applied here
Site percolation with a stated criterion; Monte Carlo threshold estimation; box-counting D; Murray's
law radius inference; Kirchhoff solve.

### Extended here
- From **bond** (Price & Weitz) to **site** percolation on real venation. **[DEM]**
- From **random-only** damage to **random + two centrality-weighted** removal processes on a real
  cohort. **[DEM]**
- From **n = 9 taxa** (Mander & Williams) / a single AUC index (Price & Weitz) to **per-network
  thresholds across ~100 species**, regressable against measured architecture. **[DEM]**
- From observational association to an **intervention on the real graphs themselves** (reticulation
  enhancement, 0 of 105 leaves worsened under every subsetting). **[DEM]**

### Genuinely novel
1. **The experimental decoupling of ⟨k⟩ from D on a controlled synthetic grid**, with the causal claim
   re-estimated inside the empirical range (partial r 0.970 vs 0.451; β 0.981 vs 0.125). No prior
   venation study separates these axes causally. **[DEM]**
2. **The attack-gap result**: more reticulate leaves are not merely more robust but *less
   differentially exposed* to structurally biased damage (loop fraction × attack gap = −0.786, and
   −0.789 after size control; attack gap ~ N = +0.046, n.s.). No precedent located in either pass.
   **[DEM]** — currently underplayed relative to its novelty.
3. **A holoparasitic haustorial sink imposed as a boundary condition on a host vascular flow network.**
   Searched from four directions across two passes; nothing found. **[INF — absence of evidence]**

### Potential novelty, conditional on analyses not yet run
A threshold-independent quantification of how far a literature-calibrated haustorial sink sits from
cavitation (Part II) — publishable as a negative result *if* reported with the baseline control and the
derivation, not as "0 embolised".

### The overclaims to remove
- "first percolation analysis of leaf venation" — false (Mander & Williams).
- "no prior study couples HP + Kirchhoff to a percolation threshold on a real leaf-venation cohort" —
  the HP+Kirchhoff clause is broken by Skjegstad & Kirkegaard 2025 and by the paper's own data source.
- "**driven by** a holoparasitic haustorial sink" — the results show the sink and the percolation are
  decoupled; "driven by" asserts what the paper disproves.
- Any framing of the ⟨k⟩→p_c result as a discovery rather than a causally-controlled sharpening of
  Price & Weitz.

### Defensible gap statement (2–3 sentences)

> Damage robustness of real leaf venation has been quantified by random removal of vein segments
> (Price & Weitz, 2014) and framed explicitly in percolation terms (Mander & Williams, 2024), but
> neither study extracted a critical threshold, applied structurally biased damage, or solved flow on
> the damaged network; conversely, Hagen–Poiseuille flow with a Kirchhoff solve has been implemented
> on real traced venation without any damage analysis (Skjegstad & Kirkegaard, 2025), and the coupling
> of percolation to solved xylem hydraulics exists only for stem conduit networks (Mrad et al., 2021).
> We estimate per-network percolation thresholds for ~100 traced leaf venation networks under random
> and centrality-weighted removal, decouple mean degree from fractal dimension on a controlled
> synthetic grid to establish which architectural axis carries the effect, and test the relationship
> by intervention on the real networks themselves. A calibrated holoparasitic haustorial sink is
> imposed as a hydraulic boundary condition on the same networks — to our knowledge the first such
> representation — and is reported as an independent lens, since it proves to be decoupled from the
> structural threshold.

### Replacement Introduction framing
Lead with the **biological question** (does venation architecture confer measurable structural
tolerance to vascular disruption, and can that tolerance be shifted?), not with percolation.
Percolation, graph theory and the Kirchhoff solve are the instruments; say so. Concede Price & Weitz
and Mander & Williams in the second paragraph, in the paper's own voice, before a referee does it.

---

# PART V — RETICULATION EVIDENCE AUDIT

### V.1 The result, fully verified **[DEM]**

Enhancement to the cohort P90 ⟨k⟩ = 2.811 across 105 leaves: median Δp_c = **0.00950**; **93 improved,
12 unchanged, 0 worsened**; Wilcoxon (Pratt, all 105) **p = 1.67 × 10⁻¹⁸**; on the 93 non-zero
differences p = 5.57 × 10⁻¹⁷; rank-biserial r = 1.00. Gain vs baseline ⟨k⟩ Spearman **−0.821**
(R² = 0.651); vs D −0.034 (n.s.).

Grade A (n = 21): 13 improved, 8 unchanged, **0 worsened**; median Δ 0.00690; median baseline ⟨k⟩
**2.665** (the highest of any grade); sign test **p = 2.44 × 10⁻⁴**; Wilcoxon p = 1.47 × 10⁻³
(Pratt 4.68 × 10⁻⁴). Among grade-A leaves that changed at all, **13 of 13 improved.**

### V.2 Is the quality grade a confound? — No, and the reason is precise

- **The raw grade difference is not statistically significant.** Kruskal–Wallis on raw Δp_c across
  grades: **p = 0.0725**. **[DEM]** There is no grade effect to explain, and the manuscript's
  missing-vein-artifact narrative interprets noise. **Delete that sentence.**
- **Baseline connectivity explains the apparent gradient.** Grade A starts at ⟨k⟩ = 2.665 against
  grade B's 2.472, and gain falls steeply with baseline ⟨k⟩ (ρ = −0.821, R² = 0.651). Diminishing
  returns fully accounts for the smaller raw grade-A effect.
- **The artefact hypothesis predicts the wrong sign.** After conditioning Δp_c on baseline ⟨k⟩, the
  residual medians are A **+0.00201**, B −0.00019, C −0.00522, D −0.00062 — grade A is *highest*.
  Kruskal on residuals p = 2.4 × 10⁻⁴. **Caveat, stated honestly:** this is a two-stage
  residualise-then-test procedure and its p-value is not exact; it should be reported as a supporting
  diagnostic, not as the primary evidence. The primary evidence is the non-significant raw test plus
  the subset table.
- **The effect survives every defensible exclusion with zero reversals** (Part I, S1). Excluding all
  C-flagged leaves the median gain *rises* to 0.0108.

**Verdict: "tracing artifact" is not supported by the data.** The correct wording is *not supported*,
not *refuted* — absence of a significant grade effect at n = 105 is not proof of absence.

### V.3 Is grade C creating measurement bias in the *connectivity* result? — No; it is diluting it

Excluding all 15 C-flagged leaves: p_c ~ ⟨k⟩ **0.733 → 0.789**, partial | log N **0.745 → 0.800**,
p_c ~ loop fraction 0.727 → 0.782, while p_c ~ D *weakens* 0.496 → 0.427. **[DEM]**

### V.4 Ceiling / diminishing-return behaviour is real and is a mechanism, not a defect
Gain ~ baseline ⟨k⟩ at ρ = −0.821. Noblin et al. (2008) supply the physical basis: vein addition
saturates once inter-vein spacing approaches the diffusive path length. **[LIT]** This also explains
the 3.7× over-prediction by the response surface.

### V.5 Alternative explanations considered and their status

| Alternative | Status |
|---|---|
| Tracing artefact (missing veins restored) | **Not supported** — raw grade test n.s.; residual sign opposite; survives C- and D-exclusion |
| Network-size effect | **Excluded** — ⟨k⟩ ~ N = +0.037 (p = 0.72); gain is not size-driven |
| Boundary/crop-edge artefact | **Excluded** — boundary-pass-only subset: 92/10/0, median 0.00995 |
| Over-segmentation inflating ⟨k⟩ | **Excluded** — effect *strengthens* without C-flagged leaves |
| Ceiling effect in high-⟨k⟩ leaves | **Confirmed and mechanistic**, not a confound |
| Trade-offs not modelled (carbon, mechanics, leaf area) | **Real and unaddressed** — Price & Weitz 2014 (+3.3% volume, +0.51% conductance), Nardini et al. 2012 (higher LMA, smaller leaves), Ronellenfitsch & Katifori 2019 (Pareto). "0 worsened" is an artefact of optimising one axis of a three-way trade-off — **say so** |

### V.6 Strongest defensible formulation
Of the four offered in the brief, the evidence supports **(3) reticulation provides a structural basis
for resistance**, with (2) association established observationally and the *within-model* causal step
established by intervention. **(1) "reticulation causes resistance" is not available**, because
"resistance" is not measured — only structural tolerance to simulated element loss is.

---

# PART VI — CONFOUND & ROBUSTNESS AUDIT

### VI.1 Mean degree vs loop fraction — the mathematical dependence, resolved

1. **Exact relationship under the definitions used.** Code: `loop_fraction = (E − |bridges|)/E`.
   The cycle-rank fraction, stored separately as `n_cycles/E`, satisfies exactly
   `(E − N + c)/E = 1 − 2/⟨k⟩ + c/E` (verified to 1.4 × 10⁻¹⁶ on all 120 leaves). **[DEM]**
2. **Is loop fraction mathematically derived from ⟨k⟩?** **No.** Non-bridge fraction differs from the
   identity by a mean of 0.564 and is 3.63× larger; a spanning-tree edge lying between two chords is a
   non-bridge yet contributes no independent cycle. Two graphs with identical ⟨k⟩ can differ widely in
   non-bridge fraction. **[DEM]**
3. **Should both be treated as independent biological predictors?** **No** — but for an *empirical*,
   not an algebraic, reason: Spearman(⟨k⟩, loop fraction) = **0.9937** across 120 leaves; a cubic fit
   of loop fraction on ⟨k⟩ gives R² = 0.917 with residual SD 0.047 (range −0.221 to +0.231). They are
   near-collinear in *this* family of planar venation networks.
4. **Redundant information / pseudoreplication?** Yes, as reported. Presenting ρ = 0.733 and ρ = 0.727
   side by side as two lines of evidence overstates convergent support.
5. **Primary metric:** **mean degree ⟨k⟩.** It is the intervention variable (the enhancement raises
   ⟨k⟩ to a target), it is the synthetic grid's axis, and it is directly comparable to Price & Weitz's
   meshedness.
6. **Loop fraction should be presented as a derived descriptive metric**, reported once in Table 1 with
   its correlation to ⟨k⟩ stated, and used **only** where it is not interchangeable — namely the
   bridge/non-bridge decomposition and the attack-gap correlation, where the *bridge* half carries
   the mechanism.
7. **Regressions affected:** none of the fitted models — ⟨k⟩ and D are near-orthogonal (Pearson 0.148,
   **VIF = 1.022**), and the paper's own residual test (loop | ⟨k⟩ vs p_c: ρ = −0.088, p = 0.386)
   already shows loop fraction adds nothing beyond ⟨k⟩. Only the **descriptive correlation table and
   its narrative** need repair.

**Do not write "loop fraction ≈ 1 − 2/⟨k⟩ is a graph identity."** Write instead: *the cycle-rank
fraction is an exact function of mean degree, and the non-bridge loop fraction — the quantity we
report — is not, but is empirically near-collinear with mean degree in planar venation networks
(ρ = 0.994), so we treat connectivity as a single axis represented by ⟨k⟩.*

### VI.2 Fractal dimension vs network size

| quantity | value |
|---|---|
| Spearman(N, D), 100-leaf cohort | **+0.880** |
| R² of D on log₁₀ N | **0.73** |
| Spearman(N, D), synthetic grid | **+0.990** |
| p_c ~ D raw | +0.496 |
| p_c ~ D, D residualised on log N | **+0.577** |
| p_c ~ D, partial given log N | **+0.633** |
| p_c ~ D, excluding C-flagged leaves | +0.427 |
| grid partial r(p_c, D | ⟨k⟩), full | 0.195 |
| grid partial r(p_c, D | ⟨k⟩), restricted to ⟨k⟩ ≤ 2.99 | **0.451** |

**Interpretation.** D is substantially a size readout in both cohorts — which must be disclosed — but
the D–p_c association **survives and strengthens** under size control, and inside the empirical ⟨k⟩
range D's partial correlation more than doubles. The first pass's implication that D is largely a size
artefact is too strong.

**Recommended status for D: supporting predictor, reported residualised or as a partial, with the
size confound stated.** Not primary; not removed. The manuscript's raw ρ = 0.496 should be replaced by
the size-controlled 0.633 with both shown.

### VI.3 Finite-size effects

Empirical Spearman(N, p_c) = **+0.232** (p = 0.020) — weak and **opposite in sign** to the
fixed-architecture synthetic sweep (p_c falls 0.2701 → 0.0772 as N goes 1,023 → 16,383). ⟨k⟩ and loop
fraction are size-independent (ρ = 0.037 and 0.030). Every headline association strengthens under log-N
control. The attack gap is size-clean (ρ = +0.046, p = 0.65). **[DEM]**

**Conclusion: network size does not meaningfully confound p_c, the attack response, mean degree or
loop fraction in the empirical cohort.** The finite-size limitation is real for the *synthetic* sweep
and should be stated there — and the empirical size-control result should be reported in the same
paragraph, because it is what prevents the limitation from contaminating everything else.

*Residual concern:* baseline fragmentation. `n_components` reaches 4,477 in one cohort leaf and
baseline `gcc_fraction` correlates with p_c at +0.389. Report the distribution and confirm the
associations hold on the 99 leaves with `gcc_fraction` > 0.99.

### VI.4 Collinearity / VIF
Pearson r(⟨k⟩, D) = 0.148 → **VIF = 1.022**. The multiple regressions are not collinearity-affected.
The 0.994 problem is confined to the descriptive table (VI.1).

### VI.5 Quality-grade structure

**Not ordinal.** Per the deposit's data dictionary: A excellent; B >80% of veins correct
(*under*-segmentation); C spurious minor veins (*over*-segmentation); D physical damage <25% of leaf
area; E <80% segmented; F damage >25%. B/C/D are orthogonal defect *types* with opposite effects on
connectivity. **Any statement of the form "A > B > C > D" as a quality gradient is invalid.**

Does the manuscript treat them ordinally? Effectively yes, in narrative ("smallest and most
conservative in the artifact-free grade-A tracings … largest in grade B"). No *test* assumes
ordinality (Kruskal treats them as unordered groups), so the statistics are sound; the **prose** is not.

**Recommended treatment: categorical sensitivity stratum, not an exclusion criterion.** Report the
subset table (Part I, S1) as a declared sensitivity block. Additionally: **report flag *presence*, not
the leading letter** — 4 C-contaminated and 28 damaged leaves are currently mislabelled by the
leading-flag rule.

### VI.6 Effect sizes

| Result | Existing statistic | Effect size | Value | Interpretation | Location |
|---|---|---|---|---|---|
| random vs degree-targeted | Wilcoxon W = 0, p = 3.9e−18 | matched-pairs rank-biserial | **r = 1.00**; CL = 100% | perfect directional consistency; magnitude is the median 0.0305 | Results, attack modes |
| reticulation enhancement | Wilcoxon Pratt p = 1.7e−18 | rank-biserial | **≈ 1.00**; 93/12/0 | direction universal; magnitude is the median 0.0095 | Results, enhancement |
| loop quartiles Q1 vs Q4 | Mann–Whitney U = 4, p = 2.3e−9 | **Cliff's δ** | **+0.987** | near-complete separation; medians 0.158 → 0.231 | Results, quartiles |
| p_c ~ ⟨k⟩ | Spearman 0.733 | ρ is its own effect size | + partial 0.745 | — | Results, predictors |
| grade differences in Δp_c | Kruskal p = 0.0725 | **ε² (not yet computed)** | — | **n.s. — report as null** | Results, enhancement |
| K_leaf check | Spearman 0.187, p = 0.073 | **Fisher-z CI** | **[−0.024, +0.382]** | underpowered, not null | Validation |

**Do not add** effect sizes to the 5.67M-vein verification (n makes every statistic meaningless) or to
the Spearman correlations at p ≈ 1e−18.

### VI.7 Targeted-attack axis (new)

| weights | distinct values | Gini | max | nominal 0.2023 → realised | nominal 0.1889 → realised |
|---|---|---|---|---|---|
| degree | 6 | 0.274 | 2.4 | 0.2023 (no clipping) | 0.1889 |
| betweenness | 619 | 0.754 | 29.4 | **0.1578** | **0.1498** |

**Required repair:** either re-express the betweenness threshold on the realised-removed-fraction axis
(**0.150**, not 0.189) or state explicitly that targeted thresholds are quoted as nominal removal
intensities. The qualitative conclusion (betweenness most damaging) *strengthens*.

### VI.8 Hydraulic-conductance model

**What was actually verified.** The deposit defines `Resistance_4` as *"predicted resistance to flow
based on Poiseuille flow i.e. l/r4"*; `realleaf._assign_conductances` implements
`g = (r/r_max)⁴/(L/L_mean)`. Reproducing it to a per-leaf ratio CV of 1.12 × 10⁻⁷ therefore verifies
geometry parsing, unit conversion, exponent and numerical conditioning at scale across 119 leaves and
5,668,467 veins. That is a real and non-trivial **software-correctness** result. It is **not** a
physical validation, because both sides assume the same formula. **The word "validation" must be
replaced by "verification" wherever it refers to this check.**

**What remains independently unvalidated.** That ℓ/r⁴ on *segmented vein width* is the right physics
for a vein bundle; that inferred radii track conduit radii; the omission of end-wall/pit resistance
(~54% of conduit resistivity, Sperry et al. 2005 **[LIT]**); the outside-xylem pathway (26–39%
typically, 11–74% across species **[LIT]**).

**Can `Resistance_2` provide a meaningful sensitivity analysis? — RUN AND ANSWERED.**
`scripts/run_resistance_convention_sensitivity.py`, all **120 leaves**, both conventions solved on the
identical graph: **[DEM]**

| quantity | value |
|---|---|
| Spearman(K_model^r⁴, K_model^r²) across leaves | **0.860** |
| Pearson on log conductance | 0.918 |
| median ratio K^r⁴ / K^r² | 0.064 |
| leaves with degenerate conductance | 1 |
| **K_leaf check under ℓ/r⁴** (n = 112) | **ρ = 0.1764, p = 0.063** |
| **K_leaf check under ℓ/r²** (n = 112) | **ρ = 0.1792, p = 0.059** |

**Decisive result: the convention choice is immaterial to the outcome.** The two conventions rank
species similarly (ρ = 0.86) and give statistically indistinguishable, equally non-significant
agreement with measured K_leaf. **The failed validation is therefore not an artefact of the ℓ/r⁴
choice** — it is a scope limitation of a xylem-only topological model, exactly as Scoffoni et al.
(2017) and Matos et al. (2024) predict. This converts the single most obvious reviewer objection into
a reported robustness result, and it should be stated in one sentence in the validation paragraph.

*Discrepancy to resolve:* this run matches 112 species to measured K_leaf; the manuscript reports
n = 93. The point estimates agree (0.176 vs 0.187), so the difference is almost certainly a cohort
restriction — **confirm which cohort the manuscript's K_leaf check uses and state it.**

**Crucially, the scope is limited: no percolation result can change, because `percolation.py` never
reads conductance.** The convention affects only the Table 1 hydraulic characterisation and the
K_leaf check.

---

# PART VII — BIOLOGICAL INTERPRETATION AUDIT

### VII.1 Parasite / haustorial mechanism

| Biological phenomenon | Model representation | Supporting evidence | Abstraction level | What cannot be claimed |
|---|---|---|---|---|
| Haustorial attachment to host vasculature | a leak conductance `K_h·g_node` at 10 adjacent nodes | Balios et al. 2025: xylic hyphae contact host xylem **[LIT]** | **[MOD]** high | that attachment occurs on leaf-lamina vein junctions — *Cuscuta* attaches to stems, petioles and pedicels **[LIT]** |
| Parasite water withdrawal | Q = K_h(ψ_host − ψ_parasite) with ψ_parasite fixed | Jiang et al. 2003: 20% of host root water uptake (hemiparasite, whole plant) **[LIT]** | **[MOD]** moderate | that 20% is a holoparasite value, a leaf-level value, or a per-haustorium value |
| Host–parasite driving gradient | 1.5 MPa, swept 0–3 | **no primary measurement exists for any holoparasite** (Balios et al. 2025, explicit) **[LIT]** | **[SPEC]** | any specific gradient value; the largest measured parasite–host leaf gradient is ≈0.5 MPa (Griebel et al. 2022) |
| Parasite xylem as high-resistance element | potential boundary condition rather than a wide-bore edge | Zhang et al. 2024/25: parasite xylem narrower, lower conductivity **[LIT]** | **[MOD]** low — well justified | — |
| Host vessel embolism | node removed when ψ < PSI_CAVITATION | Tyree & Sperry runaway framing **[LIT]** | **[MOD]** high | that this occurs at the calibrated sink — it does not (Part II) |
| Node removal in the percolation model | uniform-random or centrality-weighted site deletion | **none for parasitic node deletion**; nearest positive evidence is *host-defence* occlusion in resistant genotypes (Pérez-de-Luque et al. 2005; Cao et al. 2023) **[LIT]** | **[MOD]** very high | that a haustorium deletes host vein junctions. Kaga et al. 2020: the haustorium *adds* a xylem bridge — topologically an edge addition **[LIT]** |
| Network disconnection / p_c | GCC < 50% of N₀ with probability 0.5 | Mander & Williams 2024 use a fixed-fraction functional criterion **[LIT]** | **[MOD]** moderate | that GCC loss is cavitation, PLC, or wilting |

**Required Methods sentence:** *site removal represents loss of conducting function at a junction, from
any cause, and is not a claim that haustorial attachment physically deletes host vein junctions; the
empirically documented route to host conductance loss at an infection site is the host's own
lignification and occlusion response in incompatible interactions.*

### VII.2 Reticulation as resistance
See Part V.6. Strongest available: **"provides a structural basis for resistance"** / **"is a candidate
resistance trait"**. Supporting **[LIT]**: Sack et al. 2008 (complete tolerance of 2°+ vein damage;
75% ± 10% K_leaf loss on midrib severance in pinnate leaves), Mander & Williams 2024 (reticulate >
branched over 200 Myr), Mrad et al. 2021 (connectivity improves embolism-spread resistance without a
conductivity penalty), Katifori et al. 2010 (loops are the damage optimum).
Contradicting / bounding **[LIT]**: Blonder et al. 2018 (reticulation's ecological signal runs to
mechanical strength and chemical defence, not hydraulics); Blonder et al. 2020 (architecture–function
links weak and scale-dependent); Matos et al. 2024 (architecture predicts resilience *weakly* on these
same 122 species); Loepfe et al. 2007 (connectivity raises embolism vulnerability at conduit scale);
Blackman et al. 2018 (P50_leaf unrelated to vein density; governed by conduit wall reinforcement).

### VII.3 The graph-to-physiology bridge

| Claim | Evidence type | Confidence | Allowed wording |
|---|---|---|---|
| Higher ⟨k⟩ → higher p_c | **[DEM]** intervention + causal grid + observation | High | "increases", "raises", causal *within the model* |
| p_c is a property of venation architecture | **[DEM]** | High | "architectural robustness index" |
| ⟨k⟩ → hydraulic conductance | **[MOD]** — the conductance model is not independently validated (K_leaf ρ = 0.187, CI [−0.024, 0.382]) | Low | "modelled conductance"; never "conductance" unqualified |
| Connectivity loss → hydraulic dysfunction | **[INF]** — Brodribb et al. 2021 show supply-path severance causes irreversible local damage **[LIT]**; no threshold mapping exists | Moderate for the mechanism, none for the number | "loss of a connected supply path has been shown to cause local tissue damage"; never "p_c corresponds to hydraulic failure" |
| Connectivity loss → embolism / cavitation | **[SPEC]** — contradicted at mild stress (Scoffoni 2017; Avila 2022) | None | **forbidden** |
| p_c → physiological failure / wilting | **[SPEC]** | None | **forbidden** |
| Parasite sink → cavitation | **[DEM] negative** — ΔΨ = −0.026 MPa; needs a 6.26 MPa gradient | High (as a negative) | "the calibrated sink does not approach the modelled cavitation threshold" |
| Parasite sink → structural collapse | **[DEM] negative** — no collapse at any haustorial density at calibrated K_h | High (as a negative) | report as a decoupling finding |

---

# PART VIII — CITATION & REFERENCE AUDIT

### Independently verified via Crossref this pass

| Reference | Verified record | Status |
|---|---|---|
| Matos et al. 2024 **dataset** | *Ecology* **105**(12), e4436, doi 10.1002/ecy.4436, "Leaf architecture and functional traits for 122 species at the University of California Botanical Garden at Berkeley"; authors Matos, Boakye, Antonio, Carlos, Chu… | **CONFIRMED** — this is the data citation |
| Matos et al. 2024 **analysis** | *New Phytologist* **244**(2), 407–425, doi 10.1111/nph.20037; authors Matos, Boakye, Niewiadomski, Antonio… | **CONFIRMED distinct paper** — the manuscript currently fuses the two |
| Ronellenfitsch & Katifori 2019 | *Phys. Rev. Lett.* **123**(24), **248101**, "Phenotypes of Vascular Flow Networks" | **CONFIRMED** — manuscript's "038301" is wrong |
| Sack et al. 2008 | *PNAS* **105**, 1567–1572, doi 10.1073/pnas.0709333105 | **CONFIRMED** — manuscript's "*Plant Cell Environ* 31:943–958" does not resolve |
| Mrad et al. 2021 | *New Phytologist* **231**, 996–1007; authors **Mrad, Johnson, Love, Domec** | **CONFIRMED** — distinct from Mrad et al. 2018 (Mrad, Domec, Huang, Lens, Katul) |
| Xu et al. | *New Phytologist* **229**, 631–648, issued **2020** | `rrl/F` gives 2021 — **use 2020** |
| Zhang et al. | *New Phytologist* **245**, 607–624; Crossref issued **2024**, print issue 2025 | state the year consistently; verify against the printed issue |
| Scoffoni et al. | *New Phytologist* **213**, 1076–1092; Crossref issued 2016, print 2017 | 2017 is fine (print) |
| Price & Weitz 2014; Mander & Williams 2024; Loepfe 2007; Newman 2003; Newman & Ziff 2001; Dorogovtsev 2008; Albert 2000; Callaway 2000; Scoffoni 2017 *Plant Physiol*; Mrad 2018; Jiang 2003; Muraleedharan 2023 | all resolve as cited | **CONFIRMED** |

Additional: **Albert, Jeong & Barabási (2000) carries a published erratum**, *Nature* **409**(6819), 542,
doi 10.1038/35054111. Cite it alongside.

### Claim-by-claim classification of substantive manuscript claims

| # | Claim (as currently written) | Class | Action |
|---|---|---|---|
| 1 | Host networks collapse at a well-defined connectivity threshold | **A** | keep; rename p_c → f₅₀ or state the criterion inline |
| 2 | Degree-targeted loss is more damaging than random | **A** | keep; add r_rb = 1.00 and the 100/100 count |
| 3 | Betweenness-targeted loss is most damaging (p_c = 0.1889) | **A**, number wrong | re-express on the realised axis (0.150) or label as nominal |
| 4 | Connectivity is the dominant lever on p_c | **A** | keep; use the restricted-grid numbers |
| 5 | Fractal dimension is a real but secondary predictor | **A**, understated | report size-controlled 0.633 and restricted-grid partial 0.451 |
| 6 | Adding loops raises p_c in 89% of leaves and lowers it in none | **A** | keep; add the subset table |
| 7 | The grade-A result is the honest lower bound because artifacts overstate headroom | **E** | **delete** — raw grade test p = 0.0725 |
| 8 | The haustorial sink is sub-symptomatic; 0 vessels embolise | **A** at −2.0 MPa only | reframe threshold-independently (Part II.6) |
| 9 | The hydraulic sink and percolation collapse are decoupled lenses | **A** | promote to a finding |
| 10 | A pre-symptomatic window exists in which the host is functionally compromised before visible wilting | **D/E** | remove from Results/Conclusion; retain as **B** in the Introduction with the empirical citations |
| 11 | The model's hydraulic core is validated to floating-point precision | **E** (mislabelled) | "verified"; state the shared-convention caveat |
| 12 | Modelled conductance correlates weakly with measured K_leaf | **A** | add CI [−0.024, 0.382]; call it underpowered |
| 13 | f_c = 0.524 agrees with the Molloy–Reed prediction 0.531 | **C**, weak | state both are tree-like calculations on the same degree sequence — internal consistency, not corroboration |
| 14 | No prior work couples a hydraulic resistor model to a percolation threshold on real leaf venation | **E** | replace with the Part IV gap statement |
| 15 | Reticulate venation buys robustness by providing redundant pathways | **B** | keep; cite Katifori 2010 + Sack 2008 + Price & Weitz 2014 |
| 16 | Vein reticulation is a host-resistance trait | **C** | soften to "provides a structural basis for" / "candidate" |
| 17 | The networks tolerate random failure but are fragile to concentrated loss | **A/B** | keep, but note the gap is *small* (15.7%) — as Albert et al. predict for a homogeneous degree distribution |

**Claims needing softening rather than another citation:** 7, 8, 10, 11, 14, 16.

---

# PART IX — REVISED SCIENTIFIC ARGUMENT

**Problem.** Leaf venation networks vary enormously in how reticulate they are, and reticulation is
widely assumed to buy tolerance to vascular damage — but the assumption is supported mostly by
qualitative contrasts, and it has not been separated from the geometric traits reticulation covaries
with.

**Gap.** Damage robustness of real venation has been measured as a curve or an area-under-curve index
on random segment removal (Price & Weitz 2014; Mander & Williams 2024), never as a per-network
threshold; no study has separated connectivity from spatial complexity experimentally; no study has
applied structurally biased damage to a real venation cohort; and no study has imposed a parasitic
hydraulic boundary condition on a host vascular network.

**Research question.** Does venation connectivity determine how much structural loss a leaf's vascular
network can absorb before it fragments — and can that tolerance be shifted by adding reticulation?

**Hypothesis.** Networks with more reticulate connectivity fragment only after a larger fraction of
junctions is lost, and the effect is attributable to connectivity rather than to spatial complexity.

**Methodological test.** Site percolation on 100 traced venation networks under random and
centrality-weighted removal; a 42-network synthetic grid decoupling ⟨k⟩ from D; an intervention that
raises ⟨k⟩ to the cohort's own 90th percentile on the real graphs; a Kirchhoff/Hagen–Poiseuille solve
with a literature-calibrated haustorial sink as an independent hydraulic lens.

**Major results.** (i) p_c median 0.200 random / 0.169 degree-targeted, 100/100 leaves, r_rb = 1.00.
(ii) p_c ~ ⟨k⟩ ρ = 0.733 (0.745 size-controlled; 0.789 excluding over-segmented leaves).
(iii) On the decoupled grid within the empirical range, partial r(p_c, ⟨k⟩|D) = 0.970 vs
r(p_c, D|⟨k⟩) = 0.451, standardised β 0.981 vs 0.125. (iv) Enhancement raises p_c in 93/105 leaves and
lowers it in none, in every quality subset. (v) More reticulate leaves show a *smaller* random-minus-
targeted gap (ρ = −0.786). (vi) The calibrated sink depresses leaf potential by 0.027 MPa and requires
a 6.26 MPa gradient to cavitate — it is decoupled from the structural threshold.

**Mechanism.** ⟨k⟩ sets the expected number of surviving neighbours per retained node, which is what
determines whether a spanning cluster persists; loops supply the alternative routes that a bridge
cannot. Bridge-rich leaves are simultaneously less robust *and* more differentially exposed to
structurally biased loss, which is why the attack gap tracks bridge fraction.

**Biological interpretation.** Venation connectivity is a measurable architectural determinant of
structural tolerance to vascular element loss — the substrate on which any resistance to vascular
disruption must act — but it is not itself a demonstration of resistance in planta.

**Limitations.** Topology, not physiology; crop windows without petioles; a conductance model that
fails its only independent test; a parasite abstraction with no anatomical warrant for node deletion;
no cost term in the enhancement.

**Contribution.** The first per-network percolation thresholds for a large real venation cohort; the
first experimental decoupling of connectivity from fractal dimension in venation robustness; the first
demonstration that reticulation narrows differential exposure to structurally biased damage; and the
first haustorial sink imposed as a boundary condition on a host vascular network — reported, honestly,
as decoupled from the structural result.

---

# PART X — RESULTS → DISCUSSION MATRIX

| Result | What it shows | Pattern | Statistical support | Mechanism | Literature | Biological meaning | Caveat |
|---|---|---|---|---|---|---|---|
| Median p_c 0.200 random | venation fragments after ~1/5 of junctions are lost | invariant ordering across all 100 leaves | 2,400 trials/leaf; logistic inflection | connectivity sets surviving-neighbour count | Mander & Williams 2024 (fixed-fraction criterion) | an architectural tolerance index | criterion-dependent; not a critical point; not physiological |
| 0.200 → 0.169 degree-targeted | *where* loss falls matters | 100/100 leaves; median diff 0.0305 | W = 0, p = 3.9e−18, **r_rb = 1.00** | biased removal hits load-bearing junctions | Albert 2000 (+erratum); Callaway 2000 | vulnerability is not a function of loss magnitude alone | weighted-stochastic, not rank-ordered; gap is small, as predicted for a homogeneous degree distribution |
| Betweenness 0.1889 nominal (0.150 realised) | backbone-weighted loss is worst | ordering betweenness < degree < random | 1e5 trials, bootstrap CI | betweenness concentrates on bridges/articulation points | Tian et al. 2017; Motter & Lai 2002 | the structural worst case | synthetic reference only; axis differs from random |
| p_c ~ ⟨k⟩ 0.733 (0.745 ctrl; 0.789 no-C) | connectivity predicts tolerance | monotone, strengthens under every control | n = 100, p = 4.5e−18 | alternative routes | Price & Weitz 2014 (meshedness) | reticulation is a robustness phenotype | observational; ⟨k⟩ and loop fraction are one axis |
| Grid partial 0.970 vs 0.451 (restricted) | connectivity carries the effect, D contributes | dominance shrinks 13.9:1 → 7.8:1 in-range | n = 24, R² 0.940 | decoupled by design | Ronellenfitsch 2015 (topology ⊥ geometry) | geometry is secondary, not irrelevant | synthetic; extrapolation removed |
| D ~ N 0.880; p_c ~ D 0.633 ctrl | D is size-entangled but survives control | raw 0.496 → controlled 0.633 | p = 1.6e−12 | space-filling covaries with extent | Muraleedharan 2023 (box-counting limits) | spatial complexity contributes secondarily | must be reported residualised |
| Enhancement 0.201 → 0.215, 0 worsened | tolerance is manipulable | holds in every quality subset | Pratt p = 1.7e−18; grade-A sign p = 2.4e−4 | added loops close bridges | Katifori 2010; Price & Weitz cost | reticulation is a lever, not a correlate | no cost term; within-model only |
| Gain ~ baseline ⟨k⟩ −0.821 | diminishing returns | R² 0.651 | p = 8.1e−27 | vein-addition saturation | Noblin et al. 2008 | sparse leaves have the most to gain | mediates the entire grade pattern |
| Loop × attack gap −0.786 (−0.789 ctrl) | reticulate leaves are less differentially exposed | size-clean (N: +0.046 n.s.) | p = 3.5e−22 | bridges are what targeting exploits | Tian et al. 2017 | reticulation buys uniformity of risk, not only robustness | one finding measured several ways |
| Sink: ΔΨ −0.027 MPa; 6.26 MPa to cavitate | the calibrated sink cannot cavitate | linear depression law, R² ≈ 1 | deterministic solve | K_h/(1+K_h) clamp | Griebel 2022 (0.6 MPa measured); Scoffoni 2017 (minor veins do not embolise) | parasite harm is resource drain, not rupture | arithmetic consequence of the parameterisation; threshold-dependent below −1.1 MPa |
| K_leaf ρ 0.187, CI [−0.02, 0.38] | topology alone does not predict K_leaf | underpowered | n = 93 | outside-xylem dominates | Scoffoni 2017 (86–100%); Matos 2024 (architecture predicts efficiency weakly) | the model is a xylem-network model | the paper's only independent physical test |

---

# PART X-B — RESULT RANKING (Tier A–D)

Ranked on relevance to the central hypothesis, statistical strength, biological meaning, novelty,
literature support and robustness.

### Tier A — full Discussion paragraph each
| Rank | Result | Why it ranks here |
|---|---|---|
| 1 | **Reticulation enhancement: 93/105 improved, 0 worsened, in every quality subset** | The only within-network intervention; survives C-exclusion, D-exclusion, grade-A, and boundary subsetting; zero reversals anywhere; directly tests the central hypothesis |
| 2 | **Decoupled synthetic grid, restricted to the empirical range** (partial 0.970 vs 0.451; β 0.981/0.125; R² 0.940) | The causal warrant; phylogeny-free, artefact-free, quality-free; now stated inside the observed range |
| 3 | **p_c ~ connectivity across 100 leaves** (0.733 raw → 0.745 size-controlled → 0.789 excluding over-segmented leaves) | Strengthens under every control; the association the whole paper rests on |
| 4 | **Structurally biased loss is more damaging in 100/100 leaves** (0.200 → 0.169, r_rb = 1.00) | Within-leaf paired design; most confounds cancel; unanimity is very hard to attack |
| 5 | **The attack-gap result** (loop × gap −0.786, size-clean) | Genuinely novel, no precedent located, and currently underplayed |
| 6 | **The haustorial-sink decoupling, threshold-independently framed** (ΔΨ −0.027 MPa; 6.26 MPa needed) | A quantified, derivable negative result; the only novel clause left in the novelty claim |

### Tier B — supporting evidence, folded into a Tier-A paragraph
| Result | Folds into |
|---|---|
| Diminishing returns: gain ~ baseline ⟨k⟩ = −0.821, R² 0.651 | Tier A #1 (explains the magnitude and the grade pattern) |
| Fractal dimension, size-controlled (0.496 → 0.633; grid partial 0.451 in-range) | Tier A #2 (as the demoted-but-not-dismissed second axis) |
| Loop quartiles Q1 → Q4, Cliff's δ = 0.987 | Tier A #3 |
| Architectural characterisation (⟨k⟩ 2.520, degree SD 0.848, max degree 4–5) | Tier A #4 (establishes the homogeneous, planar-bounded regime that *predicts* a small attack gap) |
| Empirical size-control table | Tier A #3 |

### Tier C — Results only, no Discussion paragraph
Solver verification against `Resistance_4` (relabelled) · the ℓ/r² convention sensitivity (one
sentence) · baseline fragmentation distribution · boundary/crop-edge check · trial budgets and MCSE ·
effect-size table.

### Tier D — Supplementary or omit
The pre-symptomatic window (synthetic threshold, arbitrary time units — **omit or reduce to a labelled
dimensionless illustration**) · the finite-size sweep (Supplement, with the empirical size-control
result beside it) · f_c vs Molloy–Reed (Supplement, labelled as an internal consistency check) ·
β / universality (omit entirely) · the five-parasite comparison (already dropped) · the response-surface
headroom prediction (Supplement, with the 3.7× reconciliation).

---

# PART XI — DISCUSSION PARAGRAPH BLUEPRINT

Fourteen paragraphs. Patterns refer to `rrl/J_paragraph_architecture.md`.

| # | Purpose | Opening claim | Results | Quantitative pattern | Mechanism | Literature bridge | Implication | Qualification | Pattern |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Fix the threshold as a measurable per-leaf architectural quantity | real venation fragments after ~1/5 of its junctions are lost | median 0.200; synthetic 0.271 as internal contrast | invariant across 4.5 orders of magnitude in N | surviving-neighbour count | Mander & Williams 2024 | an architectural index comparable across species | criterion-dependent; not a critical point | P1 |
| 2 | Connectivity as the leading correlate, and what the partial rules out | connectivity predicts tolerance | ρ 0.733; partial|D 0.736; size-controlled 0.745; no-C 0.789 | strengthens under every control | alternative routes | Price & Weitz 2014 | reticulation is a robustness phenotype | R² 0.507 — half the variance is elsewhere | P2 |
| 3 | The causal warrant, stated inside the empirical range | decoupling connectivity from geometry isolates the effect | restricted grid: partial 0.970 vs 0.451; β 0.981/0.125; R² 0.940 | dominance 7.8:1 in-range vs 13.9:1 extrapolated | design | Ronellenfitsch 2015 | connectivity is causally upstream *within the model* | synthetic; effect size does not transfer | P5→P1 |
| 4 | Place fractal dimension correctly — secondary, not artefactual | D is entangled with size yet survives it | ρ(N,D) 0.880; p_c~D 0.496 raw → 0.633 controlled; grid partial 0.451 in-range | control *raises* the association | space-filling covaries with extent | Muraleedharan 2023 | geometry contributes secondarily | box-counting is scale-range-limited | P4 |
| 5 | Attack modes as an envelope, with realism status per mode | where loss falls matters more than how much | 0.200→0.169, 100/100, r_rb 1.00; betweenness 0.150 realised | ordering is the result | weighted-stochastic removal | Trajanovski 2013; Callaway 2000; Memmott 2004 | bounds the plausible response range | no organism computes centrality; the gap is small, as predicted | P3 |
| 6 | Loops act asymmetrically | reticulation narrows differential exposure | loop × targeted +0.818; loop × gap −0.786 (−0.789 ctrl) | size-clean | bridges are what targeting exploits | Tian et al. 2017 | uniformity of risk, not just robustness | one construct measured several ways | P2/P5 |
| 7 | The intervention | tolerance is manipulable, not merely correlated | 0.201→0.215; 93/12/0; every subset; grade-A p 2.4e−4 | zero reversals anywhere | added loops close bridges | Katifori 2010 | reticulation is a lever | no cost term modelled | P1 |
| 8 | Derive why the gain is small | the magnitude follows from where thresholds live | 0.014 against the R² 0.507 spread; gain ~ ⟨k⟩₀ −0.821 | diminishing returns | vein-addition saturation | Noblin 2008; Price & Weitz cost | small but universal | do not extrapolate beyond the tested range | P12 |
| 9 | Quality triage — and retire the artefact narrative | tracing quality does not explain the gain | raw Kruskal p = 0.0725; no-C median *rises* to 0.0108; 0 worsened in all subsets | the artefact hypothesis predicts the wrong sign | baseline-⟨k⟩ mediation | — | the effect is not measurement recovery | not supported ≠ refuted; grades are non-ordinal | P14 |
| 10 | Reconcile the 3.7× surface-vs-rewiring gap | two analyses disagree by 3.7× and are not the same quantity | ratio stated first | between-leaf extrapolation vs within-leaf perturbation | covariate confounding | — | rely on the intervention | never split the difference | P13 |
| 11 | The sink null, threshold-independently | the calibrated sink cannot approach cavitation | ΔΨ −0.027 MPa; slope −0.268 MPa/MPa; 6.26 MPa needed; 91 vessels embolise at ψ_leaf −2.5 with no parasite | linear and derivable | K_h/(1+K_h) clamp | Griebel 2022; Scoffoni 2017 | harm is resource drain, not rupture | arithmetic consequence of the parameterisation; inverts at −1.0 MPa | P6+P12 |
| 12 | Draw the topology/physiology boundary and forbid the crossing | the two analyses share a graph but not a currency | uses ¶1, ¶5, ¶11 | — | — | Brodribb 2021 (supply-path severance) | p_c is architectural, not physiological | binds the Abstract too | P9 |
| 13 | The failed validation, with the dependency partition | topology alone does not predict measured K_leaf | ρ 0.187, CI [−0.024, 0.382] | underpowered, not null | outside-xylem dominance | Scoffoni 2017; Matos 2024 | the model is a xylem-network model | **percolation results do not depend on this test; the sink simulation does** | P7 |
| 14 | Assumptions ranked, then the increment, then close | four assumptions of decreasing security | site-vs-bond; radius inference; crop windows/no petiole/no enforced source; sink parameterisation | — | — | Sperry 2005; Price 2013 | — | no priority claim | P11 → P10 |

**Do not combine** (carried forward and extended): D with connectivity; the sink with the percolation
threshold; synthetic with empirical thresholds as a magnitude comparison; the enhancement gain with
the response-surface prediction; the failed K_leaf check with any check that passed; the withdrawn
finite-size claim with the synthetic threshold values. **New:** do not combine the betweenness result
with the empirical two-mode result without marking the axis difference.

---

# PART XII — HOSTILE PANEL REVIEW

**Novelty — "Isn't percolation of venation already established?"**
*Vulnerability:* yes, Mander & Williams 2024 use the word; Price & Weitz 2014 plot the curve.
*Evidence needed:* the specific increment. *Answer:* prior work reports curves and AUC indices on
random segment removal for 9 and 339 leaves; this study reports per-network thresholds for ~100
species, applies structurally biased removal, decouples connectivity from geometry experimentally, and
intervenes on the real graphs. *Limitation:* the framing is not new and the paper must say so first.

**"Isn't hydraulic network modelling already established?"** *Vulnerability:* yes — Skjegstad &
Kirkegaard 2025, and the deposit's own `Resistance_4`. *Answer:* the hydraulic layer is not claimed as
novel; it is an instrument, and its only independent test failed. *Limitation:* it should be presented
as a secondary lens.

**Biological mechanism — "What does the parasite actually do in the model?"**
*Answer:* it imposes a leak conductance at ten adjacent nodes, drawing water toward a fixed reservoir
potential. It removes nothing. The node removals in the percolation analysis are a separate, generic
damage abstraction. *Limitation:* there is no anatomical warrant for parasite-driven node deletion;
*Cuscuta* haustoria *add* a xylem bridge (Kaga et al. 2020).

**"Is graph attack a valid haustorial abstraction?"** *Answer:* no, and the paper should not claim it
is. Random removal is a null structural scenario; centrality-weighted removal is a bounding scenario
in the sense of Trajanovski et al. (2013) and Memmott et al. (2004). *Limitation:* the biologically
realistic damage geometry — a spatially contiguous lesion — was not simulated.

**Hydraulic interpretation — "How do you know this is hydraulic collapse?"**
*Answer:* it is not. p_c is computed on an unweighted adjacency matrix; no hydraulic quantity enters.
*Limitation:* the title must change.

**"How do you distinguish topology from physiology?"** *Answer:* by refusing the crossing. The paper
can say that severance of a supply path causes irreversible local damage (Brodribb et al. 2021) and
that its threshold quantifies when such severance becomes widespread; it cannot convert p_c to PLC,
P50 or ψ.

**Pre-symptomatic — "Where is the evidence that it occurs before symptoms?"**
*Answer:* in the literature (Shen 2007 ~50 d; Cochavi 2017 ~20 d), not in this model, which contains no
symptom variable. *Limitation:* remove the term from the title and results.

**Reticulation — "Could the result be explained by network size?"**
*Answer:* no. ⟨k⟩ ~ N = +0.037 (p = 0.72); every association strengthens under log-N control; the
attack gap is size-clean. *Limitation:* one leaf has 4,477 baseline components.

**"Could it be a tracing artifact?"** *Answer:* not supported. The raw grade difference is not
significant (Kruskal p = 0.0725); excluding all over-segmented leaves *strengthens* the connectivity
association (0.733 → 0.789) and *raises* the enhancement gain (0.0095 → 0.0108); zero leaves worsened
in any subset. *Limitation:* not supported is not refuted, and the grades are non-ordinal.

**"Could reticulation have trade-offs?"** *Answer:* yes, and the model has no cost term. Price & Weitz
price the material cost, Nardini et al. the ecological cost, Ronellenfitsch & Katifori the Pareto
structure. *Limitation:* "0 worsened" reflects single-objective optimisation.

**Fractal dimension — "Is D mostly measuring network size?"** *Answer:* 73% of its variance is, but
the D–p_c association survives and strengthens under size control (0.496 → 0.633) and its in-range
grid partial is 0.451. *Limitation:* report residualised; do not lead with D.

**Percolation — "Is p_c biological or mathematical?"** *Answer:* mathematical, with a functional
interpretation borrowed from Mander & Williams' "proxy for retention of a functional vascular transport
system". *Limitation:* rename to f₅₀ and state that a fixed-fraction criterion is not a critical point.

**"Does it survive finite-size effects?"** *Answer:* the empirical cohort does — p_c ~ N = +0.232,
opposite in sign to the synthetic sweep, with all associations strengthening under size control. The
synthetic sweep supports no claim and none is made. *Limitation:* no scaling collapse was run.

**Cavitation — "What happens at −1.0, −1.5, −2.0 MPa?"** *Answer:* onset gradients 1.1, 4.0 and
6.0 MPa respectively; at −1.0 MPa the calibrated sink embolises one vessel at the illustrative gradient
and the null inverts. *Limitation:* the null is threshold-dependent and must be reported as such.

**Graph metrics — "Why use both mean degree and loop fraction?"** *Answer:* we should not. They are
near-collinear (ρ = 0.994) in planar venation; ⟨k⟩ is the intervention variable and is reported as the
single connectivity axis; loop fraction is descriptive, and the bridge decomposition is retained only
where it carries the mechanism. *Limitation:* they are not algebraically identical — the identity holds
for cycle rank, not for the non-bridge fraction.

**Quality grades — "Are A–D ordinal?"** *Answer:* no; they are defect types. *Limitation:* the archive
keeps only the leading flag, hiding 4 over-segmented and 28 damaged leaves.

**Data — "Why use leaf venation as a proxy for xylem?"** *Answer:* we do not claim it is one. The
object is the venation network; the conductance layer is a modelled overlay whose only independent
test was underpowered. *Limitation:* a vein segment contains many conduits; failure is conduit-scale.

**"Is `Resistance_4` matching independent validation or implementation verification?"**
*Answer:* verification. The deposit defines the column as ℓ/r⁴ and the solver implements ℓ/r⁴.
*Limitation:* stated; and the ℓ/r² sensitivity is being reported.

---

# PART XIII — DO NOT CLAIM

1. "First percolation analysis of leaf venation" — Mander & Williams (2024) used the term.
2. "First to couple Hagen–Poiseuille and Kirchhoff to leaf venation" — Skjegstad & Kirkegaard (2025),
   and the source deposit's own resistance column.
3. "Driven by a holoparasitic haustorial sink" — the study reports the sink as decoupled.
4. "The parasite causes embolism" / "parasite-induced hydraulic collapse" — ΔΨ = −0.026 MPa; zero
   vessels embolise at the calibrated strength; a 6.26 MPa gradient would be required.
5. "0 vessels embolise at any gradient" — false at −1.0 MPa and outside the 0–3 MPa sweep.
6. "The host retains a 0.98 MPa safety margin" — 97.4% of that margin is the stipulated
   `PSI_LEAF − PSI_CAVITATION` gap.
7. "p_c equals, corresponds to, or predicts the physiological cavitation threshold" — different units,
   no mapping, and the percolation engine never reads a water potential.
8. "Pre-symptomatic collapse" without an operational definition — and not at all in Results.
9. "Early warning" — no source in either pass supports it.
10. "Validated hydraulic model" — say **verified**; the one independent test gave ρ = 0.187,
    CI [−0.024, 0.382].
11. "Degree- or betweenness-targeted attack represents parasite behaviour" — they are bounding
    scenarios; removal is probabilistic, not rank-ordered.
12. "The parasite removes/deletes host vein junctions" — haustorial connection is topologically
    *additive* (Kaga et al. 2020).
13. "Fractal dimension independently measures spatial complexity" — 73% of its variance is log N.
14. "Mean degree and loop fraction are independent predictors" — ρ = 0.994; report one axis.
15. "Loop fraction ≈ 1 − 2/⟨k⟩ is a graph identity" — true for cycle rank, false for the non-bridge
    fraction actually reported.
16. "A > B > C > D quality gradient" — the grades are non-ordinal defect types.
17. "The reticulation benefit is smaller in clean tracings because artifacts overstate headroom" —
    the raw grade difference is not significant (p = 0.0725).
18. "Betweenness-targeted p_c = 0.1889 is 30% below the random threshold" — 0.1889 is a nominal
    removal intensity; the realised removed fraction is 0.150.
19. "Reticulation causes host resistance" — only structural tolerance to simulated element loss is
    demonstrated.
20. "f_c = 0.524 validates the model against Molloy–Reed" — both are tree-like calculations on the
    same degree sequence.
21. "Architecture strongly predicts resilience" — the source study reports the opposite on these same
    122 species.
22. "The finding generalises to whole leaves" — 100 of 120 networks are crop windows with no petiole.
23. "Adding reticulation is beneficial" without a cost caveat — no cost term exists in the model.
24. "The transition is a phase transition" / any universality-class or β claim.

---

# PART XIV — WRITING HANDOFF

**Strongest claims, in the order they should carry weight**
1. Venation connectivity predicts and, by intervention, shifts a network's structural tolerance to
   junction loss — with 0 of 105 leaves worsened in *every* quality subset.
2. On a design that decouples connectivity from spatial complexity within the empirically observed
   range, connectivity carries the effect (partial 0.970 vs 0.451; β 0.981 vs 0.125; R² 0.940).
3. Structurally biased loss is more damaging than random loss in 100 of 100 leaves, and more reticulate
   leaves are *less differentially exposed* to it.
4. Every association strengthens under network-size control and under exclusion of over-segmented
   tracings.
5. A literature-calibrated haustorial sink is decoupled from the structural threshold — reported as a
   quantified negative result with a derivation.

**Safest terminology**
f₅₀ or "critical removal fraction" (not p_c/"percolation threshold" unqualified) · "structural
tolerance"/"architectural robustness" (not "resistance"/"hydraulic collapse") · "verified" (not
"validated") for the resistance-column check · "sub-critical"/"pre-fragmentation" (not
"pre-symptomatic") · "weighted removal"/"bounding scenario" (not "attack"/"targeting") · "modelled
conductance" (never bare "conductance") · "imposed as a boundary condition" (not "driven by").

**Strongest evidence to foreground**
The subset table (Part I S1) · the C-exclusion strengthening (S2) · the size-control table (S3) ·
the restricted-grid partials (Mo2) · the attack-gap size-cleanliness · the cavitation depression law.

**Critical citations**
Price & Weitz 2014 · Mander & Williams 2024 · Skjegstad & Kirkegaard 2025 · Mrad et al. 2021
(as *support*) · Sack et al. 2008 (PNAS) · Scoffoni et al. 2017 (*Plant Physiol*) · Matos et al. 2024
(*Ecology* e4436 for data, *New Phytol* 244:407 for the analysis) · Brodribb et al. 2016 & 2021 ·
Katifori et al. 2010 · Balios et al. 2025 · Griebel et al. 2022 · Kaga et al. 2020 · Trajanovski et al.
2013 · Tian et al. 2017 · Noblin et al. 2008.

**Critical caveats that must appear**
Crop windows, no petiole, no enforced source node · p_c is topological and independent of the hydraulic
model · the K_leaf test is the only independent physical test and it is underpowered · the sink null is
threshold-dependent and derivable from the parameterisation · quality grades are non-ordinal · ⟨k⟩ and
loop fraction are one axis · D is 73% size · no cost term in the enhancement · no phylogenetic
correction.

**De-emphasise or cut**
The pre-symptomatic window section (synthetic threshold, arbitrary time units — cut or reduce to a
labelled illustration) · the five-parasite comparison (already dropped) · β and universality ·
the Molloy–Reed agreement · the 16-digit Pearson r · the grade-artifact narrative sentence.

**Analyses that must be completed before writing**
1. ⚑ **Re-express or relabel the betweenness threshold** on the realised-removed-fraction axis.
2. ⚑ **Adopt the threshold-independent sink framing** and add the Part II tables to the Supplement.
3. ⚑ **Source-anchored connectivity variant** — `realleaf` already assigns a root by a documented rule
   (`G.graph['root_rule']`), so connectivity-to-source is computable; report it alongside GCC on at
   least a subsample. *Not yet run — requires re-running percolation.*
4. ⚑ **Localised (contiguous-disc) removal** on a subsample, following Mander & Williams' protocol.
   *Not yet run.*
5. Betweenness-vs-Kirchhoff-flux rank correlation (converts the design choice into a measured result).
6. Confirm whether common random numbers were used in the paired enhancement runs; name the bootstrap
   method and B.
7. Re-check the associations on the 99 leaves with baseline `gcc_fraction` > 0.99.
8. ~~`Resistance_2` sensitivity~~ — **DONE** (Part VI.8): both conventions give ρ ≈ 0.18, p ≈ 0.06,
   n = 112. Fold one sentence into the K_leaf paragraph. Also **confirm the manuscript's K_leaf cohort**
   (n = 93 there vs n = 112 here).

**Manuscript sections expected to change**
Title · Abstract · Introduction (novelty framing, pre-symptomatic paragraph) · Methods (attack-mode
description, criterion naming, verification-vs-validation, grade handling, sink parameterisation) ·
Results Table 2 (betweenness axis), Table 3 (sink), Table 4 (D), Table 6 (grade narrative) ·
Discussion §§ on the sink, pre-symptomatic window, novelty and validation · Conclusion · References.

**Sections that can probably remain structurally intact**
The architectural characterisation (Table 1, modulo the loop-fraction framing and the conductance
convention) · the random-vs-degree comparison · the predictor regression · the synthetic-grid section
(with restricted-range numbers added) · the enhancement section (with the subset table added and the
artefact sentence deleted) · the boundary/crop-edge check · Appendix C.
