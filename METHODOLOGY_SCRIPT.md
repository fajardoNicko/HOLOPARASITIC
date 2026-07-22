# Methodology — Comprehensive Speaking Script
### The six steps, explained from first principles
**Speaker:** Member C · **Slides:** 5 – 10 (Proposal Defense deck) / Slide 5 (PR2 deck)

---

## HOW TO USE THIS DOCUMENT

This is the **long form**. It is deliberately longer than you can deliver — that is the point.
You cannot speak a step convincingly that you only half-understand, and a panel's follow-up
question always lands one level *below* the level you spoke at. So learn this, then deliver
the tier that fits your clock.

Each step has four parts:

| Part | What it is | Use it |
|---|---|---|
| **▶ SAY** | word-for-word delivery | out loud |
| **▼ THE LOGIC** | why this step exists at all | to answer *"why did you do it that way?"* |
| **⚙ THE MECHANICS** | what the code actually does | to answer *"how, specifically?"* |
| **🛡 IF ASKED** | the panel's likely probe + your answer | only when probed |

**Three delivery tiers.** Pick one *before* you rehearse, not during:

- **TIER 1 — 2 minutes** (PR2 proposal, one methodology slide): the **▶ SAY** blocks only,
  and only the sentences marked **[CORE]**.
- **TIER 2 — 4 minutes** (full defense, slides 5–10): all **▶ SAY** blocks, complete.
- **TIER 3 — unbounded** (the Q&A, the panel that actually cares): everything.

**The rule that governs all three:** never read a bullet aloud. The panel can read faster than
you can talk. Your entire job is to say the thing that is *not* printed on the slide — the
*why*. The slide carries the *what*.

---

## THE ONE-BREATH VERSION

Before the six steps, plant the shape of the whole thing. If the panel loses the thread at
step 4, this is what they fall back on. Say it once, at the top, and do not rush it:

> **[CORE]** **"Everything we do reduces to one sentence: we turn a plant into a circuit, we
> turn the parasite into a leak in that circuit, and then we ask at what point the circuit
> stops being a circuit. Steps one and two build the plant. Step three makes it a circuit and
> attaches the leak. Steps four and five find the breaking point. Step six asks what changes
> it."**

*(Beat. Then go to step one.)*

---
---

# ① GENERATE THE SYNTHETIC VASCULAR NETWORK
### *Slide 6 · ~45 s in Tier 2 · Output: the host plant, as a graph*

## ▶ SAY

**[CORE]** **"Step one. We build the host — but we build it in the computer, as a graph. Nodes
are vascular junctions. Edges are xylem vessels. That is the whole abstraction: a plant's
plumbing is a set of pipes meeting at junctions, and that is exactly what a graph is."**

**[CORE]** **"We grow it by recursive bifurcation — every vessel splits into two, nine
generations deep. That gives us 1,023 nodes: one root, 510 internal junctions, and 512
terminal nodes, which are the leaf sites where water evaporates."**

**"But a branching tree alone is not a plant, and the two rules we impose are what make it
one.**

**First — Murray's Law. When a vessel splits, the cube of the parent's radius equals the sum
of the cubes of the daughters' radii. Murray derived that in 1926 from a minimum-work
argument: it is the branching ratio that moves fluid at the least total metabolic cost. It is
not a rule we invented for convenience — it is the rule that real vasculature converges on,
in plants and in animals both.**

**Second — Hagen–Poiseuille. Every vessel gets a hydraulic resistance: R equals eight eta L
over pi r to the fourth. The part that matters is that **fourth power**. Halve a vessel's
radius and you don't double its resistance — you multiply it by sixteen. Which means the
network's behaviour is dominated, overwhelmingly, by its widest vessels. That single fact is
why the network has a backbone worth attacking, and it comes back in step six."**

**[CORE]** **"And then the step that the whole study depends on. We add 2,044 cross-links —
anastomoses — turning the tree into a **reticulate mesh**. Final network: 1,023 nodes, 3,066
vessels, mean degree about six.**

**[CORE]** **"I want to be very direct about why. **A tree has no loops. A network with no
loops has no percolation transition — none, mathematically.** Cut any single edge of a tree
and everything downstream is orphaned instantly; there is no threshold to find, because every
edge is already critical. If we had modelled the plant as a pure tree, the number this entire
study exists to measure would **not exist.** Reticulation is not a refinement we added for
realism. It is the precondition of the question.**

**And it is also simply what leaves are. Real venation is looped and mesh-like. Ronellenfitsch
and Katifori showed those loops emerge from a real trade-off — efficiency against cost against
robustness — and that loops are precisely what lets flow **reroute around damage.** A model
without loops wouldn't be a simplified plant. It would be a structure that fails in a way no
real leaf fails."**

## ▼ THE LOGIC

Why synthesize a network instead of using a real digitized leaf?

