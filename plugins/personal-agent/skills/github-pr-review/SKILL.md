---
name: github-pr-review
description: Qualified, critical code reviews using GitHub's pending review API. Inline comments, verification, and validation.
metadata:
  category: engineering
---

# GitHub PR Review Skill 🔍

> **Qualified, critical code reviews using GitHub's pending review API.**
>
> Use this skill when reviewing pull requests. Produces inline code comments,
> code suggestions, and a qualified verdict (APPROVE / REQUEST_CHANGES / COMMENT).
> Always validates that changes match the PR description before assessing quality.

## Philosophy

- **Be critical.** Actively look for problems -- don't rubber-stamp.
- **Validate claims.** Does the code actually do what the PR description claims?
- **Verify impact.** Are there side effects, missing edge cases, security issues?
- **Inline findings.** Every issue goes directly on the affected line, not just in a summary.
- **One review, one notification.** Always batch via pending reviews.

## Trigger Modes

This skill activates in one of these ways:

| Mode | How |
|------|-----|
| **Manual** | User says "review PR #42" or links a PR |
| **Scheduled** | Cron job polls for open PRs without a review yet |
| **@mention** | Agent is tagged in a PR comment or requested as reviewer |

```bash
# Example: find PRs awaiting review (for scheduled mode)
gh pr list --repo <owner>/<repo> --json number,title,reviewDecision \
  --jq '.[] | select(.reviewDecision == "" or .reviewDecision == "REVIEW_REQUIRED")'
```

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- Collaborator / write access on the target repo

## Configuration

Adjust review depth based on model capabilities and budget:

| Scenario | Recommended Model | Notes |
|----------|------------------|-------|
| Security / complex logic | Opus or Sonnet | Worth the tokens for critical paths |
| Standard feature PRs | Sonnet | Good balance of depth and cost |
| Style / docs / config | Haiku or Flash | Fast triage, low cost |
| Large diffs (>500 lines) | Split approach | Haiku for triage, Sonnet for flagged files |

## Review Workflow

### Step 1: Gather Context

```bash
REPO="owner/repo"
PR=42

# PR metadata
gh pr view $PR --repo $REPO --json title,body,state,baseRefName,headRefName,commits,files

# Full diff
gh pr diff $PR --repo $REPO

# Latest commit SHA (needed for review API)
COMMIT=$(gh pr view $PR --repo $REPO --json commits --jq '.commits[-1].oid')
```

### Step 2: PR Hygiene Check

Before reviewing code, validate the PR itself:

**Title & Description:**
- Does the title follow conventional commits? (`feat:` / `fix:` / `chore:` / `docs:`)
- Does the description explain **Why** (context), **What** (changes), and **Impact** (outcome)?
- Are there changes **NOT mentioned** in the description? (scope creep)
- Are there claims in the description **NOT reflected** in the code? (incomplete)

**Metadata:**
- Is someone assigned?
- Are appropriate labels set? (enhancement, bug, documentation, etc.)
- Is the base branch correct? (usually `main`)

**Scope:**
- Is this a single focused change, or does it mix unrelated things?
- Could this be split into smaller PRs?

If any of these are missing or wrong, flag it in the review. PR hygiene is not optional -- sloppy PRs lead to sloppy repos.

### Step 3: Analyze the Diff

Read every changed file. Prioritize checks by severity:

**🔴 Always check (blocking):**

| Check | What to Look For |
|-------|-----------------|
| **Correctness** | Logic errors, off-by-ones, wrong conditions |
| **Security** | Injection, secrets in code, unsafe deserialization, auth gaps |
| **Secrets in diffs** | High-entropy strings (>20 chars, Base62/Base64/hex) in code, docs, examples, configs, markdown. If it looks like a real token and isn't an obvious placeholder (`your-token-here`, `xxx`, `<token>`, `sk-...`), it's a **blocking finding** -- even in documentation |
| **Breaking changes** | API contract changes, removed fields, changed defaults |

**🟡 Check if relevant (important):**

| Check | What to Look For |
|-------|-----------------|
| **Error handling** | Missing try/catch, unchecked return values, silent failures |
| **Edge cases** | Null/undefined, empty arrays, boundary values |
| **Tests** | Missing test coverage for new/changed behavior |
| **Performance** | N+1 queries, unnecessary allocations, missing indexes |

**🟢 Nice to have (non-blocking):**

