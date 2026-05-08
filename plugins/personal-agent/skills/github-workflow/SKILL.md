---
name: github-workflow
description: Standardized Git + GitHub workflows for AI agents. Branching, committing, PRs, reviews, CI checks.
metadata:
  category: engineering
---

# GitHub Workflow Skill 🐙

> **Standardized Git + GitHub workflows for AI agents.**
>
> Use this skill for all Git operations: branching, committing, PRs, reviews, CI checks.

## Branch Strategy

```
main              ← Protected. Never push directly (shared repos).
└── feat/<name>   ← Feature branches. One per task.
└── fix/<name>    ← Bug fixes.
└── chore/<name>  ← Maintenance, docs, config.
```

## The PR Workflow (Standard)

### 1. Create Feature Branch

> 💡 **Using OpenClaw + symlinked skills?** Work in the `-dev` worktree, not the stable copy.
> See `openclaw-skill-import` skill for details.

```bash
cd <repo>  # or <repo>-dev if using worktrees
git checkout main && git pull origin main
git checkout -b feat/<descriptive-name>
```

### 2. Work & Commit
```bash
# Conventional Commits (required)
git add -A
git commit -m "feat: add BLE client provider

- Global keepAlive provider for connection persistence
- Scan, connect, disconnect lifecycle"
```

**Commit message format:**
- `feat:` New feature
- `fix:` Bug fix
- `chore:` Maintenance
- `docs:` Documentation
- `refactor:` Code restructuring

### 3. Push & Create PR
```bash
git push origin feat/<name>

gh pr create \
  --title "feat: Add BLE client provider" \
  --body "## Summary
- What changed and why

## Testing
- How it was tested" \
  --base main
```

### 4. Self-Assign & Label

After creating a PR, always assign yourself and apply relevant labels:

```bash
# Self-assign
gh api repos/<owner>/<repo>/issues/<pr-number>/assignees \
  -X POST -f 'assignees[]=<your-github-username>'

# Check available labels
gh label list --repo <owner>/<repo>

# Apply matching labels (e.g. enhancement, bug, documentation)
gh api repos/<owner>/<repo>/issues/<pr-number>/labels \
  -X POST -f 'labels[]=enhancement'
```

**Label mapping:**
| PR Type | Label |
|---------|-------|
| `feat:` | `enhancement` |
| `fix:` | `bug` |
| `docs:` | `documentation` |
| `chore:` / `refactor:` | _(no default -- use best match if available)_ |

### 5. Monitor CI
```bash
# Check PR status
gh pr checks <pr-number> --repo <owner/repo>

# View failed logs
gh run view <run-id> --repo <owner/repo> --log-failed
```

### Fix a Wrong Commit on an Open PR

If a PR accidentally includes the wrong commits, **edit the branch -- don't close and recreate**:

```bash
# Remove the last N commits but keep changes staged
git reset --soft HEAD~N

# Or interactively pick which commits to keep
git rebase -i HEAD~N

# Force push the corrected branch -- ONLY if the branch is yours and no one else has pulled it
git push --force-with-lease origin <branch-name>
```

The PR stays open, history gets clean. Closing + recreating adds noise.

⚠️ **Force push is a last resort.** Only use it on your own feature branches, never on `main` or shared branches. Prefer `--force-with-lease` over `--force` (safer: fails if someone else pushed in the meantime). If you find yourself force pushing often, something is wrong upstream.

### 6. Address Review

```bash
# Push fixes to same branch
git add -A && git commit -m "fix: address review feedback"
git push origin feat/<name>
```

**After pushing fixes:**

1. **Reply to each review comment** -- explain what you changed, or ask a question if the finding is unclear:
   ```bash
   # Reply to a specific review comment
   gh api repos/<owner>/<repo>/pulls/<pr-number>/comments/<comment-id>/replies \
     -X POST -f body="Fixed -- added null check as suggested."
   ```

2. **Dispute findings when appropriate** -- if a reviewer's conclusion is wrong, reply with reasoning directly on their comment. Don't silently ignore it.

