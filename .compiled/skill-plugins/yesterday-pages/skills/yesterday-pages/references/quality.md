# Quality Gate

Run this gate after the first render, revise, then run it again.

## Source Integrity

- Every factual claim, quote, number, and source is traceable to supplied material.
- Uncertainty stays visible; missing evidence is not disguised with copy.
- Selected images add information and have accurate captions or alt text.

## Information Design

- The thesis is clear in the first viewport.
- The reading order works without motion or interaction.
- Each section advances the argument; repeated points are removed.
- Charts state a takeaway and remain understandable without hover.

## Interface

- Landmarks and heading levels are semantic.
- Controls work by keyboard, show focus, and have literal labels.
- Color is never the only state signal.
- `prefers-reduced-motion` preserves meaning and end states.
- Empty, default, changed, and reset states behave deliberately.

## Rendering

- Inspect at desktop and mobile widths; test one narrow width at or below `390px`.
- Check for horizontal overflow, clipped labels, broken paths, awkward crops, and unreadable lines.
- Check browser console errors and every interactive path.
- Verify print/PDF output when the page is editorial, analytical, or an offer.

## Visual Review

- Compare the render with the brief, not with the reference HTML.
- Remove one unnecessary effect, badge, card, or accent.
- Confirm the result feels specifically Yesterday and specifically about this subject.
- Capture final desktop and mobile screenshots before declaring completion.
