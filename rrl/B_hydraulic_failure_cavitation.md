## TIER 1 (essential)

---

**Citation** | Brodribb, T. J., Brodersen, C. R., Carriqui, M., Tonet, V., Rodriguez Dominguez, C., & McAdam, S. (2021). Linking xylem network failure with leaf tissue death. *New Phytologist, 232*(1), 68–79.
**DOI** | 10.1111/nph.17577
**Access level** | ABSTRACT ONLY (Europe PMC core record; Wiley full text 403)
**Study type** | Empirical, optical + imaging observation of dehydrating leaves
**System studied** | Leaves of woody species under water stress
**Main finding** | Provides the first empirical demonstration of the causal chain from vein-network failure to tissue death: "water column breakage under tension in leaf veins which severs local leaf tissue water supply, immediately causing acute cellular dehydration and irreversible damage." Failure is described as a *catastrophic sequence* initiated in the vein network, and the authors explicitly frame it as "the primacy of vascular network failure in the death of leaves."
**Relevant variable** | Loss of continuous water-supply path → localised tissue death
**Exact relevance** | This is the single source that authorises the paper's central conceptual move. It establishes that *severance of a supply path within the leaf vein network* — not merely conduit-level conductivity loss — is the operative mechanism of leaf damage. This is what makes a connectivity criterion (GCC of the venation graph) a physiologically meaningful, rather than merely mathematical, quantity. It licenses the framing "loss of connected supply to a leaf region causes irreversible local damage" without requiring the paper to equate GCC loss with cavitation.
**Paragraph location** | Intro (motivating the connectivity criterion); Discussion-topology/physiology bridge
**Claim it can support** | Failure of the leaf vein network to maintain a continuous water-supply path to a tissue region has been shown empirically to cause immediate, irreversible cellular damage in that region, which is why network connectivity — not only bulk conductivity — is a functionally relevant descriptor of leaf hydraulic integrity.
**Strength** | Essential
**Caveat** | It does NOT establish a connectivity *threshold*, does not compute a giant connected component, and the severance it observes is caused by cavitation under tension — not by node deletion, and not by a parasitic sink. It shows local supply loss matters; it does not validate any particular percolation criterion.

---

**Citation** | Mander, L., & Williams, H. T. P. (2024). The robustness of some Carboniferous fossil leaf venation networks to simulated damage. *Royal Society Open Science, 11*(5), 240086.
**DOI** | 10.1098/rsos.240086
**Access level** | FULL TEXT READ (PMC11076108; Methods and Results)
**Study type** | Computational network-robustness analysis on traced real leaf venation
**System studied** | 7 Pennsylvanian fossil taxa (2 branched, 5 reticulate) + *Rhacopteris lindsaeformis* and living *Betula alba*; 9 taxa total
**Main finding** | Uses connected-component labelling — explicitly framed as percolation-based robustness, citing Newman (2010) — measuring the proportion of the venation network still attached to the structural vein by a continuous path, described as "a simple proxy for retention of a functional vascular transport system within the leaf." Removal was **random** only (random vein pixels; random 60-pixel blade holes). Result: branched networks collapse earliest (function falls toward ~0.05 by ~0.80 of network remaining), reticulate fossil networks collapse at ~0.85 remaining, and hierarchical reticulate *Betula alba* remains functional to ~0.60 remaining.
**Relevant variable** | Reticulation/loopiness vs. robustness under random element removal; largest-connected-component criterion
**Exact relevance** | This is the closest methodological precedent in existence to the present paper, and it independently reproduces the paper's central empirical result — reticulate venation is more robust to random removal than branched venation — using the *same* class of metric on *real* traced leaves. It corroborates the reticulation-enhancement result (median p_c 0.201 → 0.215; 88.6% of leaves improved, 0 worsened) from a completely independent dataset and taxonomic range. Critically, the authors state their own limitation: quantifying actual transport capacity "would require a model of fluid flow through the leaf," which they did not construct. The present paper's Hagen–Poiseuille + Kirchhoff solver is precisely that missing component, and this sentence is the cleanest available novelty anchor.
**Relevance (secondary)** | Also validates the choice of a *fractional-GCC* criterion as an accepted proxy in this literature, which softens the arbitrariness objection to the GCC < 50% rule.
**Paragraph location** | RRL; Methods (justifying GCC criterion); Discussion-reticulation; Novelty statement
**Claim it can support** | Percolation-style connected-component analysis has already been applied to real traced leaf venation networks and shows that reticulate architectures retain a connected transport path under substantially greater random damage than branched architectures; the present work extends that approach by coupling it to an explicit resistor-network flow solution, which prior robustness analyses of leaf venation lacked.
**Strength** | Essential
**Caveat** | Random removal only (no targeted attack), 9 taxa, mostly fossils, no Monte Carlo p_c estimate, no flow physics, and the authors explicitly disclaim that their damage simulations match real-world tolerance. It supports the *ordering* (reticulate > branched) far more strongly than any absolute threshold value.

---

**Citation** | Scoffoni, C., Albuquerque, C., Brodersen, C. R., Townes, S. V., John, G. P., Bartlett, M. K., Buckley, T. N., McElrone, A. J., & Sack, L. (2017). Outside-xylem vulnerability, not xylem embolism, controls leaf hydraulic decline during dehydration. *Plant Physiology, 173*(2), 1197–1210.
**DOI** | 10.1104/pp.16.01643
**Access level** | FULL TEXT READ (Oxford Academic)
**Study type** | Empirical — microCT imaging + hydraulic measurement + partitioning model
**System studied** | 8 angiosperm species from 8 families; microCT on 4
**Main finding** | Outside-xylem conductance (K_ox) decline accounted for **86–100% of K_leaf decline at turgor loss point** (mean 96%), **95–100% at P50,Kleaf** (mean 98%), and **75–100% at P88,Kleaf** (mean 93%). Only **5–8.5% of midrib conduits were embolised at turgor loss point**, with **no emboli in minor veins above turgor loss point**; substantial embolism (up to 44%) appeared only well beyond turgor loss. P50,Kx was **1.6 MPa more negative** than P50,Kleaf, while P50,Kox was only **0.1 MPa less negative** than P50,Kleaf. A model using P50,Kox alone explained 81% of cross-species variation in P50,Kleaf. Conclusion: "the decline of K_leaf during dehydration arose first and foremost due to the vulnerability of outside-xylem tissues."
**Relevant variable** | Partitioning of leaf hydraulic resistance and of hydraulic *decline* between xylem and outside-xylem pathways
**Exact relevance** | **This is the decisive defence of the failed K_leaf validation.** The paper's cross-check of modelled xylem-only K_leaf against measured whole-leaf conductance returned Spearman 0.187, p = 0.073, n = 93. Scoffoni et al. show that this is the *expected* outcome, not a model failure: measured K_leaf and its decline are 86–100% governed by a pathway the model does not represent at all. A xylem-only resistor network is being compared against a quantity dominated by bundle-sheath/mesophyll resistance. The validation that *did* succeed — reproduction of the source dataset's own Hagen–Poiseuille resistances across 119 leaves and 5,668,467 veins to ~1e-7 — is the appropriate test of the solver, and this source explains why the K_leaf comparison is the wrong test rather than a failed one.
**Secondary relevance** | The finding that **no emboli occur in minor veins above turgor loss point** independently corroborates the paper's haustorial-sink sweep result (0 vessels embolised at the calibrated K_h; 0 across all 31 gradients from 0–3.0 MPa; minimum margin 0.678 MPa). Minor-vein xylem is empirically *hard* to embolise, so a null embolism result at modest host water potentials is physiologically credible rather than a modelling artefact.
**Paragraph location** | Methods-validation; Results-interpretation (K_leaf cross-check); Limitations; Discussion-haustorial sink
**Claim it can support** | Because 86–100% of the decline in whole-leaf hydraulic conductance during dehydration is attributable to outside-xylem tissues, and because P50 of the leaf xylem is approximately 1.6 MPa more negative than P50 of the whole leaf, a xylem-only resistor-network model should not be expected to predict measured whole-leaf conductance; the weak and non-significant rank correlation observed here is consistent with that partitioning rather than evidence of solver error.
**Strength** | Essential
**Caveat** | 8 species only; and the finding is actively contested — Brodribb et al. (2016, *New Phytologist* 209) report strong agreement between leaf-vein embolism dynamics and K_leaf decline (see Counterevidence). The paper must present this as a live controversy it sits inside, not as settled fact. It also does NOT excuse the model from the K_leaf comparison; it explains the result.

---

