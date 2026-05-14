# Decisions

Append-only architectural and product decisions for skills. Never rewrite past entries. If a decision is reversed, add a new entry that supersedes.

Format for each entry:

## YYYY-MM-DD: <Short title>

**Context:** <what forced the decision>
**Options considered:** <A, B, C>
**Chose:** <selected option>
**Reason:** <why>
**Supersedes:** <link to earlier entry if this reverses a prior decision>

---

## 2026-05-08: Compile pipeline = single Node script, no build system

**Context:** Need to turn `skills/**/SKILL.md` sources into installable plugin folders for Claude Code + Cursor, plus a marketplace.json. ~GOAL.md spec is short (discover → scaffold → symlink-or-generate). Repo has no package.json / build infra.

**Options considered:**

- A) `compile.mjs` standalone Node script at repo root, no deps
- B) Add Turborepo / pnpm package with TS + tests
- C) Bash script

**Chose:** A.

**Reason:** Spec is small and stable. Zero install. Node 22 is on dev machines. Single file = trivially auditable. TS infra would dwarf the actual logic (~150 LOC). Bash gets ugly fast for JSONC stripping + recursive walks.

---

## 2026-05-08: Discovery via `skills/**/SKILL.md`, slug = parent dir

**Context:** Per ~GOAL.md, compilation discovers skills via SKILL.md presence.

**Options considered:**

- A) Slug = parent dir name (`skills/concepts/web-design/SKILL.md` → `web-design`)
- B) Slug = SKILL.md frontmatter `name`
- C) Path-flattened (`concepts-web-design`)

**Chose:** A, with collision detection (skip + warn).

**Reason:** Matches ~GOAL.md ("Auto-flattens folder name to avoid collisions"). Frontmatter `name` could drift from folder name; folder is the canonical anchor. Path-flattening is ugly and breaks predictable install paths. Collision = explicit error so author can rename.

---

## 2026-05-08: Symlink source folder, generate manifest only when missing

**Context:** Per ~GOAL.md "symlink (when .plugin.json exists) or generate {.claude-plugin,.cursor-plugin}/plugin.json".

**Options considered:**

- A) Always symlink source folder; for plugin.json: symlink source `.plugin.json` if present, else generate from SKILL.md frontmatter
- B) Always copy (no symlinks)
- C) Always generate plugin.json from frontmatter (ignore source `.plugin.json`)

**Chose:** A.

**Reason:** Symlinks keep `.compiled/` cheap + always in sync with source edits. Source-`.plugin.json` is opt-in richer manifest (author, keywords, repo) — respect it when present. Frontmatter-derived fallback covers minimal skills with just name + description. Copy would silently drift; ignoring `.plugin.json` would lose hand-curated metadata.

---

## 2026-05-08: marketplace.json auto-discovery + top-level header file

**Context:** marketplace.json needs top-level metadata (name, description, owner) plus a `plugins[]` array mixing externals (e.g. ytstack via github), local bundles (`./plugins/<name>`), and standalone skills (`./.compiled/skill-plugins/<slug>`). marketplace.jsonc was only a one-shot reference template.

**Options considered:**

- A) Hand-maintain marketplace.json fully
- B) Generate from a JSONC template + comment-strip
- C) Auto-discover bundles + standalone, merge with hand-written header file (`./marketplace.json` containing only name/description/owner + optional externals)

**Chose:** C.

**Reason:** Adding/removing skills = re-run compile, no marketplace edit needed. Externals (github-sourced like ytstack) stay declarative in the header file. JSONC template (B) would mean every plugin add still needs manual edits — defeats the point of auto-discovery.

---

## 2026-05-08: Bundle plugin.json canonical at `plugins/<name>/plugin.json`

**Context:** Bundles previously had plugin.json only inside `.claude-plugin/`. Cursor expects the same file at `.cursor-plugin/plugin.json`. Two parallel files would drift.

**Options considered:**

