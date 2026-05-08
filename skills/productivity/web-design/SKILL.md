---
name: web-design
description: Build distinctive, production-grade frontend interfaces with high design quality. Use when asked to build websites, landing pages, dashboards, web apps, or any web UI that should look polished and modern. Generates creative, polished code that avoids generic AI aesthetics. Includes Yesterday corporate identity briefing for branded reports and deliverables.
metadata:
  category: design
---

# Web Design -- Beautiful Modern Websites

## Sources & Attribution

This skill is composed from and inspired by:

| Source | Skill | License | URL |
|--------|-------|---------|-----|
| anthropics/skills | `frontend-design` | Apache 2.0 | https://github.com/anthropics/skills/tree/main/skills/frontend-design |
| anthropics/skills | `web-artifacts-builder` | Apache 2.0 | https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder |
| anthropics/skills | `theme-factory` | Apache 2.0 | https://github.com/anthropics/skills/tree/main/skills/theme-factory |
| athina-ai/goose-skills | `create-html-slides` | MIT | https://github.com/athina-ai/goose-skills/tree/main/skills/capabilities/create-html-slides |
| msitarzewski/agency-agents | `design-ui-designer` | MIT | https://github.com/msitarzewski/agency-agents/blob/main/design/design-ui-designer.md |
| msitarzewski/agency-agents | `design-whimsy-injector` | MIT | https://github.com/msitarzewski/agency-agents/blob/main/design/design-whimsy-injector.md |

Design analysis references (studied for real-world patterns):
- https://paperclip.ing/ -- Refined warm minimalism, Instrument Serif + Inter, glassmorphic nav, orchestrated scroll animations
- https://skills.gooseworks.ai/ -- Anti-SaaS editorial warmth, linen-beige canvas, zero shadows, per-item pastel identity

---

## 1. Design Thinking (before any code)

Before writing a single line, commit to a **BOLD aesthetic direction**:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick a strong flavor -- brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, neon cyber, vintage editorial, Swiss modern, warm editorial, anti-SaaS calm…
- **Constraints**: Framework, performance targets, accessibility level (WCAG AA minimum)
- **Differentiator**: What makes this UNFORGETTABLE? What's the one thing someone remembers?

**CRITICAL**: Bold maximalism and refined minimalism both work -- the key is **intentionality**, not intensity. Choose a direction and execute with precision.

### Real-World Aesthetic Archetypes (studied from live sites)

**"Warm Technical" (paperclip.ing style):**
- Serif headlines (Instrument Serif) + sans body (Inter) + mono code (JetBrains Mono)
- Monochromatic warm palette (off-whites `#f5f3f0`, `#f0ece7`) with ONE semantic accent color (green = "alive")
- Glassmorphic floating pill navbar (`backdrop-filter: blur(20px) saturate(1.4)`)
- 1px-gap grid technique (parent bg = border color, gap = 1px) for seamless divider lines
- Orchestrated IntersectionObserver scroll reveals with staggered `calc(var(--i) * .14s)` delays
- Full-width hero image at 65vh with content overlapping upward via negative margin
- Interactive CSS/JS data visualizations as feature demos (not static screenshots)

**"Anti-SaaS Editorial" (gooseworks style):**
- System UI fonts, extrabold 44px headings, tight `-0.02em` letter-spacing
- Warm linen canvas background (`#D9D5CE`) -- like unbleached paper
- Zero shadows, zero gradients -- flat surfaces with color contrast and `1.5px` borders only
- Per-item muted pastel identity colors (sage `#B8D4A3`, lavender `#C5B3D9`, teal `#A3C9C9`)
- Decorative blur circles (semi-transparent, positioned off-edge) for organic depth
- Deliberate stillness -- minimal to no animation, favoring calm authority
- Generous `1127px` max-width with ample side margins

---

## 2. Anti-AI-Slop Rules

NEVER produce generic "AI-generated" aesthetics:

