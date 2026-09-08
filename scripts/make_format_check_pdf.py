# -*- coding: utf-8 -*-
r"""
make_format_check_pdf.py -- typeset the formatting review of the deliverable.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_format_check_pdf.py

Findings from a page-by-page read of "PR2 Research Paper (Deliverable) (7).pdf"
(74 pp). Ordered by what has to be fixed first: things that visibly break on the
page, then numbers that contradict each other, then everything else. Page
numbers are the printed page numbers of that PDF.

The list lives in FINDINGS below so the PDF is the only deliverable. Same
reportlab and font conventions as make_ppt_guide_pdf.py.

Markup:
    @TITLE / @SUB     document title and subtitle lines
    @PART text        section heading (starts a new page)
    @H text           subheading
    @ITEM p. N | text | fix        one finding
    @NOTE text        commentary paragraph
    @RULE             horizontal rule
Inline: **bold**, *italic*, `mono`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame,
                                KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "FORMAT_CHECK.pdf"
FONT_DIR = Path(r"C:\Windows\Fonts")

MARGIN_X = 0.8 * inch
MARGIN_TOP = 0.8 * inch
MARGIN_BOT = 0.8 * inch

INK = colors.HexColor("#1A1D21")
MUTED = colors.HexColor("#6B7280")
VEIN = colors.HexColor("#2E7D5B")
LOSS = colors.HexColor("#C1462F")
RULE = colors.HexColor("#D9D9D2")

DOC_TITLE = "Formatting Review"


FINDINGS = r"""
@TITLE Formatting Review, second pass
@SUB PR2 Research Paper (Deliverable) (8).pdf, 74 pp -- re-checked against the first review
@SUB 26 fixed. 7 new. 33 still open.

Same format as before: location, defect, remedy. Section 1 is damage introduced
by the edit pass, which is where to start. Section 4 lists what is now closed,
so nothing there needs re-checking.

@RULE

@PART 1. New in this version

@NOTE Seven things broke or were introduced while fixing the first list. Two of
them are worse than what they replaced.

@ITEM p. 41 | **Table 14's note is truncated mid-sentence.** It ends "...vary by no more than 0.0070 and 0.0059 across the sweep;" -- on a semicolon, with nothing after it. The old note was wrong; this one stops. The clause separating these meshes from the reference network of Table 4 is also missing. | Complete it: "...across the sweep; these meshes are therefore not the reference network of Table 4. Pinning two descriptors does not pin the architecture: loop fraction falls from 0.692 to 0.561 across the sweep, so the threshold tracks the loss of reticulation rather than the growth in size."
@ITEM p. 43 | **Figure 13's note has a missing period and a doubled one.** "...(N = 1,023) This f_c is not the 0.524 reported in the finite-size analysis, which was measured on a different mesh.." | Full stop after "(N = 1,023)", single full stop after "mesh", and name the size: "on a different mesh at N = 8,191."
@ITEM p. 42 | **"located on the N = 8,191(f_c = 0.524)"** -- no space before the bracket and the noun is missing, so the sentence reads "located on the N = 8,191". | "located on the N = 8,191 mesh (f_c = 0.524)".
@ITEM p. 22 | **Dormann et al. is now cited, but as "Doorman et al., 2013".** The reference list spells it Dormann. | Dormann.
@ITEM p. 51 | **"rho = 0. 999"** -- the new clause introduces the same space-inside-a-decimal defect flagged elsewhere in this list. "reported in Table 6 and 8" should also be "Tables 6 and 8". | Close the space; pluralise "Tables".
@ITEM p. 29-30 | **Figure 4's label is now orphaned.** The figure no longer runs off the page, but "Figure 4" sits alone at the foot of p. 29 with its title and both panels on p. 30. This is the defect that was just fixed for Table 6. | Move the label to p. 30.
@ITEM p. 45 | **A stray full stop sits on its own line** below Table 17's note. | Delete it.

@PART 2. Still open, highest cost first

@H The supplementary tables

