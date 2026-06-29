# Holoparasite-Induced Vascular Percolation — Pipeline & Data Analysis

*Computational biophysics model of holoparasitic haustorial sink strength and the
Vascular Percolation Threshold p_c of a host plant. Focused on holoparasites
(*Cuscuta* stem, *Orobanche* root, *Pilostyles* systemic; calibrated on *Cuscuta
campestris*); hemiparasites (*Striga*, mistletoe) are kept as a comparison (§3.7).*

This document explains the full computational pipeline, catalogues the data it
produced, and analyses those results. All numbers below come from the production
run (`data/results.npz`, `data/summary.json`) on the reference network
(N = 1023 nodes, 1 000 000 Monte Carlo trials).

---

## Part 1 — The Pipeline

The model runs as a six-stage chain. Each stage's output is the next stage's
input; the shared object throughout is a `networkx.Graph` `G` following a frozen
schema (see `config.py`).

```
[1] Generate network ─► [2] Measure D ─► [3] Hydraulic solve ─┐
                                                              │
        ┌─────────────────────────────────────────────────────┘
        ▼
[4] Monte Carlo percolation ─► [5] Logistic regression → p_c ─► [6] Sweeps & figures
```

### Stage 1 — Synthetic vascular network (`network.py`)

A 2-D host xylem network is grown by recursive **Murray's-law** bifurcation.
Starting from a root vessel at the stem base, each vessel splits into two
children whose radii satisfy

> **Murray's law:**  r_parent³ = r_child1³ + r_child2³

so for a symmetric split each child radius is `r_parent / 2^(1/3)`. Vessel
lengths contract by a fixed `length_ratio` each generation, producing a
self-similar (pre-fractal) tree.

A pure tree, however, has **no redundant paths** — removing any internal vessel
disconnects its whole subtree, so it would collapse gradually with no sharp
threshold. Real vascular tissue (especially leaf venation) is *reticulate*, so
we add **anastomoses** (cross-links) joining spatially close vessels from
different branches. The number of cross-links is fixed at
`reticulation × (N−1)` and the shortest candidates are added first, which keeps
mean degree constant while creating the loops that give a genuine percolation
threshold.

**Reference network:** N = 1023 vessels, 3066 segments, **2044 anastomoses
(loops)**, 512 terminal (leaf) sites, mean degree 6.0.

### Stage 2 — Fractal dimension (`fractal.py`)

The drawn network is rasterised into a point cloud and **box-counting** is
applied: the number of occupied boxes `N(ε)` is counted across box sizes `ε`,
and the dimension is the slope of `log N(ε)` vs `log(1/ε)` over the genuine
scaling window. For the reference network **D = 1.43**, inside the measured
1.39–1.76 range of real leaf venation (Crisci et al., *Relbunium*; see
`VALIDATION.md`). Denser venation raises D — see Stage 6.

### Stage 3 — Hydraulic flow solver (`hydraulics.py`)

Steady-state xylem flow is solved as a sparse linear system from **Kirchhoff's
current law** on the conductance-weighted graph. Each vessel's hydraulic
resistance is

> **Hagen–Poiseuille:**  R = 8ηL / (πr⁴),  with flow  Q = ΔΨ / R

At every internal node, inflow = outflow + sinks, giving `A Ψ = b` (A = the
conductance Laplacian). Boundary conditions: the root is held at the source
potential, terminals at the leaf (transpirational) potential. A **haustorium**
is modelled exactly as the brief's leak equation,

> **Haustorial sink:**  Q_parasite = K_h (Ψ_host − Ψ_parasite)

i.e. a leak conductance `K_h` tying a host vessel to a more-negative parasite
reservoir. A vessel whose tension exceeds the cavitation limit
(Ψ < Ψ_cavitation) **embolises** and is removed — the physical event that links
sink strength K_h to topological collapse.

### Stage 4 — Monte Carlo percolation (`percolation.py`)

Because a finite network's transition is sigmoidal, p_c is estimated
statistically. For each of 50 haustorial-density values ρ ∈ [0, 1], many trials
are run; each trial removes a fraction ρ of vessels, measures the **Giant
Connected Component (GCC)**, and records a binary outcome:

> **collapse = 1 if GCC < 50 % of the original network, else 0**

Three removal modes are implemented:

