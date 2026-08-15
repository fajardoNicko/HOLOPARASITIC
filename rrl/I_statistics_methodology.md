## TIER 1 (essential methodological sources)

---

**Morris, T. P., White, I. R., & Crowther, M. J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine, 38*(11), 2074–2102.**
| **DOI** 10.1002/sim.8086 | **Access** FULL TEXT READ (PMC6492164) | **Type** Methodological tutorial / reporting framework
| **Main point** Simulation studies must be planned and reported under ADEMP — **A**ims, **D**ata-generating mechanisms, **E**stimands, **M**ethods, **P**erformance measures — and every simulation-derived estimate carries a quantifiable Monte Carlo standard error that should be reported alongside it. For a proportion-type performance measure, `n_sim = E(p)(1−E(p)) / MCSE_req²`; the worked example states that a 50% proportion requires **n_sim = 10,000 for MCSE = 0.5%**, and ~1,900 for a 95% quantity at the same precision. Explicit rule: *"results should not be presented to greater accuracy than is justified by the Monte Carlo SE."*
| **Exact relevance** Three separate analyses. (1) The **unequal trial budgets** (2,400 vs 10,000 per leaf) are exactly the n_sim question this paper answers, and the paper's own numbers fall out of the formula: p_c is *defined* as the point where P(collapse) = 0.50, i.e. the worst case, so MCSE = √(0.25/2,400) = **0.0102** vs √(0.25/10,000) = **0.0050** on the survival-probability scale — a factor of 2.04. Morris's worked example makes 10,000 the *justified* choice and 2,400 the one needing defence. (2) The 16-significant-figure Pearson r (0.999999999999996) is a direct violation of the accuracy-of-presentation rule. (3) ADEMP gives a ready-made skeleton for the percolation Methods subsection.
| **Paragraph location** Methods — Percolation simulation design (as a short ADEMP-structured paragraph); Methods — Statistical analysis (MCSE sentence); Discussion — Limitations.
| **Supports** "2,400 and 10,000 trials give per-leaf Monte Carlo SEs of 1.0 and 0.5 percentage points on the collapse probability at the threshold; the enhancement cohort was run at the higher budget because the estimand there is a *difference* of order 0.01."
| **Strength** Very high — the standard reference, and directly quantitative for this design.
| **Caveat** Morris frames MCSE for the *performance measure*; p_c is a threshold, not a proportion, so the MCSE must be propagated through the slope dP/dp at the crossing (or obtained by bootstrapping trial outcomes and re-solving the threshold). Do not report √(0.25/n) as if it were the SE of p_c itself.

---

**Koehler, E., Brown, E., & Haneuse, S. J.-P. A. (2009). On the assessment of Monte Carlo error in simulation-based statistical analyses. *The American Statistician, 63*(2), 155–162.**
| **DOI** 10.1198/tast.2009.0030 | **Access** FULL TEXT READ (PMC author manuscript; publisher page 403) | **Type** Methodological + survey of published practice
| **Main point** Monte Carlo error is systematically underappreciated and is often larger than assumed. Of **223 simulation studies surveyed in major journals, only 8 reported any MCE estimate**. Replication counts should be *justified against a target precision*, not chosen by convention (they single out the reflexive R = 1,000). MCE magnitude is design- and estimand-specific — no one-size-fits-all.
| **Exact relevance** Supplies the empirical warrant for the paper's strongest available rebuttal on trial budgets: reporting MCSE at all puts it in the top ~4% of simulation papers. Directly targets the "2,400 vs 10,000 was deliberate but unjustified" exposure — the fix is not to equalise, it is to *justify against a precision target*. Also justifies the bootstrap route to per-leaf p_c uncertainty, which the paper already has running code for (it produced the synthetic reference CIs).
| **Paragraph location** Methods — Statistical analysis, one sentence; Discussion — Limitations.
| **Supports** "Replication counts were chosen to meet a target Monte Carlo standard error rather than by convention."
| **Strength** High — the citation that makes MCSE reporting a virtue rather than a defensive concession.
| **Caveat** Written for statistical-method simulations; percolation thresholds are not its worked setting.

---

**Rochon, J., Gondan, M., & Kieser, M. (2012). To test or not to test: Preliminary assessment of normality when comparing two independent samples. *BMC Medical Research Methodology, 12*, 81.**
| **DOI** 10.1186/1471-2288-12-81 | **Access** FULL TEXT READ | **Type** Simulation study
| **Main point** The two-stage "test normality, then choose the test" procedure **substantially distorts conditional Type I error**: for exponential data that passed Shapiro–Wilk, the subsequent t-test showed observed Type I error of **10.8% (α_pre = .005) and 17.0% (α_pre = .100)** against a nominal 5%. The *unconditional* error rate and power of the whole two-stage procedure nevertheless stayed acceptable. Recommendation: establish the distributional assumption from external sources (prior studies, pilot data); failing that, **use nonparametric tests unconditionally rather than running a two-stage procedure**.
| **Exact relevance** This is the single most likely reviewer objection to the paper's stated design, and this source resolves it in the paper's favour *if one sentence is added*. The paper's rule was (a) pre-specified and (b) applied to **all** association tests uniformly — that is precisely Rochon's endorsed "use nonparametrics unconditionally" branch, not the condemned per-variable branch. The distinction is load-bearing here because the paper's four Shapiro–Wilk results **disagree with each other**: p_c (p = 5.1e-06) and D (p = 0.0084) reject hard, mean degree (p = 0.027) rejects marginally, and **loop fraction (p = 0.089) does not reject at all**. A per-variable rule would have sent loop fraction to Pearson and the other three to Spearman — visibly incoherent. Uniform application is what makes the paper defensible, and it is currently implicit.
| **Paragraph location** Methods — Statistical analysis, immediately after the normality results.
| **Supports** "Because normality was rejected for the primary outcome, a pre-specified rule switched **all** association tests to Spearman; no test was selected post hoc on the basis of its own W statistic."
| **Strength** Very high — converts a known weak practice into a defensible one at the cost of one clause.
| **Caveat** Rochon's simulations concern two-sample location tests, not correlation coefficients. The transfer is by analogy. Also: Shapiro–Wilk on the *marginal* distributions does not test the assumption the multiple regression actually makes (normality of **residuals**) — see Cheap Wins.

---

