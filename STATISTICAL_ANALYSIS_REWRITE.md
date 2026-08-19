# Statistical Analysis — replacement section

Drop-in replacement for the *Statistical Analysis* subsection of the Methods
(current pp. 15–18). Formulas are given in plain text for re-entry into the Word
equation editor; each is followed by a *where* block in the same style as the
existing section.

Corrections folded in relative to the current draft:

- collapse criterion restated as the GCC half-size rule actually used (Results p. 38),
  not "a spanning connected cluster";
- the four real trial budgets replace the single "about 10,000";
- the bootstrap is specified (percentile, B = 200, 50,000-trial cap) and its
  conservatism disclosed;
- eight previously undescribed tests added (Mann–Whitney U, Cliff's δ,
  Kruskal–Wallis H, rank-biserial r, sign test, Pratt treatment, Gini, quartile
  binning);
- α, multiple-comparison policy, phylogenetic-correction policy, common random
  numbers and seeding declared.

---

## Statistical Analysis

All statistical procedures were carried out in Python 3.13 using NumPy, SciPy and
scikit-learn. All inferential tests were two-sided and evaluated at α = 0.05. Because
the analysis is exploratory across a fixed set of pre-specified architectural predictors,
no correction for multiple comparisons was applied; the number of tests reported is
therefore stated wherever a family of tests appears, and no single p-value is
interpreted as confirmatory in isolation. Every simulation was run from a fixed random
seed, and the seed and trial budget are recorded with each result so that any figure or
table can be regenerated exactly.

### Descriptive Summaries

Each structural and hydraulic metric — fractal dimension, hydraulic conductance, degree
distribution, reticulation density and GCC size — was summarised across the empirical
and synthetic cohorts by the mean, standard deviation, median and range.

```
x̄ = (Σ xᵢ) / n

s = √[ Σ(xᵢ − x̄)² / (n − 1) ]

⟨k⟩ = 2E / N
```

where

    x̄  = the sample mean of a metric
    xᵢ  = the i-th observed value of that metric
    n   = the number of networks in the cohort
    s   = the sample standard deviation
    Σ   = summation over all observations
    ⟨k⟩ = the mean degree
    E   = the number of edges (vein segments)
    N   = the number of nodes (junctions)

Quantities whose distributions were non-normal are reported by the median and range
alongside the mean and standard deviation.

### Collapse Probability and the Critical Threshold

The probability of structural collapse at a given removal fraction was estimated by
Monte Carlo simulation as the proportion of independent trials in which the giant
connected component fell below half of its undamaged size.

```
P(collapse) = m_collapse / N_trials
```

where

    P(collapse) = the estimated probability of collapse at a given removal fraction
    m_collapse  = the number of Monte Carlo trials in which the GCC fell below half
                  its undamaged size
    N_trials    = the total number of Monte Carlo trials at that removal fraction

This half-size rule was adopted in preference to a spanning-cluster criterion because it
can be applied consistently to networks spanning roughly four and a half orders of
magnitude in size. It is an operational threshold rather than a critical point, and no
claim of universality or of a critical exponent is made from it.

Trial budgets differed by experimental unit and are identified wherever a result is
reported. The empirical percolation cohort was evaluated at 2,400 trials per network per
attack strategy; the enhancement cohort at 10,000 trials per network per arm, because its
estimand is a paired difference of order 0.01 and therefore requires a finer resolution;
the synthetic reference network at 1,000,000 trials under random removal and 100,000
under each targeted strategy; and the coupled haustorial-density surface at 6,000 trials
per cell. Following the reporting framework of Morris et al. (2019), each budget is
justified against a target precision rather than by convention, and the Monte Carlo
standard error of the collapse probability follows the binomial form.

```
SE(P̂) = √[ P̂(1 − P̂) / N_trials ]
```

where

    SE(P̂)    = the Monte Carlo standard error of the estimated collapse probability
    P̂        = the estimated collapse probability at that removal fraction
    N_trials = the number of trials at that removal fraction

