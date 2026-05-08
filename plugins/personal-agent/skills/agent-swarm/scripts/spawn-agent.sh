#!/bin/bash

# Agent Swarm: Spawn Agent 🐣
# Usage: ./spawn-agent.sh <task-name> <branch-name> "<prompt>"

TASK_NAME="$1"
BRANCH_NAME="$2"
PROMPT="$3"

if [ -z "$TASK_NAME" ] || [ -z "$BRANCH_NAME" ] || [ -z "$PROMPT" ]; then
    echo "Usage: ./spawn-agent.sh <task-name> <branch-name> \"<prompt>\""
    exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
WORKTREE_DIR="$REPO_ROOT/../worktrees/$TASK_NAME"

echo "🐣 Spawning agent '$TASK_NAME'..."

# 1. Create Worktree
if [ -d "$WORKTREE_DIR" ]; then
    echo "Worktree already exists. Cleaning up..."
    rm -rf "$WORKTREE_DIR"
    git worktree prune
fi

git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" origin/main
if [ $? -ne 0 ]; then
    echo "Failed to create worktree."
    exit 1
fi

# 2. Prepare Environment
cd "$WORKTREE_DIR" || exit
echo "📦 Installing dependencies..."
# Detect package manager
if [ -f "pnpm-lock.yaml" ]; then
    pnpm install
elif [ -f "yarn.lock" ]; then
    yarn install
elif [ -f "package-lock.json" ]; then
    npm install
fi

# 3. Write Task Context
echo "# Task: $TASK_NAME" > TASK.md
echo "" >> TASK.md
echo "$PROMPT" >> TASK.md
echo "" >> TASK.md
echo "## Instructions" >> TASK.md
echo "1. Understand the codebase in this worktree." >> TASK.md
echo "2. Implement the feature." >> TASK.md
echo "3. Verify with tests." >> TASK.md
echo "4. Create a PR." >> TASK.md

# 4. Launch Agent (Instructions for Orchestrator)
echo "✅ Agent Environment Ready at: $WORKTREE_DIR"
echo ""
echo "Now, use 'sessions_spawn' with this task:"
echo "----------------------------------------"
echo "cd $WORKTREE_DIR && cat TASK.md && <start coding>"
echo "----------------------------------------"

# Note: Ideally, this script would call sessions_spawn automatically via API,
# but for now, it prepares the environment for the orchestrator to launch.
