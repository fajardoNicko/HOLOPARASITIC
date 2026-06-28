# Proposal Presentation — Slides + 5-Minute Script

**Format:** ≤ 5 minutes, all 4 members present. Fill in `[bracketed]` placeholders.
Slide content is written to be pasted directly into PowerPoint (keep bullets short
on the slide; the *spoken* detail lives in the script below).

---

# PART A — SLIDE CONTENT

---

## SLIDE 1 — Title & Members  *(Section I: Name)*

**The Effect of Holoparasitic Sink Dynamics on the Vascular Percolation
Threshold of Host Plants**
*A Computational Biophysics Model Using Pre-Fractal Hydraulic Networks*

- **Researchers:** [Member A], [Member B], [Member C], [Member D]
- [School / Strand] · [Subject / PR2] · [Date]

> *Speaker note: 1 slide, just read the title and names.*

---

## SLIDE 2 — Working Title & Big Question  *(Section II: Proposal)*

**Working title:** *The Effect of Holoparasitic Sink Dynamics on the Vascular
Percolation Threshold (p_c) of Host Plants.*

**One-line question:**
> *How much of a crop's internal "plumbing" can a parasite drain before the whole
> network suddenly collapses — and can we predict that point before the plant
> looks sick?*

- Reference parasite: *Cuscuta campestris* (dodder)
- New metric proposed: **Vascular Percolation Threshold, p_c**

---

## SLIDE 3 — Why This Topic  *(Section III: Reasons / Justifications)*

- **A real agricultural threat.** Parasitic weeds (*Cuscuta*, and relatives
  *Striga* / *Orobanche*) cause major crop yield loss; *Striga* alone threatens
  ~50 million farmers in sub-Saharan Africa.
- **Detection happens too late.** Current methods (visual scouting, drones) spot
  *wilting* — which occurs **after** the damage is irreversible.
- **A gap no one has bridged.** Three research areas exist separately and have
  **never been combined**:
  1. Plant **hydraulic failure** 2. **Cuscuta** parasite biology 3. **Network
  theory** of how connected systems break.

> *Hook to memorize: "By the time you see it, it's already too late."*

---

## SLIDE 4 — Expected Contribution  *(Section IV: Growth of Knowledge)*

- **A new predictive metric — p_c**, the *mathematical tipping point* of vascular
  collapse. (First study to apply **percolation theory** to a parasite-stressed
  plant network.)
- **A pre-symptomatic early-warning window** — defines the danger line *before*
  visible symptoms.
- **A breeding insight** — denser vein networks (higher fractal dimension *D*)
  resist collapse longer → a target for resistant crops.
- **A general framework** — re-parameterizes for *Striga*, *Orobanche*, etc.

---

## SLIDE 4B — Generality: It's Not Just Dodder  *(supports Section IV)*

The same framework ranks **four** parasitic weeds on the same host (lower p_c =
collapses sooner = more devastating):

| Parasite | Type | Attacks | p_c |
|---|---|---|---|
| *Orobanche* (broomrape) | holoparasite | root | **0.15** |
| *Cuscuta* (dodder) | holoparasite | stem | **0.18** |
| *Striga* (witchweed) | hemiparasite | root | **0.26** |
| Mistletoe | hemiparasite | branch | **0.42** |

- **Full parasites collapse the host sooner** than partial (photosynthetic) ones.
- **Root attack** (severing the base) is more devastating than **stem attack**.

> *Visual: the `parasites.png` bar chart. Answers the judge's "only Cuscuta?".*

---

## SLIDE 5 — Core Equations  *(optional: formulas needed)*

| Equation | Plain meaning |
|---|---|
| Murray's Law: **r_p³ = r₁³ + r₂³** | how vessels branch (sizes of pipes) |
| Hagen–Poiseuille: **R = 8ηL / πr⁴** | a pipe's resistance to flow |
| Hydraulic Ohm's Law: **Q = ΔΨ / R** | flow = pressure ÷ resistance |
| Haustorial sink: **Q = K_h (Ψ_host − Ψ_parasite)** | the parasite's "leak" *(our variable K_h)* |
| Percolation scaling: **P∞ ~ (p − p_c)^β** | how the network collapses near p_c |
| *(Future work)* Reaction–diffusion: **∂C/∂t = D∇²C + f(C) − σ** | resource depletion over time |

---

## SLIDE 6 — Methodology  *(1–6 sequence)*

1. **Generate** a synthetic reticulate vascular network (Murray's-law branching +
   loops, like real leaf veins).
2. **Measure** its fractal dimension **D** by box-counting.
3. **Solve** water flow with Kirchhoff's laws; attach the parasite as a
   haustorial **sink (K_h)**; let over-stressed vessels **embolize**.
4. **Monte Carlo:** remove vessels over many trials; track the **Giant Connected
   Component (GCC)** — collapse = GCC < 50%.
5. **Logistic regression** on the trials → pinpoint **p_c** (with a confidence
   interval).
6. **Sweep** K_h × D → build the **p_c surface** (heatmap of vulnerability).

> *Visual: small flow diagram, left→right arrows between the 6 boxes.*

---

## SLIDE 7 — Related Literature  *(Section V: RRL)*

**Hydraulic failure & embolism**
- Sperry et al. (2003); Tyree & Sperry (1989); Urli et al. (2013, *Tree Physiol.*)

**Cuscuta / parasite biology**
- Shen et al. (2020, *Mol. Plant*); Yoshida et al. (2019); Hibberd & Jeschke (2001)

