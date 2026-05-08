---
name: project-engine
description: >
  Autonomous project execution engine for AI agents. Orchestrates scheduled cron
  jobs per project using workflow templates (dev-autonomous, research, ops).
  Integrates PR-Gate, GitHub workflow, ROADMAP tracking, and human notification
  via project-tracking. Use when: setting up scheduled project work, running an
  autonomous session, or designing an agent's development loop.
  Builds on forward-momentum (philosophy) and implements it as a concrete system.
metadata:
  author: ManniTheRaccoon
  version: "1.0"
  category: ops
compatibility: >
  Requires: OpenClaw cron system, gh CLI (authenticated), git.
  Optional: Yesterday API (for agent consultation), ClawRAG (for knowledge lookup).
  Depends on: forward-momentum (philosophy), project-tracking (registry),
  github-workflow (branch/PR mechanics), software-craftsmanship (code quality).
---

# Project Engine 🏗️

> The execution layer for [Forward Momentum](../forward-momentum/SKILL.md).
>
> Forward Momentum defines the *philosophy* (every interaction → state change).
> Project Engine defines the *system* (workflows, schedules, PR gates, human routing).

## Overview

```
┌─────────────────────────┐
│  PROJECTS_TRACKING.md   │  ← Project registry (project-tracking skill)
│  - Project A: dev-auto  │
│  - Project B: research  │
│  - Project C: unscheduled│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  OpenClaw Cron Jobs     │  ← One job per scheduled project
│  - Job A → Workflow X   │
│  - Job B → Workflow Y   │
└────────┬────────────────┘
         │ triggers
         ▼
┌─────────────────────────┐
│  Workflow Template       │  ← This skill defines the steps
│  1. PR-Gate check        │
│  2. Work                 │
│  3. Artifact (PR/Doc)    │
│  4. Notify Lead (Human)  │
└─────────────────────────┘
```

## Project States

A project is either **scheduled** (has a cron job + workflow) or **unscheduled** (idea/observation, collecting notes).

| State | Meaning | Action |
|---|---|---|
| **Unscheduled** | Idea / Discovery / Observation | Collect notes, no autonomous work |
| **Scheduled** | Active work via cron job | Runs a workflow template per session |

To schedule a project: create an OpenClaw cron job whose prompt references this skill and specifies the workflow.

## Workflow Templates

---

### 1. `dev-autonomous` -- Full Development Cycle

For projects with a code repo, ROADMAP/Issues, and GitHub PR workflow.

**Session Protocol:**

```
STEP 1 -- PR-GATE (mandatory first step, never skip)
  Check for open PRs from last session:
    → gh pr list --state open --author @me --repo <REPO>
  If open PR exists:
    a) Read ALL comments and reviews: gh pr view <N> --comments
    b) Work through review action items
    c) Push fixes to the existing branch
    d) If all resolved → note completion in PR comment
    e) STOP here -- do NOT start new work until PR is merged/closed
  If no open PR → continue to Step 2

STEP 2 -- ORIENT
  Read the project's ROADMAP.md or GitHub Issues
  Identify the next actionable item
  Optional: consult another agent (e.g., Ken via Yesterday API)

STEP 3 -- EXECUTE
  Create a feature branch: git checkout -b feat/<descriptive-name>
  Implement the change (code, tests, docs)
  One feature/fix per session -- keep it small
  Follow conventional commits (feat:/fix:/chore:/docs:)

STEP 4 -- SHIP
  Push branch and create PR:
    gh pr create \
      --title "<type>: <description>" \
      --body "## Summary\n<what and why>\n\n## Changes\n<details>\n\n## Next Step\n<what comes after>" \
      --reviewer <REVIEWER> \
      --assignee @me
  Update ROADMAP.md with progress

STEP 5 -- NOTIFY
  Send summary to the project's Lead (Human)
  Include: PR link, key decisions, blockers, next step
  Route to correct human (see "Human Routing" below)
```

**Cron Prompt Template:**

```
Forward Momentum: dev-autonomous

Project: <PROJECT_NAME>
Repo: <OWNER/REPO>
ROADMAP: <path/to/ROADMAP.md>
Reviewer: <GITHUB_USERNAME>

Read the project-engine skill (skills/project-engine/SKILL.md).
Follow the dev-autonomous workflow strictly.
Read AGENTS.md for workspace conventions.
Resolve Lead (Human) from PROJECTS_TRACKING.md for notifications.
```

---

### 2. `research` -- Research & Documentation

For projects in exploration phase that produce structured documents.

**Session Protocol:**

```
STEP 1 -- ORIENT
  Read the project's research brief or open questions
  Check ClawRAG for existing knowledge on the topic

STEP 2 -- RESEARCH
  Use web search, Exa, ClawRAG, or agent consultation
  Focus on answering ONE specific question per session

STEP 3 -- DOCUMENT
  Write findings to a structured document (e.g., docs/<topic>.md)
  Include: sources, key takeaways, open questions
  Commit and push (direct to main OK for docs-only, PR for shared repos)

STEP 4 -- NOTIFY
  Brief summary to Lead (Human): what was found, what's still open
```

---

### 3. `ops` -- Operations & Maintenance

For infrastructure, monitoring, and deployment tasks.

**Session Protocol:**

