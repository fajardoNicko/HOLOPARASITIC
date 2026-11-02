# Supplementary Tables

These tables collect quantities that were computed and archived by the analysis scripts but that the main Results tables do not carry. **No table here reports a new analysis.** Each is generated directly from the archived result files by `scripts/make_supplementary_tables.py`, and each is cited from the Discussion so that no interpretive statement rests on an unnumbered value.

| Table | Content | Source file |
|---|---|---|
| S1 | Removal-weight distributions; nominal versus realised removed fraction; betweenness as a proxy for solved flux | `data/graph_metric_audit.json`, `data/final_resolution_checks.json` |
| S2 | Reticulation-enhancement result across every quality and boundary subset; grade mediation by baseline connectivity; response-surface reconciliation | `data/second_pass_audit.json`, `data/rrl_diagnostics.json`, `data/robustness_ceiling_summary.json` |
| S3 | Predictor collinearity, size control, criterion and locality dispersion, crop-edge detail, bootstrap interval widths | `data/rrl_diagnostics.json`, `data/second_pass_audit.json`, `data/criterion_and_locality.json`, `data/boundary_check.json`, `data/final_resolution_checks.json` |
| S4 | Full haustorial-sink sensitivity: cavitation onset by threshold, by sink strength, and by host operating potential; haustorial-density surface | `data/cavitation_sensitivity.json`, `data/sink_surface.json` |
| S5 | Both synthetic size sweeps with the unpinned architectural descriptors; generating-function comparisons | `data/finite_size_fixedD.json`, `data/scaling_mesh.json`, `data/robustness.json` |

---

**Table S1**

*Removal-Weight Distributions, the Nominal Versus Realised Removal Axis, and Betweenness as a Proxy for Solved Flux*

| Weight | Gini | Max (× mean) | Distinct values | Largest tied group | Realised fraction at nominal ρ = 0.1889 | at 0.2023 |
|---|---:|---:|---:|---:|---:|---:|
| Degree | 0.274 | 2.4 | 6 | 32.1% | 0.1889 | 0.2023 |
| Betweenness | 0.754 | 29.4 | 619 | 32.1% | 0.1498 | 0.1578 |

| Network | N | Free nodes | ρ(betweenness, flux) | ρ(degree, flux) | ρ(betweenness, degree) | Flux Gini |
|---|---:|---:|---:|---:|---:|---:|
| synthetic hero mesh (config.DEFAULT_NETWORK) | 1,023 | 510 | .511 | .178 | .329 | 0.8909 |
| real leaf Tri_lan | 1,436 | 1,407 | .184 | .078 | .119 | 0.8898 |
| real leaf Tod_bar | 2,129 | 1,591 | .629 | .342 | .445 | 0.9308 |
| real leaf Tas_lan | 2,192 | 1,670 | .495 | .255 | .349 | 0.9851 |

*Note.* Removal is **weighted stochastic**: each node is removed with probability proportional to its centrality, clipped at unity, following the degree-dependent occupation formalism of Callaway et al. (2000). It is not rank-ordered deletion of the top-*k* nodes. Because the clip binds for heavy-tailed weights, the nominal control parameter overstates the realised removed fraction for betweenness but not for degree, which is why Table 4 reports both axes. Weight statistics are computed on the synthetic reference network (*N* = 1,023). Flux is the solved Kirchhoff through-flow at each node; all flux correlations have *p* < .001 except ρ(degree, flux) on *Tri_lan* (*p* = .004).

---

**Table S2**

*Reticulation Enhancement Across Every Quality and Boundary Subset, Grade Mediation, and the Response-Surface Reconciliation*

