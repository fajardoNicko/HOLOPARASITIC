# -*- coding: utf-8 -*-
r"""make_appendix_c.py -- build "Appendix C: Data Analysis and Computation" as a
LaTeX document in the APA layout used by the reference hardbound paper.

The appendix mirrors the Results section by section: every table, every figure
and every number quoted in the running text of that chapter has a corresponding
derivation here. For each reported statistic the raw unit-level data are
tabulated or their sufficient sums are given, the defining formula is stated, the
intermediate arithmetic actually obtained from the data is substituted, and the
result is carried to the precision reported in the Results.

Every number is recomputed from data/*.csv and data/*.json. Nothing is copied
from the manuscript text. The recomputed-versus-reported reconciliation is
written to APPENDIX_C_CHECKS.csv and printed to stdout; it is deliberately NOT a
section of the appendix, which contains only material that belongs to the
Results.

    python scripts/make_appendix_c.py

Writes APPENDIX_C_COMPUTATIONS.tex (compile with pdflatex) and
APPENDIX_C_CHECKS.csv.  ASCII-only stdout.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _appendix_c_part1 as p1
import _appendix_c_part2 as p2
import _appendix_c_part3 as p3
import _appendix_c_part4 as p4
import _appendix_c_part5 as p5
import _appendix_c_part6 as p6
import _appendix_c_part7 as p7
import _appendix_c_part8 as p8
import _appendix_c_part9 as p9

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "APPENDIX_C_COMPUTATIONS.tex"
CHECKS_CSV = ROOT / "APPENDIX_C_CHECKS.csv"

L: list[str] = []
CHECKS: list[tuple[str, float, float, float]] = []


def w(s: str = "") -> None:
    L.append(s)


def steps(*lines):
    r"""Emit a multi-stage derivation, one arithmetic step per line."""
    w(r"\begin{align}")
    for i, ln in enumerate(lines):
        if i == len(lines) - 1:
            w(ln)
            continue
        # A row holding a compound fraction is two fraction-heights tall, and
        # the 3 pt that suits ordinary rows leaves it touching its neighbour.
        gap = 9 if r"\dfrac" in ln or r"\dfrac" in lines[i + 1] else 3
        w(ln + r" \\[%dpt]" % gap)
    w(r"\end{align}")


def check(label, reported, computed, tol=5e-4):
    CHECKS.append((label, float(reported), float(computed), tol))
    return computed


def J(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def esc(s):
    return str(s).replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")


def num(x, d=4):
    if x is None or (isinstance(float(x), float) and not math.isfinite(float(x))):
        return "--"
    return ("%." + str(d) + "f") % float(x)


def mint(x):
    """Thousands-separated integer safe for math mode (1{,}023 not 1,023)."""
    return "{:,}".format(int(x)).replace(",", "{,}")


def sgn(x, d=4):
    """Signed decimal safe for text mode: renders the minus as $-$."""
    v = float(x)
    return ("$-$" if v < 0 else "") + (("%." + str(d) + "f") % abs(v))


def sci(x, d=2):
    """Scientific notation typeset as math: 2.79 x 10^{-2}."""
    s = ("%." + str(d) + "e") % float(x)
    mant, exp = s.split("e")
    return r"$%s\times10^{%d}$" % (mant, int(exp))


def rho(x):
    """APA rank statistic: no leading zero, negative rendered as $-$."""
    v = float(x)
    if abs(v) >= 1.0:
        return ("$-$" if v < 0 else "") + ("%.3f" % abs(v))
    s = "%.3f" % abs(v)
    return ("$-$" if v < 0 else "") + "." + s.split(".")[1]


def pval(p):
    p = float(p)
    if p < 0.001:
        return "$<$ .001"
    if p >= 1.0:
        return "= 1.000"
    return "= ." + ("%.3f" % p).split(".")[1]


def describe(xs):
    xs = [float(v) for v in xs]
    n = len(xs)
    s = sum(xs)
    ss = sum(v * v for v in xs)
    m = s / n
    var = (ss - n * m * m) / (n - 1)
    sd = math.sqrt(max(var, 0.0))
    o = sorted(xs)
    mid = n // 2
    mdn = o[mid] if n % 2 else (o[mid - 1] + o[mid]) / 2.0
    return dict(n=n, sum=s, sum_sq=ss, M=m, SD=sd, Mdn=mdn, min=o[0], max=o[-1])


def quartile_cut(xs, q):
    """Linear-interpolation quantile, matching numpy's default."""
    o = sorted(float(v) for v in xs)
    h = (len(o) - 1) * q
    lo = int(math.floor(h))
    hi = min(lo + 1, len(o) - 1)
    return o[lo] + (h - lo) * (o[hi] - o[lo])


_DIGIT_COMMA = re.compile(r"(?<=[0-9]),(?=[0-9])")