1. **Control.** We need to vary architecture (D) as an *independent variable*. You cannot ask
   a real leaf to be 8% more densely veined while holding everything else fixed.
2. **Sample size.** We need thirty independent networks per condition to report D as a
   distribution rather than an anecdote. There is no dataset of thirty statistically matched
   real leaves.
3. **Falsifiability.** A synthetic network makes the *assumptions* explicit and therefore
   testable — which is what the empirical validation phase then does.

Why 9 generations? It is the smallest depth at which the finite-size scaling analysis still
sharpens cleanly (we test 6→10) while keeping 10⁶ trials tractable on a consumer machine. It
is a tractability choice, and we say so.

## ⚙ THE MECHANICS

- Recursive bifurcation → NetworkX graph, positions assigned geometrically so the network can
  be rasterized in step 2.
- Radii assigned top-down from Murray's Law with the branching exponent **fixed at 3**.
- Conductance `g = 1/R` is the quantity actually carried on each edge — the solver never sees
  R, because Kirchhoff assembly wants conductances.
- Anastomoses added between spatially proximate nodes of similar generation (not at random
  across the whole graph — that would create biologically absurd shortcuts from a leaf tip to
  the root).
- Everything seeded. Same seed → byte-identical network.

## 🛡 IF ASKED

**"Why exponent 3, and not 2 or 2.5?"**
> "Murray's original derivation gives exactly 3 for laminar flow under minimum work. And it
> survives the obvious objection — Skjegstad and Kirkegaard, this year, extended Murray's Law
> specifically to **reticulate** venation rather than pure trees, which is our case, and they
> recover optimal exponents close to 3 for full-scale leaf networks. So the value is defended
> for the geometry we're actually using. It's also the one assumption our empirical phase
> tests directly: we measure the real exponent from stem cross-sections and test the null that
> it equals 3."

**"Isn't 1,023 nodes tiny compared to a real leaf?"**
> "Yes, absolutely — a real leaf has orders of magnitude more. But the quantity we measure is
> a **critical threshold**, and thresholds are scale-invariant properties, not extensive ones.
> That's not an assumption we're asking you to grant — we test it. Our finite-size scaling
> analysis runs the whole pipeline from 6 to 10 generations and shows the transition **sharpens**
> as the network grows while the threshold stays put. That's the signature of a real phase
> transition. If the threshold had drifted with size, we'd have a finite-size artifact, and
> we'd have to say so."

**"Why not just use a real leaf image?"**
> "That's phase two — the empirical validation. But it can't replace the synthetic phase,
> because we need D as a *controlled* variable, and a real leaf hands you exactly one value of
> D with no way to move it."

---
---

# ② MEASURE THE FRACTAL DIMENSION D
### *Slide 6 · ~30 s · Output: D = 1.434 ± 0.007*

## ▶ SAY

**[CORE]** **"Step two. We have a network — now we need one number that captures its
**architecture**, because architecture is going to be our host-side variable. That number is
the fractal dimension, D, and we get it by **box-counting**."**

**"The procedure is simple enough to picture. Rasterize the network. Overlay a grid, and count
how many boxes contain vein. Then shrink the boxes and count again. We do this from sixteen
boxes per side up to 1,024. Plot the log of the occupied-box count against the log of one over
box size, take the slope — that slope is D."**

**"What D **means** is how aggressively the venation fills space. D near 1 is a sparse line —
think of the parallel venation of a monocot. D approaching 2 is a mesh so dense it's
effectively a filled sheet. Real leaves live in between, and D is the knob we turn to ask:
does how a host is *built* determine how long it survives?"**

**[CORE]** **"Our networks measure **D = 1.434**, and the published range for real leaf
venation is **1.39 to 1.76.** We land inside it. And D is dimensionless — it's a ratio of
logarithms — so we never have to commit the model to millimetres for this to be a fair
comparison."**

**"One honest caveat, and we raise it ourselves rather than wait to be caught on it. Vishnu
and colleagues showed that box-counting on leaves has two systematic failure modes: leaves are
only self-similar over a **limited band of scales**, so fitting across all scales returns a
biased D; and the count is sensitive to where you happen to place the grid. So we fit only
over the **genuinely linear window**, and we report D as **one descriptor** of architecture —
not a complete characterization of it."**

## ▼ THE LOGIC

D is doing one job: it is the **host-architecture axis** of the step-6 sweep. We need
architecture reduced to a scalar or we cannot put it on an axis. D is the standard,
literature-backed, dimensionless scalar for exactly this.

Why report D as a *distribution* over 30 seeds rather than one number? Because any single
generated network is one draw from a stochastic process. A single D is an anecdote. A mean
with a t-based CI separates *the model's systematic architecture* from *run-to-run noise* —
and it's the only form in which D can be t-tested against real leaf measurements later.

## ⚙ THE MECHANICS

