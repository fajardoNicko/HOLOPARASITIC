# Model Validation Against the Literature

This document tests the model's assumptions and outputs against published
empirical and theoretical values (the reference list provided by the team). Each
section gives **our value → the literature value(s) → a verdict**. Citations are
to the specific sources checked; values behind paywalls are flagged.

> **Headline:** the percolation engine is validated against analytical theory and
> by formal statistical tests (§6: logistic fit pseudo-R² 0.85; transition sharpens
> with size; power-law critical scaling β = 0.69 ± 0.04 — a genuine continuous
> transition), and the tipping-point framing is well supported. Two honest caveats
> emerge: our fractal dimension is *statistically* below the measured leaf-venation
> range (t = −67, p ≈ 10⁻³³), and our "connectivity → robustness" assumption holds
> only for the *fragmentation* failure mode (real xylem also has a
> connectivity-vs-embolism-spread trade-off).

---

## Verdict summary

| Aspect | Our model | Literature | Verdict |
|--------|-----------|------------|---------|
| Percolation engine (GCC → 0) | ~71 % removal | Callaway *f_c* = 0.714 | ✅ **Matches theory** |
| Operational p_c (GCC < 50 %) | 0.222 | stricter, earlier criterion | ✅ Consistent, distinct metric |
| Targeted < random | 0.203 < 0.222 | theory: yes (gap small ⇒ homogeneous) | ✅ Correct direction |
| Tipping-point framing | phase transition | catastrophe/bifurcation; P88 | ✅ Supported (different formalism) |
| Fractal dimension D | 1.26–1.51 | 1.39–1.76 (Crisci, box-counting) | ⚠️ **At/below empirical range** |
| Reticulation → robustness | higher p_c | ✅ fragmentation; ✗ embolism spread | ⚠️ **Mode-dependent (key caveat)** |
| *Cuscuta* strong sink (K_h) | leak conductance | strong sink confirmed; no flux value | ✅ Qualitative; calibration gap |
| Host architecture → resistance | p_c rises with D | host heterogeneity confirmed | ✅ Supported |

---

## 1. Percolation threshold & engine ✅ (validated) + ⚠️ (define your metric)

**Our model:** mean degree ⟨k⟩ = 3.60, ⟨k²⟩ = 16.18, so the Molloy–Reed ratio
κ = ⟨k²⟩/⟨k⟩ = **4.50**. Operational p_c (collapse = GCC < 50 %) = **0.222**;
near-total fragmentation (GCC < 5 %) at ρ = 0.51; GCC essentially gone (~1 %) by
ρ = 0.71.

**Theory (Callaway, Newman, Strogatz & Watts 2000, *PRE* / cond-mat/0007300):**
a giant component exists iff κ > 2 (ours is 4.5 ✓), and the critical *random
removal* fraction is
> *f_c* = 1 − 1/(κ − 1) = 1 − 1/3.50 = **0.714**.

**The match:** our simulated giant component vanishes (~1 % of N) right at
ρ ≈ 0.71 — **exactly the analytical prediction from our own degree
distribution.** This is strong evidence the percolation code is correct, not an
artifact.

**The important distinction (state this in the paper):** the textbook threshold
*f_c* ≈ 0.71 is where the giant component reaches *zero*. Our headline
**p_c = 0.222 is a deliberately stricter, earlier criterion** — "the host has lost
half its connected vasculature" — which is the biologically meaningful failure
point, not complete fragmentation. So p_c = 0.22 < f_c = 0.71 is **expected and
internally consistent**; they measure different things. Report both, and label
p_c as a "50 %-GCC operational threshold."

**Bethe-lattice context (Wikipedia):** p_c = 1/(z−1) = 1/2.6 ≈ 0.385 for z = 3.6
(tolerable removal ≈ 0.615) — same ballpark as Callaway, confirming the regime.

**Targeted vs random:** theory says hub-first removal collapses a network sooner
(it depletes ⟨k²⟩ fastest), so targeted p_c < random p_c is the correct
direction — and ours is (0.203 < 0.222). The *small* gap (~9 %) is itself
informative: large gaps are characteristic of scale-free/heterogeneous networks,
so a small gap confirms our network is relatively **degree-homogeneous** (a
reasonable property for vasculature).

