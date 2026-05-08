---
name: pm-patrol-routine
description: >
  Project Manager patrol for GitHub repos. Triages new issues, reviews PRs
  for completeness (not code quality), verifies fixes match issue requirements,
  closes resolved issues, and coordinates between engineer and reviewer.
  Integrates with issue-patrol-routine (Scotty) and review-patrol-routine (Rémy).
metadata:
  author: ManniTheRaccoon
  version: "1.0"
  category: ops
compatibility: >
  Requires gh CLI authenticated with write access to target repos.
  Works alongside issue-patrol-routine (engineer) and review-patrol-routine (reviewer).
---

# PM Patrol -- Project Manager Routine 📋

> **The PM doesn't write code or review code quality. The PM ensures the right
> things get built, issues get closed, and nothing falls through the cracks.**

## Philosophy

- **Issues are the source of truth.** Every change traces back to an issue.
- **PRs must solve their issue.** Code quality is the reviewer's job. Completeness is the PM's job.
- **Close the loop.** An issue is only done when the fix is verified on `main`.
- **Unblock, don't bottleneck.** If something is stuck, figure out why and fix the process.
- **Consolidate, don't duplicate.** User feedback → clean issue. Multiple reports → one issue.

## Role Boundaries

| Responsibility | PM (Manni) | Engineer (Scotty) | Reviewer (Rémy) |
|---|---|---|---|
| Triage new issues | ✅ | ❌ | ❌ |
| Write issue descriptions | ✅ | ❌ | ❌ |
| Assign issues to engineer | ✅ | ❌ | ❌ |
| Maintain ROADMAP | ✅ | ❌ | ❌ |
| Plan sprints/phases | ✅ | ❌ | ❌ |
| Implement fixes | ❌ | ✅ | ❌ |
| Code quality review | ❌ | ❌ | ✅ |
| Acceptance testing | ✅ | ❌ | ❌ |
| Verify PR solves the issue | ✅ | ❌ | ❌ |
| Close issues after merge | ✅ | ❌ | ❌ |
| Consolidate user feedback | ✅ | ❌ | ❌ |
| Stakeholder communication | ✅ | ❌ | ❌ |
| Enforce project standards | ✅ | ❌ | ❌ |
| Monitor GitHub mentions | ✅ | ❌ | ❌ |

## The Patrol Cycle

```
PM Patrol (every 2-4 hours)
  │
  ├── 0. MENTIONS -- Check GitHub notifications for @mentions
  ├── 1. TRIAGE -- New issues without labels/assignee
  ├── 2. PR REVIEW -- Open PRs: does the fix match the issue?
  ├── 3. VERIFY & CLOSE -- Merged PRs: is the fix actually on main?
  ├── 4. STUCK CHECK -- Issues/PRs without progress >48h
  ├── 5. ENFORCE -- CI health, PR hygiene, repo settings, stale issues
  └── 6. LOG -- Update patrol state + daily notes
```

### Step 0: MENTIONS -- Check GitHub Notifications

Before anything else: check if someone mentioned you, requested your review, or assigned you something.

```bash
# All unread mentions
gh api notifications --jq '.[] | select(.reason == "mention") | "\(.subject.type): \(.subject.title) | \(.repository.full_name)"'

# Review requests
gh api notifications --jq '.[] | select(.reason == "review_requested") | "\(.subject.title) | \(.repository.full_name)"'

# Assignments
gh api notifications --jq '.[] | select(.reason == "assign") | "\(.subject.title) | \(.repository.full_name)"'

# Quick summary
gh api notifications --jq '
  group_by(.reason) | .[] |
  "\(.[0].reason): \(length) notification(s)"
'
```

**Actions per type:**

| Reason | Action |
|---|---|
| `mention` | Read the comment/issue, respond or act |
| `review_requested` | Review the PR (completeness check, not code quality) |
| `assign` | New issue/PR assigned to you -- triage or act |
| `ci_activity` | CI failed -- check if it needs an issue |
| `comment` | Someone replied to your issue/PR -- read and respond |

