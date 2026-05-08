---
name: using-github
description: |
  Operating policies for safe GitHub interaction via the `gh` CLI and `git`.
  Use this skill before any PR edit, comment, branch operation, push, or
  merge interaction. Covers state-before-action checks, force-push discipline,
  squash-merge divergence handling, and verification that mutations actually
  landed.
metadata:
  category: engineering
---

# using-github

Operating policies for interacting with GitHub via `gh` and `git`. Read before any PR / branch / push action. The rules below exist because each one was learned from a real failure.

## P1: Check PR state before any edit or comment

**Rule:** before `gh pr edit`, `gh pr comment`, `gh pr review`, or any mutation on a PR, run:

```bash
gh pr view <num> --json state,mergedAt,closed --jq '.state, .mergedAt, .closed'
```

If `state` is `MERGED` or `CLOSED`: **stop**. The mutation will silently no-op or land in an unintended place. Tell the human, ask whether to open a follow-up PR instead.

**Why:** `gh pr edit` on a merged PR returns success but does not change the visible body. `gh pr comment` on a closed PR posts to the closed PR (which nobody will see). Both are silent failures.

**How to apply:** any time more than 5 minutes have passed since the last `gh pr view`, or any time someone else might have merged in the meantime, re-check state first. Treat PR state as live data that decays fast.

## P2: Verify mutations actually landed

**Rule:** after every `gh pr edit`, `gh pr comment`, `gh issue edit`, etc., re-fetch the resource and confirm the change is visible:

```bash
gh pr view <num> --json body --jq '.body' | head -20
```

Stderr warnings (e.g. `GraphQL: Projects (classic) is being deprecated...`) are not the same as failure -- but they are also not the same as success. Always verify with a re-fetch. Exit code 0 from `gh` means the request was accepted; it does not mean your change is live (see P1).

**Why:** the `gh` CLI prints warnings to stderr and continues. A merged-PR edit returns 0 but does nothing visible.

## P3: Verify branch before every commit

**Rule:** before every `git commit`, run:

```bash
git branch --show-current
```

Confirm the branch is what you expect. Do not trust that the branch from 10 minutes ago is still the active one -- `git checkout`, hook switches, and worktree changes can move it.

**Why:** committing to the wrong branch (especially main when you meant a feature branch) is hard to unwind. Cherry-picking after the fact loses author/timestamp context.

## P4: Never force-push, with one exception

**Rule:** never `git push --force` or `git push -f`. If you genuinely need to overwrite remote history (e.g. squash before review, fix a wrong commit message), use `git push --force-with-lease` AND only with the human's explicit, in-this-session consent.

**Why:** force-push overwrites collaborators' work irrecoverably. `--force-with-lease` aborts if anyone else has pushed since your last fetch, which is the safety net `--force` lacks. Even with `--force-with-lease`, the human should know.

**How to apply:** when tempted to force-push: stop, describe what you want to do, ask. Do not assume past consent applies to a new force-push.

## P5: Never destructively reset working-tree changes

**Rule:** never `git checkout <file>`, `git restore <file>`, `git reset --hard`, or `git clean -fd` on uncommitted changes that you did not personally just write. If your own edits are wrong on disk, use the `Edit` tool with explicit `old_string` / `new_string` reverts instead.

**Why:** the working tree may contain the human's uncommitted edits that you never saw. Discarding them silently destroys hours of work.

**How to apply:** when the working tree is unexpectedly modified, ask: "I see uncommitted changes to <files> -- should I commit, stash, or wait?" Do not unilaterally clean.

## P6: Squash-merge divergence -- branch fresh, do not rebase