- Network rasterized to a binary occupancy grid.
- Box sizes k ∈ {16 … 1024}, log-spaced.
- `D` = OLS slope of `log N(ε)` on `log(1/ε)`, restricted to the scale-invariant window.
- 30 seeds → mean, SD, 95% CI via Student's *t*.

## 🛡 IF ASKED

**"Isn't the fractal dimension of a leaf a contested measurement?"**
> "It is, and that's why we cite Vishnu explicitly and window the fit. We're not claiming D is
> the *truth* about venation — we're claiming it's a **defensible, reproducible descriptor**
> that we apply **identically** to synthetic and to real leaves. Even if D carries systematic
> bias, the bias is the *same on both sides of the comparison*, which is what makes the
> comparison valid."

**"Why does D even matter to percolation?"**
> "Because D is a proxy for reticulation density, and reticulation is what supplies alternate
> paths. More loops, more reroutes, more damage absorbed before the network fragments. That's
> the mechanism, and step 6 is the test of it — and it holds: ↑D → ↑p_c."

---
---

# ③ SOLVE THE WATER FLOW · ATTACH THE PARASITE · LET VESSELS EMBOLIZE
### *Slide 7 · ~60 s · This is the physics core. Do not rush this step.*

## ▶ SAY

**[CORE]** **"Step three is the heart of the model, and it has three parts: solve the flow,
attach the parasite, and then — the important one — connect the physics to the topology."**

### Part A — three laws, three levels

**[CORE]** **"We use three laws, and they are not competing. They operate at three different
levels of description.**

**Hagen–Poiseuille works at the level of **one vessel.** It converts a radius into a
conductance. That's it. That's its whole job.**

**Darcy's law — in its hydraulic Ohm's-law form — works at the level of **one conduit's
flow.** Flow equals conductance times the difference in water potential across it. Q equals g
times delta psi. It is Ohm's law with water potential where voltage would be.**

**Kirchhoff's Current Law works at the level of **the junction.** It says: whatever water
flows into a node must flow out of it. Conservation of mass, nothing more.**

**[CORE]** **"Now watch what happens when you apply Darcy to every single edge and Kirchhoff
to every single node **simultaneously.** You get one equation per node, and one unknown per
node. The whole plant collapses into a single **sparse linear system** — the conductance
Laplacian times the vector of unknown potentials equals a boundary vector. **The plant is a
resistor circuit.** We solve it once and we know the water potential at every junction in the
network."**

**"Boundary conditions, because a linear system needs them. The root node is held at zero
megapascals — that's the soil–stem interface. Every terminal leaf node is held at negative one
megapascal — that's transpirational pull, the suction the atmosphere exerts on the leaf. Water
flows from high potential to low, so it moves root to leaf. That's the healthy plant."**

**"And I want to be clear this isn't a liberty we took. Wason and colleagues modelled embolism
spread through **real grapevine xylem** with exactly this machinery — Hagen–Poiseuille plus
conservation of mass, solved as a resistor circuit. The formulation is the established one in
quantitative xylem hydraulics. **What's new is not the method. It's the target.** They pointed
it at drought. We point it, for the first time, at a parasite."**

### Part B — the parasite

**[CORE]** **"Now the parasite. And this is the part I most want to land, because it's where
the biology becomes an equation.**

**The haustorium enters our model as **one term.** One. It is a **leak conductance, K_h**,
tying a host node to a parasite reservoir held at **negative three megapascals.**

**Why negative three? Because that is **more negative than anywhere in the healthy host** —
the leaves only reach negative one. Water always flows down the potential gradient, so making
the parasite the most negative thing in the system is what makes the water go **into** it
rather than out. The parasite doesn't pump. **It doesn't have to.** It simply offers a steeper
hill, and physics does the rest. That is what parasitism *is*, hydraulically.**

**The flow into it is K_h times the difference between the host node's potential and the
parasite's. And that single parameter, K_h, is our primary independent variable — because
**K_h is mathematically identical to haustorial sink strength.** The literature already tells
us in words that a haustorium is an additional hydraulic sink whose strength varies with
biomass and developmental stage. We are writing that sentence down as an equation."**

### Part C — the bridge

**[CORE]** **"And here is the hinge of the entire study.**

**Xylem doesn't carry water under push. It carries it under **tension** — the column is
literally stretched. Pull it too hard and the column snaps: a bubble nucleates, and the vessel
**cavitates.** It embolizes. It is now a pipe full of air, and an air-filled pipe conducts
nothing.**

**So: when our solver finds a vessel drawn below **negative two megapascals**, we **delete
that edge from the graph.** Permanently.**

**[CORE]** **"Read what just happened. A **hydraulic** event — too much tension — became a
**topological** event — an edge vanishing from a network. That single rule is what lets us
stop doing fluid mechanics and start doing **percolation theory.** Once vessels start
disappearing, 'when does the plant fail?' is no longer a question about water. It is a
question about **whether the graph is still connected.** And percolation theory has spent
sixty years learning how to answer that question."**

