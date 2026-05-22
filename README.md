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
node compile.mjs                       # build .compiled/ + symlinks
/plugin marketplace add ./             # add this repo as a local marketplace
```

No auth required -- this catalog is public.

---

## What's in the catalog

18 plugins total: 1 external, 5 bundles, 2 MCP servers, 10 standalone skills.

### Bundles (`./plugins/`)

| Plugin | Purpose |
|---|---|
| [office](./plugins/office) | Daily-work core -- 6 generic skills (exa search, excalidraw, slack, GitHub, web/x scrapers) |
| [office-extras](./plugins/office-extras) | Daily-work extras tier -- 4 SaaS integrations (Figma, Miro, Voxtral TTS, VRR) |
| [personal-agent](./plugins/personal-agent) | Agent core -- 14 generic agent skills (multi-agent, patrols, self-improvement) |
| [systems-operations](./plugins/systems-operations) | Ops core -- 6 skills (opentofu, railway-deploy, butler-deploy, land-and-deploy, canary, setup-deploy) |
| [webflow](./plugins/webflow) | Ships the Webflow MCP server (`.mcp.json`, HTTP/OAuth) + the `webflow` skill -- manage Webflow sites (pages, CMS, assets, styles, publish) |

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
| [para-memory-files](./skills/capabilities/memory/para-memory-files) | PARA-method file-based agent memory |
| [voxtral-tts-api](./skills/capabilities/tts/voxtral-tts-api) | Mistral Voxtral TTS API client |

#### Productivity

| Skill | Purpose |
|---|---|
| [creative-productivity](./skills/concepts/creative-productivity) | Deliverables orchestrator (excalidraw + miro + reveal/marp + draw.io) |
| [excalidraw-diagram](./skills/productivity/excalidraw-diagram) | Hand-drawn diagrams as Excalidraw JSON |
| [figma-console-mcp](./skills/productivity/figma-console-mcp) | Figma + FigJam + Slides via MCP |
| [miro-board](./skills/productivity/miro-board) | Miro board content via MCP |
| [web-design](./skills/concepts/web-design) | Build distinctive, production-grade frontend interfaces |

#### Development operations

| Skill | Purpose |
|---|---|
| [create-shareable-skill](./skills/operations/create-shareable-skill) | Author a catalog-ready skill: quality gate, placement routing, scaffold, docs, PR |
| [paperclip-api](./skills/development-operations/paperclip-api) | Paperclip AI REST API client (companies, agents, issues, budgets) |

#### Travel

| Skill | Purpose |
|---|---|
| [vrr-efa-api](./skills/travel/vrr-efa-api) | VRR (Verkehrsverbund Rhein-Ruhr) live transit API |

### External

| Plugin | Source | Purpose |
|---|---|---|
| ytstack | github `Yesterday-AI/ytstack` | Engineering OS for AI coding agents -- project-OS artifact discipline + curated skill wrappers |

---

## Compile pipeline

`compile.mjs` discovers `skills/**/SKILL.md`, generates per-skill plugin scaffolds in `.compiled/skill-plugins/`, and produces `.compiled/marketplace.json` from the top-level header (`./marketplace.json`) merged with auto-discovered bundles + standalone.

```bash
node clean.mjs    # wipe .compiled/ + root symlinks
node compile.mjs  # rebuild from sources
```

See [`.ytstack/DECISIONS.md`](./.ytstack/DECISIONS.md) for the rationale (single Node script, no build infra, symlink-first strategy).

---

## License

MIT. See [LICENSE](./LICENSE). Listed plugins carry their own license (mostly MIT). External plugins are fetched from their upstream repos and not redistributed.

---

Maintained by [Yesterday](https://github.com/Yesterday-AI).
