# Related Work & Novelty Positioning — verified citations

> Consolidates the adjacent literature this study must cite and distinguish itself from.
> Every DOI below was resolved by web search on 2026-07-30. Use the ready-to-paste paragraph
> at the bottom in the Discussion/Introduction. See also `RESEARCH_FINDINGS_VERIFIED.md`
> (Vishnu→Flora citation fix; Zhang et al. 2025 haustorial-flux gap).

## The three adjacent studies — what they did, and how this work differs

### 1. Mander & Williams (2024) — closest prior art (leaf networks + damage)
**Mander, L., & Williams, H. T. P. (2024). The robustness of some Carboniferous fossil leaf
venation networks to simulated damage. *Royal Society Open Science, 11*(5), 240086.**
`https://doi.org/10.1098/rsos.240086`

- **What:** removes vein segments / blade regions from 9 real extracted leaf venation networks
  (Carboniferous fossils + extant *Betula alba*) and measures what stays connected to the main vein.
  Confirms loops (reticulation) confer damage robustness.
- **How we differ (verified from the paper):** it reports **no formal p_c, no critical exponents,
  no hydraulic model** — it states *"we do not simulate any processes directly"* and names fluid-flow
  modelling as **future work**. This study couples a **Hagen–Poiseuille resistor network + Kirchhoff
  solve** to the connectivity collapse and estimates a **quantitative p_c**, on a **122-species** cohort,
  under a **holoparasitic sink** driver. Mander & Williams is the paper that *leaves us the opening*.

### 2. Mrad et al. (2021) — percolation on xylem, but the opposite connectivity effect
**Mrad, A., Johnson, D. M., Love, D. M., & Domec, J.-C. (2021). The roles of conduit redundancy and
connectivity in xylem hydraulic functions. *New Phytologist, 231*(1), 996–1007.**
`https://doi.org/10.1111/nph.17429`

- **What:** graph theory + percolation on the **stem xylem conduit network**; models how embolism
  *spreads* between connected conduits. Finds higher connectivity is a **liability** — it speeds
  embolism *contagion* through the network.
- **How we differ:** their percolation models **embolism spread (contagion)** — connectivity *hurts*.
  Ours models **structural fragmentation of the transport network** — connectivity *helps* (more loops =
  higher p_c = more sink-resistant). Same mathematics, **opposite sign of the connectivity effect**, and
  a different biological target (leaf venation vs stem conduits; parasite sink vs drought embolism).
  Cite it to show we know the percolation-on-xylem literature and to sharpen the contrast.

### 3. Loepfe et al. (2007) — the foundational "xylem is a network" argument
**Loepfe, L., Martínez-Vilalta, J., Piñol, J., & Mencuccini, M. (2007). The relevance of xylem network
structure for plant hydraulic efficiency and safety. *Journal of Theoretical Biology, 247*(4), 788–803.**
`https://doi.org/10.1016/j.jtbi.2007.03.036`

- **What:** first 3-D network model of the xylem; shows connectivity raises both conductivity **and**
  vulnerability to embolism spread — "the xylem can no longer be interpreted as the mere sum of its
  conduits."
- **How we differ:** same efficiency–safety framing, but again **embolism spread**, **stem xylem**, and
  **no parasite / no p_c on a real leaf-venation cohort.** Cite as the origin of the network view we build
  on.

**One-line distinction to hold in your head:** *Mrad and Loepfe percolate embolism (contagion, connectivity
hurts); we percolate connectivity loss (fragmentation, connectivity helps); Mander & Williams fragment real
leaf networks but add no hydraulics or p_c.* Nobody has coupled a hydraulic resistor model to a percolation
threshold on a real leaf-venation cohort under a parasitic sink.

## Ready-to-paste related-work / novelty paragraph (hedged, bulletproof)

> Percolation and graph theory have been applied to plant vascular networks before, but with a different
> target and the opposite connectivity effect: models of the stem xylem treat higher conduit connectivity
> as a *liability* that accelerates the spread of embolism (Loepfe et al., 2007; Mrad et al., 2021). Our
> analysis instead treats connectivity as *protective* — a more reticulate leaf-venation network fragments
> at a higher removal fraction, raising the critical threshold p_c. On the leaf side, Mander & Williams
> (2024) removed elements from real fossil and extant leaf venation networks and confirmed that reticulation
> improves damage robustness, but they report no critical threshold and no hydraulic model, explicitly
> naming fluid-flow simulation as future work. To our knowledge, no prior study couples a Hagen–Poiseuille
> resistor network and a Kirchhoff solve to a percolation threshold on a real leaf-venation cohort, driven
> by a holoparasitic haustorial sink — the gap this study addresses.

