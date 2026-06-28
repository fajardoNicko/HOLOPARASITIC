# Every Concept in This Research — Explained Simply

A study guide. Each term gets a plain-language meaning and a note on **how it's
used in our project**. Read top to bottom — the ideas build on each other.

Running analogy: think of the plant's water system as a **city of roads** (or
household **plumbing**). Water = traffic; pipes = roads; the parasite = roadblocks.

---

## 1. The living things (biology)

**Parasite** — an organism that lives off another and harms it. 

**Holoparasite** — a "full" parasite that has basically *given up making its own
food* (little or no photosynthesis) and steals everything — water, sugars,
nutrients — from its host. (A *hemi*parasite only steals some.) *Cuscuta* is a
holoparasite. → This is why our model treats it as a pure **drain**.

**_Cuscuta campestris_ (dodder)** — a leafless, orange, spaghetti-like parasitic
vine that wraps around crops and feeds on them. Our reference parasite.

**Host** — the plant being fed on (the victim). In our model, the network we
attack.

**Haustorium** (plural **haustoria**) — the parasite's feeding peg. It drills
into the host's plumbing and acts like a **straw**. → In our model each
haustorium is a **leak** that pulls water out. The number of haustoria is the
density **ρ**.

**Vascular tissue / vasculature** — the plant's plumbing system: the network of
pipes that moves water and food around. → This *is* the network we study.

**Xylem** — the specific pipes that carry **water** (and minerals) upward from
roots to leaves. Made of dead, hollow cells joined end to end. → Our "pipes."

**Phloem** — the other plumbing, which carries **sugars**. (We focus on xylem/
water, but dodder taps both.)

**Vessel / conduit** — one individual pipe in the xylem. → One node/edge in our
network.

**Transpiration** — the "pull" at the top: water evaporates from leaf pores,
which sucks the whole water column upward like sipping a straw. → In our model
this is the boundary condition at the leaf/terminal nodes.

**Wilting / necrosis** — visible damage: drooping (wilting) and tissue death
(necrosis). These are **late** symptoms. → Our whole point: collapse happens
*before* you see these.

**Pre-symptomatic** — "before symptoms show." → The window we're trying to give
farmers.

---

## 2. How water moves (the physics of plant plumbing)

**Water potential (Ψ, "psi")** — a measure of how much water "wants" to move, like
**pressure**. Water flows from high Ψ to low Ψ. In plants it's usually *negative*
(the water is under suction). → The thing our flow solver calculates at every
junction.

**Tension / negative pressure** — plants pull water up under suction, not push it.
The water column is literally stretched. Too much stretch and it snaps (see
embolism).

**Cohesion–tension theory** — the accepted explanation of how water climbs a tall
tree: water molecules stick together (cohesion) and are pulled up by evaporation
(tension). The real science our pipes are based on.

**Sink** — anything that *removes* water/resource from the system (opposite of a
source). → The haustorium is a sink. The brief's "sink term" is the math for this.

**Flow rate (Q)** — how much water moves per second (the "traffic volume").

**Hydraulic resistance (R)** — how hard it is for water to push through a pipe.
Skinny pipe = high resistance; fat pipe = low resistance.

**Conductance** — the opposite of resistance (how *easily* water flows). Our
solver uses conductance.

**Viscosity (η, "eta")** — how "thick/sticky" the fluid is (honey vs water). A
constant in the resistance formula.

**Hagen–Poiseuille equation** — `R = 8ηL / (π r⁴)`. The recipe for a pipe's
resistance. The key part is **r⁴**: doubling a pipe's radius makes it carry
**16× more** water. So a few big pipes dominate the flow. → How we assign
resistance to every vessel.

**Hydraulic Ohm's law** — `Q = ΔΨ / R`. Same idea as electricity (current =
voltage / resistance), but for water: flow = pressure-difference / resistance. →
The basic flow rule.

**Murray's law** — `r³ = r₁³ + r₂³`. The rule for how pipes branch efficiently:
the parent pipe's radius cubed equals the sum of the children's radii cubed. Real
plants actually obey this. → How our generator sizes each branch.

