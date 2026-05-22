# Premium Infographic — Element Taxonomy (Atoms · Composites · Layouts)

The full visual vocabulary behind the Daily-Dose-of-DS / Akshay-Pachaar look,
organised atomic-design style. Used by **Premium Infographic Mode**
(`../SKILL.md`). Derived from analysis of 25+ of his infographics (RAG / KV-cache
/ HyDE / attention / function-calling+MCP / DBSCAN, etc.).

- **Most atoms/icons/composites below ship as drop-in shapes in `references/libraries/infographic-elements.excalidrawlib` (26 items) — the executable counterpart to this catalog. Use those first; this doc is the *why*, the lib is the *what*.** For anything not yet in the lib, pull from the other `references/libraries/` packs rather than redrawing.
- Colors come from the "Premium Infographic Palette" in `color-palette.md`.
- **When lifting a library icon as a pure glyph, strip its baked-in `text` elements** (many library items ship with a caption baked in — keep the shapes, drop the label, add your own).

---

## 1. ATOMS (smallest reusable units)

### 1a. Containers
- **Pill** — rounded rect, state-colored fill + darker/charcoal stroke. The workhorse.
- **Title pill** — color-coded headline pill.
- **Tab / caption pill** — small label, often on a band's left edge.
- **Card frame** — white/faint rounded rect, thin gray stroke (holds a mini-diagram).
- **Soft-tinted panel** — low-saturation full-width band background (green/blue/cream).
- **Dashed grouping box / banner** — dashed border = grouping or "pending".
- **Dashed loop ellipse** — encloses a cycle ("repeats every step").
- **Speech bubble** (rect + tail) / **thought bubble** (cloud + trailing dots). **The tail must emerge from the side facing the speaker and point at them** — left-side tail when the mascot is to the left, bottom tail only when the speaker is below. A generic bottom tail (or a long thin diagonal spike) reaching across to a side-placed figure looks broken. Make the tail a short, filled-white triangle so it merges with the bubble.
- **Sticky note** — slightly rotated rect (`angle` ≠ 0).
- **Poster frame** — a colored outer margin (solid pastel rect) wrapping the whole white inner card. Frames a single-concept poster (DBSCAN). The figure sits *inside* the frame.
- **macOS code window** — dark rounded panel + 3 traffic-light dots (red/amber/green) top-left, optional filename tab + language logo, syntax-highlighted mono code (`fontFamily: 3`, keyword/string/number colored). The richer "code snippet" form — use instead of a plain mono pill when the code is the point. Often slightly tilted (`angle` ≠ 0) and overlapped in pairs.

### 1b. Connectors
- **Dashed arrow** — his DEFAULT flow connector (most arrows are dashed charcoal, not solid). Use solid only for emphasis.
- **Curved / elbow arrow** — for routing around elements (similarity-search curve).
- **Plain line** — divider, underline, leader line, tree branch.
- **Dashed vertical divider** — between bands / grid columns / before-after.
- **Bracket glyph** `{` `]` — group several items under one label.
- **Leader line** — thin line from a margin label to the thing it annotates.

### 1c. Badges & markers
- **Numbered step badge** — dashed circle (~28px, butter `#FCEDCE`/`#B5872B`) + number, on each arrow.
- **Marker dot** — small filled ellipse (timeline node, bullet).
- **Checkmark ✓** (mint/green) / **cross ✗** (coral/red) — result markers.
- **"+" combiner glyph** — boxed/plain `+` (coral) merging stacked inputs.
- **"=" glyph**, **"VS" badge** (in a circle between two panels).
- **Sparkle ✦ / ✨** — "AI/magic" accent next to titles & vector DBs.