3. **Request re-review** -- always @mention the reviewer so they know fixes are ready:
   ```bash
   # Request re-review from the reviewer
   gh api repos/<owner>/<repo>/pulls/<pr-number>/requested_reviewers \
     -X POST -f 'reviewers[]=<reviewer-username>'

   # Or leave a comment @mentioning them
   gh pr comment <pr-number> --repo <owner>/<repo> \
     --body "@<reviewer-username> Review feedback addressed -- ready for re-review. See replies on your comments for details."
   ```

### 7. Merge (after approval)
```bash
gh pr merge <pr-number> --squash --delete-branch
```

## Quick Reference

| Task | Command |
|------|---------|
| List open PRs | `gh pr list --repo <owner/repo>` |
| View PR details | `gh pr view <number> --repo <owner/repo>` |
| List issues | `gh issue list --repo <owner/repo>` |
| Create issue | `gh issue create --title "..." --body "..."` |
| Check CI runs | `gh run list --repo <owner/repo> --limit 5` |
| View run logs | `gh run view <id> --log-failed` |
| Clone repo | `gh repo clone <owner/repo>` |
| Fork repo | `gh repo fork <owner/repo>` |
| Create repo | `gh repo create <name> --public --source=. --push` |
| API query | `gh api repos/<owner>/<repo>/pulls --jq '.[].title'` |

## Rules 🛡️

1. **NEVER push to `main`** on shared repos. Always PR. No exceptions -- not for docs, not for typos, not for "small" changes.
2. **Conventional Commits** -- no `"fixed stuff"` messages.
3. **Small PRs** -- one feature/fix per PR. Easier to review.
4. **Rebase before PR** -- `git pull --rebase origin main` to avoid merge commits.
5. **Direct commit OK** on solo repos (when explicitly approved by owner). A shared repo is NEVER a solo repo, even if you have push access.
6. **NEVER close issues.** The issue owner decides when to close. Agents link PRs with `Closes #X` in the PR body, but GitHub's auto-close only triggers on merge -- and the owner can always reopen if needed.
7. **Comment on the issue when a linked PR is merged.** Let the owner know the work is done so they can verify and close.
8. **Branch naming is intentional** -- `feat/`, `fix/`, `docs/`, `chore/`. Never work directly on main, even locally.

## Safety Checks 🛡️

**Avoid Race Conditions:**
Before working on any PR (review, push, merge), agents MUST check if it's still open.

```bash
STATE=$(gh pr view <N> --json state --jq .state)
if [ "$STATE" != "OPEN" ]; then
  echo "⚠️ PR <N> is $STATE. Aborting to avoid conflicts."
  exit 0
fi
```

## Solo Repos (Direct Commit Allowed)
- `ManniTheRaccoon/y-watch` ✅

## Shared Repos (PR Required)
- `Yesterday-AI/agentic-foundation` 🔀

## Agent Account Setup 🔑

How to set up a GitHub account for a new AI agent:

### 1. Register Account
Create a new GitHub account using the agent's email:
```
<yourname+agentname@yesterday-ai.de>
```
Example: `alex+manni@yesterday-ai.de`

### 2. Add SSH Key
1. On the agent's server, generate a key:
   ```bash
   ssh-keygen -t ed25519 -C "agentname@yesterday-ai.de" -f ~/.ssh/id_ed25519_agentname
   ```
2. Add to `~/.ssh/config`:
   ```
   Host github.com
     IdentityFile ~/.ssh/id_ed25519_agentname
   ```
3. Add the public key to GitHub: https://github.com/settings/keys

### 3. Authenticate `gh` CLI
```bash
gh auth login
```
- Select **GitHub.com** → **SSH** → **Login with a web browser**
- The agent will output a one-time code (e.g. `ABCD-1234`)
- **Human action required:** Enter this code at https://github.com/login/device
- Verify: `gh auth status`

### 4. Grant Repository Access
With a **@Yesterday-AI** org admin:
- Invite the agent account as collaborator to selected private repos
- Agent accepts via: `gh api user/repository_invitations --method GET` then `PATCH`

---

*Authored by ManniTheRaccoon.* 🦝
