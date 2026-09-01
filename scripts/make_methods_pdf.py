# -*- coding: utf-8 -*-
r"""
make_methods_pdf.py -- typeset METHODS_FOR_VALIDATION_FORM.md as a manuscript PDF.

Manuscript style: Times New Roman 12 pt, 1.15 line spacing, justified body with a
0.5 in first-line indent, 1 in margins, APA-style headings, page number top right.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_methods_pdf.py

The markdown file is the source of truth; this script only typesets it.

Source conventions:
  # Title            -> centred bold heading (APA level 1)
  ## Subhead         -> flush-left bold heading (APA level 2)
  $ equation         -> centred display equation, italic, unindented
  blank-line blocks  -> justified body paragraphs
  x^{4}, g_{ij}      -> superscript / subscript
  angle brackets     -> drawn from the Symbol face, which Times New Roman lacks
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "METHODS_FOR_VALIDATION_FORM.md"
OUT = ROOT / "METHODS_FOR_VALIDATION_FORM.pdf"

FONT_DIR = Path(r"C:\Windows\Fonts")
FONT_SIZE = 12.0
# Word renders "single" spacing for Times New Roman 12 at about 13.8 pt, so 1.15
# line spacing lands near 15.9 pt. Matching that keeps the PDF flush with the
# manuscript rather than with reportlab's 1.2x default.
LEADING = 15.9
INDENT = 0.5 * inch
MARGIN = 1.0 * inch


def register_fonts() -> None:
    faces = {
        "TNR": "times.ttf",
        "TNR-Bold": "timesbd.ttf",
        "TNR-Italic": "timesi.ttf",
        "TNR-BoldItalic": "timesbi.ttf",
    }
    for name, filename in faces.items():
        path = FONT_DIR / filename
        if not path.exists():
            raise SystemExit(f"missing font: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "TNR", normal="TNR", bold="TNR-Bold",
        italic="TNR-Italic", boldItalic="TNR-BoldItalic",
    )


# Times New Roman carries no angle brackets and no proportional sign, so those
# three characters are drawn from the Symbol face, which is what Word itself
# substitutes. Every other symbol in the source is native to Times New Roman.
SYMBOL_FALLBACK = {
    "\u27e8": "\u2329",   # mathematical left angle bracket
    "\u27e9": "\u232a",   # mathematical right angle bracket
    "\u221d": "\u221d",   # proportional to
}


def inline(text: str) -> str:
    """Escape XML, then apply the source's inline markup."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\^\{([^}]*)\}", r"<super>\1</super>", text)
    text = re.sub(r"_\{([^}]*)\}", r"<sub>\1</sub>", text)
    for char, symbol_char in SYMBOL_FALLBACK.items():
        text = text.replace(char, f'<font face="Symbol">{symbol_char}</font>')
    return text


def build_styles() -> dict[str, ParagraphStyle]:
    body = ParagraphStyle(
        "body", fontName="TNR", fontSize=FONT_SIZE, leading=LEADING,
        alignment=TA_JUSTIFY, firstLineIndent=INDENT, spaceAfter=0,
    )
    return {
        "body": body,
        "flush": ParagraphStyle("flush", parent=body, firstLineIndent=0),
        "title": ParagraphStyle(
            "title", parent=body, fontName="TNR-Bold", alignment=TA_CENTER,
            firstLineIndent=0, spaceAfter=LEADING * 0.5, keepWithNext=1,
        ),
        "head2": ParagraphStyle(
            "head2", parent=body, fontName="TNR-Bold", alignment=TA_LEFT,
            firstLineIndent=0, spaceBefore=LEADING * 0.5, spaceAfter=0,
            keepWithNext=1,
        ),
        "equation": ParagraphStyle(
            "equation", parent=body, fontName="TNR-Italic", alignment=TA_CENTER,
            firstLineIndent=0, spaceBefore=LEADING * 0.5,
            spaceAfter=LEADING * 0.5, keepWithNext=1,
        ),
    }


def parse(md: str, styles: dict[str, ParagraphStyle]) -> list:
    flow: list = []
    after_equation = False
    for block in [b.strip() for b in md.split("\n\n") if b.strip()]:
        block = " ".join(line.strip() for line in block.splitlines())
        if block.startswith("## "):
            flow.append(Paragraph(inline(block[3:]), styles["head2"]))
            after_equation = False
        elif block.startswith("# "):
            flow.append(Paragraph(inline(block[2:]), styles["title"]))
            after_equation = False
        elif block.startswith("$ "):
            flow.append(Paragraph(inline(block[2:]), styles["equation"]))
            after_equation = True
        else:
            # Prose resuming after a display equation continues the sentence
            # that introduced it, so it alone is set flush left.
            style = styles["flush"] if after_equation else styles["body"]
            flow.append(Paragraph(inline(block), style))
            after_equation = False
    return flow


def page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("TNR", FONT_SIZE)
    canvas.drawRightString(
        letter[0] - MARGIN, letter[1] - MARGIN + 0.25 * inch, str(doc.page)
    )
    canvas.restoreState()


def main() -> int:
    register_fonts()
    styles = build_styles()
    doc = BaseDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Materials and Methods", author="Nicko Fajardo",
    )
    frame = Frame(
        MARGIN, MARGIN, letter[0] - 2 * MARGIN, letter[1] - 2 * MARGIN,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=page_number)])
    doc.build(parse(SRC.read_text(encoding="utf-8"), styles))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