**After handling:** Mark notifications as read:
```bash
# Mark all as read
gh api notifications -X PUT -f read=true

# Or mark specific thread
gh api notifications/threads/<thread_id> -X PATCH
```

**Rule:** Mentions are highest priority. If someone @-mentioned you, they're waiting. Handle before triage.

### Step 1: TRIAGE -- New Issues

```bash
# Find untriaged issues (no labels, no assignee)
gh issue list --repo $REPO --state open --json number,title,labels,assignees \
  --jq '.[] | select(.labels | length == 0) | "#\(.number) \(.title)"'
```

For each new issue:
1. **Read the issue** -- understand what's being asked
2. **Label it** -- `bug`, `enhancement`, `documentation`, etc.
3. **Assign to engineer** -- `gh issue edit $N --add-assignee YyScotty`
4. **Improve description if needed** -- add context, acceptance criteria, reproduction steps
5. **Prioritize** -- is this blocking? urgent? can wait?

### Step 2: PR REVIEW -- Completeness Check

```bash
# Find open PRs
gh pr list --repo $REPO --state open --json number,title,body,author \
  --jq '.[] | "#\(.number) \(.title) by @\(.author.login)"'
```

For each open PR:
1. **Read the PR description** -- what issue does it claim to close?
2. **Read the linked issue** -- what was actually requested?
3. **Compare** -- does the PR address ALL points from the issue?
4. **Check edge cases** -- did the issue mention specific scenarios? Are they covered?
5. **Verdict:**
   - ✅ Complete → Comment "PM review: looks complete, solves #N as described"
   - ⚠️ Incomplete → Comment with what's missing, request changes
   - ❓ Unclear → Ask for clarification

**Important:** Do NOT review code quality (that's Rémy's job). Focus on:
- Does the PR solve the issue?
- Are all acceptance criteria met?
- Are there obvious gaps (mentioned in issue but not in PR)?

### Step 3: VERIFY & CLOSE -- Post-Merge Verification

```bash
# Find recently merged PRs that reference issues
gh pr list --repo $REPO --state merged --json number,title,body,mergedAt \
  --jq '.[] | select(.mergedAt > "'$(date -u -d '48 hours ago' +%Y-%m-%dT%H:%M:%SZ)'") | "#\(.number) \(.title)"'
```

For each recently merged PR:
1. **Extract the issue number** from `Closes #N` / `Fixes #N`
2. **Verify on main:**
   ```bash
   # Check the fix actually landed
   gh api repos/$REPO/contents/<changed_file> --jq '.content' | base64 -d | grep <expected_change>
   ```
3. **If verified** → Close the issue with a comment:
   ```bash
   gh issue close $N --repo $REPO --comment "Verified on main via PR #M. Fix confirmed."
   ```
4. **If NOT verified** (squash dropped commits, revert, etc.) → Reopen issue, document what happened

**⚠️ CRITICAL RULE:** Never claim "ist raus" without verifying on `main`. Branch ≠ main. PR merged ≠ fix landed.

### Step 4: STUCK CHECK

```bash
# Issues assigned but no PR after 48h
gh issue list --repo $REPO --state open --assignee YyScotty --json number,title,updatedAt \
  --jq '.[] | select(.updatedAt < "'$(date -u -d '48 hours ago' +%Y-%m-%dT%H:%M:%SZ)'") | "#\(.number) \(.title)"'

# PRs with REQUEST_CHANGES but no new commits after 24h
gh pr list --repo $REPO --state open --json number,title,updatedAt,reviewDecision \
  --jq '.[] | select(.reviewDecision == "CHANGES_REQUESTED") | "#\(.number) \(.title) (updated: \(.updatedAt))"'
```

