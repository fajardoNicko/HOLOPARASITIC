# Handoff — Holoparasitic Percolation Project
_Written 2026-08-04; updated 2026-08-05 (added Scope & Delimitations; citation fix applied). Nothing is running; working tree has uncommitted changes (see below)._

## Where the project stands
The **spine of the project is now the real-leaf reticulation cohort** (real Matos data), not the
synthetic hero and not the parasite comparison. The haustorial sink is literature-grounded but was found
to be **sub-symptomatic**. The multi-parasite comparison has been **dropped**.

## Scope & Delimitations (agreed — the framing the whole paper rests on)
These are the boundary decisions we settled. State them explicitly in the paper so a panel reads them
as deliberate methodology, not as gaps they extracted.

**THE STUDY USES TWO COMPLEMENTARY METHODS (both must be named in scope):**
- **(i) Percolation lens** — random removal of vein junctions (nodes) → critical threshold p_c. Measures
  the leaf's *structural* robustness to distributed conductive loss. This is the reticulation cohort (the
  HEADLINE): `cohort_suggested.csv`.
- **(ii) Haustorial-sink lens** — the haustorium modelled as a leak conductance K_h draining to a low-ψ
  reservoir → Kirchhoff water-potential solve → embolism check. Measures the *hydraulic* stress of the
  drain itself: `sink_demo.json` / `make_sink_demo.py`.
- The two are **decoupled** (see delimitation 4): the sink is the upstream cause (systemic tension), the
  percolation collapse is the leaf-level consequence. They are two lenses on one host, not one cause→effect.

**THE LOAD-BEARING ONE — what the leaf network represents (adopted framing, "Option A"):**
- Cuscuta attaches to the host **STEM**; Orobanche to **ROOTS**. **Neither attaches to the leaf blade.**
  So removing nodes from a leaf network is **NOT** a picture of the haustorium damaging the leaf.
- The leaf is modelled as the **readout tissue for systemic parasite-induced water stress**, not the
  attachment site. Mechanism: parasite drains the stem → whole-plant water potential drops → leaf
  conduits **cavitate stochastically under the elevated tension** → distributed loss of functional
  conduits → GCC fragments = the pre-symptomatic → symptomatic transition (wilting/chlorosis).
- Therefore **random site percolation is the faithful abstraction**: cavitation under rising tension is
  spatially scattered and stochastic, so random node loss (not targeted) is the correct model.
- This also reconciles the sink finding: the localized haustorial drain **alone** is sub-cavitation
  (§ sink), but the **systemic tension** it contributes to, on top of normal transpiration, is what
  drives the distributed leaf cavitation. Sink = upstream cause; percolation collapse = leaf consequence.
- (Alternative "Option B" — leaf as a generic vascular-network exemplar, parasite merely motivating —
  was considered and NOT adopted; it demotes the parasite and weakens the Life-Sciences framing.)

**Other deliberate delimitations:**
1. **Percolation cohort run in `random` mode only.** The engine still HAS a betweenness-targeted mode
   (`percolation.py`, `mode="targeted"`) — it was not deleted, just not run for the cohort. A raw
   *degree*-targeted attack was never a real mode (the code itself notes it is weaker than random in a
   reticulate network). Random-only is deliberate: it matches the stochastic, distributed cavitation of
   Option A, not a parasite-targeting guess. (Optional future work: re-run in `targeted` mode as a
   worst-case backbone-attack bound.)
2. **Site (junction/node) percolation, not bond (vessel/edge).** Same critical physics; different label.
   (METHODOLOGY.md prose still says "vessels" in one place — pending one-line fix; see Open decisions.)
3. **K_h fixed to a literature-anchored constant** (0.0392), not swept. Trades the p_c-vs-K_h heatmap for
   a grounded single-strength demonstration. **KNOWN LITERATURE GAP (state this):** there is *no published
   holoparasite-specific* "% of host water" or host-parasite gradient measurement. The two calibration
   anchors are both hedged: ~18-20% diversion is a *hemiparasite* floor (Jiang 2003), and the ~1.5 MPa
   gradient is an *illustrative review-level* value (NOT primary, NOT in Kaiser 2015 — corrected 2026-08-08).
   The exact sink magnitude is therefore a **delimitation, not a measured input**; a direct holoparasite
   flux/gradient measurement is named as future work. (The sub-cavitation finding holds at *any* gradient,
   so the conclusion does not depend on the exact value.)
