# -*- coding: utf-8 -*-
r"""
run_kleaf_validate.py -- validate MODELLED leaf hydraulic conductance against the
MEASURED Kleaf reported by Matos/Sack for the same species.

For each cohort leaf we solve the baseline hydraulic field (source psi=0, terminals
psi=-1) and read off the effective source->terminal conductance K_model = (total flux
leaving the source) / Delta-psi. We then rank-correlate K_model against the measured
Kleaf (hydraulics/UCBG_venation_kmax.csv), joined by spp_code.

Units differ (model r^4/L in mm vs physiological mmol m^-2 s^-1 MPa^-1), so only the
RANK/relative agreement is meaningful -- a positive Spearman rho is the validation
that the network model captures the right relative hydraulic ordering across species.

Incremental, resumable -> data/kleaf_validation.csv (+ _summary.json).
ASCII-only stdout.
"""
import os
import sys
import csv
import glob
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

from holoparasitic import realleaf, hydraulics

DATA = os.path.join(ROOT, "data")
LEAFDIR = os.path.join(ROOT, "UCBG_venation_form_data", "UCBG_venation_form_data")
KMAX = os.path.join(ROOT, "hydraulics", "hydraulics", "UCBG_venation_kmax.csv")
OUT = os.path.join(DATA, "kleaf_validation.csv")
SUMMARY = os.path.join(DATA, "kleaf_validation_summary.json")
FIELDS = ["spp_code", "N", "E", "k_model", "kleaf_meas", "kleaf_area_meas", "n_meas", "seconds"]


def _f(s):
    try:
        v = float(s)
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def measured_kleaf():
    """median Kleaf and Kleaf_area per spp_code (drop NA)."""
    by = {}
    with open(KMAX, newline="") as f:
        for r in csv.DictReader(f):
            code = r.get("spp_code", "").strip()
            if not code:
                continue
            by.setdefault(code, {"kleaf": [], "karea": []})
            k = _f(r.get("Kleaf")) or _f(r.get("Kleaftcor"))
            ka = _f(r.get("Kleaf_area"))
            if k is not None:
                by[code]["kleaf"].append(k)
            if ka is not None:
                by[code]["karea"].append(ka)
    out = {}
    for code, d in by.items():
        if d["kleaf"]:
            out[code] = (float(np.median(d["kleaf"])),
                         float(np.median(d["karea"])) if d["karea"] else None,
                         len(d["kleaf"]))
    return out


def cohort_species():
    rows = list(csv.DictReader(open(os.path.join(DATA, "cohort.csv"), newline="")))
    return [r["name"] for r in rows if r.get("include", "").strip() == "True"]


def k_model_for(spp):
    d = os.path.join(LEAFDIR, spp)
    nfiles = glob.glob(d + "/*_nodes.csv")
    vfiles = glob.glob(d + "/*_veins.csv")
    if not nfiles or not vfiles:
        return None
    G = realleaf.load_matos(nfiles[0], vfiles[0], name=spp)
    solver = hydraulics.HydraulicSolver(G)
    psi = solver.solve(haustoria=None)
    ri = solver.index[solver.root]
    # total flux leaving the source; Delta-psi = psi_source - psi_leaf = 0-(-1)=1
    flux = 0.0
    for nbr in G.neighbors(solver.root):
        g = G[solver.root][nbr].get("conductance", 0.0)
        flux += g * (psi[ri] - psi[solver.index[nbr]])
    return G.number_of_nodes(), G.number_of_edges(), float(flux)


def done_set():
    if not os.path.exists(OUT):
        return set()
    return {r["spp_code"] for r in csv.DictReader(open(OUT, newline=""))}


def run():
    meas = measured_kleaf()
    spp = [s for s in cohort_species() if s in meas]
    done = done_set()
    print("cohort leaves with measured Kleaf: %d  (done: %d)" % (len(spp), len(done)))
    exists = os.path.exists(OUT)
    for i, s in enumerate(spp):
        if s in done:
            continue
        t0 = time.time()
        try:
            res = k_model_for(s)
        except Exception as e:
            print("  skip %s: %s" % (s, e)); continue
        if res is None:
            continue
        N, E, k_model = res
        km, ka, nm = meas[s]
        row = {"spp_code": s, "N": N, "E": E, "k_model": round(k_model, 6),
               "kleaf_meas": round(km, 6), "kleaf_area_meas": (round(ka, 4) if ka else ""),
               "n_meas": nm, "seconds": round(time.time() - t0, 1)}
        with open(OUT, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if not exists:
                w.writeheader(); exists = True
            w.writerow(row)
        print("[%2d/%2d] %s N=%d k_model=%.3g Kleaf=%.4g (%.1fs)"
              % (i + 1, len(spp), s, N, k_model, km, row["seconds"]))
    summarize()


def summarize():
    from scipy.stats import spearmanr, pearsonr
    rows = list(csv.DictReader(open(OUT, newline="")))
    km = np.array([float(r["k_model"]) for r in rows])
    kl = np.array([float(r["kleaf_meas"]) for r in rows])
    # log for pearson (both span orders of magnitude, positive)
    ok = (km > 0) & (kl > 0)
    out = {
        "n_species": int(ok.sum()),
        "spearman_rho": float(spearmanr(km[ok], kl[ok]).statistic),
        "spearman_p": float(spearmanr(km[ok], kl[ok]).pvalue),
        "pearson_loglog_r": float(pearsonr(np.log(km[ok]), np.log(kl[ok])).statistic),
        "note": ("Units differ (model r^4/L mm vs measured mmol/m2/s/MPa); "
                 "rank/relative agreement is the meaningful test."),
    }
    json.dump(out, open(SUMMARY, "w"), indent=2)
    print(json.dumps(out, indent=2))
    print("summary ->", os.path.relpath(SUMMARY, ROOT))


if __name__ == "__main__":
    if "--summary-only" in sys.argv:
        summarize()
    else:
        run()
