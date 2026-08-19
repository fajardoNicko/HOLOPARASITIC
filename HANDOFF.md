# HANDOFF — state of the project

**Last updated 2026-08-16.** Supersedes the previous handoff (2026-08-09). Software build and analysis
are complete; the project is now in the manuscript-writing phase.

---

## Where things stand

Three review passes ran on 2026-08-15, in order. Each has a standalone deliverable, and each is the
authority for the one after it.

| Pass | Deliverable | What it settles |
|---|---|---|
| 1. Deep RRL + results mining | `DEEP_RRL_EVIDENCE_PACK.md` + `rrl/A…J` (~130 carded sources) | Literature base, evidence matrix, novelty audit, paragraph architecture |
| 2. Scientific stress test | `SECOND_PASS_AUDIT.md` (Parts I–XIV) | Risk assessment, confounds, claim classification, DO-NOT-CLAIM list |
| 3. Final resolution | `FINAL_RESOLUTION_PASS.md` (§§2–15) | Every open flag closed; title decision; writing handoff |
| — Manuscript revision | `MANUSCRIPT_REVISED_SECTIONS.md` + `.docx` | Revised Introduction, Methods, Results |

**`FINAL_RESOLUTION_PASS.md` is the authoritative source** for corrections, terminology, and claim
strength. `MANUSCRIPT_REVISED_SECTIONS.md` is the drafted text built from it.

## The five things that changed the paper

1. **p_c is topological, not hydraulic.** `network.to_csr` returns an unweighted int8 adjacency and
   `percolation.py` never reads a conductance, radius or potential. "Hydraulic collapse" is not what
   the headline measures — and no radius-inference or Murray's-law objection can touch p_c.
2. **The haustorial sink is decoupled.** It contributes ΔΨ = −0.026 MPa; reaching the modelled −2.0 MPa
   threshold needs a ~6.0 MPa gradient against a ≈0.5 MPa largest measured value. 97.4% of the reported
   "margin" is the stipulated `PSI_LEAF − PSI_CAVITATION` gap. Report threshold-independently.
3. **The reticulation result is scope-limited to dispersed damage.** Localised lesions are 2.3–2.5×
   *less* damaging (100/100 networks, zero exceptions), but connectivity stops predicting tolerance
   under them (ρ = −.000 and .151, n.s., against .737 dispersed). This must be stated, not buried.
4. **Two first-pass claims were wrong and were corrected in pass 2** — the loop-fraction "graph
   identity" (it is empirical, not algebraic) and the "targeted attack" framing (removal is weighted-
   stochastic, so the betweenness threshold 0.1889 nominal is 0.1498 realised).
5. **The pre-symptomatic section is cut** from Results and Conclusion; retained only as literature
   framing in the Introduction. The title was replaced (see `FINAL_RESOLUTION_PASS.md` §10).

## New scripts and data written this session

All reproducible, all reading only the archive or the raw deposit; none re-runs the original pipeline.

```
scripts/make_revised_sections_docx.py            -> MANUSCRIPT_REVISED_SECTIONS.docx
scripts/verify_manuscript_numbers.py             -> (checks the manuscript against the archive)
scripts/run_rrl_diagnostics.py                   -> data/rrl_diagnostics.json
scripts/run_cavitation_sensitivity.py            -> data/cavitation_sensitivity.json
scripts/run_graph_metric_audit.py                -> data/graph_metric_audit.json
scripts/run_second_pass_audit.py                 -> data/second_pass_audit.json
scripts/run_resistance_convention_sensitivity.py -> data/resistance_convention_sensitivity.{csv,json}
scripts/run_criterion_and_locality.py            -> data/criterion_and_locality.{csv,json}
scripts/run_final_resolution_checks.py           -> data/final_resolution_checks.json
```

`run_criterion_and_locality.py` is **complete at 100 of 100** cohort networks, and both deliverables
carry the final n = 100 figures. The re-implementation reproduces the archived cohort at Spearman
0.9988 with an identical median (0.1998 vs 0.1998). Values were stable to three decimals across
n = 75 / 85 / 97 / 99 / 100.

