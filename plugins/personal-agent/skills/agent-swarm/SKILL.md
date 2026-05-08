---
name: agent-swarm
description: Orchestrate specialized coding agents in isolated worktrees for parallel development tasks.
metadata:
  category: platform
---

# Agent Swarm Orchestration 🐝

> **Orchestrate specialized coding agents in isolated worktrees.**
> Based on [Elvis Sun's architecture](https://x.com/elvissun/status/2025920521871716562).

## Concept

- **Orchestrator (You):** Holds business context, decisions, memory. Spawns agents.
- **Workers (Agents):** Hold codebase context only. Run in isolated `git worktrees`.
- **Loop:** Monitoring script checks PRs, CI, and agent health.

## Usage

### 1. Spawn an Agent

```bash
# Creates a worktree and prepares the task context
./skills/agent-swarm/scripts/spawn-agent.sh <task-name> <branch-name> "<prompt>"
```

### 2. Monitor Progress

```bash
# Checks all active agents and reports status
./skills/agent-swarm/scripts/monitor-agents.sh
```

## Structure

Each agent gets:
1. **Isolated Git Worktree:** `../worktrees/<feature-branch>`
2. **Task Context:** A dedicated prompt file.
3. **Session:** A tracked session (TMux or OpenClaw Sub-Agent).

## Rules 🛡️

1. **CONTEXT_SEPARATION:** Orchestrator knows *why* (Business). Worker knows *how* (Code). Do not overload workers with business docs.
2. **DEFINITION_OF_DONE:** PR created + CI passed + Self-Review done.
3. **FAIL_FAST:** If an agent is stuck, kill it and respawn with better context (don't loop).

---

*Adapted for OpenClaw by ManniTheRaccoon.* 🦝
