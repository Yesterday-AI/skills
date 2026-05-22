---
milestone: M002
slice: S02
project: skills
created: 2026-05-21T10:06:28Z
status: planned
task_count: 3
completed_tasks: 0
---

# M002-S02 -- Slice Plan

**Goal:** Document the reusable premium "signature elements" with copy-paste JSON
templates and adopt robust sizing formulas, so an agent can assemble DDoDS-style
components without redrawing from scratch or producing text overflow.

## Tasks

- [ ] T01 -- Add a "Premium Signature Elements" section to `SKILL.md` cataloguing each device with when/why + a short visual description: title pill, highlighter swipe behind free text, mascot/narrator figure, speech & thought bubble, mandatory bottom-summary thesis sentence, sparing emoji accents, inline icons in pills, dashed=pending/grouping, numbered cycle (1..n on arrows), 2x2 quadrant map with axes, side-by-side panel with good/bad colored glow.
- [ ] T02 -- Add copy-paste JSON templates for the new elements to `references/element-templates.md`: title pill (filled rounded-rect + centered hand-drawn text), highlighter-swipe (thin filled rounded-rect behind text), speech bubble, bottom-summary text block, numbered-step marker, dashed callout box. Pull colors from the premium palette section.
- [ ] T03 -- Adopt the opencoredev sizing formulas into the premium guidance (`SKILL.md` + `element-templates.md`): `max(160, charCount*11+40)` width, per-line height (60/80/100), >=80px arrow gap, >=20px inner padding. Reconcile with the existing glyph-width estimation so the two don't contradict.

## Done when

All tasks marked `[x]` and verified via `ytstack:summarize-task`.

## Notes

- Depends on S01 palette section existing (templates reference premium colors).
- Sizing formulas sourced from opencoredev/excalidraw-cli (MIT).