For stuck items:
- **Issue stuck >48h** → Ping engineer, ask if blocked
- **PR stuck after review >24h** → Ping author, remind of review feedback
- **Issue blocked on external** → Document blocker, notify human

### Step 5: ENFORCE -- Project Policies & Hygiene

The PM is the "Kindergarten-Wächter" 🧹 -- if standards slip, nobody else will catch it.

#### CI Pipeline Health

```bash
# Check for repeatedly failing CI on open PRs
for PR in $(gh pr list --repo $REPO --state open --json number --jq '.[].number'); do
  STATUS=$(gh pr checks $PR --repo $REPO 2>/dev/null | grep -c "fail" || echo 0)
  if [ "$STATUS" -gt 0 ]; then
    echo "⚠️ PR #$PR has failing CI"
  fi
done

# Check last 5 runs on main -- is the default branch healthy?
gh run list --repo $REPO --branch main --limit 5 --json conclusion \
  --jq '[.[] | .conclusion] | if (map(select(. == "failure")) | length) > 2 then "🔴 main branch CI unstable!" else "✅ main CI healthy" end'
```

**Actions (do NOT ask -- just do it):**
- PR CI fails repeatedly (>2 runs) and author isn't fixing → Comment: "CI failing since X -- please fix or mark as draft"
- Main branch CI broken → **Immediately** create a `bug` issue, assign engineer. Don't ask the stakeholder for permission.
- CI flaky (passes/fails randomly) → Create issue to investigate, label `flaky-test`

**Rule:** The PM never asks "should I create an issue?" -- if something is broken, the issue gets created. That's your job. Act, don't ask.

#### PR Hygiene -- Calling Out Sloppy Work

Check every PR against project standards:

| Check | What to look for | Action if violated |
|---|---|---|
| **Labels** | PR has no labels | Comment: "Please add labels (bug/enhancement/docs)" |
| **Assignee** | PR has no assignee | Comment: "Please self-assign" |
| **Description** | PR body is empty or one-liner | Comment: "PR needs Context/Changes/Outcome sections" |
| **Issue link** | No `Closes #N` / `Fixes #N` | Comment: "Which issue does this solve? Link it." |
| **Branch name** | Not `feat/`, `fix/`, `docs/`, `chore/` | Comment: "Use conventional branch naming" |
| **Commit messages** | Non-conventional commits | Comment on PR, not blocking but noted |
| **Draft PRs >7d** | Draft sitting for over a week | Comment: "This draft is 7+ days old -- close or finish?" |

```bash
# Find PRs without labels
gh pr list --repo $REPO --state open --json number,labels \
  --jq '.[] | select(.labels | length == 0) | "#\(.number) has no labels"'

# Find PRs without assignees
gh pr list --repo $REPO --state open --json number,assignees \
  --jq '.[] | select(.assignees | length == 0) | "#\(.number) has no assignee"'

# Find PRs with empty body
gh pr list --repo $REPO --state open --json number,body \
  --jq '.[] | select(.body | length < 20) | "#\(.number) has no description"'
```

#### Repo Settings & Branch Protection

Periodically verify (weekly, not every cycle):

```bash
# Check branch protection on main
gh api repos/$REPO/branches/main/protection --jq '{
  enforce_admins: .enforce_admins.enabled,
  required_reviews: .required_pull_request_reviews.required_approving_review_count,
  status_checks: .required_status_checks.strict
}' 2>/dev/null || echo "⚠️ No branch protection on main!"
```

**Expected settings:**
- Branch protection on `main` enabled
- At least 1 required review
- Status checks required before merge
- No force-push to main

If misconfigured → Create an issue, label `security`, assign to human (not engineer -- this needs admin access).

#### Issue Hygiene

```bash
# Issues open >30 days without activity
gh issue list --repo $REPO --state open --json number,title,updatedAt \
  --jq '.[] | select(.updatedAt < "'$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ)'") | "#\(.number) \(.title) -- stale"'
```

