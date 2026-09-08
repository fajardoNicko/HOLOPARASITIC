# -*- coding: utf-8 -*-
r"""
make_defense_script_pdf.py -- typeset the spoken defense script as a lectern PDF.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_defense_script_pdf.py

The script text lives in SCRIPT below rather than in a markdown file, because
the deliverable is the PDF and a parallel .md would only drift out of sync.
Edit SCRIPT, re-run, and the PDF is rebuilt.

Layout is set for reading aloud at a lectern, not for reading at a desk:
spoken lines are 12.5 pt Times New Roman on 1.5 leading so a line can be found
again after looking up, and every non-spoken element -- board cues, delivery
notes, section commentary -- is set in grey Arial so that nothing you must not
read aloud is ever in the same typeface as something you must. Blocks are kept
whole on a page wherever they fit, so no sentence is split across a page turn.

Markup accepted in SCRIPT:
    @TITLE text          document title
    @SUB text            subtitle line under the title
    @PART text           part heading (starts a new page)
    @BLOCK n | name | d  numbered delivery block, d = a duration label
    @CUE text            board cue, not spoken
    > text               spoken line
    @NOTE text           delivery direction, not spoken
    @H text              minor heading
    @Q text              a question from the panel
    @TABLE a | b         table row (consecutive rows form one table)
    @THEAD a | b         table header row
    @RULE                horizontal rule
    text                 plain commentary paragraph
Inline: **bold**, *italic*.
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
OUT = ROOT / "DEFENSE_SCRIPT.pdf"
FONT_DIR = Path(r"C:\Windows\Fonts")

MARGIN_X = 0.95 * inch
MARGIN_TOP = 0.85 * inch
MARGIN_BOT = 0.85 * inch

INK = colors.HexColor("#1A1D21")
MUTED = colors.HexColor("#6B7280")
VEIN = colors.HexColor("#2E7D5B")
LOSS = colors.HexColor("#C1462F")
RULE = colors.HexColor("#D9D9D2")

DOC_TITLE = "Defense Script"


# --------------------------------------------------------------------------
# The script
# --------------------------------------------------------------------------

SCRIPT = r"""
@TITLE Defense Script
@SUB Percolation Analysis of Vein Reticulation as a Structural Basis for Damage Tolerance in Leaf Venation Networks under Simulated Vascular Damage
@SUB Nicko Fajardo  |  spoken runtime about fifteen minutes  |  ten blocks

Read the grey text; say the black text. Board cues tell you where to point, never
what to read aloud. Every number here traces to Part 8 of the study mastery guide.

@RULE

@BLOCK 1 | The cold open | 45 sec
@CUE Cuscuta photograph, full bleed, no text

> This is *Cuscuta*. Dodder. It is a holoparasite, which means it gave up on
> photosynthesis entirely. No chlorophyll. Barely any roots. No real leaves.
>
> It survives by finding another plant, wrapping around its stem, and drilling a
> feeding structure called a haustorium straight into the host's plumbing. And then
> it drinks.
>
> It is one of about four thousand parasitic plant species, and it is the one that is
> best studied, which is why it is on the screen. But the question I started with is
> the general one: how much water does a parasitic sink have to steal before it kills
> the host's vascular system?

@NOTE Slow, low, and let the pause before the last sentence sit. This is the only stretch of the defense where you have their attention without earning it, so do not spend it on the title of your study. Greet the panel after this, or fold it into block 2. Name the organism here because a named organism is what makes an opening image work, but name it as an exemplar, so that nothing later in the defense rests on it being that particular species.

@BLOCK 2 | The negative result, stated first | 1:30
@CUE The 2.6 percent tile

