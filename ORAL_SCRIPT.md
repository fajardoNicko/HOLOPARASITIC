# Oral Presentation Script — PR2 Topic Proposal
### Group 9 · VCSMS · June 2026
**Deck:** 8 slides · **Target:** ≈ 5 min 45 s · **Speakers:** 4

---

## ⚠️ FIX THESE ON THE SLIDES BEFORE YOU PRESENT

Three errors a panel *will* see:

| Slide | Says | Should say |
|---|---|---|
| 5 (Methodology) | "Kirch**hh**off's laws" | "Kirch**h**off's laws" |
| 6 (RRL) | "Parasitic **Plans** as an Agricultural Threat" | "Parasitic **Plants**…" |
| 3 (Justification) | "There are no studies that **looks** into" | "…that **look** into" |

Also on **Slide 3**, soften bullet 2 to **"We could find no study that models the host's failing vascular network."** The absolute claim *"there are no     studies"* is unfalsifiable and a panelist can kill it with one counterexample. The hedged version is bulletproof and sounds *more* rigorous, not less.

---

## ⏱ TIMING & SPEAKER MAP

| Speaker | Slides | Time | Job |
|---|---|---|---|
| **Member A** | 1 – 3 | ~80 s | The hook + why this matters |
| **Member B** | 4 | ~55 s | What we will deliver |
| **Member C** | 5 | ~2 min | How we will do it (the meat) |
| **Member D** | 6 – 8 | ~95 s | What the literature says + close |

**The one rule:** *nobody reads a bullet out loud.* The panel can read. Your job is to say
the thing that is **not** on the slide.

---
---

# 🎤 MEMBER A — Slides 1 to 3 *(~80 seconds)*

### SLIDE 1 — Cover
> *Stand still. Do not start talking until the room is quiet. Then:*

**"Good [morning/afternoon]. We are Group 9, and our research is about a plant that
kills its host without ever leaving a mark — until it's too late."**

*(Beat. Advance.)*

---

### SLIDE 2 — Title

**"Our title is 'Holoparasitic Haustorial Sink Dynamics and Pre-Symptomatic
Giant-Component Collapse in Host Xylem Networks.'**

**Let me unpack that in plain terms.**

**A *holoparasite* is a plant that has completely given up photosynthesis. It has no
working chloroplasts. It cannot feed itself at all — so it drills into a crop and drinks.
The organ it drills with is called a *haustorium*, and once it connects to the host's
xylem, it becomes a permanent leak in the plant's plumbing.**

**Our study asks one question:
how much of that plumbing can a parasite drain before the whole network suddenly
collapses — and can we see that coming *before* the plant looks sick?"**

*(Advance.)*

---

### SLIDE 3 — Justification

> *Do NOT read the three bullets. Tell the story underneath them.*

**"Here is the problem. By the time a farmer *sees* a parasitized crop wilting, the plant
is already gone. Wilting is not an early warning — it's an obituary. The damage happens
silently, inside the vascular system, weeks before anything shows on the outside.**

**Now, there is an enormous amount of research on parasitic plants. But almost all of it
looks at the *parasite* — its genetics, its molecular biology, how the haustorium forms.
We could find no study that turns the camera around and models what is happening to the
**host's** network as it fails.**

**And this is not a foreign problem. The Philippines is a global hotspot for parasitic
plants — *Rafflesia*, *Balanophora*, and *Aeginetia indica*, which is a documented pest of
our own **rice and sugarcane**. The local computational work that does exist maps *where
these species grow*. Nobody has modeled what they *do* to the plant they're growing on.**

**That gap is our study."**

> 👉 **Handoff:** **"[Member B] will now tell you what we expect to contribute."**

---
---

# 🎤 MEMBER B — Slide 4 *(~55 seconds)*

### SLIDE 4 — Expected Contribution

**"We expect this study to produce three things.**

**First — a new predictive metric we call **p-sub-c**, the vascular percolation threshold.
It is a single number: the fraction of a host's vessels a parasite must drain before the
transport network collapses. Not when the plant *looks* dead — when the plumbing
*functionally* fails. And because that is a topological event, it happens **before** any
visible symptom.**

**Second — a quantitative resistance trait. We expect p-sub-c to depend on how densely
veined the host is. If that holds, then a plant's **architecture is a defence** — and
vein density becomes something a breeder can actually screen and select for.**

