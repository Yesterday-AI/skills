# Color Palette & Brand Style

**This is the single source of truth for all colors and brand-specific styles.** To customize diagrams for your own brand, edit this file — everything else in the skill is universal.

Based on **Yesterday Corporate Identity** (see `web-design/references/yesterday-ci-briefing.md` for full CI spec).

---

## Shape Colors (Semantic)

Colors encode meaning, not decoration. Each semantic purpose has a fill/stroke pair.

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#FFD8CB` | `#FC4E14` |
| Secondary | `#FFECB9` | `#FFBB38` |
| Tertiary | `#E5E5E5` | `#737373` |
| Start/Trigger | `#FFECB9` | `#92610F` |
| End/Success | `#E6F4EC` | `#1B7340` |
| Warning/Reset | `#FCEAE7` | `#C43D2E` |
| Decision | `#FFF4E0` | `#92610F` |
| AI/LLM | `#EFF6FF` | `#2563EB` |
| Inactive/Disabled | `#F5F5F5` | `#8C8C8C` (use dashed stroke) |
| Error | `#FCEAE7` | `#C43D2E` |

**Rule**: Always pair a darker stroke with a lighter fill for contrast.

---

## Text Colors (Hierarchy)

Use color on free-floating text to create visual hierarchy without containers.

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#0A0A0A` | Section headings, major labels |
| Subtitle | `#FC4E14` | Subheadings, secondary labels (Yesterday Orange) |
| Body/Detail | `#737373` | Descriptions, annotations, metadata |
| On light fills | `#1A1A1A` | Text inside light-colored shapes |
| On dark fills | `#FFFFFF` | Text inside dark-colored shapes |

---

## Evidence Artifact Colors

Used for code snippets, data examples, and other concrete evidence inside technical diagrams.

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#1A1A1A` | Syntax-colored (language-appropriate) |
| JSON/data example | `#1A1A1A` | `#1B7340` (Yesterday Green) |

---

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Use the stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | `#0A0A0A` (Yesterday Black) or `#737373` (Slate) |
| Marker dots (fill + stroke) | `#FC4E14` (Yesterday Orange) |

---

## Background

| Property | Value |
|----------|-------|
| Canvas background | `#FFFFFF` |

---

## Premium Infographic Palette (opt-in)

**Use this palette only in Premium Infographic mode** (see `SKILL.md` →
"Premium Infographic Mode"). It reproduces the hand-drawn Daily-Dose-of-DS /
Akshay-Pachaar look. The default skill palette above is unchanged for normal
diagrams. Values measured from 55+ DDoDS infographics + verified by render.

### Canvas

| Property | Value | Note |
|----------|-------|------|
| Background | `#F7F3E9` | warm cream, NOT pure white -- set `appState.viewBackgroundColor` and render with `--theme light` |

**Renderer note:** the bundled renderer forces white bg in `--theme dark` and
inverts colors; premium infographics MUST render with `--theme light` for the
cream canvas + true pastels to appear.

### State-coded pastel fills (each fill pairs with a darker same-hue stroke OR a charcoal `#1F1F1F` hand-drawn outline)

| State / meaning | Fill | Stroke |
|-----------------|------|--------|
| Neutral / info | `#D3EBF7` (blue) | `#2F6FA8` |
| Good / done / correct | `#C2E7B0` (mint) | `#4E8C3F` |
| Special / uncertain | `#D2B9DE` (lavender) | `#7B5BA6` |
| Bad / warning / discarded | `#F9BC9E` (coral) | `#C75A3A` |
| Highlight / emphasis | `#FCEDCE` (butter) | `#B5872B` |
| Inactive / secondary | `#ECECE8` (neutral) | `#8A8A82` |

Color = state. Green=done/correct, coral=bad/discarded, lavender=special,
blue=neutral, butter=highlighted. Use dashed strokes for pending/grouping.

### Text & lines (premium)

| Element | Color |
|---------|-------|
| Title / label on light fill | `#1A1A1A` |
| Body / subtitle on a colored pill | the pill's stroke color (e.g. blue text `#2F6FA8`) |
| Annotation / metadata | `#737373` |
| Bottom-summary thesis sentence | `#1F1F1F` |
| Hand-drawn outlines & arrows | `#1F1F1F` (charcoal) |
| Structural dashed loop / divider | `#8A8A82` |

### Highlighter swipe

A thin filled rounded-rect (the state fill, `strokeColor: "transparent"`) placed
*behind* a free-floating label gives the "annotated whiteboard" look. Used behind
arrow labels (e.g. mint behind "action", lavender behind "observation").

---

## Yesterday CI — Editorial Treatment (opt-in)

