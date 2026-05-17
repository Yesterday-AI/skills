---
name: excalidraw-diagram
description: >
  Create Excalidraw diagram JSON files that make visual arguments -- workflows, architectures,
  concepts. Use when the user wants to visualize systems, processes, or ideas as .excalidraw files.
  Covers design methodology, section-by-section building, render-validate loop, and quality checklist.
metadata:
  author: Yesterday-AI
  version: "1.1"
  category: design
  source: https://github.com/coleam00/excalidraw-diagram-skill
compatibility: >
  File write access required. Rendering to PNG requires Python 3.11+, uv, and Playwright (chromium).
---

# Excalidraw Diagram Creator

Generate `.excalidraw` JSON files that **argue visually**, not just display information.

**Setup:** If the renderer hasn't been set up yet:
```bash
cd skills/excalidraw-diagram/references
uv sync
uv run playwright install chromium
```

## Customization

**All colors and brand-specific styles live in one file:** `references/color-palette.md`. Read it before generating any diagram and use it as the single source of truth for all color choices -- shape fills, strokes, text colors, evidence artifact backgrounds, everything.

To make this skill produce diagrams in a different brand style, edit `color-palette.md`. Everything else in this file is universal design methodology and Excalidraw best practices.

---

## Core Philosophy

**Diagrams should ARGUE, not DISPLAY.**

A diagram isn't formatted text. It's a visual argument that shows relationships, causality, and flow that words alone can't express. The shape should BE the meaning.

**The Isomorphism Test**: If you removed all text, would the structure alone communicate the concept? If not, redesign.

**The Education Test**: Could someone learn something concrete from this diagram, or does it just label boxes? A good diagram teaches--it shows actual formats, real event names, concrete examples.

---

## Depth Assessment (Do This First)

Before designing, determine what level of detail this diagram needs:

### Simple/Conceptual Diagrams
Use abstract shapes when:
- Explaining a mental model or philosophy
- The audience doesn't need technical specifics
- The concept IS the abstraction (e.g., "separation of concerns")

### Comprehensive/Technical Diagrams
Use concrete examples when:
- Diagramming a real system, protocol, or architecture
- The diagram will be used to teach or explain (e.g., YouTube video)
- The audience needs to understand what things actually look like
- You're showing how multiple technologies integrate

**For technical diagrams, you MUST include evidence artifacts** (see below).

---

## Research Mandate (For Technical Diagrams)

**Before drawing anything technical, research the actual specifications.**

If you're diagramming a protocol, API, or framework:
1. Look up the actual JSON/data formats
2. Find the real event names, method names, or API endpoints
3. Understand how the pieces actually connect
4. Use real terminology, not generic placeholders

Bad: "Protocol" -> "Frontend"
Good: "AG-UI streams events (RUN_STARTED, STATE_DELTA, A2UI_UPDATE)" -> "CopilotKit renders via createA2UIMessageRenderer()"

**Research makes diagrams accurate AND educational.**

---

## Evidence Artifacts

Evidence artifacts are concrete examples that prove your diagram is accurate and help viewers learn. Include them in technical diagrams.