| Mode | Mechanism | Used for |
|------|-----------|----------|
| `random` | each vessel removed with probability ρ (classic site percolation) | the headline 10⁶-trial sigmoid |
| `targeted` | high-degree vessels removed first (Albert–Barabási hub attack) | random-vs-targeted comparison |
| `hydraulic` | place ρ haustoria → solve flow → embolise over-tension vessels → remove | the K_h–D surface (K_h actually moves p_c) |

The hot loop runs entirely on a CSR sparse adjacency built once, never touching
NetworkX — this is what makes 10⁶ trials feasible.

### Stage 5 — Threshold estimation (logistic regression)

All `(ρ, outcome)` pairs are fed to a logistic regression. The fitted sigmoid's
inflection point — where P(collapse) = 0.5 — is **p_c = −intercept/coef**. A
percentile **bootstrap** over the trials gives a 95 % confidence interval.

### Stage 6 — Parameter sweeps (`sweep.py`) & figures (`viz.py`)

- **p_c vs D:** vary anastomosis (vein) density at constant N, *measure* D for
  each network, record p_c — denser venation → higher D and higher connectivity.
- **(K_h, D) surface:** for a grid of sink strengths × dimensions, run the
  coupled hydraulic mode to build the p_c heatmap.

Figures produced: `network.png`, `sigmoid.png` (hero), `pc_heatmap.png`,
`collapse_montage.png`, `collapse.gif`, `sigmoid_targeted.png`.

---

## Part 2 — Data Gathered

| File | Contents |
|------|----------|
| `data/summary.json` | headline scalars: network stats, D, p_c (random & targeted), CI, n_trials |
| `data/results.npz` | 13 arrays (hero curve, targeted curve, p_c-vs-D, K_h×D surface) |
| `data/csv/sigmoid.csv` | the 50-point hero curve: `rho, p_collapse, gcc_fraction` |
| `data/csv/pc_vs_D.csv` | `D, p_c` |
| `data/csv/pc_surface.csv` | p_c table, rows = D, columns = K_h |

**`results.npz` arrays:**

| Array | Shape | Meaning |
|-------|-------|---------|
| `rhos` | (50,) | haustorial-density axis ρ ∈ [0,1] |
| `p_collapse` | (50,) | P(collapse) at each ρ — the red sigmoid |
| `gcc_fraction` | (50,) | mean surviving GCC fraction — the green survival curve |
| `surface_D` | (4,) | fractal dimensions of the 4 swept networks |
| `surface_kh` | (5,) | sink strengths K_h |
| `surface_pc` | (4,5) | p_c at each (D, K_h) — the heatmap |
| `pcd_D`, `pcd_pc` | (4,) | p_c as a function of D (topological) |

**Headline numbers**

| Quantity | Value |
|----------|-------|
| Vascular percolation threshold (random) | **p_c = 0.279** |
| 95 % confidence interval (10⁶ trials) | **[0.2778, 0.2809]** |
| Threshold, backbone (betweenness) attack | **p_c = 0.177** |
| Threshold, degree attack | **p_c = 0.314** |
| Fractal dimension of reference network | D = 1.43 |
| Mean degree / loops | 6.0 / 2044 |

---

## Part 3 — Analysis

### 3.1 The threshold is sharp, and it is *low*

The collapse probability stays near zero while ρ < 0.12, then rises steeply:

| ρ | 0.12 | 0.16 | 0.20 | 0.24 | 0.27 | **0.28** |
|---|------|------|------|------|------|----------|
| P(collapse) | 0.002 | 0.021 | 0.078 | 0.22 | 0.378 | **≈0.50** |
| GCC fraction | 0.85 | 0.78 | 0.70 | 0.60 | 0.54 | **≈0.48** |

Two things matter here:

1. **It is a genuine phase transition, not a slow decline.** The logistic fit is
   steep and the 10⁶-trial confidence interval is only ±0.0015 wide (±0.6 %).
   This statistically validates the central claim that vascular failure is a
   *threshold phenomenon* with a well-defined critical point.

2. **The host collapses after losing only ~28 % of its vessels.** Intuition
   might expect a network to survive until roughly half its nodes are gone; this
   reticulate vascular topology fragments at well under a third. The system is
   far more fragile than its vessel count suggests.

### 3.2 The pre-symptomatic window (the core argument)

Macroscopic symptoms — wilting, necrosis — appear only when bulk water transport
has largely failed, i.e. when the GCC is small (ρ well beyond p_c). But the
*functional* point of no return is p_c = 0.28, where the GCC is still ~50 % and
the plant may look healthy.

