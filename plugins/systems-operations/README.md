<div align="center">
  <img src="../../logo.svg" width="90" />

  <h1>systems-operations</h1>

  <p><em>Ops skills for Claude Code agents. Provision, deploy, observe.</em></p>

  <p>
    A Claude Code plugin with generic skills for infrastructure-provisioning, deployment, and post-deploy observability. Works for any team running Claude Code agents that touch real infra.
  </p>

  <p>
    <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue"></a>
    <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-plugin-0A0A0A">
    <img alt="visibility" src="https://img.shields.io/badge/visibility-public-22C55E">
  </p>

</div>

---

## What systems-operations is

The ops layer of the Yesterday plugin family. Skills for the deploy-arc that comes after `ytstack:ship` and `ytstack:document-release` (handled by `ytstack` core in M011): provisioning new infra, executing deploys, watching for post-deploy regressions.

**Audience:** Claude Code agents (and their operators) that touch real infra -- K8s clusters, cloud environments, deployments. Operators install `systems-operations` so their agents have a curated set of patterns for safe deploy + observe loops.

## What's in it

6 generic skills:

| Skill | Purpose |
|---|---|
| opentofu | Autonomous infrastructure provisioning |
| railway-deploy | Deploy/manage/debug services on Railway via CLI |
| butler-deploy | Publish HTML5 game builds to itch.io via butler |
| land-and-deploy | Merge + deploy + canary-checks prod + offer revert |
| canary | Post-deploy visual monitor (console errors, perf regressions, broken links) |
| setup-deploy | Initialize deploy infrastructure |

Plus one cross-marketplace dependency (auto-pulled via plugin.json):

| Plugin | Purpose |
|---|---|
| `skill-creator` (from `claude-plugins-official`) | Meta-skill for creating new agent skills |

## Install

```bash
/plugin marketplace add Yesterday-AI/skills
/plugin install systems-operations@yesterday-public-plugins
```

Skills appear under `/systems-operations:<skill-name>`.

### Local dev

```bash
claude --plugin-dir /path/to/systems-operations
```

## Why "systems-operations"

Part of Yesterday's plugin family alongside `ytstack` (engineering OS), `office` (daily-work), `personal-agent` (agent core), and `systems-operations` (ops core).

## Repo layout

```
systems-operations/
├── .claude-plugin/
│   └── plugin.json -> ../plugin.json
├── .cursor-plugin/
│   └── plugin.json -> ../plugin.json
├── plugin.json
├── skills/
├── README.md
├── LICENSE                     MIT
└── NOTICE                      attribution
```

## License

MIT. See [LICENSE](./LICENSE).

---

Maintained by [Yesterday](https://github.com/Yesterday-AI). Listed in the [Yesterday public plugin catalog](https://github.com/Yesterday-AI/skills).
