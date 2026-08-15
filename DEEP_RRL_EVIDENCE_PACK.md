# Deep RRL + Results-Mining Evidence Pack

**Paper:** *Percolation Analysis of Pre-Symptomatic Vascular Collapse in Host Xylem Networks under Holoparasitic Haustorial Sink Stress*
(alt framing: *Vein Reticulation as a Host-Resistance Trait Against Pre-Symptomatic Hydraulic Collapse Under Parasite-Induced Water Stress*)

**Generated 2026-08-15** by a ten-agent literature-and-evidence mining pass, plus eight new diagnostics computed directly against `data/analysis_master.csv` and `data/synthetic_grid_pc.csv`.

**How to use this file.** Parts I–X follow the brief. Full evidence cards for every source live in `rrl/A…J`, one file per domain; this file carries the synthesis, the matrix, the results mining, and everything that required cross-domain reasoning. Where a claim below is marked **[computed]** it was calculated here from the project archive, not taken from literature.

**Reproducing the [computed] numbers.** `python scripts/run_rrl_diagnostics.py` → `data/rrl_diagnostics.json`. Reads only `data/analysis_master.csv` and `data/synthetic_grid_pc.csv`; no simulation is re-run.

**Access discipline.** Every card in `rrl/` states FULL TEXT READ / ABSTRACT ONLY / PUBLISHER RECORD ONLY. Nothing marked abstract-level should be quoted verbatim or cited for a specific number. Several DOIs are flagged for verification before the reference list is finalised — see Part VIII.

---

# PART 0 — NEW DIAGNOSTICS COMPUTED FOR THIS PASS

Three independent agents converged on the same request: *check whether the empirical thresholds are confounded by network size, and whether the reticulation gain is a tracing artefact.* Both were computable from the archive. Both were run. **One result defends the paper, one changes what it must disclose, and one refutes an objection the paper was about to concede.**

### 0.1 The size confound — mostly clean, with one serious exception **[computed]**

Across the 100-leaf percolation cohort (N = 1,436 to 300,633 nodes):

| Spearman with network size N | ρ | p |
|---|---|---|
| p_c (random) | **+0.232** | 0.020 |
| p_c (degree-targeted) | +0.165 | 0.101 |
| mean degree ⟨k⟩ | +0.037 | 0.717 |
| loop fraction | +0.030 | 0.766 |
| **fractal dimension D** | **+0.880** | **1.6 × 10⁻³³** |

**Reading.** (a) The empirical p_c–N association is weak and **positive**, i.e. *opposite in sign* to the fixed-architecture synthetic sweep where p_c falls with N. The finite-size artefact does not propagate into the empirical cohort in the direction feared; say so explicitly and the finite-size limitation stops contaminating every empirical claim. (b) ⟨k⟩ and loop fraction are essentially size-independent — the connectivity result is not a window-size effect. (c) **Box-counting D is rank-correlated with network size at ρ = 0.880.** In the synthetic grid the same coupling is ρ = 0.990 **[computed]**, because the D axis was realised by varying generations. D is therefore substantially a size readout in *both* cohorts. This must be disclosed; it is the single most important new caveat in this pack.

Partial Spearman with p_c (random), controlling log₁₀N:

| Predictor | marginal ρ | partial ρ (| log N) |
|---|---|---|
| ⟨k⟩ | 0.733 | **+0.745** |
| loop fraction | 0.727 | **+0.740** |
| D | 0.496 | **+0.633** |

All three *strengthen* under size control. The connectivity result is robust; D's association is real but its raw value is entangled with size in a way the paper has not previously stated.

### 0.2 The reticulation gain is NOT a tracing artefact — the objection is refutable **[computed]**

The adversarial pass flagged as *Major*: "the benefit is largest in the worst tracings (grade B Δ = 0.0137, 96% improved) and weakest in the clean ones (grade A Δ = 0.0069, 62% improved, n = 21) — the signature of measurement recovery, and on the clean subset 62% is a coin flip." **Both halves are wrong, and the data say so.**

| grade | n | median Δp_c | median baseline ⟨k⟩ | % improved | residual Δ after conditioning on baseline ⟨k⟩ |
|---|---|---|---|---|---|
| A | 21 | 0.0069 | **2.665** | 61.9 | **+0.0020** (highest) |
| B | 46 | 0.0137 | 2.472 | 95.7 | −0.0002 |
| C | 10 | 0.0082 | 2.506 | 100.0 | −0.0052 |
| D | 28 | 0.0086 | 2.534 | 92.9 | −0.0006 |

- Grade A leaves start at the **highest** baseline connectivity (median ⟨k⟩ 2.665 vs 2.472 for grade B), and gain vs baseline ⟨k⟩ is Spearman **−0.821**. The smaller grade-A gain is exactly what diminishing returns predicts.
- After conditioning Δp_c on baseline ⟨k⟩, **grade A has the largest positive residual of any grade.** The artefact hypothesis predicts the opposite sign.
- Grade A: **13 improved, 8 unchanged, 0 worsened.** The "62%" is 13/21 including exact zeros. Among leaves that changed at all, **13 of 13 improved**. Sign test p = 2.4 × 10⁻⁴; Wilcoxon p = 1.5 × 10⁻³ (Pratt p = 4.7 × 10⁻⁴). **The clean subset is significant, not a coin flip.**
- Residual differences across grades remain detectable (Kruskal–Wallis H = 19.3, p = 2 × 10⁻⁴) but run *in the paper's favour*.

**Write this up.** It converts a Major concession into a robustness result, and it is three sentences.

### 0.3 Predictor orthogonality — the 0.994 problem is confined to one table **[computed]**

- Pearson r(⟨k⟩, D) = **0.148** → **VIF = 1.022**. The multiple regression is not collinearity-affected. (This confirms the value back-solved analytically from the reported betas in `rrl/I`.)
- Spearman ρ(⟨k⟩, loop fraction) = **0.9945**; Pearson r = 0.972.
- For a connected planar graph, loop fraction ≈ 1 − 2/⟨k⟩ up to an O(1/V) correction, so **0.9945 is the finite-V residual of a graph identity, not an empirical coincidence.** Stating this converts an apparent inflation of evidence into a demonstration of command of the material. The paper's existing residual test (loop | ⟨k⟩ vs p_c: ρ = −0.088, p = 0.386) is the correct analysis and belongs in the main text, not an appendix.

### 0.4 The synthetic grid survives truncation to the empirical range **[computed]**

| Grid | n | β(⟨k⟩) | β(D) | dominance | R² | F |
|---|---|---|---|---|---|---|
| Full (⟨k⟩ ≤ 4.00) | 42 | 0.934 | 0.067 | 13.9 : 1 | 0.887 | 152.6 |
| **⟨k⟩ ≤ 2.99 (empirical max)** | **24** | **0.981** | **0.125** | **7.8 : 1** | **0.940** | **164.1** |
| ⟨k⟩ ≤ 2.60 | 14 | 0.991 | 0.074 | 13.3 : 1 | 0.998 | 2305.0 |

The extrapolation objection is answerable: restricted to the range real leaves occupy, the fit is **stronger** (R² 0.940) and connectivity still dominates by ~8:1. Report the restricted numbers as primary and the full grid as the extended range. 18 of 42 grid cells lie above the empirical maximum.

### 0.5 Missing effect sizes — all computable with no new simulation **[computed]**

| Comparison | test | effect size |
|---|---|---|
| random vs degree-targeted (n = 100) | W = 0, p = 3.9 × 10⁻¹⁸ | **matched-pairs rank-biserial r = +1.00**; 100/100 leaves; median difference 0.0305 |
| enhancement (n = 105) | Pratt W = 0, **p = 1.7 × 10⁻¹⁸**; Wilcoxon on 93 non-zero W = 0, p = 5.6 × 10⁻¹⁷ | r_rb ≈ +0.99; 93 improved / 12 unchanged / **0 worsened**; median Δ = 0.0095 |
| loop-fraction Q1 vs Q4 (25 vs 25) | U = 4, p = 2.3 × 10⁻⁹ | **Cliff's δ = +0.987**; medians 0.158 → 0.231 |

Always report the effect size *next to* the median difference, never instead of it — r_rb = 1.00 is a directional-consistency statement, not a magnitude.

### 0.6 The K_leaf result is underpowered, not null **[computed]**

ρ = 0.187, n = 93 → Fisher-z 95% CI = **[−0.024, +0.382]**. Compatible with anything from no relationship to a moderate positive one. Report the interval and call it an underpowered check, not a failed validation. This is the single most intellectually honest change available.

### 0.7 Dataset facts verified against the local archive **[computed]**

- `is_crop`: **100 crop windows, 20 whole leaves** of 120. The crop-window caveat is confirmed and quantifiable.
- Quality codes present locally: **A, B, C, D only** (no E or F), appearing as comma-separated multi-flags (`A` 34, `D` 29, `B,D` 23, `B` 19, `C` 7, `C,D` 4, `B,C` 3, `B,C,D` 1). The `grade` column is the leading flag.
- **However**, the Dryad data dictionary defines a **six-tier A–F** scale (see `rrl/F`): A excellent; B >80% of veins correct; C fake minor veins segmented; D damage <25% of leaf area; E <80% segmented; F damage >25%. The project's working note recorded a four-tier scale with D described as "physical damage or partial lamina", which understates D and omits E/F entirely. **Correct the Methods:** state the six-tier scale, state that the retained set spans A–D, and state that the grades are **non-ordinal** — C inflates connectivity (spurious veins) while B and E deflate it, so "grade ≥ D" is not a monotone quality filter.

### 0.8 Two things the archive cannot answer — check the code before submission