**Rule:** when a PR is squash-merged, the original branch diverges from `origin/main` (the squash creates a new commit; the branch's commits remain visible in history but unreachable from main). To continue work:

```bash
git fetch origin
git checkout main && git pull
git checkout -b <new-branch-name>  # branch fresh from updated main
```

Do NOT `git rebase main` on the old branch -- it will replay the original commits onto the squash, producing duplicate work. Do NOT `git push --force` to "clean up" the old branch.

**Why:** rebase-after-squash is the most common cause of duplicated commits and the second-most common reason for "why is my PR diff huge".

## P7: Read PR comments before claiming "done"

**Rule:** when an automated reviewer (Bugbot, CodeRabbit, Renovate, etc.) leaves comments on a PR, read them before declaring the PR ready or before merging. Address each comment explicitly: either fix the issue, push back with reasoning, or note why it is out of scope.

**Why:** silently ignored review comments accumulate technical debt and erode reviewer trust. Bugbot in particular catches real issues (security, bugs, type holes).

```bash
gh pr view <num> --json comments,reviews --jq '.comments[].body, .reviews[].body'
```

## P8: Pull before branching from main

**Rule:** before `git checkout -b <new-branch>` from main, always:

```bash
git checkout main && git pull --no-rebase
```

A stale local main as the branch base means your PR's "additions" diff includes other people's commits, which makes review noisy and risks reverting their work via merge conflicts.

**Why:** working from a stale base produces PRs that look like they are reverting unrelated changes.

## P9: Pass PR bodies via `--body-file`, not inline

**Rule:** when creating or editing a PR with multi-line body content, write the body to a temp file and pass `--body-file /tmp/<file>.md`:

```bash
gh pr create --title "..." --body-file /tmp/pr-body.md
gh pr edit <num> --body-file /tmp/pr-body.md
```

Do not pass multi-line bodies via inline `--body "$(cat <<EOF ...)"` heredocs -- they interact badly with shell quoting, history expansion, and special characters.

**Why:** inline heredocs can silently truncate or mangle content, especially with backticks, dollar signs, or em-dashes.

## P10: Keep `gh auth` and `git push` aligned

**Rule:** after `gh auth switch`, also run:

```bash
gh auth setup-git
```

Otherwise `git push` may use a stale credential from the macOS Keychain, overriding the active gh auth identity.

**Why:** `gh auth switch` only updates the gh CLI's internal token; it does not propagate to `git push`. Symptoms: pushing to a repo as the wrong user, "permission denied" despite `gh auth status` showing the right user.

## P11: Sync org-level repo lists on visibility changes / new repos

**Rule:** when adding a new repo to a GitHub org OR flipping an existing repo's visibility (private ↔ public), check whether the org maintains profile-style repo lists in `<org>/.github` (public profile) and/or `<org>/.github-private` (private member-only landing). If either exists and lists repos, update them as part of the same change set:

- Public profile (`<org>/.github/profile/README.md`): list/unlist the repo in the relevant table.
- Private landing (`<org>/.github-private/profile/README.md` or equivalent): update the visibility marker (e.g. `🌐` ↔ `🔒` columns are a common convention) and any catalog summaries that mention the repo by name.
- Also sweep for sibling files in those repos (e.g. curated `IMPORTANT-REPOS.md` or similar) and surface them to the human if found.

```bash
gh repo view <org>/.github --json visibility
gh repo view <org>/.github-private --json visibility
```

Interpret the result:

- Exit 0 -- repo exists and is accessible. Read its `profile/README.md` (or equivalent) and treat the list as part of the change set.
- 404 / "Could not resolve to a Repository" -- **AMBIGUOUS**. GitHub returns 404 both for repos that do not exist AND for private repos the current token cannot see (a deliberate security measure to avoid confirming existence). Do NOT treat 404 as "rule does not apply" without further evidence. Either verify the token sees the org's private repos (e.g. `gh auth status` confirms an account with org-member scope, and `gh api orgs/<org>/memberships/{username}` returns `state: active`), or ask the human whether the convention applies.
- Network or server error -- stop and surface to the human.

**Why:** the public profile is the org's outward-facing landing page; out-of-date listings either advertise repos that 404 for non-members or hide repos that are actually public. The private landing typically uses a `Vis` column to mirror public state -- drift means org members get a wrong picture of what is shareable. Both files are easy to forget because they live in their own repos, separate from the repo whose visibility is changing.

**How to apply:** when the human asks for a visibility flip or a new-repo addition, treat the org-list update as a sibling task in the same plan, with its own PR(s) per repo. The human should not need to remind you.

## Quick reference

| Situation | Command |
|---|---|
| Before any PR mutation | `gh pr view <num> --json state,mergedAt --jq .` |
| After any PR mutation | `gh pr view <num> --json body --jq '.body' \| head -20` |
| Before every commit | `git branch --show-current` |
| After squash-merge of your branch | `git fetch && git checkout main && git pull && git checkout -b <new-branch>` |
| Read automated PR reviews | `gh pr view <num> --json comments,reviews --jq '.comments[].body, .reviews[].body'` |
| Multi-line PR body | write to `/tmp/<file>.md`, pass `--body-file` |
| Switch GitHub identity | `gh auth switch && gh auth setup-git` |
| Visibility flip / new repo | also update `<org>/.github/profile/README.md` and `<org>/.github-private/profile/README.md` if they exist |

## When in doubt

If a GitHub action might be irreversible (force-push, branch delete, PR close, repo settings change), describe it to the human and ask before running. The cost of a 10-second confirmation is much less than the cost of an unrecoverable mistake.
