---
project: skills
slug: skills
last_updated: 2026-05-15T11:00:00Z
current_milestone: M001
active_slice: none
active_task: none
---

# State

**Status:** M001 done -- `create-shareable-skill` is a standalone catalog skill at `skills/operations/create-shareable-skill/` + contributor docs updated. Executed directly (no formal slice/task pass) on explicit user instruction. Initial `.agents/` placement was reversed on user review (see DECISIONS.md supersede entry).

**Next action:** None pending for M001. Run `ytstack:reassess-roadmap` if continuing.

**Catalog context:** Public catalog live at `Yesterday-AI/skills` with 14 plugins (1 external + 4 bundles + 10 standalone). Compile pipeline working, marketplace symlinks generated, GitHub Actions workflow in place. Open question on plugin install path (cache resolution).

**2026-05-15 marketplace surgery:** `sunoflow` external listing moved out to `lx-0/skills` (lx-0's personal public catalog). `personal-agent` no longer depends on it. README + plugin counts updated. Commit `8dafe09`.

## What's done

- Compile pipeline (`compile.mjs`, `clean.mjs`) -- symlink-based; auto-scaffolds bundle `.claude-plugin` + `.cursor-plugin` symlinks
- Top-level `marketplace.json` header with `name=yesterday-public-plugins`, `allowCrossMarketplaceDependenciesOn=["claude-plugins-official"]`, externals incl. `ytstack` via github source
- 4 bundle plugins (office, office-extras, personal-agent, systems-operations) -- canonical `plugin.json` at bundle root, editor-folder manifests symlinked
- 9 standalone skills under `skills/<category>/<slug>/` (concepts, capabilities, productivity, development-operations, travel)
- OSS scaffold: README, LICENSE (MIT), CONTRIBUTING, NOTICE, AGENTS.md
- `.ytstack/` project memory (this file + DECISIONS, KNOWLEDGE, RUNTIME, PROJECT, PREFERENCES)
- `.agents/skills/audit-skills/` -- 3-axis repo audit skill (leaks, consistency, spec compliance)
- `skills/operations/create-shareable-skill/` -- standalone authoring skill: intake → quality gate → catalog + standalone/bundle placement → scaffold → compile+audit → docs → PR (M001; counterpart to audit-skills)
- GitHub Actions: `compile.yml` (auto-recompile on main push, PAT-pushed via `COMPILE_PUSH_TOKEN`, bot identity from `vars.BOT_NAME` / `vars.BOT_EMAIL`); `secret-scan.yml` (gitleaks)
- Repo created on GitHub (Yesterday-AI/skills, public), 12 topics set
- Sister repo `Yesterday-AI/yesterday-skills` (private catalog) brought to parity: same compile pipeline, OSS scaffold, `.ytstack/`, and as of 2026-05-13 also `compile.yml` + folder/name parity rule + normalized bundle READMEs
- 2026-05-13: removed install-breaking cross-marketplace dep (`skill-creator@claude-plugins-official`) from `plugins/systems-operations/plugin.json` -- `/doctor` was erroring on clean installs (see DECISIONS.md)

## Open

### Critical -- blocks plugin install

- **Cache symlink resolution unclear.** After `/plugin install web-design@yesterday-public-plugins`, the plugin shows enabled in `/plugins` but no skills appear in `/skills`. Cache at `~/.claude/plugins/cache/yesterday-public-plugins/web-design/<sha>/skills/` was observed empty. The Claude Code spec claims "symlinks are preserved in the cache, resolve at runtime" -- but the observed cache state contradicts that. Needs proper investigation BEFORE any code change:
  - `readlink` the cache-side symlinks to see actual target string
  - Compare cache `<sha>` against latest commit -- could be stale
  - `/plugin marketplace update` then re-test
  - Search GitHub issues for `actions/checkout` symlink dereferencing
  - Check what `git clone` does with symlinks across platforms

### Stale content in user-facing files (cleanup needed)

- `plugins/systems-operations/README.md` still lists `skill-creator` as a cross-marketplace dep in its "What's in it" table -- the dep was removed from `plugin.json` 2026-05-13. README must be updated to match.
- `plugins/systems-operations/README.md` has an internal-perspective leak: "the deploy-arc that comes after `ytstack:ship` and `ytstack:document-release` (handled by `ytstack` core in M011)" -- the `M011` milestone reference is internal framing, should be scrubbed per the no-internal-perspective rule.

### Architectural questions surfaced

- Should we adopt dotagents-style distribution (`.agents/skills/`, `agents.toml`, `agents.lock`) alongside or instead of marketplace catalog?
- If the cache-symlink-resolution is genuinely a Claude Code limitation, what's the right architecture? (Don't decide without evidence. Don't refactor compile.mjs without explicit approval.)

### Cross-repo artifact (context, not a task here)

- AI strategy doc created 2026-05-13 at `company-orga/03_technologies/32_strategy/04_ai-skills-und-plugins.md` -- explains skills/plugins as Yesterday's knowledge- + tool-sharing layer. Not yet linked from the `company-orga` README index; the `37_concepts/agentic-engineering/agent-skills/` stub could cross-reference it.

## Recent summaries

(No T##-SUMMARY.md entries yet -- work has been ad-hoc, pre-milestone.)
