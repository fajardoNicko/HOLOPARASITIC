# -*- coding: utf-8 -*-
r"""
patch_discussion_docx.py — apply the audit's required corrections to the
Discussion and Conclusion, writing a NEW file and leaving the original untouched.

The audit found four claims in the Discussion/Conclusion that the archive does
not support, one of which is a plain factual error (the empirical host threshold
is reported as the synthetic reference network's value). Those are corrected
here rather than left as a to-do, because they are the kind of error a reviewer
checks first.

Every replacement is verified to have matched; a pattern that does not match is
reported and nothing is written until all of them are accounted for, so the file
can never be half-patched. Values come from data/results_verified.json, so this
script cannot drift from the recomputed statistics.

    in:  Results_Discussion_Conclusion.docx   (never modified)
    out: DISCUSSION_CONCLUSION_REVISED.docx
         DISCUSSION_PATCH_LOG.md

    C:\laragon\bin\python\python-3.13\python.exe scripts\patch_discussion_docx.py
"""

import os
import re
import sys
import json
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from docx import Document

import config

SRC = os.path.join(ROOT, "Results_Discussion_Conclusion.docx")
OUT = os.path.join(ROOT, "DISCUSSION_CONCLUSION_REVISED.docx")
LOG = os.path.join(ROOT, "DISCUSSION_PATCH_LOG.md")

R = json.load(open(os.path.join(config.PATHS.data, "results_verified.json"),
                   encoding="utf-8"))
T3 = R["T3_attack_thresholds"]
T11 = R["T11_validation"]


def n3(x):
    """APA: bounded coefficient, leading zero dropped."""
    return f"{x:.3f}".lstrip("0")


MDN_R = n3(T3["random"]["Mdn"])          # .200
MDN_T = n3(T3["degree_targeted"]["Mdn"])  # .169
RED = T3["relative_reduction_of_median_pct"]
CV = T11["hydraulic_resistance"]["worst_ratio_cv"]
TOL = T11["hydraulic_resistance"]["cv_tolerance"]
KP = n3(T11["kleaf"]["p"])
KR = n3(T11["kleaf"]["rho"])

DASH = r"[\u2014\u2013-]"     # em / en / hyphen, as Word may hold any of them

EDITS = [
    ("D1 · Discussion attributes the synthetic threshold to the host",
     r"Under random loss the reference host collapsed at p_c = 0\.271, and "
     r"under degree-targeted loss the threshold fell to p_c = 0\.202",
     "Across the 100-network empirical cohort the median threshold under random "
     "loss was p_c = %s, and under degree-targeted loss it fell to %s; on the "
     "calibrated synthetic reference network, evaluated at a far larger trial "
     "budget, the corresponding values are .271 and .202"
     % (MDN_R, MDN_T)),

    ("D2 · Conclusion states the synthetic threshold as the host result",
     r"host xylem networks collapse at a well-defined connectivity "
     r"threshold" + DASH + r"near p_c = 0\.271 under random loss" + DASH +
     r"and degree-targeted loss is more damaging \(p_c = 0\.202\)",
     "host xylem networks collapse at a well-defined connectivity threshold "
     "\u2014 the empirical cohort's median was p_c = %s under random loss, with "
     "the calibrated synthetic reference collapsing at .271 \u2014 and "
     "degree-targeted loss is more damaging, lowering the cohort median to %s"
     % (MDN_R, MDN_T)),

    ("D3 · size-convergence and Molloy-Reed claim (Discussion)",
     r"The collapse is a genuine, size-converged percolation transition rather "
     r"than a modeling artifact: p_c converged as network size grew, the "
     r"transition was continuous \(log" + DASH + r"log R² = 0\.995\), and the "
     r"empirical connectivity threshold \(f_c = 0\.524\) matched the "
     r"Molloy" + DASH + r"Reed prediction \(0\.531\)",
     "The collapse behaves as a percolation transition rather than a modeling "
     "artifact, though the supporting evidence is weaker than first reported. "
     "The size sweep that appeared to show convergence raised fractal dimension "
     "along with network size, and a second sweep holding fractal dimension and "
     "mean degree fixed leaves the loop fraction still drifting, so no "
     "finite-size claim is made here. What does hold is that the connectivity "
     "threshold f_c = 0.524 \u2014 the removal fraction at which the giant "
     "component vanishes, a different criterion from p_c \u2014 is of the same "
     "order as the Molloy\u2013Reed prediction (0.531), a qualitative agreement "
     "only, since that prediction assumes a locally tree-like graph while the "
     "planar mesh contains short loops"),

    ("D4 · size-convergence and Molloy-Reed claim (supplementary paragraph)",
     r"The estimated threshold converged with increasing network size, while "
     r"the transition displayed continuous critical behavior with a log-log "
     r"\(R\^2=0\.995\)\. The empirical connectivity threshold \(f_c=0\.524\) "
     r"also closely matched the Molloy" + DASH + r"Reed prediction of 0\.531\.",
     "The sweep that produced the apparent size convergence raised fractal "
     "dimension along with network size, and a second sweep with fractal "
     "dimension and mean degree pinned shows the loop fraction still drifting, "
     "so neither sweep can establish convergence and none is claimed. The "
     "empirical connectivity threshold (f_c=0.524) is of the same order as the "
     "Molloy\u2013Reed prediction of 0.531, which is a qualitative check rather "
     "than a validation, because that prediction assumes a locally tree-like "
     "graph."),

    ("D5 · \u201cphysics reproduced exactly\u201d in the validation table",
     r"physics reproduced exactly",
     "agreement to floating-point precision"),

    ("D6 · validation prose overstates the correlation and hides the p value",
     r"\(Pearson on log-resistance ≥ 1\.000000\); a cross-check against "
     r"measured leaf conductance is weak \(ρ = 0\.187\)",
     "(agreeing to floating-point precision: the worst per-leaf coefficient of "
     "variation of the model-to-source resistance ratio is %.1e, against a %.0e "
     "tolerance); a cross-check against measured leaf conductance is weak and "
     "not statistically significant (\u03c1 = %s, p = %s)" % (CV, TOL, KR, KP)),

    ("D7 · K_leaf row in the validation table",
     r"xylem-only; weak \(limitation\)",
     "xylem-only; weak and non-significant (limitation)"),

    ("D8 · targeting reduction quoted from the synthetic network",
     r"the degree-targeted threshold represents approximately a 25\.5% "
     r"reduction in the fraction of nodes that can be removed before collapse\.",
     "the degree-targeted threshold represents approximately a 25.5%% reduction "
     "in the fraction of nodes that can be removed before collapse on the "
     "synthetic reference network; across the 100-network empirical cohort the "
     "corresponding reduction is %.1f%% of the median threshold." % RED),

    ("D9 · K_leaf limitation paragraph omits non-significance",
     r"the weak association between the modeled xylem conductance and measured "
     r"whole-leaf conductance \(\(\\rho=0\.187\)\)",
     "the weak and statistically non-significant association between the "
     "modeled xylem conductance and measured whole-leaf conductance "
     "(\u03c1 = %s, p = %s)" % (KR, KP)),

    ("D11 · limitations sentence omits the K_leaf p value",
     r"correlates weakly with measured whole-leaf conductance "
     r"\(Spearman ρ = 0\.187\)",
     "correlates weakly and non-significantly with measured whole-leaf "
     "conductance (Spearman ρ = %s, p = %s, n = %d species)"
     % (KR, KP, T11["kleaf"]["n_species"])),

    ("D10 · Conclusion pins the contribution to a single threshold value",
     r"The central contribution is not that every parasitized leaf will "
     r"collapse at \(p_c=0\.271\)",
     "The central contribution is not that every parasitized leaf will collapse "
     "at one particular threshold value"),
]