The data therefore define an **actionable early-warning window**: between the
onset of measurable network disruption (ρ ≈ 0.12, GCC ≈ 85 %) and the percolation
threshold (ρ ≈ 0.28), a span of **~16 percentage points of haustorial density**.
Detection or intervention inside this window is pre-symptomatic; past p_c it is
too late. This is the quantitative basis for proposing p_c as a diagnostic
target rather than waiting for visible wilting.

### 3.3 Targeting the backbone collapses the host much sooner — and *degree* is the wrong target

There are two ways to "attack the important vessels," and they disagree — which is
itself a finding.

- **Backbone attack (betweenness centrality):** removing the stem and major veins
  — the low-degree vessels that carry the most flow paths — gives **p_c = 0.177 vs
  0.279 random**, collapse **~37 % sooner**. This matches Albert–Barabási (attack
  the structurally critical nodes) *and* the biology: *Cuscuta* preferentially
  invades the main stem and large bundles, i.e. exactly this backbone.
- **Degree attack:** removing the *highest-degree* vessels first gives
  **p_c = 0.314 > random** — *weaker* than random. In a hierarchical vascular
  network the high-degree nodes are the redundant reticulated periphery, not the
  critical backbone, so attacking them wastes effort.

The lesson: **degree is the wrong proxy for vulnerability in vasculature;
betweenness (the backbone) is right.** Because real *Cuscuta* hits the backbone,
the true threshold is nearer 0.18 — so the random estimate (0.28) is
**conservative**, strengthening the pre-symptomatic argument.

### 3.4 Host architecture sets baseline resistance (p_c vs D)

| D | 1.35 | 1.39 | 1.43 | 1.48 |
|---|------|------|------|------|
| p_c | 0.233 | 0.255 | 0.283 | 0.317 |

p_c rises monotonically with fractal dimension, at roughly **Δp_c/ΔD ≈ 0.65 per
unit D**. Denser, higher-dimensional venation — more anastomoses, more redundant
pathways — requires substantially more haustorial load before it fragments. A
host with D = 1.48 tolerates ~36 % more disruption than one with D = 1.35 before
collapsing. This identifies **vein density / network redundancy as a heritable
resistance trait**, a concrete target for crop selection or breeding.

### 3.5 The (K_h, D) surface: parasite strength × host architecture

`pc_surface.csv` (rows = D, columns = K_h):

| D \ K_h | 0.30 | 0.60 | 1.00 | 1.50 | 2.50 |
|---------|------|------|------|------|------|
| 1.35 | 0.375 | 0.241 | 0.183 | 0.159 | 0.138 |
| 1.39 | 0.442 | 0.279 | 0.211 | 0.181 | 0.161 |
| 1.43 | 0.467 | 0.309 | 0.240 | 0.210 | 0.193 |
| 1.48 | 0.643 | 0.353 | 0.296 | 0.267 | 0.247 |

Three patterns:

1. **p_c falls steeply with sink strength, then saturates.** Going from K_h = 0.3
   to 0.6 roughly *halves* p_c at every D (e.g. 0.643 → 0.353 at D = 1.48); past
   K_h ≈ 1.0 further increases barely move it. Once each haustorium is strong
   enough to embolise its local neighbourhood, additional strength adds little —
   the damage per haustorium is already near-maximal.

2. **p_c rises with D at every K_h**, consistent with §3.4 — host robustness
   helps regardless of parasite aggressiveness.

3. **The two factors compound.** The most resistant corner (weak sink, dense
   network: K_h = 0.3, D = 1.48) has p_c = 0.643; the most vulnerable corner
   (strong sink, sparse network: K_h = 2.5, D = 1.35) has p_c = 0.138 — a **4.7×
   range**. Vulnerability is jointly determined, so neither parasite strength nor
   host architecture alone predicts outcome.

### 3.6 The physical (embolism) model predicts *earlier* collapse than random removal

A key cross-check: at moderate-to-strong sinks the coupled hydraulic thresholds
fall *below* the purely topological random value (0.28). For example at D ≈ 1.43,
K_h = 1.0 gives p_c = 0.240 vs 0.283 topological. The reason is mechanistic — a
haustorium does not merely disable the vessel it taps; by drawing down local
water potential it **embolises neighbouring vessels too**, so each haustorium
removes more than one node-equivalent and the cascade amplifies damage. Only at
weak sinks (K_h ≤ 0.6) is the hydraulic threshold *higher* than random, because
weak sinks rarely trigger cavitation and many are needed. The crossover near
K_h ≈ 0.7 is itself a model prediction. Net effect: incorporating the physics
makes the host look **more**, not less, fragile.