**"And this isn't us assuming a cliff exists so we can find one. Johnson and colleagues argue
independently, from plant physiology, that plants have genuine **hydraulic tipping points** —
that conductance collapses nonlinearly rather than degrading gently. They made the argument.
**We quantify it, for a parasitic sink.**"**

## ▼ THE LOGIC

Why steady state? Because the question is *"at what load does the topology fail?"*, not *"what
does Tuesday afternoon look like?"* Steady state is the correct altitude for a threshold
question, and transients (diurnal cycling, refilling) would add parameters we cannot calibrate
without buying precision we cannot honour. We state it as a limitation.

Why is K_h swept instead of fitted? **Because no published study reports a haustorial
volumetric flux.** There is nothing to fit to. This is a documented gap in the *literature*,
not a shortcut in our *method* — and the honest response to an uncalibratable parameter is to
sweep it and report the shape of the response, which is exactly what step 6 does.

Why −2.0 MPa for cavitation? It sits in the physiological range for the vulnerability curves
of mesic angiosperms. Like every parameter, it is centralized in the frozen `config.py`, and
the qualitative result — that a sharp threshold exists — is robust to moving it.

## ⚙ THE MECHANICS

- Assemble sparse conductance Laplacian `L`; solve `LΨ = b` with SciPy sparse.
- Dirichlet BCs: `Ψ_root = 0`, `Ψ_leaf = −1.0` MPa.
- Haustorium: add `K_h` to the diagonal of the attachment node and `K_h · Ψ_par` to `b`.
  (It is literally one extra conductance to a fixed-potential node — same as any boundary.)
- Cavitation: `Ψ_edge < −2.0` → drop edge → the graph is now different.
- A **small grounding term** is added to the diagonal so `L` stays non-singular even when
  severe infestation detaches a chunk of the network. Without it the solver returns a
  plausible, meaningless answer to a singular system — a silent failure, the worst kind.

## 🛡 IF ASKED

**"Did you use Darcy's law?"** *(near-certain — the slide invites it)*
> "Yes. Every edge obeys `Q = g·ΔΨ` — that **is** Darcy's law. Kirchhoff isn't an alternative
> to Darcy; it's the **conservation** law that stitches all those Darcy elements into one
> solvable system. Hagen–Poiseuille sets each conductance from the radius. Three laws, three
> levels: vessel, conduit, junction. We need all three."

**"A plant isn't a circuit."**
> "Agreed — it's an analogy, but it's a **structurally exact** one, not a metaphor. Water
> potential plays voltage, volumetric flow plays current, hydraulic resistance plays
> resistance, and Kirchhoff's law is just conservation of mass, which holds in both. The
> analogy is exact wherever flow is laminar and steady. Where it breaks — turbulence,
> transients, refilling — we've stated as limitations. And it's not our analogy: it's the
> standard formulation in the field, and Wason et al. applied it to real grapevine xylem."

**"Isn't K_h uncalibrated?"** *(the sharpest question available — answer it head-on)*
> "It is, and we say so on the slide before you ask. No published study reports a haustorial
> volumetric flux. So we do the only defensible thing: we **sweep K_h across a range** rather
> than assert a value, and we report how the threshold **responds** to it. What we claim is the
> *shape* of the response and the *ordering* of the parasites — both of which are robust. We
> do not claim the third decimal place. A model that pretends to a calibration it doesn't
> have does more damage to the record than one that's simply wrong."

**"Why −3.0 MPa for the parasite?"**
> "It only has to be **more negative than anywhere in the host** — that's the entire
> requirement, because it's what sets the direction of flow. The magnitude scales the flux,
> and the flux is already governed by K_h, which we sweep. So the qualitative behaviour
> doesn't hinge on that specific value."

---
---

# ④ MONTE CARLO PERCOLATION
### *Slide 8 · ~40 s · Output: 1,000,000 binary collapse/survive trials*

## ▶ SAY

**[CORE]** **"Step four. We now damage the network on purpose, and we do it a million times.**

**We define an **infestation load, rho** — the fraction of vessels drained or disabled. We
sweep rho from zero to one in fifty steps. At each of those fifty loads, we disable that
fraction of vessels and check what's left — and we repeat that **twenty thousand times.** Fifty
loads times twenty thousand repeats is **one million independent trials.**

**Why repeat it twenty thousand times instead of once? Because *which* vessels die is random,
and near the threshold the outcome is genuinely a coin flip. One trial tells you nothing. The
threshold is a **probability**, so you have to measure it as a frequency, and twenty thousand
per bin is what buys us error bars tight enough to distinguish parasites from each other."**

**[CORE]** **"After **every single trial**, we compute the **giant connected component** — the
largest surviving piece of plumbing **still attached to the root.** Attached to the root is the
key phrase. A perfectly intact vein that's been cut off from the water supply is, functionally,
dead tissue. It doesn't count.**

