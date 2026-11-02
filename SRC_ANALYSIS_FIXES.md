# SRC Analysis Fixes: Results and Where They Go

Prepared 10/31/26 for the "Analysis fixes" rows of `SRC_COMPLIANCE_TIMELINE.xlsx`. Every number below comes
from a script in `scripts/` and a file in `data/`; section 11 lists them. Page numbers are the **printed**
page numbers of the paper the SRC reviewed (`LS-I-DO16`, 175 pp.).

**Disclosure.** The scripts, runs and this report were done by Claude (AI) on 10/25 and 10/31 at Nicko's
instruction. Add this to the Form 2A AI-use attachment and the logbook. Where wording is suggested below,
it is a starting point: put it in your own words before it goes into the paper.

---

## At a glance

| SRC item | What the check found | Does a result change? |
|---|---|---|
| R1: verify planarity and edge crossings in the enhancement | The enhancement never checked crossings. 0.95% of the added veins (5,738 of 606,351) crossed a traced vein. Redone with a crossing filter | **No.** Same 93 improved / 12 unchanged / 0 worsened; median gain 0.0096; every enhanced p_c within 0.0009 of the old value. In the placement control, random-order closures still beat shortest-first in 26/27 (3.3× instead of 3.7×) |
| R1: claims about planarity | 61 of 105 traced leaves are already non-planar graphs. The synthetic networks are non-planar in all 43 cases | **Wording only.** p_c never reads the layout, so no threshold changes. Every "planar" claim must be corrected |
| R2 #3: results that hold whatever threshold is set | Re-read p_c at collapse criteria 10% to 90% on all 100 networks | **Mean degree: holds everywhere** (ρ .70–.87). **Fractal dimension: depends on the criterion** (n.s. at 10–20%). Degree-weighted < uniform: 100/100 up to 50%, 72/100 at 90%. The enhancement gain holds at 30/50/70% |
| R1: correct uncertainty claims | The SE numbers on p. 24 use the whole trial budget. The Table 4 CIs were capped | **Numbers change.** New SEs, seed-replicate SDs and uncapped CIs are below |
| R1: one collapse definition, one loop-fraction definition | Up to six wordings of collapse; two loop-fraction definitions | **Wording only** |
| R1: analytic vs simulated thresholds | Three places mix them | **Wording only** |
| R1: Table S3, appendix references, formulas | Table S3 had 4 wrong cells and 3 mislabelled rows. 9 formula or wording errors | **Table S3 regenerated.** Formula fixes are listed below |
| R1: hydraulic-diversion wording | The "20%" is a hemiparasite value and the 1.5 MPa gradient is illustrative. The "no embolism" result holds only at the −2.0 MPa threshold | **Wording only** |

---

## 1. Edge crossings in the reticulation enhancement

**What was wrong.** `add_loops` (`scripts/make_real_suggested.py`) adds the shortest Delaunay non-edges of
the leaf's own junction coordinates. Delaunay edges never cross each other, but nothing stopped one from
crossing a traced vein, because the traced veins are not Delaunay edges. The paper (p. 18) says the Delaunay
construction gives "a planar network". That is true of the candidate set on its own, not of the leaf plus
the new veins.

**What was run.** `scripts/run_planarity_check.py` checked all 105 enhancement-cohort networks. Each vein is
treated as a straight segment between its two junctions.

- **Crossings in the original enhancement.** 5,738 of 606,351 added veins (**0.95%**) crossed a traced vein.
  91 of the 93 networks that received veins had at least one crossing. Per network the median share was 0.66%
  (IQR 0.41–1.62%, maximum 4.18%, Bux_har).
