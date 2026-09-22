# Assignment 9 — Research-page benchmark and locked design

This note records the research-page design decision for the FlyRank ML Internship capstone before implementation.

## Benchmark sources reviewed

### Distill
- Guide: https://distill.pub/guide/
- Interactive-article design study: https://distill.pub/2020/communicating-with-interactive-articles/
- Useful pattern: research-first long-form web reading, restrained typography, narrow readable measure, figures integrated into the narrative, and explanations designed to reduce cognitive load.
- Decision for this project: adopt the reading experience and figure-first storytelling, but avoid unnecessary interactive components.

### Nature / Nature Methods
- Formatting and figure guidance:
  - https://www.nature.com/nature/for-authors/formatting-guide
  - https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
- Useful pattern: methods must be sufficient for interpretation and replication; figures should be simple, labelled, self-contained and accessible; unnecessary visual complexity should be removed.
- Decision for this project: use publication-style chart hygiene, explicit metric definitions, clear captions, and a concise but reproducible Methods section.

### Nerfies research project page
- Project page: https://nerfies.github.io/
- Source: https://github.com/nerfies/nerfies.github.io
- Useful pattern: title/author hero, immediate artifact buttons, a one-line result statement, prominent visual evidence, then abstract and deeper sections.
- Decision for this project: use a compact hero with direct Repo / Notebook / Data-credit links and surface the key empirical result before the long-form paper.

### Papers with Code
- https://paperswithcode.com/
- Useful pattern: the research claim is connected directly to code, datasets and evaluation tables.
- Decision for this project: make reproducibility a first-class section and link directly to the exact notebooks that generated the paper's results.

### Web usability and accessibility
- Nielsen Norman Group: https://www.nngroup.com/articles/how-users-read-on-the-web/
- W3C WCAG use of colour: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color
- Useful pattern: web readers scan; meaningful headings, short paragraphs and front-loaded conclusions matter. Colour must not be the only carrier of meaning.
- Decision for this project: optimize for a fast 10-minute read and mobile use; charts will use labels/markers/text as well as colour.

## Locked format

The deployed artifact will be a **single responsive static research page** in `docs/index.html`, served by GitHub Pages from the `main` branch.

This is intentionally a hybrid:
- **Distill-style** readable research narrative,
- **Nerfies-style** project-page hero and artifact links,
- **Nature-style** methodological and figure discipline,
- **Papers-with-Code-style** reproducibility links.

It will not imitate a journal PDF and will not add interactive widgets unless they materially improve understanding.

## Locked information architecture

The public page will preserve the assignment's nine required sections, in this order:

1. Title + Abstract
2. Introduction / Problem
3. Data
4. Methodology
5. Results
6. Limitations & honest framing
7. Ranked recommendations
8. Reproducibility
9. Acknowledgments & data credit

The visual hero may appear above Section 1, but it will not replace any required section.

## Hero design

Above the paper body:
- research-question-led title rather than a generic project name,
- author name,
- short descriptor: FlyRank ML Internship capstone,
- compact artifact buttons/links,
- one-sentence empirical takeaway,
- optional small metadata row for dataset scale / decision point / validation type.

No unsupported performance claim will appear in the hero.

## Reading layout

- One-column reading layout with a constrained text width.
- Short paragraphs and meaningful headings.
- Sticky navigation only if it remains simple on mobile; otherwise a compact table of contents.
- Key metrics shown in small summary cards near Results, but the full comparison remains a normal table.
- Tables must scroll horizontally on narrow screens instead of breaking the layout.
- No decorative animation, autoplay media, parallax, or dashboard-style clutter.

## Figure policy

Target: **three strong figures**, not a gallery.

Preferred roles:
1. Problem/data or validation design diagram only if it clarifies the March → April decision setup.
2. Model-vs-baseline comparison on the same held-out split.
3. Ranked-action/playbook evidence or score/action distribution that supports the recommendation section.

Every figure must:
- make one primary point,
- label axes and metrics in plain language,
- remain legible on mobile,
- include a short caption plus a one-sentence takeaway,
- avoid rainbow colour scales,
- avoid using colour as the only differentiator,
- avoid unnecessary panels, effects, shadows and decoration.

## Results presentation

The model-vs-baseline table is the primary quantitative artifact because exact values are easier to audit in a table.

Charts provide shape and emphasis, not replacement values.

Where appropriate the page will expose:
- baseline value,
- learned-model value,
- direction of improvement,
- evaluation population / split,
- any important caveat needed to interpret the number.

The page will distinguish training-CV tuning results from held-out evaluation results. A CV result will never be presented as if it were final held-out performance.

## Claim language

Use:
- observed
- measured
- held-out
- directional
- decision-support
- associated with
- under this validation design

Avoid unsupported language such as:
- proves
- causes
- guarantees
- production-ready
- universally generalizes

## Reproducibility UX

The page must link to:
- repository root,
- `work/notebooks/capstone.ipynb`,
- the relevant Assignment 4–8 notebooks used to support methodology/results,
- any public-safe generated outputs embedded in the paper.

The reproducibility section will state the grouped validation design, random seed(s), decision point and rerun path in concise form.

## Public-safety rules

Before deployment, scan the served `docs/` folder and the final notebook for:
- client names,
- client URLs/domains,
- raw/private search queries,
- credentials/tokens,
- local machine paths,
- non-public identifiers,
- claims that expose individual clients or imply causal impact not established by the analysis.

Only aggregated, pseudonymized or already public-safe information may appear.

## Final implementation choice

Build a hand-authored, responsive `docs/index.html` with lightweight local CSS and relative assets.

Reason:
- cleaner public artifact than a raw notebook export,
- precise control over the nine-section structure,
- easy GitHub Pages deployment,
- mobile-friendly,
- no build framework required,
- minimal deployment risk.

The notebook remains the analytical source of truth; the static page is the communication layer.
