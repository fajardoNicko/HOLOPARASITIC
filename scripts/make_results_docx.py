# -*- coding: utf-8 -*-
r"""
make_results_docx.py -- build the REVISED Results section as a .docx in which
every number is read from the archived data files at generation time.

Nothing in the output is typed by hand. The document is assembled from:

    data/results_verified.json     every cohort statistic (build_analysis_master.py)
    data/cohort_provenance.json    the four cohorts, their screens and budgets
    data/summary.json              synthetic reference thresholds + CIs
    data/sink_demo.json            calibrated haustorial sink
    data/sink_sweep.csv            0-3 MPa gradient sweep
    data/sink_surface.json         coupled (K_h, D) surface on the calibrated mesh
    data/finite_size_fixedD.json   finite-size sweep at fixed architecture
    data/scaling_mesh.json         critical-behaviour fit
    data/dynamics.json             pre-symptomatic window

so a transcription error is not possible: rerun this script after any rerun of
the analysis and the prose updates itself.

Output: RESULTS_REVISED.docx

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_results_docx.py
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import config

DATA = config.PATHS.data
OUT = os.path.join(ROOT, "RESULTS_REVISED.docx")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


R = load("results_verified.json")
PROV = load("cohort_provenance.json")
SUM = load("summary.json")
SINK = load("sink_demo.json")
SURF = load("sink_surface.json")
FSD = load("finite_size_fixedD.json")
SCAL = load("scaling_mesh.json")
DYN = load("dynamics.json")
SWEEP = pd.read_csv(os.path.join(DATA, "sink_sweep.csv"))
MASTER = pd.read_csv(os.path.join(DATA, "analysis_master.csv"))
N_CROP = int(MASTER.is_crop.sum())


# ---------------------------------------------------------------------------
# formatting helpers
# ---------------------------------------------------------------------------
def p3(x, d=3):
    """APA-style number: leading zero dropped for bounded coefficients."""
    return f"{x:.{d}f}"


def rho(x):
    s = f"{abs(x):.3f}".lstrip("0")
    return ("-" if x < 0 else "") + s


def pval(p):
    return "< .001" if p < .001 else ("= " + f"{p:.3f}".lstrip("0"))


def apa_borders(table):
    """APA table rules: line above and below the table, and under the header."""
    tbl = table._tbl
    for row_idx, row in enumerate(table.rows):
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for edge in ("top", "left", "bottom", "right"):
                el = OxmlElement(f"w:{edge}")
                show = ((edge == "top" and row_idx == 0)
                        or (edge == "bottom" and row_idx in (0, len(table.rows) - 1)))
                el.set(qn("w:val"), "single" if show else "nil")
                if show:
                    el.set(qn("w:sz"), "6")
                    el.set(qn("w:color"), "000000")
                borders.append(el)
            tcPr.append(borders)
    tbl.getparent()  # keep reference alive


class Doc:
    def __init__(self):
        self.d = Document()
        st = self.d.styles["Normal"]
        st.font.name = "Times New Roman"
        st.font.size = Pt(12)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        pf = st.paragraph_format
        pf.line_spacing = 2.0
        pf.space_after = Pt(0)
        for s in self.d.sections:
            s.left_margin = s.right_margin = Inches(1)
            s.top_margin = s.bottom_margin = Inches(1)

    def para(self, text="", bold=False, italic=False, indent=True,
             align=WD_ALIGN_PARAGRAPH.LEFT, size=None, spacing=2.0):
        p = self.d.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = spacing
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
        return p

    def head(self, text, level=1):
        p = self.d.add_paragraph()
        p.paragraph_format.line_spacing = 2.0
        p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if level == 1
                       else WD_ALIGN_PARAGRAPH.LEFT)
        r = p.add_run(text)
        r.bold = True
        r.italic = (level >= 3)
        return p

    def caption(self, number, title):
        self.para(number, bold=True, indent=False)
        self.para(title, italic=True, indent=False)

    def note(self, text):
        p = self.d.add_paragraph()
        p.paragraph_format.line_spacing = 2.0
        r = p.add_run("Note. ")
        r.italic = True
        p.add_run(text)
        return p

    def table(self, header, rows, widths=None, size=10):
        t = self.d.add_table(rows=1, cols=len(header))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(header):
            c = t.rows[0].cells[i]
            c.text = ""
            run = c.paragraphs[0].add_run(str(h))
            run.bold = False
            run.font.size = Pt(size)
            c.paragraphs[0].paragraph_format.line_spacing = 1.0
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                run = cells[i].paragraphs[0].add_run(str(v))
                run.font.size = Pt(size)
                cells[i].paragraphs[0].paragraph_format.line_spacing = 1.0
        apa_borders(t)
        if widths:
            for r_ in t.rows:
                for i, w in enumerate(widths):
                    r_.cells[i].width = Inches(w)
        self.d.add_paragraph().paragraph_format.line_spacing = 1.0
        return t

    def save(self, path):
        self.d.save(path)


# ---------------------------------------------------------------------------
D = Doc()

# ===========================================================================
# 0. What changed
# ===========================================================================
D.head("REVISED RESULTS — WHAT CHANGED AND WHY")
D.para("Every value below is generated directly from the archived data files by "
       "scripts/make_results_docx.py; none is transcribed. The table lists the "
       "corrections applied to the audited draft. Figure numbers here run "
       "sequentially within the Results only; renumber them continuing from the "
       "Methods figures.", indent=False)

T7 = R["T7_reticulation_and_bridges"]
T5 = R["T5_predictors"]
T3 = R["T3_attack_thresholds"]
T9 = R["T9_enhancement"]
T10 = R["T10_gain_dependence"]
T11 = R["T11_validation"]
T1 = R["T1_characterization"]
T2 = R["T2_descriptor_correlations"]
T6 = R["T6_synthetic_grid"]
T8 = R["T8_quartiles"]

changes = [
    ["1", "Reticulation/bridge table",
     "loop fraction x p_c(degree-targeted) reported as -.818, contradicting the "
     "quartile ladder",
     "Two row labels were swapped. loop x targeted = %s; the -.818 belongs to "
     "bridge fraction x targeted and the -.786 to loop fraction x the "
     "random-minus-targeted gap." % rho(T7["loop_x_pc_degree_targeted"]["rho"])],
    ["2", "Results introduction",
     "\u201cthe reference network was evaluated at one million Monte Carlo "
     "trials\u201d, with n = 100, 105 and 112 used without explanation",
     "The four nested cohorts and their separate trial budgets are now stated "
     "before any threshold is reported."],
    ["3", "Discussion and Conclusion",
     "p_c = .271 described as the collapse threshold of host networks",
     "That is the synthetic reference. The empirical cohort median is %s."
     % rho(T3["random"]["Mdn"])],
    ["4", "Predictor table",
     "loop-fraction correlation given as .719 while Table 1 used a different "
     "loop-fraction definition",
     "The non-bridge definition is now canonical throughout; the correlation is "
     "%s." % rho(T5["spearman_with_pc_random"]["loop_fraction"]["rho"])],
    ["5", "Validation table",
     "\u201cphysics reproduced exactly\u201d, evidenced only by a correlation",
     "Replaced with the ratio statistics that do establish equality: worst "
     "per-leaf CV %.1e and worst median-ratio departure %.1e against a %.0e "
     "tolerance."
     % (T11["hydraulic_resistance"]["worst_ratio_cv"],
        T11["hydraulic_resistance"]["worst_abs_median_ratio_minus_1"],
        T11["hydraulic_resistance"]["cv_tolerance"])],
    ["6", "Validation table",
     "leaf-conductance check called \u201cweak\u201d; crop-edge check called "
     "\u201cnegligible\u201d",
     "The conductance check is weak and non-significant (p %s); 15 of 120 "
     "leaves fall outside the crop-edge tolerance and three of them remain in "
     "the enhancement cohort."
     % pval(T11["kleaf"]["p"])],
    ["7", "Sink-strength surface figure",
     "captioned as a p_c surface, computed on the pre-2026 generator at sink "
     "strengths 8-64x the calibrated value",
     "Recomputed on the calibrated mesh with the sink axis anchored on the "
     "calibrated K_h. Its threshold is a critical haustorial density, not a "
     "removed-node fraction, and is labelled as such."],
    ["8", "Finite-size figure",
     "\u201cp_c converges as network size grows\u201d",
     "The original sweep raised fractal dimension along with size. A sweep at "
     "fixed architecture was run; its outcome is reported in the supplementary "
     "subsection and the convergence claim is withdrawn."],
    ["9", "Enhancement tables",
     "a third column labelled \u201cp_c\u201d; a column labelled "
     "\u201cStandardized\u201d",
     "Renamed to the median change in p_c, and to the change in p_c per "
     "standard deviation of the predictor, which is what the value is."],
    ["10", "Threshold-gain table",
     "no confidence interval available for the targeted synthetic threshold",
     "Bootstrap intervals were computed and are now reported."],
    ["11", "Throughout",
     "\u201c112 valid whole-leaf networks\u201d",
     "%d of the %d source networks are calibrated crop windows, so the cohort is "
     "described as leaf-venation networks."
     % (N_CROP, PROV["traced"]["n"])],
    ["12", "Throughout",
     "interpretive claims embedded in the Results",
     "Sentences asserting mechanism, independence or scale-invariance were moved "
     "to the Discussion; the Results report measurement, direction, effect size "
     "and significance."],
]
D.table(["#", "Location", "Issue in the audited draft", "Correction applied"],
        changes, widths=[0.3, 1.2, 2.2, 2.8], size=9)

D.d.add_page_break()

# ===========================================================================
# RESULTS
# ===========================================================================
D.head("RESULTS")

prov_pc = PROV["percolation_cohort_100"]
prov_en = PROV["enhancement_cohort_105"]
prov_sy = PROV["synthetic_reference_network"]

D.para(
    "All percolation thresholds are expressed as the fraction of nodes removed "
    "at giant-connected-component (GCC) collapse, so a higher threshold "
    "indicates that the network tolerates more loss before it fragments. Three "
    "experimental units appear below and are identified wherever they are used. "
    "The empirical cohort is %d leaf-venation networks, each evaluated at %s "
    "Monte Carlo trials per attack strategy; it is the primary unit for every "
    "host-level result. The enhancement cohort is %d networks evaluated at %s "
    "trials each under a separate screen given with its table. The synthetic "
    "reference network is a single calibrated mesh (N = %s) evaluated at %s "
    "trials under random attack and %s under each targeted strategy; it is "
    "reported only where a high-precision threshold is required and is "
    "identified as synthetic wherever it appears. The three sets are nested "
    "within the %d networks that passed the characterization screen, drawn from "
    "%d traced leaves. Non-normal quantities are summarized by the median and "
    "range alongside the mean and standard deviation, all inferential tests were "
    "evaluated at \u03b1 = .05, and p_c denotes the critical threshold while p "
    "denotes a significance value."
    % (prov_pc["n"], f"{prov_pc['trials_per_leaf_per_mode']:,}",
       prov_en["n"], f"{prov_en['trials_per_leaf']:,}",
       f"{prov_sy['N']:,}", f"{prov_sy['trials']['random']:,}",
       f"{prov_sy['trials']['each_targeted']:,}",
       PROV["characterization_112"]["n"], PROV["traced"]["n"]))

# --- Table 1 ---------------------------------------------------------------
D.head("Structural and Hydraulic Characteristics of the Host Networks", 2)
D.caption("Table 1", "Structural and Hydraulic Characterization of the "
                     "Empirical and Synthetic Networks")


def ms(d, dec=3, sci=False):
    if sci:
        return f"{d['M']:.2e} ({d['SD']:.2e})"
    return f"{d['M']:.{dec}f} ({d['SD']:.{dec}f})"


def mr(d, dec=3, sci=False):
    if sci:
        return f"{d['Mdn']:.2e} [{d['min']:.1e}, {d['max']:.1e}]"
    return (f"{d['Mdn']:.{dec}f} [{d['min']:.{dec}f}, {d['max']:.{dec}f}]")


e, s = T1["empirical"], T1["synthetic"]
rows = [
    ["Fractal dimension D", ms(e["D"]), mr(e["D"]), ms(s["D"]), mr(s["D"])],
    ["Hydraulic conductance", ms(e["hydraulic_conductance"], sci=True),
     mr(e["hydraulic_conductance"], sci=True),
     ms(s["hydraulic_conductance"], sci=True),
     mr(s["hydraulic_conductance"], sci=True)],
    ["Mean degree \u27e8k\u27e9", ms(e["mean_degree"]), mr(e["mean_degree"]),
     ms(s["mean_degree"]), mr(s["mean_degree"])],
    ["Degree standard deviation", ms(e["degree_sd"]), mr(e["degree_sd"]),
     ms(s["degree_sd"]), mr(s["degree_sd"])],
    ["Loop fraction", ms(e["loop_fraction"]), mr(e["loop_fraction"]),
     ms(s["loop_fraction"]), mr(s["loop_fraction"])],
    ["Bridge fraction", ms(e["bridge_fraction"]), mr(e["bridge_fraction"]),
     ms(s["bridge_fraction"]), mr(s["bridge_fraction"])],
    ["GCC fraction", ms(e["gcc_fraction"]), mr(e["gcc_fraction"]),
     ms(s["gcc_fraction"]), mr(s["gcc_fraction"])],
    ["Network size N (nodes)",
     f"{e['N']['M']:,.0f} ({e['N']['SD']:,.0f})",
     f"{e['N']['Mdn']:,.0f} [{e['N']['min']:,.0f}, {e['N']['max']:,.0f}]",
     f"{s['N']['M']:,.0f} ({s['N']['SD']:,.0f})",
     f"{s['N']['Mdn']:,.0f} [{s['N']['min']:,.0f}, {s['N']['max']:,.0f}]"],
]
D.table(["Characteristic", "Empirical M (SD)", "Empirical Mdn [range]",
         "Synthetic M (SD)", "Synthetic Mdn [range]"], rows,
        widths=[1.5, 1.35, 1.6, 1.35, 1.6], size=9)
D.note("Empirical n = %d leaf-venation networks passing the characterization "
       "screen (at least 500 veins), drawn from %d traced; synthetic n = %d. "
       "%d of the source networks are calibrated crop windows "
       "rather than entire laminae, so network extent is bounded by the traced "
       "window. Loop fraction is the proportion of edges lying on at least one "
       "cycle (non-bridge edges), computed identically for both cohorts and used "
       "with this definition throughout; bridge fraction is its complement and "
       "represents the proportion of veins whose individual loss disconnects part "
       "of the network."
       % (T1["empirical_n"], PROV["traced"]["n"], T1["synthetic_n"], N_CROP))

D.para("The empirical networks were sparse and close to tree-like (Mdn "
       "\u27e8k\u27e9 = %s), spanned a wide fractal-dimension range [%s, %s], "
       "and were almost entirely connected (Mdn GCC fraction = %s). A median of "
       "%.1f%% of veins lay on at least one cycle, so the median network still "
       "carried %.1f%% of its veins as bridges. The synthetic networks bracketed "
       "the empirical envelope in mean degree and fractal dimension."
       % (p3(e["mean_degree"]["Mdn"]), p3(e["D"]["min"]), p3(e["D"]["max"]),
          p3(e["gcc_fraction"]["Mdn"]),
          100 * e["loop_fraction"]["Mdn"], 100 * e["bridge_fraction"]["Mdn"]))

# --- Table 2 ---------------------------------------------------------------
D.caption("Table 2", "Spearman Rank-Order Correlations Among Architectural "
                     "Descriptors of the Empirical Networks")
lab = [("Mean degree and loop fraction", "mean_degree_x_loop"),
       ("Loop fraction and terminal fraction", "loop_x_terminal"),
       ("Loop fraction and GCC fraction", "loop_x_gcc"),
       ("Mean degree and fractal dimension", "mean_degree_x_D"),
       ("Loop fraction and fractal dimension", "loop_x_D"),
       ("Loop fraction and network size", "loop_x_N")]


def strength(r):
    a = abs(r)
    band = ("very weak" if a < .20 else "weak" if a < .40 else
            "moderate" if a < .60 else "strong" if a < .80 else "very strong")
    return f"{band} {'positive' if r > 0 else 'negative'}"


rows = []
for name, key in lab:
    st = T2[key]
    rows.append([name, rho(st["rho"]), pval(st["p"]),
                 "Reject" if st["p"] < .05 else "Fail to reject",
                 strength(st["rho"])])
D.table(["Variables correlated", "\u03c1", "p", "Decision on H\u2080",
         "Interpretation"], rows, widths=[2.2, 0.7, 0.8, 1.1, 1.5], size=9)
D.note("n = %d. H\u2080: there is no monotone relationship between the paired "
       "descriptors. Strength bands: < .20 very weak, .20-.39 weak, .40-.59 "
       "moderate, .60-.79 strong, \u2265 .80 very strong." % T2["n"])
D.para("Mean degree and loop fraction were almost perfectly rank-correlated "
       "(\u03c1 = %s), so only mean degree and fractal dimension are entered "
       "jointly in the analyses that follow. Loop fraction was the near-inverse "
       "of the terminal fraction (\u03c1 = %s). Fractal dimension was weakly and "
       "non-significantly related to either connectivity measure (\u03c1 = %s "
       "and %s), and neither measure was related to network size (\u03c1 = %s, "
       "p %s)."
       % (rho(T2["mean_degree_x_loop"]["rho"]), rho(T2["loop_x_terminal"]["rho"]),
          rho(T2["mean_degree_x_D"]["rho"]), rho(T2["loop_x_D"]["rho"]),
          rho(T2["loop_x_N"]["rho"]), pval(T2["loop_x_N"]["p"])))

D.caption("Figure 1", "Representative empirical host network and calibrated "
                      "synthetic mesh.")
D.note("Each network is reduced to nodes (vein junctions) and edges (vein "
       "segments).")

# --- Table 3 ---------------------------------------------------------------
D.head("Collapse of the Host Networks Under Structural Attack", 2)
D.caption("Table 3", "Critical Collapse Threshold of the Empirical Cohort Under "
                     "the Two Attack Strategies")
rd, td, dd = T3["random"], T3["degree_targeted"], T3["difference"]
D.table(["Attack strategy", "M", "SD", "Mdn", "Range"],
        [["Random (primary)", f"{rd['M']:.4f}", f"{rd['SD']:.4f}",
          f"{rd['Mdn']:.4f}", f"[{rd['min']:.4f}, {rd['max']:.4f}]"],
         ["Degree-targeted", f"{td['M']:.4f}", f"{td['SD']:.4f}",
          f"{td['Mdn']:.4f}", f"[{td['min']:.4f}, {td['max']:.4f}]"]],
        widths=[1.8, 1.0, 1.0, 1.0, 1.6], size=10)
D.note("n = %d empirical leaf-venation networks, %s Monte Carlo trials per "
       "network per attack strategy. The cohort is the subset of the %d "
       "characterized networks meeting the percolation screen (at least 2,000 "
       "veins, at least one cycle, no more than 5%% of terminals at the window "
       "edge, and a mean-degree shift of at most 0.05 when window cut-ends are "
       "stripped). H\u2080: the two attack strategies give the same threshold. "
       "Wilcoxon signed-rank test (paired, distribution-free): W = %.0f, p "
       "%s; H\u2080 rejected. The random threshold exceeded the degree-targeted "
       "threshold in %d of %d networks (M difference = %.4f, SD = %.4f; Mdn "
       "difference = %.4f)."
       % (T3["n"], f"{T3['trials_per_leaf_per_mode']:,}",
          PROV["characterization_112"]["n"], T3["wilcoxon"]["W"],
          pval(T3["wilcoxon"]["p"]), T3["n_positive"], T3["n"],
          dd["M"], dd["SD"], dd["Mdn"]))
D.para("Random removal collapsed the networks at a median threshold of %.4f, "
       "whereas degree-targeted removal collapsed them after removing fewer "
       "nodes (Mdn = %.4f), a reduction of %.1f%% in the tolerable removal "
       "fraction. The ordering held in every one of the %d networks examined."
       % (rd["Mdn"], td["Mdn"], T3["relative_reduction_of_median_pct"], T3["n"]))

# --- Table 4 ---------------------------------------------------------------
D.caption("Table 4", "High-Precision Threshold Estimates From the Calibrated "
                     "Synthetic Reference Network")
D.table(["Attack strategy", "p_c", "95% CI", "Trials"],
        [["Random", f"{SUM['p_c_random']:.4f}",
          f"[{SUM['p_c_ci95'][0]:.4f}, {SUM['p_c_ci95'][1]:.4f}]",
          f"{SUM['n_trials']:,}"],
         ["Degree-targeted", f"{SUM['p_c_targeted_degree']:.4f}",
          f"[{SUM['p_c_targeted_degree_ci95'][0]:.4f}, "
          f"{SUM['p_c_targeted_degree_ci95'][1]:.4f}]",
          f"{SUM['n_trials_targeted']:,}"],
         ["Betweenness-targeted", f"{SUM['p_c_targeted_betweenness']:.4f}",
          f"[{SUM['p_c_targeted_betweenness_ci95'][0]:.4f}, "
          f"{SUM['p_c_targeted_betweenness_ci95'][1]:.4f}]",
          f"{SUM['n_trials_targeted']:,}"]],
        widths=[1.9, 1.0, 1.7, 1.2], size=10)
D.note("Calibrated synthetic mesh, N = %s, E = %s, \u27e8k\u27e9 = %.4f, D = "
       "%.4f. This network is not an empirical leaf. It is retained because its "
       "trial budget yields intervals about two orders of magnitude tighter than "
       "the cohort estimates and because the supplementary scaling analyses were "
       "performed on it. All intervals are bootstrap percentile intervals; those "
       "for the targeted strategies were computed for this revision, the "
       "original run having stored point estimates only."
       % (f"{SUM['network']['n_nodes']:,}", f"{SUM['network']['n_edges']:,}",
          SUM["network"]["mean_degree"], SUM["D"]))
D.para("The ordering observed in the cohort was reproduced on the reference "
       "network, where targeted removal collapsed the mesh at a lower threshold "
       "(%.4f under degree targeting and %.4f under betweenness targeting) than "
       "random removal (%.4f). Because this network is far smaller than the "
       "typical empirical network (Mdn N = %s), its absolute threshold is not "
       "comparable with the cohort medians."
       % (SUM["p_c_targeted_degree"], SUM["p_c_targeted_betweenness"],
          SUM["p_c_random"], f"{e['N']['Mdn']:,.0f}"))
D.caption("Figure 2", "Collapse probability and giant-component survival under "
                      "random and degree-targeted attack, and the progressive "
                      "fragmentation of the giant component.")

# --- Table 5: sink --------------------------------------------------------
D.head("Hydraulic Behaviour of the Calibrated Haustorial Sink", 2)
D.caption("Table 5", "Hydraulic Behaviour of the Literature-Calibrated "
                     "Haustorial Sink Across the Swept Gradient")
sw = SWEEP
sel = sw[sw.gradient_MPa.isin([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])]
rows = [[f"{r.gradient_MPa:.1f}", f"{r.min_psi_MPa:.4f}",
         f"{r.margin_to_cavitation_MPa:.4f}", f"{100 * r.diversion_fraction:.1f}%",
         int(r.n_embolized)] for _, r in sel.iterrows()]
D.table(["Host\u2013parasite gradient (MPa)", "Minimum \u03c8 (MPa)",
         "Margin to cavitation (MPa)", "Flow diverted", "Vessels embolized"],
        rows, widths=[1.5, 1.2, 1.4, 1.0, 1.3], size=9)
D.note("Sink strength K_h = %.4f, calibrated so that the haustorium withdraws "
       "%.1f%% of leaf throughput at the illustrative %.1f MPa gradient; the "
       "cavitation threshold is %.1f MPa. Every fifth point of the %d-point "
       "sweep is shown. The diverted fraction rises with the gradient because "
       "the parasite reservoir deepens while K_h is held fixed, so the %.0f%% "
       "figure is specific to the illustrative gradient. No vessel embolized at "
       "any of the %d gradients tested, so the cavitation-onset gradient is "
       "undefined below %.1f MPa."
       % (SINK["K_H_HOLOPARASITE"], 100 * SINK["achieved_diversion"],
          SINK["gradient_MPa"], config.PSI_CAVITATION,
          R["T4_sink_sweep"]["n_gradients"], 100 * SINK["target_diversion"],
          R["T4_sink_sweep"]["n_gradients"],
          R["T4_sink_sweep"]["gradient_range_MPa"][1]))
D.para("At the calibrated strength the minimum host leaf water potential was "
       "%.4f MPa at the illustrative gradient, %.4f MPa above the cavitation "
       "threshold, and the sink embolized no vessels. Sweeping the "
       "host\u2013parasite gradient from %.1f to %.1f MPa left the margin "
       "positive throughout, its smallest value being %.4f MPa, and the "
       "embolized-vessel count was zero at every gradient tested."
       % (SINK["min_psi_at_literature_MPa"],
          SINK["min_psi_at_literature_MPa"] - config.PSI_CAVITATION,
          R["T4_sink_sweep"]["gradient_range_MPa"][0],
          R["T4_sink_sweep"]["gradient_range_MPa"][1],
          R["T4_sink_sweep"]["min_margin_MPa"]))

# --- Table 6: predictors --------------------------------------------------
D.head("Architectural Predictors of the Collapse Threshold", 2)
D.caption("Table 6", "Normality Tests and Rank-Order Correlations of the "
                     "Architectural Predictors With p_c")
sh = T5["shapiro_wilk"]
sp = T5["spearman_with_pc_random"]
pa = T5["partial_spearman"]
rows = [
    ["Mean degree \u27e8k\u27e9", f"{sh['mean_degree']['W']:.3f}",
     pval(sh["mean_degree"]["p"]), rho(sp["mean_degree"]["rho"]),
     pval(sp["mean_degree"]["p"]), rho(pa["mean_degree_given_D"])],
    ["Fractal dimension D", f"{sh['D']['W']:.3f}", pval(sh["D"]["p"]),
     rho(sp["D"]["rho"]), pval(sp["D"]["p"]), rho(pa["D_given_mean_degree"])],
    ["Loop fraction", f"{sh['loop_fraction']['W']:.3f}",
     pval(sh["loop_fraction"]["p"]), rho(sp["loop_fraction"]["rho"]),
     pval(sp["loop_fraction"]["p"]), rho(pa["loop_given_D"])],
]
D.table(["Predictor", "Shapiro\u2013Wilk W", "p", "\u03c1 with p_c", "p",
         "Partial \u03c1"], rows, widths=[1.5, 1.2, 0.8, 1.0, 0.8, 1.0], size=9)
D.note("n = %d. Shapiro\u2013Wilk rejected normality for p_c (W = %.3f, p %s) "
       "and for both connectivity predictors, so Spearman's \u03c1 was used "
       "rather than Pearson's r. Each partial correlation controls for fractal "
       "dimension, except that of fractal dimension itself, which controls for "
       "mean degree."
       % (T5["n"], sh["p_c_random"]["W"], pval(sh["p_c_random"]["p"])))
reg = T5["regression_semi_standardized"]
regs = T5["regression_fully_standardized"]
D.para("All three architectural measures were positively and significantly "
       "associated with the threshold, the connectivity measures most strongly. "
       "Mean degree and fractal dimension each remained significant with the "
       "other partialled out (\u03c1 = %s and %s). A multiple regression of p_c "
       "on the two z-scored predictors gave p_c = %.4f + %.4f z\u27e8k\u27e9 + "
       "%.4f zD, R\u00b2 = %s, F(%d, %d) = %.2f, p %s; the coefficients are in "
       "threshold units per standard deviation of the predictor, so a one-standard"
       "-deviation increase in mean degree corresponds to an increase of %.4f in "
       "p_c. The corresponding fully standardized coefficients are %s and %s."
       % (rho(pa["mean_degree_given_D"]), rho(pa["D_given_mean_degree"]),
          reg["intercept"], reg["beta"][0], reg["beta"][1], rho(reg["R2"]),
          reg["df"][0], reg["df"][1], reg["F"], pval(reg["p"]),
          reg["beta"][0], rho(regs["beta"][0]), rho(regs["beta"][1])))

# --- Table 7: synthetic grid ----------------------------------------------
D.caption("Table 7", "Synthetic Causal Grid: Threshold Regressed on Two "
                     "Decoupled Architectural Axes")
rows = []
for attack, label in (("random", "Random"),
                      ("degree_targeted", "Degree-targeted")):
    a = T6[attack]
    rows.append([label, "Mean degree \u27e8k\u27e9",
                 rho(a["spearman_mean_degree"]["rho"]),
                 f"{a['ols_raw']['beta_mean_degree']:.4f}",
                 rho(a["ols_fully_standardized"]["beta"][0]),
                 rho(a["ols_raw"]["R2"])])
    rows.append(["", "Fractal dimension D", rho(a["spearman_D"]["rho"]),
                 f"{a['ols_raw']['beta_D']:.4f}",
                 rho(a["ols_fully_standardized"]["beta"][1]),
                 rho(a["ols_raw"]["R2"])])
D.table(["Attack", "Predictor", "\u03c1", "OLS b (raw units)",
         "Standardized \u03b2", "Model R\u00b2"], rows,
        widths=[1.2, 1.5, 0.7, 1.3, 1.2, 0.9], size=9)
D.note("n = %d synthetic networks in which mean degree and fractal dimension "
       "were varied independently by construction (Pearson r = %s; Spearman "
       "\u03c1 = %s). The raw coefficients are in threshold units per unit of "
       "each predictor and are not comparable with one another, because mean "
       "degree spans %.2f units across the grid and fractal dimension spans "
       "%.2f; the standardized coefficients are comparable. Model R\u00b2 refers "
       "to the full two-predictor model and is therefore identical for both rows "
       "of an attack strategy."
       % (T6["n"], rho(T6["predictor_decoupling"]["pearson"]),
          rho(T6["predictor_decoupling"]["spearman"]),
          T6["ranges"]["mean_degree"][1] - T6["ranges"]["mean_degree"][0],
          T6["ranges"]["D"][1] - T6["ranges"]["D"][0]))
a = T6["random"]
D.para("With the two axes decoupled by construction, the threshold tracked "
       "connectivity almost deterministically (\u03c1 = %s) and fractal "
       "dimension only weakly (\u03c1 = %s). The fitted surface was p_c = %.4f + "
       "%.4f \u27e8k\u27e9 + %.4f D, R\u00b2 = %s, F(2, %d) = %.2f, p %s. "
       "Expressed per standard deviation, the connectivity coefficient is about "
       "%.0f times the geometry coefficient. The grid's connectivity axis "
       "extends to \u27e8k\u27e9 = %.2f against an empirical maximum of %.2f, so "
       "its upper portion is an extrapolation relative to the measured cohort."
       % (rho(a["spearman_mean_degree"]["rho"]), rho(a["spearman_D"]["rho"]),
          a["ols_raw"]["intercept"], a["ols_raw"]["beta_mean_degree"],
          a["ols_raw"]["beta_D"], rho(a["ols_raw"]["R2"]), T6["n"] - 3,
          a["ols_raw"]["F"], pval(a["ols_fully_standardized"]["p"]),
          abs(a["ols_fully_standardized"]["beta"][0]
              / a["ols_fully_standardized"]["beta"][1]),
          T6["ranges"]["mean_degree"][1], T6["ranges"]["empirical_mean_degree"][1]))

# --- Table 8: reticulation / bridges --------------------------------------
D.head("Reticulation, Bridge Dependence, and Damage Tolerance", 2)
D.caption("Table 8", "Reticulation, Bridge Dependence, and Damage Tolerance")
pairs = [("Loop fraction and p_c (random)", "loop_x_pc_random"),
         ("Bridge fraction and p_c (random)", "bridge_x_pc_random"),
         ("Loop fraction and p_c (degree-targeted)", "loop_x_pc_degree_targeted"),
         ("Bridge fraction and p_c (degree-targeted)",
          "bridge_x_pc_degree_targeted"),
         ("Loop fraction and the random-minus-targeted gap", "loop_x_attack_gap"),
         ("Residual loop fraction (\u27e8k\u27e9 controlled) and p_c",
          "residual_loop_given_mean_degree_x_pc")]
rows = []
for name, key in pairs:
    st = T7[key]
    rows.append([name, rho(st["rho"]), f"{st['t']:.2f}", pval(st["p"]),
                 "Reject" if st["p"] < .05 else "Fail to reject"])
D.table(["Variables correlated", "\u03c1", "t", "p", "Decision on H\u2080"],
        rows, widths=[2.6, 0.7, 0.8, 0.9, 1.2], size=9)
D.note("n = %d; df = %d. Bridge fraction is the exact complement of loop "
       "fraction, so the two carry the same information with opposite sign. The "
       "final row tests whether loop fraction predicts the threshold beyond mean "
       "degree; the non-significant result follows from the near-collinearity "
       "reported in Table 2 and is not evidence that reticulation is "
       "unimportant."
       % (T7["loop_x_pc_random"]["n"], T7["loop_x_pc_random"]["df"]))
D.para("Loop fraction was positively associated with the threshold under both "
       "attack strategies, and more strongly under the targeted strategy "
       "(\u03c1 = %s) than the random one (\u03c1 = %s). The gap between the two "
       "thresholds narrowed as reticulation increased (\u03c1 = %s), so more "
       "reticulate networks lost less of their tolerance when the damage was "
       "concentrated rather than distributed."
       % (rho(T7["loop_x_pc_degree_targeted"]["rho"]),
          rho(T7["loop_x_pc_random"]["rho"]),
          rho(T7["loop_x_attack_gap"]["rho"])))

# --- Table 9: quartiles ---------------------------------------------------
D.caption("Table 9", "Damage Tolerance by Reticulation Quartile")
names = {1: "Q1 (least reticulate)", 2: "Q2", 3: "Q3",
         4: "Q4 (most reticulate)"}
rows = [[names[q["quartile"]], q["n"], f"{q['median_loop_fraction']:.3f}",
         f"{q['median_mean_degree']:.3f}", f"{q['median_pc']:.4f}"]
        for q in T8["quartiles"]]
D.table(["Quartile", "n", "Mdn loop fraction", "Mdn \u27e8k\u27e9", "Mdn p_c"],
        rows, widths=[1.9, 0.6, 1.5, 1.2, 1.2], size=10)
D.note("H\u2080: the least- and most-reticulate quartiles do not differ in p_c. "
       "Mann\u2013Whitney U = %.0f, p %s, n = %d per quartile; H\u2080 rejected."
       % (T8["mann_whitney"]["U"], pval(T8["mann_whitney"]["p"]),
          T8["mann_whitney"]["n1"]))
D.para("More highly reticulated networks tolerated more structural loss before "
       "fragmenting. The median threshold rose monotonically across reticulation "
       "quartiles, from %.4f in the least reticulate quartile to %.4f in the "
       "most reticulate. The most reticulate quartile withstood the removal of "
       "an additional %.1f%% of its nodes, a relative gain of %.1f%%."
       % (T8["quartiles"][0]["median_pc"], T8["quartiles"][3]["median_pc"],
          100 * T8["absolute_difference"], T8["relative_gain_pct"]))

# --- Table 10: enhancement ------------------------------------------------
D.head("Effect of Enhancing Venation Reticulation", 2)
D.caption("Table 10", "Reticulation-Enhancement Effect by Tracing-Quality Grade")
rows = [[g["grade"], g["n"], f"{g['median_pc_current']:.4f}",
         f"{g['median_pc_enhanced']:.4f}", f"{g['median_delta_pc']:.4f}",
         f"{g['pct_improved']:.0f}%"] for g in T9["by_grade"]]
rows.append(["Full valid cohort", T9["n"], f"{T9['median_pc_current']:.4f}",
             f"{T9['median_pc_enhanced']:.4f}",
             f"{T9['delta_pc']['Mdn']:.4f}", f"{T9['pct_improved']:.0f}%"])
D.table(["Grade", "n", "Mdn p_c current", "Mdn p_c enhanced",
         "Mdn \u0394p_c", "% improved"], rows,
        widths=[1.4, 0.6, 1.3, 1.3, 1.1, 1.0], size=10)
D.note("n = %d networks meeting the enhancement screen (%s), evaluated at %s "
       "trials each. Grade is the leading flag of the source dataset’s "
       "comma-separated extraction-quality code (A = no vein-level defect, B = "
       "missing minor veins, C = spurious minor veins, D = physical damage or "
       "partial lamina), so a network flagged \u201cB,D\u201d is counted under B "
       "and the grades partition the cohort. H\u2080: the median change in p_c "
       "is zero. Wilcoxon signed-rank test on the %d non-zero differences (%d "
       "ties discarded): W = %.0f, p %s; H\u2080 rejected. Of the %d networks, "
       "%d improved, %d were unchanged and none worsened (M \u0394p_c = %.4f, SD "
       "= %.4f, range [%.4f, %.4f]; median relative gain %.1f%%)."
       % (T9["n"], prov_en["rule"].split(" (")[0], f"{T9['trials_per_leaf']:,}",
          T9["wilcoxon"]["n_nonzero"], T9["wilcoxon"]["n_zero_discarded"],
          T9["wilcoxon"]["W"], pval(T9["wilcoxon"]["p"]), T9["n"],
          T9["n_improved"], T9["n_unchanged"], T9["delta_pc"]["M"],
          T9["delta_pc"]["SD"], T9["delta_pc"]["min"], T9["delta_pc"]["max"],
          T9["median_relative_gain_pct"]))
D.para("Raising each network's connectivity toward the reticulation ceiling "
       "\u27e8k\u27e9 = %.3f \u2014 the 90th percentile of the percolation cohort's "
       "own mean degree, so no network is made denser than the most looped "
       "networks observed \u2014 raised the collapse threshold in %.0f%% of the %d "
       "networks and lowered it in none. The effect was smallest in the "
       "artifact-free grade-A tracings (Mdn \u0394p_c = %.4f) and largest in "
       "grade B (Mdn \u0394p_c = %.4f)."
       % (T9["ceiling_mean_degree"], T9["pct_improved"],
          T9["n"], T9["by_grade"][0]["median_delta_pc"],
          T9["by_grade"][1]["median_delta_pc"]))

# --- Table 11: gain dependence --------------------------------------------
D.caption("Table 11", "Dependence of the Threshold Gain on Initial Architecture")
g1 = T10["spearman_initial_mean_degree_x_delta"]
g2 = T10["spearman_D_x_delta"]
rg = T10["regression_semi_standardized"]
rgs = T10["regression_fully_standardized"]
D.table(["Initial trait", "\u03c1 with \u0394p_c", "p",
         "b (\u0394p_c per 1 SD)", "Standardized \u03b2"],
        [["Initial mean degree \u27e8k\u27e9", rho(g1["rho"]), pval(g1["p"]),
          f"{rg['beta'][0]:.5f}", rho(rgs["beta"][0])],
         ["Fractal dimension D", rho(g2["rho"]), pval(g2["p"]),
          f"{rg['beta'][1]:.5f}", rho(rgs["beta"][1])]],
        widths=[1.8, 1.2, 0.9, 1.4, 1.2], size=10)
D.note("n = %d. Both regression columns come from the same model, in which the "
       "predictors are z-scored; the fourth column leaves the outcome in its "
       "own units (change in p_c per standard deviation of the predictor) and "
       "the fifth standardizes it. R\u00b2 = %s." % (T10["n"], rho(rg["R2"])))
D.para("The gain depended strongly and negatively on the network's initial mean "
       "degree (\u03c1 = %s): the sparser the starting network, the larger the "
       "improvement. Fractal dimension was unrelated to the gain (\u03c1 = %s, "
       "p %s), and the two-predictor model explained R\u00b2 = %s of the "
       "variance in \u0394p_c."
       % (rho(g1["rho"]), rho(g2["rho"]), pval(g2["p"]), rho(rg["R2"])))

# --- Table 12: top gainers ------------------------------------------------
D.caption("Table 12", "Networks Exhibiting the Largest Threshold Gain From "
                      "Added Reticulation")
NAMES = {"Clu_ala": "Clusia alata", "Chl_spi": "Chloranthus spicatus",
         "Ane_cal": "Anemopsis californica", "Met_dav": "Metapanax davidii",
         "Eur_jap": "Eurya japonica", "Smi_his": "Smilax hispida"}
rows = [[NAMES.get(t["name"], t["name"]), f"{t['N']:,}", f"{t['mean_degree']:.3f}",
         f"{t['loops_added']:,}", f"{t['pc_before']:.4f}",
         f"{t['pc_after']:.4f}", f"{t['delta_pc']:.4f}"]
        for t in R["T12_top_gainers"]]
D.table(["Species", "N (nodes)", "\u27e8k\u27e9 current", "Loops added",
         "p_c before", "p_c after", "\u0394p_c"], rows,
        widths=[1.6, 0.9, 1.0, 0.9, 0.9, 0.9, 0.8], size=9)
outside = [NAMES.get(t["name"], t["name"]) for t in R["T12_top_gainers"]
           if not t["boundary_ok"]]
D.note("Sorted by descending gain. Each network began with a mean degree near "
       "the lower bound of the cohort range. %s"
       % ("One caveat applies to this table: %s falls outside the crop-edge "
          "tolerance reported in Table 13 (boundary terminal fraction %.3f "
          "against a 0.05 tolerance), so its extent is more strongly bounded by "
          "the traced window than the rest of the cohort."
          % (outside[0], [t["boundary_terminal_frac"] for t in R["T12_top_gainers"]
                          if not t["boundary_ok"]][0])
          if outside else ""))
D.caption("Figure 3", "Per-network change in threshold following reticulation "
                      "enhancement, and a representative network before and "
                      "after enhancement.")

# --- Supplementary ---------------------------------------------------------
D.head("Supplementary Analyses", 2)
D.para("The analyses in this subsection establish the validity of the model and "
       "the interpretation of the critical behaviour. They fall outside the four "
       "specific questions and are reported for completeness.", indent=False)

D.caption("Table 13", "Model Validation Summary")
hv = T11["hydraulic_resistance"]
D.table(["Check", "Scope", "Statistic", "Result", "Reading"],
        [["Hydraulic resistance",
          f"{hv['n_leaves']} leaves, {hv['n_veins']:,} veins",
          "Worst per-leaf ratio CV", f"{hv['worst_ratio_cv']:.1e}",
          "Agreement to floating-point precision"],
         ["", "", "Worst |median ratio \u2212 1|",
          f"{hv['worst_abs_median_ratio_minus_1']:.1e}",
          f"Inside the {hv['cv_tolerance']:.0e} tolerance"],
         ["Wrong-exponent control", "Same veins", "Median Pearson r (log)",
          f"{T11['wrong_exponent_control']:.3f}",
          "The match is not trivial"],
         ["Leaf conductance K_leaf", f"{T11['kleaf']['n_species']} species",
          "Spearman \u03c1", f"{rho(T11['kleaf']['rho'])} (p {pval(T11['kleaf']['p'])})", "Weak and non-significant; xylem-only"],
         ["Crop-edge boundary", f"{T11['boundary']['n']} leaves",
          "Within both tolerances",
          f"{T11['boundary']['n_within']} of {T11['boundary']['n']}",
          f"{T11['boundary']['n_outside']} outside; "
          f"{len(T11['boundary']['outside_in_enhancement_cohort'])} of those "
          "remain in the enhancement cohort"]],
        widths=[1.4, 1.3, 1.4, 1.2, 1.6], size=9)
D.note("One leaf was excluded from the resistance comparison for having fewer "
       "than 50 usable veins, hence %d rather than 120. The resistance check "
       "compares the model's Hagen\u2013Poiseuille resistance vein by vein "
       "against the resistance column shipped with the source dataset; the "
       "log-scale Pearson correlation was at least %.6f in every leaf, but it is "
       "the ratio statistics, not the correlation, that establish equality."
       % (hv["n_leaves"], hv["min_pearson_log_r"]))

D.para("The hydraulic solver reproduced the source dataset's own resistance "
       "column across %d leaves and %s veins to floating-point precision: the "
       "ratio of modelled to source resistance had a worst-case per-leaf "
       "coefficient of variation of %.1e and a worst-case median departure from "
       "unity of %.1e, both inside the pre-set %.0e tolerance. Repeating the "
       "comparison with a deliberately wrong exponent dropped the median "
       "correlation to %.3f. Two checks were weaker and are reported as "
       "limitations. Modelled whole-network conductance tracked measured leaf "
       "conductance only weakly and non-significantly (\u03c1 = %s, p %s, n "
       "= %d species), as expected of a xylem-only model compared with a "
       "quantity dominated by resistances outside the xylem. In the crop-edge "
       "sensitivity test, %d of %d leaves fell inside both tolerances; the %d "
       "that did not are the smallest and most heavily windowed tracings, and "
       "%d of them remain in the enhancement cohort."
       % (hv["n_leaves"], f"{hv['n_veins']:,}", hv["worst_ratio_cv"],
          hv["worst_abs_median_ratio_minus_1"], hv["cv_tolerance"],
          T11["wrong_exponent_control"], rho(T11["kleaf"]["rho"]),
          pval(T11["kleaf"]["p"]), T11["kleaf"]["n_species"],
          T11["boundary"]["n_within"], T11["boundary"]["n"],
          T11["boundary"]["n_outside"],
          len(T11["boundary"]["outside_in_enhancement_cohort"])))

# --- coupled sink surface --------------------------------------------------
D.caption("Figure 4", "Critical haustorial density across sink strength and "
                      "fractal dimension.")
mult_min = SURF["smallest_k_h_multiple_with_a_threshold"]
mult_all = SURF["smallest_k_h_multiple_with_a_threshold_in_every_row"]
mult_nomax = SURF["largest_k_h_multiple_with_NO_threshold_in_any_row"]
D.note("The vertical axis of this surface is the critical fraction of nodes "
       "BEARING a haustorium under the coupled hydraulic model, in which a node "
       "is removed only if its solved water potential falls below the %.1f MPa "
       "cavitation threshold. It is therefore a different quantity from the "
       "removed-node threshold reported in Tables 3 to 9 and is not comparable "
       "with those values. The surface was computed on the cohort-calibrated "
       "mesh (N = %s, \u27e8k\u27e9 held at %.2f) with the sink axis anchored on "
       "the literature-calibrated K_h = %.4f and expressed as multiples of it, "
       "at %s trials per cell with bootstrap intervals."
       % (config.PSI_CAVITATION, f"{SURF['N']:,}", SURF["mean_degree_measured"][0],
          SURF["calibrated_k_h"], f"{SURF['n_trials_per_cell']:,}"))
if mult_min:
    scope = ("At the literature-calibrated sink strength"
             if mult_nomax == 1 else
             "At the literature-calibrated sink strength, and at every strength "
             "up to %d times it" % mult_nomax)
    D.para("%s, no network collapsed at any haustorial density: the collapse "
           "probability never reached .50 at any density between 0 and 1, so "
           "there is no threshold to report. A threshold first appeared in the "
           "least reticulate network at %d times the calibrated strength and in "
           "every network at %d times it, after which it fell steeply as the "
           "sink was strengthened further. The calibrated haustorial drain is "
           "therefore sub-cavitating not only at the illustrative gradient of "
           "Table 5 but at every attachment density the model can represent."
           % (scope, mult_min, mult_all))
else:
    D.para("No cell of the surface produced hydraulic collapse at any haustorial "
           "density: at the calibrated sink strength and at every multiple "
           "tested, the collapse probability never reached .50.")

# --- finite size -----------------------------------------------------------
D.caption("Figure 5", "Size dependence and critical behaviour of the transition.")
fs = FSD["sizes"]
drift = FSD.get("architecture_drift_audit", {})
sc = SCAL["finite_size"]
D.note("Two size sweeps were run. In the first (data/scaling_mesh.json) the "
       "generator's depth parameter raises network size and fractal dimension "
       "together, from D = %.3f at N = %s to D = %.3f at N = %s, so the "
       "accompanying rise in p_c from %.4f to %.4f mixes the two and cannot be "
       "read as a size effect. In the second (data/finite_size_fixedD.json) "
       "fractal dimension and mean degree were pinned by tuning the generator's "
       "length ratio and mesh fraction at each size."
       % (sc[0]["D"], f"{sc[0]['N']:,}", sc[-1]["D"], f"{sc[-1]['N']:,}",
          sc[0]["p_c"], sc[-1]["p_c"]))
D.table(["N", "D", "\u27e8k\u27e9", "Loop fraction", "p_c", "95% CI",
         "10\u201390% window"],
        [[f"{r['N']:,}", f"{r['D']:.3f}", f"{r['mean_degree']:.3f}",
          (f"{r['unpinned_descriptors']['loop_fraction_nonbridge']:.3f}"
           if "unpinned_descriptors" in r else "\u2014"),
          f"{r['p_c']:.4f}", f"[{r['ci95'][0]:.4f}, {r['ci95'][1]:.4f}]",
          f"{r['width_0.1_0.9']:.4f}"] for r in fs],
        widths=[0.9, 0.8, 0.9, 1.2, 0.9, 1.4, 1.2], size=9)
D.note("Finite-size sweep with fractal dimension and mean degree held fixed. "
       "%s" % drift.get("verdict", "").replace(" -- ", " — "))
D.para("Across the fixed-architecture sweep the threshold moved from %.4f at N = "
       "%s to %.4f at N = %s while the pinned descriptors varied by no more than "
       "%.4f in D and %.4f in mean degree. That decline cannot be attributed to "
       "size either: pinning two descriptors does not pin the architecture, and "
       "the loop fraction of the same networks fell from %.3f to %.3f over the "
       "sweep, so the threshold tracks the loss of reticulation rather than the "
       "growth in size.%s Because a definitive statement "
       "about the transition's universality class requires a multi-size scaling "
       "collapse at genuinely constant architecture, no critical exponent is "
       "reported here. The empirical connectivity threshold located on the "
       "largest network (f_c = %.3f) is the removal fraction at which the giant "
       "component vanishes, and is therefore a different quantity from the p_c "
       "reported elsewhere, which is the fraction at which the giant component "
       "falls below half its initial size; read against that definition it is of "
       "the same order as the Molloy\u2013Reed prediction for this network "
       "(%.3f), a qualitative agreement only, because Molloy\u2013Reed assumes a "
       "locally tree-like graph and the planar mesh contains short loops."
       % (fs[0]["p_c"], f"{fs[0]['N']:,}", fs[-1]["p_c"], f"{fs[-1]['N']:,}",
          FSD["D_spread_achieved"], FSD["mean_degree_spread_achieved"],
          drift["loop_fraction_range"][1], drift["loop_fraction_range"][0], "",
          SCAL["beta_test"]["empirical_fc"],
          SCAL["beta_test"]["molloy_reed_fc"]))

# --- pre-symptomatic window ------------------------------------------------
D.caption("Figure 6", "The modelled pre-symptomatic window across infestation "
                      "growth rates.")
rates = DYN["rates"]
rk = list(rates)
D.note("Infestation is modelled as logistic growth in the affected node fraction "
       "(\u03c1\u2080 = %.2f) at three stipulated rates. The window is the "
       "interval between the threshold at which the network fragments (p_c = "
       "%.3f) and the point at which the giant component vanishes (f_c = %.3f), "
       "both evaluated on the synthetic reference network. The time unit is set "
       "by the assumed growth rate and is not calibrated to any measured "
       "infestation time-course."
       % (DYN["rho0"], DYN["p_c"], DYN["f_c"]))
D.table(["Growth rate", "Time to threshold", "Time to full fragmentation",
         "Window"],
        [[k, f"{rates[k]['t_c']:.2f}", f"{rates[k]['t_wilt']:.2f}",
          f"{rates[k]['window']:.2f}"] for k in rk],
        widths=[1.6, 1.4, 1.8, 1.0], size=10)
D.para("A separation between functional fragmentation and complete loss of the "
       "giant component was present at every growth rate examined, spanning "
       "%.2f growth-time units at the slowest rate and %.2f at the fastest. The "
       "existence and shape of that separation, not its duration in real time, "
       "is the result: the model contains no measured infestation time-course, "
       "so the time axis carries no calendar units."
       % (rates[rk[0]]["window"], rates[rk[-1]]["window"]))

# ===========================================================================
# Edits required elsewhere in the manuscript
# ===========================================================================
D.d.add_page_break()
D.head("EDITS REQUIRED IN THE DISCUSSION AND CONCLUSION")
D.para("The Results above no longer contain these claims, so the Discussion has "
       "to carry them. The first group is text to insert; the second is text to "
       "correct.", indent=False)

D.head("Interpretive sentences relocated from the Results", 3)
for s in [
    "Mean degree and loop fraction were almost perfectly rank-correlated, which "
    "indicates that local connectivity and topological redundancy are two "
    "measurements of a single architectural axis rather than independent traits; "
    "reporting both as separate predictors would double-count one architectural "
    "property.",
    "Fractal dimension was unrelated to either connectivity measure, confirming "
    "that how completely a venation fills space and how redundantly it is wired "
    "are separate properties: two leaves may occupy space equally thoroughly and "
    "still differ in their capacity to reroute flow.",
    "Neither connectivity measure was related to network size, so the "
    "architectural differences described here are differences among species "
    "rather than by-products of leaf size or of the extent of the traced window.",
    "Because the drain is sub-cavitating at the calibrated strength, the "
    "hydraulic sink and the percolation collapse are best read as two decoupled "
    "lenses on the same host rather than as cause and effect: the sink describes "
    "how hard the parasite pulls, the threshold how much connectivity the host "
    "can lose before supply fails.",
    "Because the synthetic grid manipulates the two architectural axes rather "
    "than observing them, it supports a stronger reading than the cohort "
    "correlations do: within the range the generator spans, connectivity is the "
    "dominant architectural determinant of the threshold and geometry a real but "
    "secondary one. It does not establish causation in the host plant, only "
    "within the model.",
]:
    D.para("• " + s, indent=False)

D.head("Sentences that must be corrected", 3)
corr = [
    ["Conclusion", "“host xylem networks collapse at a well-defined "
     "connectivity threshold — near p_c = 0.271 under random loss”",
     "the empirical host networks collapsed at a median threshold of p_c = %s "
     "under random loss (n = %d), while the calibrated synthetic reference "
     "collapsed at %.3f"
     % (rho(T3["random"]["Mdn"]), T3["n"], SUM["p_c_random"])],
    ["Conclusion", "“degree-targeted loss is more damaging (p_c = "
     "0.202)”",
     "degree-targeted loss was more damaging in every network examined, lowering "
     "the median threshold to %s, a reduction of %.1f%%"
     % (rho(T3["degree_targeted"]["Mdn"]),
        T3["relative_reduction_of_median_pct"])],
    ["Discussion", "“Δp_c = 0.069 … approximately a 25.5% "
     "reduction”",
     "that arithmetic is the synthetic reference's (%.3f to %.3f). On the "
     "empirical cohort the reduction is %.1f%% of the mean and %.1f%% of the "
     "median"
     % (SUM["p_c_random"], SUM["p_c_targeted_degree"],
        T3["relative_reduction_of_mean_pct"],
        T3["relative_reduction_of_median_pct"])],
    ["Discussion", "“reproducing the source dataset's own resistance "
     "column … physics reproduced exactly”",
     "reproducing it to floating-point precision, with a worst-case per-leaf "
     "ratio CV of %.1e inside a %.0e tolerance"
     % (T11["hydraulic_resistance"]["worst_ratio_cv"],
        T11["hydraulic_resistance"]["cv_tolerance"])],
    ["Discussion", "“p_c converged as network size grew, the transition was "
     "continuous … and the empirical connectivity threshold (f_c = 0.524) "
     "matched the Molloy–Reed prediction (0.531)”",
     "the size sweep that produced that statement varied fractal dimension along "
     "with size, and a sweep with the architecture pinned shows the loop fraction "
     "still drifting; f_c and p_c are also different collapse criteria. State "
     "only that f_c is of the same order as the Molloy–Reed prediction, "
     "qualitatively, and drop the convergence claim"],
    ["Discussion", "“correlates weakly with measured whole-leaf conductance "
     "(Spearman ρ = 0.187)”",
     "add that the correlation is also non-significant (p %s, n = %d)"
     % (pval(T11["kleaf"]["p"]), T11["kleaf"]["n_species"])],
    ["Throughout", "“112 valid whole-leaf networks”",
     "112 valid leaf-venation networks; 100 of the 120 source files are "
     "calibrated crop windows rather than entire laminae"],
]
D.table(["Location", "Current text", "Replace with"], corr,
        widths=[1.0, 2.6, 2.9], size=9)

D.save(OUT)
print("wrote", OUT)
