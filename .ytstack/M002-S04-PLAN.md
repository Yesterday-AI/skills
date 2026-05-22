---
milestone: M002
slice: S04
project: skills
created: 2026-05-21T10:06:28Z
status: planned
task_count: 4
completed_tasks: 0
---

# M002-S04 -- Slice Plan

**Goal:** Ship the batteries-included assets and prove the recipe: five MIT OSS
libraries bundled with previews, plus a freshly authored sample infographic that,
after the render-validate loop, visibly matches the DDoDS "Family B" look AND
tells a story.

## Tasks

- [ ] T01 -- Download and bundle 5 MIT-licensed `.excalidrawlib` libraries into `references/libraries/` (Stick Figures / Bubbles / Emojis / Sticky Notes + one icon set -- pick the 5th: Awesome Icons vs System Design Icons). Record source URL + author + MIT license for each (NOTICE / per-file attribution).
- [ ] T02 -- Generate preview PNGs for the 5 new libraries and update `references/libraries/README.md`: extend the decision matrix mapping each new library to its premium signature role (mascots / bubbles / emoji / pills / inline icons).
- [ ] T03 -- Author a proof-of-concept premium sample `.excalidraw` on a real ML/AI topic: opt-in premium mode, single thesis, multi-zoom layout, >=2 signature elements, a narrator/mascot, and a bottom-summary sentence.
- [ ] T04 -- Run the render-validate loop (minimum 3 passes) on the sample; iterate until zero defects, it visibly matches Family-B, and the story reads cold; save the final PNG as the skill's bundled example and reference it from `SKILL.md`.

## Done when

All tasks marked `[x]` and verified via `ytstack:summarize-task`. This slice
carries the milestone's proof exit-criterion.

## Notes

- Libraries from libraries.excalidraw.com (all MIT): Stick Figures (Youri Tjang), Bubbles (Oscar Capraro), Emojis (Anumitha Apollo), Sticky Notes (ferminrp), + icon set.
- Same bundle format as the existing 4 `.excalidrawlib` files already in `references/libraries/`.
