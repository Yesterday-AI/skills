# Excalidraw Library Bundle

Pre-bundled libraries from <https://libraries.excalidraw.com/> chosen to cover the full architecture-diagramming spectrum without overlap. Use them as **shape vocabularies** — copy-paste relevant library items into your diagram, then arrange / connect / annotate per the skill's design methodology in `../../SKILL.md`.

Ten libraries are bundled. **Nine** are MIT-licensed upstream downloads: **four**
cover architecture diagramming (below), **five** supply third-party signature
elements for **Premium Infographic Mode**. The **tenth — `infographic-elements`
— is built in-house**: the drop-in implementation of the atoms, concept icons,
data-viz primitives and composites catalogued in `../signature-elements.md`
(see "In-house infographic elements" below).

## Decision matrix — when to use which

| If your diagram is about… | Reach for | Why |
|---|---|---|
| **A user interface** (buttons, forms, alerts, cards, page frames) | `lo-fi-wireframing-kit` | 23 UI primitives + device frames (phone/desktop/tablet); hand-drawn aesthetic matches Excalidraw default |
| **Generic system architecture** ("a database", "a cache", "a load balancer", "a message queue") | `system-design` | 24 well-drawn shapes: 6 DB types, server variants, cache, DNS, LB, queue, pipeline, CDN, archive, mobile, web app — when the *category* of the box is what matters |
| **Concrete tech stack** ("this runs on Kubernetes + Postgres + Redis + Kafka") | `technology-logos` | 18 cloud-native logos: K8s, Docker, git, Cloud Foundry, Terraform, Spring, Quarkus, Micronaut, Knative, Camunda, Azure, Kafka, Kotlin, OpenStack, paketo.io, Neo4J, Redis — when the *brand* of the box is the argument |
| **Distributed-system patterns** (retry, circuit breaker, sharding, throttling, queue-based load leveling) | `cloud-design-patterns` | 24 multi-element pattern compositions — each tile is a *complete mini-diagram* that argues a pattern visually, not just an icon |

## Premium infographic signature libraries

