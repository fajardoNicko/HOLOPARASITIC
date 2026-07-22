# Research Proposal Defense — Slide Deck

**Structure (as required):**
I. Justification · II. Expected Contribution · III. Refined Methodology (6 steps)
· IV. Review of Related Literature

Slide text is written to be **pasted straight into PowerPoint**. Keep bullets short
on the slide — the spoken detail lives in the *Speaker Note* under each slide.
Fill in `[bracketed]` placeholders.

---

## 🖼 FIGURE MAP — which PNG goes on which slide

All files are in `figures/`. They render on white, so they sit cleanly on a light
theme. **Keep each figure's aspect ratio — do not stretch.**

| File | Shows | Slide |
|---|---|---|
| `network.png` | the synthetic vascular network (reads instantly as a plant) | **1** (title accent), **8** (Method 1) |
| `sigmoid.png` | the hero S-curve — collapse probability vs. load, with p_c | **6**, **11** |
| `sigmoid_targeted.png` | random vs. targeted attack curves | **10** |
| `parasites.png` | p_c bar chart across the 5 parasites | **7** |
| `pc_heatmap.png` | the p_c surface over (K_h × D) | **12** (Method 6) |
| `dynamics.png` | ρ(t) logistic curve crossing p_c and f_c — the warning window | **13** |
| `collapse_montage.png` | the network fragmenting frame-by-frame | **6** (optional) |
| `stat_beta_fit.png` · `stat_finite_size.png` | critical exponent β, finite-size scaling | **Backup** |

---
---

# PART A — SLIDE CONTENT

---

## Slide 1 — Title

**Haustorial Sink Strength and Pre-Symptomatic Vascular Collapse:
A Percolation Model of Holoparasite-Induced Hydraulic Failure in Host Plants**

*A Computational Biophysics Study Using Pre-Fractal Hydraulic Networks*

- **Researchers:** [Member A], [Member B], [Member C], [Member D]
- [School / Strand] · Practical Research 2 · [Date]

> 🖼 `network.png` as a side accent.

---
---

# I. JUSTIFICATION
### *Why we chose this research*

---

## Slide 2 — The Problem

**Holoparasitic weeds are invisible until they are irreversible.**

- Holoparasites have **no functioning chloroplast** — they draw water, nutrients,
  and carbon **entirely** from a host through **haustoria** *(Twyford, 2018)*.
- Infestation causes chlorosis, stunting, impaired water transport, and
  **premature death** *(Gogi et al., 2021; Maqsood & Khaliq, 2022)*.
- **The farmer's problem:** by the time the crop **visibly wilts**, the vascular
  network has *already* failed. Detection happens **after** the point of no return.
- **In the Philippines:** *Aeginetia indica* is an occasional pest of **sugarcane
  and rainfed rice paddies** *(Pelser et al., 2024)*; the archipelago is a global
  center of holoparasite diversity *(Bascos et al., 2021; Lambio et al., 2024)*.

> **Speaker Note:** Lead with the farmer, not the physics. The pain point is that
> the *symptom* is a lagging indicator — you see it only after the plumbing is gone.

---

## Slide 3 — The Gap We Are Filling

**Everyone studies the parasite. Nobody has modelled the host's network failing.**

| What the literature has done | What is missing |
|---|---|
| Molecular & biological mechanisms of parasitism | How parasitic demand degrades the **host's transport network** |
| Philippine work: **biogeography** (species distribution modelling of *Rafflesia*, Obico et al., 2024) | No local study models **host physiology** under parasitic load |
| Hydraulic failure studied under **drought** | Hydraulic failure under a **biotic sink** is "insufficiently explored" |

**Our question:**
> *How much of a crop's internal plumbing can a parasite drain before the whole
> network suddenly collapses — and can we predict that point **before** the plant
> looks sick?*

**Why it must be computational:** you cannot ethically or practically watch 1,000,000
crops die. You can simulate it.

