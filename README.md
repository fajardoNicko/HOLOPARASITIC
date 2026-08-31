# Holoparasite-Induced Vascular Percolation Study

Computational biophysics model of holoparasitic haustorial sink strength and the
vascular percolation threshold p_c of a host plant's hydraulic network — the
point at which the network fragments irreversibly. The argument for p_c is that
it is reached *before* visible wilting, so it is a pre-symptomatic intervention
metric rather than a diagnosis after the fact.

The study runs on two kinds of network, deliberately:

- **Real leaves.** 120 traced venation networks from Matos et al. (2024), UC
  Berkeley Botanical Garden (Dryad `10.5061/dryad.1g1jwsv36`). These carry the
  observational result and its confounds.
- **Synthetic networks.** A Murray's-law generator calibrated to the real
  cohort's branching geometry. Because its two structural knobs are
  near-orthogonal, it separates causes the real cohort can only correlate.

Parasites are modelled as attachment geometry × trophic efficiency, anchored on
*Cuscuta campestris*: stem (*Cuscuta*), root (*Orobanche*) and systemic
(*Pilostyles*) holoparasites, with *Striga* and mistletoe kept as hemiparasitic
comparisons.

## Pipeline

```
  real leaf CSVs ──► realleaf.py ─┐
                                  ├─► one networkx.Graph  ──► fractal.py ──► D
  config.py params ─► network.py ─┘   (schema in config.py)      │
                                              │                  │
                        hydraulics.py ◄───────┤                  │
                        Kirchhoff A·psi = b   │                  │
                        + haustorial sink K_h │                  │
                        + cavitation          ▼                  ▼
                                       percolation.py  ──► logistic fit ──► p_c
                                       Monte Carlo node
                                       removal, GCC size
```

Every module reads and writes the same graph contract, so a traced leaf and a
generated network are measured by literally the same code path. That is what
makes the two halves of the study comparable rather than merely analogous.

## Quick start

Pinned to Python 3.13; see `requirements.txt`.

```powershell
C:\laragon\bin\python\python-3.13\python.exe -m pip install -r requirements.txt

# invariants — 5 tests, a few seconds
C:\laragon\bin\python\python-3.13\python.exe tests\test_smoke.py

# end-to-end demo, seconds, writes figures\
C:\laragon\bin\python\python-3.13\python.exe scripts\run_demo.py

# the archived reference run: 1,000,000 trials + figures (~11 min, i5-8265U)
C:\laragon\bin\python\python-3.13\python.exe scripts\run_full.py
C:\laragon\bin\python\python-3.13\python.exe scripts\run_full.py 100000   # lighter
```

Anything touching real leaves additionally needs the Matos deposit unzipped into
`UCBG_venation_form_data/` (~4.4 GB, deliberately not committed).

## Reference network and headline numbers

The reference ("hero") network is `config.DEFAULT_NETWORK`: the cohort-calibrated
planar **mesh**, promoted 2026-07-30. Reproduce these with `run_full.py`.

| Quantity | Value |
|---|---|
| N | 1,023 |
| mean degree ⟨k⟩ | 2.489 |
| independent loops | 251 |
| box-counting D | 1.387 |
| p_c, random removal | **0.2711**, 95% CI [0.2700, 0.2720] (10⁶ trials) |
| p_c, betweenness-targeted | 0.1889, 95% CI [0.1879, 0.1902] (10⁵ trials) |
| p_c, degree-targeted | 0.2023, 95% CI [0.2014, 0.2033] (10⁵ trials) |

Both targeted attacks fall below random, with the betweenness (backbone) attack
strongest. This matches the real cohort, where degree-targeted p_c is below
random in 100 leaves out of 100. Source: `data/summary.json` and
`data/targeted_ci.json`.

Four cohorts are used, nested 100 ⊂ 105 ⊂ 112 ⊂ 120. They were screened by
different rules for different purposes, so which one a number came from matters:

| Cohort | n | Criterion |
|---|---|---|
| traced | 120 | every Matos leaf loaded |
| characterized | 112 | ≥ 500 veins |
| enhancement | 105 | N ≥ 1,000 and current p_c ≥ 0.02 |
| percolation | 100 | ≥ 2,000 veins, ≥ 1 cycle, cut-end terminal fraction ≤ 0.05, absolute mean-degree shift ≤ 0.05 |

`data/cohort_provenance.json` records each membership and every exclusion reason.
`data/results_verified.json` is the machine-readable source of truth for every
reported statistic; the manuscript documents are generated from it by
`scripts/make_results_docx.py`, never hand-edited.

Main findings, all with n and test in `results_verified.json`:

- On the 100-leaf cohort, mean degree and D are both independent predictors of
  p_c (partial Spearman 0.736 and 0.502) and are themselves nearly uncorrelated.
- On the 42-network synthetic grid, where the two are manipulated separately,
  mean degree carries almost all of the effect (standardized β 0.933 vs 0.067,
  R² = 0.887). Connectivity is the lever; D is real but small.