| Check | What to Look For |
|-------|-----------------|
| **Dead code** | Unused imports, unreachable branches, leftover debug code |
| **Naming & clarity** | Misleading names, magic numbers, missing comments on complex logic |

### Step 4: Create Pending Review with Inline Comments

**Always use the 2-step pending review pattern** -- even for a single comment.

```bash
# Create pending review with inline comments
gh api repos/$REPO/pulls/$PR/reviews \
  -X POST \
  -f commit_id="$COMMIT" \
  -f 'comments[][path]=src/auth.ts' \
  -F 'comments[][line]=25' \
  -f 'comments[][side]=RIGHT' \
  -f 'comments[][body]=Missing null check -- `user` can be undefined when token is expired.

```suggestion
if (!user) {
  throw new AuthError("Invalid or expired token");
}
```' \
  -f 'comments[][path]=src/auth.ts' \
  -F 'comments[][line]=40' \
  -f 'comments[][side]=RIGHT' \
  -f 'comments[][body]=This catches all errors silently. At minimum, log the error.' \
  --jq '{id, state}'

# Returns: {"id": 12345, "state": "PENDING"}
```

**Parameter reference:**

| Parameter | Flag | Notes |
|-----------|------|-------|
| `commit_id` | `-f` | Latest commit SHA from Step 1 |
| `comments[][path]` | `-f` | File path relative to repo root |
| `comments[][line]` | `-F` | Line number (end line for multi-line) -- **numeric, use `-F`** |
| `comments[][side]` | `-f` | `RIGHT` for added/modified lines, `LEFT` for deleted lines |
| `comments[][body]` | `-f` | Comment text, optionally with ` ```suggestion ` block |
| `comments[][start_line]` | `-F` | For multi-line suggestions (optional) |

**Syntax rules:**
- Always single-quote `'comments[][...]'` parameters
- `-f` for strings, `-F` for numbers
- Code suggestions replace the entire specified line range

### Step 5: Submit the Review

```bash
REVIEW_ID=12345  # from Step 3 response

gh api repos/$REPO/pulls/$PR/reviews/$REVIEW_ID/events \
  -X POST \
  -f event="REQUEST_CHANGES" \
  -f body="## Review Summary

Found 2 issues:
1. Missing null check in auth flow (blocking)
2. Silent error swallowing (blocking)

Please address before merge."
```

### Step 6: Post-Review Action

After submitting:

| Verdict | Action |
|---------|--------|
| **APPROVE** | Merge if auto-merge is enabled/permitted for the repo: `gh pr merge $PR --repo $REPO --squash --delete-branch`. Otherwise leave approval for a human to merge. |
| **REQUEST_CHANGES** | Done. Author fixes, then re-review. |
| **COMMENT** | Done. No blocking action needed. |

> ⚠️ **Auto-merge is opt-in per repo/team.** Don't auto-merge unless explicitly configured.
> Check your agent's operational rules (MEMORY.md / AGENTS.md) for repo-specific merge policies.

### Step 7: Handle Author Responses

After submitting a review, the PR author may reply to your comments. Follow up:

**If the author pushed fixes:**
- Re-review the new diff (`gh pr diff`) -- don't just trust "fixed"
- Reply to your original comments confirming the fix or flagging remaining issues
- Submit a new review with updated verdict

**If the author disputes a finding:**
- Read their argument carefully -- you might be wrong
- Reply directly on the comment thread (not in a new review)
- If they're right: acknowledge it and resolve
- If you still disagree: explain why with specific reasoning

**If the author asks a question:**
- Answer directly on the comment thread
- If it reveals you made a wrong assumption, update your review

```bash
# Reply to a review comment thread
gh api repos/$REPO/pulls/$PR/comments/<COMMENT_ID>/replies \
  -X POST -f body="Good point -- I missed that the null check happens upstream. Withdrawing this finding."
```

**After confirming a fix:** Resolve the conversation thread so the PR shows a clean state before merge.

```bash
# List open review threads to find IDs
gh api graphql -f query='
  query {
    repository(owner: "<owner>", name: "<repo>") {
      pullRequest(number: <PR>) {
        reviewThreads(first: 50) {
          nodes { id isResolved comments(first: 1) { nodes { body } } }
        }
      }
    }
  }
' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)'

# Resolve a confirmed thread
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "<THREAD_NODE_ID>"}) {
      thread { isResolved }
    }
  }