At the threshold, where P = 0.50 and the standard error is largest, this gives 0.0102 at
2,400 trials and 0.0050 at 10,000 trials on the survival-probability scale.

A logistic model was fitted to the collapse curve and the critical threshold was taken as
its inflection point, the cut point at which the fitted probabilities are bisected
(Zhang et al., 2020).

```
P(collapse) = 1 / (1 + exp[−(wρ + b)])

p_c = −b / w
```

where

    exp[] = the exponential function, e raised to the bracketed quantity
    ρ     = the removal fraction (fraction of nodes removed)
    w     = the fitted logistic slope coefficient
    b     = the fitted logistic intercept
    p_c   = the critical removed fraction at the inflection point

Where the fitted inflection fell outside the swept range of ρ, the direct 0.5-crossing of
the empirical curve was used instead.

### Confidence Intervals

Each threshold carries a 95% confidence interval obtained by resampling the Monte Carlo
trial outcomes and re-solving the threshold on each resample. The interval is a
percentile interval taken from B = 200 bootstrap replicates (Efron & Tibshirani, 1993),
with the resample size capped at 50,000 trials.

```
CI₉₅ = [ θ*(0.025), θ*(0.975) ]
```

where

    CI₉₅ = the 95% confidence interval for the threshold
    θ*   = a bootstrap replicate of the estimated threshold
    B    = the number of bootstrap replicates (200)

Because of the 50,000-trial cap, intervals computed on runs that exceed 50,000 trials are
conservative — wider than the nominal interval by a factor of approximately
√(N_trials / 50,000), which is 1.41 at 100,000 trials and 4.47 at 1,000,000 trials. The
reported intervals are therefore upper bounds on the true width and are never narrower
than the sampling uncertainty warrants.

### Distributional Screening and Correlation

The choice of correlation coefficient was governed by a Shapiro–Wilk test of normality on
each variable (Shapiro & Wilk, 1965). Pearson's r was used where both variables were
approximately normal and their relationship approximately linear; otherwise the
rank-based Spearman's ρ was used (Wisniewski & Brannan, 2024).

```
W = (Σᵢ aᵢ x₍ᵢ₎)² / Σᵢ (xᵢ − x̄)²

r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[ Σ(xᵢ − x̄)² Σ(yᵢ − ȳ)² ]

ρ = 1 − [ 6 Σᵢ₌₁ⁿ dᵢ² ] / [ n(n² − 1) ]
```

where

    W     = the Shapiro–Wilk normality test statistic (nearer 1 = more normal)
    aᵢ    = the Shapiro–Wilk weighting constants
    x₍ᵢ₎  = the i-th order statistic (the data sorted in ascending order)
    r     = the Pearson product-moment correlation coefficient
    xᵢ, yᵢ = the paired values of a predictor and p_c for leaf i
    x̄, ȳ  = the means of x and y
    ρ     = the Spearman rank-correlation coefficient
    dᵢ    = the difference between the ranks of xᵢ and yᵢ
    n     = the number of leaves

### Isolating the Unique Contribution of Each Predictor

The unique contribution of each architectural predictor was isolated by partial
correlation and by a standardised multiple linear regression (Wisniewski & Brannan,
2024), and collinearity among predictors was assessed by the variance inflation factor
(Dormann et al., 2013).

```
r(xy·z) = (r_xy − r_xz · r_yz) / √[ (1 − r_xz²)(1 − r_yz²) ]

p_c = β₀ + β₁⟨k⟩ + β₂D + ε

VIF_j = 1 / (1 − R_j²)
```

where

    r(xy·z)          = the partial correlation of x and y controlling for z
    r_xy, r_xz, r_yz = the pairwise correlations among x, y and z
    β₀, β₁, β₂       = the regression intercept and slope coefficients
    D                = the fractal dimension
    ε                = the residual (error) term
    VIF_j            = the variance inflation factor for predictor j
    R_j²             = the R² from regressing predictor j on the remaining predictors

