# Reveal.js Presentation Guide

Generate self-contained HTML presentations with Reveal.js — no build step required.

## When to Use

- Client-facing presentations (pitch decks, QBRs, strategy reviews)
- Conference talks and workshops
- Interactive demos with live code or charts
- When you need animations, transitions, and speaker notes

## Recommended Skill

For full Reveal.js generation with visual validation, use the dedicated skill:
- **Source:** [ryanbbrown/revealjs-skill](https://github.com/ryanbbrown/revealjs-skill)
- **Features:** Themes, Chart.js, overflow detection, screenshot review, PDF export

## Quick Start (Without Dedicated Skill)

Generate a single HTML file with embedded CSS and JS:

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css">
  <style>
    /* Custom overrides */
    :root {
      --r-heading-color: #1a1a2e;
      --r-main-color: #333;
      --r-link-color: #0066cc;
    }
    .reveal .slide-title { font-size: 2.5em; font-weight: 700; }
    .reveal .highlight-box {
      background: #f0f4ff; border-left: 4px solid #0066cc;
      padding: 1em; margin: 0.5em 0; text-align: left;
    }
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">

      <section>
        <h1 class="slide-title">Title</h1>
        <p>Subtitle — Date</p>
        <aside class="notes">Speaker notes go here</aside>
      </section>

      <section>
        <h2>Key Point</h2>
        <div class="highlight-box">
          <strong>Insight:</strong> The main takeaway for this slide.
        </div>
      </section>

    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
  <script>Reveal.initialize({ hash: true, transition: 'slide' });</script>
</body>
</html>
```

## Slide Types

| Type | Use For | Pattern |
|------|---------|---------|
| Title | Opening, section breaks | Large heading + subtitle |
| Content | Key points, arguments | Heading + bullet list or highlight box |
| Two-Column | Comparisons, before/after | CSS grid or flexbox layout |
| Chart | Data visualization | Chart.js canvas element |
| Image | Visual evidence | Full-bleed or centered image |
| Quote | Testimonials, key statements | `<blockquote>` with attribution |
| Agenda | Workshop/meeting flow | Numbered list with timing |
| CTA | Closing, next steps | Bold action items |

## Chart.js Integration

```html
<section>
  <h2>Growth Metrics</h2>
  <canvas id="chart1" width="600" height="400"></canvas>
  <script>
    Reveal.on('slidechanged', event => {
      if (event.currentSlide.querySelector('#chart1')) {
        new Chart(document.getElementById('chart1'), {
          type: 'bar',
          data: { labels: ['Q1','Q2','Q3','Q4'], datasets: [{ data: [10,25,40,65] }] }
        });
      }
    });
  </script>
</section>
```

## PDF Export

```bash
# Via DeckTape
npx decktape reveal presentation.html output.pdf

# Via browser print (Ctrl+P with ?print-pdf query param)
# Open: presentation.html?print-pdf
```

## Tips

- One idea per slide — if you need a scroll bar, split the slide
- Use `<section>` nesting for vertical slide groups (drill-down)
- Fragment animations: `<li class="fragment">Appears on click</li>`
- Dark themes for screen, light themes for print
- Always include `<aside class="notes">` for presenter context
