---
name: yesterday-app-style
description: Build or review Yesterday Academy app prototypes and features in the calm, clear, quietly confident product style. Use when a UI should feel like the Yesterday app rather than a generic AI dashboard.
metadata:
  short-description: Yesterday Academy visual and interaction language
---

# Yesterday App Style

Use this skill whenever you build, redesign, review, or prototype a Yesterday Academy app surface. It is the compact working memory for the design files: apply these rules directly instead of making the next agent rediscover the design system.

The desired feeling is **ruhig, einfach, aufgeräumt, professionell und warm**. The interface should create orientation and trust. Motivation may support the work, but never become spectacle. When a choice is unclear, choose the quieter, more explicit, more spacious option.

## Portable design contract

This package contains the visual and interaction rules below and the optional [Kanban pattern](references/kanban.md). It does not require a design repository or private meeting notes. In an existing app, map these roles to its token system and component APIs; do not invent a second set. For a standalone prototype, use the reference values below. This is a style guide, not a complete component implementation library.

Font files are not distributed. Use the named Season faces only when the project supplies properly licensed files; otherwise use Inter or the system sans-serif fallback and disclose that typographic difference. Never fetch trial fonts or assume a font license from the skill.

## The visual contract

### Color

Use tokens in product code. The values below are the reference values when a prototype is standalone.

Light theme:

| Token | Value | Use |
|---|---|---|
| `ink` | `#121a34` | primary text, deep page content |
| `ink-soft` | `#313951` | secondary text |
| `muted` | `#6f778f` | captions, metadata, quiet controls |
| `muted-2` | `#9aa1b4` | tertiary metadata |
| `page` | `#ffffff` | outer canvas |
| `panel` | `#f3f2f0` | content shell and soft grouping |
| `panel-2` | `#eeece9` | recessed fills, avatar/icon backplates |
| `card` | `#ffffff` | raised content surface |
| `line` | `rgba(18,26,52,.10)` | quiet boundaries |
| `line-strong` | `rgba(18,26,52,.18)` | control borders |
| `violet` | `#6652ff` | brand accent, active learning state, links |
| `orange` | `#ff8a2a` | warmth and progress only |
| `success` | `#15803d` on `#ecfdf3` | confirmed/completed |
| `info` | `#1d4ed8` on `#eff6ff` | information |
| `warning` | `#b45309` on `#fffbeb` | caution |
| `error` | `#b91c1c` on `#fef2f2` | error/destructive meaning |

The hero/banner gradient is the deliberate exception to the quiet neutral canvas: `#2a858a → #1f6f74 → #195a5e`. Use it only for a true hero/banner surface.

Dark theme is a token remap, never a second hand-tuned design: page `#17171a`, panel `#1d1d20`, card `#252528`, recessed well `#1a1a1d`, primary text `#f7f7fb`, secondary `#d8dbe5`, muted `#a9adba`, tertiary `#767b89`, lines `rgba(255,255,255,.09)` / `.14`. Every visual token needs a dark override and no layout should shift when the theme changes.

Rules:

- Color never carries meaning alone. Pair status color with text and/or an icon.
- Orange is not a generic status color; reserve it for progress and warmth.
- Violet is an accent and active-state cue, not a reason to tint every surface.
- Prefer surface contrast over borders. Avoid heavy outlines and black frames.
- No indigo/purple AI-dashboard gradients, neon colors, rainbow status systems, or decorative color noise.

### Typography

- UI, labels, navigation, buttons, and forms: **Inter** (`--academy-font-sans`).
- Headlines and titles: **Season Sans-TRIAL** (`--academy-font-heading`).
- Mission-card descriptive copy: **Season Mix-TRIAL** (`--academy-font-mission-body`).
- Code and technical provenance: system monospace.
- Use the scale; do not scatter ad-hoc sizes: display 58/44/33/26px, title 20/17/15px, body 15/13px, caption 12px, micro 11px, button/nav 13px.
- Headlines are restrained: regular or medium weight. The 650 display-sm strong variant is exceptional, not a default.
- Use natural case for badges, tags, chips, and statuses. Uppercase is reserved for a genuine eyebrow or legal footer.
- Copy is direct, concrete, German in the Academy UI, and explicit about what happens next. Avoid marketing hype and unexplained AI language.

### Rhythm, shape, and elevation

Spacing is a 4px rhythm: `4, 8, 12, 16, 20, 24, 32, 36, 48, 64px`. Start with 24px internal breathing room and add space before adding decoration.

- Small control radius: 6px.
- Ordinary card: 10px.
- Medium control: 12px.
- Interactive item/icon container: 14px.
- Large shell: 28px.
- Buttons and segmented controls: pill (`999px`).
- Icon container: 42×42px, 14px radius, 22px glyph.
- Shadows are rare and soft. Use inset highlights or a quiet surface change for ordinary cards. Reserve real elevation for overlays and genuinely raised lead cards.
- Buttons are flat: no button drop shadows.

## Shell and layout

