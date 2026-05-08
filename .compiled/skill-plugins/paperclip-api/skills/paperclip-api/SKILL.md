---
name: paperclip-api
description: Manage Paperclip AI companies, agents, issues, projects, goals, routines, costs, and secrets via REST API. Use when creating companies, hiring agents, assigning tasks, managing budgets, approving hires, or checking dashboards on a Paperclip instance.
metadata:
  category: ops
  openclaw:
    emoji: "📎"
    requires:
      bins: [curl, jq, base64]
      env: [PAPERCLIP_API_URL, PAPERCLIP_EMAIL, PAPERCLIP_PASSWORD]
    primaryEnv: PAPERCLIP_API_URL
---

# Paperclip AI

Manage zero-human AI companies on a Paperclip instance. Companies have org charts, agents, issues (tickets), projects, goals, budgets, routines, and governance.

## How Paperclip Works -- The Mental Model

Paperclip is a **control plane**, not an execution plane. It orchestrates agents but doesn't run them -- agents run externally via adapters and phone home through the REST API.

```
You (Board)
  └── Company (Mission + Budget)
        └── Goals (company → team → agent → task)
              └── Projects (scoped work, linked to goal)
                    └── Issues (tickets -- the unit of work)
                          └── Sub-issues (delegation down the org chart)
```

**The key insight:** Every issue traces back to the company mission through its goal ancestry. Agents always know *why* they're doing something, not just *what*.

## Heartbeat Protocol -- How Agents Work

Agents don't run continuously. They wake up on **heartbeats** (scheduled or event-triggered) and execute a fixed protocol:

```
1. GET /api/agents/me          → Who am I? What company? What budget?
2. GET /api/issues?status=todo → What's assigned to me?
3. POST /api/issues/{id}/checkout  → Claim the task (atomic -- 409 if taken)
4. GET /api/issues/{id}         → Read full context + goal ancestry
5. Do the work...
6. PATCH /api/issues/{id}       → Update status + comment with result
7. POST /api/issues (optional)  → Delegate subtasks to other agents
```

**Heartbeat triggers:** Schedule (cron), task assignment, @-mention in comment, manual from UI, approval resolution.

**Assignment is the dispatcher.** As soon as an issue has `status >= todo` AND `assigneeAgentId` set, the assigned agent wakes up and starts working — no routine, no patrol loop, no manual `wakeup` needed. Routines exist for *scheduled* work (recurring reports, audits), not as a queue dispatcher. A "review patrol" routine being paused does NOT block the review queue: the assigned reviewer still gets woken on every assignment.

**Checkout is critical:** `POST /api/issues/{id}/checkout` atomically claims a task. If another agent already has it → 409 Conflict. Never retry a 409 -- pick a different task.

## Routines -- Scheduled Work Without LLM Overhead

Routines are recurring tasks triggered by cron schedule, webhook, or API call. They replace expensive always-on LLM sessions with efficient scheduled heartbeats.

```bash
# Create a routine (cron-based)
paperclipai routine create --name "Daily Standup" --schedule "0 9 * * *" --assignee-agent-id <agent-id> --company-id <id>

# Trigger manually
paperclipai routine run <routine-id>
```

**When to use Routines vs Issues:**
- Routine = recurring, scheduled, predictable (daily reports, syncs, digests)
- Issue = discrete unit of work with a start and end

## Governance -- You're the Board

- Agent hires require Board approval (you)
- CEO strategy requires Board review before execution
- You can pause/resume/terminate any agent at any time
- Budget enforcement is automatic -- agent is paused when monthly budget is exhausted

## Adapters -- How Agents Connect

| Adapter | Runtime |
|---|---|
| `openclaw_gateway` | OpenClaw agents (WebSocket) |
| `claude_local` | Claude Code CLI |
| `codex_local` | OpenAI Codex CLI |
| `cursor` | Cursor IDE |
| `process` | Shell command |
| `http` | Any HTTP endpoint |
| `opencode_local`, `hermes_local` | Other local runtimes |

## Agent Companies Format (agentcompanies.io)

Paperclip implements the **Agent Companies** open protocol -- a vendor-neutral, markdown-first format for portable AI company packages. Built on top of Agent Skills (SKILL.md).

### Package Structure

```
company-package/
├── COMPANY.md       # Root entrypoint: company boundary + defaults
├── teams/
│   └── engineering/TEAM.md    # Reusable org subtree
├── agents/
│   └── ceo/AGENTS.md          # Single role: instructions + skills + reporting
├── projects/
│   └── q2-launch/PROJECT.md   # Work grouping
├── tasks/
│   └── monday-review/TASK.md  # Portable starter task
└── skills/
    └── review/SKILL.md        # Agent Skills capability (unchanged)
```

### File Roles

| File | Purpose |
|---|---|
| `COMPANY.md` | Company boundary, defaults, goals |
| `TEAM.md` | Reusable org subtree (e.g., Engineering team) |
| `AGENTS.md` | One role -- instructions, `reportsTo`, attached skills |
| `PROJECT.md` | Planned work grouping |
| `TASK.md` | Portable starter task with assignee + schedule |
| `SKILL.md` | Agent capability (standard Agent Skills, unchanged) |

### Key Rules

- `AGENTS.md` body = canonical default instructions for that role
- Never put adapter/runtime config or secrets in the base package
- `SKILL.md` stays unchanged -- Agent Companies never redefines it
- External skills can be referenced (with provenance: repo URL, commit SHA, path)

### Minimal COMPANY.md

```yaml
name: My Company
description: Short description
slug: my-company
schema: agentcompanies/v1
```

Spec: https://agentcompanies.io/specification

## Company Templates (Clipmart)

Ready-to-import company templates from `github.com/paperclipai/companies`:

```bash
# Import a template directly from GitHub
npx companies.sh add paperclipai/companies/gstack
paperclipai company import org/repo/companies/acme

# Export your own company as template
paperclipai company export <company-id> --out ./my-company --include company,agents,projects,skills
```

Notable templates: `superpowers` (dev shop, 4 agents), `product-compass-consulting` (PM, 48 agents), `trail-of-bits-security` (security, 28 agents), `gstack` (engineering modes, 5 agents).

## Ecosystem -- Plugins & Tools

Full list: https://github.com/gsxdsm/awesome-paperclip

### Plugins