**Citation** | Brodribb, T. J., Bienaimé, D., & Marmottant, P. (2016). Revealing catastrophic failure of leaf networks under stress. *Proceedings of the National Academy of Sciences, 113*(17), 4865–4869.
**DOI** | 10.1073/pnas.1522569113
**Access level** | ABSTRACT ONLY (verified Europe PMC; PNAS 403) + indexed Results excerpts
**Study type** | Empirical, novel optical embolism imaging of whole leaf networks
**System studied** | Architecturally diverse leaves incl. the fern *Adiantum capillus-veneris* and the angiosperm *Eucalyptus globulus*
**Main finding** | Two results matter here. (1) **Failure order is non-random and highly conserved**: "within an individual venation network, susceptibility to embolism always increased proportionally with the size of veins, and initial nucleation always occurred in the largest vein." (2) **Topology determines the failure mode**: "considerable diversity in the pattern of network failure was found between species, related to differences in vein network topology. The highest-risk network was found in a fern species, where single events caused massive disruption to leaf water supply, whereas safer networks in angiosperm leaves contained veins with composite properties, allowing a staged failure of water supply." Indexed Results also report a quiescent pre-embolism period ranging from ~30 min (*Adiantum*) to ~70 h (*E. globulus*) before large embolism events spread through the network.
**Relevant variable** | Vein-network topology vs. mode and abruptness of hydraulic failure; vein size vs. embolism order
**Exact relevance** | Does double duty. **Supporting**: it is the strongest empirical statement in the literature that vein network topology governs whether leaf hydraulic failure is catastrophic-in-one-event or staged/graceful. The fern (open, low-loop venation) fails catastrophically; reticulate angiosperm networks degrade in stages. That is the physiological interpretation of what the paper measures as a percolation threshold, and it directly underwrites the reticulation-as-resistance-trait framing and the loop-fraction result (median 0.776). **Constraining**: the "largest vein first, always" rule is direct counterevidence to random node removal (see Counterevidence). It does, however, partially rehabilitate the degree-targeted scenario — major veins are the high-junction-degree elements of a venation graph — making the targeted p_c (empirical median 0.169; synthetic 0.2023) the more physiologically motivated of the two bounds, and random p_c (0.200 empirical, 0.271 synthetic) the conservative upper bound.
**Paragraph location** | Intro; RRL; Discussion-reticulation; Discussion-limitations (removal-order); Methods-justification of targeted scenario
**Claim it can support** | Direct optical observation of embolism in whole leaves shows that the *pattern* of hydraulic network failure differs systematically with vein network topology — poorly reticulate fern venation suffering abrupt whole-network disruption from single events while reticulate angiosperm venation fails in stages — which is the physiological counterpart of the sharper versus more gradual connectivity breakdown seen in low- versus high-reticulation networks here.
**Strength** | Essential
**Caveat** | It does not compute connectivity, a giant component, or any percolation threshold; "catastrophic" is used descriptively, not in the critical-phenomena sense. It also explicitly makes embolism *ordered by vein size*, which no random-removal model reproduces. It reports no p_c and no universality claim — consistent with this paper making none.

---

**Citation** | Mrad, A., Johnson, D. M., Love, D. M., & Domec, J.-C. (2021). The roles of conduit redundancy and connectivity in xylem hydraulic functions. *New Phytologist, 231*(3), 996–1007.
**DOI** | 10.1111/nph.17429
**Access level** | ABSTRACT ONLY (Europe PMC core; Wiley 403)
**Study type** | Analytical + computational network model, validated against anatomy
**System studied** | Modelled angiosperm xylem tissue; validated with anatomical measurements of *Acer* branch xylem
**Main finding** | Explicitly develops the connectivity–hydraulics link using "graph theory, percolation theory and computational modeling of xylem." Finds that, among vessel-bearing species, **increases in conduit connectivity improve resistance to embolism spread without penalising hydraulic conductivity**, i.e. no safety–efficiency cost to redundancy. Also finds the commonly measured *grouping index* "fails to capture the totality of the effect of conduit connectivity on xylem hydraulics," and proposes connectivity variation as an explanation for why the safety–efficiency trade-off is weaker than predicted.
**Relevant variable** | Conduit connectivity / redundancy; percolation formalism in xylem
**Exact relevance** | **This is the paper's licence to use percolation theory on plant vascular networks at all.** It is a peer-reviewed *New Phytologist* paper that applies percolation and graph theory to xylem and concludes that connectivity redundancy confers resistance — the same directional claim the present paper makes for venation reticulation (<k> Spearman 0.733 with p_c; synthetic causal grid Spearman 0.991, 14:1 dominance over D per SD). It also supplies a precedent for the claim that a simple scalar anatomical index is insufficient and a genuine network treatment is required — which is the methodological justification for graph-building the Matos traces rather than using vein density.
**Author-list note** | The manuscript reportedly carries two conflicting author lists. The verified list is **Assaad Mrad, Daniel M. Johnson, David M. Love, Jean-Christophe Domec** (4 authors). It is *not* the same list as Mrad et al. 2018 (Mrad, Domec, Huang, Lens, Katul). Fix this before submission.
**Paragraph location** | Intro; RRL; Methods-justification; Discussion-reticulation
**Claim it can support** | Percolation and graph-theoretic treatments of plant vascular tissue are established in the plant-hydraulics literature, and modelling of angiosperm xylem indicates that greater conduit connectivity improves resistance to embolism spread without a conductivity penalty — consistent with the positive association between mean degree and percolation threshold reported here.
**Strength** | Essential
**Caveat** | It concerns *stem xylem conduits connected by pit membranes*, not leaf vein junctions — precisely the known vulnerability of this paper. Its "connectivity" is inter-conduit pit connectivity, a different object from venation-graph degree. It reports no p_c value transferable here. And its directional conclusion **conflicts with Loepfe et al. (2007)** (below), which must be acknowledged.

---

**Citation** | Sack, L., Dietrich, E. M., Streeter, C. M., Sánchez-Gómez, D., & Holbrook, N. M. (2008). Leaf palmate venation and vascular redundancy confer tolerance of hydraulic disruption. *Proceedings of the National Academy of Sciences, 105*(5), 1567–1572.
**DOI** | 10.1073/pnas.0709333105
**Access level** | ABSTRACT ONLY (Europe PMC core; PMC2234185)
**Study type** | Empirical manipulation — experimental vein severing with hydraulic and gas-exchange measurement
**System studied** | Woody angiosperm leaves with contrasting (pinnate vs palmate) venation
**Main finding** | Severing the midrib near the leaf base caused pinnately veined leaves to "decline strongly in leaf hydraulic conductance, stomatal conductance, and photosynthetic rate, whereas palmately veined leaves were minimally affected." Higher primary vein density predicted better tolerance of midrib damage. **All tested leaves tolerated damage to secondary and higher-order veins completely**, attributed to the reticulate minor vein network protecting against hydraulic disruption.
**Relevant variable** | Vascular redundancy/reticulation vs. *measured* hydraulic and physiological consequence of element removal
**Exact relevance** | This is the empirical validation of the paper's entire operation. It is the one study that actually **removes elements from a real leaf vein network and measures the hydraulic and photosynthetic consequence** — exactly the physical experiment the percolation simulation abstracts. It confirms both directions of the paper's result: (i) redundancy/reticulation buffers the effect of removal (the reticulation-enhancement result, 88.6% improved / 0 worsened), and (ii) removal of *topologically central, high-degree* elements (the basal midrib) is far more damaging than removal of peripheral elements — the empirical justification for contrasting degree-targeted (p_c 0.169) against random (p_c 0.200) removal, and for the finding that 100/100 leaves had targeted < random (15.7% reduction).
**Paragraph location** | Intro; RRL; Methods-justification of targeted vs random; Discussion-reticulation; Discussion-topology/physiology bridge
**Claim it can support** | Experimental severing of veins in real leaves shows that the hydraulic and photosynthetic cost of removing a vein element depends strongly on its position in the network — basal midrib severance sharply reduces leaf hydraulic conductance in pinnate leaves while palmate leaves with redundant primary pathways are minimally affected, and reticulate minor-vein damage is tolerated entirely — which is the measured, physiological analogue of the difference between targeted and random element removal reported here.
**Strength** | Essential
**Caveat** | Small number of species; cutting is a macroscopic mechanical lesion, not embolism and not haustorial sink; it demonstrates tolerance of *single, large* cuts rather than the progressive fractional removal that a percolation threshold describes; and it reports no threshold fraction.

---

