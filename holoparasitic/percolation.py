"""
percolation.py  (Person C) — Monte Carlo GCC collapse + logistic-regression p_c.

For a FINITE network the percolation transition is sigmoidal, not a step, so we
estimate the threshold statistically:

  1. For each of `n_densities` values rho in [0, 1] run many trials.
  2. Each trial removes nodes (see the three MODES below), keeps the surviving
     subgraph, and records whether the Giant Connected Component fell below
     `collapse_fraction` x N0  (binary outcome: 1 = collapsed).
  3. Logistic regression on every (rho, outcome) pair gives a smooth sigmoid;
     p_c is its inflection point  rho where P(collapse) = 0.5  ==  -b / w.

MODES
  random     classic site percolation — node removed with prob rho.
             (the fast, 1e6-trial engine behind the hero sigmoid)
  targeted   backbone-weighted removal — the highest-BETWEENNESS vessels go
             first (Albert-Barabasi-style attack on the structurally critical
             stem/major veins). In a vascular tree, betweenness (not degree)
             identifies the critical nodes: high-degree vessels are the
             redundant reticulated periphery, so a *degree* attack is actually
             weaker than random. Pass custom `weights` to override.
  hydraulic  COUPLED model: place a fraction rho of haustoria, solve the flow
             field, embolise every vessel past the cavitation tension, remove
             those, then measure the GCC. Here K_h genuinely shifts p_c — this
             is what fills the p_c-vs-(K_h, D) heatmap.

The hot loop runs on a CSR adjacency built ONCE and never touches NetworkX.
"""

from __future__ import annotations

import numpy as np
import networkx as nx
from scipy.sparse.csgraph import connected_components
from sklearn.linear_model import LogisticRegression

import config
from . import network, hydraulics


def importance_weights(G, nodes, metric="betweenness"):
    """Mean-preserving weights describing WHERE a parasite attacks / which nodes
    matter for an attack.

    'betweenness' — the structural backbone (stem/major veins); the true
        importance in a hierarchical vascular network. Stem parasites (Cuscuta,
        mistletoe) tap this.
    'root_proximal' — vessels near the stem base (low generation); root parasites
        (Striga, Orobanche) tap here.
    'degree' — raw degree. NOTE: in a vascular tree this DISAGREES with
        betweenness — high-degree nodes are the redundant reticulated periphery,
        so a degree attack is *weaker* than random.
    """
    if metric == "degree":
        w = np.array([d for _, d in G.degree(nodes)], float)
    elif metric == "root_proximal":
        gen = np.array([G.nodes[n]["gen"] for n in nodes], float)
        w = (gen.max() - gen + 1.0)          # highest at the root (gen 0)
    else:  # betweenness
        bc = nx.betweenness_centrality(G, normalized=True)
        w = np.array([bc[n] for n in nodes], float)
    return w / w.mean() if w.mean() > 0 else np.ones_like(w)


# ----------------------------------------------------------------------------
# Single-trial helpers (operate purely on the integer-indexed CSR matrix)
# ----------------------------------------------------------------------------
def _gcc_size(sub) -> int:
    if sub.shape[0] == 0:
        return 0
    _, labels = connected_components(sub, directed=False)
    return int(np.bincount(labels).max())


def _keep(adj, idx):
    return adj[idx][:, idx]


def _trial_random(adj, n, rho, rng):
    idx = np.flatnonzero(rng.random(n) > rho)
    return _gcc_size(_keep(adj, idx)) if idx.size else 0


def _trial_weighted(adj, n, rho, rng, weights):
    # node removed with prob proportional to its weight; E[fraction] = rho
    p_remove = np.clip(rho * weights, 0.0, 1.0)
    idx = np.flatnonzero(rng.random(n) > p_remove)
    return _gcc_size(_keep(adj, idx)) if idx.size else 0