> **Speaker Note:** This is the justification in one breath — a real agricultural
> threat, a real detection gap, and a question that only simulation can answer at scale.

---
---

# II. EXPECTED CONTRIBUTION
### *What this study will deliver*

---

## Slide 4 — Four Deliverables

**1. A new metric — the Vascular Percolation Threshold, p_c**
A single number: *the fraction of vessels a parasite must drain before the host's
transport network collapses.* Collapse is defined **topologically** (giant connected
component < 50 %), so it is measurable **before** any visible symptom.

**2. A physical mechanism for "pre-symptomatic" failure**
We show collapse is a **phase transition**, not a gradual decline — the host is fine,
fine, fine, then gone. That sharpness is *why* farmers get no warning.

**3. A quantitative resistance trait for breeders**
p_c rises with venation density (fractal dimension **D**) — meaning **architecture
itself is a defence**, and a screenable, breedable trait.

**4. A differential equation for the intervention window**
Coupling p_c with logistic infestation growth `dρ/dt = rρ(1−ρ)` yields the
**pre-symptomatic window** — the time between *functional* collapse and *visible*
wilting. **That window is the thing we are trying to hand to a farmer.**

> **Speaker Note:** Contribution 4 is the one that converts this from "interesting
> physics" to "usable." Say the word *window* and let it land.

---
---

# III. REFINED METHODOLOGY
### *Six steps, from a blank canvas to a vulnerability map*

---

## Slide 5 — Methodology at a Glance

> 🖼 **Paste your 6-box graphical organizer here, full width.**

| # | Step | Output |
|---|---|---|
| **1** | Generate a synthetic **reticulate vascular network** | the host, as a graph |
| **2** | Measure its **fractal dimension D** by box-counting | D = 1.434 |
| **3** | **Solve water flow** (Darcy–Ohm + Kirchhoff); attach parasite as a **haustorial sink**; let over-stressed vessels **embolize** | Ψ at every node |
| **4** | **Monte Carlo** vessel removal, **1,000,000 trials**; track the **GCC** — collapse = GCC < 50 % | collapse / survive per trial |
| **5** | **Logistic regression** on the trials → pinpoint **p_c** with a **confidence interval** | p_c = 0.279 ± 0.002 |
| **6** | **Sweep K_h × D** → build the **p_c surface** | heatmap of vulnerability |

**Stack:** Python 3.13 · NumPy · SciPy (sparse) · NetworkX · scikit-learn · Matplotlib.
**Every result is reproducible** — one frozen `config.py`, fixed RNG seeds.

---

## Slide 6 — Methods 1 & 2: Build the Host, Measure Its Architecture

**① Generate the network** *(the host plant, as a graph)*
- Recursive **bifurcating tree**, 9 generations → **1,023 nodes**.
- Vessel radii obey **Murray's Law**, `r₀³ = r₁³ + r₂³` — the biologically
  optimal branching rule *(Murray, 1926)*.
- Each vessel gets a **Hagen–Poiseuille resistance**, `R = 8ηL / πr⁴`.
- **+ 2,044 anastomoses** (cross-links) → a **reticulate mesh**, not a bare tree.
  *Real leaves have loops. A pure tree has no percolation transition at all —
  this reticulation is what makes the whole study possible.*
- Final: **1,023 nodes, 3,066 vessels, mean degree ≈ 6.0.**

**② Measure D by box-counting** *(how space-filling is the venation?)*
- Overlay grids from k = 16 to 1024 boxes; count occupied boxes N(ε).
- Slope of `log N(ε)` vs `log(1/ε)` → **D = 1.434 ± 0.007**.
- ✅ **Falls inside the measured real-leaf venation range (1.39 – 1.76).**

> 🖼 `network.png`

---

## Slide 7 — Method 3: Solve the Water Flow, Attach the Parasite

**Three laws, three levels — this is the physics core.**

