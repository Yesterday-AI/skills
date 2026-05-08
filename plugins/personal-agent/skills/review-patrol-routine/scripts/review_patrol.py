#!/usr/bin/env python3
"""
Review Patrol — deterministic PR scanner and queue classifier.

Scans a list of GitHub repos for open PRs, classifies each into a review queue,
persists state across runs, and appends a cycle log. No LLM needed.

Configuration (in order of precedence):
1. Environment variables: PATROL_REPOS (comma-separated), PATROL_SELF_LOGINS (comma-separated)
2. Config file: $WORKSPACE/patrol-config.json  {"repos": [...], "selfLogins": [...]}
3. Inline REPOS / SELF_LOGINS constants below (fallback)

Usage:
    python3 review_patrol.py markdown   # human-readable output
    python3 review_patrol.py json       # machine-readable output (default)
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── CONSTANTS ──────────────────────────────────────────────────────────────

MERGEABILITY_BLOCKERS = {"DIRTY", "BLOCKED", "UNKNOWN", "UNSTABLE"}
MERGEABILITY_READY = {"CLEAN", "HAS_HOOKS"}

# Workspace root: PATROL_WORKSPACE env > cwd
WORKSPACE = Path(os.getenv("PATROL_WORKSPACE", "")).resolve() if os.getenv("PATROL_WORKSPACE") else Path.cwd()
STATE_PATH = WORKSPACE / "memory" / "heartbeat-state.json"
LOG_PATH = WORKSPACE / "memory" / "patrol-log.jsonl"
CONFIG_PATH = WORKSPACE / "patrol-config.json"

# ─── INLINE FALLBACK CONFIGURATION ─────────────────────────────────────────
# Used only if neither env vars nor patrol-config.json provide values.

_FALLBACK_REPOS = [
    # "org/repo-a",
    # "org/repo-b",
]

_FALLBACK_SELF_LOGINS = {
    # "YyMyAgent",
}


def load_config():
    """Load repos and self-logins from env, config file, or inline fallback."""
    # 1. Environment variables
    env_repos = os.getenv("PATROL_REPOS", "").strip()
    env_logins = os.getenv("PATROL_SELF_LOGINS", "").strip()
    if env_repos:
        repos = [r.strip() for r in env_repos.split(",") if r.strip()]
        logins = {l.strip() for l in env_logins.split(",") if l.strip()} if env_logins else set()
        return repos, logins

    # 2. Config file
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open() as f:
                cfg = json.load(f)
            repos = cfg.get("repos", [])
            logins = set(cfg.get("selfLogins", []))
            if repos:
                return repos, logins
        except (json.JSONDecodeError, KeyError):
            pass

    # 3. Inline fallback
    return _FALLBACK_REPOS, _FALLBACK_SELF_LOGINS


REPOS, SELF_LOGINS = load_config()


# ─── HELPERS ────────────────────────────────────────────────────────────────

def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_json(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"command failed: {' '.join(cmd)}")
    return json.loads(proc.stdout or "null")


def load_state():
    if not STATE_PATH.exists():
        return {"version": 2, "lastPatrol": None, "cycleCount": 0, "repos": {repo: {"lastCheck": None, "prs": {}} for repo in REPOS}, "lastSummary": None}
    with STATE_PATH.open() as f:
        state = json.load(f)
    state.setdefault("version", 2)
    state.setdefault("cycleCount", 0)
    state.setdefault("repos", {})
    for repo in REPOS:
        state["repos"].setdefault(repo, {"lastCheck": None, "prs": {}})
        state["repos"][repo].setdefault("prs", {})
    return state


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


# ─── CLASSIFICATION ────────────────────────────────────────────────────────

def classify_pr(pr_state, head_sha, review_decision, is_draft):
    if is_draft:
        return None
    last_reviewed_sha = pr_state.get("lastReviewedHeadSha")
    last_verdict = pr_state.get("lastVerdict")
    if last_verdict == "REQUEST_CHANGES" and last_reviewed_sha and last_reviewed_sha != head_sha:
        return "re-review"
    if not pr_state.get("lastReviewedAt"):
        return "new-review"
    if review_decision in (None, "", "REVIEW_REQUIRED") and last_reviewed_sha != head_sha:
        return "new-review"
    return None


def is_ready_to_merge(pr_state, pr):
    if bool(pr.get("isDraft")):
        return False
    if (pr_state.get("lastVerdict") or "") != "APPROVE":
        return False
    if pr_state.get("lastReviewedHeadSha") != pr.get("headRefOid"):
        return False
    return (pr.get("mergeStateStatus") or "UNKNOWN") in MERGEABILITY_READY


def is_stale_approved(pr_state, pr):
    if bool(pr.get("isDraft")):
        return False
    if (pr_state.get("lastVerdict") or "") != "APPROVE":
        return False
    return pr_state.get("lastReviewedHeadSha") not in (None, pr.get("headRefOid"))


def derive_status_reason(pr_state, pr, category):
    review_decision = pr.get("reviewDecision") or ""
    merge_state = pr.get("mergeStateStatus") or "UNKNOWN"

    if bool(pr.get("isDraft")):
        return "draft", "draft_pr"
    if category == "new-review":
        return "new", "unreviewed"
    if category == "re-review":
        return "rereview", "new_commits_after_requested_changes"
    if is_ready_to_merge(pr_state, pr):
        return "ready", "approved_on_current_head"
    if is_stale_approved(pr_state, pr):
        return "stale", "approval_stale_after_new_commits"
    if review_decision == "CHANGES_REQUESTED" and merge_state == "DIRTY":
        return "blocked", "requested_changes_and_merge_conflicts"
    if review_decision == "CHANGES_REQUESTED" and merge_state == "BLOCKED":
        return "blocked", "requested_changes_and_blocked_merge"
    if review_decision == "CHANGES_REQUESTED":
        return "blocked", "waiting_for_author_changes"
    if merge_state == "DIRTY":
        return "blocked", "merge_conflicts"
    if merge_state == "BLOCKED":
        return "blocked", "blocked_mergeability"
    if merge_state == "UNKNOWN":
        return "blocked", "mergeability_unknown"
    if merge_state == "UNSTABLE":
        return "blocked", "checks_unstable"
    return "tracked", "open_unclassified"


# ─── MAIN ───────────────────────────────────────────────────────────────────

def main():
    if not REPOS:
        print("Error: REPOS list is empty. Edit review_patrol.py to add your repos.", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    summary = {
        "generatedAt": utc_now(), "reposScanned": 0, "openPrs": 0,
        "newReviewQueue": [], "reReviewQueue": [], "readyToMerge": [],
        "staleApproved": [], "blockedByReview": [], "blockedByMergeability": [],
        "drafts": [], "errors": [], "trackedItems": [],
    }

    for repo in REPOS:
        repo_state = state["repos"][repo]
        try:
            prs = run_json([
                "gh", "pr", "list", "--repo", repo, "--state", "open",
                "--json", "number,title,author,reviewDecision,isDraft,updatedAt,headRefOid,url,mergeStateStatus",
            ])
        except Exception as e:
            summary["errors"].append({"repo": repo, "error": str(e)})
            continue

        summary["reposScanned"] += 1
        summary["openPrs"] += len(prs)
        seen = set()

        for pr in prs:
            number = str(pr["number"])
            seen.add(number)
            author = ((pr.get("author") or {}).get("login") or "")
            if author in SELF_LOGINS:
                continue

            pr_state = repo_state["prs"].setdefault(number, {})
            pr_state.update({
                "title": pr.get("title"), "url": pr.get("url"), "author": author,
                "reviewDecision": pr.get("reviewDecision") or "",
                "mergeStateStatus": pr.get("mergeStateStatus") or "UNKNOWN",
                "headSha": pr.get("headRefOid"),
                "isDraft": bool(pr.get("isDraft")),
                "updatedAt": pr.get("updatedAt"),
                "open": True, "lastSeenAt": summary["generatedAt"],
            })

            category = classify_pr(pr_state, pr.get("headRefOid"), pr.get("reviewDecision") or "", bool(pr.get("isDraft")))

            item = {
                "repo": repo, "number": pr["number"], "title": pr.get("title"),
                "author": author, "url": pr.get("url"), "headSha": pr.get("headRefOid"),
                "reviewDecision": pr.get("reviewDecision") or "",
                "mergeStateStatus": pr.get("mergeStateStatus") or "UNKNOWN",
            }
            status, reason = derive_status_reason(pr_state, pr, category)
            item["status"] = status
            item["reason"] = reason
            summary["trackedItems"].append(item)

            if pr.get("isDraft"):
                summary["drafts"].append(item)
            elif category == "new-review":
                summary["newReviewQueue"].append(item)
            elif category == "re-review":
                summary["reReviewQueue"].append(item)
            else:
                if is_ready_to_merge(pr_state, pr):
                    summary["readyToMerge"].append(item)
                if is_stale_approved(pr_state, pr):
                    summary["staleApproved"].append(item)
                if (pr.get("reviewDecision") or "") == "CHANGES_REQUESTED":
                    summary["blockedByReview"].append(item)
                if (pr.get("mergeStateStatus") or "UNKNOWN") in MERGEABILITY_BLOCKERS:
                    summary["blockedByMergeability"].append(item)

        for number, pr_st in repo_state["prs"].items():
            if number not in seen:
                pr_st["open"] = False
        repo_state["lastCheck"] = summary["generatedAt"]

    # Update state
    state["lastPatrol"] = summary["generatedAt"]
    state["cycleCount"] = int(state.get("cycleCount") or 0) + 1
    summary["cycleCount"] = state["cycleCount"]
    state["lastSummary"] = {
        "generatedAt": summary["generatedAt"], "cycleCount": summary["cycleCount"],
        "reposScanned": summary["reposScanned"], "openPrs": summary["openPrs"],
        "newReviewCount": len(summary["newReviewQueue"]),
        "reReviewCount": len(summary["reReviewQueue"]),
        "readyToMergeCount": len(summary["readyToMerge"]),
        "staleApprovedCount": len(summary["staleApproved"]),
        "blockedByReviewCount": len(summary["blockedByReview"]),
        "blockedByMergeabilityCount": len(summary["blockedByMergeability"]),
        "draftCount": len(summary["drafts"]),
        "errorCount": len(summary["errors"]),
    }
    save_state(state)

    # Append cycle log
    log_entry = {
        "cycle": summary["cycleCount"], "at": summary["generatedAt"],
        "scanned": summary["reposScanned"], "open": summary["openPrs"],
        "new": len(summary["newReviewQueue"]), "reReview": len(summary["reReviewQueue"]),
        "readyToMerge": len(summary["readyToMerge"]),
        "staleApproved": len(summary["staleApproved"]),
        "blockedByReview": len(summary["blockedByReview"]),
        "blockedByMergeability": len(summary["blockedByMergeability"]),
        "drafts": len(summary["drafts"]), "errors": len(summary["errors"]),
        "items": [{"pr": f"{i['repo']}#{i['number']}", "status": i["status"], "reason": i["reason"]} for i in summary["trackedItems"]],
    }
    if summary["errors"]:
        log_entry["errorDetails"] = [f"{e['repo']}: {e['error'][:80]}" for e in summary["errors"]]
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a") as lf:
            lf.write(json.dumps(log_entry, separators=(",", ":")) + "\n")
    except Exception:
        pass

    # Output
    mode = sys.argv[1] if len(sys.argv) > 1 else "json"
    if mode == "markdown":
        print(f"# Review Patrol — Cycle {summary['cycleCount']}")
        print()
        for k in ["reposScanned", "openPrs"]:
            print(f"- {k}: {summary[k]}")
        for k in ["newReviewQueue", "reReviewQueue", "readyToMerge", "staleApproved", "blockedByReview", "blockedByMergeability", "drafts"]:
            print(f"- {k}: {len(summary[k])}")
        for section, label in [("newReviewQueue", "New review queue"), ("reReviewQueue", "Re-review queue")]:
            if summary[section]:
                print(f"\n## {label}")
                for i in summary[section]:
                    print(f"- {i['repo']}#{i['number']} — {i['title']} ({i['author']}) · reason={i['reason']}")
        if summary["readyToMerge"]:
            print("\n## Ready to merge")
            for i in summary["readyToMerge"]:
                print(f"- {i['repo']}#{i['number']} — {i['title']} [{i['mergeStateStatus']}] ({i['author']}) · reason={i['reason']}")
        if summary["staleApproved"]:
            print("\n## Stale approved")
            for i in summary["staleApproved"]:
                print(f"- {i['repo']}#{i['number']} — {i['title']} ({i['author']}) · reason={i['reason']}")
        for section, label in [("blockedByReview", "Blocked by review"), ("blockedByMergeability", "Blocked by mergeability")]:
            if summary[section]:
                print(f"\n## {label}")
                for i in summary[section]:
                    extra = f" [{i['mergeStateStatus']}]" if section == "blockedByMergeability" else ""
                    print(f"- {i['repo']}#{i['number']} — {i['title']}{extra} ({i['author']}) · reason={i['reason']}")
        if summary["errors"]:
            print("\n## Errors")
            for i in summary["errors"]:
                print(f"- {i['repo']}: {i['error']}")
    else:
        json.dump(summary, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