- Adding shortest Delaunay areole closures to each leaf's own venation raises
  median p_c from 0.201 to 0.215; 93 of 105 leaves improve and none worsen.
- At the literature-anchored sink strength (`K_H_HOLOPARASITE = 0.0392`) the
  haustorium is sub-cavitation: no vessel embolises at any gradient tested. The
  hydraulic sink and the percolation collapse are therefore decoupled lenses on
  the same host, not one mechanism.

Two things the study deliberately does **not** claim: a universality class (the
measured β is window-sensitive and matches neither mean-field nor 2-D; see
`scripts/run_scaling_mesh.py`), and validation against measured K_leaf (Spearman
0.187, p = 0.073, n = 93 — reported as a limitation, since the model is
xylem-only while K_leaf is dominated by outside-xylem pathways).

## Repository layout

```
config.py                 physical constants, default parameter sets, graph schema
holoparasitic/            the modelling library (module map below)
scripts/                  every runnable driver          -> scripts/README.md
tests/                    smoke tests
data/                     all generated results          -> data/README.md
figures/                  all generated figures
empirical/                our own leaf photographs, measurements and the
                          literature notes behind them   -> empirical/README.md
rrl/                      the ten-domain literature review, one file per domain
UCBG_venation_form_data/  the Matos deposit, unzipped (not committed, ~4.4 GB)
hydraulics/               Matos et al.'s measured hydraulics tables (vendored)
Rscripts/                 Matos et al.'s own R analysis code (vendored, reference)
```

`hydraulics/` and `Rscripts/` are **third-party files redistributed from the
Matos deposit**, not our work. `Rscripts/` is kept for reference only and is
never executed by this pipeline. `hydraulics/hydraulics/UCBG_venation_kmax.csv`
is a genuine input: `run_kleaf_validate.py` and
`run_resistance_convention_sensitivity.py` both read the measured K_leaf values
from it.

## Module map

| File | Role |
|---|---|
| `config.py` | Physical constants, all default parameter sets, the graph schema |
| `holoparasitic/network.py` | Synthetic Murray's-law generator; `knn` and `mesh` reticulation |
| `holoparasitic/realleaf.py` | Loader for one traced Matos leaf, onto the same schema |
| `holoparasitic/metadata.py` | The source dataset's extraction-quality flags, decoded |
| `holoparasitic/fractal.py` | Box-counting D, shared by graphs and leaf images |
| `holoparasitic/hydraulics.py` | Sparse Kirchhoff solver, haustorial sink, cavitation |
| `holoparasitic/percolation.py` | Monte Carlo GCC collapse, logistic p_c, bootstrap CI |
| `holoparasitic/characterize.py` | Full per-leaf profile and the validity screen |
| `holoparasitic/boundary.py` | Cropping-artifact test for the windowed source networks |
| `holoparasitic/calibrate.py` | Measures real branching geometry; fits the generator to it |
| `holoparasitic/matos_summary.py` | Reads the authors' precomputed metrics, as a cross-check |
| `holoparasitic/dynamics.py` | Logistic load ρ(t) and the pre-symptomatic window |
| `holoparasitic/sweep.py` | p_c vs D, and the coupled (K_h, D) surface |
| `holoparasitic/viz.py` | Network plot, collapse sigmoid, heatmap, animation |

Drivers live in `scripts/` and are catalogued in [scripts/README.md](scripts/README.md).
Outputs and their provenance are catalogued in [data/README.md](data/README.md).

## Three modelling decisions worth knowing before reading the code

**1. Reticulation is required, not decorative.** A strict Murray tree has no
redundant paths, so removing an internal node disconnects its whole subtree and
the giant component bleeds off roughly linearly — there is no sharp threshold to
measure at all. Real venation is reticulate. Two modes implement this:
`knn` adds nearest-neighbour cross-links to a tree (mean degree rises but most
edges stay bridges); `mesh` adds the shortest Delaunay edges, which are planar
and non-crossing, so each one closes a real areole. Only `mesh` reproduces the
cohort's loop fraction of ~0.78 at a mean degree of only ~2.5, which is why it
is the calibrated default.

**2. How K_h enters — two paths, both implemented.** Topologically
(`mode="random"` / `"targeted"`), p_c is a property of connectivity alone; this
is the fast engine behind the million-trial reference run. Coupled
(`mode="hydraulic"`), the solver computes vessel tension, vessels past the
cavitation limit embolise and are removed, so K_h genuinely moves the threshold.
Note that ρ means different things in the two: fraction of junctions *removed*
in the topological modes, fraction of junctions *bearing a haustorium* in the
hydraulic one. They are different quantities and are not interchangeable.