`MANUSCRIPT_REVISED_SECTIONS.docx` is generated from the markdown by
`scripts/make_revised_sections_docx.py` — 17 tables and all 14 figures embedded, APA caption layout
(label, italic title, image, note). The markdown is the source of truth; re-run the script after any
edit rather than editing the .docx by hand.

**Citation integrity.** The first draft of the revised sections lost citations during restructuring:
several claims the evidence pack supports were left uncited, and Sack et al. (2008), Brodribb et al.
(2016), Scoffoni et al. (2017), Nardini et al. (2012), Ronellenfitsch and Katifori (2019), Balios et al.
(2025) and Griebel et al. (2022) were missing from the body. All are now restored — the body carries 51
distinct first authors, up from 34 — and three deliberate removals (Dawson & Ehleringer 1993,
Wolitzky 2022, StatPearls) are documented with reasons at the end of the markdown rather than left
silent.

**Number provenance.** `scripts/verify_manuscript_numbers.py` checks 42 reported statistics against the
archived JSON files, never against a previous manuscript version. It currently passes 42/42. Run it
after any manuscript edit or analysis rerun. Note that interim values seen during the cohort run
(e.g. medians of 0.1950 / 0.1967 / 0.1997) were partial-cohort snapshots — leaves were processed
smallest-first, so any snapshot is biased toward small networks. **Only the n = 100 values are
canonical**, and no deliverable now carries an interim value.

**No processes are running.**

## What to do next

**Immediate, before any further writing**

1. Merge `MANUSCRIPT_REVISED_SECTIONS.docx` into the main manuscript. It **supersedes**
   `Chapter_I_REVISED.docx` (Introduction), `Methodology.docx` (Methods) and `RESULTS_REVISED.docx`
   (Results). Do not regenerate those three from their old scripts — those scripts emit the
   pre-revision text. Note the figure crosswalk at the top of the markdown: figures renumber to 2–14
   because Figure 1 is the Methods pipeline figure.
2. Fix the reference list — the corrections are listed at the end of `MANUSCRIPT_REVISED_SECTIONS.md`
   and in `SECOND_PASS_AUDIT.md` Part VIII. The two Matos et al. (2024) papers must be cited
   separately (*Ecology* 105:e4436 for the dataset, *New Phytologist* 244:407 for the analysis).
3. Rewrite the Discussion and Conclusion. The 14-paragraph blueprint is in `SECOND_PASS_AUDIT.md`
   Part XI; add a localised-damage paragraph and a criterion-robustness sentence.

**Optional, none blocking** (`FINAL_RESOLUTION_PASS.md` §15L)

- Raise `sample_cap` in `percolation.bootstrap_pc` from 50,000 to `n` and re-report the CIs; they are
  currently conservative by ~1.6× (100k runs) and ~4.5× (1M run).
- Pagel's λ on the regression residuals via V.PhyloMaker (~1 h). A λ ≈ 0 result would *justify* the
  OLS already reported.
- ε² for the non-significant grade comparison, only if a reviewer asks.

**One decision left to you.** Whether to lead the paper on the structural result (safest, best
supported) or on the sink decoupling (more novel, but a negative result). The selected title
accommodates either.

## Things not to re-litigate

`FINAL_RESOLUTION_PASS.md` §13 classifies 16 claims A–E and §12 fixes the controlled vocabulary;
`SECOND_PASS_AUDIT.md` Part XIII is the 24-item DO-NOT-CLAIM list. Read those before writing any new
sentence about p_c, the sink, validation, or novelty. In particular: say **verified** not *validated*
for the resistance-column check, **critical removed fraction / f₅₀** not *hydraulic collapse threshold*,
and **weighted removal** not *attack*.

## Reproduction order (unchanged from the original build)

```
python scripts/build_analysis_master.py
python scripts/run_targeted_ci.py
python scripts/run_sink_surface.py
python scripts/run_finite_size_fixedD.py
python scripts/run_dynamics.py
python scripts/export_csv.py
python scripts/make_appendix_computations.py
python scripts/make_results_docx.py
python scripts/patch_discussion_docx.py
```

Review-pass scripts are independent of the above and can be run in any order.
