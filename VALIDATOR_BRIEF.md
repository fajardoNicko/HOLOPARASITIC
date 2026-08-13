# Research Validator Brief — one page

**Study.** *Percolation Analysis of Pre-Symptomatic Giant-Component Collapse in Host Xylem Networks
Driven by Holoparasitic Haustorial Sink Dynamics.* We model a leaf's vein network as a graph of
Hagen–Poiseuille resistors, solve the steady-state water-potential field (Kirchhoff's law), attach a
holoparasitic sink (a haustorium modeled as a leak conductance K_h to a low-potential reservoir), and
ask at what fraction of disabled vessels the network's giant connected component collapses — the
percolation threshold p_c. Real networks come from the Matos et al. (2024) 122-species deposit; a
calibrated synthetic generator provides a controlled complement.

## Who should validate, and what each checks
| Validator | Checks |
|---|---|
| **Plant physiologist / hydraulic biologist** | Are the ψ boundary conditions, cavitation threshold, and the haustorium-as-sink abstraction biologically defensible? Is "giant-component collapse" a meaningful proxy for hydraulic failure? Is the parasite biology (Cuscuta, holo vs hemi) represented fairly? |
| **Biophysicist / network scientist** | Is the physics dimensionally and mathematically correct (r⁴/L conductance, Laplacian solve, site percolation, p_c estimation)? See `BIOPHYSICIST_ONE_PAGER.md`. |
| **Statistician** | Are the p_c estimation (logistic + bootstrap), the ⟨k⟩/D partial-correlation and OLS/VIF analysis, and the nonparametric group tests appropriate for bounded, skewed, small-n data? |

## The claims most worth scrutinizing (we want these challenged)
1. **A haustorium ≈ a leak conductance K_h to a fixed low reservoir.** K_h is *swept*, not fitted — no
   published haustorial conductance value was found (supported, not proven; see `RESEARCH_FINDINGS_VERIFIED.md`).
2. **Vein conductance ∝ r⁴/L.** Exact for laminar pipe flow; we verified our per-edge resistance matches
   Matos' own `Resistance_4` column on 5.67 M veins (CV ~1e-7) — an independent check of the physics.
3. **Connectivity collapse is pre-symptomatic.** The topological threshold is argued to precede visible
   wilting; this is a modeling claim, not yet measured in planta.
4. **The Matos species are representative venation, not literal Cuscuta hosts** (except where documented,
   e.g. *Camellia sinensis*). The study is about architecture, not a host-range survey.

## Disclosed limitations a validator should confirm are stated, not hidden
- **Site (node) percolation**, not bond — removing a junction removes its incident vessels.
- **GCC = largest connected component**, root-connectivity not separately enforced (safe in a rooted tree).
- **D ceiling ~1.81** — the tree-based generator can't reach the densest ~22% of real leaves; matching
  them needs an optimization-based layout (Ronellenfitsch & Katifori), stated as future work.
- **2-D planar model**; steady-state (no diurnal transients); single-parasite focus.

## A validator should be able to answer YES to:
- Is the physics correct and dimensionally consistent?
- Are the boundary conditions and thresholds biologically reasonable (or reasonably swept)?
- Are the statistical inferences appropriate for the data?
- Are the limitations disclosed and not overclaimed (esp. the novelty framing and K_h)?
