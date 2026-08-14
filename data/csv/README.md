# data/csv — provenance and supersession

All files here are exported by `scripts/export_csv.py` from `data/results.npz`
and were regenerated on 2026-08-14 because `pc_surface.csv` had gone stale: it
still held an older run (D 1.3529–1.4790, p_c 0.1381–0.6426) that disagreed with
the live `results.npz` (D 1.4440–1.5202, p_c 0.2298–0.7189). All three exports
now match the archive.

| File | Contents | Generator | Status |
|---|---|---|---|
| `sigmoid.csv` | ρ, P(collapse), GCC fraction — the hero collapse curve | cohort-calibrated planar **mesh**, N = 1,023, 1,000,000 trials | current |
| `pc_vs_D.csv` | topological p_c vs measured D | **legacy `knn` generator** (⟨k⟩ 4.4–7.0) | superseded |
| `pc_surface.csv` | p_c over the (K_h, D) grid, coupled hydraulic mode | **legacy `knn` generator**, K_h 0.3–2.5, 600 trials/cell | superseded |
| `sink_surface.csv` | critical **haustorial density** over (K_h, D) | cohort-calibrated **mesh**, K_h anchored on the calibrated 0.0392, 6,000 trials/cell + bootstrap CI | current |

## Two warnings before using the superseded files

**1. Wrong generator.** `sweep._network_for_reticulation` forces
`reticulation_mode='knn'` for the D sweep and the (K_h, D) surface, so both were
computed on the pre-2026-07 generator whose mean degree at those reticulation
settings is **4.4–7.0** — far above the empirical cohort's 2.15–2.99 and above
the calibrated mesh's 2.489. Their absolute thresholds are not comparable with
anything else in the study.

**2. `pc_surface.csv` does not report the same quantity as the rest of the
study.** In `percolation.py` hydraulic mode, ρ is the fraction of nodes *bearing
a haustorium*, not the fraction removed; nodes are removed only if the solved
water potential falls below `PSI_CAVITATION`. The threshold is therefore a
critical **haustorial attachment density**.

Use `sink_surface.csv` (written by `scripts/run_sink_surface.py`) instead. It
reports the same quantity on the calibrated mesh, with the sink-strength axis
expressed in multiples of the literature-calibrated
`config.K_H_HOLOPARASITE = 0.0392`, and it records explicitly which cells have
**no threshold at all** — a distinction the legacy export could not make.