| Subset | n | Improved | Unchanged | Worsened | Mdn Δp_c | Mdn baseline ⟨k⟩ | Wilcoxon (Pratt) p | Sign test p |
|---|---:|---:|---:|---:|---:|---:|---|---|
| Full enhancement cohort | 105 | 93 | 12 | **0** | 0.0095 | 2.512 | < .001 | < .001 |
| Excluding every network with a C flag | 91 | 79 | 12 | **0** | 0.0108 | 2.520 | < .001 | < .001 |
| Excluding every network with a D flag | 49 | 40 | 9 | **0** | 0.0070 | 2.548 | < .001 | < .001 |
| A or B only, no C and no D | 40 | 31 | 9 | **0** | 0.0079 | 2.571 | < .001 | < .001 |
| Leading grade A only | 21 | 13 | 8 | **0** | 0.0069 | 2.665 | < .001 | < .001 |
| Inside both crop-edge tolerances | 102 | 92 | 10 | **0** | 0.00995 | 2.510 | < .001 | < .001 |
| Baseline GCC fraction > .99 | 103 | 91 | 12 | **0** | 0.0094 | — | — | < .001 |

| Grade | n | Mdn raw Δp_c | Mdn baseline ⟨k⟩ | Mdn Δp_c residualised on baseline ⟨k⟩ |
|---|---:|---:|---:|---:|
| A | 21 | 0.0069 | 2.6653 | +0.00201 |
| B | 46 | 0.0137 | 2.4715 | −0.00019 |
| C | 10 | 0.0083 | 2.5061 | −0.00522 |
| D | 28 | 0.0086 | 2.5337 | −0.00062 |

| Comparison | Statistic | Value |
|---|---|---|
| Δp_c by grade, raw | Kruskal–Wallis H | 6.981, *p* = .072 |
| Δp_c by grade, residualised on baseline ⟨k⟩ | Kruskal–Wallis H | 19.266, *p* < .001 |
| Δp_c on baseline ⟨k⟩ | Spearman ρ | −.821, *R*² = .651 |
| Response surface, predicted median gain | — | 0.0355 |
| Rewiring, measured median gain | — | 0.0095 |
| **Ratio, predicted : measured** | — | **3.74** |
| Response surface, predicted median p_c | — | 0.2595 |
| Measured median p_c | — | 0.1998 |
| Networks for which reticulation is the dominant modelled lever | — | 89 of 100 |
| Enhancement ceiling ⟨k⟩ (P90 of the percolation cohort) | — | 2.811 |
| Initial ⟨k⟩ of the 12 networks whose threshold did not change | — | 2.8352 – 2.9893, **all already above the ceiling** |

*Note.* Quality flags are **defect types, not severity levels**, and subsets are defined on flag *presence* rather than on the leading flag, because the archive retains only the leading flag of a comma-separated code and thereby hides 4 over-segmented and 28 damaged networks inside other leading grades. **No subset contains a single worsened network.** The residual column asks whether any grade difference survives mediation by baseline connectivity; grade A carries the largest positive residual, which is the opposite of what a tracing-recovery artefact would produce. The response surface extrapolates a between-network regression to a counterfactual architecture, whereas the rewiring measures a within-network perturbation; the two answer different questions and are not averaged.

---

**Table S3**

*Predictor Collinearity, Loop-Fraction Identities, Network-Size Control, Criterion and Locality Dispersion, Crop-Edge Detail, Bootstrap Intervals, and Resistance Convention*

| Quantity | Value |
|---|---|
| Pearson r(⟨k⟩, D), n = 100 | .148, *p* = .141 |
| Variance inflation factor | 1.02 |
| Pearson r between the uniform and degree-weighted thresholds (n = 100) | .984 |
| Spearman ρ(⟨k⟩, loop fraction), n = 100 | .994 |
| Pearson r(⟨k⟩, loop fraction), n = 100 | .972 |
| Cubic fit of loop fraction on ⟨k⟩, n = 100 | *R*² = .987, residual *SD* = 0.015 |
| Cycle-rank fraction (E − N + c)/E vs the identity 1 − 2/⟨k⟩ + c/E | max \|difference\| = 2.5e-16 across all 120 traced networks (**exact to floating point**) |
| Non-bridge loop fraction vs the cycle-rank fraction, n = 100 | mean \|difference\| = 0.559 (**not** an identity) |
| Mean non-bridge fraction ÷ mean cycle-rank fraction, n = 100 | 0.767 ÷ 0.208 = 3.69 |

