# Empirical-Phase Data Sources — VERIFIED

> **Status: verified 2026-07-23 by direct fetch of each source.** Every URL below was resolved and
> its contents confirmed against the page itself, not from an agent summary. This supersedes the
> priority items in `RESEARCH_LEADS_UNVERIFIED.md`; that file remains as the fuller (unchecked) pool.

The one decision this research was meant to settle — *photograph our own leaves, or download real ones?*
— now has an answer: **a single open deposit supplies real venation images AND vessel anatomy for 122
species, calibrated, no blades.** Details below.

---

## ★ THE FORK DECIDER — Matos et al. UC Berkeley deposit (Dryad)

**Verified live.** `https://datadryad.org/dataset/doi:10.5061/dryad.1g1jwsv36`

- **Title:** *Leaf architecture and functional traits for 122 species at the University of California
  at Berkeley botanical garden.* Matos, Blonder (corresponding), + 28 co-authors.
- **Associated paper (already in your reference list):** Matos et al. (2024), *New Phytologist*,
  244(2), 407–425. `10.1111/nph.20037`.
- **Licence:** Open Data Commons Attribution (ODC-BY) — free to copy, modify, build upon, with
  attribution. No login barrier shown.
- **Size:** 44.44 GB total. Venation images 29.37 GB; anatomy photos 11.3 GB; LeafVeinCNN models 4.78 GB.

**Why this settles the fork — it answers three of your four needs at once:**

| Your need | What the deposit gives you | Calibrated? |
|---|---|---|
| Real venation images (Step 1) | `venation_form/images/` — up to 9 PNG per species, 122 species | **Yes** — `image_resolution` column, **mm per pixel** |
| Pre-extracted graph (Step 1) | CSVs with `node_Degree`, areole `Area` (mm²), vein width, branch angles | already reduced to graph descriptors |
| Vessel radii (Step 2) | anatomy cross-section **TIFFs**, 828 files / 122 folders | **Yes** — printed 10 µm / 100 µm / 1 mm scale bars |

If your five target species (tomato, a legume, corn, mango, hibiscus) — or close relatives — are among
the 122, you download, measure with the *same* `fractal.box_counting_dimension()` you already run on the
synthetic networks, and **your risk assessment's entire sharps/reagent section becomes moot.** The
priority venation measurement needs nothing more dangerous than a file download.

**Next action:** download the species manifest CSV first (tiny) and check which of your five are present
before pulling 44 GB.

---

## ★ Software to turn any leaf photo into a graph — LeafVeinCNN

**Verified live.** `https://zenodo.org/records/8272938`

- **What:** Leaf Vein Network CNN Analysis Software v2.14 — Fricker, Blonder, Xu (Oxford / UC Berkeley).
- **No-MATLAB route confirmed:** `LeafVeinCNN_v2.14.exe` (1.1 GB) runs standalone on Windows and
  auto-downloads the MATLAB Runtime. The `.mlappinstall` route needs MATLAB 2020b + three toolboxes;
  **the .exe avoids all of it.** Manual PDF (76.5 MB) included.
- **Hard resolution requirement:** trained CNN models expect **1.68 µm/pixel.** A 1200-dpi flatbed scan
  is ~21 µm/pixel — an order of magnitude coarser — so the pretrained models may not transfer to your
  own scanner images without retraining or rescaling. *This is the catch that makes the Matos deposit
  the better path: its images are already at the resolution the tool was built for.*
- **Licence:** CC BY 4.0, no login to download.
- **Method paper:** Xu, H., Blonder, B., Jodra, M., Malhi, Y., & Fricker, M. D. (2020). Automated and
  accurate segmentation of leaf venation networks via deep learning. *New Phytologist*, 229, 631–648.
  `10.1111/nph.16923`.

---

## ★ CITATION FIX — your Vishnu et al. reference is wrong on two counts

**Confirmed against Crossref** (`10.1016/j.flora.2023.152300`, ISSN 0367-2530 = *Flora*):

Your reference list currently reads *Vishnu, M., Rajan, S. C., & Nair, J. R.* in *Chaos, Solitons &
Fractals* with "[volume and article number to be confirmed]". The verified record is:

> Muraleedharan, V., Rajan, S. C., & Jaishanker, R. (2023). Determining the limits of traditional
> box-counting fractal analysis in leaf complexity studies. *Flora, 304,* 152300.
> https://doi.org/10.1016/j.flora.2023.152300

