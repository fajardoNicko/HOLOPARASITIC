# -*- coding: utf-8 -*-
r"""
run_mc_uncertainty.py -- how much does a network's p_c move if the Monte Carlo
is simply re-run with a different random seed?

Answers SRC Reviewer 1: "correct uncertainty claims". The paper quoted the
binomial standard error of a collapse probability using the TOTAL trial budget
(0.0102 at 2,400 and 0.0050 at 10,000), but each collapse probability is
estimated from the trials at one removal fraction only (60 and 250), and the
standard error of one point on the curve is not the uncertainty of p_c anyway.
The direct measurement is to repeat the whole estimate with fresh seeds.

Design (all at the archived settings, 40 densities, rho_max 0.6):
  A. Percolation cohort budget, 2,400 trials: 12 networks spread over the size
     range of the 100-network cohort up to the median size, random removal,
     seeds 1..6. Smaller networks have wider transitions, so these are the
     noisiest networks in the cohort and the spread is an upper bound.
  B. Enhancement budget, 10,000 trials: 6 networks with added edges, traced and
     filtered-enhanced network measured with the SAME seed (common random
     numbers, as in the paper), seeds 1..5; the spread of the paired difference
     is the simulation uncertainty of each network's gain.

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_mc_uncertainty.py

Output: data/mc_uncertainty.json
"""
import os, sys, csv, glob, json, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import realleaf, percolation, planarity

LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
MASTER = os.path.join(ROOT, "data", "analysis_master.csv")


def load(s):
    return realleaf.load_matos(glob.glob(os.path.join(LEAFDIR, s, "*_nodes.csv"))[0],
                               glob.glob(os.path.join(LEAFDIR, s, "*_veins.csv"))[0],
                               name=s)


def pc(G, trials, seed):
    pp = config.PercolationParams(mode="random", n_densities=40,
                                  n_trials=trials, seed=seed)
    return percolation.find_pc(G, pp, rho_max=0.6)["p_c"]


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    rows = list(csv.DictReader(open(MASTER, newline="")))
    coh = sorted([r for r in rows if r["in_percolation_cohort_100"] == "True"],
                 key=lambda r: int(r["n_nodes"]))
    half = coh[:len(coh) // 2]                       # up to the median size
    pickA = [half[int(i * (len(half) - 1) / 11)] for i in range(12)]
    out = {"A_cohort_budget": {"trials": 2400, "seeds": [1, 2, 3, 4, 5, 6],
                               "networks": []}}
    for r in pickA:
        G = load(r["name"])
        vals = [pc(G, 2400, s) for s in range(1, 7)]
        out["A_cohort_budget"]["networks"].append(
            {"name": r["name"], "N": G.number_of_nodes(),
             "pc": [round(v, 4) for v in vals], "sd": round(float(np.std(vals, ddof=1)), 4)})
        print("A", r["name"], G.number_of_nodes(), [round(v, 4) for v in vals], flush=True)
    sds = [n["sd"] for n in out["A_cohort_budget"]["networks"]]
    between = float(np.std([float(r["pc_random"]) for r in coh], ddof=1))
    out["A_cohort_budget"]["summary"] = {
        "median_sd": round(float(np.median(sds)), 4), "max_sd": round(float(max(sds)), 4),
        "between_network_sd_of_pc": round(between, 4),
        "mc_variance_share_upper_bound_pct": round(100 * max(sds) ** 2 / between ** 2, 2)}

    enh = sorted([r for r in rows if r["in_enhancement_cohort_105"] == "True"
                  and int(r["loops_added"]) > 0 and int(r["n_nodes"]) <= 25000],
                 key=lambda r: float(r["mean_degree"]))
    pickB = [enh[int(i * (len(enh) - 1) / 5)] for i in range(6)]
    out["B_enhancement_budget"] = {"trials": 10000, "seeds": [1, 2, 3, 4, 5],
                                   "networks": []}
    for r in pickB:
        G = load(r["name"])
        G3, _, _ = planarity.add_loops_planar(G, 2.811)
        d = []
        for s in range(1, 6):
            d.append(pc(G3, 10000, s) - pc(G, 10000, s))
        out["B_enhancement_budget"]["networks"].append(
            {"name": r["name"], "N": G.number_of_nodes(), "k": round(float(r["mean_degree"]), 4),
             "delta": [round(v, 4) for v in d], "mean": round(float(np.mean(d)), 4),
             "sd": round(float(np.std(d, ddof=1)), 4)})
        print("B", r["name"], [round(v, 4) for v in d], flush=True)
    sdb = [n["sd"] for n in out["B_enhancement_budget"]["networks"]]
    out["B_enhancement_budget"]["summary"] = {"median_sd": round(float(np.median(sdb)), 4),
                                              "max_sd": round(float(max(sdb)), 4)}
    json.dump(out, open(os.path.join(ROOT, "data", "mc_uncertainty.json"), "w"), indent=2)
    print(json.dumps({k: v.get("summary") for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
