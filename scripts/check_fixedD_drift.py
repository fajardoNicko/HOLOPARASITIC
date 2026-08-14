r"""
check_fixedD_drift.py — audit what actually stayed fixed in the fixed-D
finite-size sweep.

`run_finite_size_fixedD.py` pins two architectural quantities (box-counting D and
mean degree) while N grows. Two knobs are moved to achieve that: `length_ratio`
falls and `mesh_frac` rises with depth. Pinning two descriptors does not pin the
architecture, so this script regenerates each tuned network from its recorded
knobs and measures the descriptors that were NOT pinned -- loop fraction, bridge
fraction, degree SD, terminal fraction. If those drift, the size trend in the
sweep is still not a clean finite-size effect, and the paper must say so.

    C:\laragon\bin\python\python-3.13\python.exe scripts\check_fixedD_drift.py
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import networkx as nx

import config
from holoparasitic import network, calibrate as cal


def descriptors(G):
    deg = np.array([d for _, d in G.degree()], float)
    bridges = set(map(frozenset, nx.bridges(G)))
    E = G.number_of_edges()
    nb = sum(1 for e in G.edges() if frozenset(e) not in bridges)
    return {"mean_degree": float(deg.mean()), "degree_sd": float(deg.std(ddof=1)),
            "loop_fraction_nonbridge": nb / E if E else float("nan"),
            "bridge_fraction": 1 - (nb / E if E else float("nan")),
            "terminal_fraction": float((deg == 1).mean())}


def main():
    path = os.path.join(config.PATHS.data, "finite_size_fixedD.json")
    with open(path) as f:
        doc = json.load(f)

    print("regenerating each tuned network and measuring the UNPINNED "
          "descriptors\n")
    hdr = ("     N   <k>     D      loopfrac  bridgefrac  degSD   termfrac")
    print(hdr)
    for row in doc["sizes"]:
        base = cal.calibrated_base(generations=row["generations"])
        p = config.NetworkParams(**{**base.__dict__,
                                    "length_ratio": row["length_ratio"],
                                    "mesh_frac": row["mesh_frac"]})
        d = descriptors(network.generate(p))
        row["unpinned_descriptors"] = {k: round(v, 4) for k, v in d.items()}
        print(f"  {row['N']:>6}  {d['mean_degree']:.3f}  {row['D']:.3f}  "
              f"{d['loop_fraction_nonbridge']:8.4f}  {d['bridge_fraction']:9.4f}  "
              f"{d['degree_sd']:.4f}  {d['terminal_fraction']:.4f}", flush=True)

    lf = np.array([r["unpinned_descriptors"]["loop_fraction_nonbridge"]
                   for r in doc["sizes"]], float)
    sd = np.array([r["unpinned_descriptors"]["degree_sd"]
                   for r in doc["sizes"]], float)
    pc = np.array([r["p_c"] for r in doc["sizes"]], float)

    drift = {
        "loop_fraction_range": [round(float(lf.min()), 4),
                                round(float(lf.max()), 4)],
        "loop_fraction_spread": round(float(lf.max() - lf.min()), 4),
        "degree_sd_range": [round(float(sd.min()), 4), round(float(sd.max()), 4)],
        "pearson_loop_fraction_vs_pc": round(float(np.corrcoef(lf, pc)[0, 1]), 4),
        "verdict": None,
    }
    if drift["loop_fraction_spread"] > 0.05:
        drift["verdict"] = (
            "NOT a clean finite-size sweep. Pinning D and mean degree does not "
            "pin the architecture: loop fraction drifts by %.3f across the size "
            "range, and loop fraction is itself one of this study's predictors "
            "of the threshold. No finite-size claim -- convergence OR divergence "
            "-- can be made from this generator without a construction that also "
            "holds the loop fraction fixed."
            % drift["loop_fraction_spread"])
    else:
        drift["verdict"] = (
            "Clean enough: loop fraction varies by only %.3f across the size "
            "range, so the residual size trend can be read as a finite-size "
            "effect." % drift["loop_fraction_spread"])

    doc["architecture_drift_audit"] = drift
    with open(path, "w") as f:
        json.dump(doc, f, indent=2)
    print(f"\n{drift['verdict']}")
    print(f"\nupdated {path}")


if __name__ == "__main__":
    main()
