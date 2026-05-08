---
name: review-patrol-routine
description: >
  Deterministic, stateful PR review patrol for GitHub repos. Use when an agent
  must review pull requests periodically instead of opportunistically, keep
  persistent patrol state across resets, classify new-review vs re-review
  queues, and drive heartbeat-based review cycles with explicit repo scope.
metadata:
  author: Remy
  version: "1.1"
  category: engineering
compatibility: >
  Requires Python 3 and authenticated GitHub CLI (`gh`). Optional but strongly
  recommended: an external heartbeat/cron trigger so patrol runs periodically,
  not just on demand.
---

# Review Patrol System

> A review policy is not a system. This skill turns PR patrol into a system.

## Design Principle: Deterministic First, LLM Second

The patrol script (`review_patrol.py`) is **pure Python + `gh` CLI** -- no LLM tokens consumed. It runs deterministically: same input (GitHub API state) → same output (queue classification). This means:

- **Every 30-min heartbeat cycle costs ~0 tokens** for the scan itself
- The LLM is only needed **after** the scan, when there's actually something to review
- If the scan finds `new=0, reReview=0` → the heartbeat can return `HEARTBEAT_OK` without burning tokens on review work
- State persistence means no redundant re-discovery of already-reviewed PRs

**Rule:** Everything that can be deterministic (scan, classify, log) is deterministic. Only the actual review judgment requires LLM reasoning.

Use this skill when you need **periodic PR review patrol** with:
- explicit repo scope
- persistent queue state
- deterministic new-vs-rereview classification
- heartbeat-safe reporting
- direct integration with GitHub review workflows

## When to Use

Activate this skill when:
- a human asks for **regular PR patrol**
- an agent keeps forgetting to run review cycles consistently
- you need to survive resets/restarts without losing review state
- you want a lightweight ops layer **without** a full external service

Do **not** use this skill for one-off PR reviews. For single PR review execution,
use `github-pr-review`.

## What This Skill Provides

Three layers:

1. **Trigger layer** -- heartbeat, cron, or scheduler invokes the patrol regularly
2. **State layer** -- `memory/heartbeat-state.json` stores repo/PR review state
3. **Classification layer** -- patrol script classifies every open PR into a queue

## Files

```
skills/review-patrol-routine/
├── SKILL.md                          # This file
├── scripts/
│   └── review_patrol.py              # Deterministic scan + classify script
└── references/
    └── STATE.md                      # State schema documentation
```

## Queue Semantics

### `newReviewQueue`
- PR is open, not draft, not authored by the patrol agent
- No prior review recorded in patrol state

### `reReviewQueue`
- PR is open, not draft
- Last verdict was `REQUEST_CHANGES`
- Current `headSha` differs from `lastReviewedHeadSha` (new commits pushed)

### `readyToMerge`
- PR is open, not draft
- Last verdict was `APPROVE`
- Current `headSha` matches `lastReviewedHeadSha` (no new commits)
- GitHub `mergeStateStatus` is `CLEAN` or `HAS_HOOKS`

### `staleApproved`
- PR is open, not draft
- Last verdict was `APPROVE`
- Current `headSha` differs from `lastReviewedHeadSha` (branch moved since approval)

### `blockedByReview`
- PR is open, previously received `REQUEST_CHANGES`
- No new commit since the last review

### `blockedByMergeability`
- GitHub reports `mergeStateStatus` as `DIRTY`, `BLOCKED`, `UNKNOWN`, or `UNSTABLE`

A PR can be blocked by review, blocked by mergeability, both, or neither.

### `drafts`
Observe only. Do not review unless explicitly asked.

### Per-PR `status` + `reason`

Every tracked PR gets a `status` and `reason` field for transparency:

