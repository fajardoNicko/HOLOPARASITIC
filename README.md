# Holoparasitic Vascular Percolation Study

Computational biophysics model of *Cuscuta campestris* (dodder) haustorial sink
dynamics and the **Vascular Percolation Threshold p_c** of a host plant's
hydraulic network — the point of irreversible network fragmentation, proposed as
a *pre-symptomatic* intervention metric (collapse precedes visible wilting).

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

3. **Random vs targeted removal.** `mode="targeted"` removes hubs first
   (Albert–Barabási attack); comparing it to random is itself a result.

### The D axis

`D` is swept at **constant network size N** by varying the anastomosis (vein)
density (`NetworkParams.reticulation`) and *measuring* the box-counting
dimension of each network — denser venation → more space-filling → higher `D`
(≈1.25–1.51 at N=1023). As in real leaf venation, denser networks are also
better connected, so mean degree co-varies; a `length_ratio` sweep at fixed
connectivity is the documented geometric control. Box-counting fits the genuine
scaling regime (a fixed window of box sizes), not the finite-size-saturated
coarse boxes.

## Outputs

`figures/` — `network.png`, `sigmoid.png` (hero), `pc_heatmap.png`,
`collapse_montage.png`, `collapse.gif`.
`data/` — `results.npz`, `summary.json` (reproducible numbers for the paper).

## Reproducibility

Every random draw flows through `config.new_rng(seed)`; all seeds live in
`config.py`. Same config in → same figures out.