**Citation** | Lu, D., Smith-Martin, C. M., Muscarella, R., Uriarte, M., & Zheng, T. (2025). A spatio-temporal model of embolism propagation in leaf vein networks. *AoB PLANTS, 17*(4), plaf020.
**DOI** | 10.1093/aobpla/plaf020
**Access level** | FULL TEXT READ (Oxford Academic)
**Study type** | Statistical model (Bayesian spatial survival analysis) applied to observed leaf embolism sequences
**System studied** | 53 leaf samples across multiple species, vein networks with observed embolism event ordering
**Main finding** | Models embolism as a spatially dependent survival process using ICAR priors over the venation neighbourhood structure. Incorporating spatial dependency **reduced posterior predictive error and uncertainty across most species**, i.e. embolism events are spatially autocorrelated, not independent. **47 of 53 leaf samples showed positive vein-thickness coefficients, confirming thicker veins embolise first.** Crucially, a positive correlation (r > 0.5) was found between the vein-thickness coefficient and **vein network connectivity** — "leaves with more connected vein networks exhibit a more pronounced pattern of embolizing from thicker to thinner veins." Best model C-index 0.542 (SD 0.151).
**Relevant variable** | Spatial dependence of embolism; vein thickness ordering; network connectivity as a modulator
**Exact relevance** | The most recent and most directly comparable work: same object (leaf vein networks), same question (how does failure propagate through them), different method. Three consequences. (1) **It confirms connectivity is a functionally consequential venation property in embolism dynamics**, supporting the paper's emphasis on <k>. (2) It is **strong counterevidence to random node removal**: embolism is spatially clustered and thickness-ordered. (3) It defines the correct future-work scenario — a *thickness-ranked* or *radius-ranked* removal order, which is directly computable from the Matos calibrated data and would be a far better physiological analogue than either random or degree-targeted removal. Note also the modest C-index (0.542): even a purpose-built spatial statistical model predicts embolism order only weakly, which is a useful humility anchor.
**Paragraph location** | RRL; Discussion-limitations (removal order); Future work
**Claim it can support** | Recent modelling of observed embolism sequences in leaf vein networks shows that embolism events are spatially autocorrelated and ordered by vein thickness rather than occurring independently at random, and that this ordering is more pronounced in more highly connected networks; random node removal therefore represents a null structural scenario rather than a model of embolism propagation.
**Strength** | Essential (as both support and constraint)
**Caveat** | Statistical, not mechanistic; no percolation threshold; explicitly does not discuss or critique percolation approaches; the authors state the biological mechanism behind the connectivity–thickness interaction "remains unclear." Modest predictive performance.

---

## TIER 2 (strong supporting)

---

**Citation** | Scoffoni, C., Albuquerque, C., Brodersen, C. R., Townes, S. V., John, G. P., Cochard, H., Buckley, T. N., McElrone, A. J., & Sack, L. (2017). Leaf vein xylem conduit diameter influences susceptibility to embolism and hydraulic decline. *New Phytologist, 213*(3), 1076–1092.
**DOI** | 10.1111/nph.14256 | **Access** | ABSTRACT ONLY (Europe PMC core; Wiley 403) + indexed Results excerpts (r² values below are from indexed article text, not read in situ — verify against the PDF before citing the numbers)
**Study type** | Empirical — X-ray microCT + hydraulics + anatomy + 3D physiological modelling | **System** | 8 diverse species, petioles through minor veins
**Main finding** | Tests vulnerability segmentation *within* leaves and **rejects it in the expected direction**: decline of leaf xylem conductance (Kx) "was driven by embolism initiating in petioles and midribs across all species," not in higher-order veins, and Kx vulnerability correlated strongly with petiole and midrib conduit dimensions. Simulations showed no significant contribution of conduit collapse. Indexed results: P88,Kx correlated with midrib conduit size and number (r² = 0.72 and 0.54, P < 0.05); petiole/midrib mean conduit size correlated with the potential at 50% embolised conduits under microCT (r² = 0.82–0.88, P < 0.05).
**Relevant variable** | Conduit diameter as the anatomical determinant of leaf embolism; large-vein-first failure order
**Exact relevance** | Corroborates Brodribb et al. (2016 PNAS) from a fully independent method: failure begins in the *largest* elements. It is simultaneously (a) support for treating the major-vein/high-degree backbone as the critical structure, and (b) the strongest anatomical counterargument to a purely topological account — vulnerability tracks *conduit diameter*, a variable the present model uses only for conductance, never for failure probability. It also matters that petioles are where failure initiates, and **the Matos crop windows contain no petioles at all** — the paper's networks structurally exclude the site where leaf xylem embolism actually starts. That must appear in Limitations.
**Paragraph location** | RRL; Discussion-limitations (crop windows, no petioles); Limitations
**Claim it can support** | Leaf xylem embolism initiates in the petiole and midrib rather than in minor veins, and leaf xylem vulnerability scales with major-vein conduit dimensions; because the venation traces analysed here are crop windows that exclude petioles, they omit the anatomical location at which leaf xylem failure is observed to begin.
**Strength** | Strong | **Caveat** | 8 species; does not address network connectivity at all; and its conclusion sits in tension with the same group's *Plant Physiology* paper on outside-xylem control of K_leaf (the two are compatible — Kx vs K_leaf — but must be stated carefully).

---

**Citation** | Loepfe, L., Martinez-Vilalta, J., Piñol, J., & Mencuccini, M. (2007). The relevance of xylem network structure for plant hydraulic efficiency and safety. *Journal of Theoretical Biology, 247*(4), 788–803.
**DOI** | 10.1016/j.jtbi.2007.03.036 | **Access** | ABSTRACT ONLY (Europe PMC core)
**Study type** | Theoretical network model, graph theory + Monte Carlo | **System** | Idealised wood segments
**Main finding** | Both "maximum hydraulic conductivity and vulnerability to embolism **increase** with the connectivity of the xylem network," because connectivity sets the fraction of potential paths available both for transport and for embolism spread. Concludes "the xylem can no longer be interpreted as the mere sum of its conduits."
**Exact relevance** | The founding precedent for graph-theoretic + Monte Carlo treatment of plant vascular networks — the same methodological pairing used here. But its directional result is **opposite in sign** to Mrad et al. (2021) and to the paper's reticulation-enhancement finding, *for the embolism-spread variable*. This conflict is genuinely useful: it lets the paper draw the line precisely. Higher connectivity increases *structural* robustness to element loss (this paper, Mander & Williams, Sack et al.) while its effect on *embolism propagation* is contested (Loepfe up, Mrad down). The paper's result is a structural-robustness result and must be stated as such, never as an embolism-resistance result.
**Paragraph location** | RRL; Methods-justification; Discussion-topology/physiology line
**Claim it can support** | Graph-theoretic and Monte Carlo treatments of plant vascular networks are long established, and they show that network connectivity is a first-order determinant of both transport capacity and failure behaviour; however, the sign of the connectivity effect on embolism spread specifically remains contested in that literature.
**Strength** | Strong | **Caveat** | Idealised, not anatomically derived; stem wood not leaf venation; 2007 model superseded in detail by Mrad et al.

---

**Citation** | Mrad, A., Domec, J.-C., Huang, C.-W., Lens, F., & Katul, G. (2018). A network model links wood anatomy to xylem tissue hydraulic behaviour and vulnerability to cavitation. *Plant, Cell & Environment, 41*(12), 2718–2730.
**DOI** | 10.1111/pce.13415 | **Access** | ABSTRACT ONLY (Europe PMC core)
**Study type** | Numerical network model | **System** | Diffuse-porous angiosperm xylem; validated on *Acer glabrum* terminal branch
**Main finding** | Reproduces a real vulnerability curve "relying only on real observations of xylem tissue anatomy." Sensitivity analysis shows VC shape and position along the tension axis are "heavily dependent on anatomy," and the main result is that pit-scale/vessel-scale anatomy **together with xylem network topology** significantly affect VCs. Closes by urging more research on 3D network structure of xylem tissue.
**Exact relevance** | Precedent for anatomy-derived network models producing physiologically meaningful outputs — the same logic as building networks from calibrated Matos traces. Its concluding call for network-structure research is a clean gap statement to cite in the Introduction. Also note the author list differs from Mrad et al. 2021; check which of the manuscript's two conflicting lists belongs to which paper.
**Paragraph location** | Intro (gap); RRL; Methods-justification
**Claim it can support** | Network models built directly from measured vascular anatomy have successfully reproduced observed vulnerability curves, and network topology has been identified as a significant determinant of tissue-scale hydraulic behaviour alongside conduit- and pit-scale anatomy.
**Strength** | Strong | **Caveat** | Stem xylem, pit-membrane-mediated spread; models cavitation explicitly, which this paper does not.

---

