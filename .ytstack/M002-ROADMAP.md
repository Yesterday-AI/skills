---
milestone: M002
project: skills
size: L
created: 2026-05-21T09:32:26Z
status: planned
total_slices: 4
completed_slices: 0
---

# M002 Roadmap

**Goal:** Give the `excalidraw-diagram` skill an additive, opt-in "premium
infographic" capability -- the hand-drawn DDoDS / Akshay-Pachaar visual style
plus the conceptual scaffolding (research, distillation, storytelling) to build
exciting, informative infographics -- without changing existing behavior.

**Exit criteria:**
- Opt-in premium visual style (cream bg, 6-hue state-coded pastels, hand-drawn
  font, signature-elements section, relaxed container rule).
- Conceptual support section (research -> distillation -> thesis -> narrative ->
  bottom-summary -> narrator voice).
- opencoredev sizing formulas adopted.
- 5 MIT OSS `.excalidrawlib` libraries bundled + previews.
- element-templates.md + quality checklist extended.
- Existing default behavior preserved.
- A freshly rendered sample infographic matches Family-B look AND tells a story.

## Slices

Slice detail lives in per-slice `M002-S##-PLAN.md` files, created by
`ytstack:slice-milestone`.

- [ ] S01 -- Opt-in premium visual style (cream bg, 6-hue state-coded pastels, hand-drawn font, roughness:1); defaults preserved [3 tasks]
- [ ] S02 -- Premium signature-elements section + element-templates + opencoredev sizing formulas [3 tasks]
- [ ] S03 -- Conceptual layer: research->distillation->thesis->narrative storytelling + quality checklist [3 tasks]
- [ ] S04 -- Bundle 5 MIT OSS libraries (+previews) + author & render-validate a proof sample infographic [4 tasks]

## Run order

Slices execute sequentially. After each slice, `ytstack:reassess-roadmap` checks
if the plan still fits reality.

## How to update this file

- Flip slice checkbox `[ ]` -> `[x]` when its tasks are all `summarize-task`-confirmed
- Update `completed_slices` count
- On milestone completion, flip `status: planned` -> `status: done` and update global ROADMAP.md
