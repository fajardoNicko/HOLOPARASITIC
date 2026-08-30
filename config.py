"""
config.py — central, FROZEN configuration for the Holoparasitic Vascular
Percolation Study.

Every physical constant, every default parameter set and the shared graph
schema live here, so that the modules under holoparasitic/ can be developed and
re-run independently against one contract. Nothing below should change without
re-running the pipeline: the archived results in data/ were produced under these
values, and several of them are quoted verbatim in the manuscript.

----------------------------------------------------------------------------
NETWORK DATA STRUCTURE — the contract every module reads and writes
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
    resistance  : float   Hagen-Poiseuille R = 8 eta L / (pi r^4)   [Pa.s/m^3]
    conductance : float   g = r^4 / L              (normalised, used by solver)
    kind        : str     'axial'        = Murray bifurcation edge
                          'anastomosis'  = reticulation cross-link (loop)

`conductance` is NOT the reciprocal of `resistance`: it is 1/R with the global
constant 8*eta/pi divided out, i.e. g = (pi / 8 eta) / R. That constant is the
same on every edge, so it factors out of the Kirchhoff solve and changes no
potential; dropping it keeps the sparse system well-conditioned across the
~100x caliber range between the root vessel and a minor vein. `resistance`
carries the real SI value for anything the paper reports in physical units.

Helper `network.to_csr(G)` converts G -> scipy CSR adjacency ONCE; the Monte
Carlo hot loop then works purely on integer-indexed sparse matrices and never
touches NetworkX. That is what makes the million-trial reference run feasible.
----------------------------------------------------------------------------
"""

from dataclasses import dataclass
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

# Literature-anchored holoparasite constant (scripts/make_sink_demo.py):
# K_h solved so ONE haustorium diverts ~18-20% of leaf throughput -- a CONSERVATIVE
# FLOOR taken from a hemiparasite (Jiang, Jeschke & Hartung 2003, J. Exp. Bot.
# 54:1985, ~18% in Rhinanthus/Hordeum) -- across an illustrative ~1.5 MPa host->
# parasite gradient. CAUTION: the 1.5 MPa figure is an order-of-magnitude value
# cited in Cuscuta REVIEW literature, NOT a primary measurement, and it is NOT in
# Kaiser et al. 2015 (that review does not quantify the gradient). No published
# holoparasite-specific "% of host water" or gradient measurement was located; the
# exact sink magnitude is therefore a DELIMITATION, not a measured input.
# NOTE: at this realistic strength the sink is SUB-cavitation (0 vessels embolise
# at any gradient) — it drains water/carbon but does not rupture the xylem, so the
# hydraulic sink and the percolation collapse are DECOUPLED lenses. See sink_demo.json.
K_H_HOLOPARASITE = 0.0392


