# HANDOFF — state of the project

**Last updated 2026-11-01.** Supersedes the previous handoff (2026-08-16). Software build and analysis
are complete; the project is in the manuscript-writing phase.

## 2026-11-01 addendum — SRC analysis fixes DONE (timeline tasks 10–12)

Every paused run from 10/25 was finished on 10/31–11/01. **No processes are running.** The report for Nicko
is `SRC_ANALYSIS_FIXES.md`: results, corrected numbers and a page-by-page map of where each change goes in
the submitted paper. Nicko inserts the changes and rewrites the text himself.

**Results:**
- **Enhancement crossings.** 5,738 of 606,351 added veins (0.95%) crossed a traced vein. The crossing-filtered
  rerun gave the same 93/12/0 and median Δ 0.0096; the largest change in any enhanced p_c was 0.0009
  (`data/planarity_check.json`).
- **Graph planarity.** 61 of 105 traced networks are already non-planar graphs. The original enhancement made
  40 of the 44 planar ones non-planar; the filtered one made 11 (`data/graph_planarity.json`).
- **Placement control (n = 27).** Random-order Delaunay still beats shortest-first in 26/27, by 3.3× instead
  of 3.7× (`data/planar_edge_control.json`).
- **Collapse criterion 10–90% (n = 100).** The mean-degree association holds everywhere (ρ .70–.87). The
  fractal-dimension association is criterion-dependent (not significant at 10–20%). Degree-weighted removal
  is lower than uniform in 100/100 up to 50%. Data: `data/threshold_sensitivity.json`; figure
  `figures/threshold_sensitivity.png`.
- **Uncapped Table 4 CIs** are 1.5–4.7× narrower (`data/uncapped_ci.json`). The seed-replicate SD of p_c is
  ≤ 0.003 at 2,400 trials (`data/mc_uncertainty.json`). The p. 24 SEs should be 0.065/0.032, not 0.0102/0.0050.
- **Table S3 regenerated** in `SUPPLEMENTARY_TABLES.md/.docx`: p-value formatter bug, double rounding,
  cubic fit now n = 100, uncapped bootstrap block.

**Not done (offered):** the Appendix C generator (`scripts/_appendix_c_part*.py`) still has the old SE values,
the cap paragraph and "planar" sentences, and Appendix B Table B9 has not been regenerated. The 10/25
addendum below is kept as history; its "paused" table is superseded.

## 2026-10-30 addendum — Claude context vault built (no research work this session)

Nicko asked for an Obsidian vault Claude can use as its context pool. It lives in `context-vault/`, which is
gitignored and local only. Nothing in the research code, data or manuscript changed. The SRC runs below are
still paused exactly as on 10/25, and **no processes are running.**

**What exists:**
- 29 notes: `00 START HERE.md` (hub and routing table) plus 28 topic notes in `01 Project` through `08 Defense`.
- Every fact line carries a source pointer: `@file:Lx`, `@json:file#key`, `@rows:file.csv`, `@git:sha` or `@mem:file`.
- `context-vault/_meta/verify_vault.py` machine-checks each pointer. Last run: 3,594 citations, 4,551 numbers,
  171 quotes, 1,259 paths and 184 function references, with **0 failures** and no broken links. It reads
  .xlsx/.docx/.pdf too. The output is `_meta/Verification Report.md`, which includes an inventory of every note.
- Rules for adding notes: `_meta/Conventions.md` and `_meta/Writer Brief.md`, which also holds the note ownership map.

**Not done:**
- The independent meaning check (does each sentence say what its source says?) was started and then stopped
  before any edits. The mechanical check covers numbers, quotes, paths and names only.
- The `--accept` hash snapshot has not been taken, so source-change tracking is off until it is.

**Tomorrow, per Nicko's decision:** rewrite the vault so it keeps **only what is relevant to the current
paper**. Old and superseded repo files should not be carried in it. Nicko already knows those files are old,
so the vault should not keep flagging them as STALE-IN-SOURCE. Steps:
1. Propose a keep/drop list of source files to Nicko (current manuscript, data/scripts it uses, references,
   SRC compliance, forms), drop or trim the superseded material (old drafts, superseded docs, stale defense
   answers, legacy knn artifacts), and get a yes before cutting.
2. Prune the affected notes (Document Registry, QA Index, Timeline, Validation & Robustness and Citation Issues
   carry the most legacy rows) and update `00 START HERE.md` and the ownership map.
3. Re-run `verify_vault.py`, run the meaning check on what remains, then run `--accept`.

```
C:\laragon\bin\python\python-3.13\python.exe context-vault\_meta\verify_vault.py            # check all
C:\laragon\bin\python\python-3.13\python.exe context-vault\_meta\verify_vault.py --note "<path>"
C:\laragon\bin\python\python-3.13\python.exe context-vault\_meta\verify_vault.py --accept   # snapshot
```

**Found while building it, to act on only if Nicko wants:**
- `ISEF_FORMS_2026-27/DATES_AND_CONSISTENCY_CHECK.md` now reports 35/36 checks passing (Form 1 item 4 vs
  Form 1A item 7). It was 34/34 on 10/13.
