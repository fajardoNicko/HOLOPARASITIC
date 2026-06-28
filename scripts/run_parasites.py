"""
run_parasites.py — generality result: compare the vascular collapse threshold
p_c across different parasitic weeds on the SAME host network.

Each parasite is a profile (sink strength K_h, attachment pattern, aggressiveness)
in config.PARASITES — Cuscuta (stem holoparasite), Orobanche (root holoparasite),
Striga (root hemiparasite), Mistletoe (stem hemiparasite). Shows the framework is
parasite-agnostic and answers "only Cuscuta?".

    C:\\laragon\\bin\\python\\python-3.13\\python.exe scripts\\run_parasites.py
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config
from holoparasitic import network, sweep, viz


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    G = network.generate()
    print(f"Comparing parasites on host network (N={G.number_of_nodes()}, "
          f"D from box-counting):", flush=True)
    results = sweep.compare_parasites(G)

    figdir, datadir = config.PATHS.figures, config.PATHS.data
    os.makedirs(datadir, exist_ok=True)
    viz.plot_parasite_comparison(results, os.path.join(figdir, "parasites.png"))
    with open(os.path.join(datadir, "parasites.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("-" * 60, flush=True)
    print(f"figure -> {os.path.join(figdir, 'parasites.png')}", flush=True)
    print(f"data   -> {os.path.join(datadir, 'parasites.json')}", flush=True)


if __name__ == "__main__":
    main()
