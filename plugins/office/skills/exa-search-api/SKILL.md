---
name: exa-search-api
description: Semantic web search via Exa AI API. Returns full-text content, not just snippets. Use for deep research, competitor analysis, or finding specific technical content.
metadata:
  category: research
  author: ManniTheRaccoon
  version: "1.0"
compatibility: Requires curl, jq, and an Exa API key.
---

# Exa Search 🔍🧠

Exa is a semantic search engine built for AI. Unlike traditional search (keyword matching), Exa understands *meaning* and returns **full-text content** -- not just titles and snippets.

## When to Use

| Use Exa | Use web_search (Brave) |
|---------|----------------------|
| Deep research, full article text | Quick facts, simple lookups |
| "Find articles about X" | "What is X?" |
| Competitor analysis | URL discovery |
| Technical deep-dives | News headlines |

## Usage

```bash
# Basic search (5 results)
./skills/exa-search-api/scripts/search.sh "query" 5

# Or via curl directly
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "your query", "num_results": 5, "type": "auto", "use_autoprompt": true, "contents": {"text": {"max_characters": 5000}}}'
```

## Output

Returns JSON with full results:
```json
{
  "results": [
    {
      "title": "Article Title",
      "url": "https://...",
      "text": "Full article content up to 5000 chars...",
      "score": 0.95
    }
  ]
}
```

## Key Advantages Over Other Tools

- **Full text** -- Not just snippets. Get the actual article content.
- **Semantic** -- Understands meaning, not just keywords.
- **Autoprompt** -- Rewrites your query for better results.
- **Filters** -- Date ranges, domains, content type.

## Setup

1. Get API key at https://exa.ai
2. Store key securely:
   ```bash
   echo "your-key" > ~/.openclaw/secrets/exa.key
   chmod 600 ~/.openclaw/secrets/exa.key
   ```
3. Set env var or pass to script:
   ```bash
   export EXA_API_KEY=$(cat ~/.openclaw/secrets/exa.key)
   ```

## Depends On

None (standalone). Complements [web-scraper](../web-scraper/SKILL.md) for pages Exa can't reach.

---

*Authored by ManniTheRaccoon. Tested 2026-02-20.* 🦝
