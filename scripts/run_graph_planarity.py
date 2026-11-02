# -*- coding: utf-8 -*-
r"""
run_graph_planarity.py -- is each leaf GRAPH planar before and after enhancement?

Companion to run_planarity_check.py, which counts crossings in the drawing
(straight segments between junction coordinates). This script asks the
layout-free question with networkx.check_planarity: can the graph be drawn in
the plane with no crossings in SOME layout? It is run on
  * the traced network,
  * the original enhancement (shortest Delaunay non-edges, no crossing check),
  * the filtered enhancement (same, skipping candidates that cross a traced vein),
for every network in the enhancement cohort (n = 105).

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_graph_planarity.py --workers 1

Output: data/graph_planarity.csv (+ a summary printed and written to
data/graph_planarity.json)
"""
import os, sys, csv, glob, json, time, argparse
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
MASTER = os.path.join(ROOT, "data", "analysis_master.csv")
OUT_CSV = os.path.join(ROOT, "data", "graph_planarity.csv")
OUT_JSON = os.path.join(ROOT, "data", "graph_planarity.json")
FIELDS = ["species", "N", "traced_planar", "original_enhanced_planar",
          "filtered_enhanced_planar", "seconds"]


def one_leaf(name):
    import networkx as nx
    from holoparasitic import realleaf, planarity
    from scripts.make_real_suggested import add_loops, TARGET_K
    t0 = time.time()
    G = realleaf.load_matos(glob.glob(os.path.join(LEAFDIR, name, "*_nodes.csv"))[0],
                            glob.glob(os.path.join(LEAFDIR, name, "*_veins.csv"))[0],
                            name=name)
    traced = nx.check_planarity(G)[0]
    G2, _ = add_loops(G, TARGET_K)
    orig = nx.check_planarity(G2)[0]
    del G2
    G3, _, _ = planarity.add_loops_planar(G, TARGET_K)
    filt = nx.check_planarity(G3)[0]
    return {"species": name, "N": G.number_of_nodes(), "traced_planar": traced,
            "original_enhanced_planar": orig, "filtered_enhanced_planar": filt,
            "seconds": round(time.time() - t0, 1)}


def summarize():
    rows = list(csv.DictReader(open(OUT_CSV, newline="")))
    t = lambda k: sum(r[k] == "True" for r in rows)
    S = {"n": len(rows), "traced_planar": t("traced_planar"),
         "original_enhanced_planar": t("original_enhanced_planar"),
         "filtered_enhanced_planar": t("filtered_enhanced_planar"),
         "made_nonplanar_by_original": sum(r["traced_planar"] == "True" and
                                           r["original_enhanced_planar"] == "False"
                                           for r in rows),
         "made_nonplanar_by_filtered": sum(r["traced_planar"] == "True" and
                                           r["filtered_enhanced_planar"] == "False"
                                           for r in rows),
         "test": "networkx.check_planarity (layout-free)"}
    json.dump(S, open(OUT_JSON, "w"), indent=2)
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    rows = [r for r in csv.DictReader(open(MASTER, newline=""))
            if r["in_enhancement_cohort_105"] == "True"]
    done = set()
    if os.path.exists(OUT_CSV):
        done = {r["species"] for r in csv.DictReader(open(OUT_CSV, newline=""))}
    todo = [r["name"] for r in sorted(rows, key=lambda r: int(r["n_nodes"]))
            if r["name"] not in done]
    new = not os.path.exists(OUT_CSV) or os.path.getsize(OUT_CSV) == 0
    with open(OUT_CSV, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        with Pool(args.workers) as pool:
            for i, row in enumerate(pool.imap_unordered(one_leaf, todo), 1):
                w.writerow(row); fh.flush()
                print(i, row, flush=True)
    print(summarize())


if __name__ == "__main__":
    main()