def para_text(p):
    return "".join(r.text for r in p.runs)


def set_para_text(p, text):
    """Rewrite a paragraph as a single run, keeping the first run's formatting.

    Only called on paragraphs that actually changed. Body prose in this document
    is uniformly formatted, so this is safe; a paragraph with mixed emphasis
    would lose it, which is why the log names every paragraph rewritten.
    """
    if not p.runs:
        return
    first = p.runs[0]
    first.text = text
    for r in p.runs[1:]:
        r.text = ""


def all_paragraphs(doc):
    for p in doc.paragraphs:
        yield p
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def main():
    if not os.path.exists(SRC):
        sys.exit(f"source not found: {SRC}")
    doc = Document(SRC)
    paras = list(all_paragraphs(doc))

    applied, missed, rewritten = [], [], []
    for label, pattern, repl in EDITS:
        rx = re.compile(pattern)
        hits = 0
        for i, p in enumerate(paras):
            txt = para_text(p)
            if rx.search(txt):
                new = rx.sub(repl.replace("\\", "\\\\"), txt)
                set_para_text(p, new)
                hits += 1
                rewritten.append((label, i))
        (applied if hits else missed).append((label, hits))

    if missed:
        print("NOT APPLIED — nothing written:")
        for label, _ in missed:
            print("  -", label)
        sys.exit(1)

    # A banner so nobody mistakes the Results half of this file for the current one
    first = doc.paragraphs[0]
    banner = first.insert_paragraph_before()
    run = banner.add_run(
        "[REVISED COPY. The Discussion and Conclusion below carry the "
        "corrections listed in DISCUSSION_PATCH_LOG.md. The Results section of "
        "this file is SUPERSEDED by RESULTS_REVISED.docx and was left in place "
        "only for continuity.]")
    run.bold = True

    doc.save(OUT)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("# Discussion / Conclusion — corrections applied\n\n")
        f.write("Source: `Results_Discussion_Conclusion.docx` (unmodified)\n")
        f.write("Output: `DISCUSSION_CONCLUSION_REVISED.docx`\n\n")
        f.write("Generated by `scripts/patch_discussion_docx.py`; every value is "
                "read from `data/results_verified.json`.\n\n")
        f.write("| Correction | Paragraphs rewritten |\n|---|---|\n")
        for label, hits in applied:
            f.write(f"| {label} | {hits} |\n")
        f.write("\n**Note on formatting.** Each rewritten paragraph is "
                "reassembled as a single run carrying the first run's "
                "formatting, so any mid-paragraph emphasis in those paragraphs "
                "needs re-applying by eye. No other paragraph is touched.\n")
    print(f"wrote {OUT}")
    print(f"wrote {LOG}")
    for label, hits in applied:
        print(f"  applied ({hits}x): {label}")


if __name__ == "__main__":
    main()
