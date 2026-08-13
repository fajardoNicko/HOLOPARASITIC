# Robustness Ceiling — Result + Discussion draft (hypothesis-framed)

## The result (data/robustness_ceiling.csv, _summary.json)

Using the causal response surface fitted on the synthetic grid,
**p_c = −0.091 + 0.120·⟨k⟩ + 0.029·D** (R² = 0.89), we estimated, for each of the 100 cohort species,
how much its percolation threshold could rise if its venation moved toward the reticulate end of the
**biologically observed** range (⟨k⟩ capped at the cohort's 90th percentile, 2.81), holding fractal
dimension fixed.

- **Reticulation is the dominant lever for 89% of species.** Raising D helps far less.
- **Median achievable gain: Δp_c ≈ +0.036** (≈3.6 percentage points more of the network removable before
  collapse); **maximum ≈ +0.080** (Chl_spi). Top headroom: *Chloranthus spicatus, Magnolia chevalieri,
  Metrosideros davisii, Anemone calva, Helwingia chinensis.*
- Gain from raising D to its observed ceiling: median **+0.005** — small, and bounded anyway by the
  generator's D≈1.81 ceiling.

**Interpretation.** The most sink-resistant direction in venation space is *more reticulation / more closed
loops* (higher mean degree), not higher fractal dimension. Species currently at the sparse end have the
most latent robustness to gain; species already reticulate are near their ceiling.

## Discussion draft — *implications and a proposed research pathway (a hypothesis)*

> The response-surface analysis lets us ask a design question: for each species, how much more sink-
> resistant could its venation be? Holding branching geometry and fractal dimension fixed and raising mean
> degree only to the level already observed among the most reticulate species in the cohort, the model
> predicts a median gain of ~0.036 in p_c, with reticulation the dominant lever for 89% of species. This
> identifies a *constrained optimum* — the more sink-resistant architecture achievable without exceeding
> the reticulation, and therefore roughly the construction cost, that real leaves already tolerate.
>
> We stress what this is and is not. It is a first-order, model-based estimate of a direction and its
> magnitude, not a designed "parasite-proof leaf." A real leaf cannot freely maximise reticulation: denser
> venation raises construction cost and can trade against hydraulic efficiency and other leaf functions
> (Matos et al., 2024). The estimate therefore describes headroom within observed bounds, not a target to
> push past them. Most importantly, holoparasite resistance in planta is overwhelmingly molecular and
> chemical — haustorial incompatibility, hypersensitive response, signalling — and topology governs only
> how far a collapse spreads *once* infection and vessel loss occur, not whether the haustorium connects.
>
> With those bounds stated, the result suggests a testable hypothesis and a research pathway rather than a
> breeding recipe:
> 1. Establish the natural variation and heritability of venation reticulation (loop fraction, vein
>    density, mean degree) across a crop's germplasm.
> 2. **Test the model's premise first, in planta:** challenge accessions that differ in reticulation with
>    *Cuscuta*/*Orobanche* and measure infection success, host water status, and yield loss. If higher
>    reticulation does not reduce parasite-induced decline, the pathway stops here — one cannot breed for a
>    benefit shown only in silico.
> 3. Only if validated: map the trait (QTL/GWAS; candidate genes in the auxin-canalisation vein-patterning
>    pathway), then apply marker-assisted or genomic selection *while monitoring the cost/efficiency
>    trade-offs*, and confirm no yield penalty in parasite-free conditions before field deployment.
> 4. Treat topology as a complement to, not a replacement for, existing chemical/immune resistance.

## Honest caveats (must travel with the result)
- Linear surface (R²≈0.89) extrapolated only mildly (within observed ⟨k⟩); a direction + magnitude, not a
  network design.
- Trade-offs (cost, water-use efficiency, mechanical support) are **not** in the model and bound the real
  ceiling.
- Resistance is multi-mechanism; this addresses only the topological spread of collapse post-infection.
- The D lever is additionally capped by the generator's D≈1.81 ceiling (tree-vs-mesh limitation).
