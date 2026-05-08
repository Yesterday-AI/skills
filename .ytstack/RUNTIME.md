# Runtime

Services, APIs, env vars, and ports used by skills.

## Services

- GitHub (Yesterday-AI org) — distribution channel for compiled marketplace.
- Claude Code marketplace — consumes `.compiled/.claude-plugin/marketplace.json`.
- Cursor marketplace — consumes `.compiled/.cursor-plugin/marketplace.json`.

## Environment variables

(None required for `node compile.mjs`.)

Per-skill runtime env vars are documented in each `SKILL.md` frontmatter under `metadata.openclaw.requires.env`.

## Ports

(None — compile is a one-shot CLI.)

## Deploy target

GitHub Action pipeline runs `node compile.mjs` and publishes to the marketplace repo refs.
