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

## 2026-05-08: Standalone-plugin content COPIED, not symlinked (cache survives)

**Context:** Initial implementation symlinked `skills/<slug>` and the `plugin.json` files in `.compiled/skill-plugins/<slug>/` to the source files outside the plugin folder (e.g. `../../../../skills/concepts/web-design/`). When Claude Code installs a plugin from a marketplace, it copies the plugin folder to `~/.claude/plugins/cache/<marketplace>/<plugin>/<sha>/`. Spec docs claim symlinks are "preserved in the cache" -- in practice for **external relative targets**, the symlink survives but its target path no longer resolves at the cache location, so Claude Code sees an empty `skills/` folder and zero skills load.

**Verification of the bug:** after install, `~/.claude/plugins/cache/yesterday-public-plugins/web-design/<sha>/skills/` was empty; the plugin was listed as enabled but no skills appeared in `/skills`.

**Options considered:**

- A) Keep symlinks (broken at cache)
- B) Copy source content into `.compiled/skill-plugins/<slug>/` as real files; bundle plugins keep their internal `../plugin.json` symlinks (target stays inside plugin folder, cache-safe)
- C) Restructure repo so each standalone skill lives at `.compiled/skill-plugins/<slug>/skills/<slug>/` directly (no compile step)

**Chose:** B.

**Reason:** B is the smallest fix that produces self-contained, install-correct plugin folders. C would break the source layout (`skills/<category>/<slug>/`) we want for navigation. A simply doesn't work.

**Bundle plugins are unaffected** because their canonical `plugin.json` is at `plugins/<bundle>/plugin.json` and the editor-folder symlinks (`.claude-plugin/plugin.json` -> `../plugin.json`) point INSIDE the plugin folder -- those resolve at any cache location.

**Implication for `.compiled/`:** the directory now contains real-file copies of every standalone skill, doubling on-disk size. Acceptable because `.compiled/` is the install-target tree and consumers expect it self-contained. `compile.mjs` always wipes + rebuilds, so duplication never drifts.

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

## 2026-05-08: clean.mjs targets only generated artifacts, never folder roots

**Context:** Need a `clean.mjs` to wipe build outputs before a fresh `compile.mjs` run.

**Options considered:**

- A) Wipe `.claude-plugin/` and `.cursor-plugin/` folders entirely
- B) Wipe only the generated `marketplace.json` symlink inside each, leave folders intact

**Chose:** B.

**Reason:** Those folders may later contain other content (workspace-level plugin.json, READMEs). Targeting the named generated files keeps the tool surgical and reversible. Same principle for `.compiled/`: list `skill-plugins/` and `marketplace.json` explicitly rather than wiping `.compiled/` (which would also blow away `~GOAL.md`-referenced legacy `marketplace.jsonc`).