1. **Were common random numbers used** across the paired baseline/enhanced enhancement runs? If yes, the median Δp_c = 0.0095 is far more precise than each arm's marginal CI implies and the "effect smaller than Monte Carlo noise" objection dies. If no, this needs fixing. (Supporting argument either way: with ±0.01 of *independent* per-leaf noise and a true effect of ~0.0095, some negative differences would appear by chance. **Zero leaves worsened.** That pattern is only consistent with low-noise paired estimation — report it as a noise-floor argument, not just a tally.)
2. **Is the bootstrap percentile or BCa, and with how many resamples?** Name it. At 10⁶ trials the half-width is ±0.001 and the choice is immaterial — say that and the objection dies.

---

# PART I — EXECUTIVE SYNTHESIS

## The ten findings that most change the paper

1. **The novelty claim is carried by exactly one clause, and that clause contradicts the results.** Every other clause of *"no prior study couples a Hagen-Poiseuille resistor network and a Kirchhoff solve to a percolation threshold on a real leaf-venation cohort, driven by a holoparasitic haustorial sink"* is individually broken — HP+Kirchhoff on real leaf venation by **Skjegstad & Kirkegaard (2025)** and by the source dataset's own ℓ/r⁴ column; percolation-on-venation framing by **Mander & Williams (2024)**, who use the word; percolation-coupled-to-xylem-hydraulics by **Mrad et al. (2021)**. Only *"holoparasitic haustorial sink"* survives — and the paper's own result is that the sink and the percolation are **decoupled**. "Driven by" asserts a link the results deny. Fix the wording (Part IX), not the results.

2. **Price & Weitz (2014) already established roughly 60% of the structural claim, on better data.** 339 whole cleared leaves, 3.93M vein segments, an explicit percolation curve in all but name, and "meshedness being the best predictor of robustness". For a planar graph meshedness is an **affine transform of ⟨k⟩**. The ⟨k⟩→p_c headline must be framed as a causally-controlled sharpening of their result on a threshold response variable, not as a discovery. They also priced reticulation at **+0.51% conductance / +3.3% volume** — the number the enhancement experiment needs and should cite rather than re-argue.

3. **Mander & Williams asked for exactly this paper, in print.** Verified verbatim: they name Ohm's-law / Hagen–Poiseuille flow modelling as the missing step and nominate Mrad et al. as the template. That is the strongest single citation available and it belongs in the Introduction's gap paragraph. But they *also* framed their analysis as percolation, so the "first percolation treatment of venation" sentence must go.

4. **Mrad et al. (2021) has been cited backwards in the project record.** It does **not** argue connectivity speeds embolism contagion — that is the hypothesis it sets up and resolves *against*: "Considering only species with vessels, increases in connectivity improve resistance to embolism spread without negatively affecting hydraulic conductivity." **It is the single best supporting citation for the paper's core claim.** Move it from the contrast list to the Introduction. **Loepfe et al. (2007) is the genuine sign reversal** — one theoretical paper at conduit scale, and it is a Moderate problem, not a Major one.

5. **The pre-symptomatic framing is the paper's most exposed premise, and the exposure is mechanistic.** Scoffoni et al. (2017, *Plant Physiology*) show that outside-xylem vulnerability explains **86–100% of K_leaf decline at turgor loss** and **75–100% through P88**, with only 5–8.5% of midrib conduits and **no minor-vein conduits** embolised above turgor loss. Avila et al. (2022) add that connectivity-mediated spread only engages once a *majority* of conduits are gas-filled. In the mild-stress window the paper calls pre-symptomatic, its chosen mechanism is the one not yet operating. **Redefine "pre-symptomatic" as whole-plant asymptomatic** (justified by vulnerability segmentation, Charrier et al. 2016) rather than "detected earlier than embolism", and drop "early warning" — no source supports it.

6. **The failed K_leaf validation is predicted by the literature — including by the source study's own authors.** Matos et al. (2024, *New Phytologist*), same 122 species: "Architecture strongly predicts leaf support and damage resistance axes but **weakly predicts efficiency and resilience axes**." Combined with Scoffoni 2017 and the 11–74% cross-species range of outside-xylem resistance (Sack, Tyree & Holbrook 2005), ρ = 0.187 is the **expected** outcome. And the axes venation *does* predict well — support and damage resistance — are exactly what a percolation threshold measures. **The paper's validation pattern matches the literature's pattern, and it is not currently making that argument.**

7. **The headline 1e-7 validation is a re-implementation check, and the deposit's data dictionary proves it.** `Resistance_4` is defined verbatim as *"predicted resistance to flow based on Poiseuille flow i.e. l/r4"* — the same convention the solver implements, computed from segmented **vein-segment width**, not conduit radius. Relabel it *verification*, not validation. The deposit also ships `Resistance_2` (ℓ/r², "effectively treats the resistance as scaling with the number of equal sized vessels in a bundle") — **the data providers deliberately offered two conventions, and a p_c sensitivity analysis across them is the cheapest possible answer to the deepest vulnerability in the model.**

