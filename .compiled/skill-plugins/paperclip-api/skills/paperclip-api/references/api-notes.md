# Paperclip API — Praktische Erkenntnisse

Gesammelt beim Erkunden der Acme-Instanz auf Railway. Ergänzt die offizielle Doku mit dem was tatsächlich funktioniert.

## Auth

Paperclip unterstützt **drei** Auth-Pfade ([canonical docs](https://docs.paperclip.ing/reference/api/authentication.md)):

1. **Board API Key (bearer)** — `pcp_board_*` Tokens, geminted via `paperclipai auth login`. Empfohlen für Scripts.
2. **Session Cookie (BetterAuth)** — Browser-UI und `paperclipai`-loses Skripten in trusted-mode.
3. **Agent API Key / Run JWT** — für agent-side Calls.

**Korrektur einer früheren Annahme:** Der Token-String aus der Sign-in-Response ist **nicht** ein Board API Key. Er funktioniert nur als Cookie, nicht als Bearer. Das hatte den Eindruck erweckt, Bearer-Auth funktioniere generell nicht — tut es aber, sobald man einen echten `pcp_board_*` Token via CLI-Auth-Flow erzeugt:

```bash
paperclipai auth login           # device-code flow → mintet pcp_board_* Token
export PAPERCLIP_API_TOKEN="pcp_board_..."

curl -H "Authorization: Bearer $PAPERCLIP_API_TOKEN" \
  -H "Origin: $PAPERCLIP_URL" \
  -X PATCH "$PAPERCLIP_URL/api/companies/$COMPANY_ID" -d '{"name":"..."}'
```

### Cookie-Sign-in: 429 Rate-Limit

Live-Erfahrung 2026-05-05: Wrapper-Skript signt fresh per CLI-Call, ein Burst von ~10 Calls (parallel routine list / issue list / approvals / dashboard / cost) trifft `HTTP 429 sign-in failed` auf `/api/auth/sign-in/email`. Lösung: bearer-Token nutzen oder Cookie einmalig holen und manuell wiederverwenden.

```bash
# Sign in — gibt Session-Cookie zurück (nur als Fallback)
curl -X POST "$PAPERCLIP_URL/api/auth/sign-in/email" \
  -H "Content-Type: application/json" \
  -c /tmp/cookies.txt \
  -d '{"email":"...","password":"..."}'
```

## CSRF-Schutz: Origin Header Pflicht

Für alle **mutativen Requests** (POST, PATCH, DELETE) muss der `Origin` Header auf die eigene Instanz-URL gesetzt werden:

```bash
curl -X PATCH "$PAPERCLIP_URL/api/companies/$COMPANY_ID" \
  -b /tmp/cookies.txt \
  -H "Content-Type: application/json" \
  -H "Origin: $PAPERCLIP_URL" \   # ← PFLICHT für alle Mutations
  -d '{"name":"New Name"}'
```

Ohne Origin: `{"error":"Board mutation requires trusted browser origin"}`

## Was funktioniert

### Lesen (GET) — ohne Origin Header
```
GET /api/health                       → Version, auth status, bootstrap status
GET /api/companies                    → Alle Companies
GET /api/companies/:id                → Company Details
GET /api/companies/:id/agents         → Agents der Company
GET /api/agents/:id                   → Agent Details inkl. adapterConfig, runtimeConfig
GET /api/agents/:id/skills            → Skills des Agents (managed + external)
GET /api/companies/:id/skills         → Company Skill Catalog
GET /api/companies/:id/goals          → Goals
GET /api/companies/:id/issues         → Issues
GET /api/companies/:id/approvals      → Approvals
GET /api/companies/:id/secrets        → Secret-Metadaten (kein Wert, encrypted)
```

### Schreiben (POST/PATCH) — mit Origin Header
```
PATCH /api/companies/:id              → Company umbenennen/beschreiben
PATCH /api/goals/:id                  → Goal updaten
PATCH /api/issues/:id                 → Issue updaten (status, title, comment)
POST  /api/companies/:id/skills/import → Skills von GitHub/skills.sh importieren
POST  /api/agents/:id/skills/sync     → Skills dem Agent zuweisen
POST  /api/companies/:id/secrets      → Secret anlegen
```

## Skills — Wie es wirklich funktioniert

Skills haben eine **zweistufige Struktur**: Company Catalog → Agent Assignment.

### 1. Skill in Company-Catalog importieren

```bash
curl -X POST "$PAPERCLIP_URL/api/companies/$COMPANY_ID/skills/import" \
  -b /tmp/cookies.txt \
  -H "Content-Type: application/json" \
  -H "Origin: $PAPERCLIP_URL" \
  -d '{"source":"https://github.com/paperclipai/companies/tree/main/gstack"}'
```

- Importiert **alle Skills** aus einem GitHub-Ordner auf einmal
- Gibt Array von importierten Skills zurück
- Unterstützt: `skills.sh` URLs, GitHub URLs, GitHub-Kurzform (`org/repo/path`)
- **Private Repos**: schlagen fehl (404) — nur public GitHub Repos funktionieren ohne Token

### 2. Skills dem Agent zuweisen

```bash
curl -X POST "$PAPERCLIP_URL/api/agents/$AGENT_ID/skills/sync" \
  -b /tmp/cookies.txt \
  -H "Content-Type: application/json" \
  -H "Origin: $PAPERCLIP_URL" \
  -d '{"desiredSkills":["paperclipai/companies/review","paperclipai/companies/ship"]}'
```

- Keys müssen im Company-Catalog existieren
- Ungültige Keys: `{"error":"Invalid company skill selection (unknown references: ...)"}`

## Secrets

Secrets sind **Company-scoped**, nicht Agent-scoped:

```bash
# Anlegen
curl -X POST "$PAPERCLIP_URL/api/companies/$COMPANY_ID/secrets" \
  -b /tmp/cookies.txt \
  -H "Content-Type: application/json" \
  -H "Origin: $PAPERCLIP_URL" \
  -d '{"name":"ANTHROPIC_API_KEY","value":"sk-ant-..."}'

# Response: {id, name, provider: "local_encrypted", latestVersion: 1}
```

In `adapterConfig` referenzieren:
```json
{
  "adapterConfig": {
    "env": {
      "ANTHROPIC_API_KEY": {
        "type": "secret_ref",
        "secretId": "uuid-from-above",
        "version": "latest"
      }
    }
  }
}
```

**Achtung:** Kein DELETE-Endpoint via API für Secrets gefunden.

## Was NICHT funktioniert / fehlt

| Endpoint | Status | Notiz |
|---|---|---|
| `DELETE /api/secrets/:id` | ✅ | Korrekter Pfad: direkt per Secret-ID, nicht company-scoped |
| `GET/POST /api/agents/:id/secrets` | 404 | Secrets sind Company-scoped |
| `GET /api/agents/:id/instructions` | Falsch — Bundle-API nutzen | Korrekte Endpoints unter `/instructions-bundle/*` |
| `GET /api/agents/:id/runs` | 404 | Kein Agent-Level Run-Log. Workaround: `/api/issues/:id/runs` oder `/api/agents/:id/task-sessions` |
| Private GitHub Repos | 403 | Skill-Import schlägt fehl ohne Token |
| `POST /api/issues/:id/labels` | v0.3.1 version lag | In aktueller Source vorhanden |
| `PUT /api/issues/:id/documents/:key` | v0.3.1 version lag | Upsert (kein POST auf Collection) — in aktueller Source vorhanden |

## Agent Instructions

Instructions liegen als Dateien im Container, **nicht** in der DB:
```
/paperclip/instances/default/companies/{companyId}/agents/{agentId}/instructions/AGENTS.md
```

### Was via API geht — vollständige Bundle-API

```bash
# Bundle-Metadata + File-Liste lesen
GET /api/agents/:id/instructions-bundle

# Einzelne Datei lesen
GET /api/agents/:id/instructions-bundle/file?path=AGENTS.md

# Datei schreiben/updaten
curl -X PUT "$PAPERCLIP_URL/api/agents/$AGENT_ID/instructions-bundle/file" \
  -H "Origin: $PAPERCLIP_URL" \
  -d '{"path": "AGENTS.md", "content": "# My Agent\n..."}'

# Datei löschen
DELETE /api/agents/:id/instructions-bundle/file?path=AGENTS.md

# Bundle-Settings ändern (mode, entryFile)
PATCH /api/agents/:id/instructions-bundle

# Pfad ändern
PATCH /api/agents/:id/instructions-path
```

Guards: `assertCanReadAgent()` für reads, `assertCanManageInstructionsPath()` für writes (Board, Agent selbst, oder Manager in chain of command).

**Korrektur:** Meine ursprüngliche Annahme 'nicht via API erreichbar' war falsch — Endpoints existieren unter `/instructions-bundle/*`.

### Empfohlener Workflow

Instructions-Inhalt von außen steuern:
1. `adapterConfig.cwd` auf ein Git-Repo zeigen lassen
2. `AGENTS.md` im Repo pflegen (per PR-Workflow)
3. Pfad via `instructions-path` API setzen
4. Paperclip liest die Datei beim nächsten Heartbeat aus dem Repo

So kann der Instructions-Inhalt versioniert, reviewed und per PR geändert werden.

## Agent Instructions — Bundle-Struktur

Paperclip Agents sind Claude Code mit AgentSkills. Ihr Workspace hat typischerweise:

| File | Zweck | Wer braucht es |
|---|---|---|
| `AGENTS.md` | Wer bin ich, Rolle, Regeln | Alle Agents |
| `TOOLS.md` | Tool-spezifische Infos (Git-Repos, Tech Stack, etc.) | Alle Agents |
| `HEARTBEAT.md` | Was tue ich beim Timer-Wakeup | **Nur timer-basierte Agents (z.B. CEO)** |

**Wichtig:** Agents die durch Issue-Assignments geweckt werden (`wakeOnAssignment: true`) brauchen **keine** HEARTBEAT.md — sie haben immer einen konkreten Task. Nur Agents mit Cron-Schedule / Timer-Heartbeat brauchen HEARTBEAT.md als Wakeup-Plan.

## Praktische Findings aus Hands-on Session (2026-04-05)

### Routines: projectId ist Required

```bash
# FAILS — projectId fehlt
curl -X POST "$URL/api/companies/$COMPANY_ID/routines" \
  -d '{"title": "Daily Check", "assigneeAgentId": "..."}'
# → {"error":"Validation error","details":[{"path":["projectId"],"message":"Required"}]}

# WORKS
curl -X POST "$URL/api/companies/$COMPANY_ID/routines" \
  -d '{"title": "Daily Check", "assigneeAgentId": "...", "projectId": "uuid"}'
```

### Trigger Response ist in `{"trigger": {...}}` gewrappt

```json
{"trigger": {"id": "...", "cronExpression": "0 9 * * *", "nextRunAt": "2026-04-06T07:00:00.000Z"}, "secretMaterial": null}
```
`nextRunAt` wird direkt berechnet. Webhook-Triggers haben `secretMaterial` wenn `signingMode` gesetzt.

### Approval-Flow via API vollständig steuerbar

Board-Member kann Approvals per API erteilen — kein Browser-Klick nötig:

```bash
# 1. Hire (erzeugt pending_approval)
curl -X POST "$URL/api/companies/$COMPANY_ID/agent-hires" \
  -H "Origin: $URL" \
  -d '{"name":"Engineer","role":"engineer","adapterType":"claude_local","reportsTo":"$CEO_ID"}'
# Response: {"agent": {"status": "pending_approval"}, "approval": {"id": "..."}}

# 2. Board approves via API
curl -X POST "$URL/api/approvals/$APPROVAL_ID/approve" \
  -H "Origin: $URL" \
  -d '{"note": "Approved."}'
# Agent status wechselt zu: idle
```

### requireBoardApprovalForNewAgents (Company-Setting)

```bash
curl -X PATCH "$URL/api/companies/$COMPANY_ID" \
  -H "Origin: $URL" \
  -d '{"requireBoardApprovalForNewAgents": true}'
```
Danach: jeder `agent-hires` Request erzeugt `pending_approval` statt direkt zu deployen.

### Budget bei Subscription-Instanzen

`spentMonthlyCents` bleibt $0 wenn Agents über eine Claude/Anthropic Subscription laufen (nicht eigene API Keys). Budget-Enforcement (`budgetMonthlyCents`) greift nur mit eigenen Keys (z.B. via LLM Gateway).

## Deployment-Details (Railway)

- Instanz läuft auf Railway
- `claude_local` Adapter läuft direkt im Railway Container
- Skills werden als ephemeral in `~/.claude/skills` gemountet beim Heartbeat
- External/user-installed Skills in `/paperclip/.claude/skills/` sind `readOnly: true` via API

## Workflow für neuen Agent mit Skills + Secrets

```bash
# 1. Secret anlegen
SECRET_ID=$(curl -sf -X POST "$PAPERCLIP_URL/api/companies/$COMPANY_ID/secrets" \
  -b /tmp/cookies.txt -H "Content-Type: application/json" -H "Origin: $PAPERCLIP_URL" \
  -d '{"name":"ANTHROPIC_API_KEY","value":"sk-ant-..."}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 2. Skill importieren
curl -X POST "$PAPERCLIP_URL/api/companies/$COMPANY_ID/skills/import" \
  -b /tmp/cookies.txt -H "Content-Type: application/json" -H "Origin: $PAPERCLIP_URL" \
  -d '{"source":"https://github.com/org/repo/tree/main/skills/my-skill"}'

# 3. Agent anlegen mit Secret + Skill
curl -X POST "$PAPERCLIP_URL/api/companies/$COMPANY_ID/agent-hires" \
  -b /tmp/cookies.txt -H "Content-Type: application/json" -H "Origin: $PAPERCLIP_URL" \
  -d "{
    \"name\": \"Engineer\",
    \"role\": \"engineer\",
    \"adapterType\": \"claude_local\",
    \"adapterConfig\": {
      \"cwd\": \"/path/to/workspace\",
      \"env\": {
        \"ANTHROPIC_API_KEY\": {
          \"type\": \"secret_ref\",
          \"secretId\": \"$SECRET_ID\",
          \"version\": \"latest\"
        }
      }
    },
    \"desiredSkills\": [\"my-skill-key\"]
  }"
```
