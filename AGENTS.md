# AGENTS.md

Contributor guide for AI agents working on this repo. Humans: see [README.md](./README.md) and [CONTRIBUTING.md](./CONTRIBUTING.md).

## What this repo is

`skills` is Yesterday's PUBLIC plugin catalog. Two kinds of source content:

- **Standalone skills** under `./skills/<category>/<slug>/SKILL.md` (+ optional `.plugin.json`)
- **Bundle plugins** under `./plugins/<name>/plugin.json` (canonical) with optional `skills/` subfolder

A single Node script (`compile.mjs`) discovers both and produces `.compiled/skill-plugins/` plus `.compiled/marketplace.json`. The marketplace is exposed at `./.claude-plugin/marketplace.json` and `./.cursor-plugin/marketplace.json` via symlinks.

## Hard rules (do not violate)

- **PUBLIC repo. No leaks.** Never write Yesterday-internal references (repo names ending in `-internal`, internal infra hostnames, internal Slack/Linear refs, refactor-history phrases like "promoted from temp-home in xxx-internal") into user-facing fields (descriptions, READMEs, frontmatter). Run `.agents/skills/audit-skills/` before claiming done.
- **Never edit `.compiled/`.** Always edit sources and run `node compile.mjs`. The generated tree is wiped on every build.
- **Never reintroduce `version` in `plugin.json`.** Decision in `.ytstack/DECISIONS.md`: rely on git SHA so updates propagate.
- **Slug = parent folder name.** Don't rename folders without updating cross-references; collisions are skipped with a warning.
- **`marketplace.jsonc` (if present in `.compiled/`) is a one-shot reference template, not a build input.** Don't reintroduce a JSONC parser.

## Common tasks

| Task | Where to edit |
|---|---|
| Author / promote a skill (guided) | `skills/operations/create-shareable-skill/SKILL.md` -- walks intake → quality gate → placement → scaffold → compile + audit → docs → PR |
| Add a standalone skill | `skills/<category>/<slug>/SKILL.md` (+ optional `.plugin.json`), then `node compile.mjs` |
| Add a bundle | `plugins/<name>/plugin.json` (canonical), then `node compile.mjs` |
| Add an external plugin (github-hosted) | `marketplace.json` (top-level, `plugins[]` array), then `node compile.mjs` |
| Tweak top-level catalog metadata | `marketplace.json` (`name`, `description`, `owner`, `allowCrossMarketplaceDependenciesOn`) |
| Audit before publishing | `.agents/skills/audit-skills/SKILL.md` (run inline command) |

## Project memory

This repo uses ytstack. Read these BEFORE making non-trivial changes:

- `.ytstack/PROJECT.md` -- what this is + success criteria
- `.ytstack/DECISIONS.md` -- why the compile pipeline + marketplace structure are the way they are
- `.ytstack/KNOWLEDGE.md` -- conventions, gotchas
- `.ytstack/STATE.md` -- current status, open decisions

When you make a non-trivial architectural decision, append to `DECISIONS.md` (don't rewrite past entries). When you discover a non-obvious gotcha, add to `KNOWLEDGE.md`.

## Build and verify

```bash
node clean.mjs          # wipe .compiled/ + root marketplace symlinks
node compile.mjs        # rebuild from sources
```

Verify after any source change:

```bash
# 1. confirm marketplace is valid JSON + has expected plugin count
node -e "console.log(JSON.parse(require('fs').readFileSync('.compiled/marketplace.json','utf8')).plugins.length, 'plugins')"

# 2. run leak audit (see .agents/skills/audit-skills/SKILL.md)
```

## Out of scope

- Plugins that require private infrastructure to function. See [DECISIONS.md](./.ytstack/DECISIONS.md) for the public-installability rule.
- Changing the marketplace `name` field (`yesterday-public-plugins`) -- it's the install target for every existing user.
- Auto-bumping versions -- the project decided against pinned versions on purpose.

## When in doubt

Read `.ytstack/DECISIONS.md` for context on why something is the way it is. If the answer isn't there, ask the user before making the change.
