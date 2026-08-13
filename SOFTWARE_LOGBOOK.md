# Software Logbook — Holoparasitic Percolation Project

> Chronological record of the software build, one entry per commit date, newest first.
> Pre-2026-07-22 entries are reconstructed from commit messages + the build-state record;
> entries from 2026-07-25 on are first-hand. Maintained going forward: new dated entries are
> added at the top as work lands. Repo: `c:\Users\Nicko\HOLOPARASITIC`.
> Interpreter: `C:\laragon\bin\python\python-3.13\python.exe`.

---

## 2026-08-04 — (uncommitted, working tree) Real-leaf reticulation cohort + grounded sink + parasite drop
**What happened.** Built the cohort-wide real-leaf reticulation result (the new headline), grounded the
haustorial sink in literature, dropped the multi-parasite comparison, and rebuilt the data summary.
**Software added / changed:**
- `scripts/run_cohort_suggested.py` (new) — for ALL 120 real Matos leaves, measures random-attack p_c on
  (a) the leaf as traced and (b) the same leaf with shortest Delaunay areole-loops added to its OWN
  venation up to the cohort reticulation ceiling (<k>=2.811), at 10,000 trials/network. Incremental,
  resumable save to `data/cohort_suggested.csv`. (Ran across two sessions; resumed cleanly from row 77.)
- `scripts/make_suggested_summary.py` (new) — aggregates the cohort, segmenting valid whole-leaves from
  crop fragments (N>=1000) and adding a clean-A (no vein-miscount) sensitivity block →
  `data/cohort_suggested_summary.json` + `figures/cohort_suggested.png`. **Result: 105 valid leaves,
  p_c median 0.201→0.215, delta +0.009 median (max +0.046), 89% improved, 0 worsened.** Honest caveat:
  clean-A subset (n=21) gains less (+0.007, 62% improved) — missing-vein (B) leaves inflate the headline.
- `scripts/make_sink_demo.py` (new) — anchors K_h to literature: solved so one haustorium diverts ~18–20%
  of leaf flow (hemiparasite floor, Jiang et al. 2003) at an illustrative ~1.5 MPa gradient (review-level,
  NOT primary, NOT Kaiser 2015 — corrected 2026-08-08) →
  **`config.K_H_HOLOPARASITE = 0.0392`**. **Key honest finding: at that realistic strength the sink is
  SUB-cavitation — 0 vessels embolise at any gradient; it drains water/carbon but cannot rupture the
  xylem.** So the hydraulic sink and the percolation collapse are decoupled lenses. → `figures/sink_demo.png`
  + `data/sink_demo.json`. `config.py` gains the calibrated constant (K_H_DEFAULT unchanged).
- `empirical/RELATED_WORK.md` — new "Holoparasite sink strength" section with 4 verified RRLs (Jiang &
  Jeschke & Hartung 2003; Jeschke et al. 1994; Kaiser et al. 2015; Glatzel & Geils 2009) + the honest
  sub-symptomatic reading.
- `scripts/make_data_summary_xlsx.py` — rebuilt `DATA_SUMMARY.xlsx`: **dropped the Parasites sheet**
  (stipulated efficiencies, weakest-validated), made the real reticulation cohort the centerpiece (new
  "Reticulation Cohort" per-leaf sheet + headline rows), added the grounded sink-demo rows, and flagged
  `parasites.json` as deprecated in the File Index.
- **Framing note (no code):** discussed retilting the title away from "driven by holoparasitic sink"
  (the sink is sub-symptomatic; host structure sets the threshold) and keeping the graph theory as METHOD
  so the work reads as Life Sciences, not computational science.

---

## 2026-08-01 — (commit `1f575b7`) Stale-figure sweep onto the mesh hero
**What happened.** Audited every `figures/*.png` for consistency with the promoted mesh hero and
regenerated the two that were still on the legacy knn network; confirmed the rest were already current.
**Software added / changed:**
- `figures/stat_finite_size.png` — regenerated from the already-computed `data/scaling_mesh.json`
  (no percolation re-run needed): mesh finite-size series, transition width sharpens with N.
- `figures/stat_beta_fit.png` — refreshed to the mesh β≈1.48 fit (from `stat_beta_mesh.png`),
  replacing the stale knn β figure.
- **Audit result (no change needed):** `pc_heatmap.png`, `sigmoid*.png`, `network.png`, `collapse.*`,
  `parasites.png` were all already produced by the 2026-07-31 mesh run (`run_full.py 1000000` /
  parasite re-run) and are consistent. The heatmap deliberately sweeps its D axis on knn via the
  `sweep._network_for_reticulation` patch (that is by design, not stale).