**[CORE]** **"And we define collapse: **the GCC falling below fifty percent** of the original
network. Our reasoning is simple — a plant that can no longer supply **half its leaves** has
functionally failed as a transport system, whether or not it has yet had the decency to look
wilted. Each trial gets recorded as a single bit. One for collapse, zero for survival."**

**"Using the giant component as the **order parameter** of network failure isn't our invention
— it's the standard instrument in percolation studies of network robustness. We're applying a
mature tool to a target it hasn't been pointed at."**

**"We also compare **three attack modes**, because we wanted to know whether *where* damage
happens matters as much as *how much*. **Random** removal — that's diffuse, systemic
infestation. **Targeted by betweenness** — a parasite that taps the vascular **backbone**, the
vessels the most flow routes through. And **targeted by degree** — attacking the most connected
junctions. Random failure versus centrality-targeted attack are the two canonical damage
regimes in the network literature, and they're known to give very different thresholds on the
*same* network. **The answer turned out to be yes** — and it's one of our strongest findings.
A backbone attack is nearly **twice** as efficient as random damage."**

**"One engineering note, because a million trials on a laptop invites scepticism. The hot loop
never touches NetworkX. We convert once, at the outset, to **integer-indexed SciPy sparse
matrices**, and the loop touches nothing else. That conversion is the entire reason 10⁶ trials
is a weekend and not a supercomputer."**

## ▼ THE LOGIC

Why 50% GCC as the collapse criterion? It is a **stipulated operational definition**, and we
own that. The defence is twofold: (1) it is physiologically motivated — half the canopy
unsupplied is unambiguous functional failure; (2) **the qualitative result does not hinge on
it.** Move the criterion and p_c shifts, but the *existence* and *sharpness* of the threshold,
and the *ordering* of the parasites, do not. That is what we claim.

Why Monte Carlo at all rather than an analytical result? Because analytical percolation
thresholds exist only for idealized degree distributions. Our network is neither
Erdős–Rényi nor a lattice — it is Murray-constrained, spatially embedded, and reticulated. No
closed form covers it. **But** we still check ourselves against theory where theory applies:
see the Molloy–Reed validation in the data-analysis section. That's how you use Monte Carlo
honestly — simulate what you must, but validate against closed form wherever you can.

## ⚙ THE MECHANICS

- ρ ∈ [0,1], 50 bins × 20,000 trials = 10⁶.
- Per trial: mask ρ·|E| edges → connected-components on the sparse adjacency → take the
  component containing the root → record `1` if `|GCC| < 0.5·N`, else `0`.
- Three removal orderings: random / betweenness-ranked / degree-ranked.
- Seeded RNG per trial index → the entire million is reproducible, not just the summary.

## 🛡 IF ASKED

**"Why 50%? That looks arbitrary."**
> "It's a stipulated operational definition, and we'd rather say that than dress it up. It's
> motivated — a plant that can't supply half its leaves has failed as a transport system. But
> the honest point is that **our claims don't rest on it.** Move the criterion and the number
> moves; the existence of a sharp threshold and the ranking of the parasites don't. We claim
> those. We don't claim the third decimal."

**"Why a million? Isn't that overkill?"**
> "It's what the error bars required. We're distinguishing parasite profiles whose thresholds
> differ by about 0.02 — *Striga* at 0.263 against *Pilostyles* at 0.277. To call that a real
> effect rather than sampling noise you need non-overlapping bootstrap CIs, and that needs the
> trial count. The precision isn't decoration; a claim depends on it."

**"Is random vessel removal biologically realistic?"**
> "For a diffuse systemic infestation, reasonably so. For a real parasite, no — and that's
> exactly why we don't only do random. That's what the targeted modes are for. And the
> comparison turned out to be one of our most interesting results: **where** a parasite taps
> beats **how greedy** it is. Hemiparasitic *Striga* collapses a host *sooner* than
> holoparasitic *Pilostyles*, because it attacks the root backbone."

---
---

# ⑤ THRESHOLD ESTIMATION — LOGISTIC REGRESSION + BOOTSTRAP
### *Slide 8 · ~35 s · Output: p_c = 0.279 ± 0.002*

## ▶ SAY

**[CORE]** **"Step five. A million trials gave us a million pairs: a load, and a bit. Now we
have to turn that into a **number with an error bar.**

**We fit a **binary logistic regression** — probability of collapse as a sigmoid function of
load. All those ones and zeros resolve into one smooth **S-curve.** And the threshold, p_c, is
simply where that curve crosses **fifty percent probability** — which falls out in closed form
as **minus the intercept over the coefficient.**

**Then **bootstrap resampling** — we resample the trials thousands of times and refit — which
gives us a genuine **ninety-five percent confidence interval.**

**[CORE]** **"So p_c comes out as a **measurement**, with real error bars. Not an estimate we
eyeballed off a curve."**

**"Two choices there deserve defending, briefly.**