**Network theory & percolation**
- Albert & Barabási (2002, *Rev. Mod. Phys.*); Callaway et al. (2000, *PRE*)

**Vascular geometry & fractal dimension**
- Murray (1926) / McCulloh et al. (2003, *Nature*); West et al. (1997, *Science*);
  Crisci et al. (*Relbunium* leaf-vein fractal dimension); Katifori et al. (2015)

> *Gap statement (say aloud): these bodies of work exist independently — we are
> the first to combine them.*

---

## SLIDE 8 — Closing line *(optional)*

> **We turn an invisible, too-late diagnosis into a measurable, early-warning
> number — p_c.**  *Thank you.*

---
---

# PART B — 5-MINUTE SPOKEN SCRIPT (4 members)

*Total ≈ 5 min. Each member ≈ 70–75 seconds. Pattern: say the **technical term**,
then immediately **re-explain it simply**. Practice the transitions ("I'll now
hand over to…").*

---

### 🎤 MEMBER A — Title + the Problem  *(~70s, Slides 1–3)*

"Good [morning], everyone. We are [A], [B], [C], and [D], and our research is
titled *'The Effect of Holoparasitic Sink Dynamics on the Vascular Percolation
Threshold of Host Plants.'*

Let me unpack that. Our subject is *Cuscuta campestris*, a **holoparasite** —
in plain terms, a parasitic vine that has completely given up making its own food
and survives by stealing water straight from crops. It feeds through **haustoria**
— think of them as tiny biological **straws** that drill into the plant's
**vascular tissue**, which is just its internal plumbing.

Here's the problem, and why we chose this topic: by the time a farmer *sees*
trouble — wilting, yellowing — the crop's internal water network has already
collapsed. The damage is done. Detection today is simply **too late**. I'll hand
over to [B] to explain what's missing in the science."

---

### 🎤 MEMBER B — The Gap + Our Contribution + the Physics  *(~75s, Slides 4–5)*

"Thanks, [A]. What's missing is that **three areas of science have never been
combined**: plant **hydraulic failure** — how a plant's water system breaks;
**parasite biology** — how *Cuscuta* feeds; and **network theory** — the
mathematics of how any connected system, like a power grid or a road map, falls
apart.

Our contribution is to bridge all three with one number: the **Vascular
Percolation Threshold**, which we call **p_c**. In simple terms, **p_c is the
tipping point** — the exact fraction of the plant's water pipes that can be lost
before the entire network suddenly *shatters* into disconnected islands.

And we don't invent the physics — we use established laws: **Murray's law** for
how vessels branch, the **Hagen–Poiseuille equation** for flow resistance — which
is really just *thinner pipe, harder to push water through* — and **percolation
theory** for the collapse itself. The key claim: **p_c is crossed before the
plant looks sick.** [C] will now walk through how we actually compute it."

---

### 🎤 MEMBER C — Methodology  *(~75s, Slide 6)*

"Thank you, [B]. Our method has **six steps**.

**One**, we **generate a synthetic vascular network** — a computer model of the
plant's pipes — that branches realistically and includes **loops**, like the
veins in a real leaf. **Two**, we measure its **fractal dimension, D**, using
**box-counting** — basically a single number for *how densely the veins fill the
space*. **Three**, we **simulate the water flow** using **Kirchhoff's laws** —
the same circuit math used for electricity — and we add the parasite as a *leak*.

**Four**, the core step: a **Monte Carlo simulation** — we attack the network
*a million times*, removing pipes at random, and we watch the **Giant Connected
Component** — the largest surviving connected chunk. When it drops below half, the
plant has *collapsed*. **Five**, we use **logistic regression** — a standard
statistical method — to pinpoint **p_c** precisely. **Six**, we **sweep** the
parasite's strength against the network's shape to map how p_c changes. [D] will
close with why this matters."

---

### 🎤 MEMBER D — Significance + Literature + Close  *(~70s, Slides 4, 7–8)*

"Thanks, [C]. So what does this contribute? **Three things.** First, it
**reframes detection** — instead of waiting for wilting, we define the danger
line that comes *before* it. Second, our framework shows that **denser vein
networks resist collapse longer** — which gives plant breeders a concrete target
for tougher, more resistant crops. Third, it's **general** — we ran the
same model on *Striga* and *Orobanche* — parasitic weeds that threaten tens of
millions of farmers — and it doesn't just work, it **ranks** them: broomrape and
dodder collapse the host the fastest, witchweed and mistletoe more slowly. So
this isn't a one-parasite trick.

Our work stands on solid literature: **Sperry** on hydraulic failure, **Shen**
and **Yoshida** on *Cuscuta* biology, **Albert and Barabási** on network attack,
and **Crisci** on real leaf-vein fractal dimensions — which we use to *validate*
our model against actual plants.

To put our whole project in one sentence: **we turn an invisible, too-late
diagnosis into a measurable, early-warning number — p_c.** Thank you."

---

## ⏱ Timing & delivery tips
- 4 × ~72s = ~4:48 — leaves a small buffer. **Practice once with a timer.**
- Every technical term gets **one plain sentence** right after it — never leave a
  jargon word un-translated.
- Hand-offs ("I'll hand to [B]…") keep it smooth and show teamwork.
- Memorize the two anchor lines: *"By the time you see it, it's already too late"*
  and *"p_c is crossed before the plant looks sick."*
- If you have **30 extra seconds**, [B] or [C] can mention: *"Our preliminary
  model already produces a sharp threshold at about 28% vessel loss, and we
  validated its fractal dimension against real leaf measurements."*