| Law | Governs | In our model |
|---|---|---|
| **Hagen–Poiseuille** `R = 8ηL/πr⁴` | one **vessel's** resistance | sets each edge's conductance `g` |
| **Darcy / hydraulic Ohm's law** `Q = ΔΨ / R` | flow through one **conduit** | `Q_ij = g_ij(Ψ_i − Ψ_j)` |
| **Kirchhoff's Current Law** `ΣQ_in = ΣQ_out` | conservation at each **junction** | assembles it all into `LΨ = b` |

**The whole network becomes one sparse linear system** — a resistor circuit,
solved once for the water potential Ψ at every node.

**The parasite enters as a single term:**
> **Q_parasite = K_h · (Ψ_host − Ψ_parasite)**

A **leak conductance K_h** tying a host vessel to a more-negative parasite
reservoir (Ψ_parasite = −3.0 MPa). **K_h is our independent variable — it *is*
haustorial sink strength.**

**Then: cavitation.** Any vessel pulled past **Ψ < −2.0 MPa** embolizes and is
**deleted** from the conducting network. *This is the bridge: a hydraulic event
(too much tension) becomes a topological event (a vessel vanishes).*

> **Speaker Note:** If a panelist asks "did you use Darcy's law?" — **yes.**
> `Q = g·ΔΨ` on every edge *is* Darcy. Kirchhoff is not an alternative to it; it's
> the conservation law that stitches all those Darcy elements into a solvable system.
> You need both.

---

## Slide 8 — Methods 4 & 5: Monte Carlo → the Threshold

**④ Monte Carlo removal — 1,000,000 trials**
- Sweep **infestation load ρ** from 0 → 1 in 50 steps.
- At each ρ: randomly disable that fraction of vessels, **20,000 times.**
- After each trial, compute the **Giant Connected Component (GCC)** — the largest
  surviving piece of plumbing still joined to the root.
- **Collapse := GCC < 50 % of the original network.** Record a **1** or a **0**.
- Hot loop runs on integer-indexed **SciPy sparse matrices**, never NetworkX —
  that is what makes 10⁶ trials feasible.

**⑤ Logistic regression — pinpoint p_c**
- Fit `P(collapse | ρ)` — the million 1/0 outcomes become one smooth **S-curve**.
- The threshold is where that curve crosses 50 %: **p_c = −b / w**.
- **Bootstrap resampling** → a genuine **95 % confidence interval**.

## 🎯 RESULT: **p_c = 0.279 ± 0.002**
> **A holoparasite only needs to drain ~28 % of the host's vessels to collapse it.**
> Not 50 %. Not 80 %. **Twenty-eight percent.**

> 🖼 `sigmoid.png` — *the S-curve is the money shot. Point at the cliff.*

---

## Slide 9 — Method 6: Sweep K_h × D → the Vulnerability Map

**⑥ Two-axis parameter sweep** *(the deliverable a breeder can actually use)*

- **X-axis — K_h** (haustorial sink strength): 0.3 → 2.5. *How aggressive is the parasite?*
- **Y-axis — D** (fractal dimension / venation density): 1.35 → 1.48. *How well-built is the host?*
- Re-run the full hydraulic + percolation pipeline **in every cell** → **p_c surface**.

**What it shows:**
- **↑ K_h → ↓ p_c.** A greedier parasite collapses the host with fewer haustoria.
- **↑ D → ↑ p_c.** **Denser venation resists longer.**
  → *Architecture is a defence. D is a **breedable resistance trait**.*

> 🖼 `pc_heatmap.png`

---

## Slide 10 — Beyond the 6 Steps: Two Extensions

**A. Attachment site matters more than trophic mode.**

| Parasite | Type | Attaches | **p_c** |
|---|---|---|---|
| *Orobanche* (broomrape) | holo | root | **0.155** ⬅ most destructive |
| *Cuscuta* (dodder) | holo | stem / backbone | **0.175** |
| *Striga* (witchweed) | hemi | root | **0.263** |
| *Pilostyles* (endophyte) | holo | systemic | **0.277** |
| Mistletoe | hemi | branch | **0.425** ⬅ least |

