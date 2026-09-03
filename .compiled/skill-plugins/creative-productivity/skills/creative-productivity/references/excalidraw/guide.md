# Excalidraw Diagram Guide

For the full methodology, render pipeline, and element templates, see the dedicated Excalidraw skill:
- **Source:** [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill)

This file summarizes the key principles. Install the full skill for render validation.

## Core Philosophy

**Diagrams should ARGUE, not DISPLAY.** The shape should BE the meaning.

- **Isomorphism Test:** Remove all text — does the structure alone communicate the concept?
- **Education Test:** Could someone learn something concrete, or does it just label boxes?

## Visual Patterns

| Concept | Pattern |
|---------|---------|
| One-to-many (source, hub) | Fan-out (radial arrows) |
| Many-to-one (aggregation) | Convergence (funnel) |
| Hierarchy | Tree (lines + free text) |
| Sequence | Timeline (line + dots + labels) |
| Feedback loop | Spiral/cycle |
| Abstract state | Cloud (overlapping ellipses) |
| Transformation | Assembly line (before → process → after) |
| Comparison | Side-by-side parallel |

## Key Rules

1. **Default to free-floating text.** Only add containers when the shape carries meaning.
2. **Each concept gets a different visual pattern.** No uniform card grids.
3. **Color encodes meaning, not decoration.** Use the color palette consistently.
4. **Evidence artifacts** (code snippets, JSON, real data) make technical diagrams educational.
5. **Build large diagrams section by section** — never generate all JSON in one pass.
6. **Always render and validate** — JSON previews lie. Use the Playwright render pipeline.

## Quick JSON Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 },
  "files": {}
}
```

## Setup

```bash
cd references/excalidraw && uv sync && uv run playwright install chromium
```

## Render

```bash
uv run python render_excalidraw.py <path-to-file.excalidraw>
```

Then visually inspect the PNG. Fix issues. Repeat until clean.
