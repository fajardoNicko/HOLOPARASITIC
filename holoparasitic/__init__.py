"""
holoparasitic — the modelling library behind the vascular percolation study.

Two families of network reach the same physics engine, which is the point of the
design: a real traced leaf and a synthetic generated one are the same
`networkx.Graph` contract (see config.py), so every measurement below is defined
identically on both.

Network sources
    network      synthetic reticulate Murray's-law generator ('knn' or 'mesh')
    realleaf     loader for a traced Matos et al. (2024) leaf venation network
    metadata     that dataset's own per-leaf extraction-quality record

Measurement
    fractal      box-counting fractal dimension D (shared by graphs and images)
    hydraulics   Kirchhoff sparse Ax=b flow solver + haustorial sink K_h
    percolation  Monte Carlo giant-component collapse + logistic-regression p_c
    characterize full architectural/hydraulic profile + the validity screen
    boundary     cropping-artifact test for the windowed source networks
    dynamics     logistic haustorial load rho(t) and the pre-symptomatic window

Calibration and sweeps
    calibrate    measure branching geometry from real leaves; fit the generator
    matos_summary  read the metrics Matos et al. precomputed, as a cross-check
    sweep        p_c vs D and the coupled (K_h, D) threshold surface

Output
    viz          network plot, collapse sigmoid, p_c heatmap, collapse animation

Drivers live in scripts/ (see scripts/README.md); they import from here and
write to data/ and figures/.
"""

__version__ = "1.0.0"

from . import (network, fractal, hydraulics, percolation, sweep, viz,
               realleaf, characterize, calibrate, boundary, metadata,
               matos_summary, dynamics)  # noqa: F401
