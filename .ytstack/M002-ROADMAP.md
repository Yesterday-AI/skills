---
milestone: M002
project: skills
size: L
created: 2026-05-21T09:32:26Z
status: in-progress
total_slices: 4
completed_slices: 3
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

- [x] S01 -- Opt-in premium visual style (cream bg, 6-hue state-coded pastels, hand-drawn font, roughness:1); defaults preserved [3 tasks]
- [~] S02 -- signature-elements.md DONE (+ 32-item in-house `.excalidrawlib` as its executable counterpart). REMAINING: element-templates.md premium templates + opencoredev sizing formulas.
- [x] S03 -- Conceptual layer: research->distillation->thesis->narrative storytelling section + quality-checklist "Storyline" block [done 2026-05-22]
- [x] S04 -- 5 MIT OSS libraries bundled (+previews) + render-validated proof examples [done; exceeded -- see scope expansion]

## Scope expansion (2026-05-22, beyond original exit criteria)

Delivered well past the planned S01-S04 (committed `d977b89`):
- **3 opt-in themes** (not just the one pastel style): light pastel hand-drawn + Yesterday CI editorial + flat dark technical reference.
- **`infographic_builder.py`** -- shipped composition layer (places library items by name + connective tissue; PREMIUM/YESTERDAY/DARK palettes + meter/gauge/numbered_circle/top_accent helpers).
- **9 worked examples** (vs "a sample") spanning narrative shapes; 3 sourced from the llm-wiki, genericized.
- **Verified font catalog** (corrected fontFamily IDs) + custom-fonts-unsupported finding.
See DECISIONS.md 2026-05-22 and STATE.md for the full ledger.

## Run order

Slices execute sequentially. After each slice, `ytstack:reassess-roadmap` checks
if the plan still fits reality.

## How to update this file

- Flip slice checkbox `[ ]` -> `[x]` when its tasks are all `summarize-task`-confirmed
- Update `completed_slices` count
- On milestone completion, flip `status: planned` -> `status: done` and update global ROADMAP.md