Overall model fit was tested by the F-statistic for the regression, and the model R² is
reported for the full two-predictor model. Because fractal dimension was strongly related
to network extent, each architecture–threshold association was recomputed with log network
size partialled out, and fractal dimension was additionally residualised on log network
size and the residual re-correlated with the threshold. Because mean degree and loop
fraction were very highly rank-correlated, their relationship was characterised by a cubic
model of loop fraction on mean degree, and only mean degree was entered in the regressions;
loop fraction was retained descriptively.

### Paired Comparisons Between Removal Modes

Removal modes were compared on identical networks with the Wilcoxon signed-rank test, a
paired distribution-free test appropriate because the two thresholds are measured on the
same leaves (Wilcoxon, 1945).

```
dᵢ = p_c(random)ᵢ − p_c(degree)ᵢ

W = Σ sgn(dᵢ) Rᵢ
```

where

    dᵢ  = the paired difference in p_c for leaf i between the two strategies
    Rᵢ  = the rank of the absolute difference |dᵢ|
    sgn = the sign function (+1, 0 or −1)
    W   = the Wilcoxon signed-rank test statistic

Zero differences were handled two ways and both are reported: by Wilcoxon's exclusion
convention, which discards them, and by the more conservative Pratt treatment, which
retains and ranks them (Pratt, 1959). Because a signed-rank statistic of W = 0 yields a
p-value that is a function of sample size alone, the direction and magnitude of each
paired contrast are reported separately — direction by the matched-pairs rank-biserial
correlation (Kerby, 2014), magnitude by the median paired difference.

```
r_rb = (W₊ − W₋) / (W₊ + W₋)
```

where

    r_rb = the matched-pairs rank-biserial correlation
    W₊   = the sum of ranks of the positive differences
    W₋   = the sum of ranks of the negative differences

A value of r_rb = 1.00 indicates that every pair moved in the same direction and carries
no information about effect size.

### Group Comparisons

To test whether damage tolerance varied with reticulation, networks were sorted into
quartiles of loop fraction and the least- and most-reticulate quartiles compared by the
Mann–Whitney U test (Mann & Whitney, 1947), with Cliff's δ reported as the accompanying
effect size (Cliff, 1993).

```
U = n₁n₂ + n₁(n₁ + 1)/2 − R₁

δ = [ #(xᵢ > yⱼ) − #(xᵢ < yⱼ) ] / (n₁n₂)
```

where

    U       = the Mann–Whitney rank-sum statistic
    n₁, n₂  = the group sizes
    R₁      = the sum of ranks in the first group
    δ       = Cliff's delta, the degree of non-overlap between the two groups
    #(·)    = the count of pairs satisfying the stated relation

Differences among the four tracing-quality grades were tested by the Kruskal–Wallis
test (Kruskal & Wallis, 1952), which treats the grades as unordered groups. This is the correct treatment here
because grades B, C and D denote different defect types with opposite expected effects on
apparent connectivity, and do not form an ordered quality scale.

```
H = [ 12 / (N(N + 1)) ] Σⱼ (Rⱼ² / nⱼ) − 3(N + 1)
```

where

    H  = the Kruskal–Wallis test statistic
    N  = the total number of observations across all groups
    Rⱼ = the sum of ranks in group j
    nⱼ = the number of observations in group j

Within subsets too small for a rank test, the direction of the effect was tested by an
exact sign test against a null of equal probability of improvement and worsening
(Dixon & Mood, 1946).

```
p = 2 · P(X ≥ k),   X ~ Binomial(m, 0.5)
```

where

    p = the two-sided exact p-value
    k = the number of networks improving
    m = the number of networks showing any change
    X = a binomial random variable under the null of no directional effect

### Concentration of Removal Weights

Because degree-weighted and betweenness-weighted removal draw nodes with probability
proportional to a centrality score, the concentration of those scores determines how far
a weighted mode departs from uniform removal. Concentration was quantified by the Gini
coefficient of the weight distribution (Dorfman, 1979), reported alongside the number of
distinct weight values and the ratio of the maximum weight to the mean.

