---
name: issue-to-pr-workflow
description: >
  End-to-end workflow for turning a GitHub issue into a merged PR. Covers issue
  analysis, branch creation, implementation, PR with reviewer assignment, and
  handling review feedback loops. Use when an engineering agent picks up an issue
  from a patrol queue and needs to implement it.
metadata:
  author: YyScotty
  version: "1.0"
  category: engineering
compatibility: >
  Requires gh CLI authenticated with write access to target repos.
  Depends on github-workflow skill for branch/PR conventions.
  Depends on github-pr-review skill for understanding the review process.
---

# Issue-to-PR Workflow ⚙️

> **From open issue to merged PR -- the engineering agent's implementation loop.**
>
> Use this skill when you've picked an issue from the patrol queue and need to
> turn it into working code with a reviewed PR.

## Philosophy

- **Understand before you build.** Read the issue, the codebase, the architecture -- then code.
- **Small increments.** One issue = one branch = one PR. No scope creep.
- **Tests are not optional.** New logic gets tests. Period.
- **Reviews are respected.** When the reviewer says REQUEST_CHANGES, fix it -- don't argue (much).
- **Ship results, not status updates.** Progress lives in Git, not in chat messages.

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)
- Write access to the target repo
- Familiarity with [github-workflow](../github-workflow/SKILL.md) skill (branch/PR conventions)
- Reviewer configured (default: `YyRemy` for Yesterday repos)

## The Workflow

### Phase 1: Understand the Issue

```bash
REPO="Yesterday-AI/clawrag"
ISSUE=42

# Read the full issue
gh issue view $ISSUE --repo $REPO --json title,body,labels,assignees,comments

# Check for linked PRs (avoid duplicate work)
gh pr list --repo $REPO --search "closes:#$ISSUE OR fixes:#$ISSUE"
```

**Before writing any code, answer these questions:**

1. **What exactly needs to change?** -- Can you describe the change in one sentence?
2. **Where in the codebase?** -- Which files/modules are affected?
3. **What are the edge cases?** -- Empty input? Auth failure? Race conditions?
4. **How will you test it?** -- Unit test? Integration test? Manual verification?
5. **Are there dependencies?** -- Does this need another PR to land first?

If you can't answer #1 or #2, the issue needs clarification -- don't start coding.

### Phase 2: Prepare the Branch

```bash
cd <repo-directory>
git checkout main && git pull --rebase origin main

# Branch naming: type/short-description
# Use the issue number for traceability
git checkout -b feat/issue-42-retry-logic
```

**Branch naming conventions:**
| Issue Type | Branch Prefix | Example |
|-----------|--------------|---------|
| Feature/Enhancement | `feat/` | `feat/issue-42-retry-logic` |
| Bug Fix | `fix/` | `fix/issue-13-null-pointer` |
| Documentation | `docs/` | `docs/issue-7-api-docs` |
| Maintenance | `chore/` | `chore/issue-20-update-deps` |

### Phase 3: Implement

**Work loop:**

1. **Explore** -- Read existing code around the change area
2. **Plan** -- Sketch the approach mentally (or in a comment if complex)
3. **Build** -- Write the code in small, focused commits
4. **Test** -- Run tests after each meaningful change
5. **Commit** -- Conventional Commits, reference the issue

```bash
# Good commit messages
git commit -m "feat: add exponential backoff to API client

Implements retry with exponential backoff for transient failures.
Max 3 retries, initial delay 1s, backoff factor 2.

Closes #42"
```

**Implementation rules:**

- **Follow existing patterns.** Match the repo's code style, not your preference.
- **No debug artifacts.** Remove `console.log`, `print()` debugging before commit.
- **No secrets.** Ever. Not even "as an example". Use placeholders like `your-token-here`.
- **Handle errors.** New code paths need error handling. Silent failures are bugs.
- **Update docs if needed.** Changed an API? Update the README.

### Phase 4: Create the PR

```bash
# Rebase before pushing
git pull --rebase origin main

# Push
git push origin feat/issue-42-retry-logic

# Create PR with structured body
gh pr create \
  --repo $REPO \
  --title "feat: add exponential backoff to API client" \
  --body "## Context (Why)
Transient API failures cause data loss. Issue #42 reports intermittent 503s
from the upstream service.

## Changes (What)
- Added \`RetryClient\` wrapper with exponential backoff
- Default: 3 retries, 1s initial delay, 2x backoff factor
- Configurable via environment variables

## Outcome (Impact)
API calls survive transient failures without manual intervention.
Error rate expected to drop significantly.

## Testing
- Unit tests for retry logic (happy path + max retries exceeded)
- Integration test with mock 503 responses
- Manual test against staging

Closes #42" \
  --reviewer YyRemy
```

