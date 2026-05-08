# Review Patrol State Reference

## Purpose

`memory/heartbeat-state.json` is the durable state layer for PR patrol.
It prevents duplicate review work and enables deterministic re-review detection.

## Invariants

- `lastReviewedHeadSha` must be updated after every real review submission
- `lastVerdict` must reflect the actual submitted verdict
- `lastMergedAt` is only set after the merge actually happened
- `open=false` means the PR disappeared from the open PR list on a later patrol

## Minimal PR Record

```json
{
  "title": "feat: add foo",
  "url": "https://github.com/org/repo/pull/12",
  "author": "someone",
  "headSha": "abc123",
  "lastReviewedAt": "2026-03-21T02:30:00Z",
  "lastReviewedHeadSha": "abc123",
  "lastVerdict": "REQUEST_CHANGES",
  "lastMergedAt": null,
  "open": true
}
```

## Seeding Existing History

When adopting the patrol system late, seed already-reviewed active PRs into the
state file. Otherwise the first cycle will falsely classify them as new.

## Queue Criteria

### readyToMerge
- `lastVerdict == APPROVE`
- PR is still open, not a draft
- `headSha == lastReviewedHeadSha`
- `mergeStateStatus` is `CLEAN` or `HAS_HOOKS`

### staleApproved
- `lastVerdict == APPROVE`
- PR is still open, not a draft
- `headSha != lastReviewedHeadSha` (branch moved since approval)

### blockedByReview
- `lastVerdict == REQUEST_CHANGES`
- PR is still open
- `headSha == lastReviewedHeadSha` (no new commits)

### blockedByMergeability
- GitHub `mergeStateStatus` is `DIRTY`, `BLOCKED`, `UNKNOWN`, or `UNSTABLE`

These are independent dimensions. One PR may appear in multiple lists.

## Per-PR `status` + `reason`

Every tracked PR gets a `status` and `reason` for log transparency:

| Status | Reason examples |
|--------|----------------|
| `new` | `unreviewed` |
| `rereview` | `new_commits_after_requested_changes` |
| `ready` | `approved_on_current_head` |
| `stale` | `approval_stale_after_new_commits` |
| `blocked` | `waiting_for_author_changes`, `requested_changes_and_merge_conflicts`, `merge_conflicts`, `checks_unstable` |
| `draft` | `draft_pr` |
| `tracked` | `open_unclassified` |

## Common Failure Modes

### Submitted review, forgot state update
Effect: PR may reappear as new or never enter correct re-review state.

### Wrong `lastReviewedHeadSha`
Effect: re-review classification becomes noisy or misses true updates.

### Repo removed from scope but left in state forever
Effect: harmless stale data, but confusing. Prefer pruning dead repos.
