# Leak patterns

Canonical regex list for `audit-skills`. Extend here, not in the skill body.

Each entry: pattern + category + rationale + typical fix.

## Personal info

| Pattern | Category | Why | Typical fix |
| --- | --- | --- | --- |
| `/Users/[a-z]+/` | LEAK | macOS path with username | `/Users/<you>/` or strip path |
| `/home/[a-z]+/` | LEAK | Linux path with username | `/home/<you>/` or strip path |
| `C:\\Users\\[A-Za-z]+\\` | LEAK | Windows path with username | `%USERPROFILE%\\` |
| `\b(alex|alex-claude)\b` | LEAK | personal handle | drop or replace with `<user>` |
| `kcma-d8|nas1` | LEAK | personal hostnames | drop or document as user-supplied |
| `\b(192\.168|10\.0|172\.(1[6-9]|2[0-9]|3[0-1]))\.` | LEAK | RFC1918 private IP | drop or `<lan-ip>` |
| `\.local\b|\.lan\b` | JARGON | mDNS / LAN suffix | reword to `<your-host>` |
| `sk-[A-Za-z0-9]{20,}` | LEAK | OpenAI / Anthropic key shape | revoke + remove |
| `ghp_[A-Za-z0-9]{20,}` | LEAK | GitHub PAT | revoke + remove |
| `xox[baprs]-[A-Za-z0-9-]{10,}` | LEAK | Slack token | revoke + remove |
| `AKIA[0-9A-Z]{16}` | LEAK | AWS access key | revoke + remove |

## Yesterday-internal

| Pattern | Category | Why | Typical fix |
| --- | --- | --- | --- |
| `\b\w*-internal\b` | LEAK | repo name suffix used by Yesterday for private repos | rewrite without the internal repo, point to public alternative |
| `yopstack-internal|yastack-internal|ydstack-internal|ystacks-internal` | LEAK | known internal stacks | drop or rewrite |
| `\.yesterday\.internal\b|\.ys\.internal\b` | LEAK | internal infra hostnames | drop or `<internal-host>` |
| `\btemp-home\b` | JARGON | refactoring shorthand | drop sentence |
| `promoted from .*-internal` | JARGON | refactor history that names an internal repo | drop sentence |
| `vendored from temp-home` | JARGON | refactor history | drop sentence |
| `moved out of .*-internal` | JARGON | refactor history | drop sentence |
| `marketplace["']?: ["']?[a-z-]*-internal` | LEAK | dep on internal marketplace from a public plugin | drop dep or move plugin out of public catalog |

## Process / TODOs

| Pattern | Category | Why | Typical fix |
| --- | --- | --- | --- |
| `\bTODO\(` | JARGON | author tag in a TODO | drop name, keep TODO |
| `\bFIXME\b|\bXXX:` | JARGON | dev placeholders surfacing in docs | resolve or remove |
| `(Linear|Jira|Asana)[- ]?[A-Z]{2,5}-\d+` | JARGON | private ticket reference | drop the ticket id |
