---
name: yesterday-pages
description: Use when Markdown, research, concepts, analyses, offers, image folders, or mechanisms need to become a branded Yesterday HTML page, visual report, whitepaper, visual story, data narrative, interactive explainer, or lightweight prototype.
---

# Yesterday Pages

## Principle

Choose the form from the message. Build one clear information experience, not a decorated document.

Read [brand.md](references/brand.md) before designing. Use `assets/foundation.css` as the token source; take only the rules the output needs.

## Autonomy

Complete the work in one run: specify, review, decide, build, render, revise, deliver.

Do not ask the user to select a type, approve an outline, choose an interaction, or review a draft. Infer those decisions from audience, material, and outcome. If input is incomplete, proceed with stated assumptions and disclose unavailable sources in the handoff.

## Route

Select one leading type. A page may borrow supporting patterns, but must keep one dominant reading mode and one signature interaction.

| Type | Choose when | Read exactly this reference |
|---|---|---|
| Editorial / Whitepaper | Evidence, argument, comparison, research, analysis, offer | [editorial.html](references/editorial.html) |
| Visual Story | Supplied images carry part of the argument | [visual-story.html](references/visual-story.html) |
| Interactive Explainer / Prototype | Understanding improves through changing state or trying a mechanism | [interactive-explainer.html](references/interactive-explainer.html) |

References demonstrate composition and behavior. Do not clone their page structure or sample content.

## Workflow

1. Inspect every supplied source. For image folders, inventory subject, orientation, visual weight, negative space, and semantic fit.
2. Write a compact internal brief: audience, single thesis, desired action, evidence hierarchy, leading type, signature interaction.
3. Review the brief against source and audience; decide, then outline the scan path. Remove repetition and unsupported claims. Preserve links and uncertainty.
4. Build semantic HTML with inline CSS and vanilla JavaScript. Default to one responsive `.html` file; keep supplied images in a relative asset folder. Use the official wordmark from `assets/yesterday-wordmark.svg`.
5. For data, choose the chart from the claim. Prefer accessible inline SVG, direct labels, `<title>`, `<desc>`, and a visible takeaway. Interaction may reveal detail, never the core finding.
6. Use motion only for sequence, causality, change, or state. Support `prefers-reduced-motion`. Make every control keyboard-operable and visibly focused.
7. Render, inspect, and revise using [quality.md](references/quality.md). Deliver only the finished artifact and a concise handoff.

## Output Contract

- Open with a thesis, not a generic welcome.
- Let one accent color lead; use other brand colors only to encode meaning.
- Keep editorial text readable, app text compact, and labels literal.
- Use one memorable interaction. Every other interaction must be functional.
- Never invent facts, sources, quotes, metrics, client claims, or image meaning.
- Include print styles for editorial, analysis, and offer outputs.

## Common Mistakes

- Reusing the same hero, card grid, or section rhythm for every page.
- Treating every image in a folder as mandatory.
- Hiding the main conclusion behind hover or animation.
- Shipping untested mobile layouts, broken paths, or decorative controls.

## Privacy

Use only material authorized for the intended audience. Keep real people, customer details and private source text out of reusable templates. The bundled HTML uses illustrative content. Do not add analytics, tracking pixels or remote fonts. Rendering and publishing are separate actions; publishing requires the user’s instruction. Resolve reference paths relative to this skill.
