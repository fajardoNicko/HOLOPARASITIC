# Holoparasite-Induced Vascular Percolation Study

Computational biophysics model of **holoparasitic** haustorial sink strength and
the **Vascular Percolation Threshold p_c** of a host plant's hydraulic network —
the point of irreversible network fragmentation, proposed as a *pre-symptomatic*
intervention metric (collapse precedes visible wilting). Focused on holoparasites
(*Cuscuta* stem, *Orobanche* root, *Pilostyles* endophytic; calibrated on *Cuscuta
campestris*), with hemiparasites (*Striga*, mistletoe) kept as a comparison.

## What it does

```
Murray's-law reticulate network  ──►  box-counting fractal dimension D
        │                                       │
        ▼                                       ▼
 Kirchhoff flow solver (Ax=b)            Monte Carlo node removal
 + haustorial sink K_h                   ──► Giant Connected Component
        │                                       │
        └───────────────►  embolism  ───────────┤
                                                 ▼
                              logistic regression ──► p_c
                                                 │
                              sweep K_h × D ──►  p_c surface
```

## Quick start

```powershell
# install the pinned stack
C:\laragon\bin\python\python-3.13\python.exe -m pip install -r requirements.txt

# fast end-to-end demo (~seconds) — writes figures\
C:\laragon\bin\python\python-3.13\python.exe scripts\run_demo.py

# smoke tests
C:\laragon\bin\python\python-3.13\python.exe tests\test_smoke.py

# full paper run: 1,000,000 trials + all figures (~11 min on the i5-8265U)
C:\laragon\bin\python\python-3.13\python.exe scripts\run_full.py
# lighter pass:
C:\laragon\bin\python\python-3.13\python.exe scripts\run_full.py 100000
```

## Module map (and who owns what)

| File | Owner | Role |
|------|-------|------|
| `config.py` | D | **Frozen** shared config + network data-structure contract |
| `holoparasitic/network.py` | A | Reticulate Murray's-law generator, CSR conversion |
| `holoparasitic/fractal.py` | A | Box-counting fractal dimension D |
| `holoparasitic/hydraulics.py` | B | Sparse Kirchhoff solver + haustorial sink K_h, cavitation |
| `holoparasitic/percolation.py` | C | Monte Carlo GCC collapse + logistic-regression p_c |
| `holoparasitic/sweep.py` | D | p_c-vs-D and the (K_h, D) p_c surface |
| `holoparasitic/viz.py` | C/D | Network plot, **hero sigmoid**, heatmap, collapse animation |
| `scripts/run_demo.py`, `run_full.py` | D | End-to-end drivers |

## The three modeling decisions (baked into the data structure)

1. **Reticulation.** The generator emits a *reticulate* network (tree +
   anastomoses), not a pure dendrite. A strict tree has no redundant paths and
   therefore no sharp percolation transition — the hero sigmoid would not exist.
   Controlled by `NetworkParams.reticulation`.

2. **How K_h enters.** Two honest paths, both implemented:
   - *Topological* (`mode="random"` / `"targeted"`): p_c is a property of the
     network's connectivity (depends on D). This is the fast 1e6-trial engine.
   - *Coupled* (`mode="hydraulic"`): the flow solver computes vessel tension;
     vessels past the cavitation limit embolise and are removed, so **K_h
     genuinely shifts p_c**. This fills the (K_h, D) surface.

3. **Random vs targeted removal.** `mode="targeted"` removes the highest-
   **betweenness** vessels first — the stem/major-vein backbone, the true
   structurally-critical nodes in a vascular tree (`p_c ≈ 0.18` vs `0.28`
   random). Targeting by raw *degree* is weaker than random (`0.31`), because the
   high-degree nodes are the redundant reticulated periphery — a result in itself.

### The D axis

`D` is swept at **constant network size N** by varying the anastomosis (vein)
density (`NetworkParams.reticulation`) and *measuring* the box-counting
dimension of each network — denser venation → more space-filling → higher `D`
(≈1.35–1.48 across the sweep; hero network D ≈ 1.43, inside the measured
*Relbunium* leaf-venation range 1.39–1.76). As in real leaf venation, denser
networks are also better connected, so mean degree co-varies (~6.0 at the
default). Box-counting fits the genuine scaling regime (a fixed window of box
sizes), not the finite-size-saturated coarse boxes.

## Outputs

`figures/` — `network.png`, `sigmoid.png` (hero), `pc_heatmap.png`,
`collapse_montage.png`, `collapse.gif`.
`data/` — `results.npz`, `summary.json` (reproducible numbers for the paper).

## Reproducibility

Every random draw flows through `config.new_rng(seed)`; all seeds live in
`config.py`. Same config in → same figures out.
