# -*- coding: utf-8 -*-
"""
run_trial_timing.py -- the step that picks which junctions a Monte Carlo trial
removes, done two ways, and what each costs.

  sort-based  give every junction a random key, sort the keys, remove the first
              round(rho * N)                         np.argsort -> O(N log N)
  mask-based  one random number per junction; the junction is removed when its
              number is below rho                    one pass   -> O(N)
              (this is percolation._trial_random)

Both are site percolation at removal fraction rho: sort-based removes exactly
rho*N junctions, mask-based removes rho*N on average.

  1. Removal step alone, N = 1,000 to 1,000,000 (median of repeats).
  2. One whole trial (removal + submatrix + connected components) both ways, on
     the first generator's networks (config.LEGACY_HERO_NETWORK) at 8 to 15
     generations.
  3. Reliability: p_c of the first generator's reference network (N = 1,023)
     both ways, same removal fractions, same trial count, same logistic fit.

Timings on a laptop move by tens of percent between runs; only trends are used.

    python scripts/run_trial_timing.py
Writes data/trial_timing.json. Timing only: no result in the paper uses it.
"""
from __future__ import annotations

import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config  # noqa: E402
from holoparasitic import network, percolation  # noqa: E402

RHO = 0.25
STEP_SIZES = [1_000, 3_000, 10_000, 30_000, 100_000, 300_000, 1_000_000]
GENERATIONS = range(8, 16)
PC_DENSITIES = np.linspace(0.0, 0.6, 40)
PC_TRIALS_PER_DENSITY = 150
OUT = ROOT / "data" / "trial_timing.json"


def survivors_sort(rng, n, rho):
    k = int(round(rho * n))
    return np.argsort(rng.random(n))[k:]


def survivors_mask(rng, n, rho):
    return np.flatnonzero(rng.random(n) > rho)


SCHEMES = {"sort": survivors_sort, "mask": survivors_mask}


def median_time(fn, repeats):
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return float(np.median(ts))


def gcc(adj, idx):
    if idx.size == 0:
        return 0
    _, labels = connected_components(adj[idx][:, idx], directed=False)
    return int(np.bincount(labels).max())


def removal_step():
    print("1. removal step alone")
    rows = []
    for n in STEP_SIZES:
        rng = config.new_rng(1)
        reps = int(np.clip(3_000_000 // n, 7, 300))
        r = {"N": n, "repeats": reps}
        for name, fn in SCHEMES.items():
            fn(rng, n, RHO)                                     # warm-up
            r[name] = median_time(lambda: fn(rng, n, RHO), reps)
        print(f"   N={n:>9,d}  sort {r['sort'] * 1e3:8.3f} ms   mask {r['mask'] * 1e3:8.3f} ms")
        rows.append(r)
    return rows


def whole_trial():
    print("2. one whole trial, first generator")
    rows = []
    for g in GENERATIONS:
        p = config.NetworkParams(**{**config.LEGACY_HERO_NETWORK.__dict__, "generations": g})
        adj, _ = network.to_csr(network.generate(p))
        n = adj.shape[0]
        reps = int(np.clip(2_000_000 // n, 20, 300))
        r = {"generations": g, "N": n, "E": int(adj.nnz // 2), "repeats": reps}
        for name, fn in SCHEMES.items():
            rng = config.new_rng(1)
            gcc(adj, fn(rng, n, RHO))                           # warm-up
            r[name] = median_time(lambda: gcc(adj, fn(rng, n, RHO)), reps)
        print(f"   N={n:>7,d}  sort {r['sort'] * 1e3:7.3f} ms   mask {r['mask'] * 1e3:7.3f} ms")
        rows.append(r)
    return rows


def reliability():
    print("3. p_c of the first generator's reference network, both ways")
    adj, _ = network.to_csr(network.generate(config.LEGACY_HERO_NETWORK))
    n = adj.shape[0]
    half = config.DEFAULT_PERCOLATION.collapse_fraction * n
    out = {"N": n, "densities": len(PC_DENSITIES), "trials_per_density": PC_TRIALS_PER_DENSITY}
    for name, fn in SCHEMES.items():
        rng = config.new_rng(7)
        X, y = [], []
        t0 = time.perf_counter()
        for rho in PC_DENSITIES:
            for _ in range(PC_TRIALS_PER_DENSITY):
                X.append(rho)
                y.append(int(gcc(adj, fn(rng, n, rho)) < half))
        secs = time.perf_counter() - t0
        fit = percolation.fit_pc(X, y)
        ci = percolation.bootstrap_pc(X, y)
        out[name] = {"p_c": fit["p_c"], "ci95": list(ci["ci95"]), "n_trials": len(X), "seconds": secs}
        print(f"   {name}: p_c = {fit['p_c']:.4f}  CI95 [{ci['ci95'][0]:.4f}, {ci['ci95'][1]:.4f}]"
              f"  ({len(X):,} trials, {secs:.1f} s)")
    out["difference"] = out["mask"]["p_c"] - out["sort"]["p_c"]
    return out


def loglog_slope(rows, key, min_n=10_000):
    N = np.array([r["N"] for r in rows], float)
    T = np.array([r[key] for r in rows], float)
    m = N >= min_n
    return float(np.polyfit(np.log10(N[m]), np.log10(T[m]), 1)[0])


def main():
    step = removal_step()
    trial = whole_trial()
    rel = reliability()
    fits = {"removal_step_slope_sort": loglog_slope(step, "sort"),
            "removal_step_slope_mask": loglog_slope(step, "mask"),
            "slope_fit_min_N": 10_000}
    print(f"log-log slope of the removal step (N >= 10,000): sort {fits['removal_step_slope_sort']:.3f}, "
          f"mask {fits['removal_step_slope_mask']:.3f}")
    OUT.write_text(json.dumps({
        "_purpose": "cost of the junction-removal step, sort-based vs mask-based, and their p_c agreement",
        "_generated_by": "scripts/run_trial_timing.py",
        "rho_for_timing": RHO,
        "timing": "median seconds (time.perf_counter)",
        "machine": {"python": platform.python_version(), "processor": platform.processor(),
                    "cpu_count": os.cpu_count()},
        "removal_step": step,
        "whole_trial": trial,
        "reliability": rel,
        "fits": fits,
    }, indent=2))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
