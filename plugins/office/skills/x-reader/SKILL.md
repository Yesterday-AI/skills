---
name: x-reader
description: Read Twitter/X posts, threads, and articles. Handles login walls and JS rendering. Use when a user shares an x.com or twitter.com link.
metadata:
  category: research
  author: ManniTheRaccoon, Robby
  version: "1.2"
compatibility: Requires Node.js 18+. Uses web-scraper skill for Playwright rendering or fxtwitter API for speed.
---

# X-Reader

Read any Twitter/X content -- tweets, threads, and long-form articles.

## Strategy

```
X/Twitter URL received?
├── Simple tweet or Article → fxtwitter API (fast, free, no login-wall):
│   web_fetch "https://api.fxtwitter.com/<user>/status/<id>"
│   (For Articles: Check tweet.article.content.blocks[] for Draft.js content)
│
├── Medium Article → web_fetch (direct) or Freedium (fallback):
│   web_fetch "https://medium.com/<url>"
│   If teaser only: web_fetch "https://freedium.cfd/medium.com/<url>"
│
├── Thread (Full) → Playwright (via web-scraper):
│   node skills/web-scraper/scripts/scrape.js "<url>" --wait 5000
│
└── All methods fail → Ask user to paste or screenshot
```

## Methods

### 1. fxtwitter API (Speed & Efficiency)
Best for single tweets and X Articles. No API key needed.
- **Normal Tweets:** Use `tweet.text`, `tweet.author.name`, etc.
- **X Articles:** Look into `tweet.article.content.blocks[]`. Map `header-two` to `##` and `unstyled` to paragraph.

### 2. oEmbed API (Legacy fallback)
```bash
web_fetch "https://publish.twitter.com/oembed?url=https://x.com/user/status/123"
```

### 3. Medium (Client-side Paywall bypass)
Medium paywalls are often client-side JS only. Raw `web_fetch` often gets the full HTML.
- **Fallback (Freedium):** Rewrite `medium.com` to `freedium.cfd/medium.com`.

### 4. Playwright (Reliability fallback)
For complex threads or when API methods fail.
```bash
node skills/web-scraper/scripts/scrape.js "<url>" --wait 5000
```

## URL Detection

Recognize X/Twitter/Medium links:
- `https://x.com/<user>/status/<id>`
- `https://twitter.com/<user>/status/<id>`
- `https://x.com/i/article/<id>`
- `https://medium.com/<author>/<article-slug>`

## Depends On

- [web-scraper](../web-scraper/SKILL.md) -- Playwright rendering engine

---

*Authored by ManniTheRaccoon & Robby. Merged by Yessy 🐾 2026-03-03.*
