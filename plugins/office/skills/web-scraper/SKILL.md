---
name: web-scraper
description: Extract content from any web page. Provides a tiered approach from lightweight fetch to full browser rendering. Use when web_fetch fails or pages require JavaScript.
metadata:
  category: research
  author: ManniTheRaccoon
  version: "1.0"
compatibility: Requires Node.js 18+. Playwright + Chromium for JS-rendered pages.
---

# Web Scraper

Extract readable content from any URL using the best available method.

## Tiered Approach (use in order)

### Tier 1: `web_fetch` (Built-in, fast, no deps)
Best for: Static pages, APIs, markdown docs, RSS feeds.

```
web_fetch url="https://example.com" extractMode="markdown"
```

**Strengths:** Zero setup, fast (~200ms), low cost.
**Weakness:** No JavaScript rendering. Fails on SPAs, login walls, Cloudflare.

### Tier 2: `web_search` (Built-in, Brave API)
Best for: Finding URLs, getting snippets, quick facts.

```
web_search query="topic keyword"
```

**Strengths:** Fast, structured results with snippets.
**Weakness:** Needs Brave API key. Rate limited (2000/month free).

### Tier 3: Playwright Headless (Full rendering)
Best for: JavaScript-heavy pages, SPAs, login walls, social media.

```bash
node skills/web-scraper/scripts/scrape.js "https://example.com"
```

**Strengths:** Renders everything a real browser would. Handles Cloudflare, JS, dynamic content.
**Weakness:** Slow (~5-8s), needs Chromium installed, heavier on resources.

### Tier 4: DuckDuckGo Lite (Fallback search)
Best for: When Brave API is unavailable.

```
web_fetch url="https://lite.duckduckgo.com/lite?q=search+terms"
```

**Strengths:** No API key needed.
**Weakness:** Gets blocked after ~10 queries. Captcha.

## Decision Tree

```
Need content from URL?
├── Static page / API / docs → Tier 1 (web_fetch)
├── Need to find URLs first → Tier 2 (web_search)
├── Page needs JS / is SPA / social media → Tier 3 (Playwright)
└── No Brave API key → Tier 4 (DuckDuckGo)
```

## Setup (Tier 3 only)

```bash
npm install playwright
npx playwright install chromium
npx playwright install-deps chromium  # System libs, may need sudo
```

## See Also

- [x-reader](../x-reader/SKILL.md) -- Specialized for Twitter/X content