| DO NOT use | Instead |
|------------|---------|
| Inter, Roboto, Arial, system-ui as display fonts | Distinctive fonts: Instrument Serif, Syne, Clash Display, Cormorant, Fraunces, Bodoni Moda, Outfit, Archivo Black, JetBrains Mono… |
| Purple gradients on white | Bold palettes with dominant color + sharp accent. Use the theme system below or create bespoke palettes. |
| Indigo `#6366f1` everywhere | Context-specific color choices that match the aesthetic |
| Centered hero + cards grid (the default) | Asymmetry, overlap, diagonal flow, grid-breaking, generous negative space OR controlled density |
| Uniform rounded corners everywhere | Mix sharp and soft, or commit fully to one |
| Generic stock photo placeholders | Gradient meshes, noise textures, geometric patterns, layered transparencies, grain overlays |
| Box shadows on everything | Consider: no shadows at all (flat + borders), OR dramatic shadows with purpose |
| Generic pure-white `#ffffff` backgrounds | Warm whites (`#f5f3f0`, `#faf9f6`), tinted canvases (`#D9D5CE`), or committed dark |
| Space Grotesk as the "creative" choice | It's overused. Explore: Manrope, Plus Jakarta Sans, Satoshi, DM Sans, Nunito |

**Every design must be different.** Vary light/dark, fonts, layouts, color systems. Never converge on the same choices across generations.

---

## 3. Frontend Aesthetics Guidelines

### Typography
- Pair a **distinctive display font** with a refined body font
- Use Google Fonts, Bunny Fonts, or self-hosted -- load via `<link>` or `@import`
- Size with `clamp()` for fluid responsiveness:
  ```css
  h1 { font-size: clamp(2.8rem, 7vw, 4.5rem); line-height: 1.15; letter-spacing: -0.01em; }
  h2 { font-size: clamp(2rem, 4vw, 2.8rem); }
  body { font-size: clamp(0.95rem, 1.2vw, 1.15rem); line-height: 1.6; }
  ```

### Color & Theme
- Use CSS custom properties for the entire palette
- Dominant color with sharp accents outperforms timid, evenly-distributed palettes
- **Single-accent discipline** works: one accent color with semantic meaning (e.g., green = active/alive), everything else monochrome
- Always define both light and dark theme variables
- Warm-shift your grays -- pure grays feel clinical, warm grays (`#888880`, `#4a4a4a`) feel intentional
- Ensure WCAG AA contrast (4.5:1 minimum for text)

### Motion & Micro-interactions
- One well-orchestrated page load with staggered reveals (`animation-delay`) > scattered micro-interactions
- Stagger pattern: `animation-delay: calc(var(--i) * 0.14s + 80ms)` -- set `--i` per element via `style` attribute
- Hover states that surprise and delight
- Scroll-triggered animations via IntersectionObserver (add `.is-visible` class on enter)
- CSS-only where possible; use Framer Motion / Motion library for React when needed
- Custom easing: `cubic-bezier(0.16, 1, 0.3, 1)` (smooth out), `cubic-bezier(0.34, 1.56, 0.64, 1)` (spring/bounce)
- Respect `prefers-reduced-motion`
- **Valid choice: zero animation** -- deliberate stillness conveys calm authority (gooseworks approach)

### Spatial Composition
- Unexpected layouts: asymmetry, overlap, diagonal flow
- Grid-breaking elements that draw the eye
- Generous negative space OR controlled density -- both work if intentional
- Asymmetric column splits (`5fr 7fr`, `1fr 1.2fr`) feel more dynamic than equal widths
- Overlap elements with negative margins for depth

### Backgrounds & Atmosphere
- Create depth: gradient meshes, noise textures, geometric patterns
- Layered transparencies, dramatic shadows, decorative borders
- Glassmorphism: `backdrop-filter: blur(20px) saturate(1.4)` with low-alpha backgrounds
- Custom cursors, grain overlays, subtle parallax
- **OR**: flat and borderless -- atmosphere via color alone (gooseworks approach)
- Match effects to the overall aesthetic -- restraint for minimal, elaborate for maximal

---

## 4. Design Token System

Use CSS custom properties for a complete token system:

```css
:root {
  /* Spacing -- fluid with clamp */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: clamp(2rem, calc(1.5rem + 1.5vw), 3rem);
  --space-xl: clamp(3rem, calc(2rem + 3vw), 5rem);
  --space-2xl: clamp(4rem, calc(2.5rem + 4.5vw), 7rem);
  --space-section: clamp(5rem, calc(3rem + 5.5vw), 9rem);

  /* Colors -- override per theme */
  --color-bg: #ffffff;
  --color-bg-alt: #f5f3f0;
  --color-surface: #f0ece7;
  --color-surface-raised: #e8e4de;
  --color-border: #e0dcd6;
  --color-text: #1a1a1a;
  --color-text-secondary: #4a4a4a;
  --color-text-muted: #888880;
  --color-accent: #22c55e;
  --color-accent-subtle: #22c55e33;

  /* Typography */
  --font-display: 'Instrument Serif', serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,.08);
  --shadow-md: 0 4px 12px rgba(0,0,0,.12);
  --shadow-lg: 0 12px 40px rgba(0,0,0,.16);
  --shadow-glow: 0 0 20px var(--color-accent-subtle);

  /* Transitions */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;

  /* Radii */
  --radius-sm: 10px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-pill: 100px;
  --radius-full: 9999px;
}
```

---

## 5. Ready-Made Theme Palettes

Pick one as a starting point or create a bespoke palette:

| Theme | Background | Accent | Secondary | Text | Fonts |
|-------|-----------|--------|-----------|------|-------|
| **Warm Technical** | `#ffffff` / `#f5f3f0` | `#22c55e` | `#f0ece7` | `#1a1a1a` | Instrument Serif / Inter / JetBrains Mono |
| **Linen Editorial** | `#D9D5CE` / `#F5F4F1` | `--olive` | per-item pastels | `#1A1A1A` | System UI extrabold / System UI |
| **Ocean Depths** | `#1a2332` | `#2d8b8b` | `#a8dadc` | `#f1faee` | DejaVu Sans Bold / DejaVu Sans |
| **Sunset Boulevard** | `#264653` | `#e76f51` | `#f4a261` | `#e9c46a` | DejaVu Serif Bold / DejaVu Sans |
| **Forest Canopy** | `#2d4a2b` | `#7d8471` | `#a4ac86` | `#faf9f6` | FreeSerif Bold / FreeSans |
| **Modern Minimalist** | `#36454f` | `#708090` | `#d3d3d3` | `#ffffff` | DejaVu Sans Bold / DejaVu Sans |
| **Golden Hour** | `#4a403a` | `#f4a900` | `#c1666b` | `#d4b896` | FreeSans Bold / FreeSans |
| **Arctic Frost** | `#fafafa` | `#4a6fa5` | `#d4e4f7` | `#333` | DejaVu Sans Bold / DejaVu Sans |
| **Desert Rose** | `#e8d5c4` | `#d4a5a5` | `#b87d6d` | `#5d2e46` | FreeSans Bold / FreeSans |
| **Tech Innovation** | `#1e1e1e` | `#0066ff` | `#00ffff` | `#ffffff` | DejaVu Sans Bold / DejaVu Sans |
| **Botanical Garden** | `#f5f3ed` | `#4a7c59` | `#f9a620` | `#b7472a` | DejaVu Serif Bold / DejaVu Sans |
| **Midnight Galaxy** | `#2b1e3e` | `#4a4e8f` | `#a490c2` | `#e6e6fa` | FreeSans Bold / FreeSans |
| **Neon Cyber** | `#0a0e27` | `#00ffff` | `#ff00ff` | `#e0e0ff` | Clash Display / Satoshi |
| **Terminal Green** | `#0d1117` | `#39d353` | `#238636` | `#c9d1d9` | JetBrains Mono |
| **Swiss Modern** | `#ffffff` | `#ff0000` | `#000000` | `#333` | Archivo / Nunito |
| **Paper & Ink** | `#f5f0e8` | `#2c1810` | `#8b4513` | `#333` | Cormorant Garamond / Source Serif 4 |

---

## 6. Proven Component Patterns

