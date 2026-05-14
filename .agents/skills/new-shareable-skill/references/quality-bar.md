# Quality bar -- shareable by default

A skill is only a good skill if someone else -- a colleague, a customer, a stranger's Claude Code -- can install and use it with no follow-up questions. Every item below is a gate, not a suggestion. If a skill cannot pass, `new-shareable-skill` stops and reports the gap instead of scaffolding it.

## The gates

### 1. Depersonalized (blocking in BOTH catalogs)

No personal data survives into a shared skill -- not even in the private catalog.

- No usernames in paths -- `/Users/alex/...`, `/home/<name>/...`, `C:\Users\<name>\...` -> `/Users/<you>/` or strip the path entirely
- No personal hostnames / machine names / LAN IPs (`192.168.x.x`, `*.local`, `*.lan`, personal NAS names)
- No personal tokens / keys (`sk-…`, `ghp_…`, `xox[baprs]-…`, `AKIA…`) -- revoke and remove
- No personal handles, real contributor names (other than the `Yesterday` org / public author handles), private emails
- No browser bookmarks, session cookies, OAuth callback URLs with state tokens

### 2. Self-contained

The skill carries everything it needs.

- Knowledge lives in `SKILL.md` + `references/*.md`, not in the author's Confluence / Notion / private notes
- No links to un-shared paths or private docs
- No "ask <person>" / "see the channel" -- if the agent needs it, it is in the skill
- `scripts/` are runnable as shipped; no assumed local state

### 3. No internal-perspective framing (blocking in PUBLIC; keep org framing in `.ytstack/`)

User-facing fields -- `description`, `SKILL.md` body, `README.md`, `.plugin.json` -- speak from the *user's* vantage, not Yesterday's.

- Write "install with X", "requires a SaaS account for Y" -- not "no Yesterday-infra deps", "generic-tauglich", "Yesterday team needs ..."
- No migration / refactor history: `formerly X`, `previously lived in`, `promoted from`, `(renamed: X)`, predecessor repo names
- No `-internal` repo names, internal Slack channels, Linear/Jira ticket codes
- Org / migration framing that has to be recorded somewhere goes in `.ytstack/DECISIONS.md`, never a user-facing file

### 4. Sharp description line

The frontmatter `description` is the single thing the model routes on (Anthropic Progressive Disclosure level 1). A vague description means the skill never fires.

- One paragraph. States WHAT the skill does AND WHEN it should be invoked.
- Concrete triggers: "Use when asked to build websites, landing pages, dashboards ..." beats "helps with web stuff".
- No internal jargon (it is a user-facing field).

### 5. Non-ambiguous slug

- Names the concrete capability, not the tool or domain in general: `github-worktrees` not `github`, `web-design` not `wd`, `paperclip-api` not `pc`.
- Self-explanatory in a bare `/skills` list with no conversation context.
- kebab-case, no spaces, collision-free across `skills/**`.
- Slug = folder name = `.plugin.json` `name`. Drift between the three is caught by `audit-skills`.

### 6. Spec-compliant manifest

- `.plugin.json` `name` is required, kebab-case, matches the folder.
- `author` may carry `name` (required) + `email` (optional) only -- `url` is not in the schema.
- Optional: `$schema`, `description`, `homepage`, `repository`, `license`, `keywords`, `dependencies`.
- **No `version` field** -- the catalog resolves by git SHA on purpose. A pinned `version` that is never bumped makes `/plugin update` a no-op.
- `.claude-plugin/` and `.cursor-plugin/` hold only `plugin.json`. Skills, agents, commands, hooks live at plugin root.

## `SKILL.md` template

```markdown
---
name: <slug>
description: <one paragraph -- what the skill does AND when to invoke it. User-facing, no internal jargon, concrete triggers.>
metadata:
  category: <short category tag>
---

# <Skill Title>

<One or two sentences: what an agent can do with this skill, and the shape of the workflow.>

## When to use

- <concrete trigger>
- <concrete trigger>

## Procedure

1. <step>
2. <step>

## <Domain sections as needed>

## Limits

- <what this skill does NOT do; known false positives / edge cases>

## See also

- `references/<file>.md` -- <what it holds>
```

If the skill carries source attribution (composed from other open-source skills), add a `## Sources & Attribution` table right after the title -- see `skills/productivity/web-design/SKILL.md` for the pattern.

## `.plugin.json` template

Recommended for every standalone skill so the marketplace listing is complete. Without it, `compile.mjs` generates a minimal manifest from frontmatter (`name` + `description` only).

```json
{
  "name": "<slug>",
  "description": "<same as SKILL.md frontmatter description, or a tighter one-liner>",
  "author": { "name": "Yesterday" },
  "homepage": "https://github.com/Yesterday-AI/skills/tree/main/.compiled/skill-plugins/<slug>",
  "repository": "https://github.com/Yesterday-AI/skills",
  "license": "MIT",
  "keywords": ["claude-code", "yesterday", "<domain>", "<capability>"]
}
```

For the private catalog, swap the `homepage` / `repository` URLs to `Yesterday-AI/yesterday-skills`.

## Depersonalization pass (for an existing skill being promoted)

Run this before scaffolding when the source is a personal or ad-hoc skill:

1. `grep -rnE '/Users/[a-z]+/|/home/[a-z]+/' <source>` -- paths with usernames
2. `grep -rnE 'sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-' <source>` -- tokens
3. `grep -rnE '\b\w*-internal\b|\.internal\b|192\.168\.|10\.0\.' <source>` -- internal infra
4. `grep -rniE 'formerly|previously|promoted from|renamed|migrated from' <source>` -- migration framing
5. Read the `description` -- rewrite from the user's perspective if it leaks Yesterday's vantage.
6. Read every `references/` file -- the same gates apply there; references are loaded into agent context just like the body.

After scaffolding, `audit-skills` (step 5 of the main procedure) is the authoritative re-check. This pass is the cheap pre-filter so the skill is already close to clean when it gets there.
