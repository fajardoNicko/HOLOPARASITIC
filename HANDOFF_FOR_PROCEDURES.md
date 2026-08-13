# Handoff — Methods & Procedures (sessions of 2026-07-24 and 2026-07-25)

**Purpose of this document.** This is a complete, chronological record of what
was done across two working sessions, written so it can be turned into the
**Procedures / Methodology** section of the paper. It is organised by what was
done, in what order, with which parameters, and why. Numbers here are the actual
values produced by the code and are reproducible from the named scripts.

**Study title.** *Percolation Analysis of Pre-Symptomatic Giant-Component
Collapse in Host Xylem Networks Driven by Holoparasitic Haustorial Sink
Dynamics.*

**Central question.** Does the collapse of the host leaf's water-transport
network (its giant connected component) depend on network **connectivity**
(mean degree ⟨k⟩) or on network **fractal dimension** (D)? And how do
holoparasitic haustorial sinks drive that collapse?

---

## 0. Overall design — a two-phase hybrid

The study uses two complementary sources of vascular networks, analysed by one
identical physics/percolation engine so results are directly comparable:

- **Phase 1 — Real leaves.** Extracted venation networks from Matos et al.
  (2024) are given the hydraulic + percolation physics. These provide biological
  realism and the primary empirical test.
- **Phase 2 — Synthetic networks.** A generator produces networks whose
  branching geometry is calibrated to the real leaves, but whose connectivity
  (⟨k⟩) and fractal dimension (D) can be varied **independently and on demand**.
  This provides causal control that real leaves cannot: you can change one
  property while holding the other fixed.

The logic: real leaves let you *observe* which property predicts collapse;
synthetic networks let you *intervene* to show the effect is causal.

---

## 1. Data source (Phase 1 input)

- **Dataset.** Matos et al. (2024), University of California Botanical Garden
  venation forms, Dryad `doi:10.5061/dryad.1g1jwsv36` (licence ODC-BY). 120
  species, one directory each.
- **Per leaf, two primary tables are used:**
  - `<leaf>_nodes.csv` — node ID, type, pixel coordinates, calibration
    (mm/pixel), degree, and the authors' own per-junction geometry
    (`node_D0/D1/D2` parent+daughter diameters, `node_Symmetry`,
    `theta_D1_D0/theta_D2_D0/theta_D2_D1` branching angles).
  - `<leaf>_veins.csv` — edge endpoints, vein `Type` (EL loop / ET tree),
    `Width` (mm), `Length` (mm), and the authors' own `Resistance_2`,
    `Resistance_4`.
- The archive also ships `_summary.csv` (~160 precomputed whole-leaf metrics
  incl. `Valpha` meshedness index), `_HLD.csv` (hierarchical loop decomposition,
  Horton–Strahler order), and `_areoles.csv` (per-areole geometry). These were
  used for cross-checks (Section 5).
- **A metadata table** `UCBG_venation_form_metadata.csv` carries an
  extraction-quality grade per leaf (see Section 3.3).

**Data properties that constrained the method (all discovered, none stated in
the archive):**
- 100 of 120 files are **cropped windows** of leaves, not whole leaves.
- **No petiole nodes exist** in any file (`node_Type` is 'E' throughout), so the
  water-source node had to be chosen on hydraulic grounds, not anatomically.
- Vein counts span **4.5 orders of magnitude** (12 to 396,260 veins; median
  ~16,900).

---

## 2. Building a solvable network from each real leaf

Module: `holoparasitic/realleaf.py`, function `load_matos()`.

Each leaf's two CSVs are read into a NetworkX graph carrying the same attribute
contract as the synthetic generator, so downstream code treats real and
synthetic networks identically:

- **Nodes:** position (mm, via the calibration factor), kind
  (root/terminal/internal), BFS generation from the root.
- **Edges:** radius = Width/2, length, kind ('anastomosis' for Matos type EL,
  'axial' otherwise), and a conductance.
- **Conductance** is Hagen–Poiseuille: `g ∝ r⁴ / L`, with the global constant
  8η/π omitted because it cancels in the potential solve. Radii are normalised by
  the maximum radius so the sparse linear system stays well-conditioned across
  the ~100× caliber range.