### 1d. Text atoms
- **Hand-drawn title** (`fontFamily: 1`).
- **Vertical accent bar** — short fat colored rect flush-left of the headline's first word (small lavender/state-colored tick that "starts" the title).
- **Multi-color title** — each concept-word in the title gets its OWN highlighter swipe in that concept's color (e.g. "Function Calling" blue swipe + "MCP" green swipe in one headline), so the title doubles as a color legend.
- **Highlighter swipe** — thin filled rounded-rect (transparent stroke) **behind** text, vertically centered on the glyphs (NOT below them).
- **Marker underline** — thick colored line under a title.
- **Color-coded keyword run** — split a sentence into multiple `text` elements so load-bearing words take state colors.
- **Underlined sub-heading** — "Insight 1" + short line beneath.
- **Gray annotation / italic side-note** — metadata, "20–100 often beats 500".
- **Color-matched annotation** — when a label points at a colored element, color the label text to MATCH it (orange "Core Point" → orange dot, green "Border Point" → green dot). The color *is* the cross-reference.
- **Footnote / disclaimer** — small italic asterisked caveat pinned to the bottom edge ("*MCP Host does not have two LLMs — shown twice to simplify").
- **Mono data snippet** — `fontFamily: 3` inside a light pill (code/JSON/scores).
- **Sub/superscript** — Q₄, t-3, K₁ (approximate with small inline text).
- **Math** — Excalidraw has NO LaTeX. Approximate with text, or pre-render to PNG and embed via the `files` map + an `image` element.
- **Source mark** — `join.DailyDoseofDS.com` top-right / `@handle` pill (often a coral/butter rounded pill bottom-center).
- **Author signature card** — round avatar + name + 🐦`@handle`, pinned bottom-right corner.

### 1e. Concept icons (consistent glyph system — biggest gap vs basics)
Reuse the SAME glyph for the same concept across the WHOLE figure.

| Concept | Glyph | Source |
|---|---|---|
| Embedding model | circuit-brain (teal) | draw, or `awesome-icons` |
| LLM | circuit-brain (red/orange) | `awesome-icons`; `technology-logos` for a named model |
| Vector DB | cylinder + ✦ | `system-design` (DB) + "✦" text |
| DB variants | relational/object/graph/document/columnar | `system-design` |
| Document / data source | paper / stacked pages | `awesome-icons` |
| Query | envelope | `awesome-icons` (email) |
| Prompt template | doc with lines | `awesome-icons` |
| Tools / control | gear | `awesome-icons` |
| Search / web | magnifier / globe | `awesome-icons` |
| Graph | nodes + edges | draw: `ellipse` dots + `line` edges |
| Compute | CPU/GPU/TPU chip | draw, or `technology-logos` |
| Image / JPG | framed thumbnail | draw: rect + small mountain glyph |
| Trash / discard | bin | `awesome-icons` / draw |
| Funnel | funnel (reduction) | draw: trapezoid + lines |
| Stacked / layered | offset stacked rects | draw |
| Window / phone frame | browser / device | `lo-fi-wireframing-kit` |
| Specific tech | brand logo (Kafka, Redis, AWS, K8s, deepseek…) | `technology-logos` |
| Agents (multiple) | color-differentiated figures/robots | `stick-figures` (recolor per agent) |
| Narrator | shrug / happy / sad / thinking figure | `stick-figures` |

### 1f. Data-viz atoms
- **Multi-instance icon grid** — repeat the SAME small icon in a tight 2×3 / 3×2 grid to mean "many of X" (a grid of folder icons = "MCP Tools", many docs = a corpus). One icon = one; a grid = a set.
- **Set / region diagram** — overlapping outlined circles (clusters/sets) with colored dots placed *inside* by membership; color encodes class (orange = core, green = border, gray = outlier). Annotate with leader arrows + color-matched labels; show a parameter as a labeled radius line (a thin line center→edge with rotated text "eps"). Concept-space, not flowchart.
- **Token / cell sequence column** — vertical stack of rounded cells (K₁…Kₙ), newest highlighted mint.
- **Tensor / matrix grid** — M×N small squares, one hue per matrix (W_Q lavender, W_K blue, W_V butter).
- **Mini bar chart** — a few bars (often inside a speech bubble).
- **Scatter / Pareto plot** — axes + bubbles placed by meaning + frontier curve.
- **2×2 quadrant** — labeled axes + a center compass + placed bubbles.
- **Overlapping distribution curves** — filled bell curves (explore/exploit).
- **Gauge / meter**, **timeline** (line + dots + alternating pills).

---

## 2. COMPOSITES (recurring atom combinations)