| Status | Reason examples |
|--------|----------------|
| `new` | `unreviewed` |
| `rereview` | `new_commits_after_requested_changes` |
| `ready` | `approved_on_current_head` |
| `stale` | `approval_stale_after_new_commits` |
| `blocked` | `waiting_for_author_changes`, `requested_changes_and_merge_conflicts`, `merge_conflicts`, `checks_unstable` |
| `draft` | `draft_pr` |
| `tracked` | `open_unclassified` |

## Patrol State Model

Canonical state file: `memory/heartbeat-state.json`

```json
{
  "version": 2,
  "lastPatrol": "2026-03-29T11:00:00Z",
  "cycleCount": 290,
  "repos": {
    "org/repo": {
      "lastCheck": "2026-03-29T11:00:00Z",
      "prs": {
        "42": {
          "title": "feat: something",
          "url": "https://github.com/org/repo/pull/42",
          "author": "someone",
          "headSha": "abc123",
          "lastReviewedAt": "2026-03-28T...",
          "lastReviewedHeadSha": "abc123",
          "lastVerdict": "APPROVE",
          "lastMergedAt": null,
          "open": true
        }
      }
    }
  },
  "lastSummary": { ... }
}
```

## Cycle Log

Every patrol run appends one JSON line to `memory/patrol-log.jsonl`:

```json
{"cycle":290,"at":"2026-03-29T11:00:00Z","scanned":19,"open":11,"new":2,"reReview":0,"readyToMerge":1,"staleApproved":0,"blockedByReview":5,"blockedByMergeability":3,"drafts":1,"errors":0,"items":[{"pr":"org/repo#42","status":"new","reason":"unreviewed"}]}
```

This log is append-only and never truncated. Use it for:
- Debugging why a PR was or wasn't reviewed
- Auditing patrol coverage over time
- Answering "when did the patrol last see PR #X?"

## Setup

### 1. Configure repos and identity

The script loads configuration in this precedence order:

**Option A: Environment variables** (recommended for CI/cron)
```bash
export PATROL_REPOS="org/repo-a,org/repo-b,org/repo-c"
export PATROL_SELF_LOGINS="YyMyAgent,myagent"
export PATROL_WORKSPACE="/path/to/agent/workspace"  # optional, defaults to cwd
```

**Option B: Config file** (recommended for agents)
Create `patrol-config.json` in your workspace root:
```json
{
  "repos": [
    "org/repo-a",
    "org/repo-b"
  ],
  "selfLogins": ["YyMyAgent", "myagent"]
}
```

**Option C: Inline edit** (last resort)
Edit `_FALLBACK_REPOS` and `_FALLBACK_SELF_LOGINS` directly in the script.

**Workspace resolution:** The script uses `PATROL_WORKSPACE` env var if set, otherwise `cwd`. State and log files are written relative to this workspace root. This means agents can use the script directly from `agentic-foundation` without copying -- just configure via env or config file and run from the workspace directory.

Only include repos the human explicitly approved. No scope drift.

### 2. Initialize state

```bash
mkdir -p memory
echo '{"version":2,"lastPatrol":null,"cycleCount":0,"repos":{},"lastSummary":null}' > memory/heartbeat-state.json
```

### 3. Add to HEARTBEAT.md

```markdown
## PR Review Patrol

```bash
python3 skills/review-patrol-routine/scripts/review_patrol.py markdown
```
```

### 4. Seed known review history

If the agent already reviewed active PRs before adopting this skill, write those
PRs into the state file so they don't appear as false-new.

## Operating Procedure

### Per heartbeat / cycle

1. Run patrol script
2. Check GitHub notifications for @mentions and review requests (see below)
3. Review every PR in `newReviewQueue`
4. Re-review every PR in `reReviewQueue`
5. **Do NOT merge** -- merging is the PM's responsibility. Leave `readyToMerge` items as-is and report them.
6. Skip drafts
7. After each review, update the matching PR entry in state:
   - `lastReviewedAt`, `lastReviewedHeadSha`, `lastVerdict`
8. Emit a compact cycle summary