### 3.7 Generality: the framework ranks holoparasite types (with a hemiparasite comparison)

The model is **parasite-agnostic** — a parasite is just an *attachment pattern*
(where it taps) and a per-haustorium *efficiency* (how completely it disables a
vessel: 1.0 for a full holoparasite, ~0.6 for a partly-photosynthetic
hemiparasite). Because the model distinguishes parasites by **attachment × mode**,
two species with the same profile collapse the host identically; the holoparasite
set below therefore spans the **three distinct attachment geometries** (stem, root,
systemic) rather than listing same-profile species (e.g. *Cassytha* would duplicate
*Cuscuta*; *Phelipanche* would duplicate *Orobanche*). The two hemiparasites are
kept as a **comparison only**. Running them on the *same* host network
(`run_parasites.py`):

| Parasite | Type | Attaches | p_c | 95% CI |
|---|---|---|---|---|
| *Orobanche* (broomrape) | **holoparasite** | root | **0.155** | [0.153, 0.157] |
| *Cuscuta* (dodder) | **holoparasite** | stem | **0.175** | [0.173, 0.177] |
| *Striga* (witchweed) | hemiparasite *(comparison)* | root | **0.263** | [0.260, 0.265] |
| *Pilostyles* (endophyte) | **holoparasite** | systemic | **0.277** | [0.275, 0.280] |
| Mistletoe | hemiparasite *(comparison)* | stem | **0.425** | [0.420, 0.430] |

**The ranking is statistically significant:** every adjacent pair has
non-overlapping 95% bootstrap confidence intervals, so the ordering is not noise.
Three effects emerge: (1) **among holoparasites, *attachment site* sets the
threat** — root (*Orobanche* 0.155) > stem (*Cuscuta* 0.175) > systemic/diffuse
(*Pilostyles* 0.277); (2) **at equal attachment, full beats partial** — holo
collapses the host sooner than hemi (stem: *Cuscuta* 0.175 vs mistletoe 0.425;
root: *Orobanche* 0.155 vs *Striga* 0.263); (3) **the two axes can cross** — the
targeted root *hemi*parasite *Striga* (0.263) outranks the diffuse *holo*parasite
*Pilostyles* (0.277), i.e. *where* a parasite attacks can outweigh *how completely*
it feeds. Reassuringly, *Cuscuta* here (0.175) reproduces the betweenness-backbone
result of §3.3 (0.177), and *Pilostyles* (random attachment, 0.277) reproduces the
random-attack p_c of §3.2 (0.279) — two internal consistency checks. This answers
*"only Cuscuta?"*: **no** — the same framework predicts and *ranks* multiple
holoparasites and places them against hemiparasite weeds that threaten tens of
millions of farmers.

---

## Part 4 — Significance

- **Diagnostic reframing.** Current detection (drone imagery, visual scouting)
  registers wilting — which occurs *after* p_c is crossed. This model defines the
  threshold that precedes symptoms, establishing a pre-symptomatic target.
- **Breeding insight.** Network redundancy (vein density, fractal dimension) is a
  quantitative resistance trait (§3.4) — higher-D cultivars tolerate more load.
- **Generality.** The framework is parasite-agnostic; *Orobanche* and *Striga*
  (which threatens ~50 M farmers in sub-Saharan Africa) fit the same model with
  re-parameterised K_h and host D.

---

## Part 5 — Limitations

- **Synthetic, 2-D networks** — not yet calibrated to imaged crop venation.
- **Normalised units** — qualitative trends, not absolute MPa/flow predictions.
- **Single-shot embolism** — one solve per trial; a full iterative embolism
  cascade is future work.
- **Analytical sink term** — the full reaction–diffusion solver
  (∂C/∂t = D∇²C + f(C) − σ) was de-scoped to σ(x,t) = K_h·n(t); listed in Future
  Work.
- **No experimental validation** — wet-lab confirmation (dye-tracing, real
  haustorial conductance, imaged D) is the recommended next step.

---

## Reproduce

```powershell
C:\laragon\bin\python\python-3.13\python.exe -m pip install -r requirements.txt
C:\laragon\bin\python\python-3.13\python.exe scripts\run_full.py          # full 1e6-trial run
C:\laragon\bin\python\python-3.13\python.exe scripts\export_csv.py        # CSV tables
C:\laragon\bin\python\python-3.13\python.exe scripts\show_npz.py data\results.npz
```

Every random draw flows through `config.new_rng(seed)`; identical config → identical
results.