- A) Keep plugin.json inside `.claude-plugin/`, copy to `.cursor-plugin/`
- B) Move plugin.json to bundle root (`plugins/<name>/plugin.json`), symlink from both `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`
- C) Generate `.cursor-plugin/plugin.json` at compile time

**Chose:** B.

**Reason:** Single source of truth. Symlinks guarantee no drift. Editor opens canonical file. Discovery in `compile.mjs` reads from canonical path (`plugins/<name>/plugin.json`), not via the symlinks.

---

## 2026-05-08: marketplace.json symlinked into both `.claude-plugin/` and `.cursor-plugin/`

**Context:** Marketplace consumers (Claude Code, Cursor) look in their respective `.<editor>-plugin/` subfolder.

**Chose:** Generate `.compiled/marketplace.json` once, symlink to `./.claude-plugin/marketplace.json` and `./.cursor-plugin/marketplace.json` at workspace root.

**Reason:** Same file, two consumer expectations. Symlink avoids duplication. Folders live at workspace root (not inside `.compiled/`) because that's where Claude Code / Cursor look when the workspace itself is treated as a plugin source.

**Supersedes:** initial implementation that placed the symlinks under `.compiled/.claude-plugin/` and `.compiled/.cursor-plugin/`.

---

## 2026-05-08: Migration history lives only in .ytstack/ docs, never in user-facing files

**Context:** This repo consolidates content from several predecessor repos. The first instinct was to document the renames + origin in user-facing files (README "Migration note" table, NOTICE "Predecessors" section, plugin READMEs with "formerly X" framing). External users don't need that history -- they need to know what's installable now.

**Options considered:**

- A) Keep migration tables / "formerly X" labels in user-facing READMEs + NOTICE
- B) Strip all migration framing from user-facing files; keep history only in `.ytstack/` (this file + KNOWLEDGE.md)
- C) Hybrid: strip from READMEs, keep a short Predecessors block in NOTICE

**Chose:** B.

**Reason:** Migration is internal-perspective context. A user reading the README has no relationship to the predecessor repos and finds the table confusing rather than orienting. NOTICE is for legal attribution, not project history. The rename is also already redirectable via GitHub repo redirects + each plugin README's clean current-state framing.

**Rule going forward:** any mention of predecessor repos, old plugin names, refactor history, or "formerly X" framing belongs in `.ytstack/DECISIONS.md` or `.ytstack/KNOWLEDGE.md` -- never in README, NOTICE, plugin READMEs, SKILL.md, or `.plugin.json` descriptions. The audit skill at `.agents/skills/audit-skills/` flags this category.

### Predecessor record (kept here for history)

| Predecessor | Current home |
|---|---|
| `Yesterday-AI/ystacks` (catalog) | this repo (`Yesterday-AI/skills`) -- marketplace + bundles + standalone |
| `Yesterday-AI/yastack` | `plugins/personal-agent/` |
| `Yesterday-AI/yopstack` | `plugins/systems-operations/` |
| `Yesterday-AI/ydstack` | `plugins/office/` |
| `Yesterday-AI/ydstack-extras` | `plugins/office-extras/` |
| `Yesterday-AI/ytstack` | external (referenced via marketplace.json `plugins[]`, source still upstream) |

Predecessor repos remain available read-only for git history continuity. New development happens here.

---

## 2026-05-08: Acceptance criterion -- public-installability, no private-infra deps

**Context:** This catalog is PUBLIC. Anyone with a Claude Code or Cursor install can `marketplace add Yesterday-AI/skills` and pick a plugin. If a listed plugin needs Yesterday-internal infrastructure (private hostnames, internal-only auth providers, services that are not publicly available) it will fail at runtime for everyone outside Yesterday and damage user trust in the catalog.

**Options considered:**

- A) Document the rule in user-facing READMEs ("no Yesterday-infra dependencies")
- B) Document the rule only in contributor-side artifacts (CONTRIBUTING, AGENTS, this file), keep user-facing READMEs free of internal-perspective framing
- C) Allow infra-coupled plugins, mark them with metadata, let them fail gracefully