'
```

## Event Type Decision Guide

```
Is there a bug, security issue, or broken behavior?
  → YES → REQUEST_CHANGES

Is something missing (tests, error handling, docs)?
  → YES → REQUEST_CHANGES

Are there only style/naming/optional improvements?
  → YES → APPROVE (with suggestions as non-blocking comments)

Just questions or neutral observations?
  → COMMENT
```

## Review Body Structure

The overall review body (Step 5) should follow this template:

```markdown
## ✅ / ❌ / 💬 Code Review

**Verdict: APPROVE / REQUEST_CHANGES / COMMENT**

### Validation
- Does the code match the PR description?
- Are the changes correct and complete?
- Are there changes NOT mentioned in the PR description? (scope creep)
- Are there claims in the description NOT reflected in the code? (incomplete)

### Verification
- Side effects? Breaking changes? Missing tests?
- Security or performance concerns?

### Risk Assessment
- Low / Medium / High -- with reasoning
```

## Code Suggestions

Use GitHub's suggestion syntax for concrete fixes:

````markdown
This variable name is misleading -- it holds a list, not a single item.

```suggestion
const users = await fetchUsers();
```

Clear naming helps the next reader.
````

**Multi-line suggestions** use `start_line`:
```bash
-F 'comments[][start_line]=10' \
-F 'comments[][line]=15' \
```
This replaces lines 10–15 with the suggestion content.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Posting comments one-by-one (notification spam) | Always use pending review → submit |
| Approving without reading the diff | Read every changed line |
| Only reviewing the "interesting" files | Check configs, tests, manifests too |
| Vague comments ("this looks off") | Be specific: what's wrong, why, and how to fix |
| Approving with blocking issues as "suggestions" | If it must be fixed → REQUEST_CHANGES |
| Using inline `\n` in `gh pr create --body` | Use heredoc or temp file for multi-line bodies |
| Auto-merging on repos without permission | Check merge policy before merging |
| **"Docs-only = zero risk" bias** | Security checks apply to **every line in the diff**, including docs, examples, and markdown. A real token in a code example is just as leaked as one in source code |
| **Approving real secrets in examples** | Any high-entropy string in a diff that isn't an obvious placeholder (`your-token-here`, `<TOKEN>`, `xxx`) must be flagged as a potential leaked secret -- especially when the PR is about auth/token usage |

## Secret Detection in Diffs

Every diff line must be scanned for potential secrets -- **including docs, examples, and markdown**.

### Heuristics

A string is suspicious if:
1. **Length ≥ 20 characters** and **high entropy** (mixed case, digits, no dictionary words)
2. **Looks like a token format**: Base62, Base64, hex, `sk-...`, `tok-...`, `ghp_...`, `clw_...`
3. **Not an obvious placeholder**: `your-token-here`, `xxx`, `<TOKEN>`, `example-key`, `sk-...your-key...`
4. **Context is auth-related**: the PR touches auth docs, token handling, API key usage, or `.env` examples

### What to do

- If suspicious → **REQUEST_CHANGES** with: "This looks like a real secret. Please replace with a placeholder."
- If the author confirms it's a dummy → they can re-push with a comment explaining why
- **Never approve a PR with a suspicious high-entropy string without explicitly verifying it's not real**

### Elevated sensitivity triggers

When a PR is **about** auth, tokens, API keys, or secrets handling, assume every token-shaped string is real until proven otherwise. The subject matter itself is the red flag.

### Real-world example (incident)

A docs PR added a callout explaining correct `X-API-Key` usage. The example contained a **real agent token** (`hlFPU...32chars`). It was approved and merged because the reviewer classified it as "docs-only, zero risk." The token had to be rotated.

**Lesson:** "Docs-only" is never "zero risk" when the diff contains strings that look like secrets.

## Review Without Inline Comments

For clean PRs with no issues, skip the 2-step pattern:

```bash
gh api repos/$REPO/pulls/$PR/reviews \
  -X POST \
  -f commit_id="$COMMIT" \
  -f event="APPROVE" \
  -f body="## ✅ Code Review

**Verdict: APPROVE**

Reviewed all changed files. Clean removal of dead code, no side effects, no orphaned references.

**Risk: Zero.**"
```

---

*Part of the [agentic-foundation](https://github.com/Yesterday-AI/agentic-foundation) skill library.*