**Citation** | Adams, H. D., et al. (2017). A multi-species synthesis of physiological mechanisms in drought-induced tree mortality. *Nature Ecology & Evolution, 1*(9).
**DOI** | 10.1038/s41559-017-0248-x | **Access** | PUBLISHER RECORD ONLY (page range not verified — confirm before citing)
**Study type** | Multi-species synthesis / meta-analysis | **System** | Multiple tree taxa at mortality
**Main finding** | Xylem hydraulic failure was near-ubiquitous at drought-induced mortality; **loss of xylem conductivity above 60% is associated with mortality**, whereas carbon starvation is not universal. Of 13 cases with both measures, trees died with high PLC and low NSC (8/13) or with high PLC only (5/13).
**Exact relevance** | Establishes that a *functional threshold criterion* for hydraulic failure is standard practice in this field, which normalises the paper's use of a defined collapse criterion (P(GCC < 50% of N₀) = 0.50). But it is also the sharpest reminder of the units problem: PLC 60% is a *conductivity* fraction, GCC 50% is a *connectivity* fraction, and the two are not interconvertible. Use it to motivate having a threshold; never to calibrate the value of one.
**Paragraph location** | Intro; Methods-justification of the collapse criterion; Discussion-topology/physiology line
**Claim it can support** | Defined functional thresholds are the established currency of hydraulic-failure research, with loss of xylem conductivity above roughly 60% associated with tree mortality across taxa; the connectivity criterion used here is analogous in role but distinct in units and must not be read as a percentage loss of conductivity.
**Strength** | Strong | **Caveat** | Whole-tree stems, not leaves; PLC ≠ GCC; verify pagination.

---

**Citation** | Pritzkow, C., Brown, M. J. M., Carins-Murphy, M. R., Bourbia, I., Mitchell, P. J., Brodersen, C., Choat, B., & Brodribb, T. J. (2022). Conduit position and connectivity affect the likelihood of xylem embolism during natural drought in evergreen woodland species. *Annals of Botany, 130*(3), 431–444.
**DOI** | 10.1093/aob/mcac053 | **Access** | ABSTRACT ONLY (Europe PMC core; PMC9486930)
**Study type** | Empirical, X-ray CT under *natural* field drought | **System** | Branch xylem of three tree species
**Main finding** | "The probability of embolism was **independent of conduit diameter** but associated with conduit **position**." Embolism was **not randomly distributed**: they observed "circumferential clustering of high and low embolism density," indicating spread among same-aged conduits; older xylem accumulated more embolism. Concludes embolism under natural drought "probably propagates by air spreading from embolized into neighbouring conduits in a circumferential pattern."
**Exact relevance** | Dual-purpose. **Support**: conduit *position within the network* — not diameter — determines failure probability, which is a position/topology argument in the paper's favour and a partial rebuttal to the pure-anatomy account. **Constraint**: the clustering finding is prime counterevidence to random removal (see Counterevidence).
**Paragraph location** | RRL; Discussion-limitations; Counterevidence handling
**Claim it can support** | Field observations of embolism under natural drought indicate that a conduit's position and connectivity within the network, rather than its diameter alone, govern its likelihood of embolism, and that embolism is spatially clustered rather than randomly distributed.
**Strength** | Strong | **Caveat** | Stem xylem; directly contradicts the diameter-based account of Scoffoni et al. (2017) and Isasa et al. (2023) — flag the disagreement rather than picking a side.

---

**Citation** | Charrier, G., Torres-Ruiz, J. M., Badel, E., Burlett, R., Choat, B., Cochard, H., Delmas, C. E., Domec, J.-C., Jansen, S., King, A., Lenoir, N., Martin-StPaul, N., Gambetta, G. A., & Delzon, S. (2016). Evidence for hydraulic vulnerability segmentation and lack of xylem refilling under tension. *Plant Physiology, 172*(3), 1657–1668.
**DOI** | 10.1104/pp.16.01079 | **Access** | ABSTRACT ONLY (Europe PMC core)
**Study type** | Empirical, X-ray microCT on intact plants | **System** | *Vitis vinifera*, *V. riparia*
**Main finding** | Stem P50 = **−1.7 MPa** (*V. vinifera*) and **−1.3 MPa** (*V. riparia*); within *V. vinifera*, stem P50 = −1.7 MPa vs **petiole P50 = −1.0 MPa** — clear vulnerability segmentation, distal organs sacrificed to protect the perennial stem. **No refilling occurred while bulk xylem pressure remained negative** (ΔPLC = 0.02 ± 0.01%); recovery occurred only where pressure became positive.
**Exact relevance** | Two jobs. (1) **Vulnerability segmentation** is the physiological frame in which a *leaf*-level collapse analysis makes sense: the leaf is the designed sacrificial element, so pre-symptomatic leaf-level vascular degradation preceding whole-plant symptoms is exactly the expected architecture — this is the cleanest support for the paper's "pre-symptomatic" framing. (2) **P50 = −1.0 MPa in a petiole** is direct evidence that the model's −2.0 MPa cavitation threshold is not conservative for all taxa (see Counterevidence). Also, the no-refilling-under-tension result partially defends the static-network assumption.
**Paragraph location** | Intro (pre-symptomatic framing); Discussion-haustorial sink; Limitations (threshold choice)
**Claim it can support** | Hydraulic vulnerability segmentation, in which distal organs such as petioles and leaves embolise at substantially less negative water potentials than perennial stems, provides the physiological rationale for expecting leaf-level vascular degradation to precede whole-plant symptoms; measured petiole P50 values as shallow as −1.0 MPa also indicate that any single generic cavitation threshold will be conservative for some taxa and permissive for others.
**Strength** | Strong | **Caveat** | Two *Vitis* species only; grapevine is unusually vulnerable; concerns stems/petioles, not the minor-vein networks modelled here.

---

**Citation** | Katifori, E., Szöllősi, G. J., & Magnasco, M. O. (2010). Damage and fluctuations induce loops in optimal transport networks. *Physical Review Letters, 104*(4), 048704.
**DOI** | 10.1103/PhysRevLett.104.048704 | **Access** | PUBLISHER RECORD ONLY + preprint record (arXiv:0906.0006)
**Study type** | Theoretical optimisation | **System** | Transport networks, explicitly inspired by leaf venation
**Main finding** | Transport networks optimised purely for efficiency are loopless trees; introducing either (i) resilience to random damage, averaged over damage to each link, or (ii) sparse/fluctuating load, produces optima containing **loops**. Both criteria independently generate reticulation.
**Exact relevance** | Supplies the theoretical *why* behind the paper's central empirical result. If loops in venation exist because they are optimal under damage, then a measurement showing that higher loop fraction and higher <k> raise the collapse threshold (loop fraction Spearman 0.727 with p_c; <k> 0.733) is recovering the selective rationale, not just a graph artefact. Pairs with Mander & Williams (2024) on the fossil record and Sack et al. (2008) on measured function to make a three-way argument: theory predicts loops for damage tolerance, the fossil record shows reticulation arising with greater damage robustness, and experiments show reticulate leaves tolerate vein damage.
**Paragraph location** | Intro; Discussion-reticulation (theoretical grounding)
**Claim it can support** | Optimisation theory shows that loops in transport networks are the optimal response to random damage and to fluctuating load, providing a theoretical basis for interpreting reticulation in leaf venation as a damage-tolerance trait.
**Strength** | Strong | **Caveat** | Abstract physics, no plant physiology, no hydraulics, no water potentials; assumes random damage, which the embolism literature contradicts.

---

**Citation** | Martin-StPaul, N., Delzon, S., & Cochard, H. (2017). Plant resistance to drought depends on timely stomatal closure. *Ecology Letters, 20*(11), 1437–1447.
**DOI** | 10.1111/ele.12851 | **Access** | ABSTRACT ONLY (Europe PMC core)
**Study type** | Meta-analysis + hydraulic modelling | **System** | Cross-species drought-response traits
**Main finding** | Identifies "an absolute limit by which stomata closure must occur to avoid rapid death." The water potential triggering stomatal closure and that triggering embolism onset **matched in only a few species**, with safety margins widening as embolism resistance increased — challenging the assumed tight stomatal–hydraulic coordination.
**Exact relevance** | Two uses. **Support**: it establishes that hydraulic risk accumulates in a phase where stomatal regulation is still operating and visible symptoms have not appeared, which is the physiological content of "pre-symptomatic." **Constraint**: it also establishes that stomatal closure is an active dynamic control that intervenes *before* embolism in most species — the model has no stomatal regulation, and this source names that omission.
**Paragraph location** | Intro (pre-symptomatic framing); Limitations (static, unregulated network)
**Claim it can support** | Stomatal closure and embolism onset are decoupled in most species, with stomata closing well before the embolism threshold is reached, so a static hydraulic network model without stomatal regulation describes a structural failure envelope rather than the trajectory an intact regulating plant would actually follow.
**Strength** | Strong | **Caveat** | Meta-analytic; stem-focused; says nothing about network topology.