```
STEP 1 -- HEALTH CHECK
  Run health checks / status commands for the service
  Check logs for errors or anomalies

STEP 2 -- ACT
  Issues found → fix, deploy, document
  Healthy → run scheduled maintenance (updates, cleanups, optimization)
  Follow the project's deploy procedure

STEP 3 -- LOG
  Update ops log or daily memory with findings
  If something broke → create a GitHub Issue

STEP 4 -- NOTIFY (only if actionable)
  Alert Lead (Human) about problems or completed maintenance
  Do NOT notify for routine "all clear" sessions
```

---

### 4. `code-review` -- Automated PR Validation

For maintainers and infrastructure admins. Validates incoming PRs against repository standards (CONTRIBUTING.md).

**Session Protocol:**

```
STEP 1 -- DISCOVER
  List open PRs where I am not the author:
    gh pr list --state open --json number,title,author,reviews --jq '.[] | select(.author.login != "@me")'
  Filter for PRs that need my attention (no review from me yet OR changes requested + updated).

STEP 2 -- ANALYZE
  For each target PR:
    a) Read the diff: gh pr diff <N>
    b) Read the repository's CONTRIBUTING.md or standards.
    c) Check specifically for:
       - Security violations (secrets, root users)
       - Architecture compliance (namespaces, labels)
       - Documentation (README, changelog)

STEP 3 -- ACT
  If violations found:
    Request Changes with specific line references and remediation steps.
    gh pr review <N> --request-changes --body "Violations found: ..."
  If compliant:
    Approve the PR.
    gh pr review <N> --approve --body "LGTM! 🚢"

STEP 4 -- REPORT
  Log the review actions in the project's tracking/memory.
  Notify Lead (Human) only if a PR is blocked by critical issues or ready to merge.
```

**Cron Prompt Template:**

```
Forward Momentum: code-review

Project: <PROJECT_NAME>
Repo: <OWNER/REPO>
Role: <ROLE>

Read skills/project-engine/SKILL.md and <REPO>/CONTRIBUTING.md.

TASK:
1. Identify open PRs in <REPO> needing review.
2. Validate against CONTRIBUTING.md standards (Security, Architecture, Docs).
3. Request Changes for violations; Approve if compliant.
4. Report actions taken.
```

---

## Human Routing

Notifications always go to the **Lead (Human)** from `PROJECTS_TRACKING.md`, not a hardcoded person.

**Resolution order:**

1. Read `PROJECTS_TRACKING.md` → find project row → `Lead (Human)` column
2. Look up the human's notification channel:
   - Workspace owner → `USER.md` (timezone, preferred channel)
   - Other humans → project's `Source of Truth` or agent config
3. Send via appropriate channel (Discord, Telegram, etc.)

**Example:**
```
| ID | Projekt | Lead (Human) | Lead (Agent) | ...
| CLW-RAG | ClawRAG | Alex | Manni | ...
| Y-PLAT | Platform | Sidney | Robby | ...
```
→ ClawRAG summaries go to **Alex**, Platform summaries go to **Sidney**.

**Fallback:** If Lead (Human) is unspecified or routing fails → notify workspace owner from `USER.md`.

## Scheduling Guide

### Recommended Frequencies

| Workflow | Frequency | Rationale |
|---|---|---|
| `dev-autonomous` | 2-4x daily | Enough to iterate; more = diminishing returns |
| `research` | 1-2x daily | Deep work needs focus, not frequency |
| `ops` | 1-2x daily | Health checks + maintenance windows |

### Multi-Project Example

```
08:30 UTC -- Project A (dev-autonomous)
12:30 UTC -- Project B (dev-autonomous)
16:30 UTC -- Project A (dev-autonomous)
20:30 UTC -- Project C (ops)
```

### Creating the Cron Job

```bash
openclaw cron create \
  --name "Forward Momentum: <PROJECT>" \
  --schedule "30 12 * * *" \
  --tz UTC \
  --model opus \
  --message "<paste workflow prompt from template above>"
```

## Integration Map

| Skill | Role |
|---|---|
| **forward-momentum** | Philosophy -- *why* we enforce action per session |
| **project-tracking** | Registry -- project list, Lead (Human), status definitions |
| **github-workflow** | Mechanics -- branch naming, PR commands, CI checks |
| **software-craftsmanship** | Standards -- PR descriptions, code quality, commit format |
| **clawrag-api** | Knowledge -- lookup during research, ingest during documentation |
| **yesterday-expert-app-api** | Consultation -- architectural decisions with other agents |

## Anti-Patterns 🚫

### `SESSION_WITHOUT_ARTIFACT`
Every session must produce something tangible: a PR, a document, a deployment, an issue.
"I read the ROADMAP and planned next steps" is NOT an artifact. Ship something.

### `PR_PILE`
Never open a new PR while the last one is still open. Step 1 (PR-Gate) prevents this.
If you skip the gate, you create review debt that compounds.

### `NOTIFICATION_SPAM`
Don't notify the human for routine sessions. Notify when:
- A PR needs review
- Something is blocked on their input
- Something broke
- A milestone was reached

### `HARDCODED_HUMAN`
Never hardcode `notify Alex` in a cron prompt. Always resolve from `PROJECTS_TRACKING.md`.
Projects change owners. Prompts shouldn't need to.

---

*"Input → Impact → Output. Every session ships."* 🦝
