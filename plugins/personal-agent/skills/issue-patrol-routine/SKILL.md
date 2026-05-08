---
name: issue-patrol-routine
description: >
  Periodic scan of GitHub repos for open issues. Classifies issues into
  actionable queues (new, needs-clarification, ready-to-implement, in-progress,
  blocked) and persists state across heartbeat cycles. Use when an engineering
  agent needs to autonomously discover and triage work.
metadata:
  author: YyScotty
  version: "1.0"
  category: engineering
compatibility: >
  Requires gh CLI authenticated with read access to target repos.
  Python 3.8+ for the patrol script.
---

# Issue Patrol System ⚙️

> **Autonomous issue discovery and triage for engineering agents.**
>
> Use this skill when you need to periodically scan repos for open issues,
> classify them into work queues, and maintain persistent state across sessions.

## Philosophy

- **Deterministic scanning.** The patrol script is pure logic -- no LLM calls.
- **Persistent state.** Every cycle updates a JSON state file so the next session knows what changed.
- **Append-only logging.** Every patrol cycle is logged for auditability.
- **Actionable queues.** Issues are classified so the agent can immediately decide what to do.

## Architecture

```
Heartbeat (~30 min)
  └→ New Session
      └→ Reads HEARTBEAT.md
          └→ Runs issue_patrol.py
              ├→ Scans repos via gh CLI
              ├→ Classifies issues into queues
              ├→ Updates memory/issue-patrol-state.json
              └→ Appends to memory/issue-patrol-log.jsonl
          └→ Agent processes queues (triage / implement / follow-up)
```

## Setup

### 1. Configure Target Repos

Define repos in your `HEARTBEAT.md`:

```markdown
## Issue Patrol
REPOS="Yesterday-AI/agentic-foundation Yesterday-AI/experts Yesterday-AI/clawrag Yesterday-AI/company-orga Yesterday-AI/blueprints"
```

### 2. Deploy the Patrol Script

Copy `scripts/issue_patrol.py` to your workspace `scripts/` directory:

```bash
cp skills/issue-patrol-routine/scripts/issue_patrol.py ~/scripts/
chmod +x ~/scripts/issue_patrol.py
```

### 3. Initialize State

First run creates the state file automatically. Or initialize manually:

```bash
python3 ~/scripts/issue_patrol.py \
  --repos "Yesterday-AI/agentic-foundation Yesterday-AI/clawrag" \
  --state ~/memory/issue-patrol-state.json \
  --log ~/memory/issue-patrol-log.jsonl
```

## Queue Classification

Every open issue is placed into exactly one queue:

| Queue | Meaning | Agent Action |
|-------|---------|--------------|
| `newQueue` | Never seen before | Triage: read, label, plan |
| `needsClarificationQueue` | Missing info, waiting on author | Monitor for updates |
| `readyToImplementQueue` | Clear requirements, no blocker | Pick up and build |
| `inProgressQueue` | Agent has an active branch/PR | Continue work |
| `blockedQueue` | Depends on external input or other work | Wait, document blocker |
| `assignedToOthersQueue` | Assigned to someone else | Skip unless asked |

### Classification Logic

```
Is the issue assigned to someone else (not me)?
  → YES → assignedToOthersQueue

Is there an active branch/PR linked to this issue?
  → YES → inProgressQueue

Does the issue have label "blocked" or "waiting-for-input"?
  → YES → blockedQueue

Does the issue have label "needs-clarification" or is the body empty/vague?
  → YES → needsClarificationQueue

Has the issue been seen in a previous cycle?
  → NO → newQueue

Is the issue labeled "bug", "feature", "enhancement", or assigned to me?
  → YES → readyToImplementQueue

Otherwise → newQueue (needs triage)
```

## State Model

See [references/STATE.md](references/STATE.md) for the full state schema.

Quick overview:

```json
{
  "version": 1,
  "lastPatrol": "2026-03-29T12:00:00Z",
  "cycleCount": 0,
  "agentUser": "YyScotty",
  "repos": {
    "Yesterday-AI/clawrag": {
      "lastCheck": "2026-03-29T12:00:00Z",
      "issues": {
        "42": {
          "title": "Add retry logic for API calls",
          "queue": "readyToImplementQueue",
          "labels": ["enhancement"],
          "assignee": "YyScotty",
          "firstSeenCycle": 5,
          "lastUpdatedAt": "2026-03-28T10:00:00Z",
          "linkedPR": null,
          "status": "ready",
          "reason": "Labeled enhancement, assigned to me, clear requirements"
        }
      }
    }
  }
}
```

