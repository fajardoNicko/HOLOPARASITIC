"""
holoparasitic — computational biophysics model of holoparasitic (Cuscuta)
sink dynamics and the vascular percolation threshold p_c of host plants.

Sub-modules
    network      reticulate Murray's-law hydraulic network generator (Person A)
    fractal      box-counting fractal dimension D                      (Person A)
    hydraulics   Kirchhoff sparse Ax=b flow solver + haustorial sink   (Person B)
    percolation  Monte Carlo GCC collapse + logistic-regression p_c    (Person C)
    sweep        K_h x D parameter sweep -> p_c surface                (Person D)
    viz          network plot, GCC sigmoid hero figure, p_c heatmap
"""

__version__ = "0.1.0"

from . import network, fractal, hydraulics, percolation, sweep, viz  # noqa: F401
