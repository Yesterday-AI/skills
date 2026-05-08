---
name: project-tracking
description: >
  Standardisiertes Projekt-Tracking für Yesterday KI-Agenten.
  Use when: setting up a new agent workspace, responding to a status request from
  another agent or a human team member, or aggregating fleet-wide project status.
  Covers: PROJECTS_TRACKING.md structure, YAML frontmatter, responsibility matrix,
  status definitions, and the Project Status Report format.
metadata:
  category: ops
---

# Project Tracking

Dieser Skill definiert den verbindlichen Standard für das Projekt-Tracking innerhalb der Yesterday KI-Agenten-Flotte. Ziel ist eine maschinenlesbare und menschenfreundliche Übersicht über Zuständigkeiten und Fortschritte.

## Setup

Lege im Root deines Agent-Workspaces eine Datei `PROJECTS_TRACKING.md` an.

### 1. YAML Frontmatter (Pflicht)

```yaml
---
agent_id: "NAME_DES_AGENTS"       # z.B. Yessy, Moss, Willi, Emmett, Manni
last_sync: YYYY-MM-DD
active_projects: ["Y-ID1", "Y-ID2"]
capabilities: ["skill-1", "skill-2"]
---
```

### 2. Tracking-Matrix (Pflicht)

```markdown
| ID | Projekt | Lead (Human) | Lead (Agent) | Status | Kurzbeschreibung | Source of Truth |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Y-ID** | **Name** | Wer gibt vor? | Wer führt aus? | 🟢 | Was wird getan? | Repo / Slack / etc. |
```

### 3. Status-Definitionen

| Symbol | Name | Bedeutung |
| :--- | :--- | :--- |
| 🟢 | **Active** | Läuft nach Plan. |
| 🟡 | **WIP/Blocked** | In Arbeit oder wartet auf Input/Entscheidung. |
| ⚪ | **Discovery** | Recherche/Ideenphase, noch kein aktiver Output. |
| 🟣 | **Skill-Dev** | Fokus auf Entwicklung neuer KI-Fähigkeiten. |
| 🔴 | **CRITICAL** | Höchste Priorität, sofortiges Handeln erforderlich. |
| ✅ | **Done** | Abgeschlossen (bleibt zur Dokumentation im Board). |

---

## Project Status Report Format

Wenn ein Agent nach seinem Projektstatus gefragt wird – egal ob durch einen anderen Agenten, einen Personal Assistant oder ein Human-Teammitglied –, antwortet er im folgenden Format:

```markdown
### Agent Status Report: [AGENT_ID]

**agent_id:** name
**Rolle:** Kurze Beschreibung der Hauptaufgabe im Team.
**Datum:** YYYY-MM-DD

#### Projekte

| ID | Projekt | Lead (Human) | Status | Beschreibung | Source of Truth |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Y-ID | Name | Human | 🟢 Active | Was machst du konkret? | Wo liegt der echte Status? |

#### Capabilities
- `skill-1`: Kurze Beschreibung.
- `skill-2`: Kurze Beschreibung.

#### Offene Punkte / Blockers (optional)
- [ ] Was brauche ich, um weiterzumachen?
```

---

## Integrations-Logik

- **ClawRAG:** Das File wird regelmäßig indiziert, um teamübergreifende Abfragen zu ermöglichen ("Wer macht X?").
- **Heartbeat:** Agenten prüfen dieses File in ihren Heartbeat-Zyklen, um Proaktivität zu steuern.
- **Handover:** Bei Delegierung von Tasks wird die ID und der Status im Tracking beider beteiligter Agenten aktualisiert.
- **Router:** Jeder Personal Assistant aggregiert die für seinen Human relevanten Trackings.

---

## Hinweise

- Die `PROJECTS_TRACKING.md` ist **kein** Ersatz für den echten Projektstatus in Repos oder Slack.
- Der YAML-Block und die Tabelle sind **Pflicht**. Weitere Sektionen sind optional.
- `last_sync` wird bei jeder manuellen oder automatischen Aktualisierung gesetzt.
- Die `Source of Truth`-Spalte immer befüllen – sie ist der Kern des Routing-Konzepts.
