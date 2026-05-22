# y-exa

Single-source MCP plugin for the Exa semantic-web-search server (`exa-mcp-server`).

## What it ships

- `.mcp.json` with a single `exa` stdio server (`npx -y exa-mcp-server`)
- a `userConfig` block in `plugin.json` declaring the `exa_api_key` field

## Why a dedicated plugin

Hoisting a shared MCP server into its own small plugin lets several bundles depend on one definition instead of each redeclaring it. That avoids the Claude Code "MCP server skipped -- same command/URL" dedupe warning, which fires when more than one installed plugin ships the same server name.

## How credentials are handled

When the plugin is enabled, Claude Code prompts for the `Exa API key` (masked, stored securely). At MCP-server-spawn time the value is interpolated into the `EXA_API_KEY` env var via `${user_config.exa_api_key}`.

No manual `~/.claude/settings.json` edit, no shell export, no `.env.example` to copy.

Get a key at <https://exa.ai/> -> dashboard -> API keys.

## How a bundle consumes it

In the bundle's `plugin.json`:

```json
{
  "dependencies": ["y-exa"]
}
```
