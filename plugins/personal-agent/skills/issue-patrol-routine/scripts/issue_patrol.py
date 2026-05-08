#!/usr/bin/env python3
"""
Issue Patrol Scanner — Deterministic issue classification for engineering agents.

Scans GitHub repos via `gh` CLI, classifies open issues into actionable queues,
and persists state + cycle log for cross-session continuity.

Usage:
    python3 issue_patrol.py \
        --repos "Owner/repo1 Owner/repo2" \
        --state memory/issue-patrol-state.json \
        --log memory/issue-patrol-log.jsonl \
        --agent-user YyScotty
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


SCHEMA_VERSION = 1
CLEANUP_DAYS = 7

IMPLEMENTATION_LABELS = {"bug", "feature", "enhancement"}
BLOCKED_LABELS = {"blocked", "waiting-for-input", "wontfix"}
CLARIFICATION_LABELS = {"needs-clarification", "question"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def gh_list_issues(repo: str) -> list[dict]:
    """Fetch open issues (not PRs) for a repo via gh CLI."""
    cmd = [
        "gh", "issue", "list",
        "--repo", repo,
        "--state", "open",
        "--limit", "200",
        "--json", "number,title,labels,assignees,updatedAt,body,comments"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"⚠️  Failed to fetch issues for {repo}: {result.stderr.strip()}", file=sys.stderr)
            return []
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"⚠️  Error fetching {repo}: {e}", file=sys.stderr)
        return []


def gh_list_prs(repo: str) -> list[dict]:
    """Fetch open PRs to detect linked branches."""
    cmd = [
        "gh", "pr", "list",
        "--repo", repo,
        "--state", "open",
        "--limit", "200",
        "--json", "number,headRefName,body,title"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return []


def find_linked_pr(issue_number: int, prs: list[dict]) -> tuple[int | None, str | None]:
    """Check if any open PR references this issue (via 'Closes #N' or 'Fixes #N')."""
    for pr in prs:
        body = (pr.get("body") or "") + " " + (pr.get("title") or "")
        body_lower = body.lower()
        for keyword in ["closes", "fixes", "resolves"]:
            if f"{keyword} #{issue_number}" in body_lower:
                return pr["number"], pr.get("headRefName")
    return None, None


def classify_issue(
    issue: dict,
    agent_user: str,
    prs: list[dict],
    prev_state: dict | None
) -> dict:
    """Classify a single issue into a queue. Returns issue state dict."""
    number = issue["number"]
    title = issue["title"]
    labels = {lbl["name"].lower() for lbl in issue.get("labels", [])}
    assignees = {a["login"] for a in issue.get("assignees", [])}
    updated_at = issue.get("updatedAt", "")
    body = issue.get("body") or ""

    # Carry forward first-seen cycle
    first_seen = (prev_state or {}).get("firstSeenCycle")
    prev_queue = (prev_state or {}).get("queue")
    last_commented = (prev_state or {}).get("lastCommentedAt")

    linked_pr, linked_branch = find_linked_pr(number, prs)

    # Classification logic (order matters — first match wins)

    # 1. Assigned to someone else
    if assignees and agent_user not in assignees:
        queue = "assignedToOthersQueue"
        status = "assigned-to-others"
        reason = f"Assigned to {', '.join(assignees)}"

    # 2. Has active PR (in progress)
    elif linked_pr is not None:
        queue = "inProgressQueue"
        status = "implementing"
        reason = f"Linked to PR #{linked_pr} on branch {linked_branch}"

    # 3. Blocked
    elif labels & BLOCKED_LABELS:
        queue = "blockedQueue"
        status = "blocked"
        reason = f"Has blocking label: {labels & BLOCKED_LABELS}"

    # 4. Needs clarification
    elif labels & CLARIFICATION_LABELS:
        queue = "needsClarificationQueue"
        status = "waiting"
        reason = f"Has clarification label: {labels & CLARIFICATION_LABELS}"

    # 5. Empty body = needs clarification
    elif len(body.strip()) < 20:
        queue = "needsClarificationQueue"
        status = "waiting"
        reason = "Issue body is empty or too short to implement"

    # 6. First time seeing this issue
    elif first_seen is None:
        queue = "newQueue"
        status = "new"
        reason = "First time seen in patrol"

    # 7. Has implementation-ready labels or assigned to me
    elif labels & IMPLEMENTATION_LABELS or agent_user in assignees:
        queue = "readyToImplementQueue"
        status = "ready"
        reason = f"Labeled {labels & IMPLEMENTATION_LABELS or 'N/A'}, assigned={agent_user in assignees}"

    # 8. Previously triaged — keep in previous queue if valid
    elif prev_queue and prev_queue != "newQueue":
        queue = prev_queue
        status = (prev_state or {}).get("status", "triaged")
        reason = "Carrying forward previous classification"

    # 9. Default: needs triage
    else:
        queue = "newQueue"
        status = "needs-triage"
        reason = "No clear classification signals"

    return {
        "title": title,
        "queue": queue,
        "labels": sorted(labels),
        "assignee": next(iter(assignees), None),
        "firstSeenCycle": first_seen,  # Will be set by caller if None
        "lastUpdatedAt": updated_at,
        "linkedPR": linked_pr,
        "linkedBranch": linked_branch,
        "status": status,
        "reason": reason,
        "lastCommentedAt": last_commented,
        "closedAt": None,
    }


def load_state(path: Path) -> dict:
    """Load existing state or return empty state."""
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "version": SCHEMA_VERSION,
        "lastPatrol": None,
        "cycleCount": 0,
        "agentUser": "",
        "repos": {},
    }


def save_state(state: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def append_log(entry: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def cleanup_closed(repo_state: dict) -> int:
    """Remove issues closed for more than CLEANUP_DAYS."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=CLEANUP_DAYS)).isoformat()
    to_remove = []
    for num, issue in repo_state.get("issues", {}).items():
        if issue.get("closedAt") and issue["closedAt"] < cutoff:
            to_remove.append(num)
    for num in to_remove:
        del repo_state["issues"][num]
    return len(to_remove)