A premium-quality treatment that keeps the **default Yesterday palette above**
(orange `#FC4E14`, gold `#FFBB38`, the semantic pairs) but presents it cleanly
and editorially — for on-brand infographics, not the hand-drawn DDoDS look.
Worked example: `references/examples/yesterday-ci-infographic.excalidraw`.

**How it differs from the Premium (Pachaar) treatment:** clean not hand-drawn.

| Setting | Value | Why |
|---------|-------|-----|
| `roughness` | `0` | Yesterday CI is precise/editorial, NOT wobbly hand-drawn |
| Canvas `viewBackgroundColor` | `#F7F3E9` (warm cream) | matches the live Yesterday product look; render `--theme light` |
| Cards / surfaces | fill `#FFFFFF`, border `#E3DDD0` (warm gray), `radius` 12 | clean white cards on cream |
| Primary accent | orange `#FC4E14` (light `#FFD8CB`) | arrows, ticks, kicker color, verdict border |
| Type ramp | display `7` Lilita One · body/labels `6` Nunito · mono/kicker `3` Cascadia | see note below |

**Font caveat (tested):** the real Yesterday CI fonts (Source Serif 4 / DM Sans /
IBM Plex Mono) are NOT in the Excalidraw renderer and custom fonts are unsupported.
The serif display face is therefore **not reproducible** — Lilita One (`7`) is the
closest strong display substitute. Body→Nunito (`6`) and mono→Cascadia (`3`) are
faithful enough. All three render umlauts correctly.

### CI signature elements (reproduce these for an on-brand figure)

- **Mono kicker** — `NN — UPPERCASE` label in Cascadia (`3`), orange `#FC4E14`, above each title (e.g. `PROGRAMM — 01`, `01 — ASSESSMENT`).
- **Orange tick** — short fat orange rect flush-left of the headline.
- **Top accent bar** — a thin colored bar near a card's top edge in that item's semantic color. On a ROUNDED card it must be **inset by the corner radius and rounded at its own ends** (≈30px inset), or its square ends poke past the card's rounded corners. The builder's `Scene.top_accent()` does this.
- **Verdict bar** — closing full-width box, cream-tinted `#FFF3EE` fill + a 12px solid orange left border + kicker `DAS PRINZIP` + a one-line display thesis. The on-brand replacement for the bottom-summary sentence.
- **Wordmark + footer** — `by Yesterday` (Lilita One) top-right; mono footer `Yesterday — yesterday.company` / `Vertraulich · Nur für interne Verwendung`.

> Source-of-truth for the broader CI lives outside this skill in the `brand/` repo
> (`brand/skills/yesterday-consulting-ci-briefing`). Note the brand docs and the
> live product palette diverge — confirm before a client-facing deliverable.

---

## Dark Technical Reference — Treatment (opt-in)

A **flat dark-mode** style for dense technical reference posters (memory/system
architectures, API maps). This is reproducible in Excalidraw — distinct from the
glowing-neon family (which is NOT, see `signature-elements.md` §5). Worked
examples: `references/examples/dark-agent-memory.excalidraw`,
`dark-inference-grid.excalidraw`. Builder palette: `DARK` in `infographic_builder.py`.

**Render with `--theme light`** (NOT `--theme dark`, which inverts colors). The
dark canvas comes from `appState.viewBackgroundColor`.

| Role | Value |
|------|-------|
| Canvas | `#1C1A2B` (dark navy) |
| Card | `#14131C` fill, border `#5B4E86` (or the card's accent color) |
| Divider / track | `#3A3550` / `#262236` |
| Text / muted | `#E8E6F2` / `#9A95B5` |
| Accents | purple `#A78BFA` · teal `#34D3C0` · green `#6BD46B` · orange `#F2913D` · pink `#FB6FA0` · red `#F2655C` |

**Signature elements (theme-agnostic — also usable in light):**
- **Gradient header band** — Excalidraw `exportToSvg` has NO native gradient; approximate with 5-6 stacked solid segments (orange→pink→purple). The one real limitation of this style.
- **Capacity / usage meter bar** — track rect + accent fill at `pct` (`Scene.meter`).
- **Gauge / timer ring** — thick-stroke ring + centered value + label below (`Scene.gauge`).
- **Horizontal step-strip** — a line with colored station dots, each `STEP N` + title + caption.
- **File card with metrics header** — dark card, mono filename left + right-aligned metrics, divider, bullet content, meter at the bottom.
- **Tier columns** — N columns, each a mono accent header + subtitle + accent divider, grouping cards.
- **Pro / con bullets** — `+` green / `−` red prefixed lines.
- **Checklist** — `▢`/`☑` or `+ …?` reflection items.
- **Secondary pill row** — small dark pills for "also available" options.