> **The cross-over finding:** hemiparasitic *Striga* (0.263) collapses the host
> **sooner** than holoparasitic *Pilostyles* (0.277). **Where** a parasite taps beats
> **how greedy** it is. A targeted backbone attack (p_c = 0.177) is nearly **twice**
> as efficient as random damage (0.279).

> 🖼 `parasites.png` · `sigmoid_targeted.png`

**B. Adding time — the differential equation.**

`dρ/dt = r·ρ(1−ρ)` → `ρ(t) = 1 / (1 + A e^(−rt))`, A = (1−ρ₀)/ρ₀

- crosses **p_c = 0.279** at **t_c** → *functional collapse* — **invisible**
- crosses **f_c = 0.837** at **t_wilt** → *visible wilting* — **too late**
- **PRE-SYMPTOMATIC WINDOW = t_wilt − t_c ≈ 10.3 time-units** (at r = 0.25)

> **That gap is the intervention window that visual scouting throws away.**

> 🖼 `dynamics.png`

---
---

# IV. REVIEW OF RELATED LITERATURE
### *Four themes converging on one gap*

---

## Slide 11 — RRL Map

> **Our study sits where four literatures meet — and none of them have met before.**

```
   2.1 Holoparasites &         2.2 Haustoria as
       Agricultural Impact  →      Hydraulic Sinks
              ↓                          ↓
        (the threat)              (the mechanism)
              ↘                          ↙
                    ★ THE GAP ★
                 p_c — the threshold
                    ↗          ↖
   2.3 Hydraulic Failure,   2.4 Mathematical Models
       Cavitation, Embolism      of Plant Hydraulics
              ↑                          ↑
        (the failure mode)         (the tools)
```

---

## Slide 12 — 2.1 · Holoparasites and Their Agricultural Impact

**The threat is real, and it is local.**

- Parasitic plants lack functioning chloroplasts and obtain water, nutrients, and
  carbon from hosts via **haustoria** — a bidirectional macromolecular interface
  *(Casadesús & Munné-Bosch, 2021; Voegele & Mendgen, 2003; Bozkurt & Kamoun, 2020)*.
- **Hemi- vs. holo-:** hemiparasites photosynthesize partially; **holoparasites
  rely on the host entirely, for life** *(Sullivan, 2021; Twyford, 2018)*.
- Consequences: assimilate redistribution away from growth *(Ossa et al., 2021)*,
  impaired water transport, chlorosis, stunting, **wilting and premature death**
  *(Gogi et al., 2021; Maqsood & Khaliq, 2022)*.
- **Philippine context:** *Aeginetia indica* (Orobanchaceae) — a root holoparasite in
  **sugarcane and rainfed rice** *(Sharma et al., 2026; Pelser et al., 2024)*. The
  country is a **global center of holoparasite diversity** — endemic *Rafflesia*,
  *Balanophora* *(Bascos et al., 2021; Lambio et al., 2024; Malabrigo et al., 2025)*.

> 🔴 **GAP:** Philippine computational work on parasitic plants is **biogeographic**
> *(Obico et al., 2024 — species distribution modelling)*. **No local study has modelled
> how progressive parasitic demand degrades the host's internal transport network.**

---

## Slide 13 — 2.2 · Holoparasitic Haustoria as Hydraulic Sinks

**This theme gives us our central modelling assumption.**

- The haustorium penetrates the host and connects directly to the **xylem** (and often
  phloem), enabling continuous extraction of water and metabolites
  *(Perez-de-Luque, 2013; Goyet et al., 2019)*.
- Physiologically, it acts as an **additional hydraulic sink** in the host network
  *(Mateus et al., 2026)* — xylem sap is **diverted**, and surrounding vessels are
  forced to compensate *(Saleem et al., 2024)*.
- **Sink strength** depends on parasite biomass, developmental stage, and host
  compatibility *(Casadesús & Munné-Bosch, 2021; Nabity et al., 2021)*.
