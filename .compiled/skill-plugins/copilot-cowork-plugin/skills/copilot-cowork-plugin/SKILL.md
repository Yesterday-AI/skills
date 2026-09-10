---
name: copilot-cowork-plugin
description: >-
  Verpackt einen bestehenden Agent-Skill als Microsoft-365-App-Paket für Copilot
  Cowork — Manifest, Icons, Konvertierung abgelehnter Dateiformate und
  Vorab-Validierung per CLI. Für den Weg vom lokalen SKILL.md-Ordner in den
  M365-Tenant; schreibt selbst keine Skills und betrifft nicht Anthropics
  Claude Cowork.
metadata:
  author: Yesterday
  category: knowledge-work
---

# Copilot Cowork Plugin — Skills nach Microsoft 365 bringen

Microsoft 365 Copilot Cowork frisst keine Skill-Ordner, sondern **M365-App-Pakete**
(„MOS-Paket"). Ein Skill ist kein Plugin: Ohne `manifest.json` auf ZIP-Wurzelebene
lautet die Antwort immer *„Dies sieht nicht wie ein unterstütztes Plug-In aus."*

Die beiden CLIs in diesem Ordner erledigen Bau und Prüfung. Schreib die Schritte nie
von Hand nach — die Fallstricke stecken in den Skripten.

## Ablauf

```bash
python3 build_package.py ./mein-skill --out ./output \
  --publisher "Example Publisher" --website https://example.com \
  --privacy https://example.com/privacy --terms https://example.com/terms
python3 validate_package.py ./output/mein-skill-cowork.zip
```

Erst hochladen, wenn der Validator **0 Fehler** meldet. Warnungen sind Absicht:
sie markieren Dateiendungen, deren Zulässigkeit noch niemand nachgewiesen hat.

Nützliche Flags: `--exclude 'agents/*'` wirft nicht portierbare Teile raus,
`--convert-unknown` wandelt auch unbelegte Endungen in `.md`,
`--package-name`, `--version`, `--icon-color/-outline` überschreiben die Defaults.
Mehrere Skill-Ordner in einem Aufruf ergeben ein Paket (max. 20).

**Zu viele Companion-Dateien?** Das Limit von 20 ist die häufigste harte Grenze bei
gewachsenen Skills. `--bundle 'kit/components/*'` fasst jedes passende Verzeichnis zu
**einer** `.md` zusammen — Markdown direkt, Code als Codeblock, Verweise darauf werden
mitgezogen. Der Agent liest ein Bündel genauso gut, hat sogar alle Teile auf einmal.


Manual-only Skills werden standardmäßig gestoppt. Erst nach Prüfung ihrer Seiteneffekte darf `--allow-auto-invocation` die entsprechende Frontmatter-Einschränkung entfernen. Eine Formatkonvertierung erteilt keine neue Ausführungsbefugnis.

## Paketstruktur

```
paket.zip                 ← Inhalte auf ROOT-Ebene, kein umschließender Ordner
├── manifest.json         ← M365 Unified App Manifest v1.28
├── color.png             ← 192×192, Pflicht
├── outline.png           ← 32×32, Pflicht
└── skills/
    └── mein-skill/       ← Ordnername MUSS == name im Frontmatter (kebab-case)
        ├── SKILL.md
        └── references/
```

Details zu Manifest-Feldern, Connectors und dem Fehlerkatalog: [REFERENCE.md](REFERENCE.md).

## Die undokumentierte Endungs-Allowlist

Cowork filtert Companion-Dateien nach Endung und **veröffentlicht die Liste nirgends**.
Verstöße erscheinen erst beim Upload als `InvalidAgentSkill: File extension '.x' is not
supported`. Stand der eigenen Tests:

| Endung | Status |
|---|---|
| `.md`, `.html` | belegt erlaubt |
| `.png`, `.jpg`, `.py`, `.json`, `.yaml`, `.txt`, `.csv`, `.sh` | belegt erlaubt — Upload-Test 2026-08-23 (ext-test-Paket), Binärdateien kommen intakt an |
| `.svg`, `.css` | belegt abgelehnt |
| alles andere (z. B. `.yml`, `.mjs`, `.pdf`, `.woff2`) | ungeprüft |

`build_package.py` überführt abgelehnte Formate automatisch in eine `.md` mit
Codeblock und biegt alle internen Verweise mit um — inhaltlich verlustfrei, der
Agent liest den Codeblock genauso.

**Neue Erkenntnis? Sofort eintragen:** die Tabelle oben plus `BLOCKED_EXT`/`SAFE_EXT`
in beiden Skripten. Der Wert dieses Skills steckt in dieser Liste.

## Upload

Cowork → **+** → **Anpassen** → Reiter **Plug-Ins** → **Plug-in hinzufügen** → ZIP wählen →
Freigabe („Nur für Sie" oder benannte Personen, falls der Tenant es zulässt) → **Anwenden**.
Tenant-weit stattdessen über M365 Admin Center → Apps → Benutzerdefinierte App hochladen.

Für ein Update dieselbe GUID behalten (`build_package.py` leitet sie deterministisch ab),
nur `--version` hochzählen, dann auf der Plugin-Detailseite **Erneut freigeben**.

Für einen Pilot mit wenigen Leuten braucht es das Paket gar nicht: **Anpassen → Skills →
Add → Upload skill** frisst direkt eine `.md`, `.zip` oder `.skill`, und ein Skill-Ordner
in OneDrive unter `/Documents/Cowork/skills/<name>/SKILL.md` wird beim nächsten
Sitzungsstart automatisch gefunden (max. 50 Skills, `SKILL.md` bis 1 MB). Beides gilt
pro Person — für den Rollout an alle bleibt das ZIP über das Admin Center der Weg.

## Grenzen

- `commands/`, `agents/`, `hooks/`, `settings.json`, `bin/` werden nicht übernommen —
  nur `skills/` und MCP-Connectors überleben die Portierung.
- Keine Shell-, Screenshot- oder Browser-Automatisierung. **Ausnahme HTML:** Cowork hat
  einen eingebauten `html`-Skill („Create, edit, and validate standalone single-file
  HTML") und rendert `.html` in der Vorschau — ein visueller Feedback-Loop über
  HTML-Artefakte funktioniert dort also sehr wohl. Ob im Vorschau-Iframe auch
  JavaScript läuft, ist nicht dokumentiert; für den echten Test die Datei
  herunterladen und lokal öffnen.
- Ob mitgelieferte `scripts/` ausgeführt werden, ist ebenfalls undokumentiert. Skills
  deshalb als reine Anweisungen plus Markdown bauen, nie mit Ausführungs-Annahme.
- Companion-Limits pro Skill: 20 Dateien, 5 MB je Datei, 10 MB gesamt.
- Skills ohne Connector brauchen keinen MCP-Server — reine Prompt-Workflows sind der Normalfall.

## Abgrenzung

Dieser Skill verpackt bereits vorhandene Skills. „Cowork" heißt bei Anthropic etwas anderes: die `create-cowork-plugin`-Skills
aus dem Plugin-Marketplace zielen auf Claude Cowork und erzeugen ein anderes Format.

## Lokaler Bau und Datenschutz

Python 3.10+ ist erforderlich. Beide Skripte relativ zu diesem installierten Skill aufrufen. Der Bau läuft lokal ohne Netzwerk und ohne Upload. Publisher sowie Website-, Datenschutz- und AGB-URLs ausdrücklich für das eigene Paket angeben; example.com ist nur ein Testplatzhalter. Eigene Icons können mitgegeben werden, sonst werden einfache PNG-Platzhalter erzeugt.

Vor dem Bau den gesamten ausgewählten Ordner einschließlich Referenzen prüfen: keine Credentials, privaten Transkripte, Kundendaten oder personenbezogenen Beispiele paketieren. Symlinks werden abgelehnt. Ausschlüsse vor dem Kopieren anwenden. Das ZIP nach dem Bau erneut inhaltlich prüfen; technische Validierung ist keine Freigabe der Inhalte. Kein Upload ohne ausdrücklichen Auftrag.

Der Validator prüft eine begrenzte lokale Regelmenge. Null Fehler sind keine Garantie für Tenant-Annahme. Die Endungstabelle dokumentiert frühere Upload-Beobachtungen und ist keine vollständige aktuelle Hersteller-Allowlist.
