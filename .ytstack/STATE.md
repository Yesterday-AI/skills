---
project: skills
slug: skills
last_updated: 2026-05-22T00:00:00Z
current_milestone: M002
active_slice: S03
active_task: none
---

# State

**Status:** M002 in progress. Premium Infographic Mode is functional end-to-end and proven by render. LANDED in the `excalidraw-diagram` skill:
- `references/render_template.html` -- `--theme light` now respects the file's `viewBackgroundColor` (cream canvas). [S01]
- `references/color-palette.md` -- "Premium Infographic Palette" section (cream bg, 6-hue state-coded pastels, highlighter swipe). [S01]
- `SKILL.md` -- "Premium Infographic Mode (opt-in)" section: font=1, roughness=1, cream bg, signature-elements list, one-thesis + mandatory bottom-summary rule, defaults preserved. [S01/S02]
- `references/libraries/` -- 5 MIT OSS libs bundled + previews (stick-figures, bubbles, emojis, sticky-notes, awesome-icons) + README updated. [S04]
- `references/examples/rag-infographic.excalidraw` + `.png` -- worked proof example (problem->solution RAG explainer, all signature elements). [S04]
- `references/signature-elements.md` -- full rich element catalog (card grid, concept-icon system, insight panels, formula annotation, combiner glyph, color-coded keywords, tensor grids, token columns, styles-to-avoid). Built from 25+ Akshay Pachaar examples (@akshay_pachaar; corpus stored gitignored under `references/~skill-designing/pachaar-examples/`). SKILL.md premium section points to it. [S02/S03]
  - 2026-05-22 enrichment from the function-calling+MCP / DBSCAN / attention batch: added poster frame, macOS code window, multi-instance icon grid, footnote/disclaimer, vertical title accent bar, multi-color title, author signature card, color-matched annotation, set/region (concept-space) diagram + single-concept-poster layout. Cover/carousel (gradient+serif+carbon) flagged as non-target family.
- `references/examples/set-diagram.{excalidraw,png}` -- 2nd worked proof example (DBSCAN concept-space poster): poster frame + overlapping set circles + color-matched leader annotations + eps measurement line + @handle pill. Render-verified twice + zoom-crop. Covers the concept-space layout the rag example doesn't.
- **Fonts (tested 2026-05-22):** read the bundle's authoritative `FONT_FAMILY` constant -- 8 built-ins (1 Virgil, 2 Helvetica, 3 Cascadia, 5 Excalifont, 6 Nunito, 7 Lilita One, 8 Comic Shanns, 9 Liberation Sans; 4 unused). Corrected the WRONG KNOWLEDGE.md note (had claimed 1=Excalifont/2=Nunito/3=Comic Shanns). Custom fonts NOT supported (no registerFont export; unregistered family falls back -- runtime-verified). SKILL.md font table expanded (Lilita One titles, Nunito labels); `references/font-catalog.png` shipped as visual swatches. KNOWLEDGE.md updated.
- `references/examples/typography-grid.{excalidraw,png}` -- 3rd worked example: 2x2 premium card grid that exercises the full type ramp (Lilita One `7` headline + blue swipe + accent bar, Nunito `6` card-title pills + source mark, Cascadia `3` mono metric chips, Excalifont `5` hand-drawn body + thesis). Render-verified 4x (2 full passes + title zoom + card zoom); confirms all four font tiers render distinct.
- `references/examples/yesterday-ci-infographic.{excalidraw,png}` -- 4th worked example + a 2nd opt-in THEME: "Yesterday CI — Editorial Treatment" (clean roughness 0, cream canvas, Yesterday orange `#FC4E14`/gold/semantic, CI signatures: mono kicker, orange tick, top accent bars, verdict bar, by-Yesterday wordmark, mono footer). Render-verified 4x. Documented in `color-palette.md` ("Yesterday CI -- Editorial Treatment" section); the Yesterday palette was already the skill DEFAULT, this adds the editorial treatment + type ramp. Font caveat: real CI fonts (Source Serif 4/DM Sans/IBM Plex Mono) NOT in renderer -> mapped to Lilita One/Nunito/Cascadia; serif display not reproducible. Brand source-of-truth + docs/live divergence: see memory `yesterday-brand-ci`.
- `references/libraries/infographic-elements.excalidrawlib` (26 items) + `-preview.png` -- IN-HOUSE drop-in library = executable counterpart to `signature-elements.md` (atoms / concept icons / data-viz / composites, pre-styled premium palette). Generator: `~skill-designing/builds/build_library.py` (source of truth, NOT an upstream download -- don't curl-refresh). Render-verified via preview grid. libraries/README.md + signature-elements.md updated to point to it.
- `references/examples/{innovation-pipeline,three-exit-framework,micro-venture-studio}.{excalidraw,png}` -- 3 story-driven examples sourced from the llm-wiki strategy articles (genericized, no internal names) and built BY DOGFOODING `infographic_builder.py`. Distinct storyline layouts: linear pipeline (idea->4 phases->3 exits), decision fork (project -> 3 outcomes), contrast+principles (classic vs studio + 4 rules). Render-verified (pipeline 1pass+zoom; exits/studio 2 passes + zoom). Generator: `~skill-designing/builds/build_wiki_examples.py`. Wiki vault: registry-located `lxw`; Read-tier only (grep index + read articles), no wiki writes.
- **Dark Technical Reference theme (3rd opt-in theme, 2026-05-22):** user flagged the dark "Memory in Hermes Agent" as a good example -> corrected my earlier mis-classification (flat dark-mode IS reproducible via dark canvas + `--theme light`; only glowing-NEON is avoid). Added: `DARK` palette + `meter()`/`gauge()`/`numbered_circle()`/`top_accent()` methods to `infographic_builder.py`; `color-palette.md` "Dark Technical Reference -- Treatment" section; signature-elements.md §5 refined (flat-dark OK vs glowing-neon avoid); 6 new lib items (Capacity meter bar, Gauge ring, Step strip, Checkbox, Pro/con pair, Speech bubble left-tail) -> lib now **32 items** + preview regenerated. Examples: `references/examples/dark-agent-memory.{excalidraw,png}` (tier columns + file cards w/ meters + gauge + step-strip + pro/con) + `dark-inference-grid.{...}` (dark card-grid). Generator `.design/builds/build_dark_examples.py`. Gradient header NOT native in exportToSvg -> approximated with stacked solid segments (the one limitation).
- **Top-accent alignment fix:** square full-width top bars poked past rounded card corners -> `Scene.top_accent()` insets by the corner radius + rounds its ends. Applied to dark-inference-grid, yesterday-ci-infographic, innovation-pipeline, micro-venture-studio (all re-shipped). Rule documented in color-palette.md.
- `references/infographic_builder.py` -- SHIPPED composition layer (the answer to "why hand-write 100+ element dicts?"). A library gives shapes, never layout; this places library items by name (`Scene.place`) + adds connective tissue (`title`/`arrow(numbered=)`/`pill`/`thesis`) + `save()`. Palettes `PREMIUM`/`YESTERDAY` + `FONT` IDs as constants. Smoke-test in `__main__` render-verified (placed Query envelope + Vector DB from the lib, 13 elements from ~8 calls). SKILL.md Step 5 documents it as the recommended path for premium/complex infographics. The gitignored `~skill-designing/builds/build_*.py` are now design-time-only (could be refactored onto this builder; not required).

**Incident 2026-05-22:** another agent reverted the two skill-file edits (render_template.html, color-palette.md); recovered + re-verified (corner pixel `#F7F3E9`). `.ytstack/` + `/tmp` artifacts were untouched.

**Recovery note:** much of S01/S02/S04 landed informally during the recovery push (not via per-task summarize ceremony) on user's "mach weiter" + frustration with ceremony overhead. Slice checkboxes NOT all flipped -- reconcile if doing formal close.

**S03 conceptual/storytelling layer -- DONE (2026-05-22):** SKILL.md premium section now has "From research to storyline (the conceptual layer)" -- distill->one thesis->pick narrative shape (transformation/journey/fork/contrast/dissection/arguing-enumeration, each mapped to a layout + worked example)->arc (hook/tension/payoff + narrator)->reading-order=story-order. Quality Checklist gained a "Storyline (premium)" block (one thesis / shape chosen / arc present / reading-order=story-order).

**Folder rename:** the gitignored design-work dir `~skill-designing/` is now `.design/` (root .gitignore line 38 `.design/`; references/.gitignore reduced to `__pycache__/`+`.venv/`). STATE/KNOWLEDGE paths that still say `~skill-designing/` mean `.design/`. Generators live in `.design/builds/`.

**Next action (remaining):** S02 element-templates.md premium templates + opencoredev sizing formulas. Then formal verification + git stage.

**M001 (done):** `create-shareable-skill` standalone catalog skill at `skills/operations/create-shareable-skill/` + contributor docs; marketplace/compile infra. Executed directly (no formal slice/task pass) on explicit user instruction. `.agents/` placement reversed on user review (see DECISIONS.md supersede entry).

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
