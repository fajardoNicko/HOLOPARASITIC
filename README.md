# Percolation Analysis of Vein Reticulation

**A Structural Basis for Damage Tolerance in Leaf Venation Networks under Simulated Vascular Damage**

[![Overall Champion — Life Science, Division STF](https://img.shields.io/badge/%F0%9F%A5%87%20Overall%20Champion-Life%20Science%20%C2%B7%20Division%20STF%202026-gold?style=for-the-badge)](#)
[![1st Place — Life Science Individual, Division STF](https://img.shields.io/badge/%F0%9F%8F%86%201st%20Place-Life%20Science%20Individual%20%C2%B7%20Division%20STF%202026-gold?style=for-the-badge)](#)
[![1st Place — District STF](https://img.shields.io/badge/%F0%9F%8F%86%201st%20Place-District%20STF%202026-%23b8860b?style=for-the-badge)](#)

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square)
![Species](https://img.shields.io/badge/real%20networks-100%20species-brightgreen?style=flat-square)
![Reproducible](https://img.shields.io/badge/seeds-fully%20pinned-lightgrey?style=flat-square)

This program measures how much vein loss a leaf venation network can take before it breaks apart.
Each traced network becomes a graph (junctions = nodes, vein segments = edges). A Monte Carlo
simulation removes junctions and records when the largest connected component falls below half of
its original size. The critical removed fraction **p_c** is where half of the trials collapse.
A hydraulic solver (Kirchhoff flow on the same graph) adds a haustorial sink as a separate test.

## Main results

| Result | Value | Networks |
|---|---|---|
| Median p_c, uniform removal | 0.1998 | 100 |
| Median p_c, degree-weighted removal (lower in every network) | 0.1685 | 100 |
| Mean degree vs p_c (holds at every collapse criterion, 10–90%) | ρ = .73 (.70–.87) | 100 |
| Adding loops to a network's own junctions raised p_c | 93 improved, 12 already above the ceiling | 105 |
| Localized lesions vs dispersed loss | 2.3–2.5× more removal needed | 100 |
| Haustorial sink taking 20% of inflow | minimum ψ −0.996 → −1.022 MPa; no vessel below −2.0 MPa | reference network |

The numbers come from the files in `data/`; the figures are in `figures/`.

## Layout

```
config.py        constants, default parameters, random seeds, graph schema
holoparasitic/   the library: network generator, leaf loader, percolation, hydraulics, fractal dimension
scripts/         runnable drivers (run_*.py compute results; make_*.py draw figures)
tests/           smoke tests
data/            all computed results (CSV, JSON, NPZ)
figures/         all result figures
empirical/       templates for locally measured leaves
hydraulics/      measured leaf conductance table from the Matos deposit (read by run_kleaf_validate.py)
```

## Run it

```powershell
python -m pip install -r requirements.txt
python tests\test_smoke.py           # quick checks, a few seconds
python scripts\run_demo.py           # end-to-end demo, seconds
python scripts\run_full.py           # reference run, 1,000,000 trials (~11 min)
```

Scripts that use real leaves need the Matos et al. deposit unzipped into
`UCBG_venation_form_data/` (about 4.4 GB, not included):

```
python scripts\run_characterize.py
python scripts\build_cohort.py
python scripts\run_cohort_percolation.py
```

Every random draw goes through `config.new_rng(seed)`, so the same settings give the same results.

## Data

The venation networks and the measured hydraulics table are not ours. They come from:

> Matos, I. S., et al. (2024). *Leaf architecture and functional traits for 122 species at the
> University of California at Berkeley botanical garden* [Data set]. Dryad.
> https://doi.org/10.5061/dryad.1g1jwsv36

Cite the deposit for anything measured from those leaves.

---

<sub>Nicko Fajardo · Valenzuela City School of Mathematics and Science</sub>
