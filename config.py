"""
config.py — central, FROZEN configuration for the Holoparasitic Vascular
Percolation Study.

Everything the four sub-modules share lives here so that Person D can freeze it
in Week 1 and A/B/C build against a stable contract.

----------------------------------------------------------------------------
FROZEN NETWORK DATA STRUCTURE  (agreed Week 1 — do not change silently)
----------------------------------------------------------------------------
The single object passed between every module is a `networkx.Graph` named `G`.

Node attributes
    pos      : tuple(float, float)   2-D coordinates (normalised units)
    gen      : int                   generation / depth in the branch hierarchy
                                     (0 = root at the stem base)
    radius   : float                 vessel radius feeding this node (norm. units)
    kind     : str                   'root' | 'internal' | 'terminal'
                                     terminal = leaf / transpiration site

Edge attributes
    radius      : float   vessel radius            (normalised, r0 = 1.0)
    length      : float   vessel length            (normalised)
    resistance  : float   Hagen-Poiseuille R = 8 eta L / (pi r^4)
    conductance : float   g = 1 / resistance       (normalised, used by solver)
    kind        : str     'axial'        = Murray bifurcation edge
                          'anastomosis'  = reticulation cross-link (loop)

Helper `network.to_csr(G)` converts G -> scipy CSR adjacency ONCE; the Monte
Carlo hot loop then works purely on integer-indexed sparse matrices and never
touches NetworkX (this is what makes 1e6 trials feasible — see the brief).
----------------------------------------------------------------------------
"""

from dataclasses import dataclass, field
import numpy as np


# ----------------------------------------------------------------------------
# Physical constants (SI).  The solver works in NORMALISED conductance units
# (g = r^4 / L, r0 = 1) to stay well-conditioned across generations; the real
# Hagen-Poiseuille resistance is still stored on every edge for the paper.
# ----------------------------------------------------------------------------
ETA = 1.002e-3          # dynamic viscosity of water at 20 C  [Pa.s]

# Water-potential boundary conditions [MPa]  (xylem tensions are negative)
PSI_SOURCE = 0.0        # stem base / soil interface (reference)
PSI_LEAF = -1.0         # transpirational pull at terminal (leaf) nodes
PSI_PARASITE = -3.0     # haustorial reservoir — more negative than host => sink
PSI_CAVITATION = -2.0   # vessel embolises (is removed) when its psi < this

# Haustorial leak conductance  Q_parasite = K_h * (psi_host - psi_parasite)
# K_h is THE independent variable of the study.  Normalised units.
K_H_DEFAULT = 0.5


# ----------------------------------------------------------------------------
# Network generation defaults  (Person A)
# ----------------------------------------------------------------------------
@dataclass
class NetworkParams:
    generations: int = 9          # tree depth; ~2^g terminal vessels (N~1023)
    branch_angle: float = 45.0    # half-angle of each bifurcation [degrees]
    angle_jitter: float = 8.0     # random angle spread [degrees]
    length_ratio: float = 0.72    # child_length/parent_length -> the D knob
    radius_exponent: float = 3.0  # Murray's law exponent (r_p^n = sum r_c^n)
    root_length: float = 1.0      # length of the root vessel (normalised)
    root_radius: float = 1.0      # radius of the root vessel (normalised)
    # Reticulation: number of anastomoses (cross-links) to add, as a fraction of
    # the (N-1) tree edges; shortest candidates first, so mean degree is
    # ~2*(1+reticulation) regardless of length_ratio. This is ALSO the D knob:
    # denser venation -> more space-filling -> higher box-counting D. Default 2.0
    # gives ~2044 loops, mean degree ~6.0 and D~1.43 — inside the measured
    # Relbunium leaf-venation range (1.39-1.76; see VALIDATION.md) — with a sharp
    # p_c~0.28. (0.0 => pure tree, which has NO sharp percolation transition.)
    reticulation: float = 2.0
    reticulation_knn: int = 10    # nearest neighbours scanned per node for links
    seed: int | None = 0