| Association | Raw ρ | p | Controlling log N | p |
|---|---:|---|---:|---|
| p_c × ⟨k⟩ | .733 | < .001 | **.745** | < .001 |
| p_c × loop fraction | .727 | < .001 | **.740** | < .001 |
| p_c × D | .496 | < .001 | **.633** | < .001 |
| Uniform-minus-weighted gap × loop fraction | −.786 | < .001 | **−.789** | < .001 |
| p_c × N | .232 | = .020 | — | — |
| Gap × N | .046 | = .647 | — | — |
| N × ⟨k⟩ | .037 | = .717 | — | — |
| N × loop fraction | .030 | = .766 | — | — |
| N × D | .880 | < .001 | — | — |
| ⟨k⟩ × gap | −.793 | < .001 | — | — |
| p_c × D, residualised on log N | .577 | < .001 | — | — |

| Damage scenario | Mdn threshold | IQR | ρ with ⟨k⟩ (p) | ρ with loop fraction (p) | ρ with D (p) |
|---|---:|---|---:|---:|---:|
| Dispersed (GCC criterion, re-run on the same draws as the rows below) | 0.1998 | 0.1572 – 0.2207 | .737 (< .001) | .731 (< .001) | .501 (< .001) |
| Dispersed (source-anchored) | 0.1837 | 0.1487 – 0.2041 | .654 (< .001) | .650 (< .001) | .465 (< .001) |
| Localised, 1 disc | 0.4951 | 0.4620 – 0.5069 | .000 (> .999) | .007 (= .942) | .142 (= .159) |
| Localised, 10 discs | 0.4511 | 0.4247 – 0.4687 | .151 (= .135) | .151 (= .134) | .523 (< .001) |

| Crop-edge quantity | Value |
|---|---|
| Networks inside both tolerances | 105 of 120 |
| Median boundary-terminal fraction | 0.0087 (tolerance 0.05) |
| Median \|mean-degree shift\| | 0.0011 (tolerance 0.05) |
| Spearman ρ(log E, boundary-terminal fraction) | −.347, *p* < .001 |
| Spearman ρ(log E, \|mean-degree shift\|) | −.373, *p* < .001 |
| Failures entering the percolation cohort | 0 |
| Failures entering the enhancement cohort | 3 |

| Synthetic reference network | Trials | p_c | 95% CI, resampling capped at 50,000 trials | 95% CI, all trials resampled | Width ratio |
|---|---:|---:|---|---|---:|
| Uniform removal | 1,000,000 | 0.2711 | [0.2700, 0.2720] | [0.2708, 0.2712] | 4.70 |
| Degree-weighted removal | 100,000 | 0.2023 | [0.2014, 0.2033] | [0.2017, 0.2030] | 1.52 |
| Betweenness-weighted removal | 100,000 | 0.1889 | [0.1879, 0.1902] | [0.1882, 0.1897] | 1.57 |

| Resistance convention | Spearman ρ with measured K_leaf | p |
|---|---:|---|
| ℓ/r⁴ (reported) | .176 | = .063 |
| ℓ/r² (deposit alternative) | .179 | = .059 |
| Median ratio of the two modelled conductances | 0.064 | — |

