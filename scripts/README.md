# scripts/ — driver catalogue

Every script here is standalone: run it with the project root as the working
directory and it will import `config.py` and `holoparasitic/` itself.

```powershell
C:\laragon\bin\python\python-3.13\python.exe scripts\<name>.py
```

Most accept `--help`. Anything marked *needs raw data* also requires the Matos
deposit unzipped into `UCBG_venation_form_data/`.

Nothing here writes to `data/` or `figures/` as a side effect of being imported;
outputs are produced only when a script is run as `__main__`.

---

## 1. Run the model

| Script | What it does | Writes |
|---|---|---|
| `run_demo.py` | Fast end-to-end demo, a few seconds. Start here. | `figures/network.png`, `sigmoid.png`, `pc_heatmap.png`, `collapse_montage.png` |
| `run_full.py [n_trials]` | The archived reference run: 10⁶-trial hero sigmoid plus every synthetic figure. ~11 min. | `data/results.npz`, `data/summary.json`, 6 figures |
| `run_parasites.py` | Compares p_c across parasite profiles on one host network. | `data/parasites.json`, `figures/parasites.png` |
| `run_dynamics.py` | Logistic haustorial load ρ(t); collapse time and pre-symptomatic window. | `data/dynamics.json`, `figures/dynamics.png` |
| `run_sink_surface.py` | Coupled (K_h, D) threshold surface on the calibrated mesh. Supersedes the `pc_surface` arrays in `results.npz`. | `data/sink_surface.json`, `figures/sink_surface.png` |
| `make_sink_demo.py` | Anchors `K_H_HOLOPARASITE` to literature and shows the sink is sub-cavitation. | `data/sink_demo.json`, `figures/sink_demo.png` |

## 2. Real leaves — load, screen, build the cohort

Run these in order; each consumes the previous one's output. *Needs raw data.*

| Script | What it does | Writes |
|---|---|---|
| `run_realleaf.py` | Phase 1: load each traced leaf and put it through the physics engine. | `data/realleaf_pc.csv`, `realleaf_summary.json` |
| `run_characterize.py` | Phase 3: full architectural and hydraulic profile per leaf. | `data/characterization.{csv,json}`, `data/species/*.json` |
| `run_boundary_check.py` | Measures the cropping artifact and sets the inclusion threshold from the data. | `data/boundary_check.{csv,json}` |
| `run_quality_check.py` | Tests whether the dataset's own extraction-quality flags bias mean degree. | `data/quality_report.json`, `characterization_annotated.csv` |
| `build_cohort.py` | Joins every screen into the definitive cohort, with a reason recorded per exclusion. | `data/cohort.{csv,json}` |
| `run_cohort_percolation.py` | The real-leaf percolation run: random and degree-targeted attack per leaf. | `data/cohort_pc.csv`, `cohort_pc_analysis.json` |

## 3. Synthetic generator — calibrate and sweep

| Script | What it does | Writes |
|---|---|---|
| `run_calibration.py` | Checks the generator reproduces the cohort's branching geometry and spans its (⟨k⟩, D) region. | `data/calibration.json`, `figures/calibration_grid.png` |
| `run_synthetic_grid.py` | The 42-network causal grid: mean degree and D manipulated separately. | `data/synthetic_grid_pc.csv`, `synthetic_grid_analysis.json` |
| `run_finite_size_fixedD.py` | Finite-size sweep with architecture pinned, so size is not confounded with D. | `data/finite_size_fixedD.json` |
| `check_fixedD_drift.py` | Audits what actually stayed fixed in that sweep. Answer: loop fraction did not. | updates `data/finite_size_fixedD.json` |
| `run_scaling_mesh.py` | Finite-size scaling and critical exponent β on the mesh hero. | `data/scaling_mesh.json`, `figures/stat_beta_mesh.png` |
| `dump_synthetic_perNetwork.py` | Per-network metrics for all 42 grid cells, for the worked-computations appendix. | `data/synthetic_pernetwork.csv` |

## 4. The reticulation-enhancement experiment

| Script | What it does | Writes |
|---|---|---|
| `run_cohort_suggested.py` | Per leaf: p_c as traced vs the same leaf with shortest Delaunay areole closures added. Resumable. | `data/cohort_suggested.csv` |
| `make_suggested_summary.py` | Aggregates the above, with a clean-extraction sensitivity block. | `data/cohort_suggested_summary.json`, `figures/cohort_suggested.png` |
| `run_random_edge_control.py` | The null arm: random edges instead of shortest-Delaunay ones, at matched count. | `data/random_edge_control.csv` |
| `run_robustness_ceiling.py` | Per-species headroom: which lever, and how much, at the observed ceiling. | `data/robustness_ceiling.csv`, `robustness_ceiling_summary.json` |

## 5. Validation and audit