**Types of evidence artifacts** (choose what's relevant to your diagram):

| Artifact Type | When to Use | How to Render |
|---------------|-------------|---------------|
| **Code snippets** | APIs, integrations, implementation details | Dark rectangle + syntax-colored text (see color palette for evidence artifact colors) |
| **Data/JSON examples** | Data formats, schemas, payloads | Dark rectangle + colored text (see color palette) |
| **Event/step sequences** | Protocols, workflows, lifecycles | Timeline pattern (line + dots + labels) |
| **UI mockups** | Showing actual output/results | Nested rectangles mimicking real UI |
| **Real input content** | Showing what goes IN to a system | Rectangle with sample content visible |
| **API/method names** | Real function calls, endpoints | Use actual names from docs, not placeholders |

The key principle: **show what things actually look like**, not just what they're called.

---

## Multi-Zoom Architecture

Comprehensive diagrams operate at multiple zoom levels simultaneously.

### Level 1: Summary Flow
A simplified overview showing the full pipeline or process at a glance.

### Level 2: Section Boundaries
Labeled regions that group related components. These create visual "rooms" that help viewers understand what belongs together.

### Level 3: Detail Inside Sections
Evidence artifacts, code snippets, and concrete examples within each section. This is where the educational value lives.

**For comprehensive diagrams, aim to include all three levels.**

### Bad vs Good

| Bad (Displaying) | Good (Arguing) |
|------------------|----------------|
| 5 equal boxes with labels | Each concept has a shape that mirrors its behavior |
| Card grid layout | Visual structure matches conceptual structure |
| Icons decorating text | Shapes that ARE the meaning |
| Same container for everything | Distinct visual vocabulary per concept |
| Everything in a box | Free-floating text with selective containers |

---

## Steady-State Principle (Not a Changelog)

**A diagram is a portrait of what the system IS today, not how it got there.** Release-history content belongs in a changelog or release notes, not on the canvas.

**Hard "never" list — these turn the diagram into a changelog:**
- "SHIPPED <month> <year>" / "Recent additions" / "What's new" sections.
- Ticket-id badges (`PROJ-123`, `M007`, `JIRA-…`) anywhere on the canvas.
- Date stamps next to pills or captions (`(added 2026-05-15)`, `(sandboxed 2026-…)`).
- Ticket tags inside feature titles (`Dashboard (M003)`, `Auth Service (PROJ-42)`) — the title is the *thing*, not the work item it shipped under.

**How to integrate a newly-shipped capability instead:** make it a noun in the body. Extend a pillar's description, add a small caption next to the box that owns it, increment a stat-card if the count moved, add a chip to a list of substrates. If a feature has no place in the steady-state portrait it isn't diagram-worthy — document it elsewhere (PROCESS docs, KNOWLEDGE log, release notes).

**Test**: read the diagram cold six months from now. Is every box still true, or are some captions only true if you remember when they shipped? Strip the time-bound captions.

---

## Container vs. Free-Floating Text

**Not every piece of text needs a shape around it.** Default to free-floating text. Add containers only when they serve a purpose.

| Use a Container When... | Use Free-Floating Text When... |
|------------------------|-------------------------------|
| It's the focal point of a section | It's a label or description |
| It needs visual grouping with other elements | It's supporting detail or metadata |
| Arrows need to connect to it | It describes something nearby |
| The shape itself carries meaning (decision diamond, etc.) | Typography alone creates sufficient hierarchy |
| It represents a distinct "thing" in the system | It's a section title, subtitle, or annotation |

**The container test**: For each boxed element, ask "Would this work as free-floating text?" If yes, remove the container.

### Mutating bound text: the `containerId` footgun

When a text element has `containerId: "<rect_id>"`, the renderer reads the *container's* position and lays the text inside it. **Changing the text's `x` / `y` does nothing visually** — the move is silently ignored.

Symptom: you re-position a bound text in JSON, re-render, and the text either disappears or stays at the old location while the new (empty) rectangle sits at the moved coordinates.

To relocate a bound text from card A → card B:
1. On the text element: set `containerId: "<B_rect_id>"`.
2. On `A.boundElements`: remove `{id: "<text_id>", type: "text"}`.
3. On `B.boundElements`: append `{id: "<text_id>", type: "text"}`.
4. On the text element: update `originalText` to match the current `text` field (Excalidraw uses `originalText` for wrap calculations; mismatch causes layout glitches).

When in doubt, prefer `containerId: null` + `boundElements: []` from the start — gives you free positioning at the cost of losing auto-text-wrap-to-container.

---

## Design Process (Do This BEFORE Generating JSON)

### Step 0: Assess Depth Required
- **Simple/Conceptual**: Abstract shapes, labels, relationships
- **Comprehensive/Technical**: Concrete examples, code snippets, real data

**If comprehensive**: Do research first. Look up actual specs, formats, event names, APIs.

### Step 1: Understand Deeply
Read the content. For each concept, ask:
- What does this concept **DO**? (not what IS it)
- What relationships exist between concepts?
- What's the core transformation or flow?
- **What would someone need to SEE to understand this?**

### Step 2: Map Concepts to Patterns
For each concept, find the visual pattern that mirrors its behavior:

| If the concept... | Use this pattern |
|-------------------|------------------|
| Spawns multiple outputs | **Fan-out** (radial arrows from center) |
| Combines inputs into one | **Convergence** (funnel, arrows merging) |
| Has hierarchy/nesting | **Tree** (lines + free-floating text) |
| Is a sequence of steps | **Timeline** (line + dots + free-floating labels) |
| Loops or improves continuously | **Spiral/Cycle** (arrow returning to start) |
| Is an abstract state or context | **Cloud** (overlapping ellipses) |
| Transforms input to output | **Assembly line** (before -> process -> after) |
| Compares two things | **Side-by-side** (parallel with contrast) |
| Separates into phases | **Gap/Break** (visual separation between sections) |

### Step 3: Ensure Variety
For multi-concept diagrams: **each major concept must use a different visual pattern**. No uniform cards or grids.

### Step 4: Sketch the Flow
Before JSON, mentally trace how the eye moves through the diagram. There should be a clear visual story.

### Step 5: Generate JSON
Only now create the Excalidraw elements. **See below for how to handle large diagrams.**

### Step 6: Render & Validate (MANDATORY)
After generating the JSON, you MUST run the render-view-fix loop until the diagram looks right. See the **Render & Validate** section below.

---

## Large / Comprehensive Diagram Strategy

**For comprehensive or technical diagrams, build the JSON one section at a time.** Do NOT attempt to generate the entire file in a single pass -- token limits and quality both demand section-by-section building.

### The Section-by-Section Workflow

**Phase 1: Build each section**

1. **Create the base file** with the JSON wrapper (`type`, `version`, `appState`, `files`) and the first section of elements.
2. **Add one section per edit.** Each section gets its own dedicated pass.
3. **Use descriptive string IDs** (e.g., `"trigger_rect"`, `"arrow_fan_left"`) so cross-section references are readable.
4. **Namespace seeds by section** (e.g., section 1 uses 100xxx, section 2 uses 200xxx) to avoid collisions.
5. **Update cross-section bindings** as you go.

**Phase 2: Review the whole**

After all sections are in place, read through the complete JSON and check:
- Are cross-section arrows bound correctly on both ends?
- Is the overall spacing balanced?
- Do IDs and bindings all reference elements that actually exist?

**Phase 3: Render & validate**

Run the render-view-fix loop from the Render & Validate section.

### What NOT to Do

- **Don't generate the entire diagram in one response.** You will hit the output token limit and produce truncated, broken JSON.
- **Don't use a coding agent** to generate the JSON. The agent won't have sufficient context about the skill's rules.
- **Don't write a Python generator script.** Hand-crafted JSON with descriptive IDs is more maintainable.

---

## Visual Pattern Library

### Fan-Out (One-to-Many)
Central element with arrows radiating to multiple targets. Use for: sources, PRDs, root causes, central hubs.

### Convergence (Many-to-One)
Multiple inputs merging through arrows to single output. Use for: aggregation, funnels, synthesis.

### Tree (Hierarchy)
Parent-child branching with connecting lines and free-floating text (no boxes needed). Use `line` elements for the trunk and branches, free-floating text for labels.

### Spiral/Cycle (Continuous Loop)
Elements in sequence with arrow returning to start. Use for: feedback loops, iterative processes.

### Cloud (Abstract State)
Overlapping ellipses with varied sizes. Use for: context, memory, conversations, mental states.

### Assembly Line (Transformation)
Input -> Process Box -> Output with clear before/after. Use for: transformations, processing, conversion.

### Side-by-Side (Comparison)
Two parallel structures with visual contrast. Use for: before/after, options, trade-offs.

### Gap/Break (Separation)
Visual whitespace or barrier between sections. Use for: phase changes, context resets, boundaries.

### Lines as Structure
Use lines (type: `line`, not arrows) as primary structural elements instead of boxes:
- **Timelines**: Vertical/horizontal line with small dots (10-20px ellipses) at intervals, free-floating labels beside each dot
- **Tree structures**: Vertical trunk line + horizontal branch lines, with free-floating text labels
- **Dividers**: Thin dashed lines to separate sections
- **Flow spines**: A central line that elements relate to

Lines + free-floating text often creates a cleaner result than boxes + contained text.

---

## Shape Meaning

Choose shape based on what it represents -- or use no shape at all:

| Concept Type | Shape | Why |
|--------------|-------|-----|
| Labels, descriptions, details | **none** (free-floating text) | Typography creates hierarchy |
| Section titles, annotations | **none** (free-floating text) | Font size/weight is enough |
| Markers on a timeline | small `ellipse` (10-20px) | Visual anchor, not container |
| Start, trigger, input | `ellipse` | Soft, origin-like |
| End, output, result | `ellipse` | Completion, destination |
| Decision, condition | `diamond` | Classic decision symbol |
| Process, action, step | `rectangle` | Contained action |
| Abstract state, context | overlapping `ellipse` | Fuzzy, cloud-like |
| Hierarchy node | lines + text (no boxes) | Structure through lines |

**Rule**: Default to no container. Add shapes only when they carry meaning. Aim for <30% of text elements to be inside containers.

---

## Color as Meaning

Colors encode information, not decoration. Every color choice should come from `references/color-palette.md`.

**Key principles:**
- Each semantic purpose (start, end, decision, AI, error, etc.) has a specific fill/stroke pair
- Free-floating text uses color for hierarchy (titles, subtitles, details)
- Evidence artifacts (code snippets, JSON examples) use their own dark background + colored text scheme
- Always pair a darker stroke with a lighter fill for contrast

**Do not invent new colors.** If a concept doesn't fit an existing semantic category, use Primary/Neutral or Secondary.

---

## Modern Aesthetics

### Roughness
- `roughness: 0` -- Clean, crisp edges. **Default for most use cases.**
- `roughness: 1` -- Hand-drawn, organic feel. Use for brainstorming/informal diagrams.

### Stroke Width
- `strokeWidth: 1` -- Thin, elegant. Good for lines, dividers, subtle connections.
- `strokeWidth: 2` -- Standard. Good for shapes and primary arrows.
- `strokeWidth: 3` -- Bold. Use sparingly for emphasis.

### Opacity
**Always use `opacity: 100` for all elements.**

### Small Markers Instead of Shapes
Use small dots (10-20px ellipses) as timeline markers, bullet points, connection nodes, visual anchors.

---

## Layout Principles

### Hierarchy Through Scale
- **Hero**: 300x150 - visual anchor, most important
- **Primary**: 180x90
- **Secondary**: 120x60
- **Small**: 60x40

### Whitespace = Importance
The most important element has the most empty space around it (200px+).

### Flow Direction
Guide the eye: typically left->right or top->bottom for sequences, radial for hub-and-spoke.

### Connections Required
Position alone doesn't show relationships. If A relates to B, there must be an arrow.

---

## Text Rules

**CRITICAL**: The JSON `text` property contains ONLY readable words.

```json
{
  "id": "myElement1",
  "text": "Start",
  "originalText": "Start"
}
```

Settings: `fontSize: 16`, `fontFamily: 3`, `textAlign: "center"`, `verticalAlign: "middle"`

---

## JSON Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

## Element Templates

See `references/element-templates.md` for copy-paste JSON templates for each element type (text, line, dot, rectangle, arrow). Pull colors from `references/color-palette.md` based on each element's semantic purpose.

---

## Pre-bundled Libraries

`references/libraries/` ships four curated `.excalidrawlib` shape vocabularies covering the full architecture-diagramming spectrum:

- **`lo-fi-wireframing-kit`** -- UI mockups (buttons, forms, alerts, cards, page frames, phone/desktop/tablet)
- **`system-design`** -- generic architecture shapes (DB types, server, cache, LB, message queue, pipeline, CDN)
- **`technology-logos`** -- concrete tech-stack logos (K8s, Docker, Terraform, Kafka, Redis, Spring, Kotlin, Neo4j, ...)
- **`cloud-design-patterns`** -- distributed-system patterns as full mini-diagrams (retry, circuit breaker, sharding, throttling, queue-based load leveling)

Read `references/libraries/README.md` for the decision matrix and per-library preview PNGs. When a diagram needs a recognizable shape that fits one of these vocabularies, lift the relevant `libraryItems[*].elements` array into your diagram instead of redrawing from scratch -- re-seed `id`/`seed`/`versionNonce` to avoid collisions, and translate coordinates to your target position.

The skill's "shape = meaning" mandate still applies: pick libraries that *encode meaning* (system-design = "this is a DB", technology-logos = "this is Postgres specifically"), not libraries that decorate.

---

## Render & Validate (MANDATORY -- minimum 3 passes)

You **cannot** judge a diagram from JSON alone. Coordinates that look correct routinely produce overlapping text, clipped labels, and broken layouts when rendered. **Never deliver a diagram without completing the render loop.**

### The Rule

**Minimum 3 render-verify-adapt passes.** No exceptions. Each pass follows this exact sequence:

1. **Render** -- Run the render script to produce a PNG
2. **View** -- Read the PNG with the Read tool and actually look at it
3. **List issues** -- Write down every problem you see (be specific: "label X overlaps shape Y", "arrow Z points into empty space")
4. **Fix** -- Edit the JSON to address every listed issue
5. **Go to 1**

A diagram is done when a pass finds **zero issues**, not when you've completed 3 passes. 3 is the floor, not the ceiling.

**Do NOT skip this loop.** Do NOT render once and declare it done. The first render almost always has problems -- that's expected and fine. The loop is how you fix them.

### How to Render

```bash
cd skills/excalidraw-diagram/references && uv run python render_excalidraw.py <path-to-file.excalidraw>
```

This outputs a PNG next to the `.excalidraw` file. Then use the **Read tool** on the PNG to actually view it.

**Scale caveat for large diagrams.** The default `--scale 2` produces a 2× device-pixel PNG. On diagrams whose final pixel dimensions exceed ~10 000 px per side, the Chrome canvas-pixel ceiling silently drops content from the rendered SVG — entire boxes vanish with no error. The renderer auto-downgrades to `--scale 1` when the projected size would cross this threshold (and logs a warning); you can force `--scale 1` manually if a section is missing from a `--scale 2` render. A smaller PNG with all content always beats a sharper PNG with missing boxes.

### Static checks before render (cheap, catch the obvious)

The render loop is the only complete validator, but two programmatic checks catch the most common defects before paying for a chromium round-trip. Run them after every JSON edit:

**Bbox-overlap scan** — for every pair of `text` elements, compute bbox-intersection area. Flag any pair >100 px². Catches a multi-line text spilling through siblings (e.g. you set a `text` element's text to 3 lines but its parent rect is sized for 1).

**Glyph-width estimation** — for every text element, estimate the rendered width of the widest line:

```python
fs = el.get("fontSize", 20)
coef = 0.60 if el.get("fontFamily") == 3 else 0.55   # 3 = Cascadia mono; else proportional
widest_chars = max(len(line) for line in el["text"].split("\n"))
est_w = widest_chars * fs * coef
```

Compare `est_w` against the element's declared `width` AND against the containing card's *interior* width. Flag any element where `est_w > declared_width + 5`. This catches monospace strings overflowing a card sideways with no warning — bbox says "fits", glyphs say "no".

Both checks are ~10 lines of Python and run in milliseconds. Use them as a pre-flight gate before the slow render-validate loop, not as a replacement for it.

### What to Check Each Pass

**Vision check** -- compare rendered result to your design intent:
- Does the visual structure match the conceptual structure?
- Does each section use the pattern you intended?
- Does the eye flow through the diagram in the right order?
- Is the visual hierarchy correct?
- For technical diagrams: are evidence artifacts readable?

**Defect check** -- look for these specific issues:
- Text clipped by or overflowing its container
- Text or shapes overlapping other elements
- Embedded images covering labels or descriptions
- Arrows crossing through elements instead of routing around
- Arrows landing on the wrong element or pointing into empty space
- Labels floating ambiguously between multiple elements
- Uneven spacing between elements that should be evenly spaced
- Text too small to read at the rendered size
- Overall composition lopsided or unbalanced
- Whole sections missing from the PNG (scale=2 canvas-ceiling silent-drop; try `--scale 1`)

**Don't trust the full-image thumbnail alone.** When the Read tool displays a large PNG, it downscales for viewing — overlaps and clipping under ~20 px vanish. For every edited region, also crop ~25% × 25% around the change and view at ≥1600 px wide. The thumbnail is for vibe; the zoom-crop is for review.

### When to Stop

The loop is done when:
- A full pass finds zero vision or defect issues
- No text is clipped, overlapping, or unreadable
- Arrows route cleanly and connect to the right elements
- Spacing is consistent and the composition is balanced
- You'd show it to someone without caveats

### First-Time Setup
```bash
cd skills/excalidraw-diagram/references
uv sync
uv run playwright install chromium
```

---

## Quality Checklist

### Depth & Evidence (Check First for Technical Diagrams)
1. **Research done**: Did you look up actual specs, formats, event names?
2. **Evidence artifacts**: Are there code snippets, JSON examples, or real data?
3. **Multi-zoom**: Does it have summary flow + section boundaries + detail?
4. **Concrete over abstract**: Real content shown, not just labeled boxes?
5. **Educational value**: Could someone learn something concrete from this?

### Conceptual
6. **Isomorphism**: Does each visual structure mirror its concept's behavior?
7. **Argument**: Does the diagram SHOW something text alone couldn't?
8. **Variety**: Does each major concept use a different visual pattern?
9. **No uniform containers**: Avoided card grids and equal boxes?

### Container Discipline
10. **Minimal containers**: Could any boxed element work as free-floating text instead?
11. **Lines as structure**: Are tree/timeline patterns using lines + text rather than boxes?
12. **Typography hierarchy**: Are font size and color creating visual hierarchy?

### Structural
13. **Connections**: Every relationship has an arrow or line
14. **Flow**: Clear visual path for the eye to follow
15. **Hierarchy**: Important elements are larger/more isolated

### Technical
16. **Text clean**: `text` contains only readable words
17. **Font**: `fontFamily: 3`
18. **Roughness**: `roughness: 0` for clean/modern (unless hand-drawn style requested)
19. **Opacity**: `opacity: 100` for all elements
20. **Container ratio**: <30% of text elements should be inside containers

### Visual Validation (Render Required)
21. **Rendered to PNG**: Diagram has been rendered and visually inspected
22. **No text overflow**: All text fits within its container (bbox AND glyph-width estimate)
23. **No overlapping elements**: Shapes and text don't overlap unintentionally
24. **Even spacing**: Similar elements have consistent spacing
25. **Arrows land correctly**: Arrows connect to intended elements
26. **Readable at export size**: Text is legible in the rendered PNG
27. **Balanced composition**: No large empty voids or overcrowded regions
28. **Zoom-crop reviewed**: Every edited region viewed at ≥1600 px wide, not just full-image thumbnail
29. **No silent-drop**: All sections present (verify if diagram is large and scale=2 was used)

### Steady-State Discipline
30. **No release-history captions**: Zero "SHIPPED <month>" sections, ticket-id badges, date stamps, or ticket-tagged titles
31. **Present-tense reading**: Every caption reads true six months from now without remembering when it shipped