**Chose:** B.

**Reason:** "No Yesterday-infra deps" is internal framing -- it tells external users about a constraint that only matters from Yesterday's perspective (we have a separate internal world they cannot see). External readers don't need that context; they need to know *what they can install*. The acceptance rule still has to live somewhere because contributors need it, so it lives here + in CONTRIBUTING + AGENTS, not in the user-facing hero / READMEs.

**Concrete acceptance criterion for new plugins:**

A plugin is acceptable for this catalog if BOTH:

1. It can be installed and (for the no-key paths) used by anyone with a public Claude Code / Cursor install. SaaS-key-gated plugins are OK as long as the SaaS itself is publicly available (Figma, Mistral, etc.).
2. It does NOT depend on private hostnames, private package registries, internal-only auth providers, or services that are not publicly reachable.

Plugins that fail either criterion belong elsewhere, not here.

---

## 2026-05-13: Public bundles avoid install-breaking cross-marketplace deps

**Context:** `systems-operations` declared a dependency on `skill-creator@claude-plugins-official`. Even with `allowCrossMarketplaceDependenciesOn: ["claude-plugins-official"]` correctly set in `marketplace.json`, `/doctor` reported a plugin error after install: the dep is NOT auto-installed -- the user must separately `/plugin marketplace add` the official catalog AND `/plugin install skill-creator@claude-plugins-official`. For a public catalog this is a broken first-run experience.

**Options considered:**

- A) Keep the dep, document the manual two-step in the README
- B) Drop the cross-marketplace dep from the bundle
- C) Vendor the needed skill into the catalog

**Chose:** B. Removed the `dependencies` block from `plugins/systems-operations/plugin.json`.

**Reason:** `allowCrossMarketplaceDependenciesOn` is a *permission whitelist*, not an installer. A public-catalog bundle that errors in `/doctor` on a clean install damages trust. `skill-creator` is a nice-to-have meta-skill, not a runtime requirement of the ops skills.

**Rule going forward:** public-catalog bundles must be installable + `/doctor`-clean with a single `/plugin install`. A cross-marketplace dep is allowed only when (1) the dependency is genuinely essential AND (2) the bundle README spells out the manual marketplace-add + install prerequisite steps. Note: this rule is public-catalog-specific -- the private `yesterday-skills` catalog intentionally relies on cross-mp deps (Yesterday-team installs add both marketplaces).

---

## 2026-05-08: clean.mjs targets only generated artifacts, never folder roots

**Context:** Need a `clean.mjs` to wipe build outputs before a fresh `compile.mjs` run.

**Options considered:**

- A) Wipe `.claude-plugin/` and `.cursor-plugin/` folders entirely
- B) Wipe only the generated `marketplace.json` symlink inside each, leave folders intact

**Chose:** B.

**Reason:** Those folders may later contain other content (workspace-level plugin.json, READMEs). Targeting the named generated files keeps the tool surgical and reversible. Same principle for `.compiled/`: list `skill-plugins/` and `marketplace.json` explicitly rather than wiping `.compiled/` (which would also blow away `~GOAL.md`-referenced legacy `marketplace.jsonc`).

---

## 2026-05-14: `new-shareable-skill` lives in `.agents/skills/`, not the marketplace tree

**Context:** M001 adds a `new-shareable-skill` meta-skill that guides authoring a shareable skill: quality gate, public-vs-private catalog routing, standalone-vs-bundle placement, category selection, docs, PR. By design it must reason about -- and name -- the private `Yesterday-AI/yesterday-skills` catalog and the routing rules between the two catalogs.

**Options considered:**

- A) Standalone skill in the marketplace tree (`skills/<category>/new-shareable-skill/`) -- gets compiled + published to `yesterday-public-plugins`
- B) Repo-local tooling in `.agents/skills/new-shareable-skill/` -- alongside `audit-skills`, not compiled, not published
- C) Two copies: a generic one published publicly, a full one with private routing in `yesterday-skills`