- **Parallel veins** between the same node pair collapse to the widest (it
  dominates r⁴ conductance); self-loops and non-positive-width/length edges are
  dropped.

**Boundary conditions (the one modelling choice a real mesh forces):**
- **Root (water source, ψ = 0).** Rule hierarchy, recorded per run in
  `G.graph['root_rule']`: explicit override → petiole node if present → otherwise
  the **endpoint of the widest vein** (the hydraulically most proximal point of
  the cropped window) → geometric fallback. Because no leaf has a petiole, the
  **widest-vein rule** is the operative one.
- **Terminals (transpiration sites, ψ = ψ_leaf).** All free vein endings
  (degree-1 nodes).

**Two silent data bugs found and fixed (both would have corrupted results):**
1. Root selection previously fell through to a geometric guess that placed the
   water source on a marginal 0.0095 mm vein instead of the 0.28 mm main vein;
   fixed with the widest-vein rule.
2. One species (`Bei_tar`) was silently dropped because its two files use a
   hyphen vs underscore in the stem; pairing is now done per-directory
   (`find_leaf_pairs`), giving all 120 pairs.

---

## 3. Screening leaves into the analysis cohort

Not every extracted window can support a meaningful percolation threshold. Three
independent, **structural** screens were applied, each decided *before* any p_c
was computed (so inclusion cannot be reverse-engineered from the result). The
final cohort is assembled by `scripts/build_cohort.py` → `data/cohort.csv`.

### 3.1 Characterization (the SOP-1 measurement)
Module `holoparasitic/characterize.py`, driver `scripts/run_characterize.py`.
Every one of the 120 leaves was profiled (topology, cycle rank, loop fraction,
hydraulic diameter, effective conductance, fractal dimension D, and branching
geometry). Runtime ~27 min; output `data/characterization.csv` +
`data/species/<spp>.json`.

Cohort-wide medians (n = 100, see below): D = 1.69 (range 1.26–1.91), ⟨k⟩ = 2.52
(2.15–2.99), loop fraction = 0.78, branch angle = 55°, Murray exponent = 2.0,
daughter symmetry = 0.68.

### 3.2 Cropping-artifact screen (size + shape)
Module `holoparasitic/boundary.py`, driver `scripts/run_boundary_check.py`.
Veins severed by a crop window's edge terminate in spurious degree-1 nodes that
artificially depress mean degree (the response-relevant variable). Each leaf's
degree-1 nodes were classified as genuine vein endings vs window cut-ends by
proximity to the bounding box, and mean degree was recomputed with cut-ends
stripped. The artifact scales with size exactly as a perimeter-to-area mechanism
predicts (Spearman cut-end fraction vs log-edges ρ = −0.35). A pure "smallest
size above which all leaves pass" rule was rejected because a single thin sliver
(`Par_tor`, 8,490 veins but 98% cut-ends) inflated it; the correct criterion is
a **combined size floor + direct cut-end gate**.

### 3.3 Extraction-quality (tested, deliberately NOT used to exclude)
Module `holoparasitic/metadata.py`, driver `scripts/run_quality_check.py`.
The metadata flags A (clean, 34), B (missing minor veins, 46), C (fabricated
minor veins, 15), D (physical damage, 57). Whether these bias mean degree was
tested rather than assumed. Clean-A leaves differ from flagged leaves on ⟨k⟩
(2.69 vs 2.48, p = 0.002), and the difference survives size control (OLS with
log-edges covariate, β = −0.11, p = 0.02). **However**, the mechanism test
overturns exclusion: if extraction error acted mechanically on connectivity,
B (missing) and C (fabricated) would shift ⟨k⟩ in **opposite** directions; they
do not (B-only 2.47, C-only 2.50, both below clean 2.69, same direction). The
grade therefore tracks **leaf identity** (clean-A is a biased subsample of
denser venation that was easier to extract), not vein-count error. Excluding B/C
would bias the sample rather than clean it. **Decision:** quality flags are
recorded but do not gate inclusion; the core analysis is instead repeated on
clean-A only as a **sensitivity check**.

### 3.4 The final inclusion criterion
A leaf enters the cohort iff **all** hold:
- n_edges ≥ 2,000 (finite-size resolvability; below this the crop artifact
  begins to dominate ⟨k⟩),