> So I built it. I solved the entire leaf as an electrical circuit. Kirchhoff's
> laws, every vein a resistor, and the parasite entered as a leak conductance
> calibrated to withdraw twenty percent of the leaf's total water throughput. That
> is a serious sink, and I will say up front where the twenty percent comes from: it
> is a hemiparasite measurement, Jiang and colleagues in 2003, because no holoparasite
> water-flux fraction has ever been measured. So the number is not species-specific,
> and I do not model a species. I model a sink of that strength.
>
> It did almost nothing.
>
> It depressed the network's minimum water potential by 0.026 megapascals. That is
> 2.6 percent of the safety margin in my model. The other 97.4 percent is my own
> stipulated boundary conditions, and I say so in the paper. To actually reach the
> modelled cavitation threshold you would need a host-parasite gradient of about six
> megapascals. The largest gradient anyone has measured in a real system is about
> half a megapascal.
>
> So the hypothesis I started with was wrong by roughly an order of magnitude, and I
> have the number that kills it. But it left a much better question standing.

@NOTE Deliver this completely flat. No apology, no nervous laugh, no hedging. You are reporting a measurement, and the calm is the whole point. Doing this in your first ninety seconds means everything after it inherits the credibility, and it permanently disarms the question about whether your parasite result is a failure, because you answered it first and on your own terms.

@BLOCK 3 | The real question | 1:30
@CUE Reticulation concept panel, branching against looped

> Here is the question that survived. Forget who is doing the damage. How much
> damage can a leaf's vein network take at all, before it stops being one connected
> network?
>
> To see why that is not obvious, think about two cities.
>
> The first is a suburb. Every street is a cul-de-sac hanging off one main road.
> Close one street and every house past it is cut off, because there is no other way
> in.
>
> The second is a grid. Every block connects to four others. Close a street and you
> go around.
>
> Leaf veins are exactly this. Some leaves are suburbs, where veins branch outward
> and never rejoin. Most flowering plants are grids, where the veins loop back and
> reconnect, closing small islands called areoles. That looping is called
> reticulation, and it is my variable.
>
> And we know it matters in real plants. Sack and colleagues cut a leaf's midrib, the
> main highway, and lost about 75 percent of its hydraulic conductance. Then they cut
> the small looped veins instead, and measured no detectable penalty at all. The grid
> routed around it.
>
> What nobody had done was turn that into a number you can compare across species.

@NOTE The sentence to land is "some leaves are suburbs, most are grids." If the panel remembers one thing about your project a week from now, it is that. Point left for the suburb and right for the grid, physically, and keep the sides consistent when the metaphor returns in block 9.

@BLOCK 4 | Percolation | 1:00
@CUE Progressive fragmentation montage

> So keep closing streets in the grid city. At first nothing happens. Everyone still
> gets everywhere. Keep going, and still nothing. Still nothing.
>
> And then, over a very narrow range, the map stops being one city and becomes a
> scatter of isolated towns. It does not degrade. It shatters.
>
> That is percolation theory, and it is the right tool precisely because connectivity
> does not decay smoothly. It holds, and holds, and then it goes.
>
> So each leaf becomes a graph. Nodes are vein junctions, edges are vein segments. I
> delete junctions at random and watch the largest surviving connected group, the
> giant connected component. My threshold is the fraction of junctions I have to
> remove before that giant component falls below half its original size, half the
> time. I call it the critical removed fraction.

@NOTE If they interrupt to ask why half, that is engagement, not an attack. Answer in one breath: these networks span 421 nodes to 300,633, four and a half orders of magnitude, and a spanning-cluster criterion behaves differently at those two extremes where a half-size rule applies identically at every scale. Add that it is operational rather than a critical point in the physics sense, and that you re-ran everything against a source-anchored criterion as a check, which correlates at rho 0.912 with every association preserved.

@BLOCK 5 | The data, and the flaw you hand them | 1:10
@CUE Methodology panel, dataset and pipeline