Use the app frame as the default composition:

1. Fixed sidebar, about 240–256px wide; collapsed width 72px. Links have at least 52px height and clear labels.
2. 52px topbar. Glass/blur is allowed only here and must remain quiet.
3. Inset rounded content shell on the page background: panel surface, 28px shell radius, generous padding.
4. Content max width about 1320px; preserve wide margins rather than stretching every module.
5. Legal footer sits outside/below the content shell on standard views.

Design for 375px first-class support. At roughly 821px the sidebar collapses; at 768px the mobile layout takes over. On mobile, stack content, preserve 44px touch targets, keep the primary action discoverable, and allow intentional horizontal scrolling only for genuinely wide data (for example a Kanban board), with a visible explanation.

Use one dominant anchor per view. The first two seconds should answer: **Where am I? What is this? What do I do next?** Do not make the user explore a decorative dashboard to discover the task.

## Component language

Reuse these patterns before creating a new component:

- **App shell / sidebar / topbar:** stable navigation, active state, quiet hover, explicit labels, tooltips for icon-only actions.
- **Page header:** small violet eyebrow when useful, clear Season Sans title, one short orientation sentence, one primary action at most.
- **Hero banner:** colored gradient surface, real or intentional media, inline-right CTA, strong contrast. Do not turn ordinary content into a hero.
- **Session/content shell:** panel background and rounded shell; adjacent panes use surface contrast, not divider walls.
- **Card:** content-type-specific interior. A mission, appointment, feedback item, process, and file must not look identical merely because they are all cards.
- **Interactive item:** violet shimmer/soft gradient token surface, small border, 14px radius, restrained hover lift.
- **Buttons:** near-black solid primary; white/outlined secondary; pill shape; readable minimum width; labels over icon-only controls. Use destructive red only for destructive action.
- **Inputs:** small 6px radius, visible top-aligned/infield label, never placeholder-only labeling; focus hugs the border with the neutral focus ring.
- **Badges:** role/emphasis badges follow button hierarchy; status badges use only the four semantic pairs; natural case; icon/text accompany color.
- **Progress:** orange gradient fill with subtle glow; communicate `Phase x / y — Name` before percentages. Track is quiet and accessible in both themes.
- **Icon containers:** decorated 42px containers for section-level icons; do not scatter bare SVGs as decoration.
- **Chevrons:** the chevron itself is the labelled interactive element with its own hover/focus, not a decorative glyph on a clickable row.
- **Disclosure:** use progressive disclosure for secondary detail. Keep the initial surface short and scannable.
- **Side panel:** use a push drawer for detail inspection when the page context should remain; reserve a modal dialog for an actual interruption or confirmation.
- **Empty, loading, and error states:** explain what is happening and what the user can do. Never leave a blank panel or a spinner without context.
- **Toast/feedback:** factual, brief, non-celebratory. No confetti, gamification chrome, or hero animation.

## Interaction and motion

- Every enabled click target has pointer, hover, focus-visible, and disabled feedback.
- Non-icon actions need visible labels. Icon-only actions need `aria-label` and a tooltip.
- Minimum touch target: 44px.
- Keyboard focus is visible and neutral; do not use a warm accent focus ring.
- Use motion only to explain state change, reveal hierarchy, or preserve spatial continuity. Default easing is `cubic-bezier(.22,1,.36,1)` with 160ms fast, 220ms normal, 360ms medium, 520ms slow.
- Honor `prefers-reduced-motion`; remove transforms and decorative bursts.
- Never animate the whole page for attention. Avoid springy, bouncy, celebratory, or game-like motion.

## Build discipline

Before coding, identify the existing shell, token file, and nearest component. Compose existing pieces before authoring new ones. Keep visual values token-based; no ad-hoc hex, arbitrary spacing, or one-off radii in a per-feature stylesheet.

For a prototype, make the smallest believable slice: real hierarchy, realistic copy, explicit states, light and dark mode, 375px behavior, and one reviewable path. Keep demo data visibly demo data and never imply a production write unless it really exists.

Before calling a surface done, inspect:

- light and dark mode;
- desktop and 375px/mobile width;
- keyboard focus and a screen-reader name for every action;
- empty, loading, error, and success states;
- whether the first view is calm and immediately understandable;
- whether the same component still looks like the same component elsewhere.

## Do not ship

Do not ship centered hero sameness, glassmorphism everywhere, indigo AI gradients, emoji feature grids, excessive pills, heavy borders, button shadows, unexplained icons, percentage-only progress, uppercase status chips, color-only status, placeholder labels, hidden gestures, confetti, or generic “AI assistant” copy.

The test is not whether the screen looks impressive in isolation. The test is whether it feels like a quiet, trustworthy part of Yesterday when placed beside the rest of the app.

## Content privacy

Use fictional demo records unless real data is explicitly authorized for the intended audience. Do not bundle customer records, meeting passages, participant names, private links or screenshots containing personal information. Never treat a design example as evidence from real workshops.