---

**Citation** | McKown, A. D., Cochard, H., & Sack, L. (2010). Decoding leaf hydraulics with a spatially explicit model: Principles of venation architecture and implications for its evolution. *The American Naturalist, 175*(4), 447–460.
**DOI** | 10.1086/650721 | **Access** | ABSTRACT ONLY (Europe PMC core)
**Study type** | Spatially explicit hydraulic model (program K_leaf) | **System** | Realistic simulated leaves
**Main finding** | Kx and K_leaf both increase with individual vein-order conductivities and densities. For hierarchical venation the greatest effect comes from raising conductivity of *lower* vein orders and density of *higher* vein orders. Vein-order conductivities are co-limiting, as are densities, and the effects of conductivities and densities are **orthogonal**. Both vein hierarchy and vein tapering raise Kx relative to xylem construction cost.
**Exact relevance** | The direct methodological ancestor of this paper's solver: a spatially explicit resistor treatment of leaf venation with hierarchical vein orders. Its orthogonality result — conductivity effects and density/topology effects are independent axes — is a strong prior justification for the paper's synthetic causal grid, which decouples <k> from D and finds <k> dominant 14:1 per SD.
**Paragraph location** | RRL; Methods-justification (resistor network on venation)
**Claim it can support** | Spatially explicit resistor-network modelling of leaf venation is an established approach, and it indicates that vein conductivity and venation density/architecture act as orthogonal determinants of leaf hydraulic conductance, supporting the separation of conductance and topology as independent axes of variation.
**Strength** | Moderate–Strong | **Caveat** | Simulated idealised leaves, not traced real ones; models conductance only, no failure, no percolation, no damage.

---

## TIER 3 (contextual)

- **Choat, B., Jansen, S., Brodribb, T. J., Cochard, H., Delzon, S., Bhaskar, R., Bucci, S. J., Feild, T. S., Gleason, S. M., Hacke, U. G., Jacobsen, A. L., Lens, F., Maherali, H., Martínez-Vilalta, J., Mayr, S., Mencuccini, M., Mitchell, P. J., Nardini, A., Pittermann, J., Pratt, R. B., Sperry, J. S., Westoby, M., Wright, I. J., & Zanne, A. E. (2012). Global convergence in the vulnerability of forests to drought. *Nature, 491*(7426), 752–755.** DOI 10.1038/nature11688 — ABSTRACT ONLY. 70% of 226 forest species from 81 sites operate with hydraulic safety margins <1 MPa, independent of mean annual precipitation. Use for the Introduction's stakes paragraph and, importantly, as the scale reference for the paper's minimum host leaf water potential of −1.02 MPa against a −2.0 MPa threshold: a 0.98 MPa margin is *typical*, not comfortable, on this global distribution.

- **Tyree, M. T., & Sperry, J. S. (1989). Vulnerability of xylem to cavitation and embolism. *Annual Review of Plant Physiology and Plant Molecular Biology, 40*, 19–38.** DOI 10.1146/annurev.pp.40.060189.000315 — PUBLISHER RECORD ONLY (indexed sources give both 19–36 and 19–38; verify pagination). The canonical origin of "runaway embolism" — the positive feedback in which conductivity loss raises tension, causing further cavitation. This is the *physiological* concept the percolation threshold structurally resembles, and the paper should name the resemblance explicitly while stating that it is an analogy, not an identity.

- **Urli, M., Porté, A. J., Cochard, H., Guengant, Y., Burlett, R., & Delzon, S. (2013). Xylem embolism threshold for catastrophic hydraulic failure in angiosperm trees. *Tree Physiology, 33*(7), 672–683.** DOI 10.1093/treephys/tpt030 — ABSTRACT ONLY. Minimum recoverable water potential ranged **−3.4 to −6.0 MPa across five angiosperms**, and the irreversible-damage embolism threshold was **close to 88%**, not 50%. Two uses: a precedent for "catastrophic threshold" language, and hard evidence that the point of no return is species-specific and far more negative than −2.0 MPa in many taxa.

- **Brodribb, T. J., Skelton, R. P., McAdam, S. A. M., Bienaimé, D., Lucani, C. J., & Marmottant, P. (2016). Visual quantification of embolism reveals leaf vulnerability to hydraulic failure. *New Phytologist, 209*(4), 1403–1409.** DOI 10.1111/nph.13846 — ABSTRACT ONLY. Reports "very strong agreement between the dynamics of embolism formation during desiccation and decline of leaf hydraulic conductance" in four angiosperms, and that embolism occurs *after* stomatal closure. Cite as the counterweight to Scoffoni et al. (2017 *Plant Physiology*) — the xylem-vs-outside-xylem control of K_leaf decline is an unresolved dispute, which is the honest framing for the failed K_leaf validation.

- **Johnson, K. M., Brodersen, C., Carins-Murphy, M. R., Choat, B., & Brodribb, T. J. (2020). Xylem embolism spreads by single-conduit events in three dry forest angiosperm stems. *Plant Physiology, 184*(1), 212–222.** DOI 10.1104/pp.20.00464 — ABSTRACT ONLY. **>80% of cavitation events were discrete, temporally separated single-vessel events**; the species with highest vessel connectivity (*Acacia mearnsii*) had the most multi-vessel events. Use in Limitations: in low-connectivity xylem, failure is *not* a propagating cascade at all.

- **Avila, R. T., Guan, X., Kane, C. N., Cardoso, A. A., Batz, T. A., DaMatta, F. M., Jansen, S., & McAdam, S. A. M. (2022). Xylem embolism spread is largely prevented by interconduit pit membranes until the majority of conduits are gas-filled. *Plant, Cell & Environment, 45*(4), 1204–1215.** DOI 10.1111/pce.14253 — ABSTRACT ONLY. Individual conduits have conserved, conduit-specific embolism thresholds; connectivity-mediated spread only becomes important once a majority of conduits are already gas-filled; **no refilling was observed upon rehydration**. The strongest single argument that a connectivity-driven cascade is a *late*-stage phenomenon, not a pre-symptomatic one.

- **Isasa, E., Link, R. M., Jansen, S., Tezeh, F. R., Kaack, L., Sarmento Cabral, J., & Schuldt, B. (2023). Addressing controversies in the xylem embolism resistance–vessel diameter relationship. *New Phytologist, 238*(1), 283–296.** DOI 10.1111/nph.18731 — ABSTRACT ONLY. Across 20 temperate broadleaf species, a robust *interspecific* P50–vessel diameter relationship exists but **no intraspecific relationship**, and inconsistencies in the literature trace to trait range and data aggregation level. Use to show that even the anatomy-based alternative explanation is contested and scale-dependent.

- **Katifori et al. (2010)** and **Mander & Williams (2024)** also serve here as the pair anchoring the loops-for-damage-tolerance argument across theory and the fossil record.

---

## THE TOPOLOGY-VS-PHYSIOLOGY LINE

**The core problem.** The percolation pipeline produces a *connectivity* quantity: p_c, the removed-node fraction at which the giant connected component drops below half the original node count with probability 0.5. Every quantity in the hydraulic-failure literature is a *conductivity* quantity (PLC, P50, P88, K_leaf) or a *water-potential* quantity (Ψ). There is no published conversion between them, and no source in this search establishes one. Every sentence in the paper that crosses from p_c to hydraulic failure must be a statement about *structural failure modes*, never about cavitation, PLC, or water potential.

**Three things also make the crossing harder in the specific direction the paper travels.** First, the hydraulic sink and the percolation collapse are already demonstrated to be decoupled *within the paper's own results*: at the calibrated K_h = 0.0392, no network collapses at any haustorial attachment density, and zero vessels embolise across all 31 gradients from 0 to 3.0 MPa (minimum margin 0.678 MPa). Second, the K_leaf cross-check failed (Spearman 0.187, p = 0.073, n = 93). Third, the literature says removal is not random. So the paper is not in a position to claim the analogy — it is in a position to *characterise* it precisely, which is a stronger and more publishable posture.

### What the paper CAN say, and who authorises it

**1. That loss of a connected supply path within the leaf vein network is a real, observed, damaging event.**
Authorised by **Brodribb et al. (2021, *New Phytologist* 232:68–79)**, which empirically demonstrates that breakage of the water column in leaf veins severs local tissue water supply and causes immediate irreversible cellular damage. This is the single most important authorisation and it should be cited at the exact point where GCC is introduced.

**2. That percolation and graph-theoretic analysis of plant vascular networks is established practice.**
Authorised by **Mrad et al. (2021)** — explicitly "graph theory, percolation theory and computational modeling of xylem," in *New Phytologist* — plus **Loepfe et al. (2007)** and **Mrad et al. (2018)**.

