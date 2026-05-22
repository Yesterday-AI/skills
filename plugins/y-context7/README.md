# y-context7

Single-source MCP plugin for the Context7 docs server (`@upstash/context7-mcp`).

## What it ships

- `.mcp.json` with a single `context7` stdio server (`npx -y @upstash/context7-mcp@latest`)

No skills, commands, or env vars. No API key required.

## Why a dedicated plugin

Hoisting the docs MCP into one small plugin lets several bundles depend on a single definition instead of each shipping its own copy. Redeclaring the same server name across multiple installed plugins triggers Claude Code's "MCP server skipped -- same command/URL" dedupe warning; one shared definition avoids it.

Context7 provides live, version-accurate library documentation to agents.

## How a bundle consumes it

In the bundle's `plugin.json`:

```json
{
  "dependencies": ["y-context7"]
}
```
