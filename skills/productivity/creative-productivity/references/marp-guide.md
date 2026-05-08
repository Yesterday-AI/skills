# Marp Slide Guide

Create slide decks in Markdown — export to PDF, PPTX, or HTML.

## When to Use

- Internal presentations (fast iteration, version-controlled)
- Developer-friendly slide authoring
- When content matters more than animation
- Quick workshop/meeting slides

## Basic Syntax

```markdown
---
marp: true
theme: default
paginate: true
header: "Company Name"
footer: "Confidential"
---

# Title Slide

Subtitle — Date

---

## Key Point

- Bullet one
- Bullet two
- Bullet three

<!-- Notes: Speaker notes go in HTML comments -->

---

## Two Columns

<div style="display: flex; gap: 2em;">
<div>

### Option A
- Fast to market
- Lower cost
- Less customization

</div>
<div>

### Option B
- Fully custom
- Higher investment
- Long-term flexibility

</div>
</div>

---

## Image Slide

![bg right:40%](https://example.com/image.png)

Content goes on the left side when using background images.

---

<!-- _class: lead -->

# Thank You

Next steps and contact info

```

## Directives

| Directive | Effect |
|-----------|--------|
| `<!-- _class: lead -->` | Centered, large text |
| `<!-- _class: invert -->` | Dark background |
| `![bg](url)` | Full background image |
| `![bg right:40%](url)` | Split layout with image |
| `![bg left:50%](url)` | Split layout, image left |
| `<!-- _paginate: false -->` | Hide page number |
| `<!-- _header: "" -->` | Hide header on this slide |

## Custom Theme (CSS)

```css
/* custom-theme.css */
@import 'default';

section {
  font-family: 'Inter', sans-serif;
  color: #1a1a2e;
}
section h1, section h2 {
  color: #0066cc;
}
section.lead {
  background: #1a1a2e;
  color: white;
}
section.lead h1 {
  color: #4ecdc4;
}
```

Use with: `marp --theme custom-theme.css deck.md`

## Export

```bash
# PDF (best for sharing)
marp --pdf deck.md

# PPTX (editable in PowerPoint)
marp --pptx deck.md

# HTML (web viewing)
marp deck.md

# With custom theme
marp --theme ./theme.css --pdf deck.md

# Watch mode (live preview)
marp -w deck.md
```

## Tips

- `---` separates slides (three dashes on their own line)
- Max 5-7 bullet points per slide
- Use `![w:300](image.png)` to control image width
- Tables work but keep them small (3-4 columns max)
- Code blocks render with syntax highlighting
- Use `_class: lead` for section dividers