**After creating the PR:**

```bash
PR_NUMBER=<returned PR number>

# Self-assign
gh api repos/$REPO/issues/$PR_NUMBER/assignees \
  -X POST -f 'assignees[]=YyScotty'

# Label based on type
gh api repos/$REPO/issues/$PR_NUMBER/labels \
  -X POST -f 'labels[]=enhancement'
```

### Phase 5: Notify the Reviewer

Don't rely solely on GitHub notifications. Ping the reviewer directly:

```
# Via agent messaging (if available)
"Hey Remy, PR #<N> auf <repo> ist ready for review. <one-line summary>"
```

### Phase 6: Handle Review Feedback

When the reviewer submits `REQUEST_CHANGES`:

```bash
# 1. Read the review
gh pr view $PR_NUMBER --repo $REPO --json reviews --jq '.reviews[-1]'

# 2. Read inline comments
gh api repos/$REPO/pulls/$PR_NUMBER/comments \
  --jq '.[] | {id, path, line: .original_line, body}'

# 3. Fix the issues
# ... make changes ...
git add -A && git commit -m "fix: address review feedback

- Added null check per reviewer suggestion
- Improved error message clarity"
git push origin feat/issue-42-retry-logic

# 4. Reply to each comment
gh api repos/$REPO/pulls/$PR_NUMBER/comments/<COMMENT_ID>/replies \
  -X POST -f body="Fixed -- added the null check as suggested."

# 5. Request re-review
gh api repos/$REPO/pulls/$PR_NUMBER/requested_reviewers \
  -X POST -f 'reviewers[]=YyRemy'
```

**Review feedback rules:**

- **Read every comment.** Don't skip any.
- **Fix blocking issues immediately.** No "I'll do it in a follow-up".
- **Disagree respectfully.** If you think the reviewer is wrong, explain why -- on the comment thread, not in a new commit message.
- **Don't force-push.** Regular push so the reviewer can see the incremental diff.
- **Ping after fixing.** Always request re-review after pushing fixes.

### Phase 7: Post-Merge

After the PR is approved and merged (by a human):

```bash
# Clean up local branch
git checkout main && git pull origin main
git branch -d feat/issue-42-retry-logic
```

**Update patrol state:**
- Set issue to closed in `issue-patrol-state.json`
- Remove from `inProgressQueue`

## Flowchart

```
Issue picked from readyToImplementQueue
  │
  ├─ Read issue → Can implement?
  │   ├─ NO → Comment for clarification → Move to needsClarificationQueue
  │   └─ YES ↓
  │
  ├─ Create branch (feat/fix/docs/chore)
  ├─ Implement (small commits, tests, no secrets)
  ├─ Create PR (structured body, reviewer assigned)
  ├─ Notify reviewer
  │
  ├─ Review result?
  │   ├─ APPROVE → Wait for human merge → Clean up
  │   ├─ REQUEST_CHANGES → Fix → Push → Re-request review → Loop
  │   └─ COMMENT → Address if needed → Continue
  │
  └─ Done ✅
```

## Quality Gates (Self-Check Before PR)

Run through this checklist before creating the PR:

- [ ] Code does what the issue asks for
- [ ] No secrets/credentials anywhere (code, comments, commit messages)
- [ ] Tests exist for new/changed logic
- [ ] No breaking changes without documentation
- [ ] PR description has Context/Changes/Outcome/Testing
- [ ] Conventional Commit messages
- [ ] No leftover debug code (`console.log`, `print`, `TODO: remove`)
- [ ] Rebased on latest `main`

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Starting to code without understanding the issue | Answer the 5 questions in Phase 1 first |
| Scope creep ("while I'm here...") | One issue, one PR. Create new issues for tangential work |
| Forgetting to rebase before PR | Always `git pull --rebase origin main` before push |
| Force-pushing after review | Regular push only -- reviewer needs to see incremental changes |
| Not notifying the reviewer | Always ping directly, don't rely on GitHub email |
| Huge PRs (>500 lines) | Split into smaller PRs if possible |
| "Fixed" without explanation | Reply to each review comment explaining what changed |

## Integration with Issue Patrol

This skill is the "action" companion to `issue-patrol-routine`:

1. Patrol classifies issues into queues
2. Agent picks from `readyToImplementQueue`
3. This workflow executes the implementation
4. Patrol tracks the issue as `inProgressQueue` via linked PR
5. After merge, patrol marks it closed

Update `issue-patrol-state.json` when:
- Starting work: set `linkedPR` + `linkedBranch`
- PR merged: issue will auto-close if `Closes #N` is in PR body

---

*Part of the [agentic-foundation](https://github.com/Yesterday-AI/agentic-foundation) skill library.*