> The networks are real, not simulated. They come from the Matos 2024 Dryad deposit,
> 122 species from the UC Berkeley Botanical Garden, traced with a convolutional
> neural network that preserves the minor veins and the areoles. There are 120 usable
> networks, and my primary percolation cohort is 100 of them after a resolvability
> screen.
>
> Now the thing you are going to find if I do not tell you. One hundred of those 120
> files are calibrated crop windows, not entire leaves. Not one file in the deposit
> carries a petiole flag.
>
> So I never say leaves. The title says leaf venation networks, every result says
> networks, and I pick my source node by a documented rule, the endpoint of the widest
> vein in the window, which is the hydraulically most proximal point where water
> enters. Does that turn a crop into a whole lamina? No, and I do not claim it does.

@NOTE Volunteering this costs eight seconds and buys the rest of the defense. A panelist who finds a hidden limitation stops trusting everything else you said; a panelist who hears you name it first assumes you know everything else too.

@BLOCK 6 | The threshold | 1:00
@CUE Hero tile 0.1998, then the collapse curve

> Across 100 real networks, the median critical removed fraction is 0.1998. Call it
> twenty percent of junctions. That is the shatter point.
>
> That is one leaf's collapse curve. Two thousand four hundred Monte Carlo trials per
> network, fixed seeds, fully reproducible, and the threshold is the inflection point
> of a logistic fit.
>
> I also ran a mode where busier junctions are likelier to fail. That drops the
> threshold to 0.1685, about 15.7 percent lower, and it did so in 100 out of 100
> networks. Not 99. All of them.
>
> One point of precision. That is not an attack. Removal is probabilistic and
> weighted, not rank-ordered, and nothing in biology computes a centrality measure. It
> is a bounding scenario: random removal gives the expected response, weighted removal
> gives its pessimistic edge.

@BLOCK 7 | Architecture predicts tolerance | 1:25
@CUE Threshold against predictors, then the quartile table

> So does being a grid actually buy you anything?
>
> Mean degree, the average number of vein segments meeting at a junction, which is my
> measure of how looped a network is, predicts the threshold at rho 0.733. Fractal
> dimension, which measures how thoroughly the venation fills space, comes second at
> 0.496.
>
> Sort the cohort into quarters by how looped they are, and the median threshold
> climbs at every step, from 0.158 to 0.231. The most reticulate quarter tolerates 7.2
> percentage points more damage than the least. That is a 45.7 percent relative gain.
>
> Two caveats before you ask for them. First, fractal dimension is partly just
> measuring size: 73 percent of its variance is explained by network size. So I
> recomputed every association with log network size partialled out, and they all got
> stronger rather than weaker. Fractal dimension went from 0.496 to 0.633. A pure size
> artifact would have collapsed under that control. Second, my two-predictor model has
> an R-squared of 0.507, so roughly half the variance in the threshold sits outside
> anything I measured. I would rather say that than have you find it.

@BLOCK 8 | The intervention | 2:35
@CUE Per-network change after enhancement, the before-and-after plot

> But everything so far is correlation. In real leaves, looping and spatial complexity
> travel together, so the most reticulate leaves also tend to be the most space-filling
> ones. Nature will not separate them for you.
>
> So I did two things.
>
> First, I built networks where I could separate them. A synthetic system in which
> connectivity and spatial complexity vary independently, which no real leaf will
> allow. Restricted to the range real leaves actually occupy, connectivity beats
> spatial complexity by about eight to one in standardised terms.
>
> Second, and this is the part I would defend hardest, I intervened on the real leaves
> themselves. I added loops to 105 real leaves and re-measured each one.
>
> I took each leaf's own junction coordinates and computed a Delaunay triangulation to
> propose candidate new veins. I chose Delaunay specifically because it is
> parameter-free. There is no knob, so there is nothing for a skeptic to accuse me of
> tuning in my own favour. I discarded the candidates that already existed and added
> the rest shortest-first, so the smallest open areoles close first, which is the most
> plausible biological order.
>
> And I stopped at a mean degree of 2.811, which is the 90th percentile of the
> cohort's own connectivity. So no leaf in this experiment is ever made denser than the
> most reticulate leaf I actually observed. Nothing is extrapolated into an
> architecture that does not exist.
>
> Then I re-measured, driving both versions with the same random number stream, so the
> Monte Carlo noise is shared between the two arms instead of adding into their
> difference. Only the edge set changed. Every leaf is its own control: same species,
> same size, same shape, same tracing quality, same phylogeny. Literally the same leaf.
>
> Ninety-three of 105 got tougher. Twelve did not move. Zero got worse.
>
> The median gain is 0.0095 in removable fraction, with a p-value on the order of ten
> to the minus eighteen, and it holds across six different tracing-quality subsets with
> no reversal in any of them. In the cleanest subset alone, the artifact-free grade-A
> tracings, thirteen improved, eight were unchanged, and none worsened.