**Third — and this is the one that matters to a farmer — a **pre-symptomatic warning
window.** If we know the threshold, and we model how fast an infestation grows, we can
compute the gap between the moment the plant *functionally* dies and the moment it
*visibly* wilts. That gap is the only time you have to intervene. Right now, nobody knows
how wide it is.**

**We intend to put a number on it."**

> 👉 **Handoff:** **"[Member C] will walk you through how."**

---
---

# 🎤 MEMBER C — Slide 5 *(~2 minutes)*

### SLIDE 5 — Methodology *(the 6-box flowchart)*

> *Point at each box as you go. Move left to right. Don't rush box ④ — it's the core one.*

**"Our methodology has six steps, and it's entirely computational — in Python.**

**① First, we **generate a synthetic vascular network**. We build a branching tree where
every vessel splits according to **Murray's Law** — the biologically optimal branching
rule — and every vessel gets a **Hagen–Poiseuille resistance**, meaning its conductance
scales with the **fourth power** of its radius. Then, crucially, we add **cross-links** —
because real leaves are not trees, they are **meshes**. They have loops. That reticulation
is what makes this whole study possible.**

**② Second, we **measure the fractal dimension D** of that network by **box-counting** —
overlaying grids of shrinking size and counting how many boxes the veins occupy. D tells
us how space-filling the venation is. It's our knob for host architecture.**

**③ Third, we **solve the water flow.** We use three laws together. **Hagen–Poiseuille**
gives each vessel its resistance. **Darcy's law**, the hydraulic Ohm's law, says flow
equals pressure difference over resistance. And **Kirchhoff's current law** enforces that
whatever water flows into a junction must flow out. Put together, the entire plant becomes
one giant **resistor circuit**, and we solve it as a sparse linear system.**

**Then we attach the parasite. The haustorium enters as **one term** — a leak conductance,
K-sub-h, tying a host vessel to a reservoir at a *more negative* water potential. That
term **is** sink strength.**

**And here's the bridge: when a vessel gets pulled past its **cavitation threshold**, an
air bubble forms, it **embolizes**, and it is **deleted** from the network. A hydraulic
event becomes a topological event.**

**④ Fourth — **Monte Carlo.** We disable vessels at increasing infestation loads and, after
every single trial, we measure the **giant connected component** — the largest surviving
piece of plumbing still attached to the root. We define **collapse as the GCC falling below
50%** — the plant can no longer supply half its leaves. We run this **one million times.**

**⑤ Fifth, we fit a **logistic regression** across those million trials. All those
collapse-or-survive outcomes become one smooth **S-curve**, and the threshold is where that
curve crosses fifty percent. Bootstrapping gives us a genuine **confidence interval** — so
p-sub-c comes out as a real measurement with real error bars, not a guess.**

**⑥ And finally, we **sweep** — varying parasite aggressiveness, K-sub-h, against host
architecture, D — to build a **p-sub-c surface.** A **heatmap of vulnerability.** Which
parasites are most dangerous, and which host architectures survive them."**

> 👉 **Handoff:** **"[Member D] will close with the literature this stands on."**

---
---

# 🎤 MEMBER D — Slides 6 to 8 *(~95 seconds)*

### SLIDE 6 — RRL: Agricultural Threat + Philippine Context

> *Do not read the citations. Summarize the theme, then land the gap.*

**"Our review rests on four themes.**

**The first establishes the **threat.** Holoparasites lack functional chloroplasts and depend
entirely on a host — that's Casadesús and Munné-Bosch, and Twyford. They connect through
haustoria, which continuously extract water, nutrients, and carbohydrates. And the documented
consequences are exactly what we're modeling: reduced photosynthesis, reduced biomass, and
**impaired water transport.**

**The second is the **Philippine context**, and it's the reason this research belongs here.
*Aeginetia indica* is a root holoparasite found throughout the country — an occasional pest of
**rice and sugarcane.** We are a biodiversity hotspot for *Rafflesia* and *Balanophora*.**

**But notice the last line. The existing Philippine computational work — Obico and colleagues —
models **species distribution.** Where the parasites *are*. **Not what they do to the host's
vascular physiology.** That is the gap, stated in our own local literature."**

*(Advance.)*

---

### SLIDE 7 — RRL: Haustoria as Hydraulic Sinks

**"The third theme is the one that gives us our central assumption — and it's the strongest
support we have.**

**The literature already establishes that a haustorium connects directly to the host's xylem,
and that it functions as **an additional hydraulic sink** — Mateus and colleagues, this year.
It **diverts water away from the plant's normal tissues.** Its **sink strength** varies with
parasite biomass and developmental stage. And that diversion creates **localized hydraulic
deficits** in the host.**

