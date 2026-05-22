---
milestone: M002
project: skills
created: 2026-05-21T09:32:26Z
size: L
---

# M002 -- Context

## Goal

Give the `excalidraw-diagram` skill an additive, opt-in "premium infographic"
capability -- both the hand-drawn Daily-Dose-of-DS / Akshay-Pachaar visual style
AND the conceptual scaffolding (topic research, content distillation,
narrative / user-story storytelling) needed to build exciting, eye-catching, and
informative infographics -- without changing the skill's existing diagram
behavior.

## Exit criteria

- Visual style (opt-in): `color-palette.md` gains a warm-cream background + a
  6-hue, state-coded pastel system (measured DDoDS hex values); the font rule is
  reversed in premium mode (hand-drawn default, monospace only for code); a new
  "premium signature elements" pattern section exists (title pills, highlighter
  swipes, mascots, speech bubbles, bottom-summary sentence, emoji accents,
  inline icons, dashed=pending, numbered cycle, quadrant map, side-by-side glow);
  the anti-container dogma is relaxed for this mode.
- Conceptual support: a research-to-infographic + storytelling methodology
  section exists (topic research -> distillation -> the single thesis/argument ->
  narrative flow -> bottom-summary -> narrator/mascot voice + other methods).
- Mechanics: opencoredev sizing formulas adopted (e.g. `max(160, charCount*11+40)`,
  per-line height, >=80px arrow gap).
- Assets: 5 MIT-licensed OSS `.excalidrawlib` libraries bundled with preview PNGs
  (Stick Figures, Bubbles, Emojis, Sticky Notes, one icon set).
- Docs: `element-templates.md` + the quality checklist extended for premium mode.
- Existing behavior preserved: default (non-premium) diagram output is unchanged
  (mono font, roughness 0, white bg, container discipline still the default).
- Proof: a freshly authored sample infographic is rendered via the render-validate
  loop and visibly matches the DDoDS "Family B" hand-drawn look AND demonstrably
  tells a story (single thesis + narrative flow + bottom-summary).

## Size

L -- see `M002-ROADMAP.md` for slice breakdown.

## Decisions locked in discuss phase

- 2026-05-21: Premium capability is ADDITIVE / opt-in. The skill's current
  defaults (monospace font, `roughness: 0`, white background, "default to no
  container") remain the default behavior; premium mode is selected explicitly.
  Reason: user chose "Additiver Modus" over changing the global default.
- 2026-05-21: Scope includes CONCEPTUAL support (topic research, content
  distillation, storytelling / user-story, narrative methods), not only visual
  styling. Reason: user's exit-criteria note ("nicht nur visuell sondern auch
  konzeptionelle unterstuetzung").
- 2026-05-21: OSS-first. Reuse rather than rebuild: adopt opencoredev's sizing
  formulas and bundle the existing MIT libraries from libraries.excalidraw.com
  (Stick Figures / Bubbles / Emojis / Sticky Notes / icon set). Only the
  combined "DDoDS-premium" recipe is net-new (no published guide exists; DDoDS
  itself now generates these via an internal image agent, not a documented
  Excalidraw style guide).
- 2026-05-21: Target the reproducible "Family B" pure-Excalidraw hand-drawn style
  (e.g. diff-wsd, grpo-six-step), NOT the polished illustrated "Family A" look,
  which is image-generated and not reproducible in Excalidraw.

## Open questions

- Selection mechanism: how is premium mode opted into -- a dedicated section /
  flag inside `SKILL.md`, a separate reference doc, or a sub-skill? (Resolve in
  slicing.)
- Font: which `fontFamily` IDs does `references/render_template.html` actually
  support (Virgil / Excalifont)? Must be verified before locking the font rule;
  a hand-drawn font that the renderer can't load would silently fall back.
- 5th library: which single icon set to bundle (Awesome Icons vs System Design
  Icons vs Random figure drawings)?
- Source / analysis assets currently live in `/tmp/ddods/` (55+ reference images,
  measured palette). Decide whether to keep any in-repo as design references.