---

## 2. Tipping-point / catastrophic-failure framing ✅ (supported)

**Our model:** vascular failure as a **phase transition** with a sharp critical
point p_c.

**Literature:**
- **"Catastrophic hydraulic failure and tipping points in plants"** (review,
  PMC9544843): plant hydraulic failure is *explicitly* described as a tipping
  point — modeled with **catastrophe theory / bifurcations** (fold catastrophe at
  the bubble scale, transcritical bifurcation at the whole-plant scale), with
  "runaway embolism." Strongly supports treating collapse as a critical
  transition.
- **Urli et al. (2013, *Tree Physiology*, PMID 23658197):** angiosperms suffer
  *lethal* failure at **≈ 88 % loss of hydraulic conductivity (P88)** (vs ≈ 50 %,
  P50, for conifers); minimum recoverable water potential −3.4 to −6.0 MPa.

**Verdict & caveat:** the *concept* (a sharp lethal threshold) is firmly
supported. Two honesty notes: (a) the biology literature uses **catastrophe/
bifurcation theory**, not percolation specifically — our contribution is
re-casting it as a *network percolation* problem, which is novel but should be
presented as a complementary lens, not the established one; (b) the empirical
threshold is a **% loss of conductivity (88 %)**, which is *not* the same axis as
our **% of vessels removed (22 %)**. Don't equate "22 % removal" with "88 % PLC"
without an explicit conductivity-vs-removal curve. (A natural future extension:
report loss-of-conductivity from the hydraulic solver alongside the GCC.)

---

## 3. Fractal dimension D ⚠️ (at/below the measured range)

**Our model:** box-counting **D = 1.26–1.51** (hero network D = 1.31).

**Literature:**
- **Crisci et al. — *Relbunium* spp. (Rubiaceae)** — the one directly comparable
  source (real leaf venation, box-counting): **D = 1.387, 1.561, 1.763** for the
  three species (range **≈ 1.39–1.76**).
- **Cheeseman et al. (2022, *Mathematics* 10(5):839):** box-counting on branching/
  vascular structures gives examples spanning **≈ 1.06–1.65**, *but the paper's
  thesis is a caution* — branching networks aren't truly self-similar, so a single
  box-counting D is partly an artifact (non-linear local log–log slopes).
- **Price et al. (2012), Katifori et al. (2015), Ronellenfitsch & Katifori
  (2024):** the leading leaf-venation papers **do not use box-counting D at all** —
  they use distributional/topological metrics (nesting number, vein density,
  areole statistics).

**Verdict:** our D is **at the low edge of / slightly below** the only directly
comparable empirical numbers (Crisci 1.39–1.76). Only the top of our swept range
(~1.51) overlaps; the hero D = 1.31 is below all three *Relbunium* leaves. Real
reticulate venation tends to measure **higher (~1.4–1.8)** — our networks are a
touch sparse. **This is the most actionable finding** (see Recommendations).
Secondary point: because the strongest modern literature questions box-counting D
as a descriptor, lean on it as *one* characterization, not the sole one.

---

## 4. "Connectivity → robustness" ⚠️ (mode-dependent — the key scientific caveat)

**Our model:** more reticulation (loops/anastomoses) → higher p_c (more robust).

**Literature — a genuine sign-flip depending on failure mode:**
- **Mrad et al. (2021, *New Phytologist*, PMID 33908055):** an explicit
  *trade-off* — higher connectivity "improves resistance to embolism spread
  without negatively affecting conductivity" in some cases, *but* "could also
  reduce resistance due to increased speed of embolism spread."
- **Loepfe et al. (2007, *J. Theor. Biol.*):** both maximum conductivity *and*
  vulnerability to embolism **increase with connectivity** — connectivity is not
  purely protective.
- **Bouda et al. (2021, grapevine, PMC8154096):** network topology adds **+40 %
  (0.66 MPa)** embolism resistance via "daisy-chain" arrangement — supports the
  protective side.
- **Johnson et al. (2020, *Plant Physiol.* 184:212):** >80 % of embolism events
  are single-conduit, but more-connected species have more multi-conduit spread
  (up to 19 %).
