# -*- coding: utf-8 -*-
r"""
run_uncapped_ci.py -- recompute the synthetic reference network's confidence
intervals without the 50,000-trial bootstrap cap.

Answers SRC Reviewer 1: "clarify trial budgets and correct uncertainty claims."

percolation.bootstrap_pc resamples at most `sample_cap` = 50,000 of the trials
per bootstrap replicate. For the 1,000,000-trial random run and the
100,000-trial weighted runs that makes every interval wider than the data
support, and the paper reported them as upper bounds. This script re-runs the
three Table 4 thresholds with the same seed and budgets (so the point estimates
reproduce exactly) and bootstraps with every trial resampled (B = 200,
percentile, seed 7, unchanged otherwise). It also reports the capped interval
from the same trials so the two can be compared directly.

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_uncapped_ci.py

Output: data/uncapped_ci.json
"""
import os, sys, json, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from holoparasitic import network, percolation

RUNS = [("random", "random", 1_000_000, None),
        ("degree", "targeted", 100_000, "degree"),
        ("betweenness", "targeted", 100_000, "betweenness")]


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    G = network.generate()
    nodes = list(G.nodes)
    out = {"network": {"N": G.number_of_nodes(), "E": G.number_of_edges()},
           "bootstrap": "percentile, B = 200, seed 7", "results": {}}
    for name, mode, n_trials, metric in RUNS:
        t0 = time.time()
        pp = config.PercolationParams(mode=mode, n_trials=n_trials, n_densities=50)
        w = percolation.importance_weights(G, nodes, metric=metric) if metric else None
        res = percolation.find_pc(G, pp, weights=w)
        capped = percolation.bootstrap_pc(res["X"], res["y"])
        full = percolation.bootstrap_pc(res["X"], res["y"], sample_cap=len(res["X"]))
        wc = capped["ci95"][1] - capped["ci95"][0]
        wf = full["ci95"][1] - full["ci95"][0]
        out["results"][name] = {
            "n_trials": n_trials, "trials_per_density": pp.trials_per_density,
            "p_c": round(res["p_c"], 6),
            "ci95_capped_50k": [round(v, 6) for v in capped["ci95"]],
            "ci95_uncapped": [round(v, 6) for v in full["ci95"]],
            "bootstrap_sd_uncapped": round(full["std"], 6),
            "width_capped": round(wc, 6), "width_uncapped": round(wf, 6),
            "width_ratio_capped_over_uncapped": round(wc / wf, 3),
            "seconds": round(time.time() - t0, 1)}
        print(name, json.dumps(out["results"][name]), flush=True)
    json.dump(out, open(os.path.join(ROOT, "data", "uncapped_ci.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