- Parasites are **less water-use-efficient than hosts**, producing a **continuous
  passive flow of xylem sap into the parasite** *(Hegenauer et al., 2017)*.
- Tissues far from the source suffer **reduced hydraulic conductivity and localized
  water deficits** *(Zagorchev et al., 2021; Chen et al., 2025)*.

> ✅ **This literature explicitly recommends our approach:** haustoria can be modelled
> as **localized sink nodes** on a network to identify **critical thresholds at which
> the transport network loses functionality.**
> **→ That is precisely our K_h term:  Q = K_h (Ψ_host − Ψ_parasite).**

---

## Slide 14 — 2.3 · Plant Hydraulic Failure, Cavitation, and Embolism

**This theme gives us our failure rule.**

- Water rises by the **cohesion–tension mechanism** *(Böhm, 1893; Dixon & Joly, 1895)* —
  a column held under **negative pressure**.
- Under excessive tension, **cavitation** forms gas bubbles; the resulting **embolism**
  blocks the vessel permanently *(Bittencourt et al., 2018)*.
- Severity is quantified by **Percent Loss of Conductivity (PLC)** *(Zhang et al., 2018)*;
  plants near critical PLC show reduced stomatal conductance and **increased mortality**
  *(Haworth et al., 2016)*.
- 🇵🇭 **Locally validated:** **Stiller et al. (2003)** measured PLC on rice at **IRRI, Los
  Baños**, reporting **P₅₀ ≈ −1.6 MPa**. **Henry et al. (2016)**, also at IRRI, showed
  drought reduces root hydraulic conductance in Philippine-grown rice.
- **Biotic** stressors can drive the same failure *(Qaderi et al., 2019)* — parasitic
  extraction raises tension in the **remaining** vessels, accelerating cavitation.

> ✅ **This justifies our cavitation threshold** (Ψ < −2.0 MPa → vessel removed) — and
> the local P₅₀ ≈ −1.6 MPa gives us a **real number to calibrate against.**
> 🔴 **GAP:** the authors themselves call parasite-driven hydraulic failure
> *"insufficiently explored."*

---

## Slide 15 — 2.4 · Mathematical Models of Plant Hydraulic Transport

**This theme gives us our entire toolkit — four laws, and we use all four.**

| Law | Equation | Role in our model |
|---|---|---|
| **Hagen–Poiseuille** *(Zhang & Hoshino, 2013)* | `ΔP = −8µL/πR⁴ · Q` | conductance ∝ **r⁴** — small radius changes dominate transport |
| **Darcy / hydraulic Ohm's law** *(Nobel, 2020)* | `Q = Δh / R_h` | flow ∝ pressure difference ÷ resistance |
| **Kirchhoff's Current Law** | `ΣI_in = ΣI_out` | mass conservation at **every vascular junction** |
| **Murray's Law** *(Murray, 1926)* | `r₀³ = r₁³ + r₂³ + … + rₙ³` | optimal branching → how we **build** the network |

- The **Darcy–Ohm analogy** maps pressure→voltage, flow→current, resistance→resistance,
  letting vascular networks be solved with **electrical-circuit mathematics**
  *(De Swaef et al., 2022)*.
- **Ohm + Kirchhoff together** let researchers model vasculature as a **resistor network** —
  explicitly "an efficient framework for analyzing flow redistribution resulting from
  vessel blockage **or parasitic water extraction**."
- Murray's Law is a **biologically justified** basis for simulating vascular
  architecture, though real plants deviate *(McCulloh et al., 2004, 2009)*.

> ✅ **The literature hands us the exact machine we built.** Our contribution is not the
> machine — it is **pointing it at a parasite** and reading off the threshold.

---

## Slide 16 — 2.5 · Synthesis and the Research Gap

**What the four themes establish, and what they leave open.**