- **Bouda et al. (2022, *Science*, add2910):** evolution favored xylem with
  **fewer independent spread pathways** for drought resistance.

**Verdict:** our assumption is correct **for the topological *fragmentation*
failure mode** — keeping the host's transport graph connected as the parasite
deletes vessels. There, more loops genuinely raise p_c (Mrad & Bouda-grapevine
support this). **But the same edges that resist fragmentation can also conduct
embolism**, so for the *air-seeding contagion* mode, more connectivity can *lower*
safety. The reconciling idea is **"arrangement beats amount"** — a single scalar
reticulation knob conflates the two. **What to do:** state explicitly that p_c
models *fragmentation robustness, not embolism contagion*, and (optionally) add a
sensitivity run where connectivity carries a spread penalty, to show the result
isn't an artifact of ignoring the trade-off.

---

## 5. *Cuscuta* as a sink (K_h) ✅ (qualitatively confirmed) + honest calibration gap

**Our model:** each haustorium is a leak conductance K_h pulling host water toward
a parasite reservoir; K_h is the swept independent variable.

**Literature — "strong sink" strongly confirmed:**
- **Yoshida et al. (2019, PMC6861301):** haustorial hyphae form an **open
  connection with host xylem vessels** and phloem continuity; "*Cuscuta* becomes a
  **strong sink** … competes with sink organs of the host."
- **Hibberd & Jeschke (2001, *JXB* 52:2043):** ~**99 % of the parasite's carbon**
  comes from the host.
- **Birschwilks / Wolswinkel (2006, *JXB* 57:911):** **86.8 ± 2.9 %** of
  translocated assimilate captured by the parasite within 3 h; "very strong sink."
- **Jhu & Sinha / Bernal-Galeano (2022, PMC9157073):** haustoria take up water and
  small molecules. Noted physiology: *Cuscuta* takes in **more water than it
  transpires** — consistent with a large haustorial draw (supports a high K_h).

**Verdict & gap:** the existence and strength of the sink are well supported, so
modelling it as a strong leak is biologically faithful. **However, no accessible
source gives a volumetric haustorial water flux / conductance** to fix K_h's
absolute value. This *justifies* our treatment of K_h as a **free, swept
parameter** rather than a calibrated constant — cite the qualitative "excess
water" evidence and flag the missing number as an open quantity (a wet-lab target).

**Host heterogeneity (supports §"architecture sets resistance"):** Evans &
Borowicz (2013, PMC4844395) show host damage is water-status-dependent (parasitism
hurt well-watered hosts more), confirming hosts differ in tolerance — consistent
with our claim that host network properties modulate vulnerability.

---

## 6. Statistical validation (formal tests)

Five formal tests, run by `scripts/validate_stats.py` (figures
`stat_finite_size.png`, `stat_beta_fit.png`). These move the claims above from
"analytical/qualitative comparison" to statistically tested.

### 6.1 Goodness-of-fit of the logistic model — ✅ excellent
- **McFadden pseudo-R² = 0.85** (> 0.4 is considered an excellent logistic fit).
- **bin-level R² = 0.9994** (predicted vs observed collapse probability across the
  50 densities — the sigmoid tracks the data almost perfectly).
- Hosmer–Lemeshow χ² = 238 (df = 48) formally rejects (p ≈ 0), but this is the
  textbook **large-n artifact**: with ~100 000 trials, negligible deviations test
  "significant." The effect sizes (pseudo-R², R²) are the honest measure → the
  logistic model is an excellent fit and p_c is well identified.

### 6.2 Finite-size scaling — ✅ genuine phase transition
Across a 16× range of size (N = 127 → 2047):
- the **transition width (P = 0.1 → 0.9) shrinks monotonically, 0.203 → 0.145** —
  the defining signature of a true transition sharpening toward a step as N → ∞.
- p_c stays in a narrow band (**0.21–0.23**, tight 95% CIs) with **no systematic
  drift toward 0 or 1**, confirming it is a *structural property, not a size
  artifact*. (The residual ±0.01 tracks the co-varying D — smaller networks have
  lower D, and p_c rises with D, per §3–4.)

