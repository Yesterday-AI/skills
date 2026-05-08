# office

Yesterday Daily Stack -- **core tier**. Generic productivity, creative, and knowledge skills for daily work. Nothing in the core bundle requires external SaaS keys at install time. Optional SaaS integrations (Figma, Miro, Voxtral TTS, VRR) live in [office-extras](../office-extras).

## Scope

Skills that are useful in day-to-day work and do NOT require `.ytstack/` project state. Engineering-focused skills belong in `ytstack` (engineering OS); autonomous-agent skills belong in `personal-agent`; ops skills belong in `systems-operations`.

## Skills shipped (6)

| Skill | Purpose |
|---|---|
| `exa-search-api` | Semantic web search via Exa AI |
| `excalidraw-diagram` | Hand-drawn diagrams as Excalidraw JSON |
| `slack-best-practices` | Slack formatting + communication etiquette |
| `using-github` | GitHub interaction policies |
| `web-scraper` | Tiered web scraping (lightweight fetch -> full browser) |
| `x-reader` | Twitter/X reader with login-wall + JS handling |

## Cross-marketplace plugins (3, auto-pulled via plugin.json)

| Plugin | Purpose |
|---|---|
| [creative-productivity](../../skills/concepts/creative-productivity) | Deliverables orchestrator (excalidraw + miro + reveal/marp + draw.io) |
| [para-memory-files](../../skills/capabilities/memory/para-memory-files) | PARA-method agent memory |
| `skill-creator` (from `claude-plugins-official`) | Meta-skill for creating new skills |

For optional SaaS integrations (Figma, Miro, Voxtral TTS, VRR transit) install [office-extras](../office-extras) alongside.

## Install

```bash
/plugin marketplace add Yesterday-AI/skills
/plugin install office@yesterday-public-plugins
```

Skills appear under `/office:<skill-name>`.