8. **Betweenness > degree is a predicted result for this network class, and the paper can turn it into a mechanism.** In planar graphs degree is bounded and near-degenerate (Mou & Hayashi 2025 report uniform-RNG ⟨k⟩ ≈ 2.50, statistically indistinguishable from the cohort's 2.520), so a degree ranking is largely ties; betweenness is continuous and concentrates on the sparse backbone and on articulation points, which are abundant at low ⟨k⟩ (Tian et al. 2017). **That is why bridge fraction correlates −0.818 with the targeted threshold: the betweenness attack is structurally a bridge attack.** Caveat: no study demonstrates *initial*-ranking betweenness beating *initial*-ranking degree on a planar ⟨k⟩ ≈ 2.5 graph — Iyer et al. (2013) report the opposite ordering for initial attacks on non-planar classes. Frame it as a novel finding with a mechanism, not as literature-supported.

9. **The localised-attack objection — "a haustorium is a point disturbance, not a uniform sprinkle" — is answerable, and the answer is counter-intuitive.** Shao et al. (2015): for random-regular networks localised attack is *less* damaging than random attack, and the direction is set by degree heterogeneity. Berezin et al. (2015), the paper that established catastrophic localised attack, states it holds "in marked contrast to single networks", and that in a *single* spatially embedded network a finite hole does not propagate. **The cohort is a single planar network with degree SD 0.848 — both conditions favour the paper.** Cite Berezin *first*, because it is the paper a reviewer would cite against you.

10. **Node removal is not what a haustorium does, and the honest reframing is stronger than the current one.** Kaga et al. (2020): *Cuscuta* searching hyphae acquire xylem identity and form a continuous **xylem bridge** — topologically an edge *addition*. Jhu et al. (2022) and Kaiser et al. (2015): *Cuscuta* host defence is **cortical/hypodermal lignification outside the vascular cylinder**; in compatible interactions no host vascular occlusion is reported at all. The only positive evidence for host conducting-element occlusion is **Pérez-de-Luque et al. (2005)** (*Orobanche crenata*/legume: carbohydrate deposits filling host xylem vessel elements, plus pericycle and endodermal lignification) and **Cao et al. (2023)** (callose in host endodermis, melon/*Phelipanche*) — both **host defence responses in resistant genotypes**, and **Echevarría-Zomeño et al. (2006)** found the mechanism absent in resistant sunflower, so it is not general. Recommended reframing in Part IX.

## The biggest conceptual opportunities

- **Turn the sink null into the paper's most interesting result.** "A sink strong enough to divert ~20% of leaf flow embolises nothing across 0–3.0 MPa; structural fragmentation and hydraulic sink stress are independent failure lenses" is publishable, honest, and it *explains* the K_leaf result instead of leaving it as an embarrassment. Griebel et al. (2022) corroborate from the field: a large mistletoe depressed host trunk ψ by only 0.60 MPa and raised modelled PLC by 11 points — substantial diversion, no cascade.
- **Compute the rank correlation between node betweenness and Kirchhoff-solved node flux.** A few lines of code on data already in hand. If it is high, betweenness-targeted removal becomes a *highest-flux-first failure sequence* (Motter & Lai 2002's betweenness-as-load) rather than an implausible act of parasite agency — converting the paper's most-attacked design choice into a measured result. **Highest-value single addition identified in this entire pass.**
- **Reframe reticulation as buying the host the right to defend itself.** If the documented route to host conductance loss is the *host's own* sealing response (lignification, callose, gel occlusion at infection sites), then a highly reticulate network can afford to seal off more of itself before fragmenting, and a poorly reticulate one cannot. This makes the second title mechanistically coherent for the first time, and it explains the decoupling rather than apologising for it.
- **Report the source-anchored variant alongside GCC.** Both prior venation-robustness studies anchor to a source (Mander & Williams: "attached to the structural vein"; Price & Weitz: "connected to the root node"). Designating the highest-order vein present in each crop window as a pseudo-source and showing the two rankings agree closes a Major objection cheaply.

## The biggest weaknesses, ranked

1. **"Pre-symptomatic" is mechanistically indefensible for a xylem-topology model in the mild-stress regime** (Scoffoni 2017; Avila 2022). Redefine or retitle.
2. **The parasite mechanism does not produce node removal, and the sink is decoupled from the headline result** — yet both are in the title.
3. **The GCC criterion is source-free**, in crop windows that contain no petiole, in a codebase where root attachment is not enforced — while both prior studies in this exact domain use source-anchored connectivity, and Scoffoni et al. (2017) locate embolism initiation in the petiole and midrib the windows exclude.
4. **p_c is a fixed-fraction criterion, not a critical point**, and falls 3.5× with N at fixed architecture. **Rename it f₅₀** and reserve p_c/f_c for the vanishing threshold. This single edit removes the largest reviewer attack surface at zero cost. (Part 0.1 shows the empirical cohort is not badly confounded — say so in the same paragraph.)
5. **D is rank-correlated with N at 0.880** **[computed]** — newly discovered here, and it must be disclosed.
6. **No phylogenetic correction**, across a sample spanning ferns and angiosperms where open-dichotomous vs reticulate venation is nearly a clade label.
7. **Static rankings understate targeted vulnerability** by possibly more than the reported random–targeted gap (Wandelt et al. 2018; Almeira et al. 2020).
8. **Random removal is contradicted as a model of embolism by five independent sources** (Brodribb 2016; Pritzkow 2022; Johnson 2020; Avila 2022; Lu 2025). Name it a *null structural scenario* in Methods, not a concession in Limitations.
9. **The −2.0 MPa cavitation threshold is not general** — measured petiole P50 reaches −1.0 MPa (Charrier et al. 2016), and the model's minimum margin is 0.678 MPa. **A threshold sensitivity sweep across −1.0 to −4.0 MPa is non-negotiable**; if the null inverts near −1.0 MPa, that is a more interesting finding than the null.
10. **Two citation errors in the current reference list** (Part VIII), one of which mis-fuses two different Matos 2024 papers.

## The ten most important papers

| # | Source | Why |
|---|---|---|
| 1 | Price & Weitz 2014, *BMC Plant Biol* 14:234 | The closest antecedent; establishes the core claim on 339 whole leaves; prices reticulation |
| 2 | Mander & Williams 2024, *RSOS* 11:240086 | Percolation framing on real venation; explicitly asks for this paper's method |
| 3 | Scoffoni et al. 2017, *Plant Physiol* 173:1197 | Outside-xylem controls 86–100% of K_leaf decline — explains the failed validation *and* threatens the premise |
| 4 | Mrad et al. 2021, *New Phytol* 231:996 | The methodological passport: percolation + graph theory + xylem, and it *supports* the connectivity claim |
| 5 | Sack et al. 2008, *PNAS* 105:1567 | The only study that removes real vein elements and measures the hydraulic consequence |
| 6 | Skjegstad & Kirkegaard 2025, *PLOS Comp Biol* 21:e1013292 | HP + Kirchhoff on real leaf venation — breaks the method-novelty clause |
| 7 | Brodribb et al. 2016, *PNAS* 113:4865 | Failure is size-ordered and topology-dependent; bounds random removal, licenses targeted |
| 8 | Matos et al. 2024, *New Phytol* 244:407 | The source study's own conclusion that architecture predicts resilience weakly |
| 9 | Balios et al. 2025, *Ann Bot* 135:823 | Explicit published negative: no water-potential measurement exists for any *Cuscuta*–host interaction |
| 10 | Katifori et al. 2010, *PRL* 104:048704 | Why loops exist at all — the theoretical warrant for treating loop fraction as functional |

---

# PART II — LITERATURE BY THEME

Full cards are in the domain files. This is the map.

| Theme | File | Load-bearing sources | The one thing it settles |
|---|---|---|---|
| **A. Venation architecture, reticulation, redundancy, fractal D** | `rrl/A_venation_reticulation_fractal.md` | Price & Weitz 2014; Katifori 2010; Corson 2010; Sack et al. 2008; Ronellenfitsch 2015 & 2019; Sack & Scoffoni 2013; Blonder 2018 & 2020; Blackman 2018; Nardini 2012 | Loops are an *evolved damage-resilience solution*, not incidental — but their ecological signal runs to mechanical strength and chemical defence, so robustness may be a by-product |
| **B. Hydraulic failure, cavitation, the topology↔physiology line** | `rrl/B_hydraulic_failure_cavitation.md` | Brodribb 2021, 2016; Scoffoni 2017 ×2; Mrad 2021, 2018; Loepfe 2007; Sack 2008; Lu 2025; Charrier 2016; Avila 2022; Pritzkow 2022; Adams 2017; Urli 2013 | Contains the explicit **CAN say / CANNOT say** list and seven drop-in hedged sentence forms |
| **C. Percolation theory, network science, threshold estimation** | `rrl/C_percolation_network_science.md` | Callaway 2000; Molloy & Reed 1995; Kownacki 2008; Djordjevic 1982; Radicchi & Castellano 2016; Melnik 2011; Mizutaka & Hasegawa 2022; Newman & Ziff 2001; Hébert-Dufresne & Allard 2019; Radicchi 2015 | Tree-like theory **overstates planar removal tolerance by 1.6–1.9×** on 3-regular graphs — so f_c 0.524 and Molloy–Reed 0.531 are upper bounds, and their agreement is an internal consistency check between two tree-like calculations, not a validation |
| **D. Attack strategies and centrality** | `rrl/D_attack_strategies_centrality.md` | Albert 2000 (+erratum); Holme 2002; Iyer 2013; Wandelt 2018; Shao 2015; Berezin 2015; Mou & Hayashi 2025; Almeira 2020; Trajanovski 2013; Tian 2017; Motter & Lai 2002; Memmott 2004 | Three independent legitimations for centrality attacks with no agent: **envelope** (Trajanovski), **biological precedent** (Memmott), **load-proxy** (Motter & Lai) — the last is the strongest |
| **E. Parasitic plants, haustoria, pre-symptomatic host effects** | `rrl/E_parasitic_plants_haustoria.md` | Jiang 2003; Balios 2025; Griebel 2022; Pérez-de-Luque 2005; Shen 2007; Cochavi 2024 & 2017; Jhu 2022; Ortiz-Bustos 2017; Cao 2023; Ossa 2021; Kaiser 2015; Echevarría-Zomeño 2006 | A pre-symptomatic window is **real and quantified** (20 days to 3 decades) but its documented signature is optical, thermal, growth- and carbon-based — **not hydraulic** |
| **F. Hydraulic graph models, Murray's law, the Matos dataset** | `rrl/F_hydraulic_models_and_dataset.md` | Dryad data dictionary; Matos 2024 ×2; Xu 2021; Sperry 2005; Sack 2004, 2005, 2006; Price 2013; McCulloh 2003; Buckley 2015; Scoffoni 2011 | `Resistance_4` is ℓ/r⁴ **by definition** — the 1e-7 match is verification, not validation; end-walls carry ~54% of conduit resistivity; outside-xylem is 26–39% typically and 11–74% across species |
| **G. Novelty audit, Mander & Williams, bridge literature** | `rrl/G_novelty_and_bridge_literature.md` | Mander & Williams 2024 (full deconstruction); Price & Weitz 2014; Skjegstad 2025; Mrad 2021; Lu 2025 | Clause-by-clause break of the novelty claim + the replacement gap statement |
| **H. Adversarial attack lines** | `rrl/H_adversarial_attack_lines.md` | 15 ranked attacks, each with severity, the reviewer's own words, the best defence, and the sentence to concede | Three rated Fatal, six Major |
| **I. Statistics and simulation methodology** | `rrl/I_statistics_methodology.md` | Morris 2019; Koehler 2009; Rochon 2012; Pratt 1959; Kerby 2014; Dormann 2013; Revell 2010; Freckleton 2009; Nakagawa & Cuthill 2007; Lin 2013; Benjamini & Hochberg 1995; Cliff 1993; Mesgaran 2014; Jin & Qian 2019 | Independently reproduced **every reported statistic** from the summaries — all exposures are interpretive or presentational, none computational |
| **J. Paragraph architecture** | `rrl/J_paragraph_architecture.md` | Sentence-by-sentence dissections of Mander & Williams, Price & Weitz, Ronellenfitsch 2015, Del Ferraro 2018, Johnson 2022 | 14 paragraph patterns with worked examples in this paper's real numbers |

---

# PART III — SOURCE EVIDENCE CARDS

Full structured cards — citation, DOI, access level, study type, system, main finding, relevant variable, exact relevance, paragraph location, claim supported, strength, caveat — are in `rrl/A` through `rrl/J`. Approximately 130 sources are carded; roughly 35 were read in full text and the rest are honestly marked abstract- or record-level.

**Read these cards before writing any paragraph that cites the source.** Several carry corrections that invert how the source has been used in the manuscript so far — most importantly Mrad et al. (2021), Muraleedharan et al. (2023), and the two Matos et al. (2024) papers.

---

# PART IV — EVIDENCE MATRIX

| Claim needed | Evidence required | Best source | Finding | Strength | Limitation | Where used |
|---|---|---|---|---|---|---|
| Vascular redundancy protects transport | Direct removal + measured consequence | Sack et al. 2008 *PNAS* 105:1567 | All leaves tolerated 2°+ vein damage completely; midrib severance cost 75% ± 10% of K_leaf in pinnate leaves | Essential | Wound-healed measurements; 6 species; severing ≠ node deletion | Intro; Discussion-reticulation |
| Reticulation is an evolved damage-tolerance trait | Theory + fossil record + experiment | Katifori 2010 + Mander & Williams 2024 + Sack 2008 | Loops optimal only under damage/fluctuation; reticulate > branched over 200 Myr; minor-vein damage fully tolerated | Essential (triangulated) | None of the three measures a threshold | Intro; Discussion ¶7 |
| Connectivity metrics predict damage robustness in real leaves | Large-cohort empirical | Price & Weitz 2014 | Meshedness best predictor across 339 leaves; MST analogues lose ~all connectivity at 10% removal vs ~50% retained in reticulate | Essential | Bond not site; no threshold; **this is prior art, not support** | RRL; Discussion ¶2 |
| Reticulation is nearly free hydraulically | Cost accounting | Price & Weitz 2014 | +6.3% length, +3.3% volume, **+0.51% conductance** vs MST | Strong | Theoretical conductance, not measured | Discussion ¶7–8 |
| …but not free in fitness terms | Ecological cost | Nardini et al. 2012 *New Phytol* 196:788 | Greater hydraulic safety ↔ higher LMA, thicker walls, smaller leaf area, reduced competitiveness at high resource | Strong | Abstract only; 6 species; vein density not connectivity | Discussion ¶7 (the "0 worsened" caveat) |
| Architecture occupies a 3-way trade-off, not a maximum | Formal Pareto | Ronellenfitsch & Katifori 2019 *PRL* 123:248101 | Efficiency / cost / **percolation penalty**; 1-D Pareto front; only 14% of networks on it | Essential | 445-node simulation; **manuscript's article number 038301 is wrong** | Discussion ¶7 |
| Percolation on plant vasculature is established practice | Peer-reviewed precedent | Mrad et al. 2021 *New Phytol* 231:996 | Graph + percolation theory on *Acer* xylem; connectivity **improves** embolism resistance without conductivity cost | Essential | Stem conduits ≠ leaf junctions; full text not opened | Intro; Methods justification |
| Connectivity can instead be a liability | Counter-sign | Loepfe et al. 2007 *JTB* 247:788 | Conductivity **and** embolism vulnerability both rise with connectivity | Strong | Theoretical; conduit scale; contagion not removal | Discussion — the reconciliation paragraph |
| Loss of a connected supply path causes real damage | Empirical mechanism | Brodribb et al. 2021 *New Phytol* 232:68 | Water-column breakage in veins severs local supply and causes immediate irreversible cellular damage | Essential | Abstract only; no threshold; caused by cavitation, not node deletion | Intro — the sentence where GCC is introduced |
| Vein network topology sets the *mode* of failure | Optical imaging | Brodribb et al. 2016 *PNAS* 113:4865 | Fern venation fails catastrophically from single events; reticulate angiosperm fails in stages; nucleation always in the largest vein | Essential | Abstract only; no threshold; also bounds random removal | Discussion; Limitations |
| Random removal is a null scenario, not a model of embolism | Failure-order evidence | Brodribb 2016 + Pritzkow 2022 + Lu 2025 | Size-ordered initiation; circumferential clustering; spatial autocorrelation reduces predictive error in 47/53 leaf samples | Essential (converging) | None reports an alternative threshold | Methods (name it); Limitations |
| Targeted removal is the physiologically motivated bound | Same three + Scoffoni 2017 | Failure starts in the largest/most connected elements | Strong | Vein size ≠ node degree; state as structural surrogate | Results-interpretation |
| Centrality attacks need no agent | Framing precedent | Trajanovski 2013 + Memmott 2004 | Robustness envelope: random = expected case, targeted = pessimistic extreme; pollinators removed in strict linkage order in *Proc R Soc B* | Very strong | Methodological / ecological, not plant-hydraulic | Methods; Limitations |
| Betweenness ≈ load in a flow network | Interpretation | Motter & Lai 2002 *PRE* 66:065102 | Node load operationalised as betweenness | Moderate–strong | Cascade result requires heterogeneous load, absent here | Discussion — betweenness paragraph |
| Betweenness > degree is expected in planar graphs | Network class | Mou & Hayashi 2025 + Tian et al. 2017 | Planar degrees bounded/bell-shaped, uniform-RNG ⟨k⟩ ≈ 2.50; AP density peaks at low ⟨k⟩; AP-targeting beats degree-targeting | Strong | Their betweenness is *recalculated*; ordering only, not numbers | Discussion ¶5 |
| Localised (haustorial) damage is not worse than random here | Attack geometry | Berezin 2015 + Shao 2015 | Catastrophic localised attack requires *interdependent* networks; in a single spatially embedded network a finite hole does not propagate; RR networks more robust to localised than random | Very strong | Graph-locality ≠ plane-locality; leaf is sparser than a lattice | Limitations |
| Tree-like theory overstates planar tolerance | Quantitative anchor | Kownacki 2008 + Djordjevic 1982 | Planar Φ³ site threshold 0.7360 (removal 0.264) and honeycomb 0.6962 (removal 0.304) vs Molloy–Reed 0.500 for the same degree sequence | Strong | 3-regular, not ⟨k⟩ 2.5; arithmetic comparison is ours | Discussion — why simulated < analytic |
| Tree-like approximation fails with abundant long loops | Theory | Radicchi & Castellano 2016 *PRE* 93:030302 | Residual error driven by "loops longer than three edges"; correction matters much more for **site** than bond | Strong | Abstract only | Limitations |
| Fixed-fraction criteria are accepted practice | Precedent | Mander & Williams 2024 + Schneider 2011 + Braunstein 2016 | Collapse at a fixed retained-function level; integrated robustness indices preferred to single critical points; dismantling = components of "sub-extensive size" | Strong | No source uses P(GCC<0.5N₀)=0.5 exactly | Methods — the f₅₀ paragraph |
| Outside-xylem dominates leaf hydraulic decline | Partitioning | Scoffoni et al. 2017 *Plant Physiol* 173:1197 | K_ox explains 86–100% of K_leaf decline at TLP, 95–100% at P50; P50,Kx is 1.6 MPa more negative than P50,Kleaf | Essential | 8 species; contested by Brodribb 2016 *New Phytol* 209 | Explains K_leaf null; **also threatens the premise** |
| Static outside-xylem share | Partitioning | Sack 2004; Sack, Tyree & Holbrook 2005 | 26–36% (2 spp.); mean 39%, range **11–74%** (10 spp.) | Strong | Small species sets; 2005 numbers search-summary sourced | Discussion — K_leaf |
| Lumen-only models omit ~half the resistance | End-wall fraction | Sperry, Hacke & Wheeler 2005 *PCE* 28:456 | End walls ≈ **0.54 ± 0.07** of total conduit resistivity, near-constant across diverse taxa | Strong | Stems not leaf veins; **near-constancy is the defence** — bias largely cancels in a relative quantity | Limitations |
| Murray's law is safe in minor veins, unsafe in major | Large geometric test | Price, Knox & Brodribb 2013 *PLOS ONE* 8:e85420 | Median exponent 2.96 across 349 species / >1.5M segments, but monotone drift to area-preserving in major veins | Strong | Geometry only | Methods + Limitations |
| The source resistance column is ℓ/r⁴ by construction | Data dictionary | Dryad 10.5061/dryad.1g1jwsv36 | `Resistance_4` = "predicted resistance to flow based on Poiseuille flow i.e. l/r4"; `Resistance_2` = ℓ/r² alternative | Decisive | — | Methods; Limitations |
| Architecture predicts resilience weakly — from the source authors | Same-data contradiction | Matos et al. 2024 *New Phytol* 244:407 | "Architecture strongly predicts leaf support and damage resistance axes but weakly predicts efficiency and resilience axes" | Essential | Trait-derived resilience ≠ simulated robustness — that is the escape hatch *and* the concession | Discussion; Limitations |
| Topological metrics are valid on centimetre-scale fragments | Crop-window defence | Ronellenfitsch 2015 + Green 2014 + Blonder 2020 | Fragment ID rises 0.35 → 0.54 when topology added; modal areole size consistent across lamina (120 leaves, 80 families); 260 species phenotyped on ≤2 cm² samples | Strong | Licenses **local geometry**, not global connectivity metrics like GCC | Limitations |
| …but failure initiates in the petiole/midrib the windows exclude | Crop-window limit | Scoffoni et al. 2017 *New Phytol* 213:1076 | Kx decline driven by embolism initiating in petioles and midribs across all species | Essential | Abstract only; dehydration-specific | Limitations (mandatory) |
| A parasite diverts a large, measured fraction of host water | Sink anchor | Jiang, Jeschke & Hartung 2003 *JXB* 54:1985 | **20%** of host root water uptake; parasite stomata open day and night; ~1200 mmol m⁻²s⁻¹ | Strong | **Hemiparasite, whole-plant**; contains **no MPa value at all** | Methods (calibration) |
| No holoparasite gradient or flux value exists | Published negative | Balios et al. 2025 *Ann Bot* 135:823 | No total water potential, osmotic potential or turgor measurement reported for **any** *Cuscuta*–host interaction | Strong | Review | Methods; Limitations |
| Measured parasite-induced host ψ depression | Field measurement | Griebel et al. 2022 *Tree Physiol* 42:523 | Trunk ψ −2.75 → **−3.35 MPa** (0.60 MPa depression); parasite leaf ~0.5 MPa below host leaf; modelled PLC 21 → 32% | Strong | Hemiparasite, woody branch; PLC modelled not measured | Discussion — sink realism |
| A pre-symptomatic window is real | Time-course | Shen et al. 2007 *JXB* 58:2929 + Cochavi et al. 2017 *Front Plant Sci* 8:909 | *Cuscuta*: photosynthetic decline **~50 days** before visible withering. *Orobanche*: **~20 days**, detectable only by hyperspectral reflectance while A, gs and E are statistically unchanged | Strong | **Neither window is hydraulic**; ψ never measured in either | Intro; Discussion |
| Host defence can occlude host conducting elements | Histology | Pérez-de-Luque et al. 2005 *Ann Bot* 95:935 | Carbohydrate substance fills host xylem vessel elements at distance from the haustorium; pericycle/endodermis lignify | Moderate–strong | Root tissue; **resistant genotypes**; not general (Echevarría-Zomeño 2006 found it absent) | Discussion — the node-removal reframing |
| Haustorial connection is topologically *additive* | Anatomy | Kaga et al. 2020 *Front Plant Sci* 11:193 | Searching hyphae acquire xylem identity and form a continuous xylem bridge | Strong | — | Limitations (mandatory concession) |
| The mistletoe/parasite is the higher-resistance element | Comparative anatomy | Zhang et al. 2025 *New Phytol* 245:607 | Parasite xylem narrower, lower theoretical conductivity, higher safety | Moderate | Paywalled; **verify 118 vs 119 species pairs** | Methods — boundary condition |
| Box-counting D has documented limits | Methods critique | Muraleedharan 2023 *Flora* 304:152300 + Vishnu & Jaishanker 2023 | Area-dependent, blind to lacunarity, restricted scaling range breaking the linear-regression estimate | Strong (as limitation) | **Measures leaf shape, not venation**; *Flora* full text not opened | Limitations |
| …and here D is confounded with network size | **[computed]** | This pack, §0.1 | Spearman(N, D) = **+0.880** empirically, **+0.990** in the synthetic grid | Decisive | Partial ρ with p_c *rises* to 0.633 under size control | Limitations (mandatory, new) |
| Species are not independent data points | Comparative methods | Freckleton 2009 + Revell 2010 | Phylogenetic signal belongs in the **residuals**, not the traits; where residual λ ≈ 0, OLS beats PGLS | Very strong | Abstract only | Methods; Limitations |

---

# PART V — RESULTS MINING

Every major result, through the five layers. Numbers are the canonical ones from `data/results_verified.json` unless marked **[computed]**.

### R1 — Architectural characterisation (n = 112)
**L1 What happened.** Median ⟨k⟩ 2.520 [2.148–2.989]; D 1.676 [1.148–1.913]; loop fraction 0.776 [0.320–0.995]; GCC fraction 1.000; N 15,404 [421–300,633].
**L2 Pattern.** Sparse and near-tree-like (⟨k⟩ barely above the tree boundary of 2) yet 78% of edges lie on a cycle. Degree SD 0.848 — a narrow, **non-scale-free** distribution.
**L3 Mechanism.** Planarity bounds degree (Mou & Hayashi 2025: planar degrees rarely exceed six, bell-shaped, peaking at 2–4). This is a structural fact, not a sampling accident.
**L4 Implication.** The classical robust-yet-fragile asymmetry is a property of *heterogeneous* degree distributions (Albert et al. 2000). The cohort sits on the homogeneous limb, which **predicts** a small random-vs-targeted gap. The observed 15.7% reduction is that prediction confirmed, not a weak result. Frame it that way.
**L5 Limitation.** N spans 700× and reflects tracing-window extent, not leaf size — 100 of 120 are crop windows **[computed]**. Loop fraction ≈ 1 − 2/⟨k⟩ by a planar identity, so ⟨k⟩ and loop fraction are one axis (ρ = 0.9945 **[computed]**), not two.
**Discussion angle.** Open by establishing that leaf venation is a *spatial* network (Barthélemy 2011) and therefore that non-spatial attack-tolerance results do not transfer without argument. This one move pre-empts three reviewer objections at once.

### R2 — Attack thresholds
**L1.** Empirical median p_c: random 0.200, degree-targeted 0.169; per-leaf difference median 0.0305; 100/100 leaves targeted < random; W = 0, p = 3.9 × 10⁻¹⁸; reduction 15.7% of the median. Synthetic reference (N = 1023): random 0.271 [0.270, 0.272] at 10⁶ trials; degree 0.2023 [0.2014, 0.2033]; betweenness 0.1889 [0.1879, 0.1902] at 10⁵ trials with bootstrap.
**L2.** The **ordering** is the result — betweenness < degree < random. Unanimity across 100 leaves. **Effect sizes [computed]: rank-biserial r = +1.00, CL = 100%.**
**L3.** Degree ranking is largely ties in a planar graph, so it carries little targeting information; betweenness is continuous and concentrates on the backbone and articulation points, abundant at ⟨k⟩ 2.52 (Tian et al. 2017). **The betweenness attack is structurally a bridge attack**, which is exactly why bridge fraction correlates −0.818 with the targeted threshold.
**L4.** Where structural loss occurs matters more than how much. Real embolism is size-ordered and starts in the largest veins (Brodribb 2016; Scoffoni 2017; Lu 2025: 47/53 samples thicker-first), so the **targeted** threshold is the biologically motivated bound and the random threshold the conservative null.
**L5.** Static (initial) rankings only — recalculated attacks are more damaging by possibly more than the gap itself (Wandelt 2018; Almeira 2020). Betweenness was run on the synthetic reference only, so its generality across real leaves is unsupported by the paper's own data. No study demonstrates initial-betweenness beating initial-degree on a planar ⟨k⟩ ≈ 2.5 graph — claim it as a new finding with a mechanism, and preempt Iyer et al. (2013), who report the opposite for initial attacks on non-planar classes.
**Discussion angle.** Report the **number of nodes tied at the cut degree and the tie-breaking rule**. A reviewer who works this out will conclude the degree mode is barely targeted; reporting it yourself makes it the central mechanistic argument.

### R3 — Architectural predictors (n = 100)
**L1.** Spearman with p_c: ⟨k⟩ 0.733, loop fraction 0.727, D 0.496. Partials: ⟨k⟩|D 0.736, D|⟨k⟩ 0.503. Regression R² 0.507, F(2,97) = 49.93; standardised β 0.526 and 0.408.
**L2.** Connectivity leads, geometry follows. **[computed]** Under log-N control the partials *rise* to 0.745, 0.740, 0.633 — the relationships are not size artefacts.
**L3.** ⟨k⟩ sets the expected number of surviving neighbours per retained node, which is the quantity percolation depends on. D describes space-filling, which does not determine whether alternative routes exist (Ronellenfitsch 2015: topology and geometry are approximately orthogonal phenotype axes).
**L4.** Reticulation is a measurable robustness phenotype. This is the paper's central positive claim and it is the one the literature supports best (Price & Weitz 2014; Sack et al. 2008; Mander & Williams 2024; Mrad et al. 2021).
**L5.** R² = 0.507 means half the variance is outside the measured descriptors — report that as the paragraph's concession, not as a success. **⟨k⟩ and D are near-orthogonal (r = 0.148, VIF = 1.022) [computed]**, so the regression is clean; the 0.994 problem is confined to the descriptive correlation table and is resolved by the existing residual test (ρ = −0.088, p = 0.386) plus the planar identity.
**L5b — new and mandatory.** **D is rank-correlated with N at +0.880 [computed].** Box-counting over a larger network yields a higher D almost mechanically. D's marginal ρ = 0.496 is therefore partly a size readout, even though its partial ρ under size control is higher. Disclose both numbers.

### R4 — Synthetic causal grid (n = 42)
**L1.** ⟨k⟩ and D decoupled by design (Pearson 0.086). p_c ~ ⟨k⟩ Spearman 0.991; standardised β 0.933 vs 0.067 (13.9:1); R² 0.887, F = 152.6.
**L2.** Under intervention the empirical ordering sharpens dramatically and D nearly vanishes.
**L3.** In real leaves D covaries with connectivity *and* with size; decoupling removes the covariance and leaves connectivity carrying the effect.
**L4.** This is the paper's causal warrant — phylogeny-free, artefact-free, quality-grade-free. **Put the weight here.**
**L5.** 18 of 42 cells exceed the empirical ⟨k⟩ maximum of 2.99 (Mesgaran et al.'s Type 1 novelty). **[computed] Restricted to ⟨k⟩ ≤ 2.99 (n = 24) the fit is stronger: β 0.981 vs 0.125, R² 0.940, F = 164.1, dominance 7.8:1.** Report the restricted numbers as primary. Also note **[computed]** that D and N are coupled at ρ = 0.990 within the grid too, because the D axis was realised through generations — so the grid does not fully decouple D from size either, only from ⟨k⟩.
**Discussion angle.** The divergence between grid β(D) = 0.067 and empirical β(D) = 0.408 reads as an internal contradiction unless explained. The restricted refit plus the D–N coupling explains it. Do not leave it unaddressed.

### R5 — Reticulation enhancement (n = 105)
**L1.** ⟨k⟩ → P90 = 2.811. Median p_c 0.201 → 0.215; median Δ 0.0095; 93 improved, 12 unchanged, **0 worsened**; Pratt W = 0, p = 1.7 × 10⁻¹⁸ **[computed]**. Gain vs baseline ⟨k⟩ Spearman −0.821; vs D −0.034 (n.s.); R² 0.655.
**L2.** Monotone, near-universal in direction, strongly diminishing in return.
**L3.** Noblin et al. (2008) supply the physical mechanism: vein addition saturates once inter-vein spacing approaches the diffusive path length. Sparse networks have more to gain. This converts a statistical regularity into a mechanism and explains the 3.7× response-surface over-prediction.
**L4.** Reticulation is directionally manipulable within the model — the paper's one within-network causal manipulation.
**L5.** No cost term. Price & Weitz price the material cost (+3.3% volume, +0.51% conductance); Nardini et al. (2012) price the ecological cost (higher LMA, smaller leaves, reduced competitiveness); Ronellenfitsch & Katifori (2019) supply the formal Pareto structure. **"0 worsened" is an artefact of optimising one axis of a genuine three-way trade-off** — say so before a reviewer does.
**L5b — the artefact objection is refuted [computed].** See §0.2. Grade A has the *highest* residual gain after conditioning on baseline ⟨k⟩, starts at the highest baseline ⟨k⟩, and is significant on its own (13/13 of changed leaves improved; sign test p = 2.4 × 10⁻⁴). The quality gradient is diminishing-returns mediation, not measurement recovery.

### R6 — The haustorial sink
**L1.** K_h = 0.0392 solved for ~20% diversion at an illustrative ~1.5 MPa gradient. Minimum host ψ = −1.02 MPa vs −2.0 MPa threshold. **0 vessels embolised at all 31 gradients across 0–3.0 MPa**; minimum margin 0.678 MPa; diversion 0.2% at 0 MPa → 35.1% at 3.0 MPa. Coupled surface: no collapse at any haustorial density at calibrated K_h; threshold first appears at 2× (least reticulate) and 3× (all).
**L2.** A large flux diversion produces a small potential excursion.
**L3.** Conductance scales as r⁴, so flow is carried overwhelmingly by the widest elements; the sink draws through low-resistance paths without generating the tension failure requires. Corroborated physiologically: **no minor-vein conduits embolise above turgor loss point** (Scoffoni 2017), so a null at modest gradients is credible rather than an artefact.
**L4.** The sink and the percolation are **decoupled lenses**. Field corroboration: Griebel et al. (2022) measured only 0.60 MPa of host ψ depression and +11 points of modelled PLC from a large established mistletoe — substantial diversion, no cascade.
**L5.** Threshold-dependent and gradient-dependent. Measured petiole P50 reaches −1.0 MPa (Charrier et al. 2016) — **against that threshold, a modelled minimum of −1.02 MPa crosses, and the entire null inverts.** The minimum margin of 0.678 MPa is smaller than the between-species P50 spread. **Run and report a threshold sensitivity sweep across −1.0 to −4.0 MPa and state the value at which embolism becomes non-zero. This is non-negotiable.** Also: the −3.0 MPa parasite potential exceeds anything measured (largest measured parasite–host leaf gradient ≈ 0.5 MPa, Griebel 2022) — present the sweep as a deliberately super-empirical stress test, which *strengthens* the null.
**Discussion angle.** Use paragraph pattern P6 (Informative Null) from `rrl/J`. The single most important sentence names **what is rate-limiting instead**.

### R7 — Validation
**L1.** Solver reproduces the source `Resistance_4` column across 119 leaves / 5,668,467 veins: worst per-leaf ratio CV 1.12 × 10⁻⁷ against a 10⁻⁶ tolerance; wrong-exponent control 0.953. K_leaf vs measured whole-leaf conductance: ρ = 0.187, p = 0.073, n = 93.
**L2.** One check passes to machine precision, the other is indeterminate.
**L3.** The first is **verification** — the source column is ℓ/r⁴ by definition, so both sides assume the same physics. The second is the genuine external test, and it is dominated by a pathway the model does not represent: outside-xylem accounts for 26–39% of static resistance (11–74% across species) and 86–100% of the dynamic decline.
**L4.** The model is a **xylem-network model**, and its own source study reports that architecture predicts efficiency and resilience weakly while predicting support and damage resistance strongly — which is exactly what a percolation threshold measures. **The validation pattern matches the literature's pattern; make that argument.**
**L5.** **[computed]** ρ = 0.187, 95% CI **[−0.024, +0.382]** — underpowered, not null. Put the wrong-exponent control on the ratio scale so it is comparable, delete the 16-digit Pearson r (below the double-precision noise floor), and drop its p-value (structurally zero at n = 5.67M).
**Discussion angle.** Use pattern P7 (Failed Validation). Its non-negotiable requirement: **partition the paper's claims by dependency on the failed test.** The percolation results depend on topology and are independent of it; the sink simulation is posed in MPa and is not.

### R8 — Finite size (withdrawn)
**L1.** With D (1.384–1.391) and ⟨k⟩ (2.487–2.493) pinned, p_c falls 0.2701 → 0.2295 → 0.1271 → 0.1008 → 0.0772 across N = 1,023 → 16,383 at 40,000 trials each; loop fraction drifts 0.692 → 0.561.
**L2.** Monotone decline with an unpinned covariate that independently predicts p_c.
**L3.** Partly a property of the criterion: a fixed-*fraction* criterion is not a critical-point observable and has no reason to converge. The loop-fraction drift moves the ensemble toward the tree-like limit, where any fixed dilution leaves a sub-extensive largest component.
**L4.** No universality class, no β, no convergence claim.
**L5.** "No claim" is correct on the exponent but is an over-correction on interpretation — a five-size, 40,000-trial sweep left uninterpreted invites the question of why it was run. **[computed] The empirical p_c–N correlation is +0.232 (p = 0.020), weak and opposite in sign to the sweep, and ⟨k⟩ and loop fraction are size-independent** — so the empirical claims are not confounded. Say that, loudly, in the same paragraph.
**The standard diagnostic exists and is cheap.** Mizutaka & Hasegawa (2022): finite-size scaling of the peak of the second-largest cluster size and of the susceptibility χ(p) = Σs²n_s / Σs·n_s, made inexpensive by the Newman–Ziff union-find algorithm on the five sizes already generated. Either the pseudo-critical point converges (much stronger paper) or it does not (positive evidence for a smeared transition, citable to Hébert-Dufresne & Allard 2019 — also publishable).

### R9 — Pre-symptomatic window
**L1.** Analytic, arbitrary time units, built on the **synthetic** p_c = 0.271 and f_c = 0.524; windows 7.25 / 4.35 / 2.72 units at stipulated growth rates.
**L5.** Uses synthetic rather than empirical thresholds, is uncalibrated to any measured infestation time course, and rests on a static model with no stomatal regulation.
**Recommendation.** This is the lowest-value, highest-risk component in the paper. **Either cut it or reduce it to a clearly labelled dimensionless illustration**, and if it stays, rebuild it on the empirical median (0.200) rather than the synthetic reference. The empirical support for a window is strong and belongs in the Introduction instead: Shen et al. (2007) ~50 days for a holoparasite, Cochavi et al. (2017) ~20 days for *Orobanche* — with the honest note that both windows are optical/photosynthetic, not hydraulic.

### R10 — The headroom diagnostic
**L1.** The response surface over-predicts measured p_c (median 0.2595 vs 0.1998, r = 0.65) and its predicted reticulation gain is **3.7×** the gain measured by rewiring. Reticulation is the dominant lever for 89% of species.
**L3.** The surface is an extrapolation from *between-leaf* variation; the rewiring is a *within-leaf* perturbation. They are not two measurements of one quantity, and a discrepancy in this direction is exactly what covariate confounding predicts — which the D–N coupling **[computed]** now documents concretely.
**L4.** This makes the headroom diagnostic *evidence for* the interpretation that leaves are not sitting where a robustness-only optimiser would put them (Blonder 2018: reticulation's ecological signal runs to mechanics and defence).
**L5.** Never split the difference. Use pattern P13 and state the 3.7× ratio **before** any explanation, so the reader never computes it unaided.

---

# PART VI — PARAGRAPH ARCHITECTURE

Full library with sentence-function skeletons, worked examples in this paper's real numbers, failure modes and length guides: `rrl/J_paragraph_architecture.md`. Fourteen patterns, derived from sentence-by-sentence dissection of five papers read in full.

**The five patterns this paper cannot do without:**

| Pattern | For | The one sentence that carries it |
|---|---|---|
| **P6 Informative Null** | the sink that cavitates nothing | name **what is rate-limiting instead**, then give the flip conditions |
| **P7 Failed Validation** | K_leaf ρ = 0.187 | **partition the paper's claims by dependency on the failed test** |
| **P9 Scope Boundary** | topology vs physiology | state the interpretation the boundary forbids — and then honour it in the Abstract |
| **P13 Reconciling Disagreeing Estimates** | the 3.7× headroom gap | state the ratio **before** explaining it |
| **P14 Artifact Triage** | the quality-grade gradient | argue why the filter removes **bias**, not merely data |

**The three density rules that matter most** (eleven are in `rrl/J`):

- **Citations are not a beat.** In every paper read, standalone citation sentences appear only when a citation *does work*: converting your number into another currency, explaining an anomalous number of your own, or supplying a measurement you lack. Elsewhere agreement is fused into the claim sentence. The fixed "→ literature →" slot is what generates result-citation-result-citation prose.
- **Hedge monotonicity.** Confidence must decline across the paragraph and never re-escalate. Mander & Williams run demonstrated → likely → may also → not quantified here, in that order.
- **Density comes from resolution, not adjacency.** Two facts side by side add; a fact that *dissolves* another multiplies. The highest-information sentences read were ones where literature resolved a tension in the authors' own data.

---

# PART VII — PARAGRAPH MAP

Fifteen paragraphs, ≈3,000–3,400 words. Ordering: strongest defensible claim first, causal warrant early, concessions late, deflation last. Full table with "must NOT claim" per paragraph in `rrl/J`, Part 5.

| # | Purpose | Results | Pattern |
|---|---|---|---|
| 1 | Fix p_c (rename **f₅₀**) as a measurable per-leaf quantity | median 0.200; 100/100; synthetic 0.271 as internal contrast | P1 |
| 2 | Connectivity as leading correlate; state what the partial rules out | ρ 0.733 / 0.727, partial 0.736 (0.745 under size control **[computed]**); R² 0.507 as the concession | P2 |
| 3 | The causal warrant on a decoupled design | restricted grid β 0.981 vs 0.125, R² 0.940 **[computed]** | P5→P1 |
| 4 | Demote D to covariate signature without discarding it | ρ 0.496; 7.8:1 dominance; **D–N ρ = 0.880 [computed]** | P4 |
| 5 | Attack-mode ordering as the result; realism status per mode | 0.271 / 0.2023 / 0.1889; 0.200 → 0.169; r_rb = 1.00 | P3 |
| 6 | Loops act asymmetrically — protective, and margin-narrowing | loop × targeted +0.818; loop × attack-gap −0.786 | P2/P5 |
| 7 | The reticulation intervention | 0.201 → 0.215; 93/105; 0 worsened; Cliff δ 0.987 | P1 |
| 8 | Derive why the gain is small rather than apologise | 0.014 against the R² 0.507 spread; Noblin saturation | P12 |
| 9 | Quality-grade triage — **and refute the artefact reading** | grade A residual +0.0020, highest; 13/13 changed leaves improved **[computed]** | P14 |
| 10 | Reconcile the 3.7× surface-vs-rewiring gap | ratio stated first | P13 |
| 11 | The sink null as a constraint on mechanism space | 20% diverted; 0 embolised over 31 gradients; flip conditions incl. the −1.0 MPa threshold | P6 (+P12) |
| 12 | Draw the topology/physiology boundary and forbid the crossing | no new results | P9 |
| 13 | The failed validation, with the dependency partition | ρ 0.187, CI [−0.024, +0.382] **[computed]** | P7 |
| 14 | Assumption audit, ranked by risk | HP; vein-vs-conduit radius; site vs bond; crop windows, absent petiole, no enforced source node | P11 |
| 15 | Withdraw the finite-size claim, then position the increment and close | the sweep + the empirical p_c–N check **[computed]**; then the novelty statement | P8 then P10 |

Do **not** merge ¶9, ¶10, ¶11, ¶12 or ¶13 into anything — each is a "do not combine" prohibition.

**The seven pairs that must NOT share a paragraph** (reasoning in `rrl/J` Part 4): D with connectivity; the sink with the percolation threshold; synthetic with empirical thresholds *as a magnitude comparison*; the enhancement gain with the response-surface prediction; the failed K_leaf check with any validation that passed; the withdrawn finite-size claim with the synthetic threshold values; the three-mode synthetic comparison with the two-mode empirical result *unless the transition is explicitly marked*.
**What may safely be combined:** the two loop-fraction correlations (+0.818 with the targeted threshold, −0.786 with the attack gap) belong together and only together — they are two faces of one claim.

---

# PART VIII — CITATION AUDIT

### Errors found in the current reference list — fix before submission

1. **The two Matos 2024 papers are fused.** The Dryad deposit's registered primary article is the **data paper**: Matos, I. S., et al. (2024), *Ecology*, **105**(12), e4436, doi **10.1002/ecy.4436**. The *New Phytologist* **244**(2), 407–425, doi 10.1111/nph.20037 is a **separate analysis paper** ("Leaf venation network architecture coordinates functional trade-offs across vein spatial scales"). The manuscript currently attaches the *New Phytologist* locators to the dataset title. **Cite ecy.4436 for the data and nph.20037 for the analysis.** A reviewer familiar with this group will notice immediately.
2. **"Ronellenfitsch & Katifori 2019, PRL 123:038301" — wrong article number.** Correct: *Physical Review Letters* **123**(24), **248101**, doi 10.1103/PhysRevLett.123.248101 (Crossref-verified). The likely source of the error is the same authors' PRL **117**, 138301 (2016).
3. **"Sack et al. 2008, Plant Cell Environ 31:943–958" does not resolve.** An enumeration of all 327 *PCE* records for 2007-06 to 2009-06 found no Sack paper in that volume. The intended reference is almost certainly **Sack, L., Dietrich, E. M., Streeter, C. M., Sánchez-Gómez, D., & Holbrook, N. M. (2008), *PNAS*, 105(5), 1567–1572, doi 10.1073/pnas.0709333105** — read in full and carded in `rrl/A`. Confirm before correcting.
4. **Mrad et al. (2021) author list.** Verified: **Mrad, A., Johnson, D. M., Love, D. M., & Domec, J.-C.** The manuscript carries two conflicting lists; the other belongs to Mrad et al. 2018 (Mrad, Domec, Huang, Lens, Katul).
5. **Muraleedharan et al. (2023) is being used against its own argument.** Its thesis is that box-counting has determinable *limits* for leaves and should be replaced. Cite it in **Limitations**, never as warrant for computing D. It also measures **leaf shape, not venation networks**. The open-access companion — **Vishnu, M., & Jaishanker, R. (2023), *Environmental Research Communications*, 5(5), 055013, doi 10.1088/2515-7620/acd5b0** — is verifiable and safer to lean on.
6. **Zhang et al. (2025) species-pair count.** The paper's context says 118; the institutional release says 119 pairs (340 individuals). Verify against the published article.
7. **Albert, Jeong & Barabási (2000) carries a published erratum** — *Nature*, **409**(6819), 542, doi 10.1038/35054111 — correcting the exponential-network error-tolerance curves. Cite the erratum alongside.
8. **DOIs still requiring Crossref verification:** Felsenstein (1985), Benjamini & Hochberg (1995), Cliff (1993), Efron (1987), Jin & Qian (2019). **Specific warning:** the JASA 82(397) DOI 10.1080/01621459.1987.10478409 attaches to a *different* title — do not use it for Efron's "Better bootstrap confidence intervals".
9. **Adams et al. (2017)** *Nature Ecology & Evolution* 1(9) — page range unverified.
10. **Tyree & Sperry (1989)** — indexed sources give both 19–36 and 19–38; verify.

### Claims currently under-cited

- **Why loops exist at all.** Katifori 2010, Corson 2010, Bohn & Magnasco 2007 — currently thin, and this is the theoretical foundation of the entire reticulation argument.
- **Why the K_leaf check should be expected to fail.** Scoffoni 2017 (*Plant Physiol*), Sack 2004/2005, Buckley 2015, and above all Matos et al.'s own "weakly predicts efficiency and resilience". The paper currently reports the failure without the prediction.
- **Why random removal is a null scenario.** Brodribb 2016, Pritzkow 2022, Lu 2025, Avila 2022, Johnson 2020 — five sources, currently zero.
- **Why targeted removal needs no agent.** Trajanovski 2013, Memmott 2004, Motter & Lai 2002 — currently zero.
- **Why localised (haustorial) damage does not break the model.** Berezin 2015, Shao 2015 — currently zero, and this is the objection most likely to be raised.
- **Why the analytic and simulated thresholds differ.** Kownacki 2008, Djordjevic 1982, Radicchi & Castellano 2016, Melnik 2011 — currently zero.
- **The cost of reticulation.** Price & Weitz 2014, Nardini 2012, Ronellenfitsch & Katifori 2019 — needed to explain "0 worsened".
- **That a pre-symptomatic window is empirically real.** Shen 2007, Cochavi 2017, Ortiz-Bustos 2017, González de Andrés 2024 — currently zero.

### Claims that are over-cited or mis-cited
- **Mrad et al. (2021) as contrary evidence** — it supports the paper. Move it.
- **Kaiser et al. (2015) for a ~1.5 MPa gradient** — re-verified twice: the article contains no MPa value. Already flagged in the project record; do not re-import.
- **Molloy–Reed as a validation.** f_c = 0.524 and MR = 0.531 are both tree-like generating-function results on the same degree sequence. Their agreement is internal consistency, not corroboration.

### Claims that should be softened rather than re-cited
Full table in `rrl/H`. The five that matter most: the title's "pre-symptomatic … haustorial sink stress"; "p_c" as a percolation threshold; ⟨k⟩ and loop fraction as two predictors; "validated to 1e-7"; any "first to apply percolation to leaf venation" phrasing.

---

# PART IX — NOVELTY AUDIT

**Full clause-by-clause analysis in `rrl/G`.** Summary:

**What is established and cannot be claimed:**
- Percolation-style robustness analysis of real leaf venation networks (Mander & Williams 2024, who use the word "percolation"; Price & Weitz 2014, who plot the curve on 339 leaves).
- Hagen–Poiseuille + Kirchhoff solve on real traced leaf venation (Skjegstad & Kirkegaard 2025; and the source dataset's own ℓ/r⁴ column).
- The coupling of percolation to solved xylem hydraulics (Mrad et al. 2021, stem conduits).
- Reticulation confers damage robustness (Price & Weitz 2014; Sack et al. 2008; Mander & Williams 2024; Brodribb et al. 2016).

**What is genuinely new:**
- **Site (node) percolation with an explicit, stated threshold criterion on traced leaf venation** — a narrow but real increment; prior work reports curves and AUC indices, not per-network thresholds.
- **Degree- and betweenness-targeted removal on a real leaf-venation cohort**, and the ordering betweenness < degree < random. No prior venation study runs any centrality-based attack.
- **Comparative scale**: ~100 species against Mander & Williams' 9 taxa, with per-network thresholds regressable against measured architecture.
- **The experimental decoupling of ⟨k⟩ from D** on a controlled grid — no prior venation study separates these axes causally.
- **A holoparasitic haustorial sink imposed as a boundary condition on a host vascular flow network** — searched from four directions; nothing found. The parasitic-plant network literature is developmental, molecular, or ecological (species-interaction networks), never vascular-hydraulic.
- **Second, currently underplayed:** that more reticulate leaves are not merely more robust but **less differentially exposed to targeting** (loop fraction × attack gap = −0.786). No precedent located for relating the random-minus-targeted gap to a topological trait.

**The framing problem that must be fixed.** The only clause holding the novelty claim up is the haustorial sink — and the paper's own result is that the sink and the percolation are decoupled. **"Driven by" asserts a causal link the results contradict.** Replace with "with a calibrated holoparasitic haustorial sink imposed as a boundary condition", hedge with "to our knowledge", and **promote the decoupling to a finding** rather than leaving it as a loose end. The replacement gap statement is drafted in full in `rrl/G`.

**Recommended title change.** The current title promises parasite-driven pre-symptomatic collapse and delivers neither: the sink embolises nothing, and "pre-symptomatic" is mechanistically indefensible for a xylem-topology model in the mild-stress regime (Scoffoni 2017; Avila 2022). The alternative framing — *Vein Reticulation as a Host-Resistance Trait* — survives if and only if (a) "resistance" is scoped to **structural tolerance of vein loss**, not embolism resistance (Loepfe/Mrad disagree on that sign), and (b) the parasite is demoted from mechanism to motivating scenario in the title as well as the text.

---

# PART X — PRIORITY READING LIST

Ranked. Tier is relevance to *this* paper, not journal prestige. ★ = obtain the full text before submission; the argument depends on content not yet verified.

**Read first — these change what the paper says (1–8)**
1. **Price & Weitz 2014**, *BMC Plant Biol* 14:234 — 10.1186/s12870-014-0234-2 — open access. The antecedent you must engage.
2. **Mander & Williams 2024**, *RSOS* 11:240086 — 10.1098/rsos.240086 — open access. Read the Discussion; they request your method by name.
3. ★ **Scoffoni et al. 2017**, *Plant Physiol* 173:1197 — 10.1104/pp.16.01643. Explains your K_leaf result and threatens your premise.
4. ★ **Mrad et al. 2021**, *New Phytol* 231:996 — 10.1111/nph.17429. Cited backwards in the project record; it supports you.
5. **Matos et al. 2024**, *New Phytol* 244:407 — 10.1111/nph.20037. Your data providers' own conclusion about architecture and resilience.
6. **Skjegstad & Kirkegaard 2025**, *PLOS Comput Biol* 21:e1013292 — 10.1371/journal.pcbi.1013292 — open access. Breaks your method-novelty clause.
7. ★ **Sack et al. 2008**, *PNAS* 105:1567 — 10.1073/pnas.0709333105. The only real-leaf removal-and-measure experiment.
8. **Balios et al. 2025**, *Ann Bot* 135:823 — 10.1093/aob/mcae208. The published negative that licenses your sink-strength hedge.

**Mechanism and interpretation (9–18)**
9. Katifori, Szöllősi & Magnasco 2010, *PRL* 104:048704 — 10.1103/PhysRevLett.104.048704
10. Corson 2010, *PRL* 104:048703 — 10.1103/PhysRevLett.104.048703
11. Ronellenfitsch & Katifori 2019, *PRL* 123:**248101** — 10.1103/PhysRevLett.123.248101
12. Ronellenfitsch, Lasser, Daly & Katifori 2015, *PLOS Comput Biol* 11:e1004680 — 10.1371/journal.pcbi.1004680
13. ★ Brodribb, Bienaimé & Marmottant 2016, *PNAS* 113:4865 — 10.1073/pnas.1522569113
14. ★ Brodribb et al. 2021, *New Phytol* 232:68 — 10.1111/nph.17577
15. Lu et al. 2025, *AoB PLANTS* 17:plaf020 — 10.1093/aobpla/plaf020 — open access
16. Loepfe et al. 2007, *J Theor Biol* 247:788 — 10.1016/j.jtbi.2007.03.036
17. Sack & Scoffoni 2013, *New Phytol* 198:983 — 10.1111/nph.12253
18. Blonder et al. 2018, *J Ecol* 106:1683 — 10.1111/1365-2745.12945 — the reticulation-is-about-defence counterargument

**Network science and attack strategy (19–26)**
19. Trajanovski et al. 2013, *J Complex Netw* 1:44 — 10.1093/comnet/cnt004 — the envelope framing
20. Berezin et al. 2015, *Sci Rep* 5:8934 — 10.1038/srep08934 — open access; kills the localised-attack objection
21. Shao et al. 2015, *New J Phys* 17:023049 — 10.1088/1367-2630/17/2/023049 — open access
22. Mou & Hayashi 2025, *PLOS ONE* 20:e0327203 — 10.1371/journal.pone.0327203 — open access; planar ⟨k⟩ ≈ 2.50
23. Tian et al. 2017, *Nat Commun* 8:14223 — 10.1038/ncomms14223 — open access; the articulation-point mechanism
24. Wandelt et al. 2018, *Sci Rep* 8:13513 — 10.1038/s41598-018-31902-8 — open access; static vs iterative
25. Radicchi & Castellano 2016, *PRE* 93:030302 — 10.1103/PhysRevE.93.030302
26. Mizutaka & Hasegawa 2022, *JPSJ* 91:044002 — 10.7566/JPSJ.91.044002 — the FSS diagnostic you should run

**Hydraulic modelling and the dataset (27–33)**
27. **Dryad data dictionary**, 10.5061/dryad.1g1jwsv36 — read it; it settles the validation question
28. ★ Matos et al. 2024, *Ecology* 105:e4436 — 10.1002/ecy.4436 — the correct data citation
29. Xu et al. 2021, *New Phytol* 229:631 — 10.1111/nph.16923
30. Price, Knox & Brodribb 2013, *PLOS ONE* 8:e85420 — 10.1371/journal.pone.0085420 — open access; Murray's law by vein order
31. Sperry, Hacke & Wheeler 2005, *PCE* 28:456 — 10.1111/j.1365-3040.2005.01287.x — the ~54% end-wall number
32. Sack, Streeter & Holbrook 2004, *Plant Physiol* 134:1824 — 10.1104/pp.103.031203
33. ★ McKown, Cochard & Sack 2010, *Am Nat* 175:447 — 10.1086/650721 — the direct modelling ancestor; do not cite from summaries

**Parasite biology (34–39)**
34. Jiang, Jeschke & Hartung 2003, *JXB* 54:1985 — 10.1093/jxb/erg212 — your calibration anchor; note it contains no MPa value
35. Griebel et al. 2022, *Tree Physiol* 42:523 — 10.1093/treephys/tpab113 — the best-measured host ψ depression
36. Shen et al. 2007, *JXB* 58:2929 — 10.1093/jxb/erm168 — ~50-day holoparasite window
37. Cochavi et al. 2017, *Front Plant Sci* 8:909 — 10.3389/fpls.2017.00909 — open access; ~20-day window with unchanged gas exchange
38. Pérez-de-Luque et al. 2005, *Ann Bot* 95:935 — 10.1093/aob/mci105 — open access; the only positive occlusion evidence
39. Jhu et al. 2022, *Plant Physiol* 189:129 — 10.1093/plphys/kiac024 — *Cuscuta* defence is cortical, not vascular
39b. ★ **Labrousse et al. 2001**, *Ann Bot* 88:859 — 10.1006/anbo.2001.1520 — possibly the single best citation for the node-removal premise (reportedly: callose deposited inside host xylem in contact with the parasite, in some cases completely closing vessels). **Encountered only as a search-level restatement, and contradicted by Echevarría-Zomeño 2006 in a different genotype. Retrieve and verify before use.**

**Statistics (40–43)**
40. Morris, White & Crowther 2019, *Stat Med* 38:2074 — 10.1002/sim.8086 — open access; ADEMP + MCSE
41. Rochon, Gondan & Kieser 2012, *BMC Med Res Methodol* 12:81 — 10.1186/1471-2288-12-81 — open access; saves your Shapiro–Wilk gate
42. Revell 2010, *Methods Ecol Evol* 1:319 — 10.1111/j.2041-210X.2010.00044.x — phylogenetic signal is in the residuals
43. Koehler, Brown & Haneuse 2009, *Am Stat* 63:155 — 10.1198/tast.2009.0030 — justify trial budgets against precision

---

# APPENDIX — THE ACTION LIST

Ordered by return per unit effort. Items marked ⚑ are, in the agents' collective judgement, required before submission.

**Free — arithmetic or wording only**
1. Rename p_c → **f₅₀**; reserve p_c/f_c for the vanishing threshold. Largest attack surface removed at zero cost.
2. Add the three effect sizes: r_rb = 1.00, r_rb ≈ 0.99, Cliff's δ = 0.987 **[computed]**, always beside the median difference.
3. Report the K_leaf **CI [−0.024, +0.382] [computed]** and call the check underpowered, not null.
4. Report VIF = 1.022 and r(⟨k⟩, D) = 0.148 **[computed]**; state the planar identity loop ≈ 1 − 2/⟨k⟩; promote the residual test into the main text.
5. ⚑ Report **Spearman(N, f₅₀) = +0.232** and the size-controlled partials **[computed]** in the finite-size paragraph.
6. ⚑ Disclose **Spearman(N, D) = +0.880 [computed]** and the grid's +0.990.
7. ⚑ Report the grade-A refutation: highest residual gain, 13/13 changed leaves improved, sign test p = 2.4 × 10⁻⁴ **[computed]**.
8. Report the **restricted-grid refit** (β 0.981 vs 0.125, R² 0.940, 7.8:1, n = 24) **[computed]** as primary.
9. ⚑ Relabel the 1e-7 result **verification**, not validation; delete the 16-digit r and its p-value; put the wrong-exponent control on the ratio scale.
10. ⚑ Fix the ten citation errors in Part VIII, starting with the two Matos papers.
11. ⚑ Rewrite the novelty statement using the drafted replacement in `rrl/G`; drop "driven by".
12. Name random removal a **null structural scenario** in Methods, with the five sources.
13. Add the Berezin/Shao localised-attack defence — one paragraph, closes the objection most likely to be raised.
14. State the uniform application of the Shapiro–Wilk rule; add one BH sentence; name the bootstrap method and B.
15. Correct the quality-grade description to the six-tier A–F scale, note the retained set spans A–D, and note the grades are non-ordinal **[computed]**.

**Cheap compute — under an hour each**
16. ⚑ **Rank-correlate node betweenness against Kirchhoff-solved node flux.** Converts the most-attacked design choice into a measured result. Highest-value single addition in this pass.
17. ⚑ **Cavitation-threshold sensitivity sweep across −1.0 to −4.0 MPa**, reporting where embolism becomes non-zero. The null is currently threshold-dependent with a margin smaller than the between-species P50 spread.
18. **p_c sensitivity across the `Resistance_2` (ℓ/r²) vs `Resistance_4` (ℓ/r⁴) conventions.** The deposit ships both; this closes the deepest model vulnerability with no new modelling.
19. **Source-anchored connectivity variant** — designate the highest-order vein in each window as a pseudo-source and show the rankings agree. Closes a Major objection.
20. **Localised (contiguous-disc) removal** on a subset, following Mander & Williams' protocol. Empirically kills the haustorium-is-local objection in your own data.
21. **Recalculated-betweenness attack on the N = 1023 synthetic reference only.** One number bounds the static-ranking concession.
22. **Susceptibility-peak / second-largest-cluster FSS** on the five pinned sizes via Newman–Ziff. Converts the paper's most exposed section into its most rigorous.
23. Report tie counts and the tie-breaking rule in the degree attack; report betweenness SD alongside degree SD 0.848.
24. Pratt-variant Wilcoxon (already run **[computed]**: p = 1.7 × 10⁻¹⁸) and one sentence on why 12 differences are exactly zero.
25. Pagel's λ on the regression residuals via V.PhyloMaker; report λ either way (Revell 2010 makes a null result *justify* the OLS).
26. Check the code for **common random numbers** in the paired enhancement runs, and report the paired MCSE.