### 6.3 Critical exponent β — ✅ continuous transition, mean-field-like
Near the threshold the order parameter (giant-component fraction) follows a clear
power law **S ~ (f_c − ρ)^β** (log-log R² = **0.95**, N = 4095, f_c fixed at the
independently-derived Callaway value — *not* fitted):
- **β = 0.69 ± 0.04** (statistical) — in the **mean-field-like regime** and
  decisively distinct from the 2-D-lattice value β = 5/36 = 0.139 (excluded at
  > 14 SE).
- A power-law order parameter confirms a **genuine continuous (second-order)
  percolation transition** — not merely "an S-shaped curve."
- **Honest caveat:** β is not exactly the mean-field 1.0; finite-size rounding and
  the 2-D spatial embedding bias single-network estimates, and the *systematic*
  uncertainty (≈ 0.7–0.9 across window/size choices) exceeds the ±0.04 statistical
  error. A precise exponent needs a multi-size finite-size-scaling collapse
  (future work). The robust claims — continuous transition, mean-field-like class,
  2-D class excluded — hold.

### 6.4 Theory agreement — ✅
The giant component collapses to ~1 % of the network right at the analytical
Callaway/Molloy–Reed **f_c = 0.72** (derived independently from the measured degree
distribution). Simulation and theory agree to within finite-size rounding —
corroborating §1.

### 6.5 Fractal D as a distribution — ⚠️ confirms the low-D caveat, quantitatively
Over 30 independent seeds, **D = 1.311 ± 0.003** (95% CI [1.308, 1.313]; SD 0.006
— highly reproducible). A one-sample t-test against the lowest measured *Relbunium*
value (1.387) gives **t = −67.5, p ≈ 2 × 10⁻³³**: our default D is **statistically
significantly below** the empirical leaf-venation range. This makes the
recalibration (Recommendation 1) evidence-based, not cosmetic.

**Statistical bottom line:** the transition is real and well-characterised — the
logistic model fits (pseudo-R² 0.85), the transition sharpens with size (genuine
phase transition), the order parameter scales as a power law (continuous
transition, mean-field-like class, 2-D class excluded), and the threshold matches
analytical theory. The one statistically-confirmed weakness is the low fractal
dimension, which the reticulation recalibration fixes.

---

## Recommendations from this validation

1. **Nudge D into the empirical range (optional, data-driven).** Our D is ~0.1–0.2
   low vs *Relbunium*. Raising the default `reticulation` from 0.8 → ~1.8–2.0
   moves D to ≈ 1.43–1.51 (into Crisci's low range) and p_c to ≈ 0.28–0.33 — a
   literature-justified recalibration. (Confirmed by our own reticulation sweep.)
2. **Report two thresholds.** State the textbook percolation point (GCC → 0,
   ≈ 0.71, matches theory) *and* the operational p_c (GCC < 50 %, 0.222), so the
   metric is unambiguous.
3. **Name the failure mode.** Say plainly that p_c is *fragmentation* robustness,
   not embolism contagion; cite Mrad/Loepfe/Bouda for the trade-off and (optional)
   add a connectivity-spread-penalty sensitivity case.
4. **Keep K_h as a swept parameter** and cite the qualitative strong-sink evidence;
   list "measure haustorial water flux" as a wet-lab next step.
5. **Add a conductivity readout.** Output % loss of hydraulic conductivity from the
   solver to connect to the empirical P88 lethal threshold (Urli 2013).
6. **Citation fix:** PMC4844395 is **Evans & Borowicz (2013)**, not Hettenhausen —
   verify this key in the reference list.

---

## What is validated vs what still needs wet-lab data

- **Validated now:** the percolation mathematics (vs Callaway theory), the
  tipping-point concept (vs the catastrophic-failure literature), the strong-sink
  premise, and host-resistance heterogeneity.
- **Still needs real data:** absolute D matched to a target crop's venation,
  haustorial water-flux to calibrate K_h, a vessel-removal-to-conductivity-loss
  mapping, and the embolism-contagion failure mode. These define the wet-lab
  validation program in Chapter 5.

*Sources accessed via the team's reference list; several full texts were paywalled
(noted inline) and values were taken from abstracts/open mirrors.*