# ----------------------------------------------------------------------------
# Percolation / Monte Carlo defaults  (Person C)
# ----------------------------------------------------------------------------
@dataclass
class PercolationParams:
    n_densities: int = 50         # rho values in [0, 1]
    n_trials: int = 10_000        # TOTAL trials -> n_trials/n_densities per rho
    collapse_fraction: float = 0.5  # GCC < 50% of N0  => collapsed (outcome 1)
    mode: str = "random"          # 'random' | 'targeted' | 'hydraulic'
    seed: int | None = 1

    @property
    def trials_per_density(self) -> int:
        return max(1, self.n_trials // self.n_densities)


# ----------------------------------------------------------------------------
# Parameter sweep defaults  (Person D) — builds the p_c vs (K_h, D) surface.
# The hydraulic-coupled mode re-solves a sparse system per trial, so it uses a
# much smaller trial budget than the 1e6-trial topological hero sigmoid.
# ----------------------------------------------------------------------------
@dataclass
class SweepParams:
    # D axis is realised at CONSTANT network size N by varying the anastomosis
    # (vein) density and MEASURING the box-counting dimension of each network:
    # denser venation -> more space-filling -> higher D (and, as in real leaf
    # venation, higher connectivity). Spans D ~ 1.35-1.48 at N=1023 (low-mid of
    # the empirical Relbunium range 1.39-1.76). Capped at ret=2.5: denser
    # networks are so robust they don't hydraulically collapse under weak sinks
    # (p_c undefined / NaN), which would leave blank heatmap cells.
    reticulation_grid: tuple = (1.2, 1.6, 2.0, 2.5)
    k_h_grid: tuple = (0.3, 0.6, 1.0, 1.5, 2.5)
    n_trials_coupled: int = 600   # per (K_h, D) cell for hydraulic mode
    n_densities: int = 30
    seed: int | None = 2


# ----------------------------------------------------------------------------
# Parasite profiles — the model is parasite-agnostic: a parasite is just a sink
# strength (K_h), an attachment pattern (WHERE it taps), and an aggressiveness
# (psi_parasite). Different weeds = different profiles, no code change.
#   attachment: 'betweenness'   -> stem/branch parasites tap the backbone
#               'root_proximal'  -> root parasites tap near the stem base
#               'random'         -> systemic/endophytic parasites tap diffusely
# The model tells parasites apart by attachment site x trophic mode (efficiency):
# two species with the SAME attachment & mode collapse the host identically, so the
# holoparasite set below spans the THREE distinct attachment geometries (stem, root,
# systemic) rather than listing same-profile species (e.g. Cassytha would duplicate
# Cuscuta; Phelipanche would duplicate Orobanche).
# NOTE: root parasites really attach to the host ROOT SYSTEM; our network models
# the shoot vasculature with the root as a single source node, so root attack is
# approximated as "tap the root-proximal (low-generation) backbone." A full root
# system is future work.
# ----------------------------------------------------------------------------
@dataclass
class Parasite:
    name: str
    attachment: str       # 'betweenness' (stem) | 'root_proximal' (root) | 'random'
    efficiency: float     # per-haustorium disabling prob: 1.0 holo, <1 hemi
    kind: str             # 'holoparasite' | 'hemiparasite' (label)


PARASITES = [
    # --- HOLOPARASITES (study focus; efficiency 1.0 = full vessel disabling) ---
    Parasite("Cuscuta (dodder)",       attachment="betweenness",
             efficiency=1.0, kind="holoparasite"),     # STEM holoparasite
    Parasite("Orobanche (broomrape)",  attachment="root_proximal",
             efficiency=1.0, kind="holoparasite"),     # ROOT holoparasite
    Parasite("Pilostyles (endophyte)", attachment="random",
             efficiency=1.0, kind="holoparasite"),     # SYSTEMIC/endophytic holo
    # --- HEMIPARASITES (comparison only; efficiency 0.6 = partial sink) ---
    Parasite("Striga (witchweed)",     attachment="root_proximal",
             efficiency=0.6, kind="hemiparasite"),     # root, partial (photosyn.)
    Parasite("Mistletoe",              attachment="betweenness",
             efficiency=0.6, kind="hemiparasite"),     # branch, partial
]


# ----------------------------------------------------------------------------
# Output locations
# ----------------------------------------------------------------------------
@dataclass
class Paths:
    figures: str = "figures"
    data: str = "data"


DEFAULT_NETWORK = NetworkParams()
DEFAULT_PERCOLATION = PercolationParams()
DEFAULT_SWEEP = SweepParams()
PATHS = Paths()


def new_rng(seed):
    """Single source of RNGs so every result is reproducible."""
    return np.random.default_rng(seed)