@NOTE This block is the study, and it runs 2:35, the longest in the script. Say "zero got worse" slower than everything around it and stop for one beat before continuing. Slides 12 and 13 both belong to this block.

@BLOCK 9 | The scope limit | 1:45
@CUE The three boxplots, dispersed against lesioned

> Now the result that constrains everything I just told you.
>
> Random removal scatters damage across the whole lamina. But a great deal of real
> damage is not scattered. A lesion, an insect bite, a necrotic patch is one solid
> region. So I re-ran everything removing contiguous patches at matched removal
> fractions.
>
> Localised damage is far less dangerous. The threshold rises from 0.1998 to 0.4951
> for a single lesion. That is two and a half times more damage tolerated, in 100 out
> of 100 networks, without a single exception.
>
> And here is the part that matters. The reticulation relationship disappears. Under
> one lesion, the correlation between looping and tolerance falls from 0.737 to
> negative zero point zero zero zero. Statistically nothing.
>
> Which makes sense if you go back to the city. A single lesion closes every street in
> one neighbourhood. The rest of the map is still contiguous, so you route around the
> hole, and the grid connections between neighbourhoods are never tested. Scattered
> damage is what attacks exactly those connections, and that is where reticulation
> earns its keep.
>
> So my claim is scoped, deliberately. Reticulation governs tolerance to dispersed
> damage. That qualifier is load-bearing and it is on my board.
>
> One more thing worth knowing. Fractal dimension behaves the opposite way. It is the
> only predictor that survives multi-lesion damage, at 0.523. Different damage
> geometry, different governing trait. That is a finding, not a hedge.

@BLOCK 10 | The close | 2:05
@CUE Conclusion panel, with the Cuscuta image returning small

> So. Leaf venation networks lose global connectivity after roughly twenty percent of
> junctions fail. Reticulation raises that threshold: it predicts it across 100
> species, it carries the effect when I decouple it experimentally, and when I add it
> to a leaf's own geometry the leaf gets tougher, in 93 of 105 cases, with none made
> worse. Conditional on the damage being dispersed.
>
> And the parasite I started with is still in the paper, as the thing that disciplined
> it. It is the reason I never once describe my threshold as hydraulic collapse,
> because the percolation engine never reads a conductance, a radius, or a water
> potential. Not once. It is purely topological, and I retitled the entire study when I
> realised that.
>
> What I want next is the experiment I cannot do on a computer: real leaves, controlled
> damage, and a measurement of whether the threshold I calculate predicts where they
> actually fail.
>
> And somebody needs to put a pressure chamber on a parasite and its host, because
> nobody has. I want to be exact about the scope of that claim, because it is the one
> place in this defense where naming the species matters. For *Cuscuta* specifically it
> is a published negative: the 2025 haustorium review by the field's own specialists
> states that no total water potential, osmotic potential, or turgor value has been
> reported for any *Cuscuta*-host interaction. Widened to holoparasites as a class it is
> my own search result rather than someone else's published statement: I found no
> holoparasite water-flux fraction, no haustorial conductance, and no host-parasite
> gradient of any kind. That is not a gap I invented for a future-work slide. I went
> looking for that number for months.