**Why fit a sigmoid instead of just reading the fifty-percent point off the observed curve?
Because each trial is a **Bernoulli** outcome — logistic regression is the natural
probabilistic description of exactly that kind of data. And fitting the whole curve uses **all
one million observations** to locate the threshold, instead of leaning only on the handful of
bins that happen to sit near the crossing. Every trial, even at rho equals 0.05, is telling us
something about where the curve is.**

**And why bootstrap instead of a standard parametric interval? Because p_c is a **ratio of two
estimated parameters** — intercept over coefficient — and the sampling distribution of a ratio
**is not normal.** A parametric CI would rest on an assumption we know to be false. The
bootstrap assumes no distribution at all. It's not the fancier option; it's the only defensible
one."**

**[CORE]** **"The result: **p_c equals 0.279, plus or minus 0.002.** A holoparasite needs to
drain about **twenty-eight percent** of the host's vessels to collapse the network. Not fifty.
Not eighty. **Twenty-eight.**"**

## ▼ THE LOGIC

The full defence of both choices is in `METHODOLOGY.md` → *Justification of the Analytical
Choices*. The compressed version:

| Choice | Alternative | Why ours |
|---|---|---|
| Logistic regression | read 50% off the empirical curve | Bernoulli data → logistic is the natural model; uses all 10⁶ points; closed-form threshold with propagable uncertainty |
| Percentile bootstrap | parametric (Wald/delta) CI | p_c is a **ratio of estimates** → non-normal sampling distribution → parametric CI assumes something known-false |
| D as 30-seed distribution | single value from one network | one network = one draw; a distribution separates architecture from noise and enables the *t*-test vs. real leaves |

## ⚙ THE MECHANICS

- `sklearn` logistic regression on (ρ, outcome), 10⁶ rows.
- `p_c = −intercept / coefficient`.
- Percentile bootstrap over trials → 95% CI.
- Fit quality: McFadden's pseudo-R² (>0.4 = excellent), plus binned R² across the 50 density
  bins (observed vs. predicted collapse proportion).

## 🛡 IF ASKED

**"Your Hosmer–Lemeshow test — did it pass?"** *(a statistician will ask this)*
> "We report it, and we interpret it with stated caution. At n on the order of 10⁵–10⁶, H–L
> flags **trivially small** deviations as significant — that's a known property of the test at
> scale, not news about our model. So we treat the **effect-size** measures as the honest
> indicators of fit — McFadden's pseudo-R² and the binned R² — and report the chi-square for
> completeness. We'd rather show it and explain it than omit it."

**"How do you know the transition is real and not a finite-size artifact?"**
> "Two tests, and they're in the analysis plan precisely because this is the objection that
> matters. **Finite-size scaling:** we rerun the whole pipeline for networks from 6 to 10
> generations. A true phase transition **sharpens** toward a step function as the system grows
> — ours does. If the width hadn't shrunk, the threshold would be an artifact and we'd have to
> report that. **Critical exponent:** we regress log GCC-fraction against log distance-from-
> threshold in the scaling window. Recovering a clean power law confirms a continuous
> transition, and we compare the fitted exponent to the known mean-field and 2-D lattice
> universality classes."

---
---

# ⑥ THE PARAMETER SWEEP — K_h × D
### *Slide 9 · ~35 s · Output: the p_c vulnerability surface*

## ▶ SAY

**[CORE]** **"Step six. One threshold is a fact. A **surface** is a tool.**

**We sweep two axes. On the x-axis, **K_h** — sink strength — from 0.3 to 2.5: *how aggressive
is the parasite?* On the y-axis, **D** — fractal dimension — from about 1.35 to 1.48: *how well
built is the host?* We hold network size constant so D is the only thing moving on that axis.

**And then, in **every cell of that grid**, we re-run the entire pipeline independently — full
hydraulic solve, full Monte Carlo, full logistic fit. Not an interpolation. The whole thing,
every time."**

**[CORE]** **"What comes out is a **p_c surface** — a heatmap of vulnerability as a joint
function of parasite aggressiveness and host architecture. And it shows two things.**

**Increase K_h, and p_c **falls.** A greedier parasite collapses the host from fewer
attachment points. That one is expected — it's a sanity check, and passing it is how you know
the model isn't lying to you.**

**[CORE]** **Increase D, and p_c **rises.** Denser venation resists longer. **That one is the
deliverable.** Because it means **architecture is a defence** — and D is a trait you can
measure with a camera and a flatbed scanner. It is **breedable.** A breeder can screen for
it."**

**"One point on data integrity, and it matters. Some cells in that grid have **no threshold at
all** — a network so densely reticulated that a weak sink simply cannot collapse it, ever. We
report those cells as **undefined.** We don't drop them, and we don't interpolate them away.
Reporting an absence of collapse as an absence of *data* would hide the model's behaviour
exactly where that behaviour is most interesting: **the region where the host wins.**"**

