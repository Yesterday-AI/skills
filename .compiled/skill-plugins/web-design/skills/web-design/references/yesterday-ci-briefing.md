# Yesterday CI Briefing — For AI Agents

> Use this briefing when you need to transform generic content (reports, analyses,
> presentations, proposals) into Yesterday Consulting brand output.
> You have access to the repos and Figma. Here is exactly where to look.

---

## 1. What You Are Doing

You are applying the Yesterday Consulting corporate identity to a piece of content.
"Generic content" means: raw markdown, plain HTML, a Word doc, a transcript, or any
unbranded material. The output is always a self-contained `.html` file — no build tools,
no frameworks, just one file that opens in a browser.

---

## 2. The Design System (CSS Variables + Fonts)

Copy this verbatim into every new HTML file's `<style>` block:

```css
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  /* Brand Colors */
  --y-orange: #FC4E14;
  --y-orange-light: #FFD8CB;
  --y-gold: #FFBB38;
  --y-gold-light: #FFECB9;

  /* Neutrals */
  --y-black: #0A0A0A;
  --y-gray-900: #1A1A1A;
  --y-gray-600: #737373;
  --y-gray-400: #8C8C8C;
  --y-gray-200: #E5E5E5;
  --y-gray-100: #F5F5F5;
  --y-white: #FFFFFF;

  /* Semantic */
  --y-green: #1B7340;    --y-green-bg: #E6F4EC;
  --y-red: #C43D2E;      --y-red-bg: #FCEAE7;
  --y-amber: #92610F;    --y-amber-bg: #FFF4E0;
  --y-blue: #2563EB;     --y-blue-bg: #EFF6FF;

  /* Typography */
  --font-display: 'Source Serif 4', Georgia, serif;   /* Headlines */
  --font-body: 'DM Sans', system-ui, sans-serif;      /* Body text */
  --font-mono: 'IBM Plex Mono', monospace;            /* Labels, kickers, meta */
}
```

**Typography rules:**

- `var(--font-display)` → section titles, hero H1, pull quotes, big numbers
- `var(--font-body)` → all body copy, nav, navigation
- `var(--font-mono)` → kickers (`01 — SECTION`), labels, badges, meta info, timestamps
- Orange (`--y-orange`) → accent, kicker color, hero span, hover states
- Never use color outside this palette. No custom colors per client.

---

## 3. The Reference Template

**File:** `consulting-projects/01-clients/01-maytoni/phase-2/units/praesi/example-html.html`

This is the canonical Yesterday HTML template. Read this file before building anything.
It contains the full CSS component library:

| Component class | Use for |
|---|---|
| `.hero` | Title + image grid at the top |
| `.hero-kicker` | Orange mono label above title |
| `.score-bar` | 5-column metric strip |
| `.meta-strip` | Date / author / context metadata |
| `.section` | Each major content block |
| `.section-kicker` | `01 — SECTION NAME` label |
| `.section-title` | Display font section header |
| `.two-col` | 50/50 content grid |
| `.prose` | Long-form body text |
| `.issue` | Finding/problem with severity (`.critical`, `.high`, `.medium`) |
| `.issue-priority` | Badge inside `.issue` |
| `.pullquote` | Editorial quote with orange left border |
| `.photo-break` | Full-width image break between sections |
| `.clean-table` | Data table with mono headers |
| `.fit-grid` | Before/after comparison grid |
| `.feat` | Numbered feature/recommendation row |
| `.feat-badge` | Priority badge (`.quick`, `.mid`, `.strategic`) |
| `.verdict` | Closing summary box with orange accent |
| `footer` | Yesterday branding + mono metadata |
| `nav` | Sticky top bar with "Yesterday" wordmark |

**Nav pattern:**

```html
<nav>
  <div class="nav-brand">Yesterday</div>
  <div class="nav-right">Report Type / Client / Monat Jahr</div>
</nav>
```

**Footer pattern:**

```html
<footer>
  <span>Yesterday Consulting — yesterday.company</span>
  <span>Vertraulich · Nur für interne Verwendung</span>
</footer>
```

---

## 4. Stock Pictures