@NOTE Do not let the two halves of that claim collapse into one. The *Cuscuta* version is a published negative you can attribute; the holoparasite version is a search result you can only vouch for yourself. Stating the narrower one first and then widening it is what keeps both defensible. Generalising it to "parasitic plants" would be simply false, because hemiparasite water relations have been measured, and the 20 percent figure in block 2 is one of those measurements.

@NOTE The ending is earned because you opened on the parasite. Close the loop, then stop. Do not say thank you until after the silence.

@PART Handling the panel

@H When they interrupt

Interruption is engagement, not hostility. The failure mode is losing your place and
restarting from the top, which is why the script is built as ten blocks rather than one
speech. After any interruption, say "coming back to it" and re-enter at the block you
were in. Never re-summarise what you already said. If they cut you badly for time, the
three blocks that carry the study are 2, 8 and 9; everything else is setup.

@H When a panelist starts lecturing

Let them. Take an actual note. Then: "That is useful, can I check I have it? You are
saying this, and the place it bites me is this." You have turned a lecture into a
collaboration in front of the rest of the panel.

@H When you do not know

You will get a question you cannot answer, and how you handle it is worth more than the
answer. Say: "I do not know. Here is what I would need to find out," and name the
specific measurement or analysis. "My instinct is this, but I have not tested it and I
would not want to claim it." Never invent a number, never hedge into vagueness, and
never use "that is beyond the scope" as a shield. Scope is a real answer only when you
can say why the boundary sits where it does.

@H When a panelist is wrong

Do not roll over and do not fight. "I might be misunderstanding. My understanding is
this, because of this. Is there a case where that breaks down?" Confident and coachable
at once, which is the highest-scoring posture available in the room.

@PART The questions that carry the most weight

The full question bank is in the earlier presentation script. These decide the grade.
The bolded sentence in each answer does the work; everything after it is support you can
drop if you are cut off.

@Q Which parasite are you actually modelling?
> None of them, and the paper does not claim one. **The sink is a generic haustorial
> leak conductance, not a species.** The one number that fixes its strength, the twenty
> percent diversion, is a hemiparasite measurement from Jiang and colleagues in 2003,
> used because no holoparasite water-flux fraction has ever been measured for any
> species. *Cuscuta* appears in my introduction as motivation, and in my limitations as
> the scope of a published negative. It does not appear in my model.
>
> And I would rather add the reason that distinction matters than have you find it.
> *Cuscuta* preferentially attaches to host stems, petioles and pedicels, not to leaf
> blades, and *Orobanche* attaches to roots. My networks are traced leaf-lamina windows.
> So a haustorial node placed inside a lamina is a modelling device, and I declare it as
> one rather than as an observed configuration.

@Q Correlation is not causation.
> Agreed, which is why the correlation is not my main result. **I intervened.** Synthetic
> networks with the two axes decoupled by construction, and then loop addition on each
> real leaf's own coordinates, with that leaf as its own control. Species, size, shape,
> tracing quality and phylogeny are all held constant, because it is literally the same
> leaf. That is as close to an experiment as a computational study gets.

@Q You added veins for free. Real leaves have to pay for them.
> That is the sharpest criticism of the intervention and I agree with it completely.
> **My model has no construction-cost, mechanical, or photosynthetic term**, so it
> identifies the direction of a relationship rather than an optimum. Real venation sits
> on a trade-off surface, which Ronellenfitsch and Katifori mapped, and greater hydraulic
> safety in real leaves comes with higher leaf mass per area and thicker conduit walls.
> Adding a cost term is the obvious next version.

@Q How can you claim hydraulic failure when you never measured conductivity or embolism?
> **I do not claim it, and I removed the claim myself.** The percolation engine never
> reads a conductance, a radius, or a water potential. It is purely topological. I had
> been describing the threshold as hydraulic collapse, I checked the code, and it was
> not. So I retitled the study to a structural basis for damage tolerance and rewrote the
> claims. That was uncomfortable and it made the paper much stronger.