- **Flagged, left as-is:** `graph_synthetic.png` still shows the old ⟨k⟩≈6 knn *methodology
  illustration* (Fig 5) — an illustration, not a results figure, so not regenerated.
- No engine/config changes; remaining session work was explanatory (documented the
  Delaunay areole-closure procedure behind the per-species suggested-reticulation figures).

---

## 2026-07-30 — (commits `4fc7fad`, `1f575b7`) Phase-2 causal result + polish sweep
**What happened.** Completed the outstanding to-do list and started the "robustness ceiling" result.
**Software added / changed:**
- `scripts/run_synthetic_grid.py` (new) — Phase-2 driver: runs percolation over the calibrated
  6×7 = 42-network grid (`calibrate.grid_params`), random + degree attack, measures ⟨k⟩ and D on each
  generated network, regresses p_c on both (partial correlations, OLS, Spearman). Incremental,
  resumable save to `data/synthetic_grid_pc.csv` + `data/synthetic_grid_analysis.json`. This is the
  causal complement to the observational real-cohort regression.
- `scripts/make_flowchart_figures.py` (new) — high-quality landscape flowcharts (Figs 1, 2, 3, 7 +
  a new cavitation-cascade loop) matching the house palette.
- `scripts/make_potential_relief.py` (new) — 3-D water-potential relief rendered from the real
  `HydraulicSolver`, showing the haustorial sink drawing a well into the ψ field.
- `scripts/make_stats_tree.py` (new) — Fig 12 statistical-analysis flowchart, rebuilt to match the
  analysis the code actually runs (logistic p_c fit + bootstrap CI; Spearman + partial correlation +
  OLS/VIF; nonparametric group tests), replacing the generic Shapiro→ANOVA/Kruskal tree.
- `scripts/run_kleaf_validate.py` (new) — validates modelled leaf conductance against measured Kleaf
  (`hydraulics/UCBG_venation_kmax.csv`).
- `scripts/run_robustness.py` (new) — root-choice sensitivity, Monte-Carlo convergence, and
  percolation-vs-theory (Molloy–Reed) on a calibrated mesh network.
- `scripts/run_robustness_ceiling.py` (new) — per-species robustness-ceiling: how much p_c each cohort
  species could gain by moving toward the reticulate end of the achievable range.
- `METHODOLOGY.md` — reconciled two code↔prose mismatches: (1) stated the model is **site (node)
  percolation**, not bond/edge removal, matching `percolation._trial_random`/`_trial_hydraulic`;
  (2) corrected the GCC definition to "largest connected component" (what `_gcc_size` computes),
  noting root-connectivity is not separately enforced.
