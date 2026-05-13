# Knowledge

Patterns, rules, and lessons learned while building skills. This file is read by every future session. Keep it short. Keep it actionable.

## Conventions

- **Skill source layout:** `skills/<category>/<slug>/SKILL.md` (frontmatter required: `name`, `description`). Optional `.plugin.json` next to it for richer manifest.
- **Bundle source layout:** `plugins/<bundle-name>/plugin.json` (canonical) + `.claude-plugin/plugin.json` + `.cursor-plugin/plugin.json` (both symlinks to `../plugin.json`).
- **Top-level marketplace header:** `./marketplace.json` carries only `name`, `description`, `owner`, and optional `plugins[]` array of externals (e.g. github-sourced plugins). Auto-discovered entries are appended.
- **Compile output:** never edit `.compiled/` by hand — it's wiped + regenerated each `node compile.mjs` run.

## Lessons learned

- `~GOAL.md` is the spec. Read it before changing the compile pipeline.
- Slug = parent dir name; SKILL.md frontmatter `name` is for discoverability/UI, not for path identity.
- Symlink paths must be relative to the link's own directory, not to ROOT — `relative(dirname(linkPath), target)`.
- **Architectural changes need explicit user approval.** A single observed symptom is not a license to refactor the compile pipeline. Investigate, read the spec carefully, propose alternatives, ask. Lesson reinforced 2026-05-08: jumped from one `ls` showing empty cache folders straight to "rip out symlinks, copy files instead" without (a) reading the spec section that says symlinks ARE preserved, (b) verifying with `readlink` whether the cache symlinks resolved, (c) checking whether the cache version was stale, (d) asking. Reverted; fix the methodology, not the code, first.
- **Repo variables (`vars.*`) work in job-level `if:`, `env.*` does not.** When a value needs to gate a workflow (loop guards, conditionals), put it in repo vars. `env:` blocks are only available in step-level `if:`.
- **`actions/checkout` and `actions/setup-node` are at v6 with native Node 24 runtime.** No `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` env workaround needed.

## Gotchas

- `marketplace.jsonc` in `.compiled/` is a one-time reference template, NOT a build input. Don't add a JSONC parser back into the compile pipeline.
- `plugins/ytstack/` is intentionally empty (sourced from github). The compile script skips bundles without `plugin.json`. To list ytstack in marketplace.json, add it to the `plugins[]` array of the top-level `./marketplace.json`.
- Slug collisions between two SKILL.md files in different categories will cause one to be skipped with a warning — rename one folder.
- **Repo-local agent skill lives at `.agents/skills/audit-skills/`** (renamed 2026-05-08 from `audit-skills-for-leaks`). Three audit axes: leaks, catalog consistency, plugin-spec compliance. References: `.agents/skills/audit-skills/SKILL.md` + `references/leak-patterns.md`.
- **dotagents standard (sentry):** our `.agents/skills/<slug>/SKILL.md` layout matches their convention, but we don't ship `agents.toml` / `agents.lock` — different distribution model (catalog/marketplace vs. git-package-manager).
- **No migration framing in user-facing files.** Predecessor repos, old plugin names, "formerly X" labels, "promoted from" / "moved out of" phrasings: all belong in `.ytstack/DECISIONS.md` (history record) or this file. Never in README, NOTICE, plugin READMEs, SKILL.md, or `.plugin.json`. See DECISIONS.md "Migration history lives only in .ytstack/ docs".
- **No internal-perspective framing in user-facing files.** Phrases like "no Yesterday-infra dependencies", "generic-tauglich", "Yesterday-team needs ...", or "private companion catalog": all describe the catalog from Yesterday's vantage point. External users don't share that vantage. Frame from the user's perspective ("install with X", "requires SaaS account Y") instead. The acceptance criterion lives in DECISIONS.md.