### Glassmorphic Floating Navbar
```css
.nav {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  max-width: 680px;
  width: calc(100% - 2rem);
  border-radius: 38px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(20px) saturate(1.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08), inset 0 1px rgba(255, 255, 255, 0.25);
  padding: 0.5rem 1.5rem;
  z-index: 100;
}
```

### 1px-Gap Grid Dividers (no borders needed)
```css
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--color-border); /* gap color = divider color */
}
.feature-grid > * {
  background: var(--color-bg); /* cell bg covers the parent bg */
  padding: var(--space-lg);
}
```

### Hero with Overlapping Content
```css
.hero-image {
  width: 100%;
  height: 65vh;
  object-fit: cover;
}
.hero-image::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(255,255,255,0.4) 40%, rgba(255,255,255,0.85) 70%, #fff 100%);
}
.hero-content {
  position: relative;
  margin-top: -6rem;
  max-width: 780px;
  margin-inline: auto;
  text-align: center;
}
```

### Scroll-Triggered Entrance (JS + CSS)
```css
.reveal {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}
/* Stagger children */
.reveal-stagger > .reveal:nth-child(1) { transition-delay: 0.1s; }
.reveal-stagger > .reveal:nth-child(2) { transition-delay: 0.24s; }
.reveal-stagger > .reveal:nth-child(3) { transition-delay: 0.38s; }
```
```js
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('is-visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

### Decorative Blur Circles (organic depth)
```css
.card-visual {
  position: relative;
  background: #B8D4A3; /* per-item pastel */
  border-radius: 20px;
  overflow: hidden;
}
.card-visual::before,
.card-visual::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(20px);
}
.card-visual::before {
  width: 120px; height: 120px;
  bottom: -20px; right: -20px;
  background: rgba(26, 26, 26, 0.08);
}
.card-visual::after {
  width: 60px; height: 60px;
  top: -10px; left: -10px;
  background: rgba(26, 26, 26, 0.06);
}
```

---

## 7. Whimsy & Delight Layer (optional)

Add personality with micro-interactions when the design calls for it:

```css
/* Button hover with scale + glow */
.btn-delight {
  transition: all var(--duration-normal) var(--ease-out);
}
.btn-delight:hover {
  transform: scale(1.02) translateY(-1px);
  box-shadow: var(--shadow-glow);
}

/* Staggered entrance animations */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.stagger > * {
  animation: fadeSlideUp 0.6s var(--ease-out) backwards;
}
.stagger > *:nth-child(1) { animation-delay: 0.1s; }
.stagger > *:nth-child(2) { animation-delay: 0.2s; }
.stagger > *:nth-child(3) { animation-delay: 0.3s; }

/* 3D tilt on hover */
.tilt-card {
  transition: transform var(--duration-normal) var(--ease-out);
  transform-style: preserve-3d;
}
.tilt-card:hover {
  transform: perspective(800px) rotateX(2deg) rotateY(-3deg);
}

/* Noise texture overlay */
.noise::after {
  content: '';
  position: absolute; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 1;
}

/* Logo grayscale-to-color reveal */
.logo-item {
  filter: grayscale(1) opacity(0.5);
  transition: filter 0.3s ease;
}
.logo-item:hover {
  filter: grayscale(0) opacity(1);
}