- `empirical/` holds templates only, with no own-leaf data, so the SRC local-leaf validation has not started.
- `data/graph_planarity.csv` has 56 rows, against 55 in the table below.

**Git:** this session only changed `.gitignore` (one appended line ignoring `context-vault/`) and this file.
Nothing was committed.

## 2026-10-25 addendum — SRC "Major Compliance" analysis fixes (PAUSED overnight)

The Regional SRC returned both reviews "For Major Compliance" (PDF in Downloads). The finish target is
11/20 (`SRC_COMPLIANCE_TIMELINE.xlsx`). Nicko asked Claude to do the "Analysis fixes" rows of that timeline,
then report everything and say where each result goes in the paper. He paused all runs on the evening of
10/25, to continue the next day. **No processes are running.**

**Done:**
- The planarity bug is confirmed. `make_real_suggested.py::add_loops` adds Delaunay non-edges without checking
  whether they cross traced veins. In 3 test leaves, 0.4–1.2% of added edges crossed a vein, and the
  unfiltered enhancement made some planar leaf graphs non-planar.
- `scripts/run_synthetic_planarity.py` → `data/synthetic_planarity.json` (**complete**). The synthetic
  reference network and all 42 grid networks are NOT planar graphs (`check_planarity` False). 91–99% of their
  tree edges cross another edge, so "calibrated planar mesh" in the paper is wrong.

**New code:**
- `holoparasitic/planarity.py`: crossing counts and `add_loops_planar`, the crossing-filtered enhancement.
- `percolation.find_pc_multi`: p_c at several collapse fractions from one sweep. It reproduces `find_pc`
  exactly at 0.5 (checked on Tri_lan and Met_dav).

**Paused runs.** All are resumable unless marked; resume with the same command and finished rows are skipped:

| Script | Output | Progress |
|---|---|---|
| `run_planarity_check.py --workers 4` | `data/planarity_check.csv/.json` | 0/105 (the largest leaves run first and were mid-run) |
| `run_threshold_sensitivity.py --workers 2` | `data/threshold_sensitivity.csv/.json` | 2/100 (both reproduce the archive at 50%) |
| `run_graph_planarity.py --workers 1` | `data/graph_planarity.csv/.json` | 55/105 |
| `run_uncapped_ci.py` | `data/uncapped_ci.json` | not resumable, rerun whole (~20–30 min) |
| `run_planar_edge_control.py` | `data/planar_edge_control.csv/.json` | not started (27 networks) |
| `run_mc_uncertainty.py` | `data/mc_uncertainty.json` | not started |

After the planarity run finishes, rerun `run_planarity_check.py --summarize`: its summary code changed
after the run started. A text audit (definitions, trial budgets, the SE formula, Table S3, formulas,
appendix references, hydraulic-diversion wording) was started and stopped before finishing; it needs
redoing. Known text errors so far:
- The SE numbers on printed p. 24 use the total trial count instead of the per-density count.
- Methods p. 19 says betweenness removal was run on small leaves; it was run on the synthetic network only.
- "Planar" claims appear on pp. 13, 15, 18, 21 and 50.

## 2026-10-13 addendum — ISEF forms and logbook (evening)

The adviser asked to hold paper revisions until the Regional SRC comments (SRC entries due 10/21/26) and to
finish the forms, logbook and dates first. `ISEF_FORMS_2026-27/` (gitignored: personal contact data) now holds
the filled 2026-2027 Forms 1, 1A, 1B, 2A (+ attachment), 3, the abstract form, a 52-entry electronic logbook
compiled from commits, reflog, file times and prompt logs, and a 34-check date report (all pass).
`ISEF_FORMS_2026-27/README_SUBMISSION.md` lists every change from the researcher's drafts and five decisions
that are his and the adviser's (07/24 real-leaf work vs the 07/25 start date, real signature dates, Form 2A
people, adviser name, July plan's four proponents). Names and dates live only in `scripts/submission_info.py`.

## 2026-10-13 addendum — design-rules section

`MANUSCRIPT_REVISED_SECTIONS.md` now carries a Results §6 "Empirical Design Rules for a Damage-Tolerant
Venation" (nine rules, Tables 17–18, Figure 15 = `figures/design_rules.png`), a Methods §9 describing
how they were derived, and a Methods §5 "Placement control" paragraph; the former Results §6–§8 are
§7–§9. Everything is reproducible from `scripts/run_design_rules.py` → `data/design_rules.json` and
`scripts/make_design_rules_figure.py`; the docx was regenerated (19 tables, 15 figures). Full detail in
`SOFTWARE_LOGBOOK.md` (2026-10-13 entry). Four open items are left to the author: (1) whether to soften
§8.2's ten-lesion fractal-dimension sentence, which Rule 8 shows is mostly network size; (2) the
Discussion has no paragraph on the rules yet; (3) `verify_manuscript_numbers.py` does not check the §6
numbers; (4) four new references to add (`REFERENCES_RESULTS_DISCUSSION.md` §B.6).

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