def _trial_parasite(adj, n, rho, rng, weights, efficiency):
    # A parasite taps vessels following its attachment pattern (weights; E[frac]
    # = rho) and DISABLES each tapped vessel with probability `efficiency` —
    # 1.0 for a holoparasite, <1 for a hemiparasite that only partially blocks.
    p_remove = np.clip(rho * weights, 0.0, 1.0) * efficiency
    idx = np.flatnonzero(rng.random(n) > p_remove)
    return _gcc_size(_keep(adj, idx)) if idx.size else 0


def _trial_hydraulic(adj, nodes, solver, rho, k_h, rng, p_attach=None,
                     psi_parasite=config.PSI_PARASITE):
    n = len(nodes)
    n_h = int(round(rho * n))
    if n_h:
        # p_attach: probability of a haustorium landing on each node (its
        # attachment pattern). None => uniform random.
        haustoria = rng.choice(nodes, size=n_h, replace=False, p=p_attach)
    else:
        haustoria = []
    psi = solver.solve(haustoria=list(haustoria), k_h=k_h,
                       psi_parasite=psi_parasite)
    embolized = set(solver.embolized_nodes(psi))
    if not embolized:
        return n
    keep = np.fromiter((i for i, nd in enumerate(nodes) if nd not in embolized),
                       int)
    return _gcc_size(_keep(adj, keep)) if keep.size else 0


# ----------------------------------------------------------------------------
# Density response: the (rho -> P(collapse)) curve and raw trial data
# ----------------------------------------------------------------------------
def density_response(G, params=None, weights=None, k_h=config.K_H_DEFAULT,
                     parasite=None):
    """Run the full Monte Carlo sweep over rho. Returns a result dict with the
    aggregated curves and the raw (X, y) needed for the logistic fit.

    parasite : a config.Parasite. In 'hydraulic' mode it sets the sink strength
               K_h, the reservoir potential, and the attachment pattern that
               haustoria follow (where they land). Lets one model Cuscuta vs
               Striga vs Orobanche on the same host network."""
    p = params or config.DEFAULT_PERCOLATION
    rng = config.new_rng(p.seed)

    adj, nodes = network.to_csr(G)
    n = adj.shape[0]
    threshold = p.collapse_fraction * n
    tpd = p.trials_per_density
    rhos = np.linspace(0.0, 1.0, p.n_densities)

    solver = (hydraulics.HydraulicSolver(G)
              if p.mode == "hydraulic" and parasite is None else None)
    if p.mode == "targeted" and weights is None:
        # attack the structural backbone (betweenness), NOT raw degree — see
        # importance_weights(): in a vascular tree these disagree.
        weights = importance_weights(G, nodes, metric="betweenness")

    # parasite profile: a topological attack following the attachment pattern,
    # scaled by a per-haustorium disabling efficiency (holo 1.0, hemi < 1.0).
    # This is robust and smooth, unlike the hydraulic embolism cascade under
    # highly-concentrated backbone placement. Overrides `mode`.
    par_w, par_eff = None, 1.0
    if parasite is not None:
        par_eff = parasite.efficiency
        par_w = (np.ones(n) if parasite.attachment == "random"
                 else importance_weights(G, nodes, metric=parasite.attachment))

    p_collapse = np.empty(p.n_densities)
    gcc_fraction = np.empty(p.n_densities)
    X = np.empty(p.n_densities * tpd)
    y = np.empty(p.n_densities * tpd, dtype=np.int8)

    for di, rho in enumerate(rhos):
        gccs = np.empty(tpd)
        for t in range(tpd):
            if parasite is not None:
                g = _trial_parasite(adj, n, rho, rng, par_w, par_eff)
            elif p.mode == "random":
                g = _trial_random(adj, n, rho, rng)
            elif p.mode == "targeted":
                g = _trial_weighted(adj, n, rho, rng, weights)
            elif p.mode == "hydraulic":
                g = _trial_hydraulic(adj, nodes, solver, rho, k_h, rng)
            else:
                raise ValueError(f"unknown mode {p.mode!r}")
            gccs[t] = g
        outcomes = (gccs < threshold).astype(np.int8)
        s = slice(di * tpd, (di + 1) * tpd)
        X[s] = rho
        y[s] = outcomes
        p_collapse[di] = outcomes.mean()
        gcc_fraction[di] = gccs.mean() / n

    return {
        "rhos": rhos,
        "p_collapse": p_collapse,
        "gcc_fraction": gcc_fraction,
        "X": X, "y": y,
        "n_nodes": n,
        "trials_per_density": tpd,
        "n_trials": p.n_densities * tpd,
        "mode": p.mode,
        "k_h": k_h if p.mode == "hydraulic" else None,
    }