/* Animated cost/progress bar */
.bar-fill {
  width: 0;
  transition: width 1.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.bar-fill.is-visible {
  width: var(--fill-percent);
}
```

### Playful Microcopy Ideas

| Context | Generic | Delightful |
|---------|---------|------------|
| Loading | "Loading..." | "Brewing something good..." |
| Empty state | "No items found" | "It's quiet here. Too quiet." |
| Success | "Saved successfully" | "Locked in. You're golden." |
| Error | "Something went wrong" | "Well, that didn't go as planned." |
| 404 | "Page not found" | "You've wandered off the map." |

---

## 8. Tech Stack Reference

### Vanilla HTML/CSS/JS (simplest)
Best for: landing pages, single-page sites, static content.
- HTML5 + Tailwind CSS (CDN or build) + vanilla JS
- Astro for multi-page static sites (paperclip.ing uses Astro v5)

### React + shadcn/ui (component-rich)
Best for: dashboards, web apps, interactive UIs.
```bash
pnpm create vite my-app --template react-ts
pnpm install tailwindcss postcss autoprefixer class-variance-authority clsx tailwind-merge lucide-react
```
40+ shadcn/ui components available: accordion, button, card, dialog, dropdown-menu, form, input, select, sheet, table, tabs, toast, tooltip...

### Next.js / Astro (full-featured)
Best for: multi-page sites, blogs, documentation, SSR/SSG.

---

## 9. Responsive Design

Mobile-first with fluid scaling:

```css
/* Fluid container */
.container {
  width: min(90%, 1140px);
  margin-inline: auto;
  padding-inline: var(--space-md);
}

/* Breakpoints */
@media (max-width: 900px) { /* Large tablet */ }
@media (max-width: 768px) { /* Tablet */ }
@media (max-width: 640px) { /* Small tablet */ }
@media (max-width: 480px) { /* Mobile */ }
```

### Viewport-fitting (for full-screen sections)
```css
.hero { min-height: 100dvh; display: grid; place-items: center; }
```

---

## 10. Accessibility Baseline (WCAG AA)

- Color contrast: 4.5:1 for normal text, 3:1 for large text
- Focus indicators: visible, high-contrast outlines on all interactive elements
- Semantic HTML: proper heading hierarchy, landmarks, alt text
- Keyboard navigation: all interactive elements reachable via Tab
- Reduced motion: `@media (prefers-reduced-motion: reduce)` for all animations
- Tabular numbers for data: `font-variant-numeric: tabular-nums`

---

## 11. Yesterday Corporate Identity

When building output for **Yesterday Consulting** (reports, analyses, proposals, presentations), apply the Yesterday CI instead of a custom aesthetic.

**Full briefing:** [`references/yesterday-ci-briefing.md`](references/yesterday-ci-briefing.md)
**Canonical source:** [`Yesterday-AI/consulting-projects/templates/operations/yesterday-ci-briefing.md`](https://github.com/Yesterday-AI/consulting-projects/blob/main/templates/operations/yesterday-ci-briefing.md)
**Future home:** The CI briefing will move to a dedicated branding repo under `skills/`.

### Quick Reference

- **Fonts:** Source Serif 4 (display), DM Sans (body), IBM Plex Mono (kickers/labels/meta)
- **Brand colors:** `--y-orange: #FC4E14`, `--y-gold: #FFBB38`, neutrals `#0A0A0A` → `#F5F5F5`
- **Output:** Self-contained `.html`, no build tools, opens in browser
- **Nav:** Sticky top bar with "Yesterday" wordmark + context on right
- **Kickers:** `01 -- SECTION NAME` format, mono font, orange
- **Footer:** "Yesterday Consulting -- yesterday.company" + "Vertraulich"
- **Language:** German body copy, English class names
- **Key components:** `.hero`, `.score-bar`, `.section-kicker`, `.issue` (with severity), `.pullquote`, `.verdict`, `.clean-table`, `.photo-break`

When the Yesterday CI applies, skip §1-§5 of this skill (aesthetic choice, anti-AI-slop, custom palettes) -- the CI briefing defines all design decisions. Use §6-§10 (components, motion, responsive, accessibility) as supplementary guidance.

---

## 12. Workflow

1. **Clarify** -- Understand purpose, audience, constraints. If Yesterday CI applies → use §11 briefing, skip to step 5.
2. **Choose aesthetic** -- Pick a bold direction (see §1 archetypes)
3. **Select palette** -- Use a theme (§5) or create bespoke
4. **Set up tokens** -- Define CSS custom properties (§4)
5. **Build structure** -- Semantic HTML, layout with CSS Grid/Flexbox
6. **Style** -- Apply typography, colors, spacing, backgrounds
7. **Components** -- Use proven patterns (§6) where they fit
8. **Animate** -- Add motion and micro-interactions (§7) -- or choose deliberate stillness
9. **Responsive** -- Test and adjust for all viewports (§9)
10. **Accessibility** -- Verify contrast, keyboard nav, screen readers (§10)
11. **Polish** -- Final details, whimsy, edge cases