def run_patrol(repos: list[str], state_path: Path, log_path: Path, agent_user: str) -> dict:
    state = load_state(state_path)
    state["agentUser"] = agent_user
    cycle = state["cycleCount"] + 1
    state["cycleCount"] = cycle
    state["lastPatrol"] = now_iso()

    total_open = 0
    queue_counts = {
        "newQueue": 0,
        "needsClarificationQueue": 0,
        "readyToImplementQueue": 0,
        "inProgressQueue": 0,
        "blockedQueue": 0,
        "assignedToOthersQueue": 0,
    }
    changes = []

    for repo in repos:
        issues = gh_list_issues(repo)
        prs = gh_list_prs(repo)

        if repo not in state["repos"]:
            state["repos"][repo] = {"lastCheck": None, "issues": {}}

        repo_state = state["repos"][repo]
        repo_state["lastCheck"] = now_iso()

        open_numbers = set()
        for issue in issues:
            num = str(issue["number"])
            open_numbers.add(num)
            total_open += 1

            prev = repo_state["issues"].get(num)
            classified = classify_issue(issue, agent_user, prs, prev)

            # Set firstSeenCycle for new issues
            if classified["firstSeenCycle"] is None:
                classified["firstSeenCycle"] = cycle

            # Track queue changes
            prev_queue = prev["queue"] if prev else None
            if prev_queue and prev_queue != classified["queue"]:
                changes.append({
                    "repo": repo,
                    "issue": issue["number"],
                    "from": prev_queue,
                    "to": classified["queue"],
                })

            queue_counts[classified["queue"]] = queue_counts.get(classified["queue"], 0) + 1
            repo_state["issues"][num] = classified

        # Mark closed issues
        for num in list(repo_state["issues"].keys()):
            if num not in open_numbers and repo_state["issues"][num].get("closedAt") is None:
                repo_state["issues"][num]["closedAt"] = now_iso()
                repo_state["issues"][num]["queue"] = "closed"

        cleanup_closed(repo_state)

    save_state(state, state_path)

    log_entry = {
        "cycle": cycle,
        "timestamp": state["lastPatrol"],
        "reposScanned": len(repos),
        "totalOpen": total_open,
        "queues": queue_counts,
        "changes": changes,
    }
    append_log(log_entry, log_path)

    return log_entry


def main():
    parser = argparse.ArgumentParser(description="Issue Patrol Scanner")
    parser.add_argument("--repos", required=True, help="Space-separated list of owner/repo")
    parser.add_argument("--state", required=True, help="Path to state JSON file")
    parser.add_argument("--log", required=True, help="Path to cycle log JSONL file")
    parser.add_argument("--agent-user", required=True, help="GitHub username of the agent")
    args = parser.parse_args()

    repos = args.repos.split()
    result = run_patrol(repos, Path(args.state), Path(args.log), args.agent_user)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
