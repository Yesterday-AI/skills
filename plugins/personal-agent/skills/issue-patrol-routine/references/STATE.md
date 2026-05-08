# Issue Patrol State Schema

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | `int` | Schema version. Currently `1`. |
| `lastPatrol` | `string` | ISO 8601 timestamp of last patrol run. |
| `cycleCount` | `int` | Total number of patrol cycles completed. |
| `agentUser` | `string` | GitHub username of the agent (for assignee filtering). |
| `repos` | `object` | Map of `owner/repo` → repo state. |

## Repo State

| Field | Type | Description |
|-------|------|-------------|
| `lastCheck` | `string` | ISO 8601 timestamp of last check for this repo. |
| `issues` | `object` | Map of issue number (string) → issue state. |

## Issue State

| Field | Type | Description |
|-------|------|-------------|
| `title` | `string` | Issue title (for quick reference without API call). |
| `queue` | `string` | Current queue classification. One of: `newQueue`, `needsClarificationQueue`, `readyToImplementQueue`, `inProgressQueue`, `blockedQueue`, `assignedToOthersQueue`. |
| `labels` | `string[]` | Current GitHub labels. |
| `assignee` | `string\|null` | GitHub username of assignee, or null. |
| `firstSeenCycle` | `int` | Cycle number when this issue was first seen. |
| `lastUpdatedAt` | `string` | ISO 8601 timestamp of last GitHub update. |
| `linkedPR` | `int\|null` | PR number if implementation is in progress. |
| `linkedBranch` | `string\|null` | Branch name if implementation is in progress. |
| `status` | `string` | Human-readable status. E.g. `new`, `triaging`, `ready`, `implementing`, `blocked`, `waiting`. |
| `reason` | `string` | Why this issue is in its current queue. |
| `lastCommentedAt` | `string\|null` | When the agent last commented on this issue. |
| `closedAt` | `string\|null` | When the issue was closed (for cleanup). |

## Lifecycle

1. Issue first appears → `newQueue`, `firstSeenCycle` = current cycle
2. Agent triages → reclassified to appropriate queue
3. Agent starts work → `inProgressQueue`, `linkedPR` + `linkedBranch` set
4. PR merged / issue closed → removed from active state (or marked closed)

## Cleanup

Issues closed for >7 days should be pruned from state to prevent unbounded growth.
The patrol script handles this automatically.