**Kirchhoff's laws** — bookkeeping rules for networks: whatever flows *into* a
junction must flow *out* (nothing vanishes). → We write one equation per junction
and solve them all at once.

**Linear system (Ax = b)** — a big set of connected equations solved together. "A"
holds the pipe network, "b" holds the sources/sinks, "x" is the unknown pressures.
→ How we compute the whole flow field in one shot (efficiently, because most
pipes don't touch most others — see *sparse*).

**Steady state** — we solve for the settled, not-changing flow (after everything
balances out), rather than tracking every second.

**Boundary conditions** — the fixed "known" values at the edges of the problem:
water supply at the root, suction at the leaves. → They anchor the solution.

**Embolism / cavitation** — when a stretched water column **snaps** and an air
bubble forms, the pipe is blocked and stops working — permanently. → In our
coupled model, a pipe that gets sucked too hard **embolizes and is removed** from
the network. This is how the parasite's strength (K_h) actually breaks the
network.

---

## 3. Networks (the math of connections)

**Network / graph** — anything made of dots connected by lines. Roads + 
intersections, friends + friendships, pipes + junctions. → The core object of the
whole study.

**Node (vertex)** — a dot (a junction/vessel).

**Edge (link)** — a line connecting two dots (a pipe segment).

**Degree** — how many lines touch a dot. A junction where 4 pipes meet has degree
4. **Mean degree** = the average over the whole network (ours ≈ 3.6).

**Hub** — a dot with *many* connections (an important junction, a big main pipe).
→ Targeted attacks go after hubs first.

**Adjacency matrix** — a big table that records which dots connect to which. The
computer's way of storing the network. 

**Sparse matrix (CSR)** — a space-saving way to store that table when *most*
entries are "not connected" (which is true for pipe networks). → Lets us run a
million simulations quickly by skipping all the empty entries.

**Connected component** — a group of dots you can travel between. If a network is
in one piece, it's one component; break it and you get several.

**Giant Connected Component (GCC)** — the **biggest** surviving connected chunk.
→ Our health meter: if the GCC is large, water can still get around; if it
shatters into small pieces, the plant's transport has failed. We declare
**collapse when the GCC drops below 50%** of the original.

---

## 4. The big idea: percolation

**Percolation** — the study of *when a network falls apart* as you remove pieces.
(The name comes from water trickling through coffee grounds — does it find a path
all the way through?) → Our central framework.

**Percolation threshold (p_c)** — the **tipping point**: the fraction of pipes you
can knock out before the network suddenly shatters. Remove a little less → still
connected; a little more → broken into islands. → **The single most important
number in the project.** Ours ≈ **0.22** (22%).

**Phase transition** — a *sudden* change of state at a critical point, like water
freezing to ice at 0 °C. It's not gradual — it flips. → Network collapse is a
phase transition; p_c is the "freezing point."

**Critical point / tipping point** — same idea as p_c: the knife-edge where
behavior flips.

**Percolation scaling law** — `P∞ ~ (p − p_c)^β`. A formula describing *how* the
giant component grows/shrinks right near the threshold. "β" (beta) is a number
that captures the steepness. → It's why we expect a sharp S-curve, and it
justifies treating p_c as a real critical point.

**Random vs targeted attack** — two ways to knock out pipes:
- **Random** — knock out pipes at random (bad luck, generic stress).
- **Targeted** — knock out the **hubs** (big pipes) first. Networks are much more
fragile to targeted attack. → Real dodder targets big vessels, so the targeted
threshold (≈0.20) is lower than random (≈0.22).

---

## 5. Fractals & shape

**Fractal** — a shape that looks similar at every zoom level — branches made of
smaller branches made of smaller branches. Trees, rivers, lungs, blood vessels,
**leaf veins**. → Our network is built to be fractal-like.

**Self-similarity** — the "looks the same when you zoom in" property of fractals.

**Pre-fractal** — a fractal stopped after a *finite* number of steps (real things
can't branch forever). → Ours stops at 9 generations, so it's "pre-fractal."

**Fractal dimension (D)** — a number (here between 1 and 2) saying how thoroughly a
shape **fills space**. A straight line is 1; a filled-in sheet is 2. A sparse vein
network is ~1.3; a dense bushy one is closer to 2. → We use D to describe network
"bushiness," and we show tougher plants have higher D.

**Box-counting** — the practical way to *measure* D: cover the shape with a grid,
count how many boxes it touches, shrink the boxes, count again. How the count
grows as boxes shrink gives D. → Our `fractal.py` does exactly this.

**Reticulation / anastomosis (plural anastomoses)** — **cross-connections** that
turn a pure tree into a net with **loops**. Real leaf veins are reticulate (full
of loops), giving backup routes. → We add these on purpose; **without loops there
is no sharp tipping point**, so they're essential to the whole result. Our network
has 818 loops.

---

## 6. The simulation and getting numbers

**Model / simulation** — a computer stand-in for the real thing, so we can
experiment safely and cheaply.

**Monte Carlo** — running something **many times with randomness** and averaging,
to get a reliable answer (named after the casino). → We attack the network a
million times because each single attack is random; the average reveals the true
threshold.

**Trial** — one single run of the random experiment. (1,000,000 trials, 20,000 at
each of 50 density values.)

**Independent variable** — the knob we deliberately turn to see what happens. →
Ours is **K_h**, the parasite's sink strength.

**Density (ρ, "rho")** — the fraction of the network occupied/removed (0 to 1). →
Our x-axis: how much of the plant the parasite has tapped.

**K_h (haustorial sink strength)** — how hard each straw sucks. Bigger K_h = more
aggressive parasite. The formula: `Q_parasite = K_h × (Ψ_host − Ψ_parasite)`.

**Sigmoid (S-curve)** — an S-shaped curve: flat-low, then a steep rise, then
flat-high. → "Chance of collapse vs damage" makes a sigmoid. The steep middle is
the tipping point.

**Logistic regression** — a standard method that fits the best S-curve through
noisy yes/no data (collapsed: yes/no). → We use it to find p_c precisely as the
middle of the fitted S-curve.

**Inflection point** — the exact middle of the S-curve, where collapse chance =
50%. → That point's x-value **is p_c**.

**Confidence interval (CI)** — an honest "± error bar": the range we're 95% sure
the true value sits in. → Ours is tiny, [0.2205, 0.2230], because a million trials
pins it down tightly.

**Bootstrap** — a trick to get that error bar: re-sample your own data many times
and see how much the answer wobbles. → How we compute the CI.

**Reaction–diffusion** — a type of equation for how a substance spreads
(diffusion) while also being made/used up (reaction): `∂C/∂t = D∇²C + f(C) − σ`.
→ The *full* version of resource spread. We **simplified it away** (replaced it
with a simple sink term) to fit the timeline — honestly noted as Future Work.

---

## 7. Symbol cheat-sheet

| Symbol | Say it | Means |
|--------|--------|-------|
| Ψ | "psi" | water potential (water pressure/suction) |
| ρ | "rho" | density — fraction of network tapped/removed |
| η | "eta" | viscosity (fluid thickness) |
| K_h | "K-sub-h" | haustorial sink strength (parasite aggressiveness) |
| p_c | "p-sub-c" | percolation threshold (the tipping point) |
| D | "D" | fractal dimension (how space-filling the network is) |
| σ | "sigma" | the sink term (water removed by the parasite) |
| β | "beta" | critical exponent (steepness near the threshold) |
| Q | "Q" | flow rate (volume of water per second) |
| R | "R" | hydraulic resistance |
| GCC | — | Giant Connected Component (biggest surviving chunk) |

---

## The whole story in one breath

We model a plant's **water-pipe network** (xylem), built with the real branching
rule (**Murray's law**) and real loopiness (**reticulation**). A parasite
(*Cuscuta*) sticks in **straws** (**haustoria**) that **drain** water (a **sink**)
and pop pipes (**embolism**). We use **percolation theory** to find the **tipping
point** (**p_c**) where the network **shatters** (the **giant component**
collapses). We find it with a **million-run Monte Carlo** simulation and pin it
down with **logistic regression**. The punchline: the network breaks **early**
(~22%) and **invisibly** — before the plant looks sick — which is why **p_c** is
useful as an early-warning signal.