- `empirical/RELATED_WORK.md` (new) — verified citations + distinctions for Mander & Williams (2024),
  Mrad et al. (2021), Loepfe et al. (2007); ready-to-paste hedged novelty paragraph; carries the
  Vishnu→Muraleedharan/*Flora* citation fix.
- Installed `statsmodels`, `scikit-posthocs`.
- **HERO PROMOTED (user-approved).** `config.DEFAULT_NETWORK` switched from the legacy knn
  ⟨k⟩≈6 network to the cohort-calibrated planar **MESH** at the real ⟨k⟩=2.5, N=1023 (generations=9,
  D=1.387) — a like-for-like size swap; old hero kept as `config.LEGACY_HERO_NETWORK`. `sweep.py`
  patched to force knn in the reticulation D-sweep (else the D-axis collapses under mesh default).
  `results.npz` regenerated via `run_full.py 1000000`. New hero p_c(random) ≈ 0.27 (was 0.279).
- `VALIDATION.md` §9 — added the honest **Kleaf limitation** (Spearman ρ=0.19, p=0.07, n=93):
  xylem-only model does not predict outside-xylem-dominated whole-leaf Kleaf.
- **β / universality class re-run on the mesh** (`scripts/run_scaling_mesh.py` → `data/scaling_mesh.json`):
  genuine continuous transition (power-law R²=0.995, width sharpens with N), but **β≈1.48 matches neither
  mean-field nor 2-D** and is f_c-sensitive → no definitive class without a multi-size collapse. Corrected an
  earlier wrong 2-D guess in `VALIDATION.md`.
- **New-hero number propagation:** re-ran `run_parasites.py` on the mesh; updated `ANALYSIS.md` (hero table,
  the degree-attack flip narrative, parasite table + reversed ordering), created `HERO_NUMBERS.md` (canonical
  old→new map), added pointer notes to PRESENTATION/ORAL_SCRIPT/PROPOSAL_DEFENSE/METHODOLOGY_SCRIPT/CONCEPTS.
- **Per-species suggested-network images fixed.** `scripts/make_suggested_network.py` used a fixed seed, so all
  five "suggested" panels were byte-identical (a real flaw). Replaced with `scripts/make_real_suggested.py`,
  which adds shortest Delaunay areole-closures to EACH species' OWN Matos leaf and reports MEASURED p_c on both
  panels → `fig_realsuggested_<spp>.png`; kept one generic as `fig_reticulation_concept.png`.

---

## 2026-07-29 — Methodology figures + 3-D figure (commits `fa82912`, `88ff06b`)
Added the data-driven methodology figure set (`scripts/make_methodology_figures.py` outputs:
real Cistus network, synthetic network, box-counting, attack modes, GCC, Monte-Carlo curve) and a
3-D figure. These are the publication figures for Chapter III.

## 2026-07-27 — Compiled figure pack (commit `035563f`)
Added `METHODOLOGY_FIGURES.html`, a single local page collecting all methodology figures
(schematics as inline SVG/CSS, data figures as PNGs) with captions and placement notes.

## 2026-07-26 — First real-vs-synthetic renders (commit `c3e023c`)
Generated the annotated graph of the largest real leaf (Cis_ant / Cistus) and a synthetic-network
image, establishing the visual real-vs-synthetic comparison.

## 2026-07-25 — Generator calibration + cohort percolation (commits `0ecf013`, `4f04206`)
The core Phase-1/Phase-2 bridge.
- `holoparasitic/calibrate.py` — `COHORT_TARGETS` (medians of the 100-leaf cohort), `calibrated_base()`,
  `grid_params()`; two near-orthogonal knobs (reticulation→⟨k⟩, generations→D).
- **Mesh reticulation fix** (`network._add_mesh_reticulation`): planar Delaunay areole closure raised
  loop_fraction from ~0.20 (decorated tree) to ~0.70 (true mesh, real ≈0.78). `reticulation_mode`
  added to `NetworkParams` (default `knn` preserves the old hero byte-identically).
- `percolation.find_pc(..., rho_max=)` kwarg added (backward-compatible) to concentrate the sweep for
  real leaves that collapse early.
- Cohort percolation run completed → `data/cohort_pc.csv`, `cohort_pc_analysis.json`. Headline: on the
  real cohort ⟨k⟩ and D are near-independent (r≈0.15) and both predict p_c (partial r 0.60 and 0.50).

## 2026-07-24 — Real data ingested (commit `e667fe7`)
Added the Matos et al. (2024) Dryad data and the real-leaf loader (`holoparasitic/realleaf.py`,
`load_matos`), plus characterization/boundary/quality modules and `scripts/build_cohort.py`
(100-leaf analysis cohort locked by a structural inclusion rule).

## 2026-07-23 — Recalibration to real venation photos (commit `865be31`)
Recalibrated the synthetic generator's branching geometry against actual venation imagery ahead of
full cohort calibration.

## 2026-07-22 — Checkpoint before auto-allow (commit `3094d20`)
Repository snapshot prior to enabling permissive tool permissions.

## 2026-07-03 — Time as a variable / differential-equation deliverable (commit `3a6fa8f`)
Added a time-dependent dynamics path (`scripts/run_dynamics.py` → `data/dynamics.json`) so the project
carries a differential-equation deliverable alongside the static percolation result.

## 2026-06-29 — Empirical-phase planning (commit `fd14173`)
Planned the cross-section and venation-photo workflow that later became the Matos-deposit route.

## 2026-06-28 — Initial build (commits `4b41073`, `2f05886`, `a5bbd87`, `811f280`, `01afc21`)
- Initial modular package: `config.py` (frozen schema) + `holoparasitic/` (network, fractal,
  hydraulics, percolation, sweep, viz); `scripts/run_demo.py`, `run_full.py`; smoke tests.
- Added concept documentation (`.md`).
- Added the statistical-analysis tool (`scripts/validate_stats.py`) and recalibrated the D-value.
- Validated the pipeline and updated the explanatory markdown docs for consistency.
- Added a second holoparasite profile plus a hemiparasite pair (`config.PARASITES`); refreshed
  `data/results.npz`.