**Pratt, J. W. (1959). Remarks on zeros and ties in the Wilcoxon signed rank procedures. *Journal of the American Statistical Association, 54*(287), 655–667.**
| **DOI** 10.1080/01621459.1959.10501526 | **Access** ABSTRACT ONLY (publisher record + Stata/SciPy/asht implementation docs) | **Type** Seminal theoretical note
| **Main point** Dropping zero differences before ranking (Wilcoxon's original convention) is **logically non-monotone**: a sample can be non-significant while a *uniformly more negative* sample is significant. Pratt's alternative — rank all observations **including** the zeros, then discard the zeros' ranks and test the remaining rank sum against its null distribution *conditional on the number of zeros* — removes the anomaly and is more conservative.
| **Exact relevance** The enhancement analysis discards **12 zero differences from 105** and tests the remaining 93. That is the Wilcoxon convention (and SciPy's default, `zero_method='wilcox'`), so it is not wrong — but it is the *anti-conservative* of the two available conventions, and a reviewer who knows Pratt will ask. Because W = 0 (every one of the 93 non-zero differences is positive), the Pratt variant **cannot change the conclusion**, which makes reporting it a free robustness statement.
| **Paragraph location** Methods — Statistical analysis (one clause naming the convention); Results — Reticulation enhancement (the Pratt sensitivity p, one parenthesis).
| **Supports** "Zero differences were handled by Wilcoxon's exclusion convention; the more conservative Pratt (1959) treatment gives the same conclusion."
| **Strength** High for the specific objection; the substantive conclusion is untouchable either way.
| **Caveat** I could not read the full paper. The 12 exact zeros are separately worth explaining — exact ties in a continuous quantity are suspicious unless p_c is snapped to a discrete grid of removed-node counts k/N, which it presumably is. **Say so**, or a reviewer will read the ties as a bug.

---

**Kerby, D. S. (2014). The simple difference formula: An approach to teaching nonparametric correlation. *Comprehensive Psychology, 3*, 11.IT.3.1.**
| **DOI** 10.2466/11.IT.3.1 | **Access** PUBLISHER RECORD ONLY (SAGE 403; corroborated by the R `effectsize::rank_biserial` and pingouin reference documentation) | **Type** Methodological/expository
| **Main point** The matched-pairs rank-biserial correlation is the **simple difference between the proportion of favourable and unfavourable evidence**, r = f − u. For the signed-rank test the evidence is rank sums: divide the positive and negative rank sums by the total rank sum and subtract. Its advantage is that it re-expresses one effect size in terms of another intuitive one (the common-language effect size).
| **Exact relevance** This is the paper's cheapest structural fix. Both Wilcoxon tests report p-values and **no effect size**. Both have W = 0, so the rank-biserial is pure arithmetic with zero compute:
  - **Random vs degree-targeted (n = 100, all 100 differences positive):** positive rank sum = 100·101/2 = 5,050; negative = 0; **r_rb = +1.00**. Common-language effect size = **100/100 leaves (100%)**.
  - **Enhancement (105 leaves; 93 positive, 12 zero, 0 negative):** on the 93 analysed, **r_rb = +1.00**. Including the ties under Pratt ranking: total rank sum = 105·106/2 = 5,565; the 12 zeros hold ranks 1–12 summing to 78; positive rank sum = 5,487; **r_rb = 5,487/5,565 = +0.986**. Common-language = **93/105 (88.6%) improved, 0% worsened**.
| **Paragraph location** Results — Attack modes; Results — Reticulation enhancement. One clause each, in the same sentence as the existing p-values.
| **Supports** "Degree-targeted attack lowered p_c in 100/100 leaves (matched-pairs rank-biserial r = 1.00; median difference 0.0305)." / "Enhancement raised p_c in 93/105 leaves and lowered it in none (r_rb = 0.99; median Δp_c = 0.0095)."
| **Strength** Very high — forecloses the "no effect sizes" objection completely, costs two clauses and no compute.
| **Caveat** Could not read Kerby's original. An r_rb of 1.00 is a *directional consistency* statement, not a magnitude statement — it must be reported **next to the median difference**, never instead of it, or it will be misread as "the effect is huge."

---

**Dormann, C. F., Elith, J., Bacher, S., Buchmann, C., Carl, G., Carré, G., … Lautenbach, S. (2013). Collinearity: A review of methods to deal with it and a simulation study evaluating their performance. *Ecography, 36*(1), 27–46.**
| **DOI** 10.1111/j.1600-0587.2012.07348.x | **Access** ABSTRACT ONLY (Wiley, HAL and Semantic Scholar all blocked) | **Type** Review + simulation study
| **Main point** Collinearity **inflates the variance of regression parameters and thereby leads to wrong identification of the relevant predictors**. Standard quantifications: pairwise r, condition index, VIF and generalised VIF, variance-decomposition proportions. Remedies range from clustering and threshold pre-selection through latent-variable methods to shrinkage.
| **Exact relevance** The ρ = 0.994 between ⟨k⟩ and loop fraction (n = 112). Reporting ρ(p_c, ⟨k⟩) = 0.733 **and** ρ(p_c, loop) = 0.727 side by side as two predictors is precisely the "wrong identification of relevant predictors" failure. **Critically, this exposure is confined to the descriptive correlation table and does NOT touch the multiple regression** — see Cheap Wins, where I back out the actual predictor correlation in the fitted model as r ≈ 0.15, VIF ≈ 1.02.
| **Paragraph location** Results — Topological predictors (reframing the two correlations as one axis); Methods — Statistical analysis (the VIF sentence).
| **Supports** "⟨k⟩ and loop fraction index a single connectivity axis and are not independent predictors; ⟨k⟩ is reported as its representative."
| **Strength** High as the citable authority; the paper's own residual test (ρ = −0.088, p = 0.386) is the actual evidence.
| **Caveat** I could **not** verify the widely quoted |r| > 0.7 threshold in the retrieved abstract — do not cite a specific number to Dormann without checking the PDF.

---

## TIER 2

**Freckleton, R. P. (2009). The seven deadly sins of comparative analysis. *Journal of Evolutionary Biology, 22*(7), 1367–1375.** | DOI 10.1111/j.1420-9101.2009.01757.x | ABSTRACT ONLY | Review. Catalogues recurrent failures in cross-species analysis, rooted in "a lack of appreciation of the underlying assumptions of comparative methods." **Relevance:** this is the paper a plant-biology reviewer will reach for when objecting that 100+ species are treated as independent in the p_c ~ ⟨k⟩ + D regression. **Location:** Discussion — Limitations. **Strength:** high as the framing of the objection; **Caveat:** it is the indictment, not the remedy — pair with Revell.

**Revell, L. J. (2010). Phylogenetic signal and linear regression on species data. *Methods in Ecology and Evolution, 1*(4), 319–329.** | DOI 10.1111/j.2041-210X.2010.00044.x | ABSTRACT ONLY (PDF fetched but not renderable) | Simulation study. **Main point:** the near-universal practice of testing the *traits* X and Y for phylogenetic signal and using that to justify PGLS is **wrong** — phylogenetic regression assumes the signal is in the **residual error**, not the raw traits. When residuals carry no signal, **OLS estimates the slope more accurately than PGLS**. **Relevance:** this is the paper's escape route, not just a criticism. It licenses a defensible OLS result *provided* Pagel's λ is computed on the residuals of p_c ~ ⟨k⟩ + D and reported. **Location:** Methods — Statistical analysis; Discussion — Limitations. **Strength:** very high — it makes the phylogenetic fix cheap and makes a null result publishable rather than embarrassing.

**Nakagawa, S., & Cuthill, I. C. (2007). Effect size, confidence interval and statistical significance: A practical guide for biologists. *Biological Reviews, 82*(4), 591–605.** | DOI 10.1111/j.1469-185X.2007.00027.x | ABSTRACT ONLY | Review/guide. NHST gives neither magnitude nor precision; biologists should report effect sizes with CIs in all cases. **Relevance:** the biology-facing citation for adding rank-biserial effect sizes and for putting a CI on the non-significant K_leaf Spearman (ρ = 0.187, p = 0.073, n = 93) instead of calling it "no relationship." **Location:** Methods — Statistical analysis; Results — K_leaf check. **Strength:** high; it is the version of this argument a plant journal's readership already accepts.

**Wasserstein, R. L., & Lazar, N. A. (2016). The ASA's statement on p-values: Context, process, and purpose. *The American Statistician, 70*(2), 129–133.** | DOI 10.1080/00031305.2016.1154108 | ABSTRACT ONLY | Position statement. **Relevance:** the one-line citation for why p = 3.9e-18 is not a finding. Use once. **Caveat:** do not build a paragraph around it — see What Not To Do.

**Lin, M., Lucas, H. C., & Shmueli, G. (2013). Research commentary — Too big to fail: Large samples and the p-value problem. *Information Systems Research, 24*(4), 906–917.** | DOI 10.1287/isre.2013.0480 | ABSTRACT ONLY | Research commentary. "In very large samples, p-values go quickly to zero, and solely relying on p-values can lead the researcher to claim support for results of no practical significance." **Relevance:** the paper's validation section rests on **5,668,467 veins**; at that n every p-value is structurally zero and carries no information. Also applies to the 1e6-trial synthetic reference. **Location:** Methods — Model verification. **Strength:** high, and unusually on-the-nose for the 5.67M-vein comparison.

**Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society, Series B, 57*(1), 289–300.** | DOI not verified in this session | PUBLISHER RECORD ONLY | Seminal method. **Relevance:** BH, not Bonferroni, is the right control here — the tests are positively dependent (nested cohorts, overlapping variables) and the aim is discovery. **Location:** Methods — Statistical analysis, one sentence. **Strength:** high for foreclosing the objection at near-zero cost.

**Cliff, N. (1993). Dominance statistics: Ordinal analyses to answer ordinal questions. *Psychological Bulletin, 114*(3), 494–509.** | DOI not verified in this session | ABSTRACT ONLY | Methodological. Introduces δ, the proportional dominance of one group over another; more robust than mean comparisons, equally or more powerful, invariant under monotone transformation. **Relevance:** the **quartile comparison** (Q1 vs Q4, U = 4) has no effect size. Cliff's δ falls straight out of U: δ = 1 − 2U/(n₁n₂). With ~26 per quartile from n = 105, δ = 1 − 8/676 = **0.988** — near-complete separation. **Location:** Results — Reticulation quartiles. **Caveat:** substitute the true per-quartile n.

---

## TIER 3

**Mesgaran, M. B., Cousens, R. D., & Webber, B. L. (2014). Here be dragons: A tool for quantifying novelty due to covariate range and correlation change when projecting species distribution models. *Diversity and Distributions, 20*(10), 1147–1159.** | DOI 10.1111/ddi.12209 | ABSTRACT ONLY | Methods paper. Distinguishes **Type 1 novelty** (outside the univariate range of the calibration data) from **Type 2 novelty** (novel *combinations* of covariates within range), quantified by Mahalanobis distance. **Relevance:** the synthetic grid's ⟨k⟩ axis reaches **4.00 against an empirical maximum of 2.99** — textbook Type 1 novelty over roughly the upper third of the synthetic range. Gives the paper precise vocabulary for a scope condition rather than an apology. **Location:** Results — Synthetic grids; Discussion. **Caveat:** an SDM-specific tool; cite for the *concept and terminology*, do not run ExDet.

**Jin, Y., & Qian, H. (2019). V.PhyloMaker: An R package that can generate very large phylogenies for vascular plants. *Ecography, 42*(8), 1353–1359.** | DOI 10.1111/ecog.04434 (inferred from the journal's ECOG-04434 appendix record; verify) | ABSTRACT ONLY | Software. Backbone megatree GBOTB.extended.tre covers **74,533 species and all extant vascular plant families**; generates trees for large species lists quickly. **Relevance:** the practical route to a phylogeny for the ~93–120 species in the cohorts. Turns "phylogenetic correction" from a project into an afternoon. **Location:** Methods — Statistical analysis (if the λ check is run).

**Ernst, M. D. (2004). Permutation methods: A basis for exact inference. *Statistical Science, 19*(4), 676–685.** | DOI 10.1214/088342304000000396 | ABSTRACT ONLY | Review. Permutation inference dates to Fisher (1935) and is exact and distribution-free under exchangeability. **Relevance:** an optional upgrade for the **Q1-vs-Q4 quartile comparison** — a permutation test on the difference in medians gives an exact p *and* a permutation CI, and sidesteps Mann-Whitney's location-shift interpretation. **Strength:** moderate; the conclusion will not change. Low priority.

**Thabane, L., Mbuagbaw, L., Zhang, S., Samaan, Z., Marcucci, M., Ye, C., … Goldsmith, C. H. (2013). A tutorial on sensitivity analyses in clinical trials: The what, why, when and how. *BMC Medical Research Methodology, 13*, 92.** | DOI 10.1186/1471-2288-13-92 | ABSTRACT ONLY | Tutorial/commentary. Sensitivity analyses assess robustness of conclusions to key assumptions — analysis method, outcome definition, outliers. **Relevance:** the citable standard for packaging the Pratt-ties check, the BH check, the extrapolation-restricted grid refit, and the residual-λ check as a single declared **sensitivity block** rather than four scattered defensive footnotes. **Location:** Methods — Sensitivity analyses (a new short subsection).

**Boulesteix, A.-L., Binder, H., Abrahamowicz, M., & Sauerbrei, W. (2018). On the necessity and design of studies comparing statistical methods. *Biometrical Journal, 60*(1), 216–218.** | DOI 10.1002/bimj.201700129 | ABSTRACT ONLY | Editorial (STRATOS Simulation Panel). Researchers assessing new methods tend to make assumptions favourable to the new method. **Relevance:** relevant to the **synthetic grid**, where the design was chosen by the authors and reaches ⟨k⟩ values real leaves never attain — the grid is a self-designed comparator, and a reviewer may read it as constructed to favour the ⟨k⟩ hypothesis. **Strength:** low-moderate; useful as a self-awareness citation in Limitations, optional.

**Efron, B. (1987). Better bootstrap confidence intervals. *Journal of the American Statistical Association, 82*(397), 171–185.** | DOI not verified (the JASA 82/397 DOI surfaced in search, 10.1080/01621459.1987.10478409, attaches to a *different* title — do not use it) | PUBLISHER RECORD ONLY | Seminal method. BCa corrects for **both bias and skewness** of the bootstrap distribution via a bias-correction and an acceleration constant; percentile intervals do not. **Relevance:** the paper reports "bootstrap 95% CIs" for the three synthetic p_c values without naming the method. p_c is a threshold of a monotone sigmoid, so its sampling distribution can be skewed and percentile vs BCa is a legitimate question. **Location:** Methods — Percolation simulation, one clause. **Caveat:** at 1e6 trials the interval is ±0.001 wide and the method choice is immaterial — say that explicitly and the objection dies.

---

## THE STATISTICAL EXPOSURE LIST

**First, a finding that reframes everything below.** I independently reproduced the paper's arithmetic from the reported summaries and **every number checks out**:

| Reported | My reconstruction |
|---|---|
| F(2,97) = 49.93 from R² = 0.5073 | (0.5073/2)/(0.4927/97) = **49.94** |
| F(2,102) = 96.77 from R² = 0.6549 | (0.6549/2)/(0.3451/102) = **96.79** |
| F(2,39) = 152.61 from R² = 0.8867 | (0.8867/2)/(0.1133/39) = **152.61** |
| R² = 0.5073 vs betas 0.526, 0.408 and Pearson r 0.587, 0.486 | 0.526(0.587) + 0.408(0.486) = **0.5071** |
| Wilcoxon n = 100, W = 0, p = 3.9e-18 | z = 2,525/√84,587.5 = 8.682 → two-sided **3.9e-18** |
| Wilcoxon n = 93, W = 0, p = 5.6e-17 | z = 2,185.5/√68,114.75 = 8.374 → two-sided **5.6e-17** |
| Relative gain 45.7% | (0.2308 − 0.1584)/0.1584 = **45.71%** |

**Every exposure below is therefore interpretive or presentational, not computational.** That is a strong position to be in and worth knowing before triaging.

---

### 1. The ρ = 0.994 pair reported as two predictors — MOST SERIOUS, and analytically explicable
**Objection:** "You report ρ(p_c, ⟨k⟩) = 0.733 and ρ(p_c, loop fraction) = 0.727 as two lines of evidence. They correlate at 0.994. This is one finding reported twice, and the reader is being given a false impression of convergent support."

**Severity: high** — this is the kind of thing that reads as either naivety or inflation, and it sits in the paper's headline result.

**Fix, in three parts, all free:**

**(a) Explain the 0.994 analytically.** For a connected planar graph, ⟨k⟩ = 2E/V and the cycle rank is E − V + 1, so if loop fraction is defined as (E − V + 1)/E then

> loop fraction = 1 − (V − 1)/E = 1 − 2(V − 1)/(⟨k⟩V) ≈ **1 − 2/⟨k⟩**

Loop fraction is a **deterministic monotone function of ⟨k⟩** up to an O(1/V) correction. The Spearman correlation would be exactly 1.000 at fixed V; **0.994 is the finite-V residual, not an empirical coincidence.** Sanity check across the observed range: ⟨k⟩ = 2.5 → 0.200; ⟨k⟩ = 2.99 → 0.331. State this in one sentence and the "hazard" becomes a demonstration that the authors understand their own graph invariants. *(Verify against the code's actual loop-fraction definition before writing it — if the denominator is faces or vertices rather than edges the algebra shifts but the monotone-function conclusion holds.)*

**(b) Promote the residual test out of the appendix.** The paper already has the decisive analysis: loop fraction residualised on ⟨k⟩ vs p_c gives ρ = −0.088, p = 0.386. That is the correct test and it is currently buried. It belongs in the main text, one sentence: *"Loop fraction carries no information about p_c beyond ⟨k⟩ (partial ρ = −0.088, p = 0.386); consistent with the planar identity above, we treat them as a single connectivity axis and report ⟨k⟩ as its representative."*

**(c) Do not regularise.** Ridge, PCA, or latent-variable treatment of this pair would be wrong. When two variables are the same quantity by a graph identity, the answer is to **drop one**, not to shrink both.

---

### 2. Missing effect sizes on every non-parametric comparison — MOST SERIOUS *fixable-in-ten-minutes*
**Objection:** "Three Wilcoxon/Mann-Whitney results are reported as p-values alone. p = 3.9e-18 tells me nothing about how much attack mode matters."

**Severity: high**, but it is the softest target in the paper because it is pure arithmetic.

**The specific aggravating fact:** both Wilcoxon p-values sit at the **boundary W = 0**, and both are normal-approximation values (I confirmed this to the digit above). At W = 0 the statistic is saturated — the p-value is a **function of n alone** and carries literally zero information about the magnitude of the effect. The *exact* p for n = 100, W = 0 is 2⁻⁹⁹ ≈ 1.6e-30, twelve orders of magnitude from the reported 3.9e-18; the gap is entirely an artefact of the normal approximation. This is the cleanest possible illustration of the Lin/Lucas/Shmueli and ASA points, and it is specific to this paper rather than borrowed.

**Fix:** add to each of the three comparisons, in the same sentence as the existing p-value:
- Attack modes: **r_rb = 1.00; 100/100 leaves; median difference 0.0305.**
- Enhancement: **r_rb = 0.99 (Pratt-ranked, all 105) or 1.00 (on the 93 non-zero); 93/105 improved (88.6%), 0 worsened; median Δp_c = 0.0095.**
- Quartiles: **Cliff's δ = 1 − 2U/(n₁n₂) ≈ 0.99; median p_c 0.1584 vs 0.2308.**

Always paired with the median difference, never alone.

---

### 3. The enhancement effect (0.0095) may be smaller than per-leaf Monte Carlo noise — SERIOUS, and currently unaddressed
**Objection:** "Your median Δp_c is 0.0095. Your synthetic reference at 1,000,000 trials has a 95% CI half-width of ±0.001. Scaling as 1/√n, at 10,000 trials that is **±0.01** — the same order as your entire claimed effect. How do I know this is not Monte Carlo noise?"

**Severity: high.** This is the objection most likely to be *decisive* rather than cosmetic, and I have not seen it addressed in the shared context.

**Two rebuttals exist and both are free:**

**(a) The paired design almost certainly kills the noise — but only if you say so.** If baseline and enhanced runs used **common random numbers** (same seeds, same trial structure), the Monte Carlo errors are correlated and the *difference* is far more precise than either arm's marginal CI implies. This is standard simulation practice and Morris et al. treat it explicitly. **State whether common random numbers were used, and report the MCSE of the difference rather than of each arm.** If they were not used, this needs fixing before submission.

**(b) The 93/12/0 pattern is itself the evidence.** If per-leaf p_c carried ±0.01 of *independent* noise and the true effect were ~0.0095, a substantial number of negative differences would appear by chance. **Zero leaves worsened.** That pattern is only consistent with low-noise paired estimation. The paper currently reports 93/12/0 as a descriptive tally; it should be reported as a **noise-floor argument**. One sentence, enormous return.

---

### 4. Extrapolation in the synthetic causal grid — SERIOUS
**Objection:** "Your grid reaches ⟨k⟩ = 4.00; real leaves top out at 2.99. Roughly a third of your synthetic ⟨k⟩ range has no empirical counterpart, and you use that grid to make a *causal* claim (β = 0.933 for ⟨k⟩ vs 0.067 for D)."

**Severity: high**, because it is attached to the paper's causal argument rather than a descriptive one.

**Aggravating factor nobody has flagged:** the grid's coefficients **diverge sharply from the empirical ones** — ⟨k⟩'s β rises 0.526 → 0.933 while D's β collapses 0.408 → 0.067. Left unstated, a reader will read this as an internal contradiction: the synthetic model says D barely matters, the empirical data says D contributes β = 0.408 at p = 1.5e-07. **The paper must address this divergence directly**; the extrapolated range is the most plausible explanation and also the easiest to test.

**Fix (~5 minutes of compute):** refit the n = 42 grid OLS restricted to grids with **⟨k⟩ ≤ 2.99** and report the restricted β's and n. Then state the scope condition in Mesgaran's vocabulary: *"the grid spans Type 1 novelty above ⟨k⟩ = 2.99; the causal claim is asserted only over the empirically realised range, where the restricted fit gives β = …"* Add a two-row table of synthetic vs empirical ranges for both predictors. This converts an unforced error into a stated limitation *and* likely explains the β divergence.

---

### 5. Absence of phylogenetic correction — MODERATE-TO-SERIOUS, journal-dependent
**Objection:** "You treat 100+ species as independent observations. Freckleton 2009."

**Severity: moderate on the science, high on the reviewer-reflex axis** — in a plant-biology venue this objection is close to automatic.

**The paper has a genuinely good substantive defence that it should make first:** p_c, ⟨k⟩ and D are all **properties of the same measured network**. The regression is a geometric/physical relation among co-measured properties of one object, not an evolutionary correlation between two independently evolving traits across a clade. Shared ancestry inflates the *sampling* of the predictor range; it does not create the p_c–⟨k⟩ relationship, which holds within the synthetic grids where no phylogeny exists. **That last clause is the strongest argument available and it is already in the paper's data.**

**But make the defence *and* run the check.** Per Revell 2010, phylogenetic signal must be assessed in the **residuals**, not the traits — and if residual λ ≈ 0, **OLS is the more accurate estimator and PGLS would be the error.** Concrete path: species list → V.PhyloMaker/GBOTB → Pagel's λ (with its likelihood-ratio p) on the residuals of p_c ~ ⟨k⟩ + D. Report λ. Either outcome is publishable; only the *absence* of the number is exposed.

**Separate and independent issue:** 120 leaves but only ~93–112 species implies **multiple leaves per species in at least some cohorts**. That is ordinary pseudoreplication and has nothing to do with phylogeny. State the leaves-per-species distribution; if it is not 1:1, either average within species or fit a species random effect as a sensitivity analysis.

---

### 6. Reporting r = 0.999999999999996 — MODERATE severity, HIGH credibility cost; the ratio fix is right but incomplete
**Assessment of the existing fix: correct in substance, insufficient in presentation.** Replacing "correlation proves equality" with ratio statistics (worst per-leaf CV 1.12e-07, worst median-ratio departure 6.1e-08, tolerance 1e-06) is exactly the right move — that is a **tolerance check**, which is what a numerical verification should be. Four things still need doing:

**(a) Delete the 16-digit r entirely.** Double-precision epsilon is 2.2e-16; sixteen significant figures in a Pearson r computed over 5.67M values is at or below the floating-point noise floor, so the trailing digits are **numerically meaningless**. A reviewer who knows floating point will spot this instantly, and it will cost credibility on results that deserve none of that doubt. Morris et al.'s rule — never present to greater accuracy than the error justifies — applies verbatim.

**(b) Drop the associated p-value.** At n = 5,668,467, any p-value is structurally zero (Lin, Lucas & Shmueli).

**(c) Put the wrong-exponent control on the ratio scale too.** Currently the test is expressed as ratios and the control as a correlation (r = 0.953) — they are not comparable. Under a wrong exponent the model/source ratio would depart by orders of magnitude; contrasted against a worst departure of 6.1e-08, that is a **far** more compelling demonstration than 0.9999… vs 0.953.

**(d) Rename it.** This is **verification** (is Hagen–Poiseuille implemented correctly?), not **validation** (does Hagen–Poiseuille describe real leaves?). Calling a self-consistency check "validation" invites the accusation that a tautology is being sold as empirical support. The genuine validation is the K_leaf check — which is non-significant, and should be reported as the honest, underpowered result it is (see Cheap Wins).

---

### 7. Unequal trial budgets between nested cohorts — MODERATE
**Objection:** "The 100-leaf percolation cohort ran 2,400 trials per leaf per mode; the 105-leaf enhancement cohort ran 10,000. These are nested cohorts. Why?"

**Severity: moderate** on its own — it becomes serious only through its coupling to exposure #3.

**Fix (no rerun needed):** state the MCSEs and the reason. At the threshold, P(collapse) = 0.50 by construction, so this is the worst case for a proportion: **2,400 → MCSE 0.0102; 10,000 → MCSE 0.0050**. Morris et al.'s worked example makes 10,000 the *justified* budget for 0.5% precision on a 50% quantity. So the honest framing is: *"the enhancement cohort was run at 10,000 trials because its estimand is a paired difference of order 0.01, requiring roughly twice the per-leaf precision of the marginal p_c estimates; the 2,400-trial budget gives MCSE ≈ 0.010 at the threshold, adequate for a cross-leaf correlation with ρ = 0.73 but not for a difference of 0.0095."* That reframes an inconsistency as a **design decision matched to estimand precision**, which is exactly what Koehler et al. ask for.

**Caveat on the arithmetic:** √(p(1−p)/n) is the MCSE of the *collapse probability*, not of p_c. Propagate through the slope at the crossing, or bootstrap the trial outcomes and re-solve the threshold — the paper already has bootstrap code from the synthetic reference.

---

### 8. Shapiro–Wilk as a test-selection gate — MODERATE, cheaply neutralised
**Objection:** "You used a normality test to choose your tests. Rochon et al. 2012 showed this distorts conditional Type I error (10.8%–17.0% against nominal 5%)."

**Severity: moderate** — the practice is criticised, but the paper's *specific* implementation is the defensible variant and is one clause away from being airtight.

**Why the paper is fine:** the rule was **pre-specified** and applied **uniformly to all association tests**. That is Rochon's own recommended fallback ("simply use nonparametric tests unconditionally"). The condemned practice is per-variable selection.

**Why it must be said explicitly:** the four W statistics **disagree** — loop fraction (p = 0.089) does not reject normality while p_c (p = 5.1e-06) rejects hard and mean degree (p = 0.027) rejects marginally. A per-variable rule would have produced a visibly incoherent mix of Pearson and Spearman across a single correlation table. The uniformity is what saves it, and it is currently implicit. One clause: *"the rule was applied uniformly to all association tests regardless of any individual variable's W; no test was selected post hoc."*

**Second, subtler problem:** Shapiro–Wilk on the **marginal** distributions does not test what the multiple regression assumes. OLS assumes normality of **residuals**. The four reported W tests neither license nor forbid the regression — they are answering the wrong question. See Cheap Wins.

**Third, a credibility item:** "pre-specified" is unverifiable without a time-stamped record. Either point to the version-controlled analysis script and its commit date, or soften to "applied uniformly."

---

### 9. No multiple-comparison control — MODERATE, foreclosed by one sentence
**Objection:** "You report roughly fifteen to seventeen hypothesis tests with no correction."

**Severity: moderate as raised, negligible in substance** — because the paper's p-values are absurd. Counting the primary tests (3 Spearman associations, 2 partials, 1 residual test, 2 regression F's, 1 grid F, 2 Wilcoxons, 1 Mann-Whitney, 1 K_leaf Spearman ≈ 14), Bonferroni at α = 0.05/14 = **0.0036**. Every significant result clears that by ten or more orders of magnitude, and the only non-significant one (K_leaf, p = 0.073) remains non-significant.

**Fix:** one sentence, no compute: *"Benjamini–Hochberg control across the K primary tests changes no conclusion; the largest significant p is [X] against a BH threshold of [Y], and the single non-significant result (K_leaf, p = 0.073) remains so."* **Use BH, not Bonferroni** — the tests are positively dependent through nested cohorts and shared variables, and the aim is discovery.

**The one place multiplicity cuts the other way:** the K_leaf result at p = 0.073 must not be reported as "no relationship." That is an absence-of-evidence error and it is the paper's *only* external empirical validation. See Cheap Wins.

---

### 10. Bootstrap CI method unspecified — MINOR
"Bootstrap 95% CIs" without naming percentile vs BCa or the number of resamples. p_c is a threshold of a monotone sigmoid, so skew is possible in principle and BCa's second-order accuracy would matter in a smaller run. **Fix:** name the method and B in Methods; add the observation that at 1e6 trials the half-width is ±0.001 and the choice is immaterial. Optionally report both for one case. **Severity: minor**, fully foreclosed by naming.

---

### 11. Finite-size sweep — CORRECTLY HANDLED, but under-exploited
Declining to claim anything from p_c falling 0.2701 → 0.0772 while loop fraction drifts is **the right call** and should be presented as a declared scope limitation rather than quietly omitted. **Report the loop-fraction series numerically next to the p_c series** so the reader can see *why* no claim is made — that is a positive display of rigour.

**But there is a live risk here that the paper must close.** A reviewer will ask the obvious follow-up: *"if p_c depends this strongly on N, are your cross-leaf p_c comparisons confounded by leaf network size?"* The empirical leaves span some range of N. **Report the Spearman correlation between per-leaf N and per-leaf p_c across the n = 100 cohort.** If it is near zero, the entire finite-size worry is defused for every empirical claim in the paper. If it is not, the authors urgently need to know before a reviewer tells them. This is one line of code and it is the **single most important missing diagnostic in the manuscript.**

---

## CHEAP WINS

Ordered by return per minute.

**1. Report the VIF of the actual regression — it is ≈ 1.02, and this kills exposure #1 for the model.** *(5 minutes, pure arithmetic.)*
The 0.994 collinearity does **not** contaminate the multiple regression, and the paper can prove it from numbers already in hand. For two standardized predictors, β₁ = (r₁ − r₂·r₁₂)/(1 − r₁₂²). Substituting the reported values (β₁ = 0.526, r₁ = 0.587, r₂ = 0.486) and solving:

> r₁₂ = 0.15 → β₁ = (0.587 − 0.486·0.15)/(1 − 0.0225) = 0.5141/0.9775 = **0.526** ✓
> and β₂ = (0.486 − 0.587·0.15)/0.9775 = 0.39795/0.9775 = **0.407** vs reported 0.408 ✓

So **Pearson r(⟨k⟩, D) ≈ 0.15**, giving **VIF = 1/(1 − 0.15²) = 1.023** for both predictors. This is consistent with the reported partial Spearmans barely moving from their marginals (0.7355 vs 0.733; 0.5025 vs 0.496). Confirm r₁₂ directly from the data and report: *"⟨k⟩ and D are near-orthogonal in this cohort (r = 0.15, VIF = 1.02); the regression coefficients are not collinearity-affected."* **Buys:** complete immunity for the headline model, and localises the 0.994 problem to a descriptive table where the existing residual test already handles it.

**2. Add the three effect sizes.** *(10 minutes, arithmetic only — all computed in Tier 1/Tier 2 above.)* r_rb = 1.00 (100/100 leaves), r_rb = 0.99 (93/105, 0 worsened), Cliff's δ ≈ 0.99 for the quartiles. **Buys:** closes the "p-values without effect sizes" objection outright — the most common single statistical criticism in review.

**3. Spearman ρ(N, p_c) across the n = 100 cohort.** *(1 line of code.)* Directly tests whether the finite-size sweep's N-dependence confounds the empirical results. **Buys:** defuses the entire finite-size limitation for every empirical claim — or reveals a real problem while it is still fixable. Highest information-per-keystroke in this list.

**4. Put a CI on the K_leaf Spearman instead of calling it null.** *(2 minutes.)* ρ = 0.187, n = 93. Fisher z = atanh(0.187) = 0.1892; Bonett–Wright SE = 1.03/√90 = 0.1086; 95% z-interval 0.1892 ± 0.2128 → back-transformed **ρ ≈ [−0.02, 0.38]**. Report: *"ρ = 0.187, 95% CI [−0.02, 0.38] — consistent with anything from no relationship to a moderate positive one. This check is underpowered, not negative."* **Buys:** converts the paper's weakest result from an apparent failed validation into an honest precision statement, and pre-empts the absence-of-evidence objection. Also the single most intellectually honest change available.

**5. Shapiro–Wilk (or a QQ plot) on the multiple-regression *residuals*, n = 100.** *(1 line.)* The four existing W tests are on marginals and do not test the model's assumption. **Buys:** answers the assumption question that was actually asked, and lets the paper cite Revell's residuals-not-traits logic consistently across both the OLS and the phylogenetic discussion.

**6. Pratt-variant Wilcoxon on the enhancement.** *(1 line — `scipy.stats.wilcoxon(..., zero_method='pratt')`.)* With W = 0 on 93 positive differences it cannot change the conclusion. **Buys:** forecloses the ties objection at zero risk. Pair with one sentence explaining *why* 12 differences are exactly zero (p_c evaluated on a discrete k/N grid) — otherwise exact ties in a continuous quantity look like a bug.

**7. One BH sentence.** *(5 minutes of arithmetic.)* Rank the ~14 primary p-values, compare to i·α/m, report that nothing changes. **Buys:** closes exposure #9 permanently.

**8. Refit the synthetic grid OLS restricted to ⟨k⟩ ≤ 2.99.** *(~5 minutes.)* Report restricted n and β's. **Buys:** closes exposure #4 *and* very likely explains the β divergence (0.933 vs 0.526 for ⟨k⟩; 0.067 vs 0.408 for D) that a reviewer would otherwise read as a contradiction between the paper's two halves.

**9. State the MCSEs and whether common random numbers were used.** *(2 minutes if the answer is known.)* MCSE 0.0102 at 2,400 and 0.0050 at 10,000 at the threshold; then the paired-difference precision statement. **Buys:** exposures #3 and #7 together — the highest-severity pair on the list.

**10. Add the planar-identity sentence for loop fraction ≈ 1 − 2/⟨k⟩.** *(5 minutes, verify against the code's definition.)* **Buys:** turns the 0.994 from a red flag into evidence of command of the material.

**11. Pagel's λ on the regression residuals via V.PhyloMaker.** *(~1 hour — the only item that might exceed the budget, and worth it.)* **Buys:** neutralises the most reflexive objection in plant-biology review, and per Revell a λ ≈ 0 result actively *justifies* the OLS already reported rather than forcing a refit.

---

## WHAT NOT TO DO

- **Do not add a normality appendix or more Shapiro–Wilk tests.** The existing four are already answering the wrong question (marginals, not residuals). Adding more compounds the exposure. Replace, do not extend.
- **Do not add a Bonferroni-corrected table of every p-value.** One BH sentence does the entire job. A correction table draws attention to multiplicity while demonstrating nothing, since every p clears any threshold by ten orders of magnitude.
- **Do not add ANOVA.** Correctly avoided already; the designs here are correlational and paired, and ANOVA would answer nothing the regressions and Wilcoxons do not.
- **Do not ridge-regress, PCA, or otherwise regularise the ⟨k⟩ / loop-fraction pair.** They are the same quantity by Euler's formula. Regularisation would obscure a relationship that should simply be *stated* and one variable dropped. Dormann's shrinkage remedies are for genuinely distinct-but-correlated ecological covariates; that is not this case.
- **Do not add a Bayesian reanalysis or Bayes factors.** With ρ = 0.73 at n = 100 and W = 0 at n = 100, no posterior will differ from the frequentist conclusion, and it doubles the methods section.
- **Do not compute post hoc power** for the non-significant K_leaf test. Observed power is a deterministic function of the p-value and adds nothing; the confidence interval (Cheap Win 4) is the correct and more informative answer.
- **Do not bootstrap the Spearman correlations that already have p ≈ 1e-17/1e-18.** Nobody doubts them, and the CIs will be uninformatively narrow.
- **Do not run a full PGLS if residual λ ≈ 0.** Report λ and cite Revell 2010 — the paper explicitly finds OLS *more accurate* than PGLS when residuals lack signal, so a gratuitous PGLS would be the methodological error, not the fix.
- **Do not run the Mesgaran ExDet tool.** Cite the Type 1 / Type 2 novelty vocabulary; the univariate range comparison (4.00 vs 2.99) is the whole argument and needs no software.
- **Do not write a paragraph about the p-value reform literature.** One ASA citation plus the effect sizes does all the work. A methodological digression signals defensiveness.
- **Do not equalise the trial budgets by re-running the 100-leaf cohort at 10,000** unless Cheap Win 9 reveals that common random numbers were *not* used in the paired comparisons. Justifying the budgets against precision targets is the correct response; burning compute to make two numbers match is not.
- **Do not replace the Mann-Whitney quartile test with a permutation test.** The conclusion is identical (U = 4 out of ~676 possible); the effect size is the gap, not the test.

---

## WHAT I COULD NOT FIND

- **Verified DOIs** for Felsenstein (1985), Benjamini & Hochberg (1995), Cliff (1993), and Efron (1987). The web-search budget (200 calls) was exhausted mid-task and every publisher page attempted afterward returned HTTP 403. The **citations** (authors, year, title, journal, volume, pages) are verified from multiple independent records; only the DOI strings are unconfirmed. **Specific warning:** the JASA 82(397) DOI that surfaced in search — 10.1080/01621459.1987.10478409 — attaches to a *different* article title ("Bootstrap Confidence Intervals and Bootstrap Approximations"), not Efron's "Better bootstrap confidence intervals." Do not use it. Verify all four against CrossRef before the reference list is finalised.
- **The Jin & Qian (2019) DOI** (10.1111/ecog.04434) is *inferred* from the journal's own "ECOG-04434" appendix identifier, not read from the article record. Verify.
- **The specific |r| threshold in Dormann et al. (2013).** The widely quoted |r| > 0.7 figure could not be confirmed — Wiley, HAL (Anubis-protected) and Semantic Scholar all failed to return the full abstract or text. Do not attribute a specific numeric threshold to Dormann without opening the PDF.
- **Full text of Kerby (2014)** (SAGE 403). The matched-pairs rank-biserial definition given above is corroborated by the R `effectsize::rank_biserial` documentation and the pingouin issue tracker, both of which cite Kerby explicitly and agree on the formula. The arithmetic I performed follows directly from the definition and is independently checkable.
- **Full text of Revell (2010)** — the PDF downloaded but this environment lacks poppler-utils, so it could not be rendered. The residuals-not-traits result and the OLS-beats-PGLS-when-residuals-are-signal-free finding are taken from the search-returned abstract summary and are consistent with the paper's well-known content, but I did not read them in the original.
- **Any methodological source addressing trial-budget allocation across *nested* cohorts of differing size specifically.** I found nothing on this exact design question. The Morris/Koehler MCSE-against-a-precision-target framework is the closest applicable guidance and is, I judge, sufficient — but the paper should present it as *applying* general MCSE logic rather than citing a specific precedent, because I do not believe one exists.
- **Any discipline-specific reporting standard for percolation-threshold uncertainty.** No physics- or network-science-specific reporting guideline surfaced. ADEMP is the best available framework and transfers cleanly, but it comes from biostatistics and should be cited as an adopted framework, not a field norm.
- **Whether the paper's bootstrap is percentile or BCa, and whether common random numbers were used across the paired baseline/enhanced runs.** Both are internal to the manuscript and code, not the literature. Both are load-bearing for exposures #10 and #3 respectively. **Someone needs to check the code.**

**Sources:**
[Morris, White & Crowther 2019 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6492164/) · [Morris et al. publisher record](https://onlinelibrary.wiley.com/doi/10.1002/sim.8086) · [Koehler, Brown & Haneuse 2009 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3337209/) · [Koehler et al. publisher record](https://www.tandfonline.com/doi/abs/10.1198/tast.2009.0030) · [Rochon, Gondan & Kieser 2012 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3444333/) · [Pratt 1959](https://www.tandfonline.com/doi/abs/10.1080/01621459.1959.10501526) · [Kerby 2014](https://journals.sagepub.com/doi/10.2466/11.IT.3.1) · [effectsize::rank_biserial documentation](https://easystats.github.io/effectsize/reference/rank_biserial.html) · [Dormann et al. 2013](https://nsojournals.onlinelibrary.wiley.com/doi/10.1111/j.1600-0587.2012.07348.x) · [Freckleton 2009](https://onlinelibrary.wiley.com/doi/10.1111/j.1420-9101.2009.01757.x) · [Revell 2010](https://besjournals.onlinelibrary.wiley.com/doi/abs/10.1111/j.2041-210X.2010.00044.x) · [Nakagawa & Cuthill 2007](https://onlinelibrary.wiley.com/doi/10.1111/j.1469-185X.2007.00027.x) · [Wasserstein & Lazar 2016](https://www.tandfonline.com/doi/abs/10.1080/00031305.2016.1154108) · [Lin, Lucas & Shmueli 2013](https://pubsonline.informs.org/doi/10.1287/isre.2013.0480) · [Benjamini & Hochberg 1995](https://cris.tau.ac.il/en/publications/controlling-the-false-discovery-rate-a-practical-and-powerful-app-2/) · [Cliff 1993](https://www.ovid.com/journals/plbul/abstract/00006823-199311000-00007~dominance-statistics-ordinal-analyses-to-answer-ordinal) · [Felsenstein 1985 (revisited)](https://www.journals.uchicago.edu/doi/10.1086/703055) · [Jin & Qian 2019 V.PhyloMaker](https://www.ecography.org/accepted-article/vphylomaker-r-package-can-generate-very-large-phylogenies-vascular-plants) · [Ernst 2004](https://projecteuclid.org/journals/statistical-science/volume-19/issue-4/Permutation-Methods-A-Basis-for-Exact-Inference/10.1214/088342304000000396.full) · [Thabane et al. 2013](https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/1471-2288-13-92) · [Boulesteix et al. 2018](https://onlinelibrary.wiley.com/doi/10.1002/bimj.201700129) · [Mesgaran et al. 2014](https://onlinelibrary.wiley.com/doi/abs/10.1111/ddi.12209) · [Efron 1987 (JASA 82/397 record)](https://www.tandfonline.com/doi/abs/10.1080/01621459.1987.10478409)
agentId: aa530c2122bcd6a67 (use SendMessage with to: 'aa530c2122bcd6a67', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 95603
tool_uses: 36
duration_ms: 664985</usage>