## ▼ THE LOGIC

Step 6 is the step that converts a physics result into an agronomic one. Steps 1–5 answer *"is
there a threshold?"* Step 6 answers *"what moves it?"* — and only the second is actionable.

The ↑K_h → ↓p_c relation is the **falsification check**: it is the direction the physics
demands, so recovering it validates the machinery. The ↑D → ↑p_c relation is the **finding**:
it's the one that wasn't guaranteed, and it's the one a breeder can use.

## ⚙ THE MECHANICS

- 5 values of K_h × N values of D → full independent pipeline per cell.
- D varied by tuning reticulation density at **constant node count** (so D moves and size
  doesn't — otherwise the axes are confounded).
- Cells with no defined threshold → recorded as undefined, rendered as such on the heatmap.

## 🛡 IF ASKED

**"Can a breeder actually use this tomorrow?"** *(say NO — this is a trap and honesty wins it)*
> "No. And I want to be plain about that. What we have is a **framework** that produces a
> **falsifiable prediction** — that D and p_c are positively related. The next step is testing
> that on real leaves, which is our empirical phase. A panel forgives an uncalibrated model. It
> should not forgive one pretending to be calibrated."

---
---

# ⑦ THE TEMPORAL EXTENSION — *(beyond the six steps)*
### *Slide 10 · ~30 s · Output: the pre-symptomatic window*

## ▶ SAY

**[CORE]** **"One thing was still missing. Percolation gives us a **threshold**, but not a
**timetable.** It says how much loss collapses the host. It says nothing about **when** that
loss arrives. So we added time."**

**"We model the growth of haustorial load as a **logistic process**: d-rho d-t equals r times
rho times one minus rho. In words — the infestation accelerates while there's still healthy
tissue to take, and saturates as that tissue runs out. That has a closed-form solution: rho of
t equals one over one plus A e to the minus r t.**

**Why logistic and not something else? Because it's the **standard** model for the temporal
progression of a plant infestation. Disease progress curves in plant epidemiology are
conventionally fitted with exponential, monomolecular, logistic, or Gompertz models, and the
logistic is the canonical choice for a **polycyclic** process — one that compounds on itself.
That's a haustorial infestation exactly."**

**[CORE]** **"And now we read off two crossing times.**

**The curve crosses **p_c = 0.279** at time **t_c.** That is **functional collapse.** The
transport network is gone. **The plant still looks perfectly healthy.**

**The curve crosses the analytical fragmentation point, **f_c = 0.837**, at **t_wilt.** *That*
is when it visibly wilts.

**[CORE]** **The gap between them — about **ten time units** at r = 0.25 — is the
**pre-symptomatic window.** It is the period during which the crop is **already functionally
dead and still looks fine.** And it is precisely the window that visual scouting throws away."**

**"We also verified the closed-form solution against **numerical integration** of the same ODE
with an adaptive Runge–Kutta solver at a relative tolerance of 1e-9 — because a derivation you
haven't checked is a derivation you've assumed."**

**"And the limitation, stated up front: **r and rho-nought are illustrative, not calibrated.**
So **the existence and the shape of that window is our finding. Its duration in days is
not.**"**

## 🛡 IF ASKED

**"Ten time units — is that ten days? Ten weeks?"**
> "We don't know, and we won't say. r isn't calibrated to a real infestation, so the axis is
> in arbitrary time units. What the model establishes is that the window **exists** and is
> **wide** — the collapse point and the wilting point are nowhere near each other. Putting days
> on it requires a field growth rate, and that's future work. We'd rather report a real shape
> than a fake number."

---
---

# ⑧ EMPIRICAL VALIDATION — *(the phase genuinely outstanding)*
### *~25 s · Output: the model, tested against real leaves*

## ▶ SAY

**[CORE]** **"Finally — and this is the part that is genuinely still ahead of us — we test the
model against reality.**

**Five species: tomato, a legume, corn, mango, hibiscus. Chosen so two purposes are served at
once — several are **documented hosts** of the parasites we model, and together they **span the
venation gradient**, from the sparse parallel venation of a monocot like corn to the dense
reticulate mesh of a broad-leaved dicot. At least **five plants per species, three leaves
each**, so we get genuine standard errors instead of inferring them from one lucky specimen."**

**"Two measurements, two instruments.**

**Top-down **venation photographs** — backlit or flatbed-scanned — measured with the **identical
windowed box-counting algorithm** we ran on the synthetic networks. Identical is the operative
word: it's what makes the comparison like-for-like rather than apples-to-oranges.**

**And **transverse cross-sections** of stems and petioles, cut **at branch points** so a parent
vessel and both daughters appear in the same field of view. That gives us real vessel radii,
and from them the **empirical Murray's-law exponent** — which our model assumes to be exactly
three. So we test that assumption directly rather than inherit it."**

**[CORE]** **"And the single most important test in the study: a **Pearson correlation** between
each species' measured D and the p_c our model predicts for it. Because that is a **direct
empirical test of our central prediction** — that more densely veined hosts resist parasitic
collapse for longer. **If that correlation fails, our headline claim is wrong, and we will
report that.**"**

**"Worth noting on safety: our **priority** measurement — the venation photographs — needs
**backlighting and a camera.** No blades, no chemicals. The sharps hazard exists only in the
secondary cross-sectioning task."**

## ⚙ THE STATISTICAL PLAN

| Test | Question it answers |
|---|---|
| One-sample *t*-test, D_real vs. D_model (per species) | is the synthetic architecture a defensible stand-in for real venation? |
| One-way ANOVA of D across the 5 species | does the intended venation-density gradient actually exist in our specimens? |
| Log-log regression of daughter radii on parent; test H₀: exponent = 3 | is the Murray assumption we built on empirically true? |
| **Pearson r: D_measured × p_c_predicted** | **the central prediction — do denser hosts resist longer?** |

---
---

# 🛡 THE CROSS-CUTTING DEFENCES
### *Not tied to one step. Know all four cold.*

### ▸ "How do you know the whole engine isn't just producing plausible nonsense?"
*(The best question available. You have a genuinely excellent answer — do not fumble it.)*

> **"We validated it against closed-form theory. The **Molloy–Reed / Callaway criterion**
> predicts a network's fragmentation point **analytically**, straight from its degree
> distribution — one minus the reciprocal of kappa minus one, where kappa is the ratio of the
> second moment of the degree distribution to the first. It's a formula. It doesn't care what
> our code does. Our simulated fragmentation point **agrees with it.**
>
> That's the difference between a model that produces plausible numbers and one that produces
> **correct physics.** We didn't only ask whether our results looked reasonable. We asked
> whether they matched a number derived independently of our code — and they do."**

### ▸ "What are your limitations?"
*(Volunteer these. A panel that has to drag limitations out of you stops trusting everything
else you said.)*

> **"Five, openly.
> **One — the network is 2-D**; real vasculature is 3-D. Wason et al. note the functional
> consequences of 3-D intervessel connection are still imperfectly understood, and we inherit
> that.
> **Two — K_h is uncalibrated.** No published study reports a haustorial volumetric flux. We
> sweep it rather than fit it. That's a documented gap in the literature, not a shortcut in our
> method.
> **Three — root parasites are approximated.** Our network is the shoot with the root condensed
> to a single source node, so root attachment is modelled as an attack on the root-proximal
> backbone. A full root-system model is future work.
> **Four — the solver is steady-state.** No diurnal cycling, no embolism refilling.
> **Five — the ODE parameters are illustrative.** The window's existence is the finding. Its
> duration in days is not."**

### ▸ "How is any of this reproducible?"

> **"Two decisions, both structural rather than aspirational. **One frozen config module** —
> every parameter in the study lives in exactly one file, so no value can be silently
> redefined in one script and not another. And **every stochastic process draws from an
> explicitly seeded RNG.** So re-running any component reproduces our reported numbers
> **exactly**, not approximately. Anyone with the code can verify every number in the paper.
> The whole project is under Git, and all generated data and figures are committed — no result
> exists only in RAM or on one machine."**

### ▸ "Why is a computational design appropriate at all?"

> **"Because the question is unanswerable any other way. To find the threshold experimentally
> you would have to destroy **the same plant** at **every** level of damage, **thousands** of
> times, holding everything else constant. That's not difficult *in vivo* — it's **impossible**.
> It's trivial *in silico*. The impossibility of the experiment **is** the justification for the
> simulation."**

---
---

# 🎯 REHEARSAL NOTES FOR MEMBER C

- [ ] **Learn the bridge sentence in step ③ by heart.** *"A hydraulic event becomes a
      topological event."* If the panel remembers one sentence from your entire section, that
      is the one worth spending. It's the intellectual core of the study.
- [ ] **Do not rush ③.** It is a third of your time and it earns it. If you're over on the
      clock, cut from ② (compress box-counting to two sentences) or ⑥ — **never** from ③.
- [ ] **Own the limitations before you're asked.** Say "K_h is uncalibrated" *on your own
      slide*. A limitation you volunteered is methodology; the same limitation extracted under
      questioning is a weakness. Same fact, opposite outcome.
- [ ] **Never say "there are no studies."** Say **"we could find no study that…"** The absolute
      claim is unfalsifiable and one counterexample kills it. The hedged one is bulletproof and
      sounds *more* rigorous, not less.
- [ ] **Rehearse ③ standing up, alone, out loud, three times.** It's the hardest step to speak
      and the easiest to speed through.
- [ ] **Never oversell.** If asked whether a farmer could use this tomorrow: **no.** It's a
      framework producing a falsifiable prediction; the next step is testing it on real leaves.
      A panel forgives an uncalibrated model. It does **not** forgive one pretending otherwise.