**3. Site, not bond, percolation.** `percolation._trial_random` removes
*junctions* (nodes), which is site percolation. The critical behaviour and the
qualitative conclusions are the same as for vessel (bond) removal, but the
numbers are not, and the methods say junctions. Relatedly, `_gcc_size` measures
the largest surviving component anywhere rather than specifically the one still
attached to the root; on networks this reticulated the two coincide, and
`run_robustness.py` measures the threshold as root-invariant, but the code does
not enforce a root check and the methods do not claim it does.

## Document index

The repository root carries the written record as well as the code. Start at the
top of each group.

**Method and results**

| Document | What it holds |
|---|---|
| [ANALYSIS.md](ANALYSIS.md) | Pipeline walkthrough and the data analysis behind each result |
| [PROJECT_DETAILED_WRITEUP.md](PROJECT_DETAILED_WRITEUP.md) | Long-form writeup feeding the paper |
| [MANUSCRIPT_REVISED_SECTIONS.md](MANUSCRIPT_REVISED_SECTIONS.md) | Current manuscript sections |
| [DISCUSSION_REVISED.md](DISCUSSION_REVISED.md), [DISCUSSION_SOP_ALIGNED.md](DISCUSSION_SOP_ALIGNED.md) | Discussion drafts; the SOP-aligned one is the later |
| [STATISTICAL_ANALYSIS_REWRITE.md](STATISTICAL_ANALYSIS_REWRITE.md) | Replacement statistics section |
| [SUPPLEMENTARY_TABLES.md](SUPPLEMENTARY_TABLES.md) | Tables S1–S5, generated from the archived JSON |
| [ROBUSTNESS_CEILING_DISCUSSION.md](ROBUSTNESS_CEILING_DISCUSSION.md) | Robustness-ceiling result, framed as hypothesis |

**Verification trail** — read these to check the work rather than to learn it

| Document | What it holds |
|---|---|
| [VALIDATION.md](VALIDATION.md) | Model vs literature, one verdict per claim |
| [SECOND_PASS_AUDIT.md](SECOND_PASS_AUDIT.md) | Second-pass scientific stress test and the repairs it forced |
| [FINAL_RESOLUTION_PASS.md](FINAL_RESOLUTION_PASS.md) | Every open flag and how it was closed |
| [DEEP_RRL_EVIDENCE_PACK.md](DEEP_RRL_EVIDENCE_PACK.md) | Ten-domain literature and evidence pass |
| [DISCUSSION_PATCH_LOG.md](DISCUSSION_PATCH_LOG.md) | Corrections applied to the Discussion, itemised |
| [SOFTWARE_LOGBOOK.md](SOFTWARE_LOGBOOK.md) | Chronological build record, newest entry first |
| [rrl/](rrl/) | The literature review itself, one file per domain (A–J) |

**References and briefing**

| Document | What it holds |
|---|---|
| [REFERENCES_RESULTS_DISCUSSION.md](REFERENCES_RESULTS_DISCUSSION.md) | Reference list for Results and Discussion |
| [REFERENCES_PARASITES.md](REFERENCES_PARASITES.md) | References behind the parasite profiles |
| [VALIDATOR_BRIEF.md](VALIDATOR_BRIEF.md), [BIOPHYSICIST_ONE_PAGER.md](BIOPHYSICIST_ONE_PAGER.md) | One-page briefs for external validators |
| [PROPOSAL_DEFENSE.md](PROPOSAL_DEFENSE.md) | Proposal defence deck |
| [HANDOFF.md](HANDOFF.md), [HANDOFF_FOR_PROCEDURES.md](HANDOFF_FOR_PROCEDURES.md) | Project state and methods handoff notes |

## Data sources and attribution

The venation networks, the measured hydraulics tables in `hydraulics/` and the R
code in `Rscripts/` are **not our data**. They come from:

> Matos, I. S., et al. (2024). *UCBG venation form data.* Dryad.
> `https://doi.org/10.5061/dryad.1g1jwsv36`

Check the licence terms on that Dryad landing page before redistributing any of
it; the copies vendored here are included so the analysis can be re-run, and
carry whatever terms the deposit sets. Cite the deposit, not this repository, for
anything measured from those leaves.

Our own contributions are the modelling code (`config.py`, `holoparasitic/`,
`scripts/`, `tests/`), everything generated into `data/` and `figures/`, and the
photographs and measurements in `empirical/`.

## Reproducibility

Every random draw goes through `config.new_rng(seed)` and every seed lives in
`config.py`, so the same configuration produces the same figures. Long runs
(`run_cohort_suggested.py`, `run_synthetic_grid.py`, `run_kleaf_validate.py`)
append to their CSV incrementally and skip completed rows, so an interrupted run
resumes rather than restarting.

Two archived artifacts are **superseded** and labelled as such rather than
deleted, because earlier drafts quote them: the `pc_vs_D` and `pc_surface` arrays
inside `data/results.npz` were computed on the legacy `knn` generator (⟨k⟩
4.4–7.0, far above anything empirical). `data/csv/README.md` sets out exactly why
and what replaced them. `sweep._network_for_reticulation` still forces `knn`
mode on purpose, so those legacy figures remain reproducible.
