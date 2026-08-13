# Biophysicist Validator — one page

**What to validate:** that the physics is correct, dimensionally consistent, numerically sound, and that
the topological reduction is justified.

## The model in six lines
1. **Graph.** Nodes = vein junctions (positions from data); edges = vein segments carrying radius r and
   length L.
2. **Conductance.** Each edge g = k·r⁴/L (Hagen–Poiseuille; exact analytical solution of laminar flow in
   a cylinder — not an approximation at the network scale).
3. **Steady-state solve.** Kirchhoff current law at every free node → sparse linear system
   **A ψ = b**, with A = L (conductance Laplacian) + diag(h) for haustorial leaks (`hydraulics.py`).
4. **Boundary conditions.** Dirichlet: source (root/widest basal vein) ψ = 0; terminal veins ψ = −1 MPa
   (transpirational pull).
5. **Parasite.** A haustorium adds a leak conductance K_h from a host node to a reservoir at
   ψ_parasite = −3 MPa; extracted flux = K_h·(ψ_host − ψ_parasite).
6. **Coupling → topology.** A vessel whose tension passes the cavitation threshold (ψ < −2 MPa)
   embolizes and is removed; repeated removal makes network failure a **percolation** question.
   p_c is estimated by a Monte-Carlo sweep + logistic fit (`percolation.py`).

## Checks to run
- **Dimensions.** Confirm g ∝ r⁴/L, flux Q = g·Δψ, and the Laplacian assembly are dimensionally consistent.
- **Independent physics validation (already done).** Our per-edge resistance L/r⁴ reproduces Matos'
  own `Resistance_4` column on **119 leaves / 5.67 M veins**, CV ~1e-7 → `data/hydraulic_validation.json`.
  This is the strongest single check that the hydraulics are implemented correctly.
- **Solver soundness.** A is SPD-ish with a small grounding term (1e-12) to stay non-singular if a
  subcomponent detaches; confirm this doesn't bias ψ.
- **Percolation definition.** It is **site** (node) percolation; GCC = largest connected component.
  Confirm these choices are stated and that p_c is robust to them (see `run_robustness.py`).
- **p_c estimation.** Logistic inflection (P = 0.5) with an empirical-crossing fallback and bootstrap CI;
  confirm the fit is well-posed and the CI is honest.

## Limitations to confirm are disclosed (not to "fix")
- **K_h is a swept free parameter** (no measured haustorial conductance exists that we could find).
- **2-D, steady-state, planar** network; **D ceiling ~1.81** in the generator.
- The r⁴ law assumes ideal cylindrical laminar flow (no tapering, pit resistance, or turbulence) — a
  standard and defensible idealization at this scale, but state it.

## Bottom line for the validator
The question is not "is a leaf really a circuit of pipes?" (it is idealized) but **"given that
idealization, is the physics implemented correctly and are the conclusions robust to the modeling
choices?"** The exact match to the source data's own resistance column is the key evidence that it is.
