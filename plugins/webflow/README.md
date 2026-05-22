# webflow

Single-source plugin for the **Webflow MCP server** (`https://mcp.webflow.com/mcp`, remote HTTP + OAuth), bundled with the `webflow` skill.

## Why this exists

Webflow MCP access was being configured per-project (a hand-written `.mcp.json`
in every repo) and the how-to lived only in chat. Hoisting the server into one
plugin means any project or bundle gets the Webflow MCP **and** the usage skill
from a single dependency — no per-repo `.mcp.json`, no `claude mcp add`.

## What it ships

- `.mcp.json` with a single `webflow` HTTP server (`https://mcp.webflow.com/mcp`).
  No API key — auth is OAuth on first use (run the `authenticate` tool).
- `skills/webflow` — the `webflow` skill (Data API vs Designer API tiers,
  setup/OAuth, core workflows, gotchas, safety).

## How to consume it

Install directly, or declare it as a dependency from a bundle `plugin.json`:

```json
{
  "dependencies": [
    { "name": "webflow", "marketplace": "yesterday-public-plugins" }
  ]
}
```

(Cross-marketplace deps are a whitelist, not an installer — the consuming
marketplace must list it in `allowCrossMarketplaceDependenciesOn` and the user
must add this marketplace + install the plugin.)

## See also

- `Yesterday-AI/yesterday-skills` → `plugins/yesterday-systems-operations`
  ships `yesterday-website-webflow`, which extends this skill with the live
  Yesterday website's site IDs, page map, and legal-page / footer conventions.