*Note.* The graph-identity row is recomputed here directly from `data/analysis_master.csv`. The corresponding field in `data/graph_metric_audit.json` reports a mean |difference| of 0.0147 with a maximum of 1.0 for the empirical set; that field is **superseded**, because its script omitted the components correction c/E, and 61 of the 120 traced networks have more than one component (up to 4,477). With the correction applied the identity is exact to floating point, and it holds for the **cycle-rank** fraction only — not for the non-bridge loop fraction reported throughout this study, which is a different quantity. n = 100 for the collinearity, loop-fraction, association and damage-scenario rows; n = 120 for the identity row; n = 112 for the convention comparison; n = 120 for the crop-edge check. The four damage-scenario rows come from one re-run on identical removal draws, which reproduces the archived thresholds at ρ = .999; this is why the dispersed row differs slightly from Tables 3, 6 and 8. Bootstrap intervals are percentile intervals with B = 200 and seed 7, resampling individual Monte Carlo trials. The earlier intervals resampled at most 50,000 trials per replicate, which made them 1.5 to 4.7 times too wide for the runs above; the uncapped column replaces them. The intervals describe only the sampling noise of a finite number of trials, not error from the logistic model or the choice of collapse rule.

---

**Table S4**

*Full Haustorial-Sink Sensitivity: Cavitation Onset by Threshold, by Sink Strength, and by Host Operating Potential*

| Modelled cavitation threshold (MPa) | Host–parasite gradient required for the first embolised vessel (MPa) | Multiple of the calibrated K_h required at the illustrative 1.5 MPa gradient |
|---:|---:|---:|
| -1.00 | 1.1 | 1× |
| -1.10 | 2.1 | 2× |
| -1.25 | 2.7 | 4× |
| -1.50 | 4.0 | 8× |
| -1.75 | 5.0 | 32× |
| -2.00 | 6.0 | none up to 256× |
| -2.50 | 8.0 | none up to 256× |
| -3.00 | 9.5 | none up to 256× |

| Host operating potential ψ_leaf (MPa) | Min ψ without parasite | Min ψ with sink | Δψ | Vessels embolised without parasite | with sink |
|---:|---:|---:|---:|---:|---:|
| -0.5 | -0.49814 | -0.66105 | -0.16291 | 0 | 0 |
| -1.0 | -0.99627 | -1.02244 | -0.02616 | 0 | 0 |
| -1.5 | -1.49441 | -1.49447 | -0.00006 | 0 | 0 |
| -2.0 | -1.99254 | -1.99261 | -0.00007 | 0 | 0 |
| -2.5 | -2.49068 | -2.49075 | -0.00007 | 91 | 93 |

| Threshold-independent sink quantity | Value |
|---|---|
| Calibrated K_h | 0.0392 |
| Diverted fraction at the illustrative gradient | 20.0% |
| Minimum interior ψ with no parasite | -0.9963 MPa |
| Depression of the network minimum by the parasite | -0.0262 MPa |
| Stipulated ψ_leaf − ψ_cavitation gap | 1.000 MPa |
| **Parasite share of the reported margin** | **2.6%** |
| Patch depression, slope in the gradient | -0.2682 MPa per MPa |
| Patch depression, intercept | -0.00010 MPa |
| Maximum residual from linearity across 0–12 MPa | 0.017 MPa |
| Analytic per-node reservoir weight K_h/(1 + K_h) | 0.0377 |
| **Gradient required to reach −2.0 MPa** | **6.26 MPa** |

| Fractal dimension of the surface row | ⟨k⟩ held at | Smallest K_h multiple with a critical haustorial density | Critical density there |
|---:|---:|---:|---:|
| 1.2282 | 2.4927 | 2× | 0.9384 |
| 1.3908 | 2.4927 | 3× | 0.8841 |
| 1.4980 | 2.4927 | 3× | 0.7778 |
| 1.5435 | 2.4907 | 3× | 0.8396 |

*Note.* All values are computed on the cohort-calibrated synthetic mesh (*N* = 1,023). The haustorial-density surface reports the fraction of nodes **bearing a haustorium** at which the collapse criterion is met under the coupled hydraulic model, which is a different quantity from the removed-node fraction of Tables 3, 4 and 9 and is not comparable with those values. Mean degree is held essentially constant across the surface, so the row that first develops a threshold is the one with the **lowest fractal dimension**, not the least reticulate one. At the calibrated sink strength no row has a threshold at any density. The linearity of the patch depression is an arithmetic consequence of specifying K_h *relative* to each node's own incident conductance, which fixes the reservoir's weight at K_h/(1 + K_h) per node independently of the network; it is not an emergent property of venation topology.

