---
name: capability-check
description: Discover available tools, sub-agents, and skills at session start or when unsure about capabilities.
metadata:
  category: platform
---

# Capability Check Skill 🔍🧰

> **Discover what you can do.**
>
> Use this skill at session start or when unsure about available tools, sub-agents, or skills.

## Usage

Run these checks to understand your current capabilities:

### 1. Available Tools
Your tools are listed in the system prompt under "Tool availability". Scan for:
- `exec` (shell commands)
- `web_search` / `web_fetch` (research)
- `browser` (browser automation)
- `sessions_spawn` / `subagents` (multi-agent orchestration)
- `cron` (scheduled tasks)
- `message` (cross-channel messaging)
- `nodes` (paired devices: cameras, screens, locations)
- `tts` (text-to-speech)

### 2. Available Skills
Check `<available_skills>` in your system prompt. Each skill has:
- **Name & Description**
- **Location** (path to `SKILL.md`)
Load with: `read <location>`

### 3. Available Sub-Agents
```
agents_list
```
Shows agent IDs you can target with `sessions_spawn`.

### 4. Active Sub-Agents
```
subagents action=list
```
Shows running sub-agent sessions.

### 5. Running Sessions
```
sessions_list
```
Shows all active sessions with optional filters.

### 6. Paired Nodes (Devices)
```
nodes action=status
```
Shows paired phones, Pis, etc.

### 7. Cron Jobs
```
cron action=list
```
Shows scheduled recurring tasks.

### 8. Current Model & Config
```
session_status
```
Shows model, usage, cost, thinking level.

## Quick Health Check

Run all of the above in sequence to get a full picture of your capabilities. Log findings to `memory/` for future reference.

## Instructions

1. **On first session:** Run the full check and log results.
2. **On task start:** Verify the tools you need are available.
3. **When stuck:** Re-check -- maybe a tool you forgot about can help.

---

*Authored by ManniTheRaccoon.* 🦝
