# -*- coding: utf-8 -*-
r"""
make_appendix_b.py -- build "Appendix B: Raw Data and Tables".

Appendix A is the photodocumentation (PHOTODOC_APPENDIX_PLAN.md) and Appendix C
re-derives every reported statistic with the arithmetic shown
(make_appendix_c.py). This script fills the gap between them: the unit-level
observations themselves, listed in full, with a manifest that fingerprints every
source file and a dictionary that defines every column and its unit.

Nothing here is an analysis. Every value is transcribed by machine from the
archive in data/; no number is typed by hand, and no number is copied from the
manuscript. The printed tables are rounded for legibility, and each one is
exported alongside at full archived precision to appendix_b/*.csv so a reader can
recompute from the same digits the analysis used.

The default output is tables and nothing else: a one-paragraph header, then
seventeen labelled tables. Pass --notes for the annotated variant, which adds an
explanatory note under each table (what the quantity is, how it was screened,
what it may not be read as) and a per-table pointer to its CSV. The tables are
byte-identical between the two; only the prose differs.

    python scripts/make_appendix_b.py
    python scripts/make_appendix_b.py --notes

Writes APPENDIX_B_RAW_DATA.md and appendix_b/B*.csv.  ASCII-only stdout.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT_MD = ROOT / "APPENDIX_B_RAW_DATA.md"
OUT_DIR = ROOT / "appendix_b"

L: list[str] = []
EXPORTS: list[tuple[str, str, int]] = []   # (csv name, table id, n rows)

# Default output is tables only. --notes adds the explanatory note under each
# table and the per-table pointer to its CSV; the tables themselves are
# identical either way.
NOTES = "--notes" in sys.argv


# --------------------------------------------------------------------------
# emit helpers
# --------------------------------------------------------------------------

def w(s: str = "") -> None:
    L.append(s)


def load(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def J(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def num(row: dict, key: str):
    """Archived value as float, or None when absent/blank/NaN."""
    v = (row.get(key) or "").strip()
    if not v:
        return None
    try:
        f = float(v)
    except ValueError:
        return None
    return None if f != f else f


DASH = "\u2014"


def f4(x, dp: int = 4):
    return DASH if x is None else ("%." + str(dp) + "f") % x


def i0(x):
    return DASH if x is None else "{:,}".format(int(round(x)))


def sci(x, dp: int = 3):
    return DASH if x is None else ("%." + str(dp) + "e") % x


def esc(c) -> str:
    """Markdown cell: a literal pipe must not be read as a column break."""
    return "" if c is None else str(c).replace("|", r"\|")


def table(tid: str, title: str, headers, rows_md, csv_name: str,
          csv_headers=None, rows_csv=None, aligns=None, note: str = "") -> None:
    """Emit one appendix table as markdown and as a full-precision CSV."""
    w("**Table %s**" % tid)
    w()
    w("*%s*" % title)
    w()
    if aligns is None:
        aligns = ["---"] + ["---:"] * (len(headers) - 1)
    w("| " + " | ".join(esc(h) for h in headers) + " |")
    w("|" + "|".join(aligns) + "|")
    for r in rows_md:
        w("| " + " | ".join(esc(c) for c in r) + " |")
    w()
    if note and NOTES:
        w(note)
        w()

    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / csv_name
    ch = csv_headers if csv_headers is not None else headers
    body = rows_csv if rows_csv is not None else rows_md
    with path.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(ch)
        for r in body:
            wr.writerow(["" if c is None else c for c in r])
    EXPORTS.append((csv_name, tid, len(body)))
    if NOTES:
        w("Machine-readable copy at full archived precision: `appendix_b/%s` "
          "(%d rows)." % (csv_name, len(body)))
        w()
    w("---")
    w()


def sha16(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def rowcount(path: Path) -> str:
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as fh:
            return "{:,}".format(max(0, sum(1 for _ in fh) - 1))
    return DASH


# --------------------------------------------------------------------------
# descriptive statistics
# --------------------------------------------------------------------------

STATS: list[tuple] = []


def describe(label: str, source: str, values, dp: int = 4) -> None:
    v = np.asarray([x for x in values if x is not None], dtype=float)
    if v.size == 0:
        return
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    fmt = ("%." + str(dp) + "f")
    big = ["N", "E"]
    g = (lambda x: "{:,}".format(int(round(x)))) if label.split(" ")[0] in big \
        else (lambda x: fmt % x)
    STATS.append((label, source, "{:,}".format(v.size), g(v.min()), g(q1),
                  g(med), g(q3), g(v.max()), g(v.mean()),
                  g(v.std(ddof=1)) if v.size > 1 else DASH))


# --------------------------------------------------------------------------
def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    master = sorted(load(DATA / "analysis_master.csv"), key=lambda r: r["name"])
    annot = {r["name"]: r for r in load(DATA / "characterization_annotated.csv")}
    cohort = sorted(load(DATA / "cohort_pc.csv"), key=lambda r: r["species"])
    sugg = sorted(load(DATA / "cohort_suggested.csv"), key=lambda r: r["species"])
    crit = sorted(load(DATA / "criterion_and_locality.csv"),
                  key=lambda r: r["species"])
    grid = load(DATA / "synthetic_grid_pc.csv")
    edge = sorted(load(DATA / "random_edge_control.csv"),
                  key=lambda r: r["species"])
    sink = load(DATA / "sink_sweep.csv")
    kleaf = sorted(load(DATA / "kleaf_validation.csv"), key=lambda r: r["spp_code"])
    conv = {r["spp_code"]: r for r in load(DATA / "resistance_convention_sensitivity.csv")}
    bound = sorted(load(DATA / "boundary_check.csv"), key=lambda r: r["name"])
    sigmoid = load(DATA / "csv" / "sigmoid.csv")
    prov = J("cohort_provenance.json")
    summ = J("summary.json")
    npz = np.load(DATA / "results.npz")
    spp = {r["spp_code"]: r for r in load(ROOT / "UCBG_122spp_list (1).csv")}

    in100 = {r["name"] for r in master if r["in_percolation_cohort_100"] == "True"}
    in105 = {r["name"] for r in master if r["in_enhancement_cohort_105"] == "True"}
    in112 = {r["name"] for r in master if r["in_characterization_112"] == "True"}

    # ---------------- front matter ----------------------------------------
    w("# Appendix B — Raw Data and Tables")
    w()
    w("Tables only. Every value is transcribed by machine from the archive in "
      "`data/` by `scripts/make_appendix_b.py`. Venation tracings: Matos et "
      "al. (2024), doi:10.5061/dryad.1g1jwsv36; all derived values are the "
      "author's own computation (Table B4 gives the origin of each column). "
      "Unit of observation: one leaf-venation network, except Tables B11, B13 "
      "and B14. Printed values are rounded; `appendix_b/*.csv` carries full "
      "archived precision. %s denotes a value absent from the archive." % DASH)
    w()
    w("---")
    w()

    # ---------------- B1 manifest -----------------------------------------
    MANIFEST = [
        ("data/analysis_master.csv", "build_analysis_master.py",
         "Merged per-leaf master table; source of Tables B6 and B7"),
        ("data/characterization_annotated.csv", "run_quality_check.py",
         "Graph descriptors joined to the deposit's extraction-quality flags"),
        ("data/cohort_pc.csv", "run_cohort_percolation.py",
         "Percolation thresholds, 100-leaf cohort (Table B8)"),
        ("data/cohort_suggested.csv", "run_cohort_suggested.py",
         "Reticulation-enhancement thresholds (Table B9)"),
        ("data/criterion_and_locality.csv", "run_criterion_and_locality.py",
         "Thresholds under four damage criteria (Table B10)"),
        ("data/synthetic_grid_pc.csv", "run_synthetic_grid.py",
         "Synthetic mesh sweep, 42 cells (Table B11)"),
        ("data/random_edge_control.csv", "run_random_edge_control.py",
         "Matched-edge-count control, incomplete (Table B12)"),
        ("data/sink_sweep.csv", "dump_sink_sweep.py",
         "Haustorial-sink gradient sweep (Table B13)"),
        ("data/csv/sigmoid.csv", "export_csv.py",
         "The 1,000,000-trial collapse curve (Table B14)"),
        ("data/results.npz", "run_full.py",
         "Archived arrays of the synthetic reference run (Table B14)"),
        ("data/kleaf_validation.csv", "run_kleaf_validate.py",
         "Modelled conductance against measured K_leaf (Table B15)"),
        ("data/resistance_convention_sensitivity.csv",
         "run_resistance_convention_sensitivity.py",
         "The same networks under both resistance conventions (Table B15)"),
        ("data/boundary_check.csv", "run_boundary_check.py",
         "Crop-window edge diagnostics (Table B16)"),
        ("data/cohort_provenance.json", "build_analysis_master.py",
         "Cohort screening rules and exclusion reasons (Tables B2, B3)"),
        ("data/summary.json", "run_full.py",
         "Scalar companions to results.npz"),
    ]
    rows_md, rows_csv = [], []
    for rel, gen, what in MANIFEST:
        p = ROOT / rel
        if not p.exists():
            continue
        digest = sha16(p)
        size = p.stat().st_size
        rows_md.append(["`%s`" % rel, rowcount(p), "{:,}".format(size),
                        "`%s`" % digest, "`%s`" % gen])
        rows_csv.append([rel, rowcount(p).replace(",", ""), size, digest, gen,
                         what])
    table(
        "B1",
        "Source-File Manifest With SHA-256 Fingerprints",
        ["Source file", "Rows", "Bytes", "SHA-256 (first 16 hex)",
         "Written by"],
        rows_md, "B01_manifest.csv",
        csv_headers=["file", "rows", "bytes", "sha256_16", "written_by",
                     "contents"],
        rows_csv=rows_csv,
        aligns=["---", "---:", "---:", "---", "---"],
        note="*Note.* Row counts exclude the header line. The digest is the "
             "first 16 hexadecimal characters of the SHA-256 of the file as it "
             "stood when this appendix was generated; it is printed so that a "
             "reader can verify the file they are given is the file the tables "
             "were built from. `results.npz` is a binary array archive and has "
             "no row count. The `Written by` column names the script in "
             "`scripts/` that produces the file, never a script that merely "
             "reads it.")

    # ---------------- B2 cohorts ------------------------------------------
    rows = [
        ["Traced networks", "120", prov["traced"]["rule"], "none"],
        ["Characterization", "112", prov["characterization_112"]["rule"],
         ", ".join(prov["characterization_112"]["excluded"])],
        ["Percolation", "100", prov["percolation_cohort_100"]["rule"],
         ", ".join(sorted(in112 - in100))],
        ["Enhancement", "105", prov["enhancement_cohort_105"]["rule"],
         ", ".join(sorted(in112 - in105))],
    ]
    table(
        "B2",
        "Cohort Definitions, Screening Rules, and Every Excluded Network",
        ["Cohort", "n", "Screening rule as coded", "Excluded from the 112"],
        rows, "B02_cohorts.csv",
        aligns=["---", "---:", "---", "---"],
        note="*Note.* %s Trial budgets: %s Monte Carlo removal trials per leaf "
             "per attack mode in the percolation cohort, %s per leaf in the "
             "enhancement cohort, and %s trials on the single synthetic "
             "reference network, which is the only object evaluated at that "
             "budget and is not an empirical leaf. The five networks in the "
             "enhancement cohort but not the percolation cohort are %s. The "
             "rules are quoted as they are coded, and the script that "
             "implements each one is named in parentheses."
             % (prov["traced"]["note"],
                "{:,}".format(
                    prov["percolation_cohort_100"]["trials_per_leaf_per_mode"]),
                "{:,}".format(prov["enhancement_cohort_105"]["trials_per_leaf"]),
                "{:,}".format(
                    prov["synthetic_reference_network"]["trials"]["random"]),
                ", ".join(prov["enhancement_cohort_105"]["in_105_not_in_100"])))

    excl = prov["characterization_112"]["exclusion_reasons"]
    rows_ex = []
    clades: dict[str, int] = {}
    for code, reason in sorted(excl.items()):
        s = spp.get(code, {})
        rows_ex.append([code, "*%s*" % s.get("spp_name_WP", DASH),
                        s.get("clade", DASH), reason])
        clades[s.get("clade", "unknown")] = clades.get(s.get("clade",
                                                             "unknown"), 0) + 1
    clade_txt = ", ".join("%d %s" % (v, k) for k, v in
                          sorted(clades.items(), key=lambda kv: -kv[1]))
    table(
        "B3",
        "Networks Excluded at Screening (n = %d)" % len(rows_ex),
        ["Code", "Species", "Clade", "Reason recorded at screening"],
        rows_ex, "B03_exclusions.csv",
        csv_headers=["spp_code", "species", "clade", "reason"],
        rows_csv=[[c, spp.get(c, {}).get("spp_name_WP", ""),
                   spp.get(c, {}).get("clade", ""), r]
                  for c, r in sorted(excl.items())],
        aligns=["---", "---", "---", "---"],
        note="*Note.* Every exclusion at this stage is a size threshold applied "
             "before any analysis: a network of fewer than 500 traced veins "
             "cannot support a stable descriptor estimate. The rule is "
             "mechanical and was fixed in advance, so no network is dropped on "
             "the basis of its result. The set removed is **not taxonomically "
             "random** (%s in the deposit's own clade column), which is one "
             "reason no claim in this study is made about the flora as a whole. "
             "The further exclusions that separate the 105- and 100-network "
             "cohorts from the 112 are listed in Table B2." % clade_txt)

    # ---------------- B3 column dictionary --------------------------------
    DICT = [
        ("Species code", "Four-plus-three-letter code of the source leaf",
         "%s" % DASH, "Deposit", "B3, B5-B10, B12, B15, B16"),
        ("N", "Nodes in the extracted graph: vein junctions and endpoints",
         "count", "Computed", "B6, B8-B12, B15"),
        ("E", "Edges in the extracted graph: vein segments between nodes",
         "count", "Computed", "B6, B8, B15"),
        ("<k>", "Mean degree, 2E/N", "dimensionless", "Computed",
         "B6, B8, B9, B11, B16"),
        ("SD(k)", "Standard deviation of the node degrees", "dimensionless",
         "Computed", "B6"),
        ("D", "Box-counting fractal dimension of the traced network",
         "dimensionless", "Computed", "B6, B8, B11"),
        ("Loop fraction", "Fraction of edges that are not bridges "
         "(the canonical definition used throughout this study)",
         "fraction", "Computed", "B7, B8, B11"),
        ("Bridge fraction", "Fraction of edges whose removal disconnects the "
         "graph; 1 - loop fraction", "fraction", "Computed", "B7"),
        ("Terminal fraction", "Fraction of nodes of degree 1", "fraction",
         "Computed", "B7"),
        ("Cycles", "Cycle rank, E - N + components", "count", "Computed", "B7"),
        ("Components", "Connected components in the extracted graph", "count",
         "Computed", "B7"),
        ("GCC fraction", "Nodes in the giant connected component, as a fraction "
         "of N, before any removal", "fraction", "Computed", "B7"),
        ("K (model units)", "Conductance of the undamaged network, solved by "
         "Kirchhoff assembly", "model units", "Computed", "B7"),
        ("Quality", "Extraction-defect flags carried by the deposit: A clean, "
         "B missing veins, C spurious veins, D damage. Comma-separated codes "
         "are defect *types*, not severity levels", "code", "Deposit", "B6"),
        ("Resolution", "Calibration of the source image", "mm per pixel",
         "Deposit", "B6"),
        ("p_c (random)", "Removed-node fraction at which the giant component "
         "first falls below half its undamaged size, uniform random removal, "
         "P = .50", "fraction of nodes", "Computed", "B8, B11"),
        ("p_c (degree)", "The same threshold under degree-weighted stochastic "
         "removal", "fraction of nodes", "Computed", "B8, B11"),
        ("Trials", "Monte Carlo removal trials behind the threshold in that row",
         "count", "Computed", "B8"),
        ("<k> suggested", "Mean degree after shortest-first Delaunay areole "
         "closures are added to the leaf's own coordinates", "dimensionless",
         "Computed", "B9"),
        ("Loops added", "Edges added by the enhancement", "count", "Computed",
         "B9"),
        ("delta p_c", "p_c (suggested) - p_c (current), the within-network "
         "change", "fraction of nodes", "Computed", "B9"),
        ("Root rule", "Rule that selects the source node under the "
         "source-anchored criterion", "%s" % DASH, "Computed", "B10"),
        ("p_c (source)", "Threshold under the source-anchored criterion: loss "
         "of connection to the widest-vein root", "fraction of nodes",
         "Computed", "B10"),
        ("p_c (disc 1 / disc 10)", "Threshold under localised damage: removal "
         "of one, or ten, contiguous discs rather than dispersed nodes",
         "fraction of nodes", "Computed", "B10"),
        ("Edges added", "Edges added by the control, matched across all four "
         "arms of that row", "count", "Computed", "B12"),
        ("Gradient", "Imposed host-parasite water-potential difference", "MPa",
         "Stipulated", "B13"),
        ("psi", "Water potential", "MPa", "Computed", "B13"),
        ("Embolised", "Vessels whose potential falls below the modelled "
         "cavitation threshold", "count", "Computed", "B13"),
        ("Diversion fraction", "Share of the network's through-flow entering "
         "the haustorial sink", "fraction", "Computed", "B13"),
        ("rho", "Fraction of nodes removed in a trial", "fraction", "Computed",
         "B14"),
        ("P(collapse)", "Fraction of trials at that rho in which the giant "
         "component fell below half its undamaged size", "probability",
         "Computed", "B14"),
        ("K_model", "Network conductance solved by Kirchhoff assembly under the "
         "stated resistance convention", "model units", "Computed", "B15"),
        ("K_leaf measured", "Leaf hydraulic conductance from the published "
         "compilation", "mmol m^-2 s^-1 MPa^-1", "Literature", "B15"),
        ("Mean-degree shift", "|<k> of the whole window - <k> of its interior|, "
         "a crop-edge artefact diagnostic", "dimensionless", "Computed", "B16"),
        ("Boundary-terminal fraction", "Degree-1 nodes lying on the crop "
         "boundary, as a fraction of all nodes", "fraction", "Computed", "B16"),
    ]
    table(
        "B4",
        "Data Dictionary: Column, Unit, and Origin",
        ["Column", "Definition", "Unit", "Origin", "Appears in"],
        [[a, b, c, d, e] for a, b, c, d, e in DICT],
        "B04_dictionary.csv",
        csv_headers=["column", "definition", "unit", "origin", "appears_in"],
        aligns=["---", "---", "---", "---", "---"],
        note="*Note.* **Origin** is the provenance boundary of this study. "
             "*Deposit* means the value is carried by the third-party Matos "
             "deposit and is reproduced unchanged. *Computed* means the value "
             "is produced by this study's code from the deposited tracings. "
             "*Literature* means a published measurement used only for "
             "validation. *Stipulated* means a modelling input the author set. "
             "Model conductances are reported in the solver's own units and are "
             "meaningful only as ranks or ratios; the model and the measurement "
             "in Table B15 are not in commensurable units, which is why they "
             "are compared by Spearman rank correlation and never by "
             "difference.")

    # ---------------- B4 species key --------------------------------------
    rows_md, rows_csv = [], []
    for r in master:
        code = r["name"]
        s = spp.get(code, {})
        memb = "+".join([c for c, m in (("100", in100), ("105", in105),
                                        ("112", in112)) if code in m]) or "120 only"
        rows_md.append([code, "*%s*" % s.get("spp_name_WP", DASH),
                        s.get("family_WP", DASH), s.get("order_apg4", DASH),
                        s.get("growth_form", DASH), memb])
        rows_csv.append([code, s.get("spp_name_WP", ""), s.get("family_WP", ""),
                         s.get("order_apg4", ""), s.get("clade", ""),
                         s.get("growth_form", ""), s.get("accession_number", ""),
                         s.get("sampling_date_YYYYMMDD", ""), memb])
    table(
        "B5",
        "Species Key and Cohort Membership (n = %d)" % len(rows_md),
        ["Code", "Species", "Family", "Order", "Growth form", "Cohorts"],
        rows_md, "B05_species_key.csv",
        csv_headers=["spp_code", "species", "family", "order", "clade",
                     "growth_form", "ucbg_accession", "sampling_date",
                     "cohorts"],
        rows_csv=rows_csv,
        aligns=["---", "---", "---", "---", "---", "---"],
        note="*Note.* Taxonomy, accession numbers and collection dates are the "
             "deposit's own metadata, reproduced without amendment. The "
             "deposit's species list carries 122 codes; `Auc_jap` and `Nym` "
             "have no traced network in the downloaded archive and therefore "
             "appear nowhere in this study. The cohort column reads as "
             "membership of the nested cohorts of Table B2; `120 only` marks a "
             "network too small to enter even the characterization set.")

    # ---------------- B5 structure ----------------------------------------
    rows_md, rows_csv = [], []
    for r in master:
        a = annot.get(r["name"], {})
        rows_md.append([r["name"], i0(num(r, "n_nodes")), i0(num(r, "n_edges")),
                        f4(num(r, "mean_degree")), f4(num(r, "degree_sd")),
                        f4(num(r, "D")), r["quality"],
                        f4(num(a, "resolution_mm_px"), 5)])
        rows_csv.append([r["name"], r["n_nodes"], r["n_edges"],
                         r["mean_degree"], r["degree_sd"], r["D"], r["quality"],
                         a.get("resolution_mm_px", "")])
    table(
        "B6",
        "Raw Structure (a): Size, Degree, Fractal Dimension, Extraction "
        "Quality (n = %d)" % len(rows_md),
        ["Code", "N", "E", "<k>", "SD(k)", "D", "Quality", "mm/px"],
        rows_md, "B06_structure.csv",
        csv_headers=["spp_code", "n_nodes", "n_edges", "mean_degree",
                     "degree_sd", "D", "quality", "resolution_mm_px"],
        rows_csv=rows_csv,
        aligns=["---", "---:", "---:", "---:", "---:", "---:", "---", "---:"],
        note="*Note.* Quality codes are the deposit's extraction-defect flags "
             "and decode as A clean, B missing veins, C spurious veins, D "
             "damage; a comma-separated code carries more than one defect type "
             "and is **not** a severity ranking. Because the archive retains "
             "only the leading flag in some derived tables, subset analyses in "
             "the manuscript are defined on flag *presence*, not on the leading "
             "flag. One hundred of the 120 source files are calibrated crop "
             "windows rather than entire laminae, so N and E bound the traced "
             "window and not the whole leaf.")

    rows_md, rows_csv = [], []
    for r in master:
        a = annot.get(r["name"], {})
        rows_md.append([r["name"], f4(num(r, "loop_fraction_nonbridge")),
                        f4(num(r, "bridge_fraction")),
                        f4(num(r, "terminal_fraction")), i0(num(r, "n_cycles")),
                        i0(num(a, "n_components")), f4(num(r, "gcc_fraction")),
                        sci(num(r, "effective_conductance"))])
        rows_csv.append([r["name"], r["loop_fraction_nonbridge"],
                         r["bridge_fraction"], r["terminal_fraction"],
                         r["n_cycles"], a.get("n_components", ""),
                         r["gcc_fraction"], r["effective_conductance"]])
    table(
        "B7",
        "Raw Structure (b): Reticulation, Fragmentation, Undamaged "
        "Conductance (n = %d)" % len(rows_md),
        ["Code", "Loop frac.", "Bridge frac.", "Terminal frac.", "Cycles",
         "Comp.", "GCC frac.", "K (model units)"],
        rows_md, "B07_connectivity.csv",
        csv_headers=["spp_code", "loop_fraction_nonbridge", "bridge_fraction",
                     "terminal_fraction", "n_cycles", "n_components",
                     "gcc_fraction", "effective_conductance"],
        rows_csv=rows_csv,
        aligns=["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
        note="*Note.* Loop fraction is the **non-bridge edge fraction**, the "
             "canonical definition used in every table of this study; it is a "
             "different quantity from the cycle-rank fraction and the two are "
             "not interchangeable. Cycles is the cycle rank E - N + components. "
             "Sixty-one networks have more than one component, which is why the "
             "components column must be carried whenever the cycle rank is "
             "used. Conductance is solved on the undamaged network in the "
             "model's own units and is comparable across rows but not against "
             "any measured conductance.")

    describe("N (nodes)", "B6", [num(r, "n_nodes") for r in master], 0)
    describe("E (edges)", "B6", [num(r, "n_edges") for r in master], 0)
    describe("<k> mean degree", "B6", [num(r, "mean_degree") for r in master])
    describe("SD(k)", "B6", [num(r, "degree_sd") for r in master])
    describe("D fractal dimension", "B6", [num(r, "D") for r in master])
    describe("Loop fraction", "B7",
             [num(r, "loop_fraction_nonbridge") for r in master])
    describe("Terminal fraction", "B7",
             [num(r, "terminal_fraction") for r in master])
    describe("GCC fraction", "B7", [num(r, "gcc_fraction") for r in master])

    # ---------------- B7 percolation cohort --------------------------------
    rows_md, rows_csv = [], []
    for r in cohort:
        rows_md.append([r["species"], i0(num(r, "n_nodes")),
                        i0(num(r, "n_edges")), f4(num(r, "mean_degree")),
                        f4(num(r, "loop_fraction")), f4(num(r, "D")),
                        f4(num(r, "pc_random")), f4(num(r, "pc_degree")),
                        i0(num(r, "n_trials"))])
        rows_csv.append([r["species"], r["n_nodes"], r["n_edges"],
                         r["mean_degree"], r["loop_fraction"], r["D"],
                         r["quality"], r["pc_random"], r["pc_degree"],
                         r["n_trials"], r["seconds"]])
    table(
        "B8",
        "Raw Percolation Thresholds Under Dispersed Random and "
        "Degree-Weighted Removal (n = %d)" % len(rows_md),
        ["Code", "N", "E", "<k>", "Loop frac.", "D", "p_c random",
         "p_c degree", "Trials"],
        rows_md, "B08_percolation_cohort.csv",
        csv_headers=["spp_code", "n_nodes", "n_edges", "mean_degree",
                     "loop_fraction", "D", "quality", "pc_random", "pc_degree",
                     "n_trials", "seconds"],
        rows_csv=rows_csv,
        note="*Note.* p_c is the fraction of **nodes** removed at which the "
             "giant connected component first falls below half its undamaged "
             "size in at least 50%% of trials. Removal is weighted stochastic, "
             "not rank-ordered deletion: under the degree-weighted mode each "
             "node is removed with probability proportional to its degree, "
             "clipped at unity. Every row rests on %s independent Monte Carlo "
             "trials per mode under common random numbers. The loop-fraction "
             "column in this file is the cycle-tagged variant carried by the "
             "percolation script; Table B7 carries the canonical non-bridge "
             "loop fraction for the same networks."
             % "{:,}".format(int(num(cohort[0], "n_trials"))))

    describe("p_c random", "B8", [num(r, "pc_random") for r in cohort])
    describe("p_c degree-weighted", "B8", [num(r, "pc_degree") for r in cohort])

    # ---------------- B8 enhancement ---------------------------------------
    rows_md, rows_csv = [], []
    for r in sugg:
        code = r["species"]
        mark = "" if code in in105 else " " + "\u2020"
        rows_md.append([code + mark, i0(num(r, "N")), f4(num(r, "k_current")),
                        f4(num(r, "k_suggested")), i0(num(r, "loops_added")),
                        f4(num(r, "pc_current")), f4(num(r, "pc_suggested")),
                        f4(num(r, "delta_pc"))])
        rows_csv.append([code, "1" if code in in105 else "0", r["N"], r["E"],
                         r["k_current"], r["k_suggested"], r["loops_current"],
                         r["loops_added"], r["D"], r["quality"],
                         r["pc_current"], r["pc_suggested"], r["delta_pc"]])
    table(
        "B9",
        "Raw Reticulation Enhancement: Threshold Before and After Delaunay "
        "Areole Closure (n = %d listed, %d analysed)" % (len(rows_md), len(in105)),
        ["Code", "N", "<k> current", "<k> suggested", "Loops added",
         "p_c current", "p_c suggested", "delta p_c"],
        rows_md, "B09_enhancement.csv",
        csv_headers=["spp_code", "in_enhancement_cohort_105", "N", "E",
                     "k_current", "k_suggested", "loops_current", "loops_added",
                     "D", "quality", "pc_current", "pc_suggested", "delta_pc"],
        rows_csv=rows_csv,
        note="*Note.* %s marks a network present in the file but **outside** "
             "the analysed enhancement cohort of 105, which is screened at "
             "N >= 1,000 and current p_c >= 0.02; those rows are printed for "
             "completeness and enter no reported statistic. The enhancement is "
             "a **within-network** perturbation: edges are added to the leaf's "
             "own traced coordinates by shortest-first Delaunay closure of "
             "existing areoles, so each network serves as its own control and "
             "delta p_c is a paired difference. Every threshold in this table "
             "is measured under dispersed uniform random removal at %s trials "
             "per network." % (
                 "\u2020",
                 "{:,}".format(prov["enhancement_cohort_105"]["trials_per_leaf"])))

    d105 = [num(r, "delta_pc") for r in sugg if r["species"] in in105]
    describe("<k> before enhancement", "B9",
             [num(r, "k_current") for r in sugg if r["species"] in in105])
    describe("<k> after enhancement", "B9",
             [num(r, "k_suggested") for r in sugg if r["species"] in in105])
    describe("p_c before enhancement", "B9",
             [num(r, "pc_current") for r in sugg if r["species"] in in105])
    describe("p_c after enhancement", "B9",
             [num(r, "pc_suggested") for r in sugg if r["species"] in in105])
    describe("delta p_c", "B9", d105)

    # ---------------- B9 criterion and locality ----------------------------
    rows_md, rows_csv = [], []
    for r in crit:
        rows_md.append([r["species"], i0(num(r, "N")), r["root_rule"],
                        f4(num(r, "pc_gcc")), f4(num(r, "pc_source")),
                        f4(num(r, "pc_disc1")), f4(num(r, "pc_disc10")),
                        f4(num(r, "pc_archived"))])
        rows_csv.append([r["species"], r["N"], r["E"], r["root_rule"],
                         r["pc_gcc"], r["pc_source"], r["pc_disc1"],
                         r["pc_disc10"], r["pc_archived"], r["seconds"]])
    table(
        "B10",
        "Raw Thresholds Under Four Damage Criteria (n = %d)" % len(rows_md),
        ["Code", "N", "Root rule", "p_c GCC", "p_c source", "p_c 1 disc",
         "p_c 10 discs", "p_c archived"],
        rows_md, "B10_criterion_locality.csv",
        csv_headers=["spp_code", "N", "E", "root_rule", "pc_gcc", "pc_source",
                     "pc_disc1", "pc_disc10", "pc_archived", "seconds"],
        rows_csv=rows_csv,
        aligns=["---", "---:", "---", "---:", "---:", "---:", "---:", "---:"],
        note="*Note.* All four columns are dispersed-versus-localised variants "
             "of the same measurement on the same graph. *GCC* is the giant "
             "component criterion of Table B8, recomputed here by an "
             "independent implementation; *source* requires connection to the "
             "widest-vein root node; *1 disc* and *10 discs* remove contiguous "
             "spatial discs rather than dispersed nodes. `p_c archived` is the "
             "value from Table B8 and is carried in the same row so that the "
             "re-implementation can be checked against the original line by "
             "line. Localised damage is markedly less severe than dispersed "
             "damage at equal removed fraction, which is why the two criteria "
             "are never pooled.")

    describe("p_c GCC criterion", "B10", [num(r, "pc_gcc") for r in crit])
    describe("p_c source-anchored", "B10", [num(r, "pc_source") for r in crit])
    describe("p_c localised, 1 disc", "B10", [num(r, "pc_disc1") for r in crit])
    describe("p_c localised, 10 discs", "B10",
             [num(r, "pc_disc10") for r in crit])

    # ---------------- B10 synthetic grid -----------------------------------
    rows_md, rows_csv = [], []
    for r in grid:
        rows_md.append([r["idx"], f4(num(r, "req_mean_degree"), 2),
                        r["generations"], i0(num(r, "N")), f4(num(r, "mean_degree")),
                        f4(num(r, "D")), f4(num(r, "loop_fraction")),
                        f4(num(r, "pc_random"), 5), f4(num(r, "pc_degree"), 5)])
        rows_csv.append([r["idx"], r["req_mean_degree"], r["generations"],
                         r["N"], r["E"], r["mean_degree"], r["D"],
                         r["loop_fraction"], r["pc_random"], r["pc_degree"],
                         r["seconds"]])
    table(
        "B11",
        "Raw Synthetic Mesh Sweep, Mean-Degree x Generation Grid "
        "(n = %d cells)" % len(rows_md),
        ["Cell", "Requested <k>", "Gen.", "N", "Realised <k>", "D",
         "Loop frac.", "p_c random", "p_c degree"],
        rows_md, "B11_synthetic_grid.csv",
        csv_headers=["idx", "req_mean_degree", "generations", "N", "E",
                     "mean_degree", "D", "loop_fraction", "pc_random",
                     "pc_degree", "seconds"],
        rows_csv=rows_csv,
        note="*Note.* The unit of observation here is one **generated** "
             "network, not a leaf. Requested mean degree is the generator's "
             "input; realised mean degree is what the planar mesh actually "
             "achieved and is the value used in every analysis. This sweep is "
             "the study's structural control: it varies connectivity and "
             "fractal dimension independently of any biological covariate, at "
             "sizes chosen to bracket the empirical cohort.")

    describe("Synthetic p_c random", "B11", [num(r, "pc_random") for r in grid],
             5)
    describe("Synthetic realised <k>", "B11",
             [num(r, "mean_degree") for r in grid])

    # ---------------- B11 random-edge control -------------------------------
    rows_md, rows_csv = [], []
    for r in edge:
        rows_md.append([r["species"], i0(num(r, "N")), i0(num(r, "edges_added")),
                        f4(num(r, "pc_current"), 5), f4(num(r, "pc_delaunay"), 5),
                        f4(num(r, "pc_rand_del"), 5),
                        f4(num(r, "pc_rand_any"), 5)])
        rows_csv.append([r["species"], r["N"], r["E"], r["k_current"],
                         r["D"], r["quality"], r["edges_added"],
                         r["pc_current"], r["pc_delaunay"], r["pc_rand_del"],
                         r["pc_rand_any"], r["d_delaunay"], r["d_rand_del"],
                         r["d_rand_any"], r["seconds"]])
    table(
        "B12",
        "Raw Matched-Edge-Count Control, Four Placement Arms (n = %d of 105 "
        "completed)" % len(rows_md),
        ["Code", "N", "Edges added", "p_c current", "p_c Delaunay",
         "p_c random-Delaunay", "p_c random-any"],
        rows_md, "B12_random_edge_control.csv",
        csv_headers=["spp_code", "N", "E", "k_current", "D", "quality",
                     "edges_added", "pc_current", "pc_delaunay", "pc_rand_del",
                     "pc_rand_any", "d_delaunay", "d_rand_del", "d_rand_any",
                     "seconds"],
        rows_csv=rows_csv,
        note="*Note.* **This control is incomplete.** %d of 105 networks have "
             "run; the file is append-only and resumable, and the remaining "
             "networks are still outstanding at the time this appendix was "
             "generated. The listed rows are reported here as raw data and no "
             "inference in the manuscript rests on them. All four arms add the "
             "**same number of edges** to the same network under common random "
             "numbers, so the arms differ only in where the edges are placed: "
             "shortest-first Delaunay closure, a random subset of the Delaunay "
             "candidate set, or an unrestricted random node pair."
             % len(rows_md))

    # ---------------- B12 sink sweep ---------------------------------------
    rows_md, rows_csv = [], []
    for r in sink:
        rows_md.append([f4(num(r, "gradient_MPa"), 2),
                        f4(num(r, "psi_parasite_MPa")),
                        f4(num(r, "min_psi_MPa")),
                        f4(num(r, "margin_to_cavitation_MPa")),
                        i0(num(r, "n_embolized")),
                        f4(num(r, "embolized_fraction")),
                        f4(num(r, "diversion_fraction"))])
        rows_csv.append([r["gradient_MPa"], r["psi_parasite_MPa"],
                         r["min_psi_MPa"], r["margin_to_cavitation_MPa"],
                         r["n_embolized"], r["embolized_fraction"],
                         r["diversion_fraction"]])
    table(
        "B13",
        "Raw Haustorial-Sink Gradient Sweep (n = %d steps)" % len(rows_md),
        ["Gradient (MPa)", "psi parasite (MPa)", "Min psi (MPa)",
         "Margin (MPa)", "Embolised", "Embolised frac.", "Diversion frac."],
        rows_md, "B13_sink_sweep.csv",
        csv_headers=["gradient_MPa", "psi_parasite_MPa", "min_psi_MPa",
                     "margin_to_cavitation_MPa", "n_embolized",
                     "embolized_fraction", "diversion_fraction"],
        rows_csv=rows_csv,
        note="*Note.* The unit of observation is one imposed gradient on the "
             "cohort-calibrated synthetic mesh (N = 1,023), not a leaf. The "
             "gradient is a **stipulated modelling input** swept far beyond any "
             "measured host-parasite difference, which is why the high rows "
             "must not be read as observations. The sweep is reported in full "
             "precisely because it shows the sink's effect on the network "
             "minimum potential to be small and linear in the gradient over the "
             "whole range.")

    # ---------------- B13 collapse curve -----------------------------------
    trho = npz["targeted_rhos"]
    tpc = npz["targeted_p_collapse"]
    rows_md, rows_csv = [], []
    for i, r in enumerate(sigmoid):
        tr = trho[i] if i < len(trho) else None
        tp = tpc[i] if i < len(tpc) else None
        rows_md.append([f4(num(r, "rho"), 6), f4(num(r, "p_collapse"), 6),
                        f4(num(r, "gcc_fraction"), 6),
                        f4(float(tr) if tr is not None else None, 6),
                        f4(float(tp) if tp is not None else None, 6)])
        rows_csv.append([r["rho"], r["p_collapse"], r["gcc_fraction"],
                         "" if tr is None else float(tr),
                         "" if tp is None else float(tp)])
    table(
        "B14",
        "Raw Collapse Curve, Synthetic Reference Network: Random (1,000,000 "
        "Trials per Point) and Betweenness-Weighted (100,000), n = %d points"
        % len(rows_md),
        ["rho (random)", "P(collapse)", "GCC fraction", "rho (targeted)",
         "P(collapse) targeted"],
        rows_md, "B14_collapse_curve.csv",
        csv_headers=["rho_random", "p_collapse_random", "gcc_fraction",
                     "rho_targeted", "p_collapse_targeted"],
        rows_csv=rows_csv,
        note="*Note.* This is the only object in the study evaluated at "
             "%s trials; it is a generated mesh (N = %s, <k> = %.4f, D = %.4f) "
             "and **not** an empirical leaf. Reading down the P(collapse) "
             "column gives the threshold directly: p_c = %.5f, 95%% CI "
             "[%.5f, %.5f]. The targeted columns carry the "
             "betweenness-weighted curve at %s trials per point, whose "
             "threshold is %.5f nominal. Both curves are evaluated on the same "
             "50-point rho grid, which is why the two rho columns coincide "
             "exactly. Nominal and realised removed fractions "
             "differ under weighted removal because the per-node removal "
             "probability is clipped at unity."
             % ("{:,}".format(summ["n_trials"]),
                "{:,}".format(summ["network"]["n_nodes"]),
                summ["network"]["mean_degree"], summ["D"],
                summ["p_c_random"], summ["p_c_ci95"][0], summ["p_c_ci95"][1],
                "{:,}".format(summ["n_trials_targeted"]),
                summ["p_c_targeted_betweenness"]))

    # ---------------- B14 hydraulic validation ------------------------------
    rows_md, rows_csv = [], []
    for r in kleaf:
        c = conv.get(r["spp_code"], {})
        rows_md.append([r["spp_code"], i0(num(r, "N")), i0(num(r, "E")),
                        sci(num(r, "k_model")), sci(num(c, "k_model_r2")),
                        sci(num(r, "kleaf_meas")), r["n_meas"]])
        rows_csv.append([r["spp_code"], r["N"], r["E"], r["k_model"],
                         c.get("k_model_r2", ""), r["kleaf_meas"],
                         r["kleaf_area_meas"], r["n_meas"]])
    table(
        "B15",
        "Raw Hydraulic Validation: Modelled Conductance Under Both "
        "Conventions Against Measured K_leaf (n = %d species)" % len(rows_md),
        ["Code", "N", "E", "K model (l/r^4)", "K model (l/r^2)",
         "K_leaf measured", "n meas."],
        rows_md, "B15_hydraulic_validation.csv",
        csv_headers=["spp_code", "N", "E", "k_model_r4", "k_model_r2",
                     "kleaf_meas", "kleaf_area_meas", "n_meas"],
        rows_csv=rows_csv,
        note="*Note.* The two model columns are the same networks solved under "
             "the Hagen-Poiseuille convention (resistance proportional to "
             "l/r^4, used throughout this study) and under the deposit's own "
             "l/r^2 alternative. They are reported together because the choice "
             "of convention changes the absolute conductance by more than an "
             "order of magnitude while leaving the rank agreement with "
             "measurement essentially unchanged. Model and measurement are in "
             "**different units** and the comparison is therefore a rank "
             "correlation, never a difference: Spearman rho = %.3f, p = %.3f, "
             "n = %d. `n meas.` is the number of published measurements "
             "averaged for that species."
             % (J("kleaf_validation_summary.json")["spearman_rho"],
                J("kleaf_validation_summary.json")["spearman_p"],
                J("kleaf_validation_summary.json")["n_species"]))

    describe("K model (l/r^4)", "B15", [num(r, "k_model") for r in kleaf], 6)
    describe("K_leaf measured", "B15", [num(r, "kleaf_meas") for r in kleaf], 6)

    # ---------------- B15 boundary check ------------------------------------
    rows_md, rows_csv = [], []
    for r in bound:
        shift = num(r, "mean_degree_shift")
        btf = num(r, "boundary_terminal_frac")
        ok = "yes" if (shift is not None and btf is not None
                       and abs(shift) <= 0.05 and btf <= 0.05) else "**no**"
        rows_md.append([r["name"], "yes" if r["is_crop"] == "True" else "no",
                        f4(num(r, "mean_degree")),
                        f4(num(r, "mean_degree_interior")), f4(shift),
                        f4(btf), f4(num(r, "margin_frac"), 2), ok])
        rows_csv.append([r["name"], r["is_crop"], r["mean_degree"],
                         r["mean_degree_interior"], r["mean_degree_shift"],
                         r["boundary_terminal_frac"], r["boundary_node_frac"],
                         r["n_boundary_terminals"], r["n_interior_terminals"],
                         r["margin_frac"], "1" if ok == "yes" else "0"])
    n_ok = sum(1 for r in rows_md if r[-1] == "yes")
    table(
        "B16",
        "Raw Crop-Window Edge Diagnostics (n = %d; %d within both "
        "tolerances)" % (len(rows_md), n_ok),
        ["Code", "Crop", "<k> whole", "<k> interior", "Shift",
         "Boundary-term. frac.", "Margin", "Within tol."],
        rows_md, "B16_boundary_check.csv",
        csv_headers=["spp_code", "is_crop", "mean_degree",
                     "mean_degree_interior", "mean_degree_shift",
                     "boundary_terminal_frac", "boundary_node_frac",
                     "n_boundary_terminals", "n_interior_terminals",
                     "margin_frac", "within_tolerance"],
        rows_csv=rows_csv,
        aligns=["---", "---", "---:", "---:", "---:", "---:", "---:", "---"],
        note="*Note.* Cutting a leaf image into a window creates artificial "
             "vein endings at the cut edge, which would inflate the terminal "
             "fraction and depress the mean degree if it went unchecked. This "
             "table is that check: for every network the mean degree of the "
             "whole window is compared against the mean degree of its interior "
             "after a %.0f%% margin is discarded. The shift is reported signed, "
             "as archived, and the screening rule is applied to its absolute "
             "value: a network passes when |shift| <= 0.05 **and** the "
             "boundary-terminal fraction is <= 0.05. "
             "The %d networks outside tolerance are excluded from the "
             "percolation cohort by the screening rule of Table B2, so no "
             "reported threshold rests on a window whose edge artefacts were "
             "not bounded."
             % (100 * float(bound[0]["margin_frac"]), len(rows_md) - n_ok))

    describe("|mean-degree shift|", "B16",
             [None if num(r, "mean_degree_shift") is None
              else abs(num(r, "mean_degree_shift")) for r in bound], 5)
    describe("Boundary-terminal fraction", "B16",
             [num(r, "boundary_terminal_frac") for r in bound], 5)

    # ---------------- B17 descriptive statistics ----------------------------
    table(
        "B17",
        "Descriptive Statistics of Every Raw Variable Above",
        ["Variable", "Table", "n", "Min", "Q1", "Mdn", "Q3", "Max", "M", "SD"],
        [list(s) for s in STATS], "B17_descriptives.csv",
        csv_headers=["variable", "table", "n", "min", "q1", "median", "q3",
                     "max", "mean", "sd"],
        aligns=["---", "---", "---:", "---:", "---:", "---:", "---:", "---:",
                "---:", "---:"],
        note="*Note.* Computed here directly from the raw columns of Tables B6 "
             "to B16 by `scripts/make_appendix_b.py`; no value is copied from "
             "the Results. Quartiles use linear interpolation between order "
             "statistics and *SD* is the sample standard deviation (denominator "
             "n - 1). The rows drawn from Table B9 cover the analysed "
             "enhancement cohort of %d only, excluding the %s-marked networks. "
             "This table describes the distributions of the raw observations; "
             "it tests nothing, and every inferential statistic in the study is "
             "derived in Appendix C instead."
             % (len(in105), "\u2020"))

    # ---------------- closing ------------------------------------------------
    w("**Index of the machine-readable exports**")
    w()
    w("| File | Table | Rows |")
    w("|---|---|---:|")
    for name, tid, n in EXPORTS:
        w("| `appendix_b/%s` | %s | %s |" % (name, tid, "{:,}".format(n)))
    w()

    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    n_tables = sum(1 for line in L if line.startswith("**Table B"))
    print("wrote %s" % OUT_MD.name)
    print("  tables        : %d" % n_tables)
    print("  csv exports   : %d in appendix_b/" % len(EXPORTS))
    print("  data rows     : %d" % sum(n for _, _, n in EXPORTS))
    print("  descriptives  : %d variables" % len(STATS))


if __name__ == "__main__":
    main()