**Do NOT write** "no one has run a percolation/connectivity analysis on a real leaf network" — Mander &
Williams did. The hedged claim above is the defensible one.

## Holoparasite sink strength — the numbers behind the calibrated K_h
> Verified 2026-08-04. These ground the haustorial leak conductance K_h as a literature-derived
> CONSTANT (`config.K_H_HOLOPARASITE`, `scripts/make_sink_demo.py`) instead of a free dial, replacing
> the stipulated parasite "efficiencies" (1.0 / 0.6) that the old five-parasite comparison used.

- **Jiang, F., Jeschke, W. D., & Hartung, W. (2003). Water flows in the parasitic association
  *Rhinanthus minor*/*Hordeum vulgare*. *Journal of Experimental Botany, 54*(389), 1985–1993.**
  `https://doi.org/10.1093/jxb/erg212`
  → The parasite **diverts ~18–20% of the host's total water uptake**; parasite leaf conductance
  ~1200 mmol m⁻²s⁻¹, stomata open day and night. This 20% is the **sink-magnitude anchor** we solve K_h
  against. *Caveat:* it is a **hemiparasite**, whole-plant figure — used as a conservative floor
  (holoparasites are stronger), not a Cuscuta-specific number.

- **Jeschke, W. D., et al. (1994). Modelling the flow and partitioning of carbon and nitrogen in the
  holoparasite *Cuscuta reflexa* Roxb. and its host *Lupinus albus* L. II. *Journal of Experimental
  Botany, 45*(6), 801–812.** `https://doi.org/10.1093/jxb/45.6.801`
  → Full C/N flow model of a **true holoparasite**: massive sink drawing from **xylem and phloem**;
  host N-fixation suppressed to 37% of control. Shows holoparasite draw is quantified as **mass flux**,
  not a water fraction — which is *why* no clean "% of xylem water" exists for holoparasites and we
  borrow the Rhinanthus 20% as a floor.

- **Kaiser, B., Vogg, G., Fürst, U. B., & Albert, M. (2015). Parasitic plants of the genus *Cuscuta*
  and their interaction with susceptible and resistant host plants. *Frontiers in Plant Science, 6*, 45.**
  `https://doi.org/10.3389/fpls.2015.00045`
  → Supports only the **qualitative** claim that *Cuscuta* haustoria tap host vasculature and extract
  water and solutes. **⚠ CORRECTION (verified 2026-08-08):** this review does **NOT** state a ~1.5 MPa
  gradient — it does not quantify the host–parasite water-potential difference at all. Do **not** cite it
  for the 1.5 MPa figure.

- **The ~1.5 MPa host–parasite gradient — ILLUSTRATIVE, no primary source located.** The value appears
  only in *Cuscuta* **review** literature (e.g. review articles on the haustorium), with no primary
  peer-reviewed measurement found. Treat ~1.5 MPa as an **order-of-magnitude driving gradient**, flagged
  as illustrative, or drop the specific number. The exact host–parasite gradient for a holoparasite is an
  **open measurement gap**, not a settled figure.

- **Glatzel, G., & Geils, B. W. (2009). Mistletoe ecophysiology: host–parasite interactions.
  *Botany, 87*(1), 10–15.** `https://doi.org/10.1139/B08-096`
  → Hemiparasite comparison: xylem-tapping mistletoe sits only **0.1–0.2 MPa** below the host — an order
  of magnitude weaker gradient than a holoparasite. Frames the holoparasite as the strong-sink extreme.

**What the calibrated demonstration shows (`figures/sink_demo.png`, `data/sink_demo.json`):** with K_h
solved to divert ~18–20% of leaf flow (hemiparasite floor, Jiang 2003) at the illustrative ~1.5 MPa gradient, the single haustorial sink is
**sub-cavitation — 0 vessels embolise at any gradient.** Because the haustorium taps a high-conductance
vessel, it withdraws a fifth of the flow while barely perturbing local tension. **Honest reading:** the
hydraulic sink (resource drain) and the percolation collapse (structural fragmentation) are **decoupled
lenses**; catastrophic collapse is the structural/cumulative process the main result quantifies, not
something one realistic sink produces. This supports — rather than weakens — the *pre-symptomatic* framing.

## Citation corrections carried over (see RESEARCH_FINDINGS_VERIFIED.md for detail)
- **Muraleedharan, V., Rajan, S. C., & Jaishanker, R. (2023).** Determining the limits of traditional
  box-counting fractal analysis in leaf complexity studies. *Flora, 304,* 152300.
  `https://doi.org/10.1016/j.flora.2023.152300` — replaces the wrong "Vishnu, M., … *Chaos, Solitons &
  Fractals*" entry (wrong journal; third author is Jaishanker, not Nair).