These five power **Premium Infographic Mode** (see `../../SKILL.md` → "Premium
Infographic Mode") — the hand-drawn Daily-Dose-of-DS / Akshay-Pachaar look. Drop
them in as the warm, narrative-driving elements that plain diagrams don't need.

| For this signature element… | Reach for | Why |
|---|---|---|
| **Mascot / narrator** (confused at the problem, happy at the resolution) | `stick-figures` | 9 hand-drawn figures (Shrug, Happy, Sad, Guy, Girl, Grandma, Child…) — the narrator voice that makes the graphic feel alive |
| **Speech / thought bubbles** (commentary in the narrator's voice) | `bubbles` | 4 simple speech + thought bubbles |
| **Emoji accents** (✓ ✗ 🧠 ⚡ used sparingly as semantic punctuation) | `emojis` | 48 drawn emojis that match the hand-drawn aesthetic (font emoji may not render) |
| **Title pills / highlighter swipes / labels** | `sticky-notes` | 7 colored note/pill shapes for headlines and annotation backgrounds |
| **Inline icons in pills** (magnifier, gear, doc, db…) | `awesome-icons` | 24 general-purpose hand-drawn icons |

## In-house infographic elements

`infographic-elements.excalidrawlib` (32 items) is **our own** library — the
executable counterpart to `../signature-elements.md`. Where the upstream libs are
generic shape packs, this one ships the *specific* recurring building blocks of
the DDoDS / Pachaar look, pre-styled with the premium palette so they drop in
ready to use. Prefer these over redrawing.

| Group | Items |
|---|---|
| Atoms | Title pill · Highlighter title · Numbered badge · Check / Cross marker · Plus combiner · Sparkle · VS badge · Dashed flow arrow + badge · Checkbox item · Pro / con pair |
| Concept icons | Brain (embed/LLM) · Vector DB · Document · Query envelope · Gear · Search · Graph |
| Data-viz | Token column · Tensor grid · Set / region pair · Distribution curve · Capacity meter bar · Gauge ring · Step strip (3 stations) |
| Composites | Card frame + title pill · Speech bubble · Speech bubble (left tail) · Thought bubble · macOS code window · Verdict bar (Yesterday CI) · Mono kicker (CI) |

Regenerate it from `~skill-designing/builds/build_library.py` (the generator is
the source of truth; edit there, not the JSON by hand).

## What they look like

Open the `*-preview.png` next to each `.excalidrawlib` to see all items in that library at a glance.

| Library | Items | Preview |
|---|---:|---|
| Lo-Fi Wireframing Kit (Aleksandra Lazovic / spfr) | 23 | `lo-fi-wireframing-kit-preview.png` |
| System Design Components (Rohan Pithadiya / rohanp) | 24 | `system-design-preview.png` |
| Technology Logos (Matthias Haeussler / maeddes) | 18 | `technology-logos-preview.png` |
| Cloud Design Patterns (Michel Caradec / michelcaradec) | 24 | `cloud-design-patterns-preview.png` |
| Stick Figures (Youri Tjang / youritjang) | 9 | `stick-figures-preview.png` |
| Bubbles (Oscar Capraro / ocapraro) | 4 | `bubbles-preview.png` |
| Emojis (Anumitha Apollo / anumithaapollo12) | 48 | `emojis-preview.png` |
| Simple Sticky Notes (kleinpetr) | 7 | `sticky-notes-preview.png` |
| Awesome Icons (ferminrp) | 24 | `awesome-icons-preview.png` |
| **Infographic Elements (in-house)** | 32 | `infographic-elements-preview.png` |

## Compositional logic

The four libraries cover **disjoint** layers of an architecture diagram:

- **`lo-fi-wireframing-kit`** answers *"what does the UI look like"* (mockup layer)
- **`system-design`** answers *"what category of thing is this"* (semantic layer)
- **`technology-logos`** answers *"which specific product is this"* (identity layer)
- **`cloud-design-patterns`** answers *"how do the things behave together"* (pattern layer)

A single diagram often pulls from two or three of them. Example: a system architecture diagram might use `system-design` for boxes you don't need to brand, `technology-logos` for boxes where the brand is the point, and `cloud-design-patterns` to annotate retry/circuit-breaker behavior between them.

## How to extract items

The `.excalidrawlib` JSON has a top-level `libraryItems` array. Each item has its own `elements` list (with relative coordinates). To use one item:

1. Find the item by name in the `.excalidrawlib` file.
2. Copy its `elements` array.
3. Translate the coordinates to where you want them in your diagram (offset all `x`/`y` by the same `dx`/`dy`).
4. Drop them into your diagram's top-level `elements` array.
5. Re-seed `id` / `seed` / `versionNonce` to avoid collisions with the rest of your diagram.

For programmatic use, see how `render_excalidraw.py` validates JSON — the same shape rules apply.

## Why these four (and not others)

Evaluated against the skill's **"shape = meaning"** mandate. The four chosen libraries either *are* semantic vocabularies (system-design, cloud-design-patterns) or fill an identification gap that text alone can't (technology-logos, ui-mockups). Rejected:

- *Team Topologies, Wardley Maps* — too niche for general use
- *AWS Serverless / GCP / Azure icons* — useful but redundant with `technology-logos` for our typical use; can be added per-diagram if a strongly cloud-specific architecture is needed
- *UML Component / Deployment / ER* — formal UML is outside the skill's argumentative-diagram brief
- *Network Topology Icons (dwelle), Dev Ops Icons (markopolo123)* — overlap with `technology-logos` but with weaker / dated aesthetics
- *Atlassian, HashiCorp, Databricks, Microsoft Fabric* — single-vendor packs; pull in case-by-case via the libraries directory if a diagram is about that vendor specifically

## Updating

Refresh a library by re-downloading from the upstream source recorded in the original libraries.json:

```
LIB=<source-path-from-libraries.json>
curl -fsSL "https://raw.githubusercontent.com/excalidraw/excalidraw-libraries/main/libraries/${LIB}" \
  -o ./<name>.excalidrawlib
```

Sources of the four bundled libraries (as of 2026-05-02):

- `spfr/lo-fi-wireframing-kit.excalidrawlib`
- `rohanp/system-design.excalidrawlib`
- `maeddes/technology-logos.excalidrawlib`
- `michelcaradec/cloud-design-patterns.excalidrawlib`

Premium infographic libraries (added 2026-05-22):

- `youritjang/stick-figures.excalidrawlib`
- `ocapraro/bubbles.excalidrawlib`
- `anumithaapollo12/emojis.excalidrawlib`
- `kleinpetr/simple-sticky-notes.excalidrawlib`
- `ferminrp/awesome-icons.excalidrawlib`

`infographic-elements.excalidrawlib` is **not** an upstream download — it is
generated in-house. Do not refresh it with `curl`; regenerate from
`~skill-designing/builds/build_library.py` and re-render its preview.