**3. That connected-component robustness has already been applied to real traced leaf venation.**
Authorised by **Mander & Williams (2024)**, who use exactly this metric on traced leaves and call it "a simple proxy for retention of a functional vascular transport system within the leaf." Their word is **proxy**, and the paper should adopt that exact register.

**4. That vein network topology demonstrably changes the mode of hydraulic failure.**
Authorised by **Brodribb et al. (2016, PNAS)** — fern venation fails catastrophically from single events, reticulate angiosperm venation fails in stages — and independently by **Sack et al. (2008, PNAS)**, where palmate/redundant leaves were minimally affected by midrib severance while pinnate leaves declined strongly in K_leaf, g_s *and* photosynthesis. Sack et al. is the one place where topological redundancy is shown to buffer *measured* hydraulic and photosynthetic function.

**5. That reticulation is a damage-tolerance trait.**
Authorised by the theory–fossil–experiment triad: **Katifori et al. (2010)** (loops are the optimum under random damage), **Mander & Williams (2024)** (reticulate networks are more robust in the fossil record), **Sack et al. (2008)** (reticulate minor-vein networks tolerate vein damage completely). This is the strongest-supported claim the paper makes and the reticulation-enhancement result (p_c 0.201 → 0.215, 88.6% improved, 0 worsened) should be foregrounded on this basis.

**6. That defined failure thresholds are normal currency in this field.**
Authorised by **Adams et al. (2017)** (PLC > 60% at mortality) and **Urli et al. (2013)** (irreversible-damage threshold near 88%). This normalises *having* a threshold criterion without licensing its numerical value.

**7. That the degree-targeted scenario is the more physiologically motivated of the two removal orders.**
Partially authorised by **Brodribb et al. (2016, PNAS)** (nucleation always in the largest vein; susceptibility scales with vein size), **Scoffoni et al. (2017, *New Phytologist*)** (failure initiates in petiole and midrib), **Lu et al. (2025)** (thicker veins embolise first in 47/53 samples), and **Pritzkow et al. (2022)** (position, not diameter, sets embolism probability). Since major veins are the high-degree junctions of a venation graph, targeted removal is a coarse structural surrogate for large-vein-first failure. This reframes the targeted p_c (empirical median 0.169; 100/100 leaves targeted < random; 15.7% reduction) as the physiologically motivated bound and the random p_c (0.200) as the conservative null — a genuine strengthening of the results section. **But state it as a structural surrogate, and note that vein size and node degree are correlated, not identical.**

### What the paper CANNOT say

- **Cannot say GCC fragmentation is cavitation, embolism, or hydraulic failure.** No source supports it. Mander & Williams explicitly disclaim it, noting that measuring transport capacity "would require a model of fluid flow through the leaf."
- **Cannot equate p_c with P50, P88, or PLC.** Different units, different physics, no published mapping.
- **Cannot claim random node removal models embolism.** Contradicted by five independent sources (Brodribb 2016; Pritzkow 2022; Johnson 2020; Avila 2022; Lu 2025). Random removal is a *null structural scenario*, and should be named as such in the Methods, not just conceded in Limitations.
- **Cannot claim the model predicts measured leaf hydraulic conductance.** Scoffoni et al. (2017, *Plant Physiology*) shows why it cannot — but this cuts both ways: it explains the failure, it does not convert it into a success.
- **Cannot claim −2.0 MPa is a general cavitation threshold.** See Counterevidence.
- **Cannot claim early warning.** Nothing found establishes that a connectivity metric detects impending hydraulic dysfunction earlier than existing physiological measures. "Early warning" language should be dropped or converted to "pre-symptomatic" in the specific vulnerability-segmentation sense of Charrier et al. (2016).
- **Cannot claim the haustorium deletes vein junctions.** The paper already knows this. Because the sink model and the percolation model are decoupled, the honest structure is to present them as two independent lenses on the same network, and the coupled-sink surface (no collapse at calibrated K_h; threshold appearing only at 2× K_h in the least reticulate network and 3× in all) as the quantification of *how far apart* they are. That is a result, not a failure.

### Defensible hedged sentence forms

> "We treat the giant connected component of the venation graph as a structural proxy for the retention of a continuous water-supply pathway, following the usage of Mander and Williams (2024); we do not equate its loss with cavitation or with percentage loss of conductivity."

> "Empirical work has established that severance of the water-supply path within leaf veins causes immediate and irreversible local tissue damage (Brodribb et al., 2021); our analysis quantifies the structural conditions under which such severance becomes widespread, not the water potentials at which it is initiated."

> "Random node removal is used here as a null structural scenario. Direct observation shows that embolism in leaves is spatially clustered and ordered by vein size rather than random (Brodribb et al., 2016; Pritzkow et al., 2022; Lu et al., 2025), so the random threshold should be read as an upper bound on the removal fraction tolerated, and the degree-targeted threshold as the closer, though still imperfect, structural surrogate for the observed large-vein-first failure sequence."

> "Because 86–100% of the decline in whole-leaf hydraulic conductance during dehydration arises outside the xylem (Scoffoni et al., 2017), a xylem-only network model is not expected to predict measured K_leaf; the weak rank correlation obtained (ρ = 0.187, p = 0.073) is consistent with that partitioning. Solver fidelity is instead evidenced by exact reproduction of the source dataset's Hagen–Poiseuille resistances across 119 leaves and 5.67 million vein segments."

> "The percolation threshold is a structural quantity and the haustorial sink a flux quantity; our results indicate that at physiologically calibrated sink strengths these two descriptions of parasite stress do not converge, and we therefore report them as complementary rather than nested lenses."

> "The correspondence between mean degree and the collapse threshold reported here is a statement about structural robustness to element loss. Whether higher vascular connectivity increases or decreases resistance to *embolism propagation* specifically remains contested (Loepfe et al., 2007; Mrad et al., 2021), and we make no claim on that question."

---

## COUNTEREVIDENCE AND LIMITS

---

**COUNTEREVIDENCE 1 — Embolism is spatially clustered, not random. Random-removal percolation does not represent it.**

**Citation** | Pritzkow, C., Brown, M. J. M., Carins-Murphy, M. R., Bourbia, I., Mitchell, P. J., Brodersen, C., Choat, B., & Brodribb, T. J. (2022). Conduit position and connectivity affect the likelihood of xylem embolism during natural drought in evergreen woodland species. *Annals of Botany, 130*(3), 431–444.
**DOI** | 10.1093/aob/mcac053 | **Access** | ABSTRACT ONLY | **Study type** | X-ray CT under natural field drought | **System** | Branch xylem, three evergreen woodland trees
**Main finding** | Embolism showed "circumferential clustering of high and low embolism density," spreading among same-aged conduits and accumulating in older xylem. Probability of embolism was independent of conduit diameter but dependent on conduit position. Propagation is described as air spreading from embolised into neighbouring conduits in a circumferential pattern.
**What it damages** | The random-removal assumption underlying the primary p_c estimates (empirical median 0.200; synthetic 0.271). Real failure is spatially autocorrelated and directional; random removal disperses damage uniformly and therefore systematically *overestimates* the removed fraction a network can absorb — clustered removal fragments a network at lower fractions than random removal at equal <k>.
**Reinforced by** | **Lu et al. (2025)**, which finds that adding an ICAR spatial-dependence prior over the venation neighbourhood structure reduced predictive error in 47/53 leaf samples — a direct, leaf-specific measurement that embolism events are not independent. And by **Brodribb et al. (2016, PNAS)**: nucleation "always occurred in the largest vein," with susceptibility scaling with vein size, in every network examined.
**How to handle** | Do not bury this. Name random removal as a null scenario in the Methods. Report the degree-targeted result as the physiologically motivated companion. State explicitly that a spatially clustered or radius-ranked removal scenario would be expected to yield lower thresholds than either, and that this is computable from the Matos radius data — flag it as the priority extension. Do not claim the current thresholds bracket the true value; they bracket two idealised orders, both of which the literature says are wrong in different ways.
**Strength of the objection** | Severe. This is the most likely reviewer objection and the paper cannot survive without addressing it head-on.

---

**COUNTEREVIDENCE 2 — Connectivity-mediated spread is a late-stage phenomenon, which undercuts "pre-symptomatic."**