---

**Table S5**

*Both Synthetic Size Sweeps With Their Unpinned Architectural Descriptors, and the Generating-Function Comparisons*

| Sweep | N | D | ⟨k⟩ | Loop fraction | Bridge fraction | Terminal fraction | p_c |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pinned D and ⟨k⟩ | 1,023 | 1.3847 | 2.4888 | 0.6921 | 0.3079 | 0.3069 | 0.2701 |
| Pinned D and ⟨k⟩ | 2,047 | 1.3906 | 2.4875 | 0.6813 | 0.3187 | 0.3102 | 0.2295 |
| Pinned D and ⟨k⟩ | 4,095 | 1.3882 | 2.4928 | 0.6524 | 0.3476 | 0.3072 | 0.1271 |
| Pinned D and ⟨k⟩ | 8,191 | 1.3875 | 2.4869 | 0.5796 | 0.4204 | 0.3243 | 0.1008 |
| Pinned D and ⟨k⟩ | 16,383 | 1.3836 | 2.4877 | 0.5610 | 0.4390 | 0.2952 | 0.0772 |
| Confounded (depth sets both) | 511 | 1.267 | — | — | — | — | 0.2531 |
| Confounded (depth sets both) | 1,023 | 1.387 | — | — | — | — | 0.2719 |
| Confounded (depth sets both) | 2,047 | 1.511 | — | — | — | — | 0.2753 |
| Confounded (depth sets both) | 4,095 | 1.638 | — | — | — | — | 0.2848 |
| Confounded (depth sets both) | 8,191 | 1.741 | — | — | — | — | 0.2857 |

| Drift audit of the pinned sweep | Value |
|---|---|
| D spread achieved across the sweep | 0.0070 |
| ⟨k⟩ spread achieved | 0.0059 |
| **Loop-fraction drift** | **0.131** (0.692 → 0.561) |
| Pearson r(loop fraction, p_c) across the sweep | .913 |
| p_c spread | 0.1929 |
| Slope of p_c per doubling of N | -0.0514 |

| Generating-function comparison | Network | κ = ⟨k²⟩/⟨k⟩ | Molloy–Reed f_c | Measured |
|---|---|---:|---:|---:|
| Confounded sweep, largest network | N = 8,191 | 3.131 | 0.531 | f_c = 0.524 |
| Separately generated mesh | N = 4,095 | 3.119 | 0.5281 | p_c = 0.2852 |

| Empirical cohort, for contrast | ρ with N | p |
|---|---:|---|
| p_c | .232 | = .020 |
| ⟨k⟩ | .037 | = .717 |
| Loop fraction | .030 | = .766 |
| D | .880 | < .001 |

*Note.* **No finite-size claim — convergence or divergence — is made from either sweep.** Pinning D and ⟨k⟩ does not pin the architecture: loop fraction, itself one of this study's predictors of the threshold, drifts by 0.131 across the size range and correlates with p_c at r = .913 over the five sweep points, so size and reticulation cannot be separated with five points and two moving variables. The confounded sweep raises N and D together and is reported only to show why it cannot be read either. f_c is the removal fraction at which the giant component vanishes; p_c is the fraction at which it falls below half its undamaged size at *P* = .50. The two are different criteria on the same network and produce different numbers, which is why the N = 8,191 and N = 4,095 rows are not comparable with one another. Molloy–Reed assumes a locally tree-like graph while a planar mesh is dense in short loops, so the correspondence is qualitative and establishes no universality class. The empirical cohort's threshold rises **weakly with** size, the opposite sign to the pinned sweep, so the synthetic behaviour does not propagate into the reported results.