**Chose:** B.

**Reason:** A marketplace-published skill is a user-facing artifact. A published skill that says "if the skill needs private infra, route it to `Yesterday-AI/yesterday-skills`" leaks the existence + name of the private catalog into the public marketplace -- exactly the internal-perspective leak the "Acceptance criterion" and "Migration history" decisions forbid. Option A would force stripping the very public/private routing the skill exists to provide. Option C duplicates a workflow skill for no gain and creates a drift surface. `.agents/skills/` is contributor tooling (same tier as `audit-skills`, which itself documents `-internal` patterns) and is explicitly excluded from the leak audit -- so the full routing logic can live there honestly. `compile.mjs` only walks `skills/`, so `.agents/` content is never compiled or published; marketplace count stays at 14.

**Rule going forward:** a meta-skill *about* the catalog (authoring, auditing, releasing) belongs in `.agents/skills/`. A skill that delivers a user-facing capability belongs in `skills/<category>/`. If publishing a skill would force an internal-perspective leak or stripping its core content, that is the signal it is `.agents/` tooling, not a catalog entry.

---

## 2026-05-14: New catalog skills enter via PR to `main`, never direct push

**Context:** M001 also had to decide the contribution path for the meta-skill itself, and the meta-skill encodes that path for every future skill.

**Chose:** Branch (`add-<slug>`) → atomic commit (`add <slug>`, CONTRIBUTING commit format) → push → `gh pr create --base main` → human signoff → merge. Never self-merge; never commit a new skill directly on `main`.

**Reason:** CI (`compile.yml` + `secret-scan.yml`) re-runs compile + a gitleaks scan on the PR -- that gate only fires on a PR. A new catalog entry changes what installers receive and is hard to walk back once `main` moves, so it needs human review. This matches the existing CONTRIBUTING "PR. CI will re-run compile + audit" guidance and makes it explicit + non-optional.

---

## 2026-05-14: `new-shareable-skill` ships as a standalone catalog skill (supersedes the `.agents/` placement)

**Context:** The prior entry placed `new-shareable-skill` in `.agents/skills/` to avoid naming the private `yesterday-skills` catalog in a published artifact. The user rejected that on review: `new-shareable-skill` is to be a standalone, compiled, marketplace-published skill like any other -- "authoring a shareable skill" is itself a user-facing capability, not just internal tooling.

**Chose:** Standalone skill at `skills/operations/new-shareable-skill/` (+ `.plugin.json`). Compiled by `compile.mjs`, listed in the marketplace (count 14 -> 15). Only `audit-skills` stays in `.agents/` -- it is pure verification machinery with no user-facing capability.

**Reason:** User decision; user instructions outrank an agent's architectural judgement. The leak concern is handled at the content level instead of by hiding the file: the actual username path example was depersonalized, gratuitous pattern tokens were softened. The two catalogs are still named -- that was an explicit requirement ("der die policies dieses und des yesterday-skills repos kennt"), and `yesterday-skills` is not an `-internal`-suffixed repo.

**Known consequence:** `references/quality-bar.md` documents leak patterns (grep commands, `-internal`, migration-framing examples). Now that the skill lives under `skills/` it is in `audit-skills`' scan scope, so axis-1 will surface known false positives from this skill's own pattern documentation -- the same reason `audit-skills` excludes `.agents/`. The clean structural fix, if the noise is unwanted, is to add `skills/operations/new-shareable-skill/references/` to `audit-skills`' `-not -path` exclusions; not done here because it modifies a second skill that was not in scope.

**Supersedes:** "2026-05-14: `new-shareable-skill` lives in `.agents/skills/`, not the marketplace tree". The "meta-skill -> `.agents/`" rule from that entry no longer holds as a blanket rule; `.agents/` is now specifically for non-user-facing verification / build machinery.
