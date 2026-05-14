# Contributing to skills

`skills` is Yesterday's PUBLIC plugin catalog for Claude Code and Cursor. Listed plugins must be installable by anyone -- no dependencies on private infrastructure or service accounts that aren't publicly available. See [`.ytstack/DECISIONS.md`](./.ytstack/DECISIONS.md) for the acceptance criteria.

## Philosophy

Catalog repos rot when they accumulate plugin-side concerns. This repo has three jobs:

1. List plugins via `marketplace.json` (the catalog header) merged with auto-discovered entries.
2. Host the source for bundle plugins (`./plugins/<bundle>/`) and standalone skills (`./skills/<category>/<slug>/`).
3. Compile both into installable plugin scaffolds under `.compiled/skill-plugins/` via `node compile.mjs`.

**Belongs in skills:**

- A new standalone skill: drop `SKILL.md` (+ optional `.plugin.json`) into `./skills/<category>/<slug>/`.
- A new bundle: create `./plugins/<bundle>/plugin.json` plus optional `skills/`, `README.md`.
- Updating existing skill / bundle content.
- Catalog metadata (top-level name, description, externals) in `./marketplace.json`.
- Build-pipeline changes (`compile.mjs`, `clean.mjs`).

**Does NOT belong:**

- Plugins that require private infrastructure to function (acceptance criteria in [DECISIONS.md](./.ytstack/DECISIONS.md)).
- Per-bundle marketplace.json files (consolidated into the top-level catalog).
- Generated artifacts (`.compiled/` is rebuilt on every `node compile.mjs`; never commit hand-edits there).

## Authoring a new skill (guided)

The fastest correct path is the `new-shareable-skill` skill at [`skills/operations/new-shareable-skill/SKILL.md`](./skills/operations/new-shareable-skill/SKILL.md). It walks one skill end to end -- intake, the "shareable by default" quality gate, the public-vs-private and standalone-vs-bundle placement decision, category selection, scaffold, `compile.mjs` + `audit-skills`, docs, and the PR to `main`. It refuses to scaffold a skill that cannot meet the bar.

The sections below are the manual reference for each step it automates.

## Adding a standalone skill

1. Create `skills/<category>/<slug>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: <slug>
   description: <one paragraph; user-facing -- no internal jargon>
   ---
   ```
2. Optionally add `skills/<category>/<slug>/.plugin.json` for richer manifest metadata (author, homepage, repository, license, keywords). Without this file, `compile.mjs` generates a minimal manifest from the SKILL.md frontmatter.
3. Run `node compile.mjs` and verify `.compiled/skill-plugins/<slug>/` looks right.
4. PR. CI will re-run compile + audit.

## Adding a bundle plugin

1. Create `plugins/<name>/plugin.json` (canonical location; symlinked from `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`).
2. Drop skills into `plugins/<name>/skills/<skill-name>/SKILL.md`.
3. Add a README + LICENSE + NOTICE per plugin if you want.
4. PR.

## Adding an external plugin

For plugins not living in this repo (e.g. github-sourced standalone repos):

1. Add an entry to the `plugins[]` array in `./marketplace.json`:
   ```json
   {
     "name": "<plugin-name>",
     "description": "<one-line purpose>",
     "source": { "source": "github", "repo": "Yesterday-AI/<plugin-name>" },
     "author": { "name": "Yesterday" },
     "keywords": ["claude-code", "yesterday", "..."]
   }
   ```
2. Run `node compile.mjs` to verify it lands in the merged catalog.
3. PR.

## Removing a plugin

Removing breaks installs for current users. Open an issue first describing why, get human signoff, then PR.

## Audit before publishing

This catalog is PUBLIC. Skills and bundles must NOT leak personal info or Yesterday-internal references. Run the local audit skill before opening a PR:

```
.agents/skills/audit-skills/SKILL.md
```

Inline scan command is in that file. Common categories: internal repo names ending in `-internal`, personal hostnames / paths, refactor history phrasings.

## Versioning

Plugins do **not** declare a `version` field. Claude Code falls back to the git commit SHA, so every commit on `main` is automatically a new version. If you reintroduce `version: "x.y.z"` you must bump it on every release or users see no updates -- preferred policy is not to.

The catalog itself is unversioned. The "release" is git `main`.

## Commit message format

- Add skill / bundle: `add <name>` (no prefix)
- Update content: `<name>: <what changed>`
- Compile pipeline: `compile: <what>`
- Catalog metadata: `marketplace: <what>`
- Docs: `docs: <what>`
- Infra: `chore: <what>`

## Atomic commits

One logical change per commit.

## Getting help

- Read [README.md](./README.md) for the catalog overview.
- Read [AGENTS.md](./AGENTS.md) for AI-agent-specific guidance.
- Read [`.ytstack/DECISIONS.md`](./.ytstack/DECISIONS.md) for the architectural rationale behind the compile pipeline + marketplace structure.
- For plugin-specific issues, open an issue against the plugin's own folder; for catalog-wide issues, open a top-level issue.
