---
milestone: M002
slice: S01
project: skills
created: 2026-05-21T10:06:28Z
status: planned
task_count: 3
completed_tasks: 0
---

# M002-S01 -- Slice Plan

**Goal:** Make the premium visual style selectable as an explicit opt-in (warm-cream
background, 6-hue state-coded pastel palette, hand-drawn font, roughness:1), while
the skill's existing defaults (mono font, roughness 0, white bg, container
discipline) stay exactly as they are when premium mode is not selected.

## Tasks

- [ ] T01 -- Verify which `fontFamily` IDs the renderer actually supports: inspect `references/render_excalidraw.py` + `references/render_template.html`, render a tiny probe `.excalidraw` per candidate hand-drawn font (Virgil / Excalifont / Nunito), view the PNGs, and document the verified hand-drawn `fontFamily` ID. Gating: a font the renderer can't load silently falls back, killing the look.
- [ ] T02 -- Rewrite `references/color-palette.md`: add a clearly separated "Premium Infographic palette" section (cream bg `#F7F3E9`; 6-hue state-coded fill/stroke pastels with the measured values: blue `#D3EBF7`/`#2F6FA8`, mint `#C2E7B0`/`#4E8C3F`, lavender `#D2B9DE`/`#7B5BA6`, coral `#F9BC9E`/`#C75A3A`, butter `#FCEDCE`/`#B5872B`, neutral `#ECECE8`/`#8A8A82`; charcoal `#1F1F1F` hand-drawn outline option; light code-pill replacing the dark block) -- keep the existing Yesterday palette intact as the default section.
- [ ] T03 -- Add a "Premium Infographic mode (opt-in)" switch to `SKILL.md` that, when selected, sets hand-drawn font + `roughness: 1` + cream bg + premium palette, and explicitly states the default behavior is unchanged otherwise. Resolve the open question on the selection mechanism (dedicated SKILL.md section vs reference doc) here.

## Done when

All tasks marked `[x]` and verified via `ytstack:summarize-task`.

## Notes

- Open question (from M002-CONTEXT): selection mechanism + verified font ID land here.
- Reference corpus + measured palette: `/tmp/ddods/`.