@Q So the parasite result is a failure.
> It is a quantified negative, which is more useful than a vague positive. **At the
> calibrated strength the parasite contributes 2.6 percent of the reported margin, and
> reaching cavitation would need six megapascals against half a megapascal ever
> measured.** And I will volunteer the weakness inside my own negative: the claim
> that no vessels embolise is threshold-dependent, and it inverts at a minus one
> cavitation threshold. I swept it, and the onset gradient is 1.1 megapascals at minus
> one, 6.0 at minus two, and 9.5 at minus three. So the correct statement is that the
> absence of embolism is specific to thresholds at or below about minus 1.10 megapascals
> within the range I swept.

@Q Your degree-weighted removal only drops the threshold 15.7 percent. In a scale-free network, targeting hubs is catastrophic. Why is yours so mild?
> Because leaf venation is not scale-free, and that is a structural finding rather than
> an excuse. **Planarity bounds node degree, and my maximum degree across the entire
> cohort is four to five.** There are no hubs to decapitate. That narrow degree
> distribution is precisely why weighted removal is a modest perturbation here and a
> catastrophe in a Barabasi-Albert network.

@PART Discipline

@H The four numbers you must never fumble

@THEAD Number | What it is
@TABLE 0.1998 | median threshold, uniform removal, n = 100
@TABLE 93 of 105, zero worsened | the intervention
@TABLE 2.46 times | the localised-damage advantage
@TABLE 2.6 percent | the parasite's share of the modelled margin

@H Two sentences loaded at all times

> The percolation engine never reads a conductance, a radius, or a water potential. The
> threshold is purely topological.

> It only holds for dispersed damage. Under a single lesion the relationship disappears
> entirely.

@H Vocabulary

A panelist who knows the field will catch every one of these, and the substitutions are
the difference between sounding careful and sounding overclaimed.

@THEAD Never say | Always say
@TABLE attack, targeted attack | degree-weighted or betweenness-weighted removal
@TABLE hydraulic collapse | network fragmentation, structural collapse
@TABLE validated | verified, for the resistance-column check
@TABLE pre-symptomatic, early warning | sub-critical, pre-fragmentation, or nothing
@TABLE conductance | modelled conductance
@TABLE driven by the parasite | with the sink imposed as a boundary condition
@TABLE reticulation improves robustness | raises tolerance to dispersed damage
@TABLE proves, or shows that plants | demonstrates in this model that
@TABLE leaves | leaf venation networks

@H The metaphor budget

Suburb against grid is the only metaphor in the script. Use it three times: block 3 to
introduce reticulation, block 9 to explain why the correlation dies under a single
lesion, and once more in questioning if someone looks lost. A fourth use makes it sound
like the metaphor is all you have.

@H The last thing before you walk in