> ⚠️ **Merge Policy:** The review agent approves, the PM (project manager) merges. Never auto-merge after approval unless explicitly configured for a specific repo by the repo owner. When in doubt: don't merge.

## GitHub Mentions & Review Requests Check

After the patrol scan, check for notifications that don't show up as open PRs in the patrol scope -- @mentions in comments, explicit review requests, etc.

### Notifications API (recommended -- catches everything)

```bash
gh api notifications --jq '.[] | select(.reason == "mention" or .reason == "review_requested") | {reason, repo: .repository.full_name, title: .subject.title, type: .subject.type, url: .subject.url}'
```

### Mentions via Search (alternative)

```bash
gh api "search/issues?q=mentions:YOUR_GITHUB_LOGIN+updated:>2026-03-30&sort=updated&per_page=10" --jq '.items[] | {title, number}'
```

### Review Requests (explicit reviewer assignment)

```bash
gh api "search/issues?q=review-requested:YOUR_GITHUB_LOGIN+is:open+is:pr&sort=updated&per_page=10" --jq '.items[] | {title, number, html_url}'
```

### Handling

For each notification:
1. Read the comment/thread to understand what's being asked
2. Respond if actionable (review the PR, answer the question, comment on the issue)
3. Mark the notification as read:
   ```bash
   gh api notifications/threads/{thread_id} -X PATCH
   ```

### Why this matters

The patrol script only sees **open PRs** in the configured repo scope. It misses:
- @mentions in issue comments or PR discussions
- Explicit review requests via GitHub's "Request review" button
- Mentions in repos outside the patrol scope
- Comments on already-reviewed/merged PRs asking for follow-up

The notifications check closes this gap.

### Required state write-back after review

```json
{
  "lastReviewedAt": "2026-03-29T...",
  "lastReviewedHeadSha": "abc123",
  "lastVerdict": "REQUEST_CHANGES"
}
```

If merged: add `"lastMergedAt": "...", "open": false`

## Triggering Strategy

This skill does **not** create time itself. You need an external trigger:
- OpenClaw heartbeat (recommended)
- OpenClaw cron
- Host-level crontab
- project-engine scheduled workflow

Recommended cadence: **every 30 min** for new + re-review patrol.

**Token budget:** The scan itself costs 0 LLM tokens. Only when `newReviewQueue` or `reReviewQueue` is non-empty does the agent need to invoke the LLM for actual review work. On quiet cycles (nothing new), the entire heartbeat completes without any LLM call.

## Gotchas

### Memory without trigger is fake periodicity
Files on disk but no scheduler → the system is persistent but **not periodic**.

### Trigger without state causes duplicate work
No `heartbeat-state.json` → every open PR looks new every time.

### Review submitted, state not updated
Queue stays wrong. The skill depends on explicit write-back.

### Bad repo scope pollutes the patrol
Remove dead/unresolvable repos quickly.

### "Docs-only = zero risk" bias
Security checks (especially secret detection) apply to **every line in the diff**,
including docs, examples, and markdown. See `github-pr-review` skill for details.

## Relationship to Other Skills

| Skill | Role |
|-------|------|
| `github-pr-review` | Execute the actual review (checklists, inline findings, verdicts) |
| `github-workflow` | Branch/PR creation conventions |
| `project-engine` | Scheduler-driven operation |
| `systemic-persistence` | Ensure the trigger survives restarts |

## Anti-Patterns

| Anti-Pattern | Description |
|-------------|-------------|
| `POLICY_WITHOUT_STATE` | "We review periodically" in prose, but no queue state file |
| `STATE_WITHOUT_TRIGGER` | Perfect JSON state, but no heartbeat/cron runs patrol |
| `FULL_RESCAN_WITHOUT_MEMORY` | Every cycle starts from zero, rediscovers same PRs |
| `BROAD_SCOPE_DRIFT` | Agent reviews repos nobody approved |

---

A patrol that depends on mood is not a patrol. It is luck.
