# data/ — output catalogue and provenance

Everything here is generated. Nothing in this directory is hand-edited, and
nothing should be: if a number looks wrong, fix the script and re-run it.
`scripts/README.md` says which script writes what.

## Read these first

| File | What it is |
|---|---|
| `results_verified.json` | **The source of truth for every reported statistic.** Written by `build_analysis_master.py`; the manuscript documents are generated from it. Its `_canonical_loop_fraction` field names the loop-fraction definition every table uses. |
| `analysis_master.csv` | One row per leaf, every descriptor and every threshold merged into a single table. |
| `cohort_provenance.json` | Which leaves are in which cohort, the rule that put them there, the trial budget, and a reason string for every exclusion. |

Three cohorts are nested — 100 ⊂ 105 ⊂ 112 ⊂ 120 — and they were screened by
different rules for different purposes. Any per-leaf number should be read
together with the cohort it came from; `cohort_provenance.json` is the record.

## The synthetic reference run

| File | Contents |
|---|---|
| `results.npz` | The archived arrays from `run_full.py`: the 10⁶-trial collapse curve (`rhos`, `p_collapse`, `gcc_fraction`), the targeted curves, and the legacy `pcd_*` / `surface_*` sweeps. |
| `summary.json` | Scalar companions to the above: p_c, its CI, D, network summary. |
| `results_preview.npz`, `summary_preview.json` | A short run kept for comparison; not a paper artifact. |
| `csv/` | Readable exports of `results.npz`. **See `csv/README.md` — two of the four are superseded and say so.** |
| `targeted_ci.json` | Bootstrap CIs for the two targeted attacks, which `run_full.py` did not store. |

The `pcd_*` and `surface_*` arrays inside `results.npz` were computed on the
legacy `knn` generator (mean degree 4.4–7.0, far above anything empirical). They
are kept because earlier drafts quote them; `sink_surface.json` is the current
(K_h, D) result and `synthetic_grid_pc.csv` is the current p_c-vs-structure one.

## Real leaves

| File | Contents |
|---|---|
| `species/*.json` | Per-leaf profile, one file per species code (120 files). |
| `characterization.{csv,json}` | The 112-leaf characterization table. |
| `characterization_annotated.csv` | The same, joined to the dataset's extraction-quality flags. |
| `boundary_check.{csv,json}` | Cropping-artifact measurement per leaf: raw vs interior-corrected mean degree. |
| `quality_report.json` | Whether extraction quality biases mean degree. |
| `cohort.{csv,json}` | The 100-leaf percolation cohort and its inclusion record. |
| `cohort_pc.csv`, `cohort_pc_analysis.json` | Random and degree-targeted thresholds per leaf, and the predictor analysis. |
| `realleaf_pc.csv`, `realleaf_summary.json` | The earlier Phase-1 pass. Superseded by the cohort files above. |
| `loop_fraction_perleaf.csv`, `loop_fraction_nonbridge.json` | Both loop-fraction definitions side by side. `loop_fraction_nonbridge` is the canonical one. |

### One naming trap, documented rather than removed

Two different quantities have been called "loop fraction" in this project:

- **tag-based** — veins the source dataset labelled type `EL`, over all veins.
  Depends on someone else's vein classification.
- **non-bridge** — veins that actually lie on a cycle, over all veins. Purely
  topological and defined identically on real and synthetic networks.

They differ by a few thousandths, which is enough to have produced a 0.719
vs 0.727 disagreement between two draft tables. **The non-bridge definition is
canonical and is what every reported figure uses.** The tag-based value is still
emitted by `realleaf.summary()` and `calibrate.measure_from_graph()` under the
name `loop_fraction`, for continuity with the archived CSVs; each of those
docstrings states the distinction, and `run_realleaf.py` now writes both columns
so they can never be confused again.

## Synthetic grid and sweeps

| File | Contents |
|---|---|
| `calibration.json` | Generator geometry vs cohort targets, and grid coverage of the real (⟨k⟩, D) cloud. |
| `synthetic_grid_pc.csv`, `synthetic_grid_analysis.json` | The 42-network causal grid. |
| `synthetic_pernetwork.csv`, `synthetic_full_metrics.json`, `synthetic_extra.json` | Per-network metrics behind the appendix arithmetic. |
| `finite_size_fixedD.json` | Finite-size sweep with architecture pinned, plus the drift audit that qualifies it. |
| `scaling_mesh.json` | Finite-size scaling and β on the mesh hero. No universality class is claimed from it. |

## Enhancement experiment

| File | Contents |
|---|---|
| `cohort_suggested.csv`, `cohort_suggested_summary.json` | p_c as traced vs with Delaunay areole closures added, per leaf and aggregated. |
| `random_edge_control.csv` | The null arm: random edges at matched count. |
| `robustness_ceiling.csv`, `robustness_ceiling_summary.json` | Per-species headroom and which lever dominates. |

## Sink and hydraulics

| File | Contents |
|---|---|
| `sink_demo.json` | The literature anchoring of `K_H_HOLOPARASITE`, and the sub-cavitation finding. |
| `sink_sweep.csv` | Per-gradient diversion and embolism counts behind it. |
| `sink_surface.{json,csv}` | Critical haustorial density over the (K_h, D) grid, on the calibrated mesh. |
| `cavitation_sensitivity.json` | Whether "0 vessels embolise" survives varying the boundary conditions. |
| `hydraulic_validation.json` | Vein resistance vs the dataset's own values, 5.67M veins. |
| `kleaf_validation.csv`, `kleaf_validation_summary.json` | Modelled conductance vs measured K_leaf. A limitation, not a validation. |
| `resistance_convention_sensitivity.{csv,json}` | Whether the conductance convention changes that conclusion. |
| `dynamics.json` | ρ(t), collapse time, and the pre-symptomatic window. |
| `parasites.json` | Per-parasite thresholds on one host. |

## Audits

`robustness.json`, `graph_metric_audit.json`, `criterion_and_locality.{csv,json}`,
`second_pass_audit.json`, `final_resolution_checks.json`, `rrl_diagnostics.json`
— each is the machine-readable output of the correspondingly named `run_*.py`
script, and each has a prose counterpart in the audit markdown at the repo root.

## Not results

`_cl_snap.csv` is a checkpoint snapshot from a long resumable run, kept so an
interrupted run can be traced. Run logs are not committed; the results they
narrate are in the files above.