# ----------------------------------------------------------------------------
# Network generation defaults
# ----------------------------------------------------------------------------
@dataclass
class NetworkParams:
    # The bare defaults below reproduce the pre-2026-07 'knn' reference network
    # exactly (see LEGACY_HERO_NETWORK at the bottom of this file). The network
    # the study actually reports on is DEFAULT_NETWORK, which overrides most of
    # them with values measured from the real cohort.
    generations: int = 9          # tree depth; ~2^g terminal vessels (N~1023)
    branch_angle: float = 45.0    # half-angle of each bifurcation [degrees]
    angle_jitter: float = 8.0     # random angle spread [degrees]
    length_ratio: float = 0.72    # child_length/parent_length; a constant-
                                  # connectivity geometric control, not a D knob
    radius_exponent: float = 3.0  # Murray's law exponent (r_p^n = sum r_c^n)
    daughter_symmetry: float = 1.0  # r_small/r_large at each split (0,1]; 1.0 =
                                    # symmetric (Murray-equal daughters, the
                                    # original behaviour). Real leaves are <1;
                                    # calibrate.py measures it from Matos data.
                                    # Murray conservation holds for any value.
    root_length: float = 1.0      # length of the root vessel (normalised)
    root_radius: float = 1.0      # radius of the root vessel (normalised)
    # Reticulation ('knn' mode only): number of anastomoses (cross-links) to add,
    # as a fraction of the (N-1) tree edges; shortest candidates first, so mean
    # degree is ~2*(1+reticulation) regardless of length_ratio. In this mode it
    # is also what moves box-counting D, because denser cross-linking fills more
    # of the plane: sweep.pc_vs_D uses it for exactly that. Default 2.0 gives
    # ~2044 loops, mean degree ~6.0 and D~1.43, inside the measured Relbunium
    # leaf-venation range 1.39-1.76 (see VALIDATION.md), with a sharp p_c~0.28.
    # 0.0 gives a pure tree, which has NO sharp percolation transition at all.
    reticulation: float = 2.0
    reticulation_knn: int = 10    # nearest neighbours scanned per node for links
    # Reticulation MODE — how loops are closed:
    #   'knn'  (original) add reticulation*(N-1) shortest nearest-neighbour
    #          cross-links to the tree. Produces a decorated TREE: mean degree
    #          rises but most edges stay bridges (loop_fraction ~0.2 at <k>=2.5),
    #          unlike real venation. Kept for the pre-2026-07 hero network.
    #   'mesh' (calibrated) close areoles the way a real leaf does: add the
    #          shortest DELAUNAY edges (planar, non-crossing) up to `mesh_frac`
    #          of the candidates. Yields a true planar MESH — most edges lie on a
    #          cycle (loop_fraction ~0.78 at <k>~2.6), matching the Matos cohort.
    #          Here mesh_frac (not reticulation) sets connectivity, and <k> and
    #          loop_fraction rise together exactly as they do across real leaves.
    reticulation_mode: str = "knn"
    mesh_frac: float = 0.10       # 'mesh' mode: fraction of Delaunay candidate
                                  # edges to add (controls <k> AND loop_fraction)
    seed: int | None = 0


# ----------------------------------------------------------------------------
# Percolation / Monte Carlo defaults
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
# Parameter sweep defaults — builds the p_c vs (K_h, D) surface.
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


# The pre-2026-07 hero (knn reticulation, <k>~6, D~1.43) — kept as a robustness
# check. It was an artifact of reticulation=2.0, not a calibration target.
LEGACY_HERO_NETWORK = NetworkParams()

# PROMOTED HERO (2026-07-30). The cohort-calibrated planar MESH: real branching
# geometry (angle 55.31, Murray exponent 2.0, daughter symmetry 0.675, length
# ratio 0.929), the real mean degree (<k> = 2.5 via mesh_frac 0.086), at N=1023
# (generations=9) — the SAME size as the legacy hero, so promoting it is a
# like-for-like swap of the connectivity model, not a change of scale. p_c stays
# ~0.28. Mirrors calibrate.calibrated_base(generations=9); hardcoded here because
# config cannot import calibrate (calibrate imports config).
DEFAULT_NETWORK = NetworkParams(
    generations=9, branch_angle=55.31, angle_jitter=30.0, radius_exponent=2.0,
    daughter_symmetry=0.675, length_ratio=0.929,
    reticulation_mode="mesh", mesh_frac=0.086, seed=0)
DEFAULT_PERCOLATION = PercolationParams()
DEFAULT_SWEEP = SweepParams()
PATHS = Paths()

# ---------------------------------------------------------------------------
# Synthetic-phase 2D sweep grid — calibrated to the 100-leaf real cohort.
# The generator's branching geometry is fixed to the cohort medians (see
# holoparasitic.calibrate.COHORT_TARGETS / calibrated_base); only these two
# axes are swept, and BOTH mean degree and D are measured on each network:
#   SWEEP_MEAN_DEGREES  -> reticulation knob (mean degree), spans+extends real
#                          2.15..2.99 with an extra high-<k> point for causal range
#   SWEEP_GENERATIONS   -> D knob (space-filling), spans the real D 1.26..1.91
# The knobs are near-orthogonal (grid <k>-D correlation ~0), so p_c can be
# attributed to each factor independently — the causal complement to the real
# cohort, where the two were uncorrelated but not manipulable.
SWEEP_MEAN_DEGREES = (2.1, 2.4, 2.7, 3.0, 3.5, 4.0)
SWEEP_GENERATIONS = (8, 9, 10, 11, 12, 13, 14)


def new_rng(seed):
    """Single source of RNGs so every result is reproducible."""
    return np.random.default_rng(seed)