**Actions:**
- Stale >30d → Comment "Still relevant? Closing in 7d if no response" + label `stale`
- Stale >37d with `stale` label → Close with "Closing due to inactivity. Reopen if needed."
- Duplicate issues → Close with "Duplicate of #N"

#### Feedback to Engineer

When the engineer repeatedly makes the same mistake:
1. **First time** → Fix silently (add label, improve description)
2. **Second time** → Comment on PR: "Reminder: PRs need labels + assignee"
3. **Third time** → Open a meta-issue: "Process: enforce PR standards" and discuss

Be constructive, not punitive. The goal is better habits, not blame.

### Step 6: LOG

Update `memory/pm-patrol-state.json`:
```json
{
  "lastPatrol": "2026-03-29T14:00:00Z",
  "cycleCount": 1,
  "repos": {
    "Yesterday-AI/clawrag": {
      "triaged": [53, 54],
      "reviewed": [49],
      "verified": [44, 46],
      "stuck": []
    }
  }
}
```

Append to daily notes `memory/YYYY-MM-DD.md`.

## ROADMAP & Planning

The PM owns the project roadmap. This means:

### Maintaining ROADMAP.md

Each managed repo should have a `ROADMAP.md`. The PM keeps it current:

```bash
# Check if ROADMAP exists
gh api repos/$REPO/contents/ROADMAP.md --jq '.name' 2>/dev/null || echo "⚠️ No ROADMAP.md!"
```

**ROADMAP responsibilities:**
- Mark items as done when PRs merge
- Reprioritize based on stakeholder feedback
- Add new items from user requests / bug reports
- Remove items that are no longer relevant
- Keep phases/milestones realistic

**When to update:** After every VERIFY & CLOSE step (issue closed → mark in ROADMAP).

### Planning Issues