- **Pipeline node** = icon + label (+ optional sub-pill), joined by dashed arrows carrying numbered badges.
- **Embedding step** = doc/img glyph → dashed arrow "embed" → brain → dashed arrow "index" → DB cylinder.
- **Retrieval loop** = query envelope → embed → curved "similarity search" → DB → "similar docs" → context box.
- **Combine block** = stacked items joined by "+" glyphs into one box ("context + query + image").
- **Decision branch** = diamond + "yes/no"-labeled branches → color-coded leaf pills.
- **Insight pair** = visual panel (left) + right column of underlined "Insight N" + color-coded sentence.
- **Formula dissection** = central equation + each term boxed/tinted + leader lines to margin explanations.
- **Memory / planning sub-block** = container holding small sub-pills (Short/Long Term; ReAct/CoT).
- **Agent cluster** = color-differentiated robot/figure avatars (Agent 1/2/3) → tool icons (search/db/cloud).
- **Narrator arc** = confused mascot + bubble at the problem … happy mascot at the payoff.
- **Good/bad contrast** = two panels, green-glow vs coral-glow, each with ✓/✗ + a mascot.
- **Result gate** = "Better? ✓ Keep" / "Worse? ✗ Discard" pills off a Test step.
- **Titled card** = card frame + corner title pill + a mini-pipeline inside.
- **Concept-space diagram** = set/region atoms (overlapping circles) + points placed by membership + color-matched leader annotations + a labeled measurement line. The non-flowchart way to teach a spatial/geometric concept (DBSCAN, margins, clusters, decision boundaries).
- **Code+effect pair** = a macOS code window beside (or above) the hand-drawn diagram of what the code does — bridges "the code" and "the intuition".

---

## 3. LAYOUTS (whole-canvas skeletons)

- **Card grid / matrix** — N identical titled cards in a 2×N / 3×N grid ("8 RAG Architectures", "5 Compute Architectures", "8 AI Models"). His dominant format.
- **Banded comparison** — 2–3 stacked tinted panels, each with a left-edge section tab + a full pipeline (RAG vs HyDE, RAG vs Agentic). For two parallel *processes* (Function Calling vs MCP), give each band a giant left-edge category label in a tinted pill so the band reads as a labeled column.
- **Single-concept poster** — one centered concept inside a poster frame (colored margin), title pill on top, `@handle` pill at the bottom. For teaching ONE idea deeply (a set diagram, one formula) rather than a multi-step pipeline.
- **Linear pipeline** — one L→R (or looped) flow with numbered steps (Multimodal RAG, KV-cache panels).
- **Insight column** — wide visual + narrow right prose column of insights.
- **Formula sheet** — central equation dissected with leader lines (BM25, attention).
- **Quadrant map** — 2×2 axes + compass + placed approaches (design-space maps).
- **Decision tree** — question diamond → branches → recommended leaf pills.
- **Timeline** — horizontal line, alternating above/below pills, a figure at the "now" end.
- **Concept-space map** — a 2D plane where position carries meaning (clusters, regions, points), annotated with leader labels — for geometric/spatial ideas (see Concept-space diagram, §2).

---

## 4. BUILD RECIPE
1. State the ONE thesis (becomes the bottom-summary).
2. Pick a **layout** (§3) for the argument shape.
3. Lay the backbone from **composites** (§2) using the shared **icon system** (§1e) — same glyph per concept; dashed arrows; numbered badges.
4. Add the narrator (mascot + bubble) and result markers (✓/✗).
5. Annotate: color-coded keywords, insight panel or margin labels, sparkles, source mark.
6. Bottom-summary thesis sentence.
7. Render `--theme light`; run the render-validate loop (zoom-crop every region — library icons can carry stray baked-in labels; swipes can sit off the text).

---

## 5. STYLES TO AVOID
Distinguish two dark looks — only ONE is the avoid case:
- **Glowing-neon / illustrated** (black canvas, glowing neon outline icons, gradients baked into the art — "8 AI model architectures") — a different tool/template family, NOT reproducible as flat Excalidraw. **Avoid.**
- **Flat dark-mode** (dark navy canvas, FLAT colored cards, mono text, meter bars — the "Memory in Hermes Agent" look) — fully reproducible and a **supported theme**: see "Dark Technical Reference" in `color-palette.md`. Render `--theme light`. NOT an avoid case.

Default target remains the **light pastel hand-drawn** family (KV-caching, HyDE,
8 RAG architectures, Multimodal RAG); flat-dark and Yesterday-CI are opt-in alternatives.

His **carousel cover slides** (gradient background, big serif title, glossy
emoji, tilted carbon.now.sh code windows) are also a different tool family — a
hook slide, not an Excalidraw infographic. Don't reproduce the gradient/serif
cover. The **macOS code window** atom itself, however, *is* reproducible in flat
Excalidraw (dark rounded rect + 3 dots + mono text) and belongs in the diagram.
