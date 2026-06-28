# The Project in Plain Language

A simple, no-jargon companion to `ANALYSIS.md`. If `ANALYSIS.md` is the
technical version, this is the "explain it to a friend" version.

---

## The big idea (one paragraph)

Plants move water through a network of tiny pipes, like a system of roads.
**Dodder** (*Cuscuta*) is a parasite vine that latches onto a host plant and
drinks its water through little straws called **haustoria**. We wanted to know:
**how much draining can the plant take before its water network breaks apart?**
We built a computer model of the pipe network, simulated the parasite attacking
it a million times, and found the exact breaking point. The surprising answer:
the plant breaks *much earlier than it looks like it should* — and by the time it
looks sick, it's already too late.

---

## The road-network analogy

Think of the plant's water pipes as a **city road map**:

- **Roads** = xylem vessels (the pipes that carry water).
- **Intersections** = junctions where pipes meet.
- **The parasite** = roadblocks. Each haustorium is like closing a road.
- **"The city still works"** = you can still drive from anywhere to anywhere —
  one big connected road network.
- **"The city breaks"** = so many roads are closed that the map splits into
  **isolated islands** that can't reach each other. Water (traffic) can no longer
  get across. We call this breaking point **p_c**.

The whole project is: *how many roadblocks does it take to break the city?*

---

## What we actually built (the 6 steps)

1. **Build the pipe network.** Grow a realistic, tree-like branching network of
   pipes — thick trunk, thinner and thinner branches — and add some
   cross-connections (loops), because real leaves have them. Loops matter: a
   network with no loops falls apart slowly and boringly; a network with loops
   holds together... until it suddenly doesn't. That "suddenly" is the whole
   point.

2. **Measure how "bushy" it is.** A single number, the **fractal dimension D**,
   describes how densely the network fills space. A sparse network has low D; a
   dense, leafy one has high D.

3. **Simulate the water flow.** Solve the physics of water moving through the
   pipes, and add the parasite's straws as "leaks" that pull water out. If a pipe
   gets sucked too hard, it fails (an air bubble forms — "embolism") and drops
   out of the network.

4. **Attack it, over and over.** Knock out pipes a little at a time and check:
   *is the network still one connected piece, or has it shattered into islands?*
   Do this a million times to average out the randomness.

5. **Find the breaking point.** Plot "chance the network has shattered" against
   "how much was knocked out." It makes an S-shaped curve. The point where there's
   a 50/50 chance of collapse is **p_c** — the breaking point.

6. **Change the conditions.** Repeat for bushier vs sparser networks, and for
   gentle vs aggressive parasites, to see what makes a plant tougher or weaker.

---

## What we found (the results, in plain words)

**1. The plant breaks early — after losing only about 22% of its pipes.**
You might guess a network survives until half its roads are closed. Not this one.
At just **22% knocked out (p_c = 0.22)**, the water network shatters into islands.
Plants are more fragile than they look.

**2. By the time it looks sick, it's already too late — but there's a warning
window.** A plant only *looks* wilted once water transport has mostly failed —
well past the breaking point. At the actual breaking point, the plant still looks
fine. But our data show a window beforehand (between about 10% and 22% damage)
where the network is quietly starting to come apart. **Catch it in that window
and you can act before the damage is permanent.** That's the headline of the whole
project: don't wait for wilting — there's an earlier, invisible danger line.

**3. Smart attacks break it faster.** If the parasite goes after the *big main
pipes* instead of random ones, the plant breaks at **20% instead of 22%**. Real
dodder *does* target the big vessels — so in reality, the plant probably breaks
even sooner than our main number says. (This makes our warning *more* urgent, not
less.)

**4. Bushier plants are tougher.** Networks with more loops and higher fractal
dimension D can take more damage before breaking (from ~19% up to ~32% as D goes
from 1.26 to 1.49). More interconnections = more backup routes. **This suggests
you could breed crops with denser veins to resist dodder.**

**5. A stronger parasite breaks it faster — but only up to a point.** A more
aggressive sucker drops the breaking point steeply at first, then the effect
levels off. Once each straw is strong enough to kill the pipes around it, making
it stronger doesn't add much.

**The combined picture:** how doomed a plant is depends on *both* the parasite's
strength *and* the plant's network design. A tough plant facing a weak parasite
survives until 64% damage; a fragile plant facing a strong one breaks at just 9%.

---

## Why anyone should care

- **Better detection.** Today, farmers and drones spot dodder by looking for
  wilting — which happens *after* the plant has crossed the point of no return.
  Our model points to an earlier, measurable danger line.
- **Better crops.** "Denser veins = tougher" is a concrete target for breeding
  resistant varieties.
- **Bigger than dodder.** The same model works for other parasitic weeds like
  *Striga*, which threatens tens of millions of farmers in Africa.

---

## The honest fine print

This is a **computer model**, not a real plant experiment yet. The networks are
synthetic and simplified (2-D, idealized). It establishes the *framework and the
prediction*; the next step is confirming it with real plants in a lab. That's a
normal and honest way to do computational science — build the theory first, then
test it.