- **Crossings already in the tracing.** The traced veins cross each other 3,455 times among 5.66 million
  segments (median 0.06% of a network's veins), in 103 of 105 networks. Part of this is the straight-line
  approximation, since real veins curve. Part is the tracing itself: as graphs, 61 of 105 traced networks
  are already non-planar (`data/graph_planarity.json`).
- **Planar graphs after enhancing.** Of the 44 traced networks that are planar graphs, the original
  enhancement turned 40 into non-planar graphs. The filtered enhancement turned 11 into non-planar graphs.
  All 11 already had straight-line crossings among their own traced veins. Strict graph planarity cannot be
  promised on such a tracing, so the defensible claim is a physical one: **no added vein crosses a traced
  vein**.

**The fix.** `planarity.add_loops_planar` takes the same candidates in the same shortest-first order and
skips any candidate that crosses a traced vein. Every network received **exactly the same number of added
veins** as before: 5,839 crossing candidates were skipped and replaced by the next shortest ones. p_c was
re-measured with the original settings (10,000 trials, same seed). The traced networks reproduced their
archived thresholds in 105 of 105 cases.

| | Archived (no crossing check) | Crossing-filtered |
|---|---|---|
| Improved / unchanged / worsened | 93 / 12 / 0 | **93 / 12 / 0** |
| Median Δp_c | 0.0095 (0.0096 from the rounded columns) | **0.0096** |
| Median relative gain | 5.49% | **5.49%** |
| Wilcoxon (93 non-zero) | W = 0, p = 5.6 × 10⁻¹⁷ | **W = 0, p = 5.6 × 10⁻¹⁷** |
| Grade A: improved / worsened (sign test) | 13 / 0 (p = 2.4 × 10⁻⁴) | **13 / 0 (p = 2.4 × 10⁻⁴)** |
| ρ(initial ⟨k⟩, Δp_c) | −.821 | **−.823** |
| Largest change in any enhanced p_c | — | **0.0009** (median 0.0001) |
| ρ between old and new gains | — | **.9997** |

Updated cells for Tables 10–12. Only these cells change; everything else stays.

- **Table 10:** grade A median Δ 0.0069 → **0.0070**; grade C 0.0083 → **0.0082**. All other cells are
  unchanged.
- **Table 11:**
  - ρ(⟨k⟩₀, Δ) −.821 → **−.823**; ρ(D, Δ) −.034 → **−.036** (p = .715).
  - Regression R² .655 → **.660**, F(2, 102) = **98.99**.
  - Semi-standardized β −0.00887 / 0.00072 → **−0.00892 / 0.00070**; fully standardized β −0.816 / 0.066
    → **−0.820 / 0.064**.
- **Table 12:**
  - Clu_ala after **0.1809**, Δ **0.0458**.
  - Ane_cal after **0.1964**, Δ **0.0419**.
  - Met_dav after **0.1982**, Δ **0.0402**.
  - Eur_jap after **0.2007**, Δ **0.0375**.
  - Chl_spi and Smi_his are unchanged.
- **Normality of Δp_c** (to justify Wilcoxon on p. 27): Shapiro–Wilk W = 0.893, p = 4.0 × 10⁻⁷.

**Important: "none worsened" is guaranteed by how the comparison is built.** The same seed and the same
junctions mean identical removals in both versions. The enhanced network has every original vein plus
more, so its largest component can never be smaller. Say this on p. 41 and p. 62, and rest the claim on the
size of the gain, not on the zero count.

### 1b. Placement control without crossings (Table 16, Figure 14, pp. 21–22, 48–49, 69)

`scripts/run_planar_edge_control.py` re-ran the 27-network control with the original settings (2,400 trials
per arm, seed 1). The traced networks reproduced their archived thresholds in 27 of 27.

How often the original arms crossed a traced vein:
- **Delaunay, shortest first:** 1.11% of added veins.
- **Delaunay, random order:** 4.08% of added veins. This is the arm the paper calls a "planar candidate set".
- **Random node pairs:** 99.96% of added veins. This arm cannot be made non-crossing without becoming a
  different rule, so it stays as it was and should be labelled "physically impossible; crosses existing
  veins".

Both Delaunay arms were redone with the crossing filter. Each network received the same number of veins as
before.

| Placement rule | Median Δp_c (old) | **Median Δp_c (crossing-filtered)** | Improved | Median difference from shortest-first | W, p (exact) |
|---|---|---|---|---|---|
| Delaunay, shortest first | +0.0117 | **+0.0119** | 27/27 | reference | — |
| Delaunay, random order | +0.0436 | **+0.0399** | 27/27 | **−0.0216** (old −0.0260) | W = 0, p = 3.0 × 10⁻⁸ (26 untied; Mel_maj tied) |
| Random node pairs (not filtered; crosses veins) | +0.1404 | +0.1404 | 27/27 | −0.1206 | unchanged |

**The result holds.** Random-order closures from the same pool still give more tolerance than shortest-first
closures in 26 of 27 networks (one tie). The ratio of the medians falls from **3.7× to 3.3×**. The same
holds at the 30% and 70% criteria: 27/27 and 26/27, ratios 2.6× and 2.0×. On p. 69, "3.7 times" becomes
"3.3 times". Keep "12.0 times" for random pairs, but state that those veins cross existing veins, so they are
a reference a leaf cannot reach.

Wording fixes:
- **p. 21:** "which removes the shortest first heuristic while keeping the planar candidate set intact" →
  "which removes the shortest-first rule but keeps the same Delaunay candidates, again skipping any that
  cross a traced vein".
- **p. 21:** "which removes planarity and locality as well" → "which ignores geometry: almost every vein it
  adds (99.96%) crosses an existing vein, so it is a reference that a leaf cannot build".

---

## 2. Does the result depend on the 50% collapse criterion? (R2, compliance item 3)

**What was run.** `scripts/run_threshold_sensitivity.py` re-ran the 100-network percolation cohort with the
original settings (2,400 trials per network per mode, seed 1). It kept every trial's largest-component
size, so p_c could be read at any criterion from 10% to 90%. At 50% it reproduces the archived thresholds in
100 of 100 networks, for both removal modes. It also records a threshold-free measure: the area under the
mean largest-component curve over removal fractions 0 to 0.6.

**Figure:** `figures/threshold_sensitivity.png` (built by `scripts/make_threshold_sensitivity_figure.py`).

| Collapse criterion (largest component below…) | Median p_c, uniform | Median p_c, degree-weighted | ρ with ⟨k⟩ | ρ with D | Partial ρ, ⟨k⟩ given D | Partial ρ, D given ⟨k⟩ | Degree-weighted lower | Rank agreement with 50% |
|---|---|---|---|---|---|---|---|---|
| 10% | 0.249 | 0.210 | .70 | .05 (p = .60) | .71 | −.15 (p = .15) | 100/100 | .83 |
| 20% | 0.230 | 0.193 | .75 | .26 | .73 | .15 (p = .13) | 100/100 | .94 |
| 30% | 0.220 | 0.183 | .75 | .36 | .74 | .31 | 100/100 | .97 |
| 40% | 0.211 | 0.177 | .74 | .46 | .74 | .45 | 100/100 | .99 |
| **50% (paper)** | **0.200** | **0.169** | **.73** | **.50** | **.74** | **.50** | **100/100** | 1 |
| 60% | 0.186 | 0.157 | .75 | .50 | .75 | .51 | 99/100 | .99 |
| 70% | 0.161 | 0.136 | .80 | .46 | .81 | .49 | 97/100 | .98 |
| 80% | 0.116 | 0.100 | .87 | .38 | .87 | .39 | 97/100 | .93 |
| 90% | 0.041 | 0.039 | .84 | .30 | .83 | .22 (p = .029) | 72/100 | .75 |
| No threshold (area) | 0.186 | 0.157 | .79 | .31 | .78 | .22 (p = .029) | 100/100 | .96 |

All ρ values are significant at p < .01 unless a p is shown. Mean-degree values are all p < 10⁻¹⁵.

**What it means.**
- **Mean degree holds at every criterion** and in the threshold-free measure. This is the paper's main
  result and it does not depend on the 50% choice.
- **The fractal-dimension result does depend on the criterion.** Its unique contribution is largest at
  40–70% and is not significant at 10–20%. Report it as criterion-dependent. Remember too that D tracks
  network size (ρ = .88).
- **Degree-weighted removal is more damaging** in all 100 networks up to the 50% criterion and in 97–99 up
  to 80%. At 90% the median threshold is only 0.041, the first few steps of the removal sweep, so that row is
  poorly resolved and should not carry weight.
- **The networks keep nearly the same order** (ρ = .93–.99 with the 50% ranking for criteria 20–80%).
- **The enhancement gain holds at other criteria** (crossing-filtered version, n = 105). At 30%: 93 improved
  / 12 unchanged / 0 worsened, median Δ 0.0101. At 70%: 93/12/0, median Δ 0.0105 (8.1%). Threshold-free
  area: 93 improved, 0 worsened.
- **The other "threshold" in the study,** the −2.0 MPa cavitation threshold of the sink model, is already
  covered by Table 17 and Table S4. Cavitation onset needs a 1.1 MPa gradient at −1.0 MPa, 6.0 MPa at
  −2.0 MPa and 9.5 MPa at −3.0 MPa. State that the sink result is conditional on that setting (section 8).

---

## 3. The synthetic networks are not planar

`scripts/run_synthetic_planarity.py` produced `data/synthetic_planarity.json`.

- **Reference network (N = 1,023):**
  - 929 of its 1,022 branching-tree edges (91%) cross another tree edge; there are 1,241 crossing pairs.
  - 68 of its 251 mesh edges cross a tree edge.
  - As a graph it is non-planar.
- **All 42 grid networks are non-planar graphs:**
  - 99% of tree edges are in at least one crossing.
  - 72% of mesh edges cross a tree edge.

The cause is the generator's layout: deep branches overlap in space, and the mesh step then joins junctions
that are close in space but far apart in the tree.

**Effect on results.** None on any threshold, because the percolation code never reads coordinates. But
"calibrated planar mesh" is not a true description. The synthetic networks contain cross-connections that
a real leaf cannot form, which is one more reason they should stay a comparison set only.

**Where:** pp. 11, 32 (Figure 3b caption), 47 ("the planar mesh contains short loops"), and Appendix C
pp. 107, 109, 121, 131. Suggested replacement: "a calibrated synthetic network (N = 1,023). Its generated
layout has crossing branches, so unlike a real leaf it is not planar. This does not affect p_c, which uses
connections only."

---

## 4. Uncertainty and trial budgets

**4.1 The standard error on p. 24 (and Appendix C pp. 134–135) is computed wrongly.** The formula defines
N_trials as "the number of trials at that removal fraction". The numbers 0.0102 and 0.0050 instead use the
whole budget, 2,400 and 10,000. Each point on the collapse curve uses 2,400/40 = **60** trials (cohort) or
10,000/40 = **250** (enhancement). At P = 0.5 the SE of one point is therefore **0.065** and **0.032**.

**4.2 The uncertainty of p_c itself**, measured directly by re-running with six different seeds
(`data/mc_uncertainty.json`):
- **p_c at 2,400 trials:** SD median **0.0014**, max **0.0029**. This was measured on 12 networks from the
  small, noisy half of the cohort, so it is an upper bound. The between-network SD is 0.054, so simulation
  noise is under 0.3% of the variance that the correlations analyse.
- **Enhancement gain at 10,000 trials,** with the same seed for both versions: SD median **0.0007**, max
  **0.0012**, measured on 6 networks. Every gain stayed positive in every seed.

Suggested p. 24 text: "Each point on the collapse curve is estimated from 60 trials (cohort) or 250 trials
(enhancement), so its binomial standard error at P = 0.5 is 0.065 or 0.032. The threshold uses all points
at once through the logistic fit. Re-running 12 cohort networks with six different seeds moved p_c by a
standard deviation of at most 0.003, against a between-network standard deviation of 0.054."

**4.3 Table 4 confidence intervals** (p. 34). The bootstrap resampled at most 50,000 trials per replicate,
so the intervals were 1.5 to 4.7 times too wide. They were re-done with all trials resampled
(`data/uncapped_ci.json`, same seed, point estimates identical):

| Removal | Trials | p_c | Old CI | **New 95% CI** |
|---|---|---|---|---|
| Uniform | 1,000,000 | 0.2711 | [0.2700, 0.2720] | **[0.2708, 0.2712]** |
| Degree-weighted | 100,000 | 0.2023 | [0.2014, 0.2033] | **[0.2017, 0.2030]** |
| Betweenness-weighted | 100,000 | 0.1889 | [0.1879, 0.1902] | **[0.1882, 0.1897]** |

Delete the cap paragraph on pp. 24–25 ("Because of the 50,000 trial cap … upper bounds on the true width").
Replace it with: "Each interval resamples all trials. It reflects only the noise from a finite number of
trials, not the choice of logistic model or collapse rule."

**4.4 One trial-budget list.** Put this once in the Methods (p. 23) and refer to it elsewhere:

| Analysis | Trials | Per removal fraction |
|---|---|---|
| Percolation cohort, n = 100 | 2,400 per network per removal mode | 40 fractions × 60 |
| Enhancement, n = 105 | 10,000 per network per version | 40 × 250 |
| Placement control, n = 27 | 2,400 per network per arm | 40 × 60 |
| Synthetic reference network | 1,000,000 uniform; 100,000 per weighted mode | 50 × 20,000; 50 × 2,000 |
| Fixed-architecture size sweep | 40,000 per size | — |
| Coupled sink surface | 6,000 per cell | — |
| Collapse-criterion check | the cohort's own trials, read at 9 criteria | 40 × 60 |

Also fix:
- **p. 19:** "Betweenness-targeted removal is examined only on the subset of smaller networks." It was run
  only on the synthetic reference network, as p. 55 says.
- **p. 20 and p. 30:** say "2,400 trials per network per removal mode (60 at each of 40 removal fractions)".
- **p. 34 note:** "Mdn N = 15,404" is the median of the 112 characterised networks. The cohort whose
  thresholds are compared has median N = 17,924.

---

## 5. One definition each

**Collapse.** Suggested sentence for the "Giant Connected Component" paragraph (p. 17), used everywhere
else in short form:

> A network is counted as collapsed in a trial when its largest connected component has fewer than half of
> the network's original junctions. The critical removed fraction, p_c, is the fraction of junctions removed
> at which half of the trials end in collapse, read from a logistic fit. p_c describes connectivity only;
> it is not a hydraulic measurement.

Short form: "the removed fraction at which the largest component falls below half its original size in half
of the trials".

| Page | Current wording | Change to |
|---|---|---|
| 1 (Abstract) | "before hydraulic continuity fails" | "before the vein network breaks apart", and add the criterion (R1's abstract comment) |
| 17 | "no macroscopic connected cluster spans the network … its loss is interpreted as the loss of whole leaf hydraulic continuity. Once the network fragments, water can no longer move across the lamina." | The definition sentence above. Keep the hydraulic meaning as an interpretation, not a fact. |
| 20 | "the network is tested for a spanning connected cluster (Newman & Ziff, 2001)" | "the size of the largest connected component is recorded". p. 23 itself says the half-size rule was used *instead of* a spanning criterion. |
| 23 | "the probability of hydraulic collapse" | "the probability of collapse" |
| 30 | "fraction of nodes removed at GCC collapse" | the short form above |
| 47–48 | three different "thresholds" | label each one; see section 6 |

Also on p. 17: the largest component is the largest anywhere in the leaf. It is not checked for a
connection to the petiole, which no traced window has. Table 17's source-anchored row shows the choice
changes little (ρ = .912).

**Loop fraction.** The Methods (pp. 16–17) define it as "the number of loop type veins divided by the total
number of edges", using the dataset's own vein labels. Every number in the paper actually uses the
**non-bridge fraction**, which the Table 1 note (p. 31) gives correctly. Suggested p. 17 sentence:

> Loop fraction is the share of vein segments that lie on at least one closed loop, (E − B)/E, where B is
> the number of bridges (segments whose removal splits the network). The dataset's own loop-vein labels give
> a slightly different value and are not used.

On p. 61, the identity must read (E − N + c)/E = 1 − 2/⟨k⟩ + c/E. It holds for the **cycle-rank**
fraction, not for the non-bridge fraction (mean difference 0.559, n = 100, Table S3).

---

## 6. Analytic predictions vs simulated thresholds

| Page | Problem | Fix |
|---|---|---|
| 47 | "The empirical connectivity threshold located on the N = 8,191 mesh (f_c = 0.524)" | "The simulated point at which the giant component disappears on the synthetic N = 8,191 network (f_c = 0.524)". It is simulated, not empirical, and it is a different criterion from p_c. The Molloy–Reed value (0.531) is an analytic prediction for that network. |
| 48 (Figure 13 note) | p_c = 0.271 and f_c = 0.525 placed side by side | Label both: "p_c (largest component below half) and f_c (largest component disappears), both simulated". |
| 65 | the response-surface value 0.2595 compared with 0.1998 | 0.2595 is predicted from the synthetic-grid regression; 0.1998 is the simulated median of the real cohort. Say so. |
| 160 (Table S5) | the Molloy–Reed f_c sits in a "Measured" column next to a simulated p_c | Add the note: "Molloy–Reed f_c is an analytic prediction of where the giant component disappears. Compare it with the simulated f_c, not with p_c." Cite Table S5 on p. 47. |

---

## 7. Formula and wording errors

| Page | Current | Correct |
|---|---|---|
| 19 | "each surviving junction is retained independently with probability ρ" | each junction is **removed** with probability ρ (kept with probability 1 − ρ) |
| 21 | "Adding any set of edges to a sparse planar graph raises site percolation tolerance" | adding edges **cannot lower** it, for any graph, because the largest component can only grow |
| 22 | "A complete Delaunay triangulation of these node sets has a mean degree near 6.1" | A triangulation cannot exceed a mean degree of 6. The 6.1 is the traced network **plus** every Delaunay candidate (median 6.09, range 6.00–6.98), which is above 6 precisely because some candidates cross traced veins. |
| 22 | "uses only about 12 to 17 per cent of the available closures" | 0.1% to 16.6% (median 8.9%) across the 93 enhanced networks |
| 23 | N_trials "= total number of Monte Carlo trials" | the number of trials **at that removal fraction** (60 or 250) |
| 24 | SE values 0.0102 and 0.0050 | 0.065 and 0.032 (section 4.1) |
| 25 | W = Σ sgn(dᵢ)Rᵢ | the reported W is the smaller of the positive-rank sum and the negative-rank sum, T = min(W⁺, W⁻) (W = 0 means every non-zero difference had the same sign) |
| 26 | partial r formula with no mention of ranks | the same formula applied to **ranks** (partial Spearman) |
| 27 | "Wilcoxon … or a paired t-test where the differences are approximately normal", plus the t formula | Remove the t-test, which was never run. Shapiro–Wilk rejects normality of Δp_c (W = 0.893, p = 4.0 × 10⁻⁷), so only Wilcoxon was used. |
| 29 | p = 2·P(X ≥ k) | p = min(1, 2·P(X ≥ max(k, m − k))) |
| 37 (Table 6 note) | Shapiro–Wilk "rejected normality … for both connectivity predictors" | It rejected normality for p_c, mean degree and fractal dimension, but **not** for loop fraction (p = .089). |
| 41, 62 | "lowered it in none", "Table 10 shows that 93 networks improved" | Table 10 shows percentages only, so give the counts in the text. Add that a decrease is impossible by construction (section 1). |
| 65 | "absence of networks becoming worse reflects optimisation toward a single objective" | it reflects the construction (section 1) |
| 72 | stray text "Opti" | delete |

---

## 8. Hydraulic-diversion wording

**The facts:**
- K_h = 0.0392 is a multiplier on each attached junction's own conductance, applied over a 10-junction
  patch.
- It was solved so that the sink takes **20% of the water entering the modelled network** at an assumed
  1.5 MPa host-to-parasite gradient.
- The 20% comes from a **hemiparasite**, *Rhinanthus minor* on barley (Jiang et al., 2003), where the
  parasite took about 20% of the host's root water uptake. No holoparasite value exists.
- The 1.5 MPa gradient is illustrative; no primary source gives it.
- "No vessel embolised" holds at the model's stipulated **−2.0 MPa** cavitation threshold. At −1.0 MPa the
  calibrated sink already embolises one vessel.
- The parasite itself lowers the minimum potential by only 0.026 MPa, which is 2.6% of the 1.0 MPa gap set
  between the leaf boundary (−1.0 MPa) and the cavitation threshold.

Suggested abstract sentence: "A haustorial sink set to take 20% of the network's water inflow (a
hemiparasite value) at an assumed 1.5 MPa gradient caused no embolism between 0 and 3.0 MPa at the model's
−2.0 MPa cavitation threshold."

| Page | Change |
|---|---|
| 1, 71 | as above; keep the null conditional on the −2.0 MPa setting |
| 20–21 | "the fraction of host water reported in parasitic associations at around 18–20% (Jiang et al., 2003)" → "about 20% of the host's water uptake, measured for the hemiparasite *Rhinanthus minor* (Jiang et al., 2003); no holoparasite value was found" |
| 35 (Table 5 note), 36 (Figure 6) | add "at the −2.0 MPa cavitation threshold" |
| 37 | "does not depend on the assumed gradient. Structural loss of connectivity, rather than the hydraulic drain itself, governs the collapse." → it does depend on the cavitation threshold (Table 17); say the sink and the percolation model were **analysed separately**, not that one governs the other |
| 45 (Figure 11 note) | "least reticulate network" → "the network with the lowest fractal dimension (D = 1.23)", because ⟨k⟩ was held at 2.49 in all four. "⟨k⟩ held at 2.4888" → "four calibrated networks (N = 1,023 each, ⟨k⟩ = 2.49)" |
| 66 | "2.6% of the reported 0.978 margin" → "2.6% of the 1.0 MPa gap set between the leaf boundary and the cavitation threshold" |
| 67 | "or a sink strength more than 256 times the calibrated value" → "no sink strength up to 256 times the calibrated value reached −2.0 MPa (the minimum levelled off near −1.82 MPa)". Also "changing the potential field by only hundredths of a megapascal" → the minimum moved 0.026 MPa, but the tapped patch itself dropped 0.40 MPa |

---

## 9. Table S3 and other supplementary-table references

`SUPPLEMENTARY_TABLES.md`/`.docx` was regenerated (`scripts/make_supplementary_tables.py`,
`make_supplementary_docx.py`). Replace Table S3 (pp. 155–157) with the new version. Changes:
- **Single-lesion p:** "0.000" was a formatting bug; it now prints "> .999".
- **ρ(⟨k⟩, loop fraction):** .995 → **.994** (it had been rounded twice).
- **Cubic fit:** it was computed on 120 networks, including 8 below the size screen; it is now **n = 100**,
  R² = .987, SD = 0.015.
- **Non-bridge row:** it is now compared with the right quantity, giving **0.559**.
- **Bootstrap block:** replaced with the uncapped intervals.
- **Note:** the n for each block is now correct, and the old claim that the intervals are "never
  anti-conservative" was removed.

Main-text references to update:
- **p. 61:** "R² = 0.917, residual SD = 0.047" → "R² = 0.987, residual SD = 0.015 (n = 100)". Add that the
  Table 8 residual test used a straight-line fit (R² = 0.945, SD = 0.030).
- **p. 61:** "mean absolute departure of 0.564" → "0.559".
- **p. 54:** the Table S1 Gini and tie values describe the **synthetic** network. Say so; they are not
  measured on the empirical leaves.
- **p. 55:** "With a mean degree of 2.520 and 22.4% of edges classified as bridges" uses empirical medians to
  describe the synthetic network (⟨k⟩ = 2.489).
- **p. 56:** "the four networks in Table S1" are three traced leaves and the synthetic network. Say so.
- **p. 56:** the Table S3 IQRs come from the re-run on shared removal draws.
- **Add "(Table S3)"** after the values on p. 51 (ρ = .880), p. 54 (r = .984), p. 58 (ρ = .037/.030/.232;
  VIF 1.02) and pp. 52–53 (ρ = .179/.176).
- **Table S2** is never cited. Cite it on p. 64 (quality partitions) and p. 65 (response surface).

---

## 10. Where everything goes, page by page

**New material to add:**

| Where | What |
|---|---|
| p. 18, Reticulation Enhancement, after "added shortest first" | The crossing filter. Suggested: "Any candidate that crossed a traced vein was skipped, so no added vein crosses an existing one. This removed 5,839 candidates (under 1% of those used); the next-shortest candidates took their place, so every network received the same number of new veins." |
| p. 23, after the half-size rule | One sentence pointing to the collapse-criterion check: "To test whether results depend on the 50% rule, p_c was also read at criteria from 10% to 90% of the original size from the same trials." |
| Results, after Table 9 or as a new short subsection before Table 17 | The section 2 table (or a shortened 30/50/70% version) + `figures/threshold_sensitivity.png` + 3–4 sentences from "What it means" |
| p. 41, after Table 10 | One sentence: the crossing-filtered rerun gave the same 93/12/0 and median gain, with every threshold within 0.0009 |
| p. 49, Table 17 | Three new rows: "Collapse criterion, 10–90% of original size → ⟨k⟩ association ρ = .70–.87 at every criterion; D association n.s. at 10–20%"; "Crossing check on the enhancement → 0.95% of added veins crossed a traced vein; filtered rerun 93/12/0, max change 0.0009"; and "Crossing check on the placement control → random-order Delaunay still beats shortest-first in 26/27, 3.3× (was 3.7×)" |
| p. 48, Table 16 | Replace the two Delaunay rows with the crossing-filtered values (section 1b) and relabel the random-pair row |
| Discussion, limitations paragraph (around p. 61–62) | The fractal-dimension result depends on the collapse criterion; the synthetic networks are not planar; 61 of 105 tracings are non-planar graphs |
| Appendix C | Its generator (`scripts/_appendix_c_part*.py`) still has the old SE values (pp. 134–135), the cap paragraph (p. 135) and four "planar" sentences (pp. 107, 109, 121, 131). Hand edits to the .tex are lost on rebuild, so these must change in the scripts. Ask Claude to do it. |
| Appendix B, Table B9 | Enhanced p_c changes by at most 0.0009. Regenerate it from `data/planarity_check.csv` or add a note. |

**Corrections to existing text,** in page order:

| Page | Section reference |
|---|---|
| 1 | 5 (collapse wording + criterion), 8 (sink sentence) |
| 11 | 3 ("calibrated planar mesh") |
| 15 | "represented as a planar graph", "largely planar structure" → "a graph of junctions and vein segments; 61 of the 105 tracings contain crossing veins and are not planar graphs" |
| 16–17 | 5 (loop fraction, collapse) |
| 18 | 1 (planar claim + crossing filter) |
| 19 | 4.4 (betweenness subset), 7 (retained/removed) |
| 20 | 4.4, 5 (spanning cluster) |
| 20–21 | 8 |
| 21–22 | 1b (placement control), 7 (6.1, 12–17%, "raises") |
| 23–29 | 4.1, 4.4, 7 (formulas) |
| 30 | 4.4, 5 |
| 32 | 3 (Figure 3b caption) |
| 34 | 4.3 (Table 4 CIs), 4.4 (median N) |
| 35–37 | 7 (Table 6 note), 8 |
| 41–42 | 1 (Tables 10–12) |
| 44 | Figure 10 note: "without altering the major-vein skeleton" → "without altering existing veins (no added vein crosses one)" |
| 45 | 8 (Figure 11 note) |
| 47–48 | 3, 6 |
| 48–49 | 1b (Table 16, Figure 14), 10 (Table 17 rows) |
| 54–56 | 9 |
| 61–62 | 5, 9, 1 |
| 65 | 6, 7 |
| 66–68 | 8 |
| 69 | 1b (control ratios) |
| 70–71 | 7 (6.1), 8 |
| 72 | 7 ("Opti") |
| 155–157 | 9 (new Table S3) |

---

## 11. Files

| Script | Output | Status |
|---|---|---|
| `holoparasitic/planarity.py` | crossing counts, `add_loops_planar` | new |
| `holoparasitic/percolation.py::find_pc_multi` | p_c at several criteria from one sweep | new, reproduces `find_pc` exactly at 50% |
| `scripts/run_planarity_check.py` | `data/planarity_check.csv/.json` | done, 105/105 |
| `scripts/run_graph_planarity.py` | `data/graph_planarity.csv/.json` | done, 105/105 |
| `scripts/run_synthetic_planarity.py` | `data/synthetic_planarity.json` | done |
| `scripts/run_planar_edge_control.py` | `data/planar_edge_control.csv/.json` | done, 27/27 |
| `scripts/run_threshold_sensitivity.py` | `data/threshold_sensitivity.csv/.json` | done, 100/100 |
| `scripts/make_threshold_sensitivity_figure.py` | `figures/threshold_sensitivity.png` | done |
| `scripts/run_uncapped_ci.py` | `data/uncapped_ci.json` | done |
| `scripts/run_mc_uncertainty.py` | `data/mc_uncertainty.json` | done |
| `scripts/make_supplementary_tables.py` (edited) | `SUPPLEMENTARY_TABLES.md/.docx` | regenerated |

Interpreter: `C:\laragon\bin\python\python-3.13\python.exe`. Every run script can be re-run from the project
folder; the resumable ones skip finished networks.