## Cycle Log

Every patrol run appends one JSON line to `memory/issue-patrol-log.jsonl`:

```json
{
  "cycle": 15,
  "timestamp": "2026-03-29T12:00:00Z",
  "reposScanned": 5,
  "totalOpen": 23,
  "queues": {
    "newQueue": 2,
    "needsClarificationQueue": 1,
    "readyToImplementQueue": 5,
    "inProgressQueue": 3,
    "blockedQueue": 1,
    "assignedToOthersQueue": 11
  },
  "changes": [
    {"repo": "Yesterday-AI/clawrag", "issue": 42, "from": "newQueue", "to": "readyToImplementQueue"}
  ]
}
```

## Running the Patrol

```bash
python3 scripts/issue_patrol.py \
  --repos "Yesterday-AI/agentic-foundation Yesterday-AI/clawrag" \
  --state memory/issue-patrol-state.json \
  --log memory/issue-patrol-log.jsonl \
  --agent-user YyScotty
```

Output is a JSON summary printed to stdout for the agent session to consume.

## HEARTBEAT.md Integration

Add to your `HEARTBEAT.md`:

```markdown
## Issue Patrol
# Schedule: Every heartbeat

1. Run: `python3 scripts/issue_patrol.py --repos "$REPOS" --state memory/issue-patrol-state.json --log memory/issue-patrol-log.jsonl --agent-user YyScotty`
2. Read the JSON output
3. For `newQueue` issues: Read issue body, decide queue placement
4. For `readyToImplementQueue`: Pick highest priority, start implementation (see `issue-to-pr-workflow` skill)
5. For `inProgressQueue`: Check PR status, address review feedback if any
6. Update state file with any manual reclassifications
```

## GitHub Mentions Check

After running the patrol scan, check for `@mentions` of your GitHub user in issue/PR comments. This catches requests that don't show up as assigned issues.

```bash
# List unread mentions
gh api notifications --jq '.[] | select(.reason == "mention") | {subject: .subject.title, repo: .repository.full_name, url: .subject.url}'
```

For each mention:
1. Read the comment thread to understand what's being asked
2. Respond if actionable (comment on the issue/PR)
3. Mark the notification as read:
   ```bash
   gh api notifications/threads/{thread_id} -X PATCH
   ```

Add to your `HEARTBEAT.md`:

```markdown
## GitHub Mentions Check
# Schedule: Every heartbeat

1. Check for new @mentions:
   ```bash
   gh api notifications --jq '.[] | select(.reason == "mention") | {subject: .subject.title, repo: .repository.full_name, url: .subject.url}'
   ```
2. For each mention: read the comment thread, respond if actionable
3. Mark handled notifications as read
```

## PR Follow-ups

After scanning issues, check all open PRs you created for mergeability and review status:

```bash
for REPO in $REPOS; do
  gh pr list --repo $REPO --state open --author @me \
    --json number,title,reviewDecision,mergeable \
    --jq '.[] | "#\(.number) [\(.mergeable)] [\(.reviewDecision // \"PENDING\")] \(.title)"'
done
```

| Status | Action |
|--------|--------|
| `CONFLICTING` | Rebase branch onto main, force-push |
| `CHANGES_REQUESTED` | Read review comments, address feedback, push fixes, request re-review |
| `APPROVED` | No action needed -- PM merges |
| `PENDING` | No action needed -- wait for review |

**Why this matters:** PRs with merge conflicts block the review pipeline. Check every cycle.

## After the Patrol

Based on queue contents, the agent should:

| Queue | Action |
|-------|--------|
| `newQueue` (>0) | Read each issue, classify, update state |
| `readyToImplementQueue` (>0) | Pick one, start `issue-to-pr-workflow` |
| `inProgressQueue` (>0) | Check linked PR for review feedback |
| `needsClarificationQueue` | Comment asking for details (if not already done) |
| `blockedQueue` | Log blocker, notify team if stale >3 days |

## Rules 🛡️

### NO_SPAM
- Don't comment on every issue every cycle. Only comment when you have something new to say.
- Track `lastCommentedAt` in state to avoid duplicate comments.

### NO_OVERCOMMIT
- Work on ONE issue at a time (max). Finish or park before starting the next.
- `inProgressQueue` should rarely have more than 1 item.

### NO_SECRETS
- Never put tokens, keys, or credentials in state files, logs, or issue comments.

---

*Part of the [agentic-foundation](https://github.com/Yesterday-AI/agentic-foundation) skill library.*
