---
name: wrapup
description: Generic end-of-conversation sweep -- works in any project, at any point. Looks at what the current repo actually has (docs, planning files, agent context, changelog, ADRs, memory layers...) and proposes which of them to extend with the learnings, decisions, and follow-ups that surfaced in the conversation. Then prepares a paste-ready resume prompt for after /compact. Use when the user says "wrapup", "wrap up", "wrap things up", "lass uns wrappen", or before /compact.
metadata:
  category: session-lifecycle
---

# wrapup

Project-agnostic end-of-conversation sweep. It does not assume any particular doc layout: it inspects the repo you are currently in, finds the right places to write things down, **proposes** the updates, and only writes after the user confirms.

## When to use

- The user says "wrapup", "wrap up", "wrap things up", "lass uns wrappen".
- Right before `/compact`, to land volatile session context in durable docs first.
- Natural end of a feature / spike / debug session that produced learnings, decisions, follow-ups, or surprises that are not yet written down anywhere.

`wrapup` is generic and minimal -- not a substitute for project-specific ceremonies:
- `ytstack:summarize-task` -- per-task closure inside a ytstack slice.
- `ytstack:handoff-session` -- explicit cross-session handoff with structured HANDOFF.md.
- Project-local rituals (release notes, sprint reviews, etc.) -- defer to them when they exist.

If a more specific ceremony fits better, point the user there and stop.

## How it works

1. **Identify what the conversation produced.**
   - Features / requirements / scope changes
   - Decisions (architectural, scoping, naming) -- including the rationale
   - Gotchas, surprises, "next time, do X" learnings
   - Open follow-ups and known risks
   - Anything that the next session would need but is not in the code or git history yet

2. **Look at where you actually are.** Before suggesting any write, check the repo. Use `ls`, `git ls-files`, and quick reads to detect what doc surfaces this project has. Examples (only suggest the ones that actually exist or are clearly conventional for this stack):
   - `README.md`, `CHANGELOG.md`, `ROADMAP.md`
   - `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/`
   - `.ytstack/STATE.md`, `.ytstack/DECISIONS.md`, `.ytstack/KNOWLEDGE.md`, `M###-*` files
   - `docs/`, `docs/adr/`, `docs/plans/`, `plans/`, `specs/`, `RFCs/`
   - PARA-style memory (`para/`, `01-projects/`, knowledge-graph YAML) -- via the `para-memory-files` skill if installed
   - Personal Claude memory dirs (`~/.claude/projects/<encoded>/memory/MEMORY.md` and its leaf files)
   - LLM-wiki vault (via the `use-llm-wiki` skill) -- only if the learning is genuinely vault-worthy
   - Project-specific spots the conversation already touched (test plans, runbooks, dashboards)

3. **Propose, don't auto-write.** Show the user a short plan:

   ```
   Wrapup plan:
   - Memorize:
     - <bullet>
     - <bullet>
   - Suggested updates (confirm before I write):
     - <file>: <one-line what to add or change>
     - <file>: <one-line what to add or change>
   - Skip / unsure (flag for user):
     - <thing>: <why uncertain>
   - Resume prompt I will prepare for after /compact:
     - "<draft prompt>"
   ```

   Wait for the user's go-ahead (or edits) before writing. If they say "mach", do all of them; if they pick a subset, do only that subset.

4. **Write the confirmed updates.** Append / extend; do not silently drop existing content. If a section looks stale, flag it -- do not delete it without confirmation.

5. **Prepare the resume prompt.** A short, paste-ready block the user can drop at the start of the next session. It should:
   - Name the goal / current focus in one sentence
   - List the files just updated so the next agent reads them first
   - Mention the immediate next step

6. **Final report.** Terse:

   ```
   Memorized:
   - <bullet>

   Updated:
   - <file>: <what changed>
   - <file>: <what changed>

   Resume prompt:
   "<paste-ready>"
   ```

## Discipline

- **Generic by default.** Do not hard-assume any particular project's layout. Inspect first, suggest second, write last.
- **Propose before writing.** This is the most important rule -- a wrap-up that silently rewrites files is worse than no wrap-up.
- **Do not invent docs.** Only write to files that exist, or that the user explicitly authorizes you to create.
- **Do not erase content.** Append / extend / amend. Flag suspected stale content; let the user decide.
- **Repo scope only.** Do not edit other repos, the user's global config, or external systems. Cross-project work needs an explicit user instruction (see global Regel #2).
- **No false "done".** "Wrapped up" is a done-claim -- do not say it without actually having written the updates and re-read them. If you only proposed and the user has not confirmed yet, say "proposed", not "done".
- **Stay terse.** The point is that the next session is informed, not that the wrap-up report is long.