- n_cycles ≥ 1 (a network with no loops has no percolation transition),
- cut-end fraction ≤ 0.05 (cropping artifact negligible),
- |mean-degree shift when cut-ends stripped| ≤ 0.05.

**Result: 100 of 120 leaves included, 20 excluded**, each exclusion logged with
an explicit reason. Worst residual cropping distortion in the cohort is
|Δ⟨k⟩| = 0.008 (~1% of the ⟨k⟩ range).

---

## 4. The physics / percolation engine (shared by both phases)

Module `holoparasitic/percolation.py` (with `holoparasitic/hydraulics.py`).

- **Hydraulic solve.** The network is a conductance (Laplacian) linear system
  L·Ψ = b solved for nodal water potentials; this is mathematically the
  finite-element assembly for 1-D Hagen–Poiseuille elements. Whole-leaf effective
  conductance (a model analogue of measured K_leaf) is the flow entering the root
  per unit potential drop.
- **Percolation (Monte Carlo).** For each of `n_densities` removal fractions
  ρ ∈ [0, ρ_max], many trials remove nodes and record whether the giant connected
  component (GCC) fell below `collapse_fraction`×N (default 0.5). p_c is the ρ at
  which P(collapse) = 0.5, estimated by logistic regression (inflection =
  −intercept/coefficient), with a robust linear-interpolation crossing as
  fallback.
- **Attack modes.** `random` (classic site percolation — the primary threshold),
  `targeted` (degree- or betweenness-weighted removal), and `hydraulic` (place
  haustoria, solve flow, embolise vessels past the cavitation tension, remove
  them, then measure the GCC — this is where the haustorial sink strength K_h
  moves p_c).
- The hot loop runs on a CSR adjacency built once; it never touches NetworkX.

**One method addition made this session:** a `rho_max` bound on the removal
sweep. Every real leaf collapses below ρ ≈ 0.3, so sweeping to 1.0 wastes ~70%
of density points where P(collapse) is already 1. Setting ρ_max = 0.6
concentrates the same trial budget in the informative range and sharpens the
per-leaf estimate; it is backward-compatible (default 1.0, so existing synthetic
results are unchanged) and does not affect p_c as long as the crossing lies
inside [0, ρ_max].

---

## 5. Validation of the implementation (external, against the source data)

These are the strongest defence that the physics is implemented correctly,
because they check against numbers the authors computed and our loader never
used.

### 5.1 Hydraulic resistance — exact match
Driver `scripts/run_validate_hydraulics.py`. Our independently-computed vein
resistance (L / r⁴) was compared vein-by-vein against the dataset's own
`Resistance_4` column. Result: **119/119 leaves exact, 5,668,467 veins,
Pearson r(log,log) = 1.000000, worst coefficient-of-variation of the ratio
= 1.1×10⁻⁷.** A control confirms correlation alone is insufficient: the *wrong*
exponent (r²) still correlates at r = 0.95, so the discriminating statistic is
the CV of the ratio, which is ~0 only for the correct r⁴ law. (One leaf,
`Equ_tel`, a horsetail with < 50 veins and no reticulate venation, was skipped —
a biological, not a data, exclusion.)

### 5.2 Branching geometry — two independent routes agree
Module `holoparasitic/calibrate.py` measures branching geometry two ways: from
the reconstructed graph (`measure_from_graph`) and from Matos' own curated
per-junction columns (`measure_from_matos_nodes`). They agree: branch angle
51–56°, daughter symmetry 0.73–0.80, Murray exponent 2.2–2.5. **Both routes
agree the Murray exponent is well below the classical value of 3.** Two reported
caveats: the per-junction Murray solve is bracket-sensitive (median moves 2.55→
2.78 as the root-finding window widens) with a broad IQR, and the branching-angle
columns are pixel-quantised.

### 5.3 Meshedness cross-check
Our alpha (meshedness) index matches the dataset's own `Valpha` to five decimals
(e.g. 0.0789 vs 0.0790), an end-to-end check on the loader.

---

## 6. Phase 1 result — what predicts collapse in real leaves

Driver `scripts/run_cohort_percolation.py` → `data/cohort_pc.csv` +
`data/cohort_pc_analysis.json`.