Two errors to fix: (1) **wrong journal** — it is *Flora*, not *Chaos, Solitons & Fractals* (the PII you
recorded, `S0367253023000907`, carries Flora's ISSN prefix). (2) **third author** is *Jaishanker, R.*,
not *Nair, J. R.* Also verify the first author's given/family split against the publisher page before
final submission — Crossref lists the first author as "Vishnu Muraleedharan", so *Muraleedharan, V.* is
likely correct rather than *Vishnu, M.*, but confirm it. Your own verification note already flagged this
entry as unconfirmed; it was right to.

---

## ★ NOVELTY CLAIM — soften it, but it survives

**Confirmed:** Mander, L., & Williams, H. T. P. (2024). The robustness of some Carboniferous fossil leaf
venation networks to simulated damage. *Royal Society Open Science, 11*(5), 240086.
`10.1098/rsos.240086`.

This study **does** run a connectivity-threshold analysis on real extracted leaf venation networks (9
taxa — mostly Carboniferous fossils plus extant *Betula alba*), removing network elements and measuring
what stays connected to the structural vein. **But** verified directly from the paper: it reports **no
formal p_c and no critical exponents**, implements **no hydraulic model** ("we do not simulate any
processes directly"), and **explicitly names hydraulic flow modelling as future work** ("a model of
fluid flow through the leaf would be needed").

**What this means for your defense:**
- ✗ "No one has run a percolation/connectivity analysis on a real leaf network" — **too strong, drop it.**
- ✓ "No one has coupled a **hydraulic resistor model** to a **percolation threshold** on a real leaf
  network, and the one connectivity study on real leaves names exactly that hydraulic step as the open
  gap" — **verified true, and now you can cite the paper that leaves you the opening.**

Use the hedged form. It is stronger *and* it is bulletproof.

---

## ★ HAUSTORIAL-FLUX GAP (your K_h justification) — holds

The most comprehensive recent parasite–host hydraulics dataset located — Zhang et al. (2025), *New
Phytologist*, 245(2), 607–624, `10.1111/nph.20257`, 118 mistletoe–host species pairs — characterises
xylem anatomy on **both sides** of the parasitic interface yet reports **no haustorial conductance and
no haustorial volumetric flux.** Its variable list is stem/branch xylem anatomy for parasite and host
*separately*; there is no interface, haustorium, or flux variable.

This is **consistent with** your claim that no published haustorial flux value exists, so sweeping K_h
rather than fitting it remains defensible. Honest caveat: absence in one dataset is supporting, not
conclusive, and the full text is paywalled — so state it as "we could find no study that reports…", never
"no study reports…".

**Bonus finding that affects your model, not just your citations:** Zhang et al. find the parasite's own
xylem is the *narrower, higher-resistance* element, not a wide-bore low-resistance conduit. That supports
your choice to model the haustorium as a **potential/tension boundary condition** (ψ_parasite = −3 MPa)
rather than a high-conductance edge — the sink is driven by the parasite's aggressive water potential,
which is exactly what your `config.PSI_PARASITE` does.

---

## Secondary sources (verified in the unchecked pool, not re-fetched here)

- **Maize vessel radii without cutting:** Hwang, B. G., Ryu, J., & Lee, S. J. (2016). *Frontiers in
  Plant Science, 7,* 941. `10.3389/fpls.2016.00941`. Protoxylem 10.9 µm, metaxylem 23.6 µm (radii ~5.5
  and ~11.8 µm). Note: a maize bundle = 1 protoxylem + 2 metaxylem, so one leaf-vein edge is three
  parallel conduits, not one tube.
- **Chemical-free imaging endorsed:** the Blonder-lab protocol (PMC12038745, 2025) explicitly endorses a
  trans-illuminated flatbed scanner as a valid venation-imaging route — but the Scoffoni & Sack protocol
  warns ~1200 dpi resolves *major* veins only, not minor veins/areoles. Reinforces: use the pre-made
  high-res Matos images rather than your own scans if you need the loop structure.
- **XFT / InsideWood / TRY:** all live, but none cleanly gives continuous vessel-lumen diameters for your
  five herbaceous/dicot species without registration or IAWA-category translation. The Matos anatomy
  TIFFs are the better vessel-radius source.