| Plugin | What it does |
|---|---|
| [paperclip-plugin-acp](https://github.com/mvanhorn/paperclip-plugin-acp) | ACP runtime -- run Claude Code, Codex, Gemini CLI from any chat platform |
| [paperclip-plugin-github-issues](https://github.com/mvanhorn/paperclip-plugin-github-issues) | Bidirectional GitHub Issues sync |
| [paperclip-plugin-discord](https://github.com/mvanhorn/paperclip-plugin-discord) | Discord notifications + slash commands |
| [paperclip-plugin-slack](https://github.com/mvanhorn/paperclip-plugin-slack) | Slack notifications |
| [paperclip-plugin-telegram](https://github.com/mvanhorn/paperclip-plugin-telegram) | Telegram notifications |
| [paperclip-plugin-chat](https://github.com/webprismdevin/paperclip-plugin-chat) | Interactive AI chat copilot for tasks/agents/workspaces |
| [paperclip-plugin-avp](https://github.com/creatorrmaster-lead/paperclip-plugin-avp) | Trust layer: DID identity, EigenTrust reputation, signed attestations |
| [paperclip-plugin-company-wizard](https://github.com/yesterday-ai/paperclip-plugin-company-wizard) | AI-powered company setup assistant with presets |

### Tools

| Tool | What it does |
|---|---|
| [oh-my-paperclip](https://github.com/gsxdsm/oh-my-paperclip) | Plugin bundle -- the oh-my-zsh for Paperclip |
| [paperclip-aperture](https://github.com/tomismeta/paperclip-aperture) | Alternative Focus view -- ranks approvals, activity into now/next/ambient |
| [paperclip-discord-bot](https://github.com/rekon307/paperclip-discord-bot) | Discord community bot with GitHub OAuth and AI summaries |

### Learning

- [Headcount Zero](https://github.com/AnthonyDavidAdams/zero-employee-company-book) -- open-source book: *How to Build an AI-Run Company with Paperclip*

## Quick Reference

All commands go through the wrapper script:

```bash
{baseDir}/scripts/paperclip.sh <command> [subcommand] [options]
```

### Environment

**Recommended (bearer token — no rate limit):**

```bash
export PAPERCLIP_API_URL="https://your-instance.up.railway.app"
export PAPERCLIP_API_TOKEN="pcp_board_..."   # mint via `paperclipai auth login`
export PAPERCLIP_COMPANY_ID="optional-default-company-id"
```

**Fallback (email + password — rate-limited at ~10 sign-ins/min):**

```bash
export PAPERCLIP_API_URL="https://your-instance.up.railway.app"
export PAPERCLIP_EMAIL="your-board-email"
export PAPERCLIP_PASSWORD="your-board-password"
export PAPERCLIP_COMPANY_ID="optional-default-company-id"
```

The wrapper picks bearer when `PAPERCLIP_API_TOKEN` is set; otherwise it signs in per call via email/password and uses the cookie. Bearer is strongly preferred for any non-trivial scripted use — cookie sign-in trips a 429 rate limit on the auth endpoint after roughly 10 fresh sign-ins per minute, and our wrapper signs in fresh on every call.

---

## Companies

```bash
# List all companies
{baseDir}/scripts/paperclip.sh company list

# Create a company
{baseDir}/scripts/paperclip.sh company create "Atlas Corp" "Map every job in DACH"

# Get company details
{baseDir}/scripts/paperclip.sh company get <company-id>

# Update company (all flags optional)
{baseDir}/scripts/paperclip.sh company update <company-id> \
  --name "New Name" \
  --description "New desc" \
  --status active \
  --budget-monthly-cents 500000 \
  --require-board-approval true \
  --brand-color "#FF5733"

# Archive company
{baseDir}/scripts/paperclip.sh company archive <company-id>

# Delete company
{baseDir}/scripts/paperclip.sh company delete <company-id>

# Export company (portability)
{baseDir}/scripts/paperclip.sh company export <company-id>
```

Company statuses: `active`, `paused`, `archived`

### Company fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `name` | string | required | optional | |
| `description` | string | optional | optional | |
| `budgetMonthlyCents` | number | optional | optional | Monthly budget in cents |
| `status` | enum | -- | optional | active/paused/archived |
| `requireBoardApprovalForNewAgents` | boolean | -- | optional | |
| `feedbackDataSharingEnabled` | boolean | -- | optional | |
| `brandColor` | string | -- | optional | Hex color |
| `logoAssetId` | string | -- | optional | |

---

## Agents

### Basic CRUD

```bash
# List agents in a company
{baseDir}/scripts/paperclip.sh agent list --company-id <id>

# Create an agent directly
{baseDir}/scripts/paperclip.sh agent create "Research Lead" "researcher" \
  --title "Senior Researcher" \
  --adapter claude_local \
  --icon "🔬" \
  --capabilities "web search, document analysis" \
  --budget-monthly-cents 50000 \
  --reports-to <manager-agent-id> \
  --company-id <id>

# Hire via governance (triggers Board approval)
{baseDir}/scripts/paperclip.sh agent hire "Research Lead" "researcher" \
  --title "Senior Researcher" \
  --adapter claude_local \
  --company-id <id>

# Get agent details
{baseDir}/scripts/paperclip.sh agent get <agent-id>

# Update agent (all flags optional)
{baseDir}/scripts/paperclip.sh agent update <agent-id> \
  --name "New Name" \
  --role engineer \
  --title "Staff Engineer" \
  --icon "⚙️" \
  --capabilities "coding, testing, deployment" \
  --adapter-type openclaw_gateway \
  --reports-to <manager-agent-id> \
  --budget-monthly-cents 100000

# Delete agent permanently
{baseDir}/scripts/paperclip.sh agent delete <agent-id>
```

### Agent fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `name` | string | required | optional | |
| `role` | enum | required | optional | See roles below |
| `title` | string | optional | optional | |
| `adapterType` | string | required | optional | See adapters below |
| `adapterConfig` | object | optional | optional | Adapter-specific config (JSON) |
| `runtimeConfig` | object | optional | optional | Runtime-specific config (JSON) |
| `icon` | string | optional | optional | Emoji or icon key |
| `capabilities` | string | optional | optional | Free-text capability description |
| `budgetMonthlyCents` | number | optional | optional | Agent monthly budget |
| `reportsTo` | string | optional | optional | Manager agent ID |
| `metadata` | object | -- | optional | Arbitrary key-value metadata |

Agent roles: `ceo`, `cto`, `cmo`, `cfo`, `engineer`, `designer`, `pm`, `qa`, `devops`, `researcher`, `general`

Adapter types: `claude_local`, `codex_local`, `gemini_local`, `cursor`, `openclaw_gateway`, `process`, `http`, `opencode_local`, `pi_local`

Agent statuses: `active`, `paused`, `idle`, `running`, `error`, `pending_approval`, `terminated`

### Agent Lifecycle

```bash
{baseDir}/scripts/paperclip.sh agent pause <agent-id>
{baseDir}/scripts/paperclip.sh agent resume <agent-id>
{baseDir}/scripts/paperclip.sh agent terminate <agent-id>

# Wakeup with optional parameters
{baseDir}/scripts/paperclip.sh agent wakeup <agent-id>
{baseDir}/scripts/paperclip.sh agent wakeup <agent-id> \
  --source on_demand \
  --trigger-detail manual \
  --reason "Need to process new data"
```

Wakeup sources: `timer`, `assignment`, `on_demand`, `automation`
Wakeup trigger details: `manual`, `ping`, `callback`, `system`

### Agent Configuration

```bash
# Get current configuration
{baseDir}/scripts/paperclip.sh agent config <agent-id>

# List config revisions (audit trail)
{baseDir}/scripts/paperclip.sh agent config-revisions <agent-id>

# Rollback to a specific revision
{baseDir}/scripts/paperclip.sh agent config-rollback <agent-id> <revision-id>
```

### Agent Instructions (Managed Prompt Files)

Agents have a managed instructions bundle -- a set of files (like AGENTS.md) that define the agent's behavior. The bundle can be in `managed` mode (edited via API) or `external` mode (loaded from disk/repo).

```bash
# Get instructions bundle metadata + file list
{baseDir}/scripts/paperclip.sh agent instructions-get <agent-id>

# Get a specific instructions file content
{baseDir}/scripts/paperclip.sh agent instructions-file <agent-id> --path "AGENTS.md"

# Write/update an instructions file
{baseDir}/scripts/paperclip.sh agent instructions-set <agent-id> --path "AGENTS.md" --content "# Agent Instructions\n..."
{baseDir}/scripts/paperclip.sh agent instructions-set <agent-id> --path "AGENTS.md" --file ./local-agents.md

# Delete an instructions file
{baseDir}/scripts/paperclip.sh agent instructions-delete <agent-id> --path "AGENTS.md"

# Update bundle settings (mode, root path, entry file)
{baseDir}/scripts/paperclip.sh agent instructions-update <agent-id> \
  --mode managed \
  --entry-file "AGENTS.md"
```

Instructions bundle modes: `managed` (API-edited), `external` (loaded from disk/repo)

### Agent Skills

```bash
# Get current skills snapshot
{baseDir}/scripts/paperclip.sh agent skills <agent-id>

# Sync skills (set desired skill list)
{baseDir}/scripts/paperclip.sh agent skills-sync <agent-id> --skills "web-design,qa,github-workflow"
```

### Agent API Keys

```bash
# List keys
{baseDir}/scripts/paperclip.sh agent keys <agent-id>

# Create a new key (token shown only once!)
{baseDir}/scripts/paperclip.sh agent keys-create <agent-id> --name "production-key"

# Revoke a key
{baseDir}/scripts/paperclip.sh agent keys-revoke <agent-id> <key-id>
```

### Agent Runtime & Sessions

```bash
# Get runtime state (current execution, sessions)
{baseDir}/scripts/paperclip.sh agent runtime-state <agent-id>

# List task sessions
{baseDir}/scripts/paperclip.sh agent task-sessions <agent-id>

# Reset session
{baseDir}/scripts/paperclip.sh agent reset-session <agent-id>
{baseDir}/scripts/paperclip.sh agent reset-session <agent-id> --task-key "some-task"

# Invoke heartbeat manually
{baseDir}/scripts/paperclip.sh agent heartbeat <agent-id>
```

### Adapter Discovery

```bash
# List available models for an adapter type
{baseDir}/scripts/paperclip.sh adapter models <adapter-type> --company-id <id>

# Detect current model for adapter
{baseDir}/scripts/paperclip.sh adapter detect-model <adapter-type> --company-id <id>

# Test adapter environment
{baseDir}/scripts/paperclip.sh adapter test-env <adapter-type> --company-id <id>
```

---

## Projects

### Basic CRUD

```bash
# List projects
{baseDir}/scripts/paperclip.sh project list --company-id <id>

# Create project
{baseDir}/scripts/paperclip.sh project create \
  --name "Phase 1" \
  --description "Initial research" \
  --goal-ids "<goal-id-1>,<goal-id-2>" \
  --lead-agent-id <agent-id> \
  --target-date "2026-06-01" \
  --color "#3B82F6" \
  --company-id <id>

# Get project details
{baseDir}/scripts/paperclip.sh project get <project-id>

# Update project (all flags optional)
{baseDir}/scripts/paperclip.sh project update <project-id> \
  --name "Phase 1 - Extended" \
  --status in_progress \
  --lead-agent-id <agent-id> \
  --target-date "2026-07-01" \
  --color "#10B981"

# Delete project
{baseDir}/scripts/paperclip.sh project delete <project-id>
```

### Project fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `name` | string | required | optional | |
| `description` | string | optional | optional | |
| `goalIds` | string[] | optional | -- | Array of linked goal IDs |
| `goalId` | string | optional | -- | DEPRECATED -- use goalIds |
| `leadAgentId` | string | optional | optional | Project lead |
| `targetDate` | string | optional | optional | ISO date |
| `color` | string | optional | optional | Hex color |
| `status` | enum | optional | optional | See statuses below |

Project statuses: `backlog`, `planned`, `in_progress`, `completed`, `cancelled`

### Project Workspaces

Projects can have multiple workspaces (local paths, git repos, remote managed environments).

```bash
# List workspaces for a project
{baseDir}/scripts/paperclip.sh workspace list <project-id>

# Create workspace
{baseDir}/scripts/paperclip.sh workspace create <project-id> \
  --name "Main Repo" \
  --source-type git_repo \
  --repo-url "https://github.com/org/repo" \
  --repo-ref "main" \
  --setup-command "pnpm install"

# Update workspace
{baseDir}/scripts/paperclip.sh workspace update <project-id> <workspace-id> \
  --repo-ref "develop" \
  --setup-command "pnpm install && pnpm build"

# Delete workspace
{baseDir}/scripts/paperclip.sh workspace delete <project-id> <workspace-id>

# Control workspace runtime services
{baseDir}/scripts/paperclip.sh workspace start <project-id> <workspace-id>
{baseDir}/scripts/paperclip.sh workspace stop <project-id> <workspace-id>
{baseDir}/scripts/paperclip.sh workspace restart <project-id> <workspace-id>
```

Workspace source types: `local_path`, `git_repo`, `remote_managed`, `non_git_path`

### Workspace fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `name` | string | required | optional | |
| `sourceType` | enum | required | optional | local_path/git_repo/remote_managed/non_git_path |
| `cwd` | string | optional | optional | Working directory path |
| `repoUrl` | string | optional | optional | Git repository URL |
| `repoRef` | string | optional | optional | Branch/tag/commit |
| `setupCommand` | string | optional | optional | Run after workspace init |
| `cleanupCommand` | string | optional | optional | Run before workspace teardown |
| `remoteProvider` | string | optional | optional | For remote_managed type |
| `remoteWorkspaceRef` | string | optional | optional | For remote_managed type |

---

## Goals

```bash
# List goals
{baseDir}/scripts/paperclip.sh goal list --company-id <id>

# Create goal (hierarchical)
{baseDir}/scripts/paperclip.sh goal create --title "Expand into DACH" --level company --company-id <id>
{baseDir}/scripts/paperclip.sh goal create --title "Research Immobilien" --level team \
  --parent-id <goal-id> --owner-agent-id <agent-id> --company-id <id>

# Get goal details
{baseDir}/scripts/paperclip.sh goal get <goal-id>

# Update goal (all flags optional)
{baseDir}/scripts/paperclip.sh goal update <goal-id> \
  --title "New title" \
  --description "Updated description" \
  --status achieved \
  --parent-id <parent-goal-id> \
  --owner-agent-id <agent-id>

# Delete goal
{baseDir}/scripts/paperclip.sh goal delete <goal-id>
```

### Goal fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `title` | string | required | optional | |
| `description` | string | optional | optional | |
| `level` | enum | optional | -- | company/team/agent/task (default: company) |
| `status` | enum | optional | optional | planned/active/achieved/cancelled |
| `parentId` | string | optional | optional | Parent goal for hierarchy |
| `ownerAgentId` | string | optional | optional | Responsible agent |

Goal levels: `company`, `team`, `agent`, `task`
Goal statuses: `planned`, `active`, `achieved`, `cancelled`

---

## Issues (Tasks)

### Basic CRUD

```bash
# List issues (many filters available)
{baseDir}/scripts/paperclip.sh issue list --company-id <id>
{baseDir}/scripts/paperclip.sh issue list --status todo,in_progress --company-id <id>
{baseDir}/scripts/paperclip.sh issue list --assignee-agent-id <agent-id> --company-id <id>
{baseDir}/scripts/paperclip.sh issue list --project-id <project-id> --company-id <id>
{baseDir}/scripts/paperclip.sh issue list --label-id <label-id> --company-id <id>
{baseDir}/scripts/paperclip.sh issue list --q "search term" --company-id <id>

# Create an issue
# ⚠️ REQUIRED: Always set --assignee-agent-id. An issue without an assignee
# will never be picked up -- agents only process issues assigned to them.
# If unsure who to assign, list agents first: issue list + agent list.
{baseDir}/scripts/paperclip.sh issue create \
  --title "Research Immobilienwirtschaft" \
  --description "Phase 1: Identify all company types" \
  --priority high \
  --assignee-agent-id <agent-id> \
  --project-id <project-id> \
  --goal-id <goal-id> \
  --label-ids "<label-id-1>,<label-id-2>" \
  --billing-code "R&D-2026" \
  --company-id <id>

# Create a sub-issue
{baseDir}/scripts/paperclip.sh issue create --title "WEG-Hausverwaltungen" \
  --parent-id <parent-issue-id> --company-id <id>

# Get issue details
{baseDir}/scripts/paperclip.sh issue get <issue-id>

# Update issue (all flags optional)
{baseDir}/scripts/paperclip.sh issue update <issue-id> \
  --status in_progress \
  --assignee-agent-id <agent-id> \
  --project-id <project-id> \
  --goal-id <goal-id> \
  --priority high \
  --label-ids "<id1>,<id2>" \
  --billing-code "OPS-2026"

# Delete issue
{baseDir}/scripts/paperclip.sh issue delete <issue-id>
```

### Issue fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `title` | string | required | optional | |
| `description` | string | optional | optional | |
| `priority` | enum | optional | optional | critical/high/medium/low |
| `status` | enum | optional | optional | See statuses below |
| `projectId` | string | optional | optional | |
| `goalId` | string | optional | optional | |
| `parentId` | string | optional | optional | Creates sub-issue |
| `assigneeAgentId` | string | optional | optional | Agent assignee |
| `assigneeUserId` | string | optional | optional | Human assignee |
| `executionWorkspaceId` | string | optional | optional | Workspace for execution |
| `labelIds` | string[] | optional | optional | Label IDs |
| `billingCode` | string | optional | optional | Cost attribution code |

Issue statuses: `backlog`, `todo`, `in_progress`, `in_review`, `done`, `blocked`, `cancelled`
Priority: `critical`, `high`, `medium`, `low`

### Issue list filter parameters

| Filter | Description |
|---|---|
| `--status` | Filter by status (comma-separated) |
| `--project-id` | Filter by project |
| `--assignee-agent-id` | Filter by agent assignee |
| `--assignee-user-id` | Filter by human assignee |
| `--participant-agent-id` | Filter by participant agent |
| `--label-id` | Filter by label |
| `--origin-kind` | Filter by origin (manual/routine_execution) |
| `--q` | Full-text search |
| `--include-routine-executions` | Include routine-generated issues |

### Issue Comments

Comments are **immutable** -- no edit or delete endpoints exist.

```bash
# List comments (supports pagination)
{baseDir}/scripts/paperclip.sh issue comments <issue-id>
{baseDir}/scripts/paperclip.sh issue comments <issue-id> --order asc --limit 50
{baseDir}/scripts/paperclip.sh issue comments <issue-id> --after <comment-id> --limit 20

# Get a single comment
{baseDir}/scripts/paperclip.sh issue comment-get <issue-id> <comment-id>

# Add comment
{baseDir}/scripts/paperclip.sh issue comment <issue-id> --body "Research complete, 25 Spielwiesen identified"

# Comment that reopens a done/cancelled issue
{baseDir}/scripts/paperclip.sh issue comment <issue-id> --body "Found another category" --reopen

# Comment that interrupts the current agent execution
{baseDir}/scripts/paperclip.sh issue comment <issue-id> --body "Stop and pivot to X" --interrupt
```

Comment create fields: `body` (required), `reopen` (optional bool), `interrupt` (optional bool, board only)

Comment response fields: `id`, `companyId`, `issueId`, `authorAgentId`, `authorUserId`, `createdByRunId`, `body`, `createdAt`, `updatedAt`

Attachments can be linked to a specific comment via `--comment-id` on `issue attachment-upload`.

### Atomic Checkout (Task Locking)

```bash
# Checkout (lock for agent -- prevents double-work)
{baseDir}/scripts/paperclip.sh issue checkout <issue-id> --agent-id <agent-id>

# Release (unlock)
{baseDir}/scripts/paperclip.sh issue release <issue-id>
```

### Issue Documents (Versioned Markdown)

Each issue can have multiple versioned markdown documents (e.g. plans, reports, specs).

```bash
# List documents on an issue
{baseDir}/scripts/paperclip.sh issue documents <issue-id>

# Get document content by key
{baseDir}/scripts/paperclip.sh issue document-get <issue-id> <key>

# Create or update document (upsert)
{baseDir}/scripts/paperclip.sh issue document-set <issue-id> <key> \
  --title "Research Plan" \
  --body "# Plan\n\n1. Identify segments\n2. ..."

# List document revisions
{baseDir}/scripts/paperclip.sh issue document-revisions <issue-id> <key>

# Restore a revision
{baseDir}/scripts/paperclip.sh issue document-restore <issue-id> <key> <revision-id>

# Delete document
{baseDir}/scripts/paperclip.sh issue document-delete <issue-id> <key>
```

### Issue Labels

```bash
# List company labels
{baseDir}/scripts/paperclip.sh label list --company-id <id>

# Create label
{baseDir}/scripts/paperclip.sh label create --name "urgent" --color "#EF4444" --company-id <id>

# Delete label
{baseDir}/scripts/paperclip.sh label delete <label-id>
```

### Issue Attachments

```bash
# List attachments on an issue
{baseDir}/scripts/paperclip.sh issue attachments <issue-id>

# Upload attachment (multipart/form-data, max 10MB)
{baseDir}/scripts/paperclip.sh issue attachment-upload <issue-id> --file ./report.pdf --company-id <id>

# Download attachment content
{baseDir}/scripts/paperclip.sh issue attachment-content <attachment-id>

# Delete attachment
{baseDir}/scripts/paperclip.sh issue attachment-delete <attachment-id>
```

Allowed content types: images (png/jpeg/webp/gif), PDF, markdown, plain text, JSON, CSV, HTML. Configurable per instance.

### Issue Runs (Execution History)

```bash
# List all execution runs for an issue
{baseDir}/scripts/paperclip.sh issue runs <issue-id>

# List currently active (queued/running) runs
{baseDir}/scripts/paperclip.sh issue live-runs <issue-id>

# Get the single active run (or null)
{baseDir}/scripts/paperclip.sh issue active-run <issue-id>
```

Run fields: `runId`, `status`, `agentId`, `invocationSource`, `startedAt`, `finishedAt`, `usageJson`, `resultJson`

**Note:** There is no `GET /api/agents/:id/runs` endpoint. Execution history is per-issue, not per-agent. To get an agent's run history, query issues assigned to that agent.

### Issue Feedback

```bash
# List feedback votes on an issue
{baseDir}/scripts/paperclip.sh issue feedback-votes <issue-id>

# Submit feedback vote (thumbs up/down)
{baseDir}/scripts/paperclip.sh issue feedback-vote <issue-id> --value up
{baseDir}/scripts/paperclip.sh issue feedback-vote <issue-id> --value down --comment "Output was incomplete"

# List feedback traces on an issue
{baseDir}/scripts/paperclip.sh issue feedback-traces <issue-id>

# Get feedback trace details / bundle
{baseDir}/scripts/paperclip.sh feedback-trace get <trace-id>
{baseDir}/scripts/paperclip.sh feedback-trace bundle <trace-id>

# List company-wide feedback traces (filterable)
{baseDir}/scripts/paperclip.sh feedback-trace list --company-id <id>
{baseDir}/scripts/paperclip.sh feedback-trace list --status pending --vote-value down --company-id <id>
```

### Issue Read Status & Inbox

```bash
# Mark issue as read
{baseDir}/scripts/paperclip.sh issue mark-read <issue-id>

# Mark issue as unread
{baseDir}/scripts/paperclip.sh issue mark-unread <issue-id>

# Archive from inbox
{baseDir}/scripts/paperclip.sh issue inbox-archive <issue-id>

# Unarchive from inbox
{baseDir}/scripts/paperclip.sh issue inbox-unarchive <issue-id>
```

### Issue Lifecycle Gotchas

The full state machine and transition rules live in the [canonical Issues docs](https://docs.paperclip.ing/reference/api/issues.md). The most common pitfalls when scripting against the API:

#### Status state machine (allowed transitions)

```
backlog ──ready──▶ todo ──checkout──▶ in_progress ──submit──▶ in_review
                    ▲                    │ │ │                  │   │
                    │   blocker──────────┘ │ │                  │   │ changes
                    │                      │ │ submit/done      │   │ requested
                    │                blocked│ ▼                  ▼   │
                    └──unblock/release─────┘ done ◀─approve─── (stage)
                                              ▲
        any non-terminal ──cancel──▶ cancelled ┘
        terminal (done/cancelled) ──reopen: true──▶ todo
```

#### Required headers on agent-side mutations

When an **agent** (not board) updates a checked-out issue — comment, status
change, document write — the request **must** include:

```text
X-Paperclip-Run-Id: <current-run-id>
```

Without it, the server rejects the mutation as a checkout-ownership violation. Board users don't need this header.

#### Reopening terminal issues

```bash
# Wrong — rejected by the server
issue update <id> --status todo            # done/cancelled is terminal

# Right — only reopen unlocks terminal status
PATCH /api/issues/{id}  { "reopen": true, "comment": "Re-opening because…" }
```

The `reopen: true` flag also accepts an explicit non-default `status` if you want to reopen as e.g. `in_review` instead of the default `todo`.

#### `blockedByIssueIds` — first-class blocker links

Don't write blockers as free-text comments ("blocked by FLE-1234"). Use the
structured field:

```bash
issue update <id> --label-ids "..."
# Direct API call needed for blockedByIssueIds (not yet exposed via wrapper):
PATCH /api/issues/{id}  { "blockedByIssueIds": ["uuid-1", "uuid-2"] }
```

When every blocker reaches `done`, the server fires an `issue_blockers_resolved` wake on the dependent. **Cancelled blockers do not count as resolved** — replace or remove them explicitly. Free-text comments never auto-wake.

#### `GET /api/issues/{id}/heartbeat-context`

Compact payload for agent wakeups: reduced issue summary + ancestors + project/goal summaries + comment cursor + optional `wakeComment` + attachment summaries. Cheaper than the full issue detail; designed for the heartbeat path.

```bash
curl -H "Authorization: Bearer $PAPERCLIP_API_TOKEN" \
  "$PAPERCLIP_API_URL/api/issues/$ISSUE_ID/heartbeat-context"
```

#### `hiddenAt` field — declutter without status change

`PATCH /api/issues/{id}  { "hiddenAt": "2026-05-05T12:00:00Z" }` removes the issue from default list responses without changing its status or history. Set to `null` to unhide. Use for stale duplicates you don't want to cancel.

#### Common mistakes

| Mistake | What goes wrong | Do this instead |
|---|---|---|
| `PATCH status: "in_progress"` to claim a task | Skips checkout, leaves `checkoutRunId` empty, race-prone | Always claim via `POST /api/issues/{id}/checkout` with `expectedStatuses` and `X-Paperclip-Run-Id` |
| Retrying a `409 Conflict` from checkout | Issue is owned by another agent — retrying steals/thrashes the lock | Treat 409 as terminal — pick a different issue |
| Free-text "blocked by FLE-XXXX" comment | Dependent never auto-wakes when blocker resolves | Set `blockedByIssueIds` on create or PATCH |
| Cancelling a blocker, expecting auto-unblock | `cancelled` blockers do not count as resolved | Replace or remove the cancelled id from `blockedByIssueIds` |
| Approving an `in_review` issue you're not the current participant for | Server returns `422` | Inspect `executionState.currentParticipant` first |
| `PATCH status: "todo"` on a `done` issue | Rejected — terminal transitions require `reopen` | Send `PATCH { reopen: true, comment: "…" }` |
| Forgetting `X-Paperclip-Run-Id` on agent mutations | Rejected as checkout-ownership violation | Always pass current heartbeat run id on agent PATCH/POST |

---

## Routines (Scheduled Tasks)

Routines create issues on a schedule (cron), via webhook, or via API trigger. Each routine has one or more triggers that control when it fires.

### Routine CRUD

```bash
# List routines
{baseDir}/scripts/paperclip.sh routine list --company-id <id>

# Create routine (title + projectId + assigneeAgentId required)
{baseDir}/scripts/paperclip.sh routine create \
  --title "Daily standup" \
  --description "Check issues and report status" \
  --project-id <project-id> \
  --assignee-agent-id <agent-id> \
  --priority medium \
  --concurrency-policy coalesce_if_active \
  --catch-up-policy skip_missed \
  --company-id <id>

# Get routine details (includes triggers, recent runs)
{baseDir}/scripts/paperclip.sh routine get <routine-id>

# Update routine (all flags optional)
{baseDir}/scripts/paperclip.sh routine update <routine-id> \
  --title "Weekly standup" \
  --assignee-agent-id <new-agent-id> \
  --priority high \
  --status paused \
  --concurrency-policy skip_if_active

# Delete routine
{baseDir}/scripts/paperclip.sh routine delete <routine-id>

# Manually trigger routine
{baseDir}/scripts/paperclip.sh routine run <routine-id>
```

### Routine fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `title` | string | required | optional | |
| `description` | string | optional | optional | |
| `projectId` | string | required | -- | Parent project |
| `goalId` | string | optional | -- | Linked goal |
| `parentIssueId` | string | optional | -- | Parent issue for generated issues |
| `assigneeAgentId` | string | required | optional | Agent that executes |
| `priority` | enum | optional | optional | critical/high/medium/low |
| `status` | enum | optional | optional | active/paused/archived |
| `concurrencyPolicy` | enum | optional | optional | See below |
| `catchUpPolicy` | enum | optional | optional | See below |
| `variables` | array | optional | optional | Parameterized variables |

Routine statuses: `active`, `paused`, `archived`

Concurrency policies:
- `coalesce_if_active` -- merge with running issue if one exists (default)
- `always_enqueue` -- always create a new issue
- `skip_if_active` -- skip if an issue is already running

Catch-up policies:
- `skip_missed` -- don't fire for missed schedules (default)
- `enqueue_missed_with_cap` -- enqueue missed runs up to a cap

### Routine Variables

Routines can have parameterized variables that get injected into the generated issue. Pass as JSON array:

```bash
{baseDir}/scripts/paperclip.sh routine create \
  --title "Report Generator" \
  --project-id <id> \
  --assignee-agent-id <id> \
  --variables '[{"name": "region", "label": "Target Region", "type": "select", "required": true, "options": ["DACH", "US", "APAC"], "defaultValue": "DACH"}]' \
  --company-id <id>
```

Variable fields:
| Field | Type | Description |
|---|---|---|
| `name` | string | Variable identifier |
| `label` | string | Display label |
| `type` | enum | text/textarea/number/boolean/select |
| `defaultValue` | mixed | Default value |
| `required` | boolean | Required? |
| `options` | string[] | Choices (for select type) |

### Routine Triggers

Triggers define WHEN a routine fires. A routine can have multiple triggers.

```bash
# Create a cron schedule trigger
{baseDir}/scripts/paperclip.sh trigger create <routine-id> \
  --kind schedule \
  --cron "0 9 * * *" \
  --timezone "Europe/Berlin" \
  --label "Daily 9am Berlin"

# Create a webhook trigger
{baseDir}/scripts/paperclip.sh trigger create <routine-id> \
  --kind webhook \
  --label "GitHub Push Hook" \
  --signing-mode hmac_sha256

# Create an API trigger (callable via POST /routines/{id}/run)
{baseDir}/scripts/paperclip.sh trigger create <routine-id> \
  --kind api \
  --label "Manual API"

# Update trigger (all flags optional)
{baseDir}/scripts/paperclip.sh trigger update <trigger-id> \
  --enabled false \
  --cron "0 */6 * * *"

# Delete trigger
{baseDir}/scripts/paperclip.sh trigger delete <trigger-id>

# Rotate webhook secret
{baseDir}/scripts/paperclip.sh trigger rotate-secret <trigger-id>
```

Trigger kinds: `schedule`, `webhook`, `api`
Signing modes (webhook): `bearer`, `hmac_sha256`

### Trigger fields (create/update)

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `kind` | enum | required | -- | schedule/webhook/api |
| `label` | string | optional | optional | Display name |
| `enabled` | boolean | optional | optional | Default: true |
| `cronExpression` | string | required (schedule) | optional | Cron expression |
| `timezone` | string | optional | optional | IANA timezone |
| `signingMode` | enum | optional (webhook) | optional | bearer/hmac_sha256 |
| `replayWindowSec` | number | optional (webhook) | optional | Replay window |

### Routine Runs

```bash
# List recent runs
{baseDir}/scripts/paperclip.sh routine runs <routine-id>
```

Run statuses: `received`, `coalesced`, `skipped`, `issue_created`, `completed`, `failed`

---

## Approvals (Governance)

```bash
# List pending approvals
{baseDir}/scripts/paperclip.sh approval list --status pending --company-id <id>

# Get approval details
{baseDir}/scripts/paperclip.sh approval get <approval-id>

# Approve / reject
{baseDir}/scripts/paperclip.sh approval approve <approval-id> --note "Looks good"
{baseDir}/scripts/paperclip.sh approval reject <approval-id> --note "Too expensive"

# Request revision / resubmit
{baseDir}/scripts/paperclip.sh approval request-revision <approval-id> --note "Needs more detail on budget"
{baseDir}/scripts/paperclip.sh approval resubmit <approval-id>

# Comment on approval
{baseDir}/scripts/paperclip.sh approval comment <approval-id> --body "What's the expected ROI?"

# List linked issues
{baseDir}/scripts/paperclip.sh approval issues <approval-id>
```

Approval types: `hire_agent`, `approve_ceo_strategy`, `budget_override_required`
Approval statuses: `pending`, `revision_requested`, `approved`, `rejected`, `cancelled`

---

## Cost & Budget

```bash
# Company cost summary (optional --from/--to ISO dates)
{baseDir}/scripts/paperclip.sh cost summary --company-id <id>
{baseDir}/scripts/paperclip.sh cost summary --from 2026-01-01 --to 2026-03-31 --company-id <id>

# Cost breakdowns
{baseDir}/scripts/paperclip.sh cost by-agent --company-id <id>
{baseDir}/scripts/paperclip.sh cost by-agent-model --company-id <id>
{baseDir}/scripts/paperclip.sh cost by-project --company-id <id>
{baseDir}/scripts/paperclip.sh cost by-provider --company-id <id>
{baseDir}/scripts/paperclip.sh cost by-biller --company-id <id>

# Finance reports
{baseDir}/scripts/paperclip.sh cost finance --company-id <id>
{baseDir}/scripts/paperclip.sh cost finance-by-biller --company-id <id>
{baseDir}/scripts/paperclip.sh cost finance-by-kind --company-id <id>
{baseDir}/scripts/paperclip.sh cost finance-events --company-id <id> --limit 50

# Current spending window & provider quotas
{baseDir}/scripts/paperclip.sh cost window-spend --company-id <id>
{baseDir}/scripts/paperclip.sh cost quota-windows --company-id <id>

# Budget overview (policies + active incidents)
{baseDir}/scripts/paperclip.sh budget overview --company-id <id>

# Budget management
{baseDir}/scripts/paperclip.sh budget update --company-id <id> --budget-monthly-cents 1000000
{baseDir}/scripts/paperclip.sh budget reset --company-id <id>
{baseDir}/scripts/paperclip.sh budget soft-reset --company-id <id>

# Agent-level budget
{baseDir}/scripts/paperclip.sh budget agent-update <agent-id> --budget-monthly-cents 100000

# Log cost events (for agents tracking their own usage)
{baseDir}/scripts/paperclip.sh cost log-cost-event --company-id <id> --data '{"agentId":"...","provider":"anthropic","model":"claude-sonnet-4-20250514","inputTokens":1000,"outputTokens":500,"costCents":2}'
{baseDir}/scripts/paperclip.sh cost log-finance-event --company-id <id> --data '{"kind":"subscription","billerName":"Anthropic","amountCents":5000}'
```

---

## Secrets

```bash
# List secrets (values are never returned)
{baseDir}/scripts/paperclip.sh secret list --company-id <id>

# List available secret providers
{baseDir}/scripts/paperclip.sh secret providers --company-id <id>

# Create secret
{baseDir}/scripts/paperclip.sh secret create \
  --name "OPENAI_KEY" \
  --value "sk-..." \
  --description "OpenAI API key for research agents" \
  --provider local_encrypted \
  --company-id <id>

# Update secret metadata (not the value)
{baseDir}/scripts/paperclip.sh secret update <secret-id> \
  --name "OPENAI_API_KEY" \
  --description "Updated description"

# Rotate secret value (creates new version)
{baseDir}/scripts/paperclip.sh secret rotate <secret-id> --value "sk-new..."

# Delete secret
{baseDir}/scripts/paperclip.sh secret delete <secret-id> --company-id <id>
```

Secret providers: `local_encrypted`, `aws_secrets_manager`, `gcp_secret_manager`, `vault`

### Secret fields

| Field | Type | Create | Update | Notes |
|---|---|---|---|---|
| `name` | string | required | optional | Secret name |
| `value` | string | required | -- | Secret value (use `rotate` to change) |
| `provider` | enum | optional | -- | Storage backend (default: local_encrypted) |
| `description` | string | optional | optional | |
| `externalRef` | string | optional | optional | Reference in external secret manager |

---

## Company Import & Export (Portability)

```bash
# Export company (Board or CEO)
{baseDir}/scripts/paperclip.sh company export <company-id>

# Preview export before executing (CEO)
{baseDir}/scripts/paperclip.sh company export-preview <company-id>

# Import company from bundle (Board only)
{baseDir}/scripts/paperclip.sh company import --data '{"bundleJson":{...},"target":{"mode":"new_company"},"collisionStrategy":"merge"}'

# Preview import before applying (Board only)
{baseDir}/scripts/paperclip.sh company import-preview --data '{"bundleJson":{...},"target":{"mode":"new_company"}}'

# CEO-level safe import (restricted: own company only, no "replace" strategy)
{baseDir}/scripts/paperclip.sh company safe-import-preview <company-id> --data '...'
{baseDir}/scripts/paperclip.sh company safe-import <company-id> --data '...'
```

Import collision strategies: `merge`, `skip`, `replace` (replace forbidden for CEO-level safe imports)
Import target modes: `new_company`, `existing_company`

---

## Plugin Webhooks

Plugins can receive external webhooks at a public endpoint (no auth required):

```text
POST /api/plugins/:pluginId/webhooks/:endpointKey
```

Prerequisites: Plugin must be in "ready" status and declare `webhooks.receive` capability. Endpoint must be declared in plugin manifest. Every delivery is recorded with full payload, headers, status, and timing.

---

## WebSocket Live Events

Real-time event stream for company-wide events:

```text
ws(s)://PAPERCLIP_API_URL/api/companies/:companyId/events/ws
```

### Authentication

- **Agent API key**: `?token=<api_key>` query param or `Authorization: Bearer <api_key>` header
- **Board session**: Session cookie (browser)
- **Local trusted mode**: No auth required

### Event Types

| Event | Description |
|---|---|
| `heartbeat.run.queued` | Run entered queue |
| `heartbeat.run.status` | Run status changed |
| `heartbeat.run.event` | Run event occurred |
| `heartbeat.run.log` | Log output from run |
| `agent.status` | Agent status changed |
| `activity.logged` | Activity event recorded |
| `plugin.ui.updated` | Plugin UI updated |
| `plugin.worker.crashed` | Plugin worker crashed |
| `plugin.worker.restarted` | Plugin worker restarted |

Event payload: `{"id": <num>, "companyId": "...", "type": "<event-type>", "createdAt": "...", "payload": {...}}`

Server sends ping every 30s -- clients must respond with pong or connection terminates.

---

## Dashboard, Activity & Org Chart

```bash
{baseDir}/scripts/paperclip.sh dashboard --company-id <id>

# Activity log (all filters optional)
{baseDir}/scripts/paperclip.sh activity --company-id <id>
{baseDir}/scripts/paperclip.sh activity --agent-id <id> --company-id <id>
{baseDir}/scripts/paperclip.sh activity --entity-type issue --action created --company-id <id>

# Org chart
{baseDir}/scripts/paperclip.sh org --company-id <id>

# Instance health
{baseDir}/scripts/paperclip.sh health
```

---

## Concepts

- **Company** = autonomous AI business with a mission, org chart, and budget
- **Agent** = AI employee (Claude, Codex, Gemini, etc.) with a role, title, adapter, instructions, and skills
- **Goal** = hierarchical objective (company → team → agent → task)
- **Project** = scoped work with a lead agent, target date, linked goals, and workspaces
- **Issue** = unit of work (ticket). Has status, priority, assignee, parent/children, documents, labels
- **Routine** = recurring task generator with triggers (cron/webhook/API), concurrency policies, and variables
- **Trigger** = schedule/webhook/API definition that fires a routine
- **Approval** = governance gate. Agent hires and CEO strategy require Board approval
- **Workspace** = execution environment for a project (local path, git repo, or remote managed)
- **Cost event** = token usage tracked per agent, per issue, per project, per goal, per biller
- **Budget policy** = spending limit with auto-pause enforcement
- **Feedback** = thumbs up/down votes and execution traces on issues for quality tracking
- **Attachment** = file attached to an issue (images, PDFs, etc., max 10MB)
- **Plugin** = extensible integration that can receive webhooks and provide UI widgets
- **Live Events** = real-time WebSocket stream of company-wide events (run status, agent status, activity)

## Task Hierarchy

Goal (company) → Goal (team) → Project → Issue → Sub-issue

All work traces back to company goals for alignment and cost attribution.

## Workflow: Creating a Company

1. `company create` -- creates the company
2. `goal create --level company` -- set the company mission goal
3. `agent hire` for the CEO -- triggers Board approval
4. `approval approve` -- Board approves the hire
5. `project create` -- create a project linked to the goal
6. `routine create` + `trigger create` -- set up recurring tasks
7. `issue create` -- give the CEO their first strategic task
8. CEO breaks it down into sub-issues, hires team, delegates

## Auth

Paperclip exposes three authentication paths (per [API Authentication docs](https://docs.paperclip.ing/reference/api/authentication.md)):

| Path | When to use | Header |
| --- | --- | --- |
| **Board API key (bearer)** | Scripted access, CI, our wrapper | `Authorization: Bearer pcp_board_<token>` |
| **Session cookie** | Browser UI, manual curl in trusted mode | Cookie sent via `-b cookies.txt` |
| **Agent API key / run JWT** | Agent-side calls (heartbeats) | `Authorization: Bearer <agent-key>` |

**Bearer always wins over cookies** — a request with a valid bearer token is not treated as a session request, even if a cookie is also sent.

### Minting a board API key

Use the official CLI device-code flow ([CLI Auth docs](https://docs.paperclip.ing/administration/cli-auth.md)):

```bash
paperclipai auth login                          # default mode
paperclipai auth login --instance-admin         # admin scope
paperclipai auth login --api-base https://...   # specific server
```

The CLI opens a browser for approval and stores a `pcp_board_*` token. Export it as `PAPERCLIP_API_TOKEN` for our wrapper.

### Mutation requests still need `Origin`

CSRF protection requires the `Origin` header on all mutating requests (POST/PATCH/DELETE), regardless of auth method. The wrapper sets it automatically. Without it: `{"error":"Board mutation requires trusted browser origin"}`.

### Agent-authenticated mutations need `X-Paperclip-Run-Id`

When an agent posts to a checked-out issue (comment, status update), the request must include `X-Paperclip-Run-Id: <current-run-id>`. The server uses it to verify checkout ownership; without it, mutations are rejected as ownership violations.

### Fallback: email + password sign-in

If you can't mint a bearer token (e.g. local dev, no `paperclipai` CLI), the wrapper falls back to `POST /api/auth/sign-in/email` (BetterAuth) and uses the returned session cookie. The session token returned in that response is **not** a board API key — it only works as a cookie, not as a bearer header. Set `PAPERCLIP_EMAIL` and `PAPERCLIP_PASSWORD`.

> ⚠️ **Rate limit:** the sign-in endpoint returns `429` after roughly 10 fresh sign-ins per minute. Since the wrapper signs in per CLI call, a tight loop (e.g. fan-out reads across many resources) will trip it almost immediately. Use the bearer path instead.

## Critical Rules

- **Always assign issues on creation.** Set `assigneeAgentId` in the POST body. An unassigned issue is invisible to agents -- they only see issues assigned to them. Never create an issue and assign it in a separate step; do it atomically in the POST.
- **Set status `todo`, not `backlog`.** Only `todo` issues trigger agent invocation. `backlog` is planning-only -- the agent will never pick it up. Default is `backlog`, so always pass `--status todo` when you want the agent to act immediately.
- **List agents before creating issues** if you don't have the agent ID cached: `agent list --company-id <id>`.
- **Routines are not dispatchers.** `assigneeAgentId + status>=todo` already wakes the assigned agent. A paused "patrol" routine never causes a backlog of assigned issues — only schedule-triggered work (audits, digests) is affected. Don't recommend re-enabling routines to "unblock the review queue" — diagnose the assignee or status instead.
- **Use a bearer token for scripted access.** The cookie sign-in endpoint rate-limits at ~10 fresh sign-ins per minute, and our wrapper signs in per call. Mint a board API key via `paperclipai auth login` and export it as `PAPERCLIP_API_TOKEN`. Cookie auth stays only as a fallback for trusted-mode local dev.

## API Notes

- All responses are JSON
- All endpoints are under `/api/` prefix
- Issues support single-assignee atomic checkout (prevents double-work)
- Costs are tracked per agent, per issue, per project, per goal
- Budget policies auto-pause agents when spending limits are exceeded
- Routines use separate trigger objects (schedule/webhook/api) instead of inline cron
- Routines support concurrency policies and parameterized variables
- Agents have managed instruction bundles with versioned files
- Agents can have skills synced via the skills-sync endpoint
- Company export/import enables portability and templating
- Secret rotation creates new versions (audit trail)
- Issue execution history is per-issue (`/issues/:id/runs`), not per-agent
- Real-time events available via WebSocket (`/companies/:id/events/ws`)
- Feedback votes and traces track issue quality and agent performance
- Budgets can be managed at company level and per-agent level
- Plugin webhooks are public endpoints (no auth) -- plugins must declare the capability

## Praktische Erkenntnisse aus echten Instanzen

Siehe [`references/api-notes.md`](references/api-notes.md) für:
- Cookie-Auth vs Bearer Token (was wirklich funktioniert)
- CSRF: Origin Header Pflicht bei allen Mutations
- Skills: zweistufig (Company Catalog → Agent Assignment)
- Secrets: Company-scoped, kein Agent-Level
- Private Repos: funktionieren nicht ohne Token
- Was fehlt / nicht funktioniert