@ITEM p. 49, 50, 51, 54, 58, 59 | **Tables S1, S3 and S4 are still cited nine times and still do not exist in the document.** S1 three times (the Gini coefficient of 0.274, the 619 distinct betweenness values, the four-network flux correlations); S3 four times (locality interquartile ranges, the four-scenario table, the residualised rho = 0.577, the cubic model R-squared = 0.917); S4 twice (the coupled-density result, the 6.0 MPa and 256x values). S2 is never cited, so the numbering also has a hole. | The largest remaining defect and the easiest for a panelist to check. Either append the supplementary section or move each value into the running text -- all nine are single numbers that would fit inside the sentence citing them.

@H Tables

@ITEM p. 26-27 | **Table 1 still breaks across pages with no "(continued)" and no repeated header.** A reader on p. 27 sees "Degree SD", "Loop fraction" and "Network size N" with no column heads. | Add "Table 1 (continued)" and repeat the header row.
@ITEM p. 26-27 | **The stray horizontal rule inside Table 1 is still there**, between the Degree SD and Loop fraction rows. | Delete it.
@ITEM p. 28-29 | **Table 3 and its note are on different pages.** The note no longer splits mid-sentence, but the table ends p. 28 and the note opens p. 29. | Keep them together.
@ITEM p. 27, 29, 31, 33, 35, 36, 37, 44 | **Notes still run straight into the next paragraph or heading.** Nine instances: Tables 1, 3, 5, 6, 8, 9, 10 and 16, plus Figure 8's note, which runs into the "Table 8" heading, and Table 16's, which runs into the "Figure 14" heading. | Insert a paragraph break after every note.
@ITEM p. 38, 43 | **Tables 12 and 15 still carry no Note row.** Every other table has one. | Add n and the trial budget.
@ITEM p. 41 | **"Table 14" and its title are still on consecutive lines with no blank line**, unlike every other table. | Insert the blank line.
@ITEM p. 28 | **Table 3's ranges are now all bracketed, but the precision is still mixed:** "[0.0262-0.2698]" and "[0.0019-0.2630]" against "[0.001-0.046]". | Four decimals throughout.
@ITEM p. 33 | Table 6 still has **two columns both headed "p"**. | "p (S-W)" and "p (rho)".
@ITEM p. 36 | Table 9's note still writes **"p_c" as plain text** where every other table uses the formatted symbol. | Match the rest.
@ITEM p. 37 | **Table 10's note is still ungrammatical:** "networks meeting the enhancement filtration of nodes must be >= 1000 and current p_c must be 0.02". 1000 also lacks the thousands comma used everywhere else. | "networks meeting the enhancement screen: N >= 1,000 nodes and a current p_c of at least 0.02".

@H Formulas and symbols

@ITEM p. 25 | **The missing subscripts are still missing.** The tofu boxes are gone, but the where-lists now read "w_i, w = the removal weights of nodes i and j", "R = the sum of ranks in group j" and "n = the number of observations in group j" -- the j is simply absent. The Kruskal-Wallis formula above them also indexes on i while its where-list indexes on j. | Restore w_j, and make the where-list use R_i and n_i to match the formula.
@ITEM p. 15, 16, 20, 26, 44, 51 | **Spaces inside decimals are unchanged, and there is now one more.** "2. 811" (p. 15), "0. 6" (p. 16), "0. 025" and "0. 975 " (p. 20), "0. 05" (p. 26), "3. 0 x 10^-8" and "1. 5 x 10^-8" (p. 44), "0. 999" (p. 51). | Close all seven, and the stray space before the bracket on p. 20.
@ITEM p. 19 | **"P(collapse) = the number of GCC collapse"** is unchanged. P is a probability, and the formula above divides by N_trials. | "the probability that the giant component has collapsed".
@ITEM p. 19 | **"This half-size rule" has no antecedent.** The paragraph refers back to a rule the preceding text never states; the formula above it defines P(collapse), not the half-size criterion. The definition first appears on p. 48, twenty-nine pages later. | State it before referring to it: "The network is scored as collapsed when the largest surviving component falls below half its undamaged size. This half-size rule was adopted..."
@ITEM p. 16 vs p. 20 | The threshold is still set as "p_c = -b/w" on p. 16 and "p_c =- b/w" on p. 20. | One form.
@ITEM p. 16 | Still **"where the inflection rate falls outside the swept range"**. The quantity is the inflection point. | "inflection point".
@ITEM throughout | **Two minus glyphs still in use.** Table 5 and the Results use a hyphen ("-0.9963"); the Discussion uses a true minus ("-1.0224" set as U+2212). | Standardise.
@ITEM p. 56 | **"p <0 .001"** -- the space is on the wrong side of the zero. | "p < .001".