| Theme | Established | Left open |
|---|---|---|
| 2.1 Agricultural impact | holoparasites devastate crops; PH is a hotspot | no model of the **host network** failing |
| 2.2 Haustoria as sinks | the haustorium **is** a hydraulic sink | **no one has computed the threshold** |
| 2.3 Cavitation & embolism | tension → embolism → conductivity loss | **biotic**-driven failure "insufficiently explored" |
| 2.4 Mathematical models | resistor-network machinery exists | **never aimed at a parasite** |

> ### ★ THE GAP
> The literature independently establishes **(a)** that haustoria are hydraulic sinks,
> **(b)** that vessels fail by embolism, and **(c)** that vascular networks can be solved
> as resistor circuits. **No study has combined the three to ask the percolation question:
> *at what fraction of drained vessels does the host network suddenly collapse?***
>
> **That number is p_c. That number is our study.**

---

## Slide 17 — Closing

**Haustorial Sink Strength and Pre-Symptomatic Vascular Collapse**

- ✅ **p_c = 0.279 ± 0.002** — a holoparasite needs only **~28 %** of the host's
  vessels to collapse it.
- ✅ Collapse is a **phase transition** — which is *why* it is pre-symptomatic.
- ✅ **Denser venation (higher D) resists longer** → a breedable resistance trait.
- ✅ The **pre-symptomatic window** (≈ 10.3 time-units) is what we hand to a farmer.

> **We are not trying to save a plant that already looks sick.
> We are trying to find it before it does.**

**Thank you. Questions?**

---
---

# PART B — BACKUP SLIDES *(for Q&A only)*

---

## B1 — "Is 0.279 statistically real?"
- **1,000,000** Monte Carlo trials; 50 densities × 20,000 trials each.
- **Bootstrap 95 % CI = [0.278, 0.281]** — the ± 0.002 is the resampled CI half-width.
- Critical exponent **β ≈ 0.745**, plus **finite-size scaling** confirming the
  transition sharpens with N — the signature of a **true** phase transition, not an artifact.
> 🖼 `stat_beta_fit.png`, `stat_finite_size.png`

## B2 — "Why is collapse GCC < 50 % and not GCC → 0?"
- **GCC → 0** is the textbook fragmentation point, `f_c = 1 − 1/(κ−1) = 0.837` (κ = 7.15).
  That is **visible wilting** — total plumbing failure.
- **GCC < 50 %** is *functional* collapse — the plant cannot supply half its leaves.
  It happens at **0.279**, long before it looks sick. **The gap between the two IS the paper.**

## B3 — "Have you validated against real leaves?"
- **D = 1.434** falls inside the measured real-leaf venation range **1.39 – 1.76**. ✅
- **Planned empirical validation** (`empirical/`): top-down venation photos + transverse
  stem/leaf cross-sections across **5 species** (tomato, a legume, corn, mango, hibiscus),
  ≥ 5 plants each → measured D and Murray's-law exponent to test against the model.

## B4 — "What are the limitations?"
Stated openly:
1. **2-D network** — real vasculature is 3-D.
2. **Uncalibrated K_h** — no published study gives a haustorial volumetric flux, so K_h is
   swept as a **range**, not fitted to a value. *This is a stated gap in the literature, not
   a shortcut on our part.*
3. **Root parasites approximated** — our network models the shoot with the root as a single
   source node, so root attack = "tap the root-proximal backbone."
4. **Pilostyles is a schematic profile** (systemic archetype), not a species-fitted model.
5. **Dynamics r and ρ₀ are illustrative** — the ODE's *shape* is the result, not its timing.

---
---

# PART C — SPEAKING ASSIGNMENTS

| Member | Slides | Owns |
|---|---|---|
| **A** | 1 – 3 | Title, Justification, the Gap |
| **B** | 4 – 7 | Expected Contribution + Methods 1–3 (the physics) |
| **C** | 8 – 10 | Methods 4–6 (Monte Carlo, p_c, the sweep) + extensions |
| **D** | 11 – 17 | Review of Related Literature + Closing |

**Rehearsal rule:** every member must be able to answer **B1–B4** regardless of which
slides they present.
