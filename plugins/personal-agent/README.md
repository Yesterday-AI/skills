<div align="center">
  <img src="../../logo.svg" width="90" alt="personal-agent" />

  <h1>personal-agent</h1>

  <p><em>Agent skills for human-AI collaboration and AI-as-expert workflows.</em></p>

  <p>
    A Claude Code plugin with generic skills for AI agents at <a href="https://arxiv.org/html/2311.02462v5#S6">Levels-of-AGI</a> 3-4 (Collaborator / Expert) -- stateful patrols, agent-to-agent orchestration, self-improvement, durable infra ops. Works for any team running long-running Claude Code agents.
  </p>

  <p>
    <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue"></a>
    <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-plugin-0A0A0A">
    <img alt="visibility" src="https://img.shields.io/badge/visibility-public-22C55E">
  </p>

</div>

---

## What personal-agent is

A curated set of skills that an AI agent uses to drive interactive work with light human supervision -- read its environment, pick up tasks, ship code, review its own work, persist fixes, learn from corrections.

**Audience:** the agent itself, not its operator. Operators install `personal-agent` so their AI agents can use these skills.

## What's in it

14 generic agent-skills:

| Skill | Purpose |
|---|---|
| agent-swarm | Multi-agent orchestration in isolated worktrees |
| agentic-news-digest | Curated team news digests via the full pipeline (sources, fact-check, relevance) |
| capability-check | Self-introspection at session start (tools / sub-agents / skills) |
| forward-momentum | Anti-paralysis discipline; tangible output per interaction |
| github-pr-review | Stateful PR review with inline comments + validation |
| github-workflow | Standard Git/GitHub workflows for autonomous agents |
| issue-patrol-routine | Periodic issue scan, classify into actionable queues |
| issue-to-pr-workflow | End-to-end issue -> implementation -> PR -> feedback loop |
| pm-patrol-routine | PM triage: PR completeness, close resolved issues |
| project-engine | Cron-driven autonomous project orchestration |
| project-tracking | Standardized agent project tracking with YAML frontmatter |
| review-patrol-routine | Stateful PR review patrol with heartbeat cycles |
| self-improving | Corrections become improvements; self-improving memory |
| systemic-persistence | Ensure fixes survive reboots; durable system solutions |

Plus cross-marketplace dependencies (auto-pulled via plugin.json):

| Plugin | Purpose |
|---|---|
| [creative-productivity](../../skills/concepts/creative-productivity) | Deliverables orchestrator (excalidraw + miro + reveal/marp + draw.io) |
| [para-memory-files](../../skills/capabilities/memory/para-memory-files) | Agent-side persistence using the PARA method |
| [office](../office) | Daily-work skills (excalidraw, exa search, GitHub, slack, web/x scrapers) -- maintained for humans, equally useful when an agent needs them |
| sunoflow (external, `lx-0/SunoFlow`) | AI music creation: songs, lyrics, sound effects, stem separation, music videos, playlist mgmt via the SunoFlow MCP server |

## Install

```bash
/plugin marketplace add Yesterday-AI/skills
/plugin install personal-agent@yesterday-public-plugins
```

Skills appear under `/personal-agent:<skill-name>`. Reload after edits with `/reload-plugins`.

### Local dev

```bash
claude --plugin-dir /path/to/personal-agent
```

## Why "personal-agent"

Part of Yesterday's plugin family alongside `ytstack` (engineering OS), `office` (daily-work), `personal-agent` (agent core), and `systems-operations` (ops core).

## Repo layout

```
personal-agent/
├── .claude-plugin/
│   └── plugin.json -> ../plugin.json
├── .cursor-plugin/
│   └── plugin.json -> ../plugin.json
├── plugin.json
├── skills/
├── README.md
├── LICENSE                   MIT
└── NOTICE                    attribution
```

## License

MIT. See [LICENSE](./LICENSE).

---

Maintained by [Yesterday](https://github.com/Yesterday-AI). Listed in the [Yesterday public plugin catalog](https://github.com/Yesterday-AI/skills).
