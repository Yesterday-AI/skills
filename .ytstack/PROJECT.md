---
name: skills
slug: skills
created: 2026-05-08T12:35:06Z
updated: 2026-05-08T12:35:06Z
---

# skills

**One-liner:** (run /ytstack:office-hours to validate the premise and populate this one-liner; until then the project has no validated pitch)

## What this project is

Yesterday's PUBLIC plugin catalog. Hosts standalone agent skills (`skills/<category>/<slug>/SKILL.md`) and bundled plugins (`plugins/<bundle>/`). A compile pipeline produces installable Claude Code + Cursor plugins under `.compiled/skill-plugins/` and a top-level marketplace.json.

## Why it exists

Single source of truth for shared, depersonalized skills/plugins that can be consumed by Claude Code and Cursor via marketplace. Avoids per-repo duplication and lets every agent pull from one curated catalog.

## Success criteria

- `node compile.mjs` produces a working `.compiled/skill-plugins/<slug>/` per discovered SKILL.md
- Generated `marketplace.json` is valid + installable in Claude Code and Cursor
- Adding a new skill = drop SKILL.md (+ optional .plugin.json) into `skills/**/<slug>/`, re-run compile

## Current status

Compile pipeline (`compile.mjs`) initial implementation done: skill discovery, per-plugin scaffolding (skills symlink + .claude-plugin / .cursor-plugin manifests), marketplace.json generation from header + auto-discovered bundles + standalone.