```
G = Σᵢ Σⱼ |wᵢ − wⱼ| / (2n² w̄)
```

where

    G      = the Gini coefficient of the removal-weight distribution (0 = uniform)
    wᵢ, wⱼ = the removal weights of nodes i and j
    w̄      = the mean removal weight
    n      = the number of nodes

Removal probabilities were clipped at unity, so for heavy-tailed weights the realised
removed fraction can fall below the nominal parameter; only the realised fraction is
compared across removal modes.

### The Reticulation-Enhancement Contrast

The change in threshold produced by loop addition is the within-network paired
difference.

```
Δp_c = p_c(suggested) − p_c(current)
```

where

    Δp_c            = the change in critical threshold produced by adding loops
    p_c(current)    = the threshold of the real, re-graphed leaf
    p_c(suggested)  = the threshold of the same leaf after loop addition

Each network served as its own control: only the edge set was altered, the node set was
held fixed, and both arms were driven by common random numbers, so that the same sequence
of removal draws was applied to the baseline and enhanced graphs (Morris et al., 2019). Monte Carlo variation is
therefore shared between the arms rather than added to their difference. Species identity,
tracing quality, network size, leaf shape, crop-window geometry and phylogeny are constant
within a pair by construction.

The difference was tested against zero with the Wilcoxon signed-rank test, or with a
paired t-test where the differences were approximately normal, and is reported with the
proportion of networks improved, unchanged and worsened. Its dependence on each network's
initial architecture was examined by linear regression.

```
t = d̄ / (s_d / √n)

Δp_c = β₀ + β₁⟨k⟩₀ + β₂D + ε
```

where

    t     = the paired t-statistic
    d̄     = the mean of the paired differences
    s_d   = the standard deviation of the paired differences
    n     = the number of leaves
    ⟨k⟩₀  = the leaf's initial mean degree
    D     = the fractal dimension
    β₀, β₁, β₂ = the regression coefficients
    ε     = the residual (error) term

### Sensitivity and Robustness Analyses

For every architecture and threshold result, a sensitivity analysis restricted to the
highest-quality tracings is reported alongside the full-cohort result, so that any
inflation of an effect by imperfect tracing is disclosed. The following additional
analyses were run and are reported in the Results and Supplementary Materials: the
connectivity criterion was varied between the giant-component and source-anchored
definitions on identical removal draws; damage geometry was varied between dispersed
removal and contiguous-disc lesions at matched realised removed fractions, using a single
lesion and ten lesions; the hydraulic resistance convention was varied between ℓ/r⁴ and
ℓ/r²; the cavitation threshold was swept from −1.00 to −3.00 MPa and the host operating
potential from −0.5 to −2.5 MPa; network size was swept from N = 1,023 to N = 16,383 with
fractal dimension and mean degree pinned by construction; and the cohort was re-analysed
excluding over-segmented networks and excluding networks with a baseline giant-component
fraction at or below 0.99.

Model implementation was checked against the source dataset by comparing modelled
Hagen–Poiseuille resistance with the resistance column shipped with the data, vein by
vein, using the per-leaf coefficient of variation and the median departure from unity of
the modelled-to-source ratio against a pre-set tolerance of 1 × 10⁻⁶, with a
deliberately wrong exponent as a negative control. Modelled whole-network conductance was
additionally compared with independently measured leaf hydraulic conductance by Spearman
correlation across the species for which both were available.

### Declared Limitations of the Analysis

Three limitations of the statistical design are stated here rather than left implicit.
No phylogenetic correction was applied, so the species are treated as independent
observations although the sample spans ferns and angiosperms; this affects the p-values
but not the point estimates. No correction for multiple comparisons was applied, as
noted above. And the bootstrap intervals are conservative for runs exceeding the
50,000-trial resample cap, as quantified above.