**Folder:** `consulting-projects/01-clients/01-maytoni/phase-2/units/praesi/stock-pictures/`

Contains ~70 PNG images exported from Figma. These are Yesterday-approved visuals:
business contexts, people working, team collaboration, workspace shots.

**When to use:** Hero images, photo breaks between sections, sidebar visuals.

**How to reference them in HTML:** Use a relative path or embed via `<img src="...">`.
If the output HTML lives in a different folder, copy the needed images there or use
absolute paths during development.

**Naming:** Files are named `image NNN.png` and `Group NN.png`. Open a few in the IDE
to pick visually — there is no semantic index. Prefer images with people or office
context for business reports. Prefer abstract/tech shots for analysis reports.

Also available:

- `consulting-projects/01-clients/01-maytoni/phase-2/units/praesi/hero.png` — generic hero image used in the ADN example
- `consulting-projects/01-clients/bvb/1-phase/fotos/` — BVB workshop photos (client-specific, only for BVB)

---

## 5. Figma Access (MCP)

You have the Figma MCP server active: `plugin-figma-figma`

**When to use Figma:**

- The user shares a Figma URL → use `get_design_context` immediately
- You need to match a visual component exactly → use `get_screenshot`
- You are unsure about spacing, colors, or structure from a Figma file → use `get_metadata`

**URL parsing:**

- `figma.com/design/:fileKey/...?node-id=:nodeId` → extract `fileKey` and `nodeId`
- Convert `-` to `:` in the `nodeId` before calling the MCP

**Key tools:**

- `get_design_context(fileKey, nodeId)` → returns code + screenshot + design tokens
- `get_screenshot(fileKey, nodeId)` → returns rendered image of the node
- `get_metadata(fileKey)` → returns file structure

The Figma output is a reference, not final code. Always adapt to the Yesterday CSS
system defined above — do not copy Figma-generated CSS directly.

---

## 6. Existing Reports to Learn From

Read these before building a new report — they show the pattern in practice:

| File | What it demonstrates |
|---|---|
| `01-clients/01-maytoni/phase-2/units/praesi/ergebnisreport-phase2.html` | Full phase report with photo breaks, findings, verdict |
| `01-clients/02-adn/1-phase-klaerungsphase/4-angebots-erarbeitung/application/public/adn-website-analyse-2026-03.html` | Website analysis with score bar, issues, recommendations |
| `01-clients/01-maytoni/phase-3/ausblick-phase3.html` | Shorter outlook document |
| `01-clients/02-adn/1-phase-klaerungsphase/3-proposal-zusammenarbeit/index.html` | Proposal / collaboration pitch |

---

## 7. Build Checklist

Before handing off a finished HTML file:

- [ ] All CSS variables use `--y-*` naming — no hardcoded hex colors outside `:root`
- [ ] Three fonts in use: display / body / mono — no others
- [ ] Nav present with "Yesterday" wordmark + context on right
- [ ] At least one `hero-kicker` in orange mono above every major title
- [ ] Section kickers follow pattern: `01 — SECTION NAME` (mono, orange)
- [ ] Footer present with "Yesterday Consulting" and "Vertraulich" note
- [ ] At least one stock photo or hero image (from the stock-pictures folder)
- [ ] File is self-contained (no external JS, no build step, opens in browser)
- [ ] Language: German body copy, English class names and code
- [ ] No generic AI output patterns: no emoji bullets, no `**Bold:**` in rendered text,
      no "In conclusion" paragraphs, no lists of 7+ identical items

---

## 8. Tone & Content Rules

- **Kicker labels:** always `NN — UPPERCASE GERMAN` format, e.g. `01 — EXECUTIVE SUMMARY`
- **Headlines:** opinionated, concrete — not "Analyse der Website" but "780 Mio. Euro Substanz. Null auf der Website."
- **Pull quotes:** use real quotes from transcripts or sharpen a key insight into a provocative one-liner
- **Numbers:** always displayed in `var(--font-display)` at large size when they are KPIs
- **Severity badges:** use `.critical` / `.high` / `.medium` — never invent new colors
- **The verdict section:** always close with a `.verdict` block that summarizes the "so what"
