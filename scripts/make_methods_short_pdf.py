# -*- coding: utf-8 -*-
r"""
make_methods_short_pdf.py -- typeset METHODS_SHORT_FOR_VALIDATION_FORM.md onto
exactly one page.

The full methods run to eight pages, which does not fit the space a validation
form leaves for methodology. This is the same method described at the length a
validator can read in one sitting: every screening rule, budget, threshold
definition, stipulated value and named test is kept, and only the exposition,
the justifying citations, and the worked reasoning are cut.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_methods_short_pdf.py

Style: Times New Roman 10.5 pt, 1.15 line spacing, 1 in margins, justified, on
short bond. The body sits half a point under the manuscript's 11 pt because
the content, once cut to what a validator has to see, still needs one line
more than 11 pt leaves; the alternatives were dropping a screening rule or
eating into the margin, and neither is worth half a point. Headings are run into the paragraph they open rather than standing
on their own line, which is what buys the page: seven standing headings would
cost about a seventh of the available depth in headings and their air alone.

The script fails rather than silently spilling onto a second page, so the
one-page guarantee holds whenever the markdown is edited.

Source conventions, matching scripts/make_methods_pdf.py:
  # Title            -> centred bold heading
  **Lead-in.** text  -> bold run-in heading, then the paragraph
  x^{4}, g_{ij}      -> superscript / subscript
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "METHODS_SHORT_FOR_VALIDATION_FORM.md"
OUT = ROOT / "METHODS_SHORT_FOR_VALIDATION_FORM.pdf"

FONT_DIR = Path(r"C:\Windows\Fonts")
FONT_SIZE = 10.5
# Word renders single spacing for Times New Roman at about 1.15x the point
# size, so 1.15 line spacing lands near 1.32x. Matching that keeps the page
# flush with what a validator would see if the text were pasted into the form.
LEADING = FONT_SIZE * 1.32
MARGIN = 1.0 * inch
PARA_GAP = 2.5


def register_fonts() -> None:
    faces = {
        "TNR": "times.ttf",
        "TNR-Bold": "timesbd.ttf",
        "TNR-Italic": "timesi.ttf",
    }
    for name, filename in faces.items():
        path = FONT_DIR / filename
        if not path.exists():
            raise SystemExit(f"missing font: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "TNR", normal="TNR", bold="TNR-Bold", italic="TNR-Italic")


# Times New Roman has no proportional sign, so it is drawn from the Symbol face,
# which is what Word itself substitutes. Every other non-ASCII character in the
# source (rho, delta, en dash, >=, <=) is native to Times New Roman.
SYMBOL_FALLBACK = {"∝": "∝"}


def inline(text: str) -> str:
    """Escape XML, then apply the source's inline markup."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\^\{([^}]*)\}", r"<super>\1</super>", text)
    text = re.sub(r"_\{([^}]*)\}", r"<sub>\1</sub>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    for char, symbol_char in SYMBOL_FALLBACK.items():
        text = text.replace(char, f'<font face="Symbol">{symbol_char}</font>')
    return text


def build_styles() -> dict[str, ParagraphStyle]:
    body = ParagraphStyle(
        "body", fontName="TNR", fontSize=FONT_SIZE, leading=LEADING,
        alignment=TA_JUSTIFY, spaceAfter=PARA_GAP,
    )
    return {
        "body": body,
        "title": ParagraphStyle(
            "title", parent=body, fontName="TNR-Bold", alignment=TA_CENTER,
            spaceAfter=LEADING * 0.5, keepWithNext=1,
        ),
    }


def parse(md: str, styles: dict[str, ParagraphStyle]) -> list:
    flow: list = []
    for block in [b.strip() for b in md.split("\n\n") if b.strip()]:
        block = " ".join(line.strip() for line in block.splitlines())
        if block.startswith("# "):
            flow.append(Paragraph(inline(block[2:]), styles["title"]))
        else:
            flow.append(Paragraph(inline(block), styles["body"]))
    return flow


def main() -> int:
    register_fonts()
    styles = build_styles()
    doc = BaseDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Materials and Methods (condensed)", author="Nicko Fajardo",
    )
    frame = Frame(
        MARGIN, MARGIN, letter[0] - 2 * MARGIN, letter[1] - 2 * MARGIN,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="body", frames=[frame])])
    flow = parse(SRC.read_text(encoding="utf-8"), styles)

    # Measure before committing, so an overlong edit is reported as the number
    # of lines to cut rather than as a silent second page.
    avail = letter[1] - 2 * MARGIN
    used = 0.0
    for item in flow:
        _, h = item.wrap(letter[0] - 2 * MARGIN, avail)
        used += h + item.getSpaceAfter()
    used -= flow[-1].getSpaceAfter()

    doc.build(flow)
    pages = doc.page
    print(f"wrote {OUT}")
    print(f"  {FONT_SIZE:.1f} pt Times New Roman, {LEADING / FONT_SIZE:.2f} leading"
          f" ({LEADING:.1f} pt), {MARGIN / 72:.2f} in margins, {letter[0] / 72:.1f} x"
          f" {letter[1] / 72:.0f} in")
    print(f"  text height {used:.0f} pt of {avail:.0f} available"
          f"  ({used / avail * 100:.1f}% of the page)")
    print(f"  pages: {pages}")
    if pages != 1:
        raise SystemExit(
            f"ERROR: {pages} pages. Cut about "
            f"{(used - avail) / LEADING:.0f} lines from {SRC.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