| Script | What it does | Writes |
|---|---|---|
| `validate_stats.py` | Statistical validation of the percolation model. Tests 2 and 3 still run on the legacy `knn` generator — see `run_scaling_mesh.py`. | `figures/stat_beta_fit.png`, `stat_finite_size.png` |
| `run_validate_hydraulics.py` | External check of the vein-resistance model against the dataset's own `Resistance_4` over 5.67M veins. | `data/hydraulic_validation.json` |
| `run_kleaf_validate.py` | Modelled conductance vs measured K_leaf. Reported as a limitation, not a validation. | `data/kleaf_validation.csv`, `kleaf_validation_summary.json` |
| `run_robustness.py` | Root-invariance, Monte Carlo convergence, and Molloy–Reed comparison. | `data/robustness.json` |
| `run_cavitation_sensitivity.py` | Is "0 vessels embolise" a finding or an artifact of the boundary conditions? | `data/cavitation_sensitivity.json` |
| `run_resistance_convention_sensitivity.py` | Does the conductance convention change the K_leaf conclusion? | `data/resistance_convention_sensitivity.{csv,json}` |
| `run_graph_metric_audit.py` | Audits two structural claims, including the loop-fraction definition. | `data/graph_metric_audit.json` |
| `run_criterion_and_locality.py` | Collapse-criterion and attack-locality sensitivity. | `data/criterion_and_locality.{csv,json}` |
| `run_second_pass_audit.py` | Confound and robustness battery for the second-pass audit. | `data/second_pass_audit.json` |
| `run_final_resolution_checks.py` | The final unresolved-item battery. | `data/final_resolution_checks.json` |
| `run_rrl_diagnostics.py` | Numbers the deep literature pass needed computed. | `data/rrl_diagnostics.json` |
| `run_targeted_ci.py` | Bootstrap CIs for the two targeted attacks, which the original run did not store. | `data/targeted_ci.json` |
| `run_empirical.py` | Box-counting D measured on leaf photographs, via the same code path as the graphs. | `data/empirical_summary.json` |

## 6. Assemble the reported numbers

Run in this order. `build_analysis_master.py` is the choke point: everything the
manuscript quotes should come from its output, not from an intermediate file.

| Script | What it does | Writes |
|---|---|---|
| `build_analysis_master.py` | Merges every per-leaf table into one, records cohort provenance, and computes every reported statistic once. | `data/analysis_master.csv`, `cohort_provenance.json`, `results_verified.json` |
| `verify_manuscript_numbers.py` | Checks every statistic in the manuscript against the archived files, never against a previous draft. | stdout report |
| `make_supplementary_tables.py` | Builds Tables S1–S5 from the archived JSON so no cited value is unsourced. | `SUPPLEMENTARY_TABLES.md` |
| `make_appendix_c.py` | Appendix C: every statistic re-derived from raw data with the arithmetic shown. | `APPENDIX_C_COMPUTATIONS.tex`, `APPENDIX_C_CHECKS.csv` |
| `make_appendix_computations.py` | The earlier appendix generator, superseded by `make_appendix_c.py`. | same targets |
| `export_csv.py` | Exports `results.npz` to readable CSV. | `data/csv/*.csv` |
| `show_npz.py` | Prints the contents of a `.npz`. Inspection only. | — |

## 7. Documents and figures

Document builders typeset a markdown file; the markdown is the source of truth,
so re-run the builder after editing rather than editing the `.docx`.

| Script | Renders |
|---|---|
| `make_results_docx.py` | Results section, every number read from `data/` at generation time |
| `make_revised_sections_docx.py` | `MANUSCRIPT_REVISED_SECTIONS.md` |
| `make_discussion_docx.py` | `DISCUSSION_REVISED.md` |
| `make_discussion_sop_docx.py` | `DISCUSSION_SOP_ALIGNED.md` |
| `make_supplementary_docx.py` | `SUPPLEMENTARY_TABLES.md` |
| `make_stats_section_docx.py` | `STATISTICAL_ANALYSIS_REWRITE.md` |
| `make_bibliography_docx.py` | The bibliography, APA 7th with hanging indent |
| `patch_discussion_docx.py` | Applies audit corrections to a copy, leaving the original intact |
| `make_data_summary_xlsx.py` | `DATA_SUMMARY.xlsx`, four sheets |

| Script | Figure |
|---|---|
| `make_methodology_figures.py` | The data-driven Chapter III figures |
| `make_flowchart_figures.py` | Chapter III flowcharts (fig01, 02, 03, 07, 08b) |
| `make_pipeline_revised.py` | Corrected overall-pipeline flowchart |
| `make_stats_tree.py` | Fig 12, matching the analysis the code actually runs |
| `make_potential_relief.py` | 3-D water-potential relief with a sink well |
| `make_real_suggested.py` | Per-species current vs more-reticulate leaf, from that species' own network |
| `make_cis_ant_zoom.py` | High-resolution zoom of the *Cissus* panel |
| `make_suggested_network.py` | Generic reticulation-concept panel |
| `make_edge_control_figure.py` | Fig 14, the placement-rule control |
| `make_board_figures.py` | The five vision-board figures |

## 8. Maintenance

| Script | What it does |
|---|---|
| `fix_sink_surface_summary.py` | Recomputes the derived summary fields of `sink_surface.json` from its own cells |
| `dump_sink_sweep.py` | Archives the per-gradient numbers behind `make_sink_demo.py` |
