r"""
run_targeted_ci.py — re-run the two TARGETED attacks on the hero network with
bootstrap confidence intervals, which the original run did not store.

`data/summary.json` carries `p_c_ci95` for the random attack only, because
`scripts/run_full.py` stage 3 calls `find_pc(...)` without `with_ci=True`. Any
confidence interval quoted for a targeted threshold is therefore unsupported by
the archive. This script fills the gap at the same trial budget stage 3 used
(100,000 = max(50_000, 1e6 // 10)) and writes the intervals back into
summary.json alongside the existing values, leaving the point estimates to be
reproduced (and checked) rather than overwritten blindly.

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_targeted_ci.py
"""

import os
import sys
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from holoparasitic import network, percolation

N_TRIALS = 100_000
N_DENSITIES = 50


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    t0 = time.time()
    spath = os.path.join(config.PATHS.data, "summary.json")
    with open(spath) as f:
        summary = json.load(f)

    G = network.generate(config.DEFAULT_NETWORK)
    _, nodes = network.to_csr(G)
    print(f"hero mesh N={G.number_of_nodes()} E={G.number_of_edges()}")
    tp = config.PercolationParams(mode="targeted", n_trials=N_TRIALS,
                                  n_densities=N_DENSITIES)

    out = {}
    for label, metric in (("betweenness", "betweenness"), ("degree", "degree")):
        t = time.time()
        w = (percolation.importance_weights(G, nodes, metric=metric)
             if metric == "degree" else None)
        res = percolation.find_pc(G, tp, weights=w, with_ci=True)
        ci = res["ci"]["ci95"]
        stored = summary.get(f"p_c_targeted_{label}")
        out[label] = {"p_c": float(res["p_c"]),
                      "ci95": [float(ci[0]), float(ci[1])],
                      "n_trials": N_TRIALS,
                      "p_c_previously_stored": stored,
                      "reproduced_within": (None if stored is None
                                            else abs(float(res["p_c"]) - stored))}
        print(f"  {label:<12} p_c={res['p_c']:.4f}  "
              f"CI95=[{ci[0]:.4f}, {ci[1]:.4f}]  "
              f"(stored {stored})   [{time.time() - t:.0f}s]", flush=True)

    summary["p_c_targeted_betweenness_ci95"] = out["betweenness"]["ci95"]
    summary["p_c_targeted_degree_ci95"] = out["degree"]["ci95"]
    summary["n_trials_targeted"] = N_TRIALS
    summary["targeted_ci_note"] = (
        "Bootstrap percentile intervals added by scripts/run_targeted_ci.py; "
        "the original stage-3 run stored point estimates only.")
    with open(spath, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nupdated {spath}")

    dpath = os.path.join(config.PATHS.data, "targeted_ci.json")
    with open(dpath, "w") as f:
        json.dump({"n_trials": N_TRIALS, "n_densities": N_DENSITIES,
                   "network": {"N": G.number_of_nodes(),
                               "E": G.number_of_edges()},
                   "results": out,
                   "seconds": round(time.time() - t0, 1)}, f, indent=2)
    print(f"wrote {dpath}\ntotal {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
