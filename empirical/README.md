# Empirical Leaf Data — Validation Inputs

Real-leaf images and measurements that validate the model against actual plants.
Two questions this data answers:

1. **Is our fractal dimension realistic?** Compare box-counting **D** measured on
   real leaf venation against the model's **D = 1.432 ± 0.007** (one-sample t-test).
2. **Does denser venation resist collapse longer?** Measuring leaves across a
   venation-density range *tests* the model's core prediction (higher D → higher p_c).

> **Every image needs a scale bar / ruler in frame.** Without a known scale you
> cannot compute physical D or vessel radii. This is the most common mistake.

---

## Folder layout — where to put what

```
empirical/
  venation_topdown/      <- TOP-DOWN whole-leaf images (cleared / backlit / scanned)
    <species>/              one subfolder per species, e.g. tomato/, maize/
  cross_sections/        <- TRANSVERSE slices under a microscope (vessel anatomy)
    <species>/
  measurements/          <- the numbers you read off the images
    venation_metrics.csv    (box-counting D, vein density per leaf)
    vessel_radii.csv        (vessel diameters from cross-sections)
  metadata.csv           <- one row per image (the master log)
```

Make a subfolder per species inside `venation_topdown/` and `cross_sections/`.

---

## The two image types

| Type | Goes in | Shows | Validates |
|---|---|---|---|
| **Top-down venation** | `venation_topdown/` | the vein *network* from above | fractal **D**, topology (**priority**) |
| **Transverse cross-section** | `cross_sections/` | xylem *vessel diameters* | Murray's-law radii, hydraulics |

**Top-down** is the priority — it is what validates D. A backlit phone photo or a
flatbed-scanner image of a fresh or pressed leaf is enough; a *cleared* leaf
(soaked to translucency) is best. **Cross-sections** are secondary: thin hand
sections viewed under a microscope, used to measure vessel calibers.

### Which organ to cross-section
Rank: **stem first, leaf second, skip the fruit, root only as future work.**

| Organ | Get it? | Why |
|---|---|---|
| **Stem** | **yes (primary)** | largest xylem vessels = the model's backbone (low-generation, big radius); also what *Cuscuta* taps |
| **Leaf** (petiole + midrib) | **yes (secondary)** | small terminal-vein radii = the model's tips; needed *with* the stem to test Murray's law across scales |
| **Root** | optional / future | model treats the root as a single source node, not a network; relevant only if you extend to a root system (Orobanche/Striga context) |
| **Fruit** | **no** | a sink organ, not part of the modelled stem→leaf transport network — no parameter maps to it |

**The one rule:** section *at or near a branch point* so a parent vessel and its
two daughters appear together — that is the only way to measure the Murray's-law
exponent (the model assumes 3.0). A slice through a plain stem gives scattered
vessels you cannot pair.

---

## Which plants (≈ 5 species)

**Set A — real hosts of the studied parasites (biological relevance):**
- **Tomato** (*Solanum lycopersicum*) — host of *both* Cuscuta and Orobanche.
- **A legume** (mungbean / cowpea / alfalfa) — Cuscuta & Orobanche host.
- **Maize / corn** (*Zea mays*) — *Striga* host (also the low-D endpoint below).

**Set B — venation-density gradient (tests D → robustness):**
- **Low D** — grass/monocot: maize or **rice** (near-parallel veins, few loops).
- **High D** — densely reticulate dicot: **mango, guava, or hibiscus** (many loops).

Use what is locally available; the requirement is (a) at least one real host of
your parasites and (b) a spread from low to high venation density.

---

## Sampling design (for real standard errors)

- **≥ 5 individual plants per species** (different plants, not 5 leaves off one).
- **3 leaves per plant**, comparable age and position on the plant.
- ≈ 15 leaves/species × 5 species ≈ **75 top-down images**.
- This yields a genuine mean ± SE per species to t-test against the model's D.

---

## File naming convention

```
<species>_<plantID>_<leafID>_<view>.<ext>
```
Examples:
- `tomato_p01_l1_topdown.jpg`  (top-down: use the leaf id)
- `tomato_p01_stem_xsec.jpg`   (cross-section: use the **organ**, not a leaf id)
- `tomato_p01_leafvein_xsec.jpg`
- `maize_p03_l2_topdown.png`

`p01` = plant 1, `l1` = leaf 1. For top-down use `<leafID>`; for cross-sections use
the **organ** (`stem` / `leafvein`). `view` = `topdown` or `xsec`. Log every file in
`metadata.csv` with its scale (pixels per millimetre).

---

## How to photograph
- **Scale:** lay a ruler in the frame, or note the scanner DPI. Record px/mm.
- **Top-down:** backlight the leaf (window, lightbox, or phone torch behind it);
  flatten it; fill the frame; avoid glare. A flatbed scanner at ≥ 600 DPI is ideal.
- **Cross-section:** thinnest possible hand section, wet mount, photograph through
  the microscope eyepiece with a stage micrometer (or any object of known size).

---

## What to measure (fill the CSV templates)
- `venation_metrics.csv` — **box-counting D** (same windowed method as the code,
  so the comparison is apples-to-apples) plus **vein density** (total vein length ÷
  leaf area). Report *both*: D is a coarse descriptor, vein density is the robust
  topological metric the modern literature prefers (see `VALIDATION.md §3`).
- `vessel_radii.csv` — for branch points in the cross-sections, the parent vessel
  radius and its two daughter radii, to check the real **Murray's-law exponent**
  (the model assumes 3.0).

---

## Honest note (state this to the panel)
Box-counting D on a real leaf carries the *same* estimation caveat as the model's
(veins are not perfectly self-similar), so we report it as a distribution with a
confidence interval and pair it with vein density rather than leaning on D alone.