**Citation** | Avila, R. T., Guan, X., Kane, C. N., Cardoso, A. A., Batz, T. A., DaMatta, F. M., Jansen, S., & McAdam, S. A. M. (2022). Xylem embolism spread is largely prevented by interconduit pit membranes until the majority of conduits are gas-filled. *Plant, Cell & Environment, 45*(4), 1204–1215.
**DOI** | 10.1111/pce.14253 | **Access** | ABSTRACT ONLY | **Study type** | Optical vulnerability method through dehydration–rehydration–dehydration cycles | **System** | Diverse angiosperms and conifers
**Main finding** | Individual conduits possess conserved, conduit-specific embolism thresholds set by pit membranes. Connectivity effects — "gas movement, local pressure differences and connectivity between conduits" — only "increasingly contribute to embolism spread" **as the percentage of embolised conduits increases**. When little pre-existing embolism is present, spread is largely prevented.
**Reinforced by** | **Johnson et al. (2020)**: >80% of cavitation events in three angiosperm stems were discrete, temporally separated single-vessel events; in low-connectivity xylem, cascading spread was uncommon. And **Scoffoni et al. (2017, *Plant Physiology*)**: only 5–8.5% of midrib conduits embolised at turgor loss point, with **no emboli in minor veins at all** above turgor loss.
**What it damages** | The paper's title claims *pre-symptomatic* collapse. This body of work says that in the pre-symptomatic regime — before substantial embolism has accumulated — connectivity is precisely the mechanism that is *not yet operating*. Network-mediated failure switches on late. A connectivity-based criterion may therefore be a poor early-warning indicator by construction.
**How to handle** | This is the strongest single argument against the framing, and the honest response is to change what "pre-symptomatic" means in the paper. It should denote *visually and physiologically asymptomatic at the whole-plant level* (justified by vulnerability segmentation — Charrier et al., 2016, where leaves and petioles are sacrificed at −1.0 MPa while stems hold to −1.7 MPa), **not** "detected earlier than embolism." Consider retitling away from any implication of early detection. Note that the paper's own null embolism result (0 vessels across all 31 gradients) is fully consistent with Avila et al. and Scoffoni et al. — minor-vein xylem is hard to embolise, so structural collapse and embolism genuinely should not co-occur at modest gradients. That consistency is worth stating; it converts an awkward null into corroboration.
**Strength of the objection** | Severe, and it targets the title.

---

**COUNTEREVIDENCE 3 — Leaf hydraulic decline is governed by outside-xylem tissue, not by the xylem network.**

**Citation** | Scoffoni, C., Albuquerque, C., Brodersen, C. R., Townes, S. V., John, G. P., Bartlett, M. K., Buckley, T. N., McElrone, A. J., & Sack, L. (2017). Outside-xylem vulnerability, not xylem embolism, controls leaf hydraulic decline during dehydration. *Plant Physiology, 173*(2), 1197–1210.
**DOI** | 10.1104/pp.16.01643 | **Access** | FULL TEXT READ
**Main finding** | K_ox decline accounted for 86–100% of K_leaf decline at turgor loss point, 95–100% at P50,Kleaf, 75–100% at P88,Kleaf. P50,Kx was 1.6 MPa more negative than P50,Kleaf. P50,Kox alone explained 81% of cross-species variation in P50,Kleaf.
**What it damages** | This is simultaneously the paper's best defence (Tier 1) and its most serious limitation. If the physiologically decisive resistance sits in the bundle sheath and mesophyll, then the *entire* xylem-network object the paper analyses — however elegantly solved — may be a secondary contributor to the leaf's actual hydraulic behaviour. The failed K_leaf validation is not merely explained by this; it is *predicted* by it, and a hostile reviewer will use it to argue the whole modelling target is misidentified.
**Partially rebutted by** | **Brodribb et al. (2016, *New Phytologist* 209:1403–1409)**, which reports "very strong agreement between the dynamics of embolism formation during desiccation and decline of leaf hydraulic conductance" across four angiosperms, connecting leaf-network embolism directly to K_leaf decline. The field has not resolved this.
**How to handle** | Present it explicitly as an open controversy with both sides cited, and be candid that the paper's object is the *xylem network*, which is one component of leaf hydraulics whose relative weight is disputed. Do not cite Scoffoni et al. as though it settles the matter in the paper's favour — it does not; it explains one result while indicting the broader premise. This belongs in Limitations as well as in Results-interpretation.
**Strength of the objection** | Severe.

---

**COUNTEREVIDENCE 4 — The −2.0 MPa cavitation threshold is not a general value.**

**Sources** | Charrier et al. (2016), *Plant Physiology* 172:1657–1668, DOI 10.1104/pp.16.01079 — ABSTRACT ONLY; Urli et al. (2013), *Tree Physiology* 33:672–683, DOI 10.1093/treephys/tpt030 — ABSTRACT ONLY; Choat et al. (2012), *Nature* 491:752–755, DOI 10.1038/nature11688 — ABSTRACT ONLY; Isasa et al. (2023), *New Phytologist* 238:283–296, DOI 10.1111/nph.18731 — ABSTRACT ONLY.
**Main finding** | Measured P50 spans at minimum from **−1.0 MPa** (*V. vinifera* petiole, Charrier et al. 2016, microCT on intact plants) to values several times more negative; minimum recoverable water potentials range **−3.4 to −6.0 MPa** across five angiosperms (Urli et al. 2013), and the irreversible-damage embolism threshold is near **88% PLC, not 50%**. Choat et al. (2012) assembled 226 species across 81 sites precisely because no single threshold generalises. Isasa et al. (2023) further show that even the anatomical predictor of P50 behaves differently at interspecific versus intraspecific scale.
**What it damages** | The model's −2.0 MPa cavitation threshold, and therefore the headline sink result: minimum host leaf water potential −1.02 MPa, margin 0.98 MPa, 0 vessels embolised; and the sweep result, 0 embolised across all 31 gradients with a minimum margin of 0.678 MPa. Both of these null results are threshold-dependent. Against a −1.0 MPa petiole-type threshold, a modelled minimum of −1.02 MPa **crosses the threshold**, and the entire "0 embolised" conclusion inverts. The minimum margin of 0.678 MPa is smaller than the between-species spread in P50, so the null result is not robust to threshold choice.
**Also note** | The dataset is 122 species from a botanical garden, so a single threshold cannot be species-appropriate for any of them.
**How to handle** | Non-negotiable: run and report a threshold sensitivity analysis across a plausible P50 range (roughly −1.0 to −4.0 MPa), and report the threshold value at which the embolism count becomes non-zero. Presenting "0 embolised" without this will not survive review. State explicitly that −2.0 MPa is an illustrative modelling parameter, not a measured or species-matched value — the same hedge already applied to the "illustrative ~1.5 MPa" gradient. If the sensitivity analysis shows the null result inverting near −1.0 MPa, report that: it is a more interesting and more honest finding than the null.
**Strength of the objection** | Severe and immediately actionable.

---

**COUNTEREVIDENCE 5 — A static, unregulated network cannot represent a stomatally regulated dynamic system.**

**Sources** | Martin-StPaul, Delzon & Cochard (2017), *Ecology Letters* 20:1437–1447, DOI 10.1111/ele.12851 — ABSTRACT ONLY; Brodribb et al. (2016), *New Phytologist* 209:1403–1409, DOI 10.1111/nph.13846 — ABSTRACT ONLY.
**Main finding** | Stomatal closure and embolism onset coincide in only a few species; safety margins widen with embolism resistance; there exists "an absolute limit by which stomata closure must occur to avoid rapid death." Brodribb et al. (2016) find embolism occurs *after* stomatal closure under extreme stress.
**What it damages** | The model has no stomatal regulation and no transpiration feedback. In a real host under haustorial water stress, stomatal closure would intervene before the modelled gradients are reached, altering both the flow diversion (0.2% at 0 MPa rising to 35.1% at 3.0 MPa) and the water potentials attained. The high-gradient end of the 0–3.0 MPa sweep describes a physiologically unreachable state for most regulating plants.
**Partial defence** | The refilling half of the dynamic objection is well answered: **Charrier et al. (2016)** found no refilling while xylem pressure remained negative (ΔPLC = 0.02 ± 0.01%), and **Avila et al. (2022)** observed no refilling upon rehydration. So the *irreversibility* assumption implicit in a static removal model is defensible; the *regulation* assumption is not.
**How to handle** | Limitations, explicitly. Note that the upper end of the gradient sweep is a bounding exercise, not a predicted physiological state. Claim the refilling defence — it is genuinely available and cheap.
**Strength of the objection** | Moderate–Serious.

---

**COUNTEREVIDENCE 6 — Vulnerability is anatomical (conduit dimensions), and the traces omit the site where failure begins.**