# ----------------------------------------------------------------------------
# Threshold estimation
# ----------------------------------------------------------------------------
def fit_pc(X, y):
    """Logistic fit; p_c is the inflection point (P = 0.5) = -intercept/coef."""
    X = np.asarray(X, float).reshape(-1, 1)
    y = np.asarray(y, int)
    if y.min() == y.max():
        return {"p_c": float("nan"), "coef": float("nan"),
                "intercept": float("nan"), "model": None,
                "note": "single-class outcomes — p_c outside [0,1] sweep range"}
    model = LogisticRegression()
    model.fit(X, y)
    w = float(model.coef_[0, 0])
    b = float(model.intercept_[0])
    p_c = -b / w if w != 0 else float("nan")
    return {"p_c": float(p_c), "coef": w, "intercept": b, "model": model}


def pc_crossing(rhos, p_collapse):
    """Robust fallback: linear-interpolated rho where P(collapse) crosses 0.5."""
    rhos = np.asarray(rhos); pc = np.asarray(p_collapse)
    above = np.where(pc >= 0.5)[0]
    if above.size == 0 or above[0] == 0:
        return float("nan") if above.size == 0 else float(rhos[0])
    i = above[0]
    x0, x1, y0, y1 = rhos[i - 1], rhos[i], pc[i - 1], pc[i]
    return float(x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0)) if y1 != y0 else float(x0)


def bootstrap_pc(X, y, n_boot=200, sample_cap=50_000, seed=7):
    """Percentile CI for p_c by resampling trials and refitting the sigmoid."""
    X = np.asarray(X, float); y = np.asarray(y, int)
    rng = config.new_rng(seed)
    n = len(X)
    take = min(n, sample_cap)
    vals = []
    for _ in range(n_boot):
        s = rng.integers(0, n, take)
        fit = fit_pc(X[s], y[s])
        if np.isfinite(fit["p_c"]):
            vals.append(fit["p_c"])
    if not vals:
        return {"p_c_mean": float("nan"), "ci95": (float("nan"), float("nan")),
                "std": float("nan")}
    vals = np.asarray(vals)
    return {"p_c_mean": float(vals.mean()),
            "ci95": (float(np.percentile(vals, 2.5)),
                     float(np.percentile(vals, 97.5))),
            "std": float(vals.std())}


def find_pc(G, params=None, weights=None, k_h=config.K_H_DEFAULT,
            with_ci=False, parasite=None):
    """One-call convenience: sweep + logistic fit (+ optional bootstrap CI)."""
    res = density_response(G, params, weights=weights, k_h=k_h,
                           parasite=parasite)
    fit = fit_pc(res["X"], res["y"])
    res.update(fit)
    res["p_c_logistic"] = res["p_c"]
    res["p_c_crossing"] = pc_crossing(res["rhos"], res["p_collapse"])
    # The logistic inflection can extrapolate outside [0, 1] when collapse is
    # near-certain at the sweep's edge; the empirical crossing is then the
    # honest estimate. NaN here means the curve never reaches 50% within rho in
    # [0, 1] (e.g. a weak sink that never triggers hydraulic failure).
    if not (0.0 <= res["p_c"] <= 1.0) or np.isnan(res["p_c"]):
        res["p_c"] = res["p_c_crossing"]
    if with_ci:
        res["ci"] = bootstrap_pc(res["X"], res["y"])
    return res


if __name__ == "__main__":
    from . import network as net
    G = net.generate()
    r = find_pc(G, config.PercolationParams(n_trials=5000), with_ci=True)
    print(f"mode={r['mode']}  N={r['n_nodes']}  p_c={r['p_c']:.4f}  "
          f"CI95={r['ci']['ci95']}")