**Read that again, because it is a description of our model. The literature is telling us —
in words — that the haustorium is a **sink node with a variable strength that drains a
network.** We are simply the first to write it down as **an equation** and ask the obvious
next question: *at what point does the network give out?*

**That question has a name in physics. It's a **percolation threshold.** And nobody has
computed it for a parasitized plant."**

*(Advance.)*

---

### SLIDE 8 — References / Close

> *Don't read references. Use this slide as your closing canvas.*

**"So to summarize.**

**The literature independently tells us three things: that haustoria are hydraulic sinks,
that vessels fail by embolism, and that vascular networks can be solved as electrical
circuits. **No one has combined the three.** When you do, you get a question with a real
answer — and that answer is a single number that tells you when a crop is already dying
while it still looks perfectly healthy.**

**We are not trying to save a plant that already looks sick.
We are trying to find it *before* it does.**

**Thank you. We're happy to take your questions."**

---
---
---

# 🛡 Q&A PREP — *everyone must know these*

You have preliminary results. **Do not volunteer them** — this is a proposal, and the slides
are proposal-framed. But if a panelist asks *"do you have anything yet?"*, this is your
moment, and it is a strong one.

### ▸ "Do you have any preliminary results?"
> **"Yes. Our pipeline is already running. Preliminary p-sub-c is **0.279, plus or minus
> 0.002**, from a full one-million-trial run. That means a holoparasite only needs to drain
> about **28%** of the host's vessels to collapse the network — not 50, not 80. And the point
> at which the plant *visibly* wilts is far later, around 84%. **That gap is the warning
> window we're trying to quantify.**"**

### ▸ "Why 28% and not 50%? Isn't that surprising?"
> **"It is — and that's the finding. It's counterintuitive because we imagine plants dying
> gradually. They don't. It's a **phase transition** — a cliff. The network holds, holds,
> holds, and then fails all at once. That sharpness is exactly *why* the damage is
> pre-symptomatic."**

### ▸ "Did you use Darcy's law?" *(likely, given your Slide 5)*
> **"Yes. Every edge in our network obeys Q = conductance × pressure difference — that **is**
> Darcy's law. Kirchhoff isn't an alternative to it; it's the **conservation** law that
> stitches all those Darcy elements together into one solvable system. Hagen–Poiseuille sets
> each conductance from the vessel radius. We use all three, at three different levels."**

### ▸ "How do you know your synthetic network is realistic?"
> **"Two ways. Our measured fractal dimension, **D ≈ 1.43**, falls inside the published
> real-leaf venation range of **1.39 to 1.76.** And we are planning empirical validation —
> top-down venation photographs and stem cross-sections across **five species**, at least five
> plants each, to measure real D and the real Murray's-law exponent and test them against
> the model."**

### ▸ "What are your limitations?" *(ANSWER THIS HONESTLY — it wins points)*
> **"Three, openly. One, our network is **2-D**; real vasculature is 3-D. Two, **K-sub-h is
> uncalibrated** — no published study reports a haustorial volumetric flux, so we **sweep it
> as a range** rather than fit it to a value. That is a stated gap in the literature, not a
> shortcut on our part. Three, we model the shoot with the root as a single source node, so
> root parasites are **approximated**. A full root system is future work."**

> ⚠️ **Never oversell.** If asked whether a farmer could use this tomorrow, say **no** —
> the model is a **framework** producing a **falsifiable prediction**, and the next step is
> testing it on real leaves. A panel forgives an uncalibrated model. It does **not** forgive
> one pretending to be calibrated.

### ▸ "Why should we care?" — *the one-sentence answer*
> **"Because we found that the plant is functionally dead at 28% vessel loss but doesn't
> *look* dead until 84% — which means there is a long, measurable window where the crop is
> already lost and still looks perfectly fine. p-sub-c is the number that tells you when
> that window opens."**

---

## 🎯 REHEARSAL CHECKLIST
- [ ] Fix the 3 slide typos above.
- [ ] Every member can answer **all** Q&A items, not just their own slides.
- [ ] Member C rehearses Slide 5 alone — it's half the talk and the easiest to rush.
- [ ] Practice the **handoff lines**. Dead air between speakers is what makes a group look
      unprepared.
- [ ] Time a full run. If over 6 minutes, cut from **Member C's box ③** (compress the three
      laws into one sentence), **not** from the justification or the close.
