#!/bin/bash

# Agent Swarm: Monitor Agents 🕵️‍♂️
# Usage: ./monitor-agents.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🕵️‍♂️ Checking Agent Swarm Status..."

# 1. Check Git Worktrees
WORKTREE_DIR="../worktrees"
if [ ! -d "$WORKTREE_DIR" ]; then
    echo "No worktrees found."
    exit 0
fi

# 2. Iterate Worktrees
for task in "$WORKTREE_DIR"/*; do
    if [ -d "$task" ]; then
        TASK_NAME=$(basename "$task")
        echo -e "\n📌 Task: $TASK_NAME"
        
        # Check Branch Status
        cd "$task" || continue
        BRANCH=$(git branch --show-current)
        echo "  Branch: $BRANCH"
        
        # Check PR
        PR_URL=$(gh pr list --head "$BRANCH" --json url --jq '.[0].url')
        if [ -n "$PR_URL" ]; then
            echo -e "  PR: ${GREEN}$PR_URL${NC}"
            
            # Check CI (Last Run)
            CI_STATUS=$(gh run list --branch "$BRANCH" --limit 1 --json conclusion --jq '.[0].conclusion')
            if [ "$CI_STATUS" == "success" ]; then
                echo -e "  CI: ${GREEN}PASS${NC}"
            elif [ "$CI_STATUS" == "failure" ]; then
                echo -e "  CI: ${RED}FAIL${NC}"
            else
                echo "  CI: $CI_STATUS"
            fi
        else
            echo "  PR: None (in progress)"
        fi
        
        # Check if Stale (Last Commit)
        LAST_COMMIT=$(git log -1 --format=%cr)
        echo "  Last Activity: $LAST_COMMIT"
        
        cd - > /dev/null
    fi
done

echo -e "\n✅ Monitoring Complete."