When creating a batch of related issues (like #52 → #53-#65):
1. Create a **parent issue** with the full plan
2. Break into **independent child issues** that can be worked in parallel
3. Add a tracking checklist to the parent
4. Prioritize: what blocks what? What delivers most value first?
5. Assign phases if the work is sequential

### Stakeholder Communication

The PM is the **Sprachrohr** (voice) between the engineering team and the stakeholder (Alex).

**Proactive updates (don't wait to be asked):**
- After a significant milestone → short summary to stakeholder
- When something is blocked on a decision → ask stakeholder directly
- When the plan changes → inform stakeholder with reason

**Reactive updates (when asked):**
- Current status of all managed projects
- What's in progress, what's stuck, what's done
- Timeline estimates (be honest, not optimistic)

**Format:** Keep it short. Stakeholder doesn't need implementation details -- they need:
- What's done since last update?
- What's in progress?
- What's blocked / needs a decision?
- What's next?

## Acceptance Testing

The PM verifies that implementations actually work -- not just that the code compiles.

### What to Test

After a PR is merged and verified on `main`:

1. **Functional test** -- Does the feature work as described in the issue?
   ```bash
   # Example: testing a new API endpoint
   curl -sf "$API_URL/v1/new-endpoint" -H "X-API-Key: $KEY" | jq .
   ```

2. **Edge cases** -- Does it handle the scenarios mentioned in the issue?
   - Empty input?
   - Invalid auth?
   - Missing required fields?

3. **Regression** -- Did it break something that worked before?
   ```bash
   # Quick smoke test of existing endpoints
   curl -sf "$API_URL/health" | jq .status
   curl -sf "$API_URL/v1/sources" -H "X-API-Key: $KEY" | jq '.sources | length'
   ```

4. **User perspective** -- Would the stakeholder consider this "done"?

### When to Test

- **Every merged PR** gets a quick functional test
- **Feature PRs** get edge case + regression testing
- **Bug fix PRs** get reproduction verification (does the original bug still happen?)

### Test Failures

If testing reveals the fix is incomplete or broken:
1. **Reopen the issue** with a comment explaining what failed
2. Add reproduction steps for the failure
3. Reassign to engineer
4. Do NOT close-and-reopen -- just reopen the original

## Special Cases

### Bug Reports from Users

1. User reports bug in chat/Discord/Telegram
2. PM creates a GitHub issue with:
   - Clear title
   - Reproduction steps (from user report)
   - Expected vs actual behavior
   - Screenshots if provided
   - `bug` label
3. Assign to engineer
4. Inform user that issue is tracked

### Re-Reviews

When Rémy requests changes on a PR:
1. Engineer pushes fixes
2. Engineer requests re-review from Rémy
3. **PM does NOT need to re-review** unless the scope changed
4. If Rémy approves → PM does final completeness check → merge

### Scope Creep in PRs

If a PR solves the issue but ALSO adds unrelated changes:
1. Comment: "This PR adds changes beyond #N scope. Please split into separate PRs."
2. Don't block if the extra changes are harmless -- just note it

### Issue Consolidation

When multiple users report the same problem:
1. Find or create the canonical issue
2. Close duplicates with "Duplicate of #N"
3. Add context from duplicate reports to the canonical issue

### Reverting a Broken Fix

If a merged PR broke something:
1. Create a new `bug` issue referencing the broken PR
2. Label as `bug` + `regression`
3. Assign to engineer with high priority
4. Do NOT revert unless critical -- prefer forward-fix

## Integration with Scotty & Rémy

```
PM (Manni)                    Engineer (Scotty)              Reviewer (Rémy)
    │                              │                              │
    ├── Triage issue #N            │                              │
    ├── Assign to Scotty ─────────►│                              │
    │                              ├── Pick up issue              │
    │                              ├── Implement on branch        │
    │                              ├── Create PR ─────────────────►│
    │                              │                              ├── Code review
    │                              │◄──── REQUEST_CHANGES ────────┤
    │                              ├── Fix + push                 │
    │                              ├── Request re-review ─────────►│
    │                              │                              ├── APPROVE
    ├── PM completeness check ◄────┤◄─────────────────────────────┤
    ├── Verify on main             │                              │
    ├── Close issue #N             │                              │
    │                              │                              │
```

## State File

`memory/pm-patrol-state.json`:
```json
{
  "version": 1,
  "lastPatrol": "2026-03-29T14:00:00Z",
  "cycleCount": 0,
  "repos": {
    "Yesterday-AI/clawrag": {
      "lastCheck": "2026-03-29T14:00:00Z",
      "issues": {
        "52": {
          "status": "triaged",
          "assignee": "YyScotty",
          "linkedPRs": [53],
          "lastChecked": "2026-03-29T14:00:00Z"
        }
      }
    }
  }
}
```

## HEARTBEAT.md / Cron Integration

```markdown
## PM Patrol
# Every 2-4 hours

1. Run triage on configured repos
2. Check open PRs for completeness
3. Verify recently merged PRs on main
4. Check for stuck issues/PRs
5. Update pm-patrol-state.json
```

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Reviewing code quality | That's Rémy's job. Focus on completeness. |
| Implementing fixes yourself | That's Scotty's job. Create an issue. |
| Claiming "done" without verifying main | Always `gh api repos/.../contents/...` |
| Closing issues without verification | Verify the fix landed on main first. |
| Creating PRs as PM | Your artifact is the issue, not the PR. |
| Ignoring stuck items | Check every cycle. Stuck >48h = escalate. |
| Ignoring failing CI | Broken pipelines block everyone. Escalate immediately. |
| Tolerating sloppy PRs | No labels, no description, no issue link = not ready. Send back. |
| Letting stale issues pile up | Stale >30d = comment. Stale >37d = close. Keep the backlog clean. |
| Being the only one who cares about standards | Document standards, create meta-issues, build habits -- not just policing. |

---

*Part of the [agentic-foundation](https://github.com/Yesterday-AI/agentic-foundation) skill library.*