4. **Sink is sub-symptomatic** — the drain alone never ruptures xylem (0 embolism at any gradient). The
   study does **NOT** claim the sink "drives" collapse; hydraulic sink & percolation collapse are
   **decoupled lenses**. (This is why the title's "driven by" overclaims — see Open decisions.)
5. **Reticulation ceiling ⟨k⟩ = 2.811** = the cohort's 90th-percentile mean degree (empirical). "Suggested"
   leaves are never denser than the most-looped real leaves observed — the ceiling is not invented.
6. **10,000 trials/leaf**, not 1,000,000 — a stated accuracy/compute tradeoff (largest leaf = 203,589 nodes).
7. **105 valid whole-leaves**; 15 crop fragments excluded (N < 1000). Headline uses the 105.
8. **Clean-A subset is the conservative claim** — the full-cohort headline is partly inflated by
   missing-vein (grade-B) tracings that look artificially sparse; report both.
9. **Multi-parasite comparison dropped** — old/synthetic; not part of the current study.
10. **Infestation duration in days is illustrative, not calibrated** — the *shape/existence* of the
    pre-symptomatic window is the finding, not its length in days.

## Headline result — real-leaf reticulation cohort
For all **120** real Matos leaves: random-attack p_c on the leaf as traced (CURRENT) vs the same leaf with
shortest Delaunay areole-loops added to its own venation up to ⟨k⟩=2.811 (SUGGESTED), 10,000 trials each.
- **105 valid whole-leaves** (15 crop fragments excluded, N<1000).
- **p_c median 0.201 → 0.215**, Δ **+0.009 median** (mean +0.012, max +0.046), **min +0.000 — 0 leaves worsened**.
- **89% improved**; the rest are already-reticulate leaves with no headroom.
- **HONEST CAVEAT (must report):** clean-A subset (n=21, no vein-miscount) gains less — **+0.007, 62% improved**.
  Missing-vein (B) leaves look artificially sparse and inflate the headline.
- Files: `data/cohort_suggested.csv`, `data/cohort_suggested_summary.json`, `figures/cohort_suggested.png`.

## Haustorial sink — grounded, and its honest finding
- `K_h` is now a literature constant: **`config.K_H_HOLOPARASITE = 0.0392`** — solved for **20% flow diversion**
  (Jiang, Jeschke & Hartung 2003) at a **1.5 MPa gradient** (Kaiser et al. 2015).
- **KEY FINDING: at realistic strength the sink is SUB-cavitation — 0 vessels embolise at ANY gradient.**
  It drains water/carbon but cannot rupture the xylem → the hydraulic sink and the percolation collapse are
  **DECOUPLED lenses**. This supports the "pre-symptomatic" framing; it does NOT show the sink driving collapse.
- Files: `figures/sink_demo.png`, `data/sink_demo.json`, `scripts/make_sink_demo.py`.

## What was done this session
1. `scripts/run_cohort_suggested.py` (new) — the all-120 current-vs-suggested run (ran across two sessions,
   resumed cleanly from row 77; resumable/incremental).
2. `scripts/make_suggested_summary.py` (new) — cohort aggregate + clean-A sensitivity + figure.
3. `scripts/make_sink_demo.py` (new) — literature K_h calibration + demo + `config.K_H_HOLOPARASITE`.
4. `empirical/RELATED_WORK.md` — new "Holoparasite sink strength" section, 4 verified RRLs w/ DOIs.
5. `DATA_SUMMARY.xlsx` rebuilt (`scripts/make_data_summary_xlsx.py`): 4 sheets, reticulation cohort as
   centerpiece, **Parasites sheet dropped**, `parasites.json` flagged deprecated.
6. `SOFTWARE_LOGBOOK.md` — 2026-08-04 entry.
7. Also earlier this session: confirmed the pc_heatmap is current; updated logbook commit-hash headers.

## Open decisions (USER'S CALL — no code touched)
1. **Title.** Drop the "driven by" overclaim (the sink is sub-symptomatic; host structure sets the threshold).
   Recommended minimal fix: *"…Host Xylem Networks **Under Holoparasitic Haustorial Sink Stress**"*.
   Bigger retilt option: lead with *"Venation Reticulation Buffers …"*.
2. **Biology-first framing** (competition category = Life Sciences, individual). Keep percolation as METHOD,
   not subject; lead with parasites / leaf architecture / host resistance / breeding. I OFFERED to draft a
   biology-first outline (abstract + section order + which figures lead) — **not yet done**.
3. **Citation fix still pending in `METHODOLOGY.md`** (lines ~115, 494, 555): replace "Vishnu, M., … *Chaos,
   Solitons & Fractals*" with the verified **Muraleedharan, V., Rajan, S. C., & Jaishanker, R. (2023). *Flora,
   304,* 152300. doi:10.1016/j.flora.2023.152300** and delete the now-moot "could not be verified" caveat.
   (Correction already lives in `empirical/RELATED_WORK.md`; just not applied to the paper.)

## Environment / how to resume
- Interpreter: `C:\laragon\bin\python\python-3.13\python.exe`.
- Re-run the cohort (resumable, skips done leaves): `python scripts/run_cohort_suggested.py`.
- Rebuild summary/figure: `python scripts/make_suggested_summary.py`.
- Rebuild sink demo: `python scripts/make_sink_demo.py`.
- Rebuild workbook: `python scripts/make_data_summary_xlsx.py`.

## Git / state
- Nothing running. Uncommitted working-tree changes: new scripts, `config.py` (added `K_H_HOLOPARASITE`),
  `DATA_SUMMARY.xlsx`, `RELATED_WORK.md`, `SOFTWARE_LOGBOOK.md`, `HANDOFF.md`, and `data/`+`figures/` outputs.
- Nothing has been committed this session — commit when ready.
