---
project: skills
slug: skills
last_updated: 2026-05-13T00:00:00Z
current_milestone: none
active_slice: none
active_task: none
---

# State

**Status:** Public catalog live at `Yesterday-AI/skills` with 14 plugins (1 external + 4 bundles + 9 standalone). Compile pipeline working, marketplace symlinks generated, GitHub Actions workflow in place. Open question on plugin install path (cache resolution).

## What's done

- Compile pipeline (`compile.mjs`, `clean.mjs`) -- symlink-based; auto-scaffolds bundle `.claude-plugin` + `.cursor-plugin` symlinks
- Top-level `marketplace.json` header with `name=yesterday-public-plugins`, `allowCrossMarketplaceDependenciesOn=["claude-plugins-official"]`, externals incl. `ytstack` via github source
- 4 bundle plugins (office, office-extras, personal-agent, dev-operations) -- canonical `plugin.json` at bundle root, editor-folder manifests symlinked
- 9 standalone skills under `skills/<category>/<slug>/` (concepts, capabilities, productivity, development-operations, travel)
- OSS scaffold: README, LICENSE (MIT), CONTRIBUTING, NOTICE, AGENTS.md
- `.ytstack/` project memory (this file + DECISIONS, KNOWLEDGE, RUNTIME, PROJECT, PREFERENCES)
- `.agents/skills/audit-skills/` -- 3-axis repo audit skill (leaks, consistency, spec compliance)
- GitHub Actions: `compile.yml` (auto-recompile on main push, PAT-pushed via `COMPILE_PUSH_TOKEN`, bot identity from `vars.BOT_NAME` / `vars.BOT_EMAIL`); `secret-scan.yml` (gitleaks)
- Repo created on GitHub (Yesterday-AI/skills, public), 12 topics set
- Sister repo `Yesterday-AI/yesterday-skills` (private catalog) brought to parity: same compile pipeline, OSS scaffold, `.ytstack/`

## Open

### Critical -- blocks plugin install

- **Cache symlink resolution unclear.** After `/plugin install web-design@yesterday-public-plugins`, the plugin shows enabled in `/plugins` but no skills appear in `/skills`. Cache at `~/.claude/plugins/cache/yesterday-public-plugins/web-design/<sha>/skills/` was observed empty. The Claude Code spec claims "symlinks are preserved in the cache, resolve at runtime" -- but the observed cache state contradicts that. Needs proper investigation BEFORE any code change:
  - `readlink` the cache-side symlinks to see actual target string
  - Compare cache `<sha>` against latest commit -- could be stale
  - `/plugin marketplace update` then re-test
  - Search GitHub issues for `actions/checkout` symlink dereferencing
  - Check what `git clone` does with symlinks across platforms
- **Compile workflow PAT.** `COMPILE_PUSH_TOKEN` set up but failed last run with 403 ("Permission to Yesterday-AI/skills.git denied to yesterday-bot"). User regenerating PAT scoped to `Yesterday-AI` org with `Contents: Read and write`. Needs verification that next push triggers a successful regenerate-and-push cycle.

### Sister-repo (`yesterday-skills`) leftover from earlier audit

Reported but not yet fixed (user may handle separately):

- `yesterday-dev-operations` deps target `development-operations` -- public plugin is named `dev-operations` (install-blocking)
- `marketplace.json` missing `allowCrossMarketplaceDependenciesOn: ["yesterday-public-plugins"]` (install-blocking for cross-mp deps)
- 5 stale bundle READMEs (heading still `# yastack-internal` etc., reference old marketplace names)
- Description leaks in `yesterday-office/plugin.json` and `yesterday-personal-agent/plugin.json` (still mention `ydstack`, `yastack`, `ystacks`, `yopstack-internal`)

### Architectural questions surfaced

- Should we adopt dotagents-style distribution (`.agents/skills/`, `agents.toml`, `agents.lock`) alongside or instead of marketplace catalog?
- If the cache-symlink-resolution is genuinely a Claude Code limitation, what's the right architecture? (Don't decide without evidence. Don't refactor compile.mjs without explicit approval.)

## Recent summaries

(No T##-SUMMARY.md entries yet -- work has been ad-hoc, pre-milestone.)