**Sources** | Scoffoni et al. (2017), *New Phytologist* 213:1076–1092, DOI 10.1111/nph.14256 — ABSTRACT ONLY + indexed excerpts; Isasa et al. (2023), *New Phytologist* 238:283–296, DOI 10.1111/nph.18731 — ABSTRACT ONLY.
**Main finding** | Leaf Kx decline "was driven by embolism initiating in petioles and midribs across all species," with vulnerability strongly correlated to petiole and midrib conduit dimensions (indexed: r² = 0.72 for P88,Kx vs midrib conduit size; r² = 0.82–0.88 for conduit size vs the potential at 50% embolised conduits under microCT). Isasa et al. confirm a robust interspecific P50–vessel-diameter relationship across 20 species after controlling for pit membrane thickness.
**What it damages** | Two things. (1) It offers a complete competing explanation of leaf hydraulic vulnerability that requires no network topology whatsoever. (2) More concretely: **failure initiates in the petiole, and the Matos traces are crop windows containing no petioles.** The paper's networks structurally exclude the anatomical location where leaf xylem failure is empirically observed to start.
**Counter-tension worth noting** | Pritzkow et al. (2022) found embolism probability *independent* of conduit diameter and dependent on position instead — so the anatomical account is itself contested, which slightly softens this objection but does not remove it.
**How to handle** | State the petiole omission plainly in Limitations alongside the existing crop-window caveat; it is a sharper and more specific version of that caveat than "not whole blades." Frame the paper's contribution as complementary to the anatomical account rather than competing with it, and note that the model already carries conduit radii through the Hagen–Poiseuille conductances even though it does not use them to set failure probability — which is exactly the extension a reviewer will suggest.
**Strength of the objection** | Serious.

---

**COUNTEREVIDENCE 7 — The connectivity literature disagrees with itself about the sign.**

**Sources** | Loepfe et al. (2007), *J. Theor. Biol.* 247:788–803, DOI 10.1016/j.jtbi.2007.03.036; Mrad et al. (2021), *New Phytologist* 231:996–1007, DOI 10.1111/nph.17429; Johnson et al. (2020), *Plant Physiology* 184:212–222, DOI 10.1104/pp.20.00464 — all ABSTRACT ONLY.
**The conflict** | Loepfe et al.: "vulnerability to embolism **increase[s]** with the connectivity of the xylem network." Mrad et al.: "increases in connectivity **improve** resistance to embolism spread without negatively affecting hydraulic conductivity." Johnson et al. supply an empirical data point on Loepfe's side — *Acacia mearnsii*, the species with the highest vessel connectivity, showed the most multi-vessel cavitation events.
**What it damages** | Any attempt to translate the reticulation-enhancement result (<k> → P90 of 2.811 raising median p_c 0.201 → 0.215) into a claim about embolism resistance. Two of three relevant sources point the opposite way from the paper's structural finding.
**How to handle** | This is manageable and actually valuable if stated precisely. The paper's result concerns **structural robustness to element loss**, where the literature is unanimous in the paper's favour (Katifori et al. 2010; Sack et al. 2008; Mander & Williams 2024; Brodribb et al. 2016 PNAS). The contested question is **embolism propagation**, on which the paper should explicitly decline to comment. Making that distinction cleanly is one of the paper's better opportunities to demonstrate command of the literature. Do not let "reticulation as a host-resistance trait" (the alternative title) slide into implying embolism resistance.
**Strength of the objection** | Moderate, but fatal to imprecise phrasing — and the alternative title is currently imprecise in exactly this way.

---

## BRIDGE VALUE

Sources linking two or more of the paper's components (venation topology / percolation formalism / hydraulic physiology / damage tolerance):

- **Mrad et al. (2021), 10.1111/nph.17429** — the only source found joining **percolation theory + graph theory + plant xylem + connectivity + hydraulic function** in one peer-reviewed plant-science paper. It is the paper's methodological passport. Cite in Introduction, Methods justification, and Discussion.

- **Mander & Williams (2024), 10.1098/rsos.240086** — joins **percolation/connected-component robustness + real traced leaf venation + reticulation vs branching + evolutionary interpretation**. Closest existing analogue to the whole pipeline, independently reproduces the reticulation result, and its stated limitation (no fluid-flow model) is the paper's novelty hook.

- **Sack et al. (2008), 10.1073/pnas.0709333105** — joins **venation topology + element removal + measured K_leaf, g_s and photosynthesis**. The only source that closes the loop from topological damage to measured physiological consequence, and the only empirical justification for the targeted-vs-random contrast.

- **Brodribb et al. (2016), 10.1073/pnas.1522569113** — joins **vein network topology + observed embolism dynamics + failure mode (catastrophic vs staged) + fern/angiosperm reticulation contrast**. Simultaneously the best support for the reticulation claim and the best constraint on the random-removal assumption.

- **Lu et al. (2025), 10.1093/aobpla/plaf020** — joins **leaf vein network connectivity + embolism ordering + spatial statistics**. The most recent work on the paper's exact object; supplies both the strongest non-randomness constraint and the concrete recipe for the next iteration (thickness-ranked removal).

- **Brodribb et al. (2021), 10.1111/nph.17577** — joins **vein network failure + local supply severance + tissue death**. Bridges structure to mortality without passing through bulk conductivity, which is precisely the route the paper needs.

- **Scoffoni et al. (2017 *Plant Physiology*), 10.1104/pp.16.01643** — joins **xylem/outside-xylem partitioning + microCT embolism + K_leaf vulnerability**. Simultaneously defends the failed validation and constrains the model's scope; the single most double-edged source in the set.

- **Katifori et al. (2010), 10.1103/PhysRevLett.104.048704** — joins **network optimisation theory + damage tolerance + loops + leaf venation**. Supplies the theoretical rationale for why loop fraction (median 0.776) should predict p_c at all.

- **Charrier et al. (2016), 10.1104/pp.16.01079** — joins **vulnerability segmentation + measured organ-level P50 + refilling**. Provides the physiological justification for a leaf-level pre-symptomatic framing *and* the counterexample that breaks the −2.0 MPa threshold.

---

## WHAT I COULD NOT FIND

1. **No study that computes a percolation threshold (p_c) on real leaf venation networks and validates it against measured hydraulic failure.** Mander & Williams (2024) do connected-component robustness on real leaves but compute no threshold, use random removal only, and explicitly build no flow model. Mrad et al. (2021) use percolation but on stem xylem conduit networks. **This gap is the paper's genuine novelty claim, and it is real** — but the claim must be phrased as *first to couple a percolation analysis of traced venation to an explicit Kirchhoff flow solution*, not *first to apply percolation to leaves*.

2. **No published mapping between a connectivity metric (GCC fraction) and a hydraulic metric (PLC, K_leaf, P50).** Nothing in this search allows conversion in either direction. The paper must not imply one exists.

3. **No leaf-specific analogue of "runaway cavitation."** The Tyree & Sperry (1989) runaway concept is stem/whole-plant. I found no source establishing a self-reinforcing connectivity cascade *within leaf venation* in the pre-symptomatic regime — and Avila et al. (2022) argues against one.

4. **No evidence that a connectivity metric provides earlier warning than existing physiological measures.** No source found supports "early warning." Recommend the term be removed from the paper.

5. **Nothing on holoparasitic haustoria altering host leaf venation network topology, connectivity, or percolation properties.** This appears genuinely unstudied; whether it is covered by another agent's domain, I found no hydraulic-network-level treatment.

6. **No source establishing whether percolation properties of a crop-window subgraph are representative of the whole blade.** Sampling-window effects on graph metrics (<k>, loop fraction, box-counting D, and hence p_c) in leaf venation appear unaddressed. Given the traces are 100/120 crop windows with no petioles, this is an unquantified and currently undefendable source of bias. Worth a synthetic sensitivity test — sub-window a synthetic full network and compare p_c — since the paper already has the machinery.

7. **Could not obtain full text of** Scoffoni et al. 2017 *New Phytologist* (Wiley 403; UCLA mirror 500), Mrad et al. 2021 (Wiley 403), Mrad et al. 2018 (Wiley 403), Brodribb et al. 2016 PNAS (403), Loepfe et al. 2007 (Elsevier), Choat et al. 2012 (Nature). All are marked ABSTRACT ONLY above, verified through the Europe PMC core API. **The r² values attributed to Scoffoni et al. 2017 *New Phytologist* came from indexed article text rather than the PDF and must be checked against the original before being cited.** The **Adams et al. 2017 page range was not verified** and must be confirmed.

8. **Species-matched P50 values for the 122 Matos species were not sought and almost certainly do not exist as a set.** This reinforces recommendation 4 in Counterevidence: report a threshold sensitivity sweep rather than a single −2.0 MPa value.
agentId: ad316f7460cfd072f (use SendMessage with to: 'ad316f7460cfd072f', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 109178
tool_uses: 50
duration_ms: 721954</usage>