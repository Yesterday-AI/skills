<div align="center">
  <img src="logo.svg" width="90" alt="yesterday" />
  
  <h1>skills</h1>

  <p><em>Yesterday's PUBLIC plugin catalog for Claude Code and Cursor.</em></p>

  <p>
    A unified marketplace + monorepo of agent skills and bundled plugins.
  </p>

  <p>
    <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue"></a>
    <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-marketplace-0A0A0A">
    <img alt="Cursor" src="https://img.shields.io/badge/Cursor-marketplace-0A0A0A">
    <img alt="visibility" src="https://img.shields.io/badge/visibility-public-22C55E">
  </p>
</div>

---

## Install

### Claude Code

```bash
/plugin marketplace add Yesterday-AI/skills
/plugin
```

Then install plugins individually:

```bash
/plugin install office@yesterday-public-plugins
/plugin install personal-agent@yesterday-public-plugins
/plugin install systems-operations@yesterday-public-plugins
# ... etc
```

### Cursor

Cursor reads the same marketplace catalog -- the manifest is mirrored at `./.cursor-plugin/marketplace.json`. See [Cursor plugin docs](https://cursor.com/docs/plugins) for the latest install flow.

### Local dev

```bash
git clone https://github.com/Yesterday-AI/skills
cd skills
node compile.mjs                       # build .compiled/ + manifest copies
/plugin marketplace add ./             # add this repo as a local marketplace
```

No auth required -- this catalog is public.

---

## What's in the catalog

22 plugins total: 1 external, 4 bundles, 2 MCP servers, 15 standalone skills.

### Bundles (`./plugins/`)

| Plugin | Purpose |
|---|---|
| [office](./plugins/office) | Daily-work core -- 5 generic skills (exa search, slack, GitHub, web/x scrapers) + creative-productivity, excalidraw-diagram, wrapup as dependencies |
| [office-extras](./plugins/office-extras) | Daily-work extras tier -- 4 SaaS integrations (Figma, Miro, Voxtral TTS, VRR) |
| [personal-agent](./plugins/personal-agent) | Agent core -- 14 generic agent skills (multi-agent, patrols, self-improvement) |
| [systems-operations](./plugins/systems-operations) | Ops core -- 6 skills (opentofu, railway-deploy, butler-deploy, land-and-deploy, canary, setup-deploy) |

### MCP servers (`./plugins/`)

Single-source MCP-server plugins -- depend on one of these from a bundle instead of redeclaring the server (avoids the Claude Code "MCP server skipped -- same command/URL" dedupe warning).

| Plugin | Purpose |
|---|---|
| [y-exa](./plugins/y-exa) | Exa semantic-web-search MCP (`npx exa-mcp-server`) -- prompts for the API key via `userConfig` |
| [y-context7](./plugins/y-context7) | Context7 live-docs MCP (`npx @upstash/context7-mcp`) -- no API key |

### Standalone skills (`./skills/`)

#### Capabilities

| Skill | Purpose |
|---|---|
| [voxtral-tts-api](./skills/capabilities/tts/voxtral-tts-api) | Mistral Voxtral TTS API client |

#### Productivity

| Skill | Purpose |
|---|---|
| [creative-productivity](./skills/productivity/creative-productivity) | Deliverables orchestrator (excalidraw + miro + reveal/marp + draw.io) |
| [excalidraw-diagram](./skills/productivity/excalidraw-diagram) | Hand-drawn diagrams as Excalidraw JSON |
| [figma-console-mcp](./skills/productivity/figma-console-mcp) | Figma + FigJam + Slides via MCP |
| [miro-board](./skills/productivity/miro-board) | Miro board content via MCP |
| [web-design](./skills/productivity/web-design) | Build distinctive, production-grade frontend interfaces |
| [chat-recall](./skills/productivity/chat-recall) | Search authorized local Codex and Claude transcript excerpts |
| [jamie](./skills/productivity/jamie) | Retrieve meetings and create source-grounded records or extractions |
| [rename](./skills/productivity/rename) | Improve task titles through available APIs or produce a title proposal |
| [yesterday-app-style](./skills/productivity/yesterday-app-style) | Calm product UI rules with a self-contained design contract |
| [yesterday-pages](./skills/productivity/yesterday-pages) | Branded HTML reports, visual stories and interactive explainers |

#### Development operations

| Skill | Purpose |
|---|---|
| [create-shareable-skill](./skills/operations/create-shareable-skill) | Author a catalog-ready skill: quality gate, placement routing, scaffold, docs, PR |
| [wrapup](./skills/operations/wrapup) | End-of-conversation sweep: propose doc/plan/memory updates + paste-ready resume prompt |
| [copilot-cowork-plugin](./skills/operations/copilot-cowork-plugin) | Build and locally validate Microsoft 365 skill packages |

#### Travel

| Skill | Purpose |
|---|---|
| [vrr-efa-api](./skills/travel/vrr-efa-api) | VRR (Verkehrsverbund Rhein-Ruhr) live transit API |

### External

| Plugin | Source | Purpose |
|---|---|---|
| ytstack | github `Yesterday-AI/ytstack` | Engineering OS for AI coding agents -- project-OS artifact discipline + curated skill wrappers |

### Deprecated

Not published in the marketplace. The source stays in the repo for reference; existing installs are dropped via `renames` (`null`) in `./marketplace.json`.

| Skill | Purpose | Deprecated |
|---|---|---|
| [paperclip-api](./skills/operations/paperclip-api) | Paperclip AI REST API client (companies, agents, issues, budgets) | 2026-10-14 |
| [para-memory-files](./skills/capabilities/memory/para-memory-files) | PARA-method file-based agent memory | 2026-10-14 |

---

## Compile pipeline

`compile.mjs` discovers `skills/**/SKILL.md`, generates per-skill plugin scaffolds in `.compiled/skill-plugins/`, and produces `.compiled/marketplace.json` from the top-level header (`./marketplace.json`) merged with auto-discovered bundles + standalone.

To deprecate a standalone skill, set `deprecated: true` in its `SKILL.md` frontmatter (compile then skips it), map its name to `null` under `renames` in `./marketplace.json`, and remove it from every bundle's `dependencies`. Claude Code's marketplace format has no deprecated state; `renames: null` is the documented way to drop a removed plugin from users' `enabledPlugins`.

```bash
node clean.mjs    # wipe .compiled/ + root manifest copies
node compile.mjs  # rebuild from sources (rewrites bundle manifest copies)
```

See [`.ytstack/DECISIONS.md`](./.ytstack/DECISIONS.md) for the rationale (single Node script, no build infra, copies instead of symlinks since 2026-09-03).

---

## License

MIT. See [LICENSE](./LICENSE). Listed plugins carry their own license (mostly MIT). External plugins are fetched from their upstream repos and not redistributed.

---

Maintained by [Yesterday](https://github.com/Yesterday-AI).