def _fix_display_math(lines):
    """Inside align/equation bodies a bare comma between digits typesets as a
    punctuation comma with math spacing (``1, 549``). Brace it so that a
    thousands separator reads as one."""
    out, depth = [], 0
    for ln in lines:
        if ln.startswith(r"\begin{align}") or ln.startswith(r"\begin{equation}"):
            depth += 1
            out.append(ln)
            continue
        if ln.startswith(r"\end{align}") or ln.startswith(r"\end{equation}"):
            depth = max(0, depth - 1)
            out.append(ln)
            continue
        out.append(_DIGIT_COMMA.sub("{,}", ln) if depth else ln)
    return out


def _rows(path):
    with open(ROOT / "data" / path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_context():
    rows = _rows("analysis_master.csv")
    perc = [r for r in rows if r["in_percolation_cohort_100"] == "True"]
    enh = [r for r in rows if r["in_enhancement_cohort_105"] == "True"]
    char = [r for r in rows if r["in_characterization_112"] == "True"]
    rv = J("results_verified.json")
    grid = _rows("synthetic_grid_pc.csv")
    K = np.array([float(r["mean_degree"]) for r in grid])

    V = dict(
        PC=np.array([float(r["pc_random"]) for r in perc]),
        PCD=np.array([float(r["pc_degree"]) for r in perc]),
        K=np.array([float(r["mean_degree"]) for r in perc]),
        DD=np.array([float(r["D"]) for r in perc]),
        LF=np.array([float(r["loop_fraction_nonbridge"]) for r in perc]),
        BF=np.array([float(r["bridge_fraction"]) for r in perc]),
        LN=np.log(np.array([float(r["n_nodes"]) for r in perc])),
    )

    C = dict(
        w=w, steps=steps, check=check, num=num, esc=esc, rho=rho, pval=pval,
        mint=mint, sgn=sgn, sci=sci,
        describe=describe, quartile_cut=quartile_cut, J=J,
        rows=rows, perc=perc, enh=enh, char=char,
        by_name={r["name"]: r for r in rows},
        syn=_rows("synthetic_pernetwork.csv"), grid=grid,
        rv=rv,
        T1=rv["T1_characterization"], T2=rv["T2_descriptor_correlations"],
        T3=rv["T3_attack_thresholds"], T5=rv["T5_predictors"],
        T6=rv["T6_synthetic_grid"], T7=rv["T7_reticulation_and_bridges"],
        T8=rv["T8_quartiles"], T9=rv["T9_enhancement"],
        T10=rv["T10_gain_dependence"], T11=rv["T11_validation"],
        T12=rv["T12_top_gainers"],
        prov=J("cohort_provenance.json"),
        cl=J("criterion_and_locality.json"),
        cav=J("cavitation_sensitivity.json"),
        ss=J("sink_surface.json"),
        summ=J("summary.json"), tci=J("targeted_ci.json"),
        gma=J("graph_metric_audit.json"),
        frc=J("final_resolution_checks.json"),
        rrl=J("rrl_diagnostics.json"), spa=J("second_pass_audit.json"),
        rcs=J("resistance_convention_sensitivity.json"),
        fz=J("finite_size_fixedD.json"), sm=J("scaling_mesh.json"),
        dyn=J("dynamics.json"),
        V=V,
    )
    C["n_grid_above"] = int((K > C["rrl"]["synthetic_grid_refit"]
                             ["empirical_max_mean_degree"]).sum())
    return C


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    C = load_context()

    p1.preamble(C)
    p1.notation(C)
    p1.provenance(C)
    p2.engine(C)

    p3.empirical_descriptors(C)
    p3.synthetic_descriptors(C)
    p3.descriptor_associations(C)

    p4.thresholds(C)
    p4.reference_network(C)

    p5.normality(C)
    p5.predictors(C)
    p5.synthetic_grid(C)

    p6.reticulation(C)
    p6.quartiles(C)
    p6.enhancement(C)
    p6.gain_dependence(C)
    p6.top_gainers(C)

    p7.sink(C)
    p7.surface(C)
    p7.verification(C)
    p7.boundary(C)
    p7.criterion(C)
    p7.locality(C)

    p8.size_dependence(C)
    p8.sensitivity(C)
    p8.comparisons(C)
    p8.sign_test(C)

    p9.concentration(C)
    p9.collinearity(C)
    p9.budgets(C)
    p9.dynamics(C)
    p9.figure_logic(C)

    w(r"\end{document}")

    OUT.write_text("\n".join(_fix_display_math(L)) + "\n", encoding="utf-8")

    n_ok = 0
    with open(CHECKS_CSV, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["quantity", "reported_in_results", "recomputed",
                     "difference", "status"])
        for label, rep, comp, tol in CHECKS:
            d = float(comp) - float(rep)
            ok = abs(d) <= tol
            n_ok += ok
            wr.writerow([label, rep, comp, d, "agrees" if ok else "DIFFERS"])

    print("wrote %s (%d lines)" % (OUT.name, len(L)))
    print("wrote %s" % CHECKS_CSV.name)
    print("  reconciliation : %d of %d agree" % (n_ok, len(CHECKS)))
    for label, rep, comp, tol in CHECKS:
        if abs(float(comp) - float(rep)) > tol:
            print("  DIFFERS: %-45s reported=%s recomputed=%s"
                  % (label, rep, comp))


if __name__ == "__main__":
    main()