@H Layout

@ITEM p. 46-61 | **The Discussion still appears to be set smaller than pp. 1-45.** Select a line on p. 45 and a line on p. 47 and compare the reported point size. | Reset the Discussion to the body size.
@ITEM p. 22-23 | **The paragraph beginning "Overall model fit was tested by the F-static" is smaller than the rest of its own page**, and continues at that size onto p. 23 through "...loop fraction was retained descriptively". | Reset both to body size.
@ITEM p. 11, 19, 29, 42, 43 | **Blank gaps remain:** the lower half of p. 11, a wide gap mid-paragraph on p. 19 between "in size." and "Trial budgets", the foot of p. 29, the lower half of p. 42, and the head of p. 43. | Close them.

@H Wording

@ITEM p. 13 | Still **"a node lies on the shortest between other pairs of nodes"** -- a word is missing. | "on the shortest paths between".
@ITEM p. 17 | Still **"the resistor network or xylem and leaf hydraulics"**. | "of".
@ITEM p. 31, 32 | Still **"20.0% of leaf throughout"** and **"approximately 20% of leaf throughout"**. p. 58 and the abstract have it right. | "throughput".
@ITEM p. 27 | Still **"22.4% of its vein as bridges"**. | "veins".
@ITEM p. 12 | Still **"rises to toward three"**. | "rises toward".
@ITEM p. 15 | Still **"for direct comparison of the original"**. | "with".
@ITEM p. 22 | Still **"the F-static for the regression"**. | "F-statistic".
@ITEM p. 23 | Still **"Its dependence of each leaf's initial mean degree"**. | "on".
@ITEM p. 7 | Still **"cultivation procedures, and the likes"**. | "and the like".
@ITEM p. 11 | Still **"the connectivity of each veins"** and **"a two layer system"**. | "each vein"; "two-layer".
@ITEM p. 11 | **The BFS sentence is unchanged.** "reachability is established by a BFS from the roots any node that the BFS can not reach is assigned a generation beyond the graph's max, labelling it as the main component." Two sentences are run together after "roots", and as written it is the unreachable node that gets labelled the main component, which is the opposite of what the code does. | Split it and fix the referent.
@ITEM p. 26 | Still **"per attack strategy, It is the primary unit"** -- comma splice with a capital after the comma. | Full stop.
@ITEM p. 26 | Still **"standard deviation, all inferential tests were evaluated"** -- comma splice. | Full stop or semicolon.
@ITEM p. 37 | **"so zero network is made denser"**, inside a sixty-word run-on. | "no network"; split the sentence.
@ITEM p. 30 | Figure 5's note: **"the curves in figure 4 summarizes it as a probability"** -- comma splice, subject-verb disagreement, and lowercase "figure". | "Figure 4 summarises it as a probability."

@H Consistency

@ITEM p. 11 | **"Hagen-Poisseulle" survives on p. 11.** p. 17 is now correct, and pp. 5, 39 and 47 use the en-dash form. | "Hagen-Poiseuille", with one dash convention.
@ITEM throughout | **British and American spelling are still mixed.** The Introduction is now British, but Methods and Results keep "utilizes" and "analyze" (p. 7), "behavior" and "visualization" (p. 9), "normalization" (p. 11), "summarized" (pp. 18, 19, 26), "Characterization" in the headings, and "embolized" (Table 5, p. 31) against "embolised" in the abstract and throughout the Discussion. | Pick one and sweep.
@ITEM p. 39, 52, 53, 54 | **Leading zeros are still mixed, sometimes inside one sentence.** "0.187 (p = .073)" in Table 13; "0.526 for mean degree and .408 for fractal dimension" (p. 52); "rho = 0.727 and .818" (p. 54); a run of ".086, .991, .227, .887, .981, .125, .940, .970, .451" on p. 53 against "0.733" elsewhere. | APA drops the leading zero only for correlations and p-values. Apply it uniformly.
@ITEM p. 32, 41 | **"In figure 6"** and **"In the figure 12.a"** are still lowercase; the second also carries a stray "the". | "In Figure 6"; "In Figure 12.a".
@ITEM p. 39 | **Figure 10's title is still sentence case** -- "A representative network before and after reticulation enhancement" -- while Figures 9, 11 and 12 are now title case. | Title case.
@ITEM p. 7, 63-64 | **"the researchers" is still plural** on p. 7 and throughout the Acknowledgement, against a single named proponent on the title page. | Singular, or name the team on the title page.
@ITEM p. 14 | **"(Callaway et al. 2000)"** is the last citation missing its comma before the year. The same source is punctuated correctly on pp. 3 and 16. | "(Callaway et al., 2000)".