The site-percolation threshold p_c (random attack, primary; degree-targeted,
secondary) was estimated for all 100 cohort leaves (2,400 trials/leaf/mode,
40 densities × 60 trials, ρ_max = 0.6; runtime ~53 min). p_c was then regressed
on ⟨k⟩ and D.

**Key finding: on real leaves ⟨k⟩ and D are nearly independent** (Pearson
r = +0.15, VIF = 1.02), so their effects separate cleanly. **Both are
significant independent predictors of p_c:**
- partial r(p_c, ⟨k⟩ | D) = **+0.60** (p = 6×10⁻¹¹)
- partial r(p_c, D | ⟨k⟩) = **+0.50** (p = 1×10⁻⁷)

Mean degree is somewhat the stronger of the two (Spearman 0.73 vs 0.50).

**This revises a preliminary result.** An earlier pilot on 10 small leaves had
found D irrelevant (r = 0.13, ns); that was underpowered with a truncated D
range. With n = 100 and the full D range (1.26–1.91), D is a genuine independent
driver of collapse robustness.

Reported caveats: (i) the real ⟨k⟩ range is narrow (2.15–2.99), which is why the
synthetic phase is still needed to vary ⟨k⟩ over a wide causal range;
(ii) loop_fraction ≈ ⟨k⟩ (r = 0.97), i.e. the same axis, not a third predictor;
(iii) the clean-A sensitivity subset (n = 16) keeps ⟨k⟩ strong (r = 0.77) but
loses significance on D (restricted range / low power — the full-cohort partial
is the trustworthy test); (iv) degree-targeted p_c < random in 100% of leaves
(mean −0.029). Figure: `figures/cohort_pc_predictors.png`.

---

## 7. Phase 2 — the calibrated synthetic generator

Module `holoparasitic/network.py`; calibration in `holoparasitic/calibrate.py`;
verification `scripts/run_calibration.py` → `data/calibration.json` +
`figures/calibration_grid.png`.

The generator grows a branching (Murray) tree and then adds reticulation
(loops). It was calibrated to the real cohort so its networks branch like real
leaves while ⟨k⟩ and D remain controllable.

### 7.1 Fixed branching geometry (calibrated to cohort medians)
Branch angle 55°, angle jitter (std) capped at 30°, Murray exponent 2.0,
daughter symmetry 0.675, length ratio 0.93. Achieved values match targets
(Murray 2.00, symmetry 0.675 exact; angle 59° achieved).

### 7.2 Reticulation — a mesh, not a decorated tree (this session's fix)
The original reticulation added nearest-neighbour cross-links to the tree, which
raised mean degree but left most edges as bridges (loop fraction ~0.20 at
⟨k⟩ = 2.5) — structurally unlike real venation, which is a planar **mesh** where
~78% of edges lie on a loop at a mean degree of only ~2.5.