Do not reread the results. You know the results. Read Part 5 of the study mastery guide,
the do-not-claim table. Restraint is what wins the room.
"""


# --------------------------------------------------------------------------
# Typesetting
# --------------------------------------------------------------------------

def register_fonts() -> None:
    faces = {
        "Body": "times.ttf",
        "Body-Bold": "timesbd.ttf",
        "Body-Italic": "timesi.ttf",
        "Body-BoldItalic": "timesbi.ttf",
        "Cue": "arial.ttf",
        "Cue-Bold": "arialbd.ttf",
        "Cue-Italic": "ariali.ttf",
    }
    for name, filename in faces.items():
        path = FONT_DIR / filename
        if not path.exists():
            raise SystemExit(f"missing font: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "Body", normal="Body", bold="Body-Bold",
        italic="Body-Italic", boldItalic="Body-BoldItalic")
    pdfmetrics.registerFontFamily(
        "Cue", normal="Cue", bold="Cue-Bold", italic="Cue-Italic")


def inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    return text


def build_styles() -> dict[str, ParagraphStyle]:
    spoken = ParagraphStyle(
        "spoken", fontName="Body", fontSize=12.5, leading=12.5 * 1.5,
        textColor=INK, alignment=TA_LEFT, spaceAfter=9,
        leftIndent=14, bulletIndent=0,
    )
    note = ParagraphStyle(
        "note", fontName="Cue-Italic", fontSize=9, leading=13,
        textColor=MUTED, alignment=TA_LEFT, spaceBefore=4, spaceAfter=12,
        leftIndent=14, rightIndent=6,
    )
    return {
        "spoken": spoken,
        "note": note,
        "commentary": ParagraphStyle(
            "commentary", fontName="Cue", fontSize=9.5, leading=14,
            textColor=MUTED, spaceAfter=10,
        ),
        "title": ParagraphStyle(
            "title", fontName="Cue-Bold", fontSize=22, leading=26,
            textColor=INK, alignment=TA_CENTER, spaceAfter=6,
        ),
        "sub": ParagraphStyle(
            "sub", fontName="Cue", fontSize=9, leading=12.5,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=3,
        ),
        "part": ParagraphStyle(
            "part", fontName="Cue-Bold", fontSize=15, leading=19,
            textColor=INK, spaceBefore=0, spaceAfter=12, keepWithNext=1,
        ),
        "block": ParagraphStyle(
            "block", fontName="Cue-Bold", fontSize=12.5, leading=16,
            textColor=VEIN, spaceBefore=0, spaceAfter=2, keepWithNext=1,
        ),
        "cue": ParagraphStyle(
            "cue", fontName="Cue-Italic", fontSize=8.5, leading=12,
            textColor=LOSS, spaceAfter=7, keepWithNext=1,
        ),
        "h": ParagraphStyle(
            "h", fontName="Cue-Bold", fontSize=10.5, leading=14,
            textColor=INK, spaceBefore=10, spaceAfter=5, keepWithNext=1,
        ),
        "q": ParagraphStyle(
            "q", fontName="Cue-Bold", fontSize=10.5, leading=14.5,
            textColor=INK, spaceBefore=12, spaceAfter=5, keepWithNext=1,
        ),
        "cell": ParagraphStyle(
            "cell", fontName="Cue", fontSize=9.5, leading=13, textColor=INK),
        "cellhead": ParagraphStyle(
            "cellhead", fontName="Cue-Bold", fontSize=9.5, leading=13,
            textColor=MUTED),
    }


class Rule(Table):
    def __init__(self, width: float):
        super().__init__([[""]], colWidths=[width], rowHeights=[1])
        self.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 0.6, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))


def make_table(rows: list[tuple[list[str], bool]], width: float,
               st: dict[str, ParagraphStyle]) -> Table:
    ncols = max(len(cells) for cells, _ in rows)
    col_widths = [width * 0.42, width * 0.58][:ncols]
    if ncols == 1:
        col_widths = [width]
    data = []
    header_rows = []
    for i, (cells, is_head) in enumerate(rows):
        style = st["cellhead"] if is_head else st["cell"]
        data.append([Paragraph(inline(c), style) for c in cells])
        if is_head:
            header_rows.append(i)
    tbl = Table(data, colWidths=col_widths, hAlign="LEFT")
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
    ]
    for i in header_rows:
        cmds.append(("LINEBELOW", (0, i), (-1, i), 0.8, MUTED))
    tbl.setStyle(TableStyle(cmds))
    return tbl


def parse(src: str, st: dict[str, ParagraphStyle], width: float) -> list:
    flow: list = []
    pending_table: list[tuple[list[str], bool]] = []
    spoken_buf: list[str] = []
    block_buf: list = []
    in_block = False

    def flush_table():
        nonlocal pending_table
        if pending_table:
            target = block_buf if in_block else flow
            target.append(make_table(pending_table, width, st))
            target.append(Spacer(1, 8))
            pending_table = []

    def flush_spoken():
        nonlocal spoken_buf
        if spoken_buf:
            target = block_buf if in_block else flow
            target.append(Paragraph(inline(" ".join(spoken_buf)), st["spoken"]))
            spoken_buf = []

    def flush_block():
        """Emit a block, keeping only its head with its first spoken line.

        Keeping a whole block together would push most blocks onto a fresh
        page and leave the previous one half empty; a block header stranded
        at the foot of a page is the only break that actually hurts at a
        lectern, so that is the only one prevented.
        """
        nonlocal in_block, block_buf
        if in_block:
            flush_spoken()
            flush_table()
            flow.append(CondPageBreak(1.3 * inch))
            head = block_buf[:3]
            flow.append(KeepTogether(head))
            flow.extend(block_buf[3:])
            flow.append(Spacer(1, 14))
            block_buf = []
            in_block = False

    lines = src.strip("\n").split("\n")
    para: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            target = block_buf if in_block else flow
            target.append(Paragraph(inline(" ".join(para)), st["commentary"]))
            para = []

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para()
            flush_spoken()
            flush_table()
            continue

        if stripped.startswith(">"):
            flush_para()
            flush_table()
            content = stripped[1:].strip()
            if not content:
                flush_spoken()
            else:
                spoken_buf.append(content)
            continue

        flush_spoken()

        if stripped.startswith("@TABLE ") or stripped.startswith("@THEAD "):
            flush_para()
            is_head = stripped.startswith("@THEAD ")
            cells = [c.strip() for c in stripped.split(" ", 1)[1].split("|")]
            pending_table.append((cells, is_head))
            continue

        flush_table()

        if stripped.startswith("@TITLE "):
            flush_para()
            flow.append(Paragraph(inline(stripped[7:]), st["title"]))
        elif stripped.startswith("@SUB "):
            flush_para()
            flow.append(Paragraph(inline(stripped[5:]), st["sub"]))
        elif stripped == "@RULE":
            flush_para()
            flow.append(Spacer(1, 10))
            flow.append(Rule(width))
            flow.append(Spacer(1, 14))
        elif stripped.startswith("@PART "):
            flush_para()
            flush_block()
            flow.append(PageBreak())
            flow.append(Paragraph(inline(stripped[6:]), st["part"]))
            flow.append(Rule(width))
            flow.append(Spacer(1, 12))
        elif stripped.startswith("@BLOCK "):
            flush_para()
            flush_block()
            num, name, secs = [p.strip()
                               for p in stripped[7:].split("|")]
            in_block = True
            block_buf = [Paragraph(
                f"{num}. {inline(name)}"
                f'&nbsp;&nbsp;<font name="Cue" size="9" color="#6B7280">'
                f"{secs}</font>", st["block"])]
        elif stripped.startswith("@CUE "):
            flush_para()
            target = block_buf if in_block else flow
            target.append(Paragraph("BOARD &rarr; " + inline(stripped[5:]),
                                    st["cue"]))
        elif stripped.startswith("@NOTE "):
            flush_para()
            target = block_buf if in_block else flow
            target.append(Paragraph(inline(stripped[6:]), st["note"]))
        elif stripped.startswith("@H "):
            flush_para()
            flush_block()
            flow.append(Paragraph(inline(stripped[3:]), st["h"]))
        elif stripped.startswith("@Q "):
            flush_para()
            flush_block()
            flow.append(Paragraph("Q. " + inline(stripped[3:]), st["q"]))
        else:
            para.append(stripped)

    flush_para()
    flush_spoken()
    flush_table()
    flush_block()
    return flow


def decorate(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Cue", 8)
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
    doc = BaseDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOT,
        title=DOC_TITLE, author="Nicko Fajardo",
    )
    frame = Frame(
        MARGIN_X, MARGIN_BOT, width, letter[1] - MARGIN_TOP - MARGIN_BOT,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="body", frames=[frame], onPage=decorate)])
    doc.build(parse(SCRIPT, st, width))
    print(f"wrote {OUT}")
    print(f"  {doc.page} pages, letter portrait, "
          f"{MARGIN_X / 72:.2f} in side margins")
    return 0


if __name__ == "__main__":
    sys.exit(main())