@H Three numbers worth a second look

@ITEM p. 9 | **Figure 1's caption says "three stages with a combined ten steps", but the diagram contains nine boxes** -- Dryad dataset, graph reconstruction, characterisation, reticulation enhancement, attack simulation, Monte Carlo percolation, haustorial sink model, statistical analysis, outputs. | Count them and correct the caption, or add the missing step.
@ITEM p. 9 | **The Figure 1 diagram still labels the source "Matos et al., 2024"** with no letter suffix, although the text now uses 2024a and 2024b correctly throughout. | Regenerate the figure with 2024a.
@ITEM p. 40 | Figure 11's note still says **"mean degree held at 2.49"** where Table 4 gives the same mesh as 2.4888. | 2.4888.

@PART 3. Closed since the first review

@NOTE Listed so none of these needs re-checking.

@ITEM Page breaks | Figure 6 no longer clipped; Table 5's header no longer split across pp. 30-31; Table 16 whole on p. 44; Table 6's label and title reunited on p. 33. | 4 items
@ITEM Numbers | Trial budget on p. 16 corrected to 2,400 per network per removal mode; "2,00" and "1,00" on p. 8 corrected; the two f_c values attributed to their own meshes; the Griebel gradient and depression named as different quantities; "median per-network ratios of 2.46 and 2.27" added; the rho = 0.737 / 0.731 provenance clause added. | 6 items
@ITEM Formulas | The haustorial flow equation now reads Q = K_h(psi_host - psi_parasite); "diverted low" corrected to "diverted flow"; both regressions written with plus signs; Table 4's CI comma restored. | 4 items
@ITEM Tables | Table 8's header changed to "Variables correlated"; Table 2's note corrected to ">= 0.80"; Table 3's note corrected to "a mean degree shift of at most 0.05" and its ranges bracketed; Table 4's note spaced as "mean degree = 2.4888". | 4 items
@ITEM Citations | Elshakhs corrected to 2024; every Matos citation now carries 2024a or 2024b; Johnson moved into alphabetical order; four of the five missing commas before years added. | 4 items
@ITEM Wording | "host-level" hyphenated; Melicytus major italicised; "Edge Placement Control" set at its siblings' heading level; Figures 9, 11 and 12 retitled in title case; the abstract's range set with an en dash; the Figure 3 sentence claiming the mesh is "biologically similar" to a leaf removed. | 6 items
"""


def register_fonts() -> None:
    faces = {"Body": "arial.ttf", "Body-Bold": "arialbd.ttf",
             "Body-Italic": "ariali.ttf", "Body-BoldItalic": "arialbi.ttf",
             "Mono": "consola.ttf"}
    for name, filename in faces.items():
        path = FONT_DIR / filename
        if not path.exists():
            raise SystemExit(f"missing font: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "Body", normal="Body", bold="Body-Bold",
        italic="Body-Italic", boldItalic="Body-BoldItalic")


def inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+?)`", r'<font name="Mono" size="8.5">\1</font>', text)
    return text


def build_styles() -> dict[str, ParagraphStyle]:
    body = ParagraphStyle("body", fontName="Body", fontSize=9.5, leading=13.5,
                          textColor=INK, alignment=TA_LEFT, spaceAfter=8)
    return {
        "body": body,
        "title": ParagraphStyle("title", parent=body, fontName="Body-Bold",
                                fontSize=21, leading=25, alignment=TA_CENTER,
                                spaceAfter=6),
        "sub": ParagraphStyle("sub", parent=body, fontSize=8.5, leading=12,
                              textColor=MUTED, alignment=TA_CENTER,
                              spaceAfter=3),
        "part": ParagraphStyle("part", parent=body, fontName="Body-Bold",
                               fontSize=14, leading=18, spaceAfter=10,
                               keepWithNext=1),
        "h": ParagraphStyle("h", parent=body, fontName="Body-Bold",
                            fontSize=10.5, leading=14, spaceBefore=10,
                            spaceAfter=5, keepWithNext=1),
        "note": ParagraphStyle("note", parent=body, fontName="Body-Italic",
                               fontSize=9, leading=13, textColor=MUTED,
                               spaceAfter=9),
        "loc": ParagraphStyle("loc", parent=body, fontName="Body-Bold",
                              fontSize=9, leading=12.5, textColor=LOSS,
                              spaceAfter=0),
        "what": ParagraphStyle("what", parent=body, fontSize=9.5, leading=13,
                               spaceAfter=2),
        "fix": ParagraphStyle("fix", parent=body, fontSize=9.5, leading=13,
                              textColor=VEIN, spaceAfter=0),
    }


class Hairline(Table):
    def __init__(self, width: float):
        super().__init__([[""]], colWidths=[width], rowHeights=[1])
        self.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 0.6, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))


def item_block(loc: str, what: str, fix: str, width: float, st) -> Table:
    """One finding: location in the margin, defect and remedy beside it."""
    left = Paragraph(inline(loc), st["loc"])
    right = [Paragraph(inline(what), st["what"]),
             Paragraph("&rarr; " + inline(fix), st["fix"])]
    tbl = Table([[left, right]], colWidths=[width * 0.16, width * 0.84],
                hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 8),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE)]))
    return tbl


def parse(src: str, st, width: float) -> list:
    flow, para = [], []

    def flush():
        nonlocal para
        if para:
            flow.append(Paragraph(inline(" ".join(para)), st["body"]))
            para = []

    for raw in src.strip("\n").split("\n"):
        s = raw.strip()
        if not s:
            flush()
            continue
        if s.startswith("@TITLE "):
            flush(); flow.append(Paragraph(inline(s[7:]), st["title"]))
        elif s.startswith("@SUB "):
            flush(); flow.append(Paragraph(inline(s[5:]), st["sub"]))
        elif s == "@RULE":
            flush(); flow.extend([Spacer(1, 9), Hairline(width), Spacer(1, 12)])
        elif s.startswith("@PART "):
            flush()
            flow.append(PageBreak())
            flow.append(Paragraph(inline(s[6:]), st["part"]))
            flow.extend([Hairline(width), Spacer(1, 10)])
        elif s.startswith("@H "):
            flush(); flow.append(Paragraph(inline(s[3:]), st["h"]))
        elif s.startswith("@NOTE "):
            flush(); flow.append(Paragraph(inline(s[6:]), st["note"]))
        elif s.startswith("@ITEM "):
            flush()
            loc, what, fix = [p.strip() for p in s[6:].split("|", 2)]
            flow.append(CondPageBreak(0.9 * inch))
            flow.append(item_block(loc, what, fix, width, st))
        else:
            para.append(s)
    flush()
    return flow


def decorate(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Body", 8)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(MARGIN_X, MARGIN_BOT * 0.55, DOC_TITLE)
    canvas.drawRightString(letter[0] - MARGIN_X, MARGIN_BOT * 0.55,
                           str(doc.page))
    canvas.restoreState()


def main() -> int:
    register_fonts()
    st = build_styles()
    width = letter[0] - 2 * MARGIN_X
    flow = parse(FINDINGS, st, width)
    doc = BaseDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOT,
        title=DOC_TITLE, author="Nicko Fajardo")
    doc.addPageTemplates([PageTemplate(
        id="body",
        frames=[Frame(MARGIN_X, MARGIN_BOT, width,
                      letter[1] - MARGIN_TOP - MARGIN_BOT,
                      leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)],
        onPage=decorate)])
    doc.build(flow)
    n_items = FINDINGS.count("@ITEM ")
    print(f"wrote {OUT}")
    print(f"  {doc.page} pages, {n_items} findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
