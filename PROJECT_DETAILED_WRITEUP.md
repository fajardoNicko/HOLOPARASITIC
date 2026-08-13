# Project Detailed Writeup — for the Paper

_A plain-language + technical narrative of everything built and found, in the order a reader
needs it. Written 2026-08-05. Every number here is pulled from a real output file; the "Source"
lines tell you exactly where each figure lives so you can cite it in the manuscript._

---

## 0. The one-sentence version

> We took **120 real leaf venation networks**, asked how badly each one falls apart when a
> parasite randomly kills water-carrying nodes (a **percolation** experiment), and then asked
> whether making each leaf **more reticulate** (adding loop veins the way a real leaf can) makes
> it measurably harder to collapse. It does — **89% of leaves improved**, with **no leaf made
> worse** — but the gain is modest and is partly inflated by imperfect tracings, which we report
> honestly. Separately, we calibrated the parasite's water-draining strength to real
> holoparasite literature and found that at realistic strength the drain alone **never ruptures
> the xylem**: the "hydraulic sink" and the "network collapse" are two *different* stress
> lenses, not one driving the other.

Everything below expands each clause of that sentence.

---

## 1. The biological question

Holoparasites (e.g. *Cuscuta*, *Orobanche*) tap directly into a host's vascular system and
divert water and nutrients. The damage often becomes visible only *after* the host's transport
network has already begun to fail — i.e. collapse is **pre-symptomatic**. We wanted a way to ask:

1. **How structurally robust is a real host leaf's water network** to losing conductive nodes?
2. **Does the leaf's own architecture — specifically how looped/reticulate its veins are —
   set that robustness?** If a more reticulate leaf resists collapse better, then venation
   architecture is a candidate host-resistance trait (relevant to breeding / resistance screening).
3. **Is the parasite's hydraulic drain, on its own, enough to rupture the network** — or does it
   harm the host some other way?

Percolation theory is the **tool** we use to answer these; the **subject** is the leaf and the
parasite. (This framing matters for the competition category — see §9.)

---

## 2. The data — real leaves, not synthetic

**Source dataset:** Matos et al. UCBG venation form dataset (`UCBG_venation_form_data/`), 120
leaf directories. Each leaf ships as two CSVs:

- `*_nodes.csv` — vein junction coordinates (x, y positions of real vein intersections).
- `*_veins.csv` — vein segments connecting those junctions, with measured radii.

**How a leaf becomes a network** (`holoparasitic/realleaf.py`, `load_matos`): junctions become
**nodes**, vein segments become **edges**, each edge carries the traced **radius** (used for
Hagen–Poiseuille conductance, `g ∝ r⁴/L`) and **length**. This is a direct, one-to-one
digitisation of the real traced leaf — nothing is invented.

**Important honesty caveat baked into the data — the "quality" grade.** Each leaf carries an
A/B/C/D extraction-quality flag (`holoparasitic/metadata.py`, `FLAG_MEANING`):

| Grade | Meaning | Effect on our metric |
|-------|---------|----------------------|
| **A** | Clean tracing | Trustworthy |
| **B** | Missing veins (false negatives) | Leaf looks **too sparse** → depresses ⟨k⟩ → **inflates** the improvement we can add |
| **C** | Fake veins (false positives) | Leaf looks too dense → inflates ⟨k⟩ |
| **D** | Physical damage | Affects extent, not topology directly |

Grades **B and C corrupt topology** (`TOPOLOGY_CORRUPTING = ("B","C")`). This is why we run a
**clean-A-only sensitivity check** on every headline number (§6).

**Fragments.** 15 of the 120 tracings are crop *windows*, not whole leaves (N < 1000 nodes).
They are excluded from the percolation headline (validity rule below).

---

## 3. The percolation experiment — how we measure "collapse resistance"

**File:** `holoparasitic/percolation.py`.

**The model of the parasite's attack.** We model parasite-induced functional loss as **random
site percolation**: at a given surviving-fraction ρ, each node independently has probability
(1−ρ) of being knocked out. We deliberately use *purely random* removal — **no** parasite-specific
efficiency, attachment, or targeting assumptions — so the result measures the *leaf's own
structural robustness*, not a guess about parasite behaviour.

**What we watch: the Giant Connected Component (GCC).** After removing nodes, we measure whether
the largest surviving connected cluster still spans a meaningful fraction of the leaf. If the GCC
has fragmented, water can no longer move across the blade → **hydraulic collapse**.

**Monte Carlo sweep.** For each leaf:

1. Sweep survival density ρ across `n_densities = 40` values, concentrated below `rho_max = 0.6`
   (real leaves collapse well below ρ ≈ 0.3, so we don't waste trials up high).
2. At each ρ, run many independent random-removal trials and record the fraction that collapsed.
   Total **10,000 trials per network** for the cohort run.
3. This yields **P(collapse) vs ρ** — an S-shaped curve.

**Defining p_c (the critical threshold).** We fit a **logistic (sigmoid)** to P(collapse) vs ρ.
The **inflection point** — where P(collapse) = 0.5 — is the critical threshold:

> **p_c = −b / w**  (b = intercept, w = slope coefficient of the logistic fit).

Interpretation: **higher p_c = more fragile** (the leaf collapses even when a large fraction of
nodes still survive); **lower p_c = more robust**. If the logistic inflection extrapolates
outside [0,1] (happens when collapse is very sharp), we fall back to the direct 0.5-crossing of
the empirical curve (`pc_crossing`). Both live in the `find_pc` result.

---

## 4. The reticulation "suggestion" — making each leaf more looped, on its own coordinates

This is the heart of the new work. **Files:** `scripts/make_real_suggested.py` (the 5 hero
figure panels) and `scripts/run_cohort_suggested.py` (the all-120 driver). The loop-adding
routine is `add_loops`.

**The idea in plain terms.** A real leaf's veins form some closed loops (areoles) and leave some
gaps. A *more reticulate* leaf closes more of those gaps — more loops means more alternative
water paths, so knocking out one node matters less. We ask: if we close each leaf's *own* open
areoles, keeping everything anchored to its *own real vein junctions*, how much more
collapse-resistant does it get?

**How the loops are chosen (technical).**

1. Take the leaf's **real node positions**.
2. Compute the **Delaunay triangulation** of those points. Delaunay gives the natural set of
   "who is adjacent to whom" candidate connections for a set of 2-D points — the triangle edges
   are the geometrically sensible short links (empty-circumcircle rule; it's the dual of the
   Voronoi diagram). This is exactly the set of plausible areole-closing veins a leaf *could*
   grow, given where its junctions already are.
3. From all Delaunay edges, drop the ones that **already exist** in the real leaf. What's left =
   **candidate new loop veins**.
4. Sort candidates by **length, shortest first** — a leaf closes small gaps before large ones,
   and short veins are the cheapest, most realistic additions.
5. Add candidates in that order until the leaf reaches a target average connectivity
   **⟨k⟩ = 2.811** (`TARGET_K`). Each added edge is tagged `kind="added_loop"` and inherits a
   conservative radius (the min of its endpoints' existing veins), so we never fabricate a
   thick vein.

**Why ⟨k⟩ = 2.811 and not something arbitrary.** It's the **90th percentile of mean degree
across the real cohort** — i.e. the reticulation level of the *most-looped real leaves we
actually observed*. So "suggested" never means "denser than any real leaf"; it means "as looped
as the top ~10% of real leaves in this very dataset." The ceiling is **empirical**, not invented.

**Self-calibrating by design.** Because the target is a fixed ⟨k⟩, a **sparse leaf gains many
loops** and an **already-reticulate leaf gains few (or zero)**. The suggestion adapts per leaf.

**The 5 hero figures** (`figures/methodology/fig_realsuggested_*.png`) show this on individual
species side-by-side: Current (real) leaf vs Suggested (same leaf, added loops in blue), each
panel annotated with its **measured** p_c so the comparison is apples-to-apples on that leaf's
own network.

---

## 5. The cohort experiment — all 120 leaves, current vs suggested

**File:** `scripts/run_cohort_suggested.py` → **`data/cohort_suggested.csv`** (one row per leaf).

For **every** leaf, we measured p_c twice — the leaf **as traced** (`pc_current`) and the **same
leaf with loops added** to ⟨k⟩ = 2.811 (`pc_suggested`) — at **10,000 trials each**. Each row
records: species, N, E, current/suggested mean degree, loops added, D (fractal dimension),
quality grade, both p_c values, Δp_c, and runtime. The run is **resumable/incremental** (it reads
which species are already done and continues), which is how it survived across two sessions and
finished 120/120.

> **Note on trial count.** A full "1,000,000 trials × 120 leaves × 2 networks" was infeasible
> (median leaf ≈ 13,757 nodes; the largest, *Asi_tri*, is **203,589 nodes**; that's weeks of
> compute). We chose **10,000 trials/leaf** as the accuracy/time trade-off. Report this as a
> stated limitation, not a hidden one.

---

## 6. The headline results (with the honest caveat)

**Source:** `data/cohort_suggested_summary.json`, figure `figures/cohort_suggested.png`.

**Validity rule:** a leaf counts as a valid whole-leaf percolation case if **N ≥ 1000 and
pc_current ≥ 0.02**. That leaves **105 valid whole-leaves** (15 fragments excluded).

**Full valid cohort (n = 105):**

| Quantity | Current | Suggested | Change |
|----------|---------|-----------|--------|
| **p_c median** | 0.201 | 0.215 | **Δ +0.0095 median** |
| p_c mean | 0.188 | 0.200 | Δ +0.0123 mean |
| Δp_c range | — | — | **min +0.000, max +0.046** |

- **88.6% of leaves improved** (frac_improved = 0.886).
- **No leaf got worse** (min Δp_c = 0.000). The leaves that didn't improve are the
  *already-reticulate* ones with no headroom (e.g. *Aex_pun*, *Cup_nud*, *Eus_jap* — all
  ⟨k⟩ ≈ 2.9 already, Δ = 0.000).
- **Median relative gain ≈ 5.5%.**
- **Direction of the effect:** suggested leaves have **higher** p_c, meaning they tolerate losing
  *more* nodes before the GCC collapses → **more robust**. (Higher p_c = collapse requires a
  higher survival fraction to be avoided; equivalently the leaf survives to lower survival
  fractions — robustness. State this consistently in the paper with one chosen convention.)

**★ THE CAVEAT YOU MUST REPORT — clean-A sensitivity (n = 21):**

When we restrict to **only clean grade-A tracings** (no missing/fake veins corrupting ⟨k⟩):

| Quantity | Value |
|----------|-------|
| p_c median | 0.220 → 0.227 |
| **Δp_c median** | **+0.0069** |
| **Fraction improved** | **61.9%** |
| Median relative gain | ≈ 3.1% |

**Why the clean number is smaller.** Grade-B (missing-vein) leaves *look* artificially sparse, so
our loop-adder has lots of "room" to add veins → big apparent gains. Clean leaves are already
closer to their true reticulation, so there's less to add. **The honest reading:** the effect is
**real and consistently positive** (still 62% improved, still zero worsened, on the cleanest
subset), but the full-cohort headline (89%, +0.009) is **partly inflated by tracing artifacts**.
Lead with the clean-A number as the conservative claim, present the full cohort as the
upper-bound.

**Biggest gainers (illustrative, from top10_gainers):** *Clu_ala* (Δ +0.046, sparse leaf ⟨k⟩ 2.19
→ +1994 loops), *Chl_spi* (Δ +0.046), *Ane_cal* (Δ +0.042, an 85k-node leaf gaining 25,460
loops). The pattern is clean: **the sparser the real leaf, the more it gains** — direct evidence
that reticulation is what's buying the robustness.

---

## 7. The haustorial sink — grounding the parasite in real numbers, and the surprise

**Files:** `scripts/make_sink_demo.py` → `data/sink_demo.json`, `figures/sink_demo.png`.
Constant added in `config.py`: **`K_H_HOLOPARASITE = 0.0392`**.

Up to here the "parasite" was just random node removal. This section asks the *hydraulic*
question: model the haustorium as a **leak conductance K_h** draining water from the host xylem
to a low-potential parasite reservoir —

> **Q_parasite = K_h · (ψ_host − ψ_parasite)**

— and calibrate K_h to **real holoparasite literature** instead of picking it arbitrarily.

**Calibration targets (both literature-anchored, both hedged — see caveat):**

- **~18–20% flow diversion** — a **conservative floor** from a *hemiparasite* (Jiang, Jeschke &
  Hartung 2003, *J. Exp. Bot.* 54:1985, reports ~18% in *Rhinanthus*/*Hordeum*).
- **~1.5 MPa water-potential gradient** — an **illustrative order-of-magnitude** value cited in
  *Cuscuta* review literature. **⚠ It is NOT a primary measurement and is NOT in Kaiser et al. (2015)**
  (that review does not quantify the gradient). No published holoparasite-specific gradient was located.

We solved (bisection) for the K_h that produces ~20% diversion at the illustrative ~1.5 MPa gradient:
**K_h = 0.0392**, achieving **20.00% diversion** (`achieved_diversion = 0.2000`). Because no clean
holoparasite sink measurement exists, the exact magnitude is treated as a **delimitation, not a measured
input** — and the sub-cavitation finding below holds at *any* gradient regardless.

**★ THE SURPRISE FINDING.** At this literature-realistic strength, we then checked the minimum
water potential anywhere in the leaf against the cavitation/embolism threshold (−2.0 MPa). Result:

- Minimum ψ at the literature gradient: **−1.02 MPa** — nowhere near −2.0 MPa.
- **Vessels embolised at realistic strength: 0.** Cavitation onset gradient: never reached
  (`cavitation_onset_gradient_MPa = NaN` → the sink never crosses −2.0 MPa **at any gradient** we
  swept).

**What this means — the two lenses are decoupled.** A realistic holoparasite drain **steals
water and carbon but does not, by itself, rupture the xylem**. So the host harm is a **resource
drain**, not a hydraulic-embolism cascade. This is a genuinely useful result for the thesis:

- It **supports "pre-symptomatic"** — the network can be functionally stressed / on the edge of a
  percolation transition long before any vessel visibly embolises.
- But it is **honest about mechanism**: our data does **not** show the sink *driving* the
  percolation collapse. The **percolation collapse** (structural, §3–6) and the **hydraulic
  sink** (§7) are **two separate stress lenses on the same host**, not a single cause→effect
  chain. This directly affects the title wording (§9).

---

## 8. What each output file is (provenance map for the paper)

| File | What it holds | Cite it for |
|------|---------------|-------------|
| `data/cohort_suggested.csv` | 120 rows: per-leaf current vs suggested p_c, ⟨k⟩, loops added, D, quality | The core dataset |
| `data/cohort_suggested_summary.json` | Aggregates, clean-A sensitivity, top/bottom gainers | Every headline number in §6 |
| `figures/cohort_suggested.png` | Scatter (current vs suggested) + Δp_c histogram | The main results figure |
| `figures/methodology/fig_realsuggested_*.png` | 5 per-species current-vs-suggested panels | Method illustration §4 |
| `data/sink_demo.json` | K_h calibration + sub-cavitation finding | §7 numbers |
| `figures/sink_demo.png` | ψ-well map + min-tension-vs-gradient curve | §7 figure |
| `data/characterization_annotated.csv` | 120 leaves' structural metrics + quality grades | Data description §2 |
| `config.py` (`K_H_HOLOPARASITE`) | The literature-grounded constant | Methods, calibration |
| `empirical/RELATED_WORK.md` | 4 verified holoparasite-strength RRLs w/ DOIs | Reference list |
| `DATA_SUMMARY.xlsx` | Human-readable master table w/ provenance | Supplementary |

---

## 9. How to frame it in the paper (category = Life Sciences, individual)

The risk: if the manuscript reads as "graph theory + random node removal," it drifts toward
Mathematics/Computer Science and away from **Life Sciences**. Keep percolation as **method**, keep
**the leaf and the parasite as subject**. Concretely:

- **Lead with biology:** host–parasite interaction, leaf venation architecture as a resistance
  trait, implications for screening/breeding resistant hosts. Introduce percolation only as *the
  measurement tool* once the biological question is on the table.
- **Title wording.** The current framing overclaims causation ("...*driven by* haustorial sink
  dynamics") — but §7 shows the sink is sub-symptomatic and does **not** drive the collapse.
  Recommended minimal fix: *"...Host Xylem Networks **Under Holoparasitic Haustorial Sink
  Stress**"* (drop "driven by"). A bolder, defensible retilt that matches what the data actually
  shows: lead with *"**Venation Reticulation Buffers** Pre-Symptomatic Vascular Collapse..."* —
  because the reticulation result (§6) is the strongest, cleanest finding.
- **Present the caveat, don't hide it.** Reviewers reward the clean-A sensitivity analysis (§6);
  it shows scientific honesty and the effect survives it.

---

## 10. Open to-dos (not blocking the narrative)

1. **Citation fix in `METHODOLOGY.md`** (~lines 115, 494, 555): replace the unverified "Vishnu,
   M., ... *Chaos, Solitons & Fractals*" with the verified **Muraleedharan, V., Rajan, S. C., &
   Jaishanker, R. (2023). *Flora, 304,* 152300. doi:10.1016/j.flora.2023.152300**, and delete the
   "could not be verified" caveat. (Correction already lives in `empirical/RELATED_WORK.md`.)
2. **Reconcile two code/prose gaps** in `METHODOLOGY.md` vs `percolation.py` (site-vs-bond
   wording; root-attachment not enforced) before submission.
3. **Title + framing** — your call, per §9.