**A new `mesh` reticulation mode was added** (`_add_mesh_reticulation`): it
closes areoles the way a real leaf does, by adding the shortest **Delaunay**
edges (planar and non-crossing by construction), each of which closes a real
areole. New anastomoses are thin minor veins (radius = the smaller endpoint's),
preserving the r⁴ conductance hierarchy. With this mode the synthetic hero
network reaches **loop fraction 0.70 at ⟨k⟩ = 2.51** (real 0.78) — a genuine
mesh. As in real leaves, ⟨k⟩ and loop fraction now rise together, controlled by
a single parameter `mesh_frac ≈ (⟨k⟩ − 2)/6`. The old `knn` mode is retained as
a non-default option so the earlier validated synthetic results are unchanged
(the `knn` default still produces its original ⟨k⟩ = 5.99, D = 1.43 network,
byte-identical).

### 7.3 Two near-orthogonal control knobs
Verified empirically: **generations** (tree depth / space-filling) moves D at
~fixed ⟨k⟩; **mesh_frac** moves ⟨k⟩ (and loop fraction) with only mild D drift.
The 2-D sweep grid (`config.SWEEP_MEAN_DEGREES` × `config.SWEEP_GENERATIONS` =
6 × 7 = 42 networks) has a grid ⟨k⟩–D correlation of just **+0.09**, spanning
⟨k⟩ 2.1–4.0 and D 1.26–1.81 and covering **78%** of the real cohort's (⟨k⟩, D)
cloud. This is the causal complement to Phase 1: the synthetic phase can move
⟨k⟩ and D one at a time, which real leaves cannot.

### 7.4 One documented, remaining limitation
Box-counting D saturates at ~1.81 because D is set by where the veins sit (the
point cloud), which mesh edges do not change; deeper generations plateau. The
~22% of real leaves with D > 1.81 (the densest meshes) are out of reach without
a space-filling/optimisation layout (Ronellenfitsch & Katifori), noted as future
work. The synthetic phase therefore tests the causal effect of D across a wide
range (1.26–1.81); it does not claim to reproduce every real leaf. This is stated
in the code, not hidden.

---

## 8. What is still pending (not yet done)
- Run the percolation engine over the calibrated 42-network synthetic grid, then
  regress p_c on ⟨k⟩ and D to confirm causally what Phase 1 found by observation.
- Decide whether to promote the calibrated (⟨k⟩ ≈ 2.5) network to the paper's
  "hero," which would supersede the older ⟨k⟩ ≈ 6 hero in the existing synthetic
  figures/numbers.
- The parasite-profile comparison and the (K_h, D) hydraulic surface already
  exist from earlier work and are unchanged by this session.

---

## 9. File map (for methods citations)
| File | Role |
|---|---|
| `holoparasitic/realleaf.py` | load a Matos leaf into a solvable graph; root/terminal boundary conditions |
| `holoparasitic/characterize.py` | full per-leaf profile + structural validity screen |
| `holoparasitic/boundary.py` | cropping-artifact (cut-end) measurement |
| `holoparasitic/metadata.py` | decode the extraction-quality flags |
| `holoparasitic/calibrate.py` | measure real branching geometry (two routes); emit calibrated synthetic params; 2-D sweep grid |
| `holoparasitic/matos_summary.py` | read the dataset's precomputed summary/HLD/areole tables (cross-checks) |
| `holoparasitic/network.py` | synthetic generator; `knn` and new `mesh` reticulation |
| `holoparasitic/percolation.py` | Monte Carlo GCC collapse + logistic p_c; `rho_max` bound |
| `holoparasitic/hydraulics.py` | conductance-Laplacian steady-state solver |
| `scripts/run_characterize.py` | Phase-3 driver over all leaves |
| `scripts/run_boundary_check.py` | cropping-artifact run |
| `scripts/run_quality_check.py` | quality-bias test + mechanism/size-control verdict |
| `scripts/build_cohort.py` | assemble the 100-leaf cohort with one auditable criterion |
| `scripts/run_validate_hydraulics.py` | exact resistance validation vs source data |
| `scripts/run_cohort_percolation.py` | Phase-1 p_c per leaf + p_c~⟨k⟩ vs p_c~D analysis |
| `scripts/run_calibration.py` | verify the synthetic generator vs the real cohort |

## 10. Key data outputs (for a results table)
| File | Contents |
|---|---|
| `data/characterization.csv` / `.json` | per-leaf architecture + hydraulics (120 leaves) |
| `data/cohort.csv` / `.json` | the 100-leaf cohort + every exclusion reason |
| `data/hydraulic_validation.json` | 119/119 exact resistance match, 5.67 M veins |
| `data/quality_report.json` | quality-bias test + verdict |
| `data/boundary_check.csv` / `.json` | cut-end fraction + corrected ⟨k⟩ per leaf |
| `data/cohort_pc.csv` | per-leaf p_c (random + degree) + predictors |
| `data/cohort_pc_analysis.json` | the p_c~⟨k⟩ vs p_c~D regression + sensitivity |
| `data/calibration.json` | synthetic-vs-real geometry + grid coverage |

## 11. Reproducibility notes
- Interpreter: Python 3.13 at `C:\laragon\bin\python\python-3.13\python.exe`.
- Libraries actually used: NetworkX, NumPy, SciPy, scikit-learn (logistic p_c),
  Matplotlib, Pillow (optional image path only). No image-segmentation stage
  (OpenCV/scikit-image) is required — the study consumes pre-extracted graphs.
- All screens and analyses are driven from CSV/JSON on disk; each long run saves
  incrementally and is resumable.
