# Referenz — Copilot Cowork Plugin-Pakete

Quelle: [Build plugins for Copilot Cowork](https://learn.microsoft.com/de-de/microsoft-365/copilot/cowork/cowork-plugin-development)
und [Verwenden von Plug-Ins mit Copilot Cowork](https://learn.microsoft.com/de-de/microsoft-365/copilot/cowork/cowork-plugins).
Alles ohne Doku-Beleg ist unten als *empirisch* markiert.

## manifest.json (v1.28)

Das Schema setzt `additionalProperties: false` auf der Wurzel — **jedes** nicht
definierte Feld lässt den Upload scheitern (`Property 'X' has not been defined and
the schema does not allow additional properties`). Aus Teams-Manifests gewohnte Felder
wie `packageName` gehören hier nicht hinein.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.28/MicrosoftTeams.schema.json",
  "manifestVersion": "1.28",
  "version": "1.0.0",
  "id": "GUID — stabil über alle Versionen halten",
  "developer": { "name": "...", "websiteUrl": "...", "privacyUrl": "...", "termsOfUseUrl": "..." },
  "name": { "short": "≤30 Zeichen", "full": "≤100 Zeichen" },
  "description": { "short": "≤80 Zeichen", "full": "≤4000 Zeichen" },
  "icons": { "color": "color.png", "outline": "outline.png" },
  "accentColor": "#RRGGBB",
  "agentSkills": [ { "folder": "./skills/mein-skill" } ]
}
```

Erlaubte Wurzelfelder: die oben gezeigten plus `agentConnectors`. Sonst nichts.

## Validierungscodes

| Code | Regel |
|---|---|
| ASKILL-M001 | `folder` ist für jeden `agentSkills`-Eintrag Pflicht |
| ASKILL-M002 | max. 20 Skills pro Paket (Connectors: max. 10) |
| ASKILL-M003 | `folder`-Pfad ≤ 256 Zeichen |
| ASKILL-P001 | referenzierter Ordner existiert im ZIP |
| ASKILL-P002 | Ordner enthält `SKILL.md` |
| ASKILL-P003 | gültiger YAML-Frontmatter zwischen `---` |
| ASKILL-P004/5 | Frontmatter enthält `name` bzw. `description` |
| ASKILL-P006 | `name` == letztes Pfadsegment des Ordners — **häufigste Fehlerursache** |
| ASKILL-P007 | `name` ist kebab-case: keine Unterstriche, keine Großbuchstaben, keine doppelten/führenden/nachgestellten Bindestriche |
| ASKILL-P008 | keine doppelten `folder`-Werte |

Companion-Dateien (alles außer `SKILL.md`): max. 20 Stück, ≤ 5 MB je Datei, ≤ 10 MB gesamt,
nur relative Pfade, kein `..`, keine Backslashes/NUL, **keine versteckten Dateien**
(darum killt ein mitgezipptes `.DS_Store` das Paket), keine reservierten Windows-Namen
(`CON`, `AUX`, `PRN`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`), Dateinamen nur aus
alphanumerisch, Bindestrich, Unterstrich, Punkt, Leerzeichen, `!`.

## Dateiendungen (empirisch)

Nicht dokumentiert — weder in der Cowork-Doku noch in den M365-Known-Issues noch in
der SharePoint-Skills-Doku. Ermittelt über echte Uploads:

| Endung | Status | Beleg |
|---|---|---|
| `.md` | erlaubt | Doku-Beispiele; Upload 2026-08-10 |
| `.html` | erlaubt | Upload 2026-08-10 durchgelaufen |
| `.png`, `.jpg`, `.py`, `.json`, `.yaml`, `.txt`, `.csv`, `.sh` | erlaubt | Upload-Test 2026-08-23: dediziertes ext-test-Paket mit allen acht in einem Rutsch akzeptiert; PNG/JPG (echte Binärdateien) kamen inhaltlich intakt beim Agenten an, der die Begleitdatei-Liste 1:1 bestätigte |
| `.svg` | abgelehnt | `InvalidAgentSkill: File extension '.svg' is not supported` |
| `.css` | abgelehnt | `InvalidAgentSkill: File extension '.css' is not supported` |
| `.yml`, `.mjs`, `.pdf`, `.woff2` u. a. | ungeprüft | noch kein Upload-Beleg (kurioserweise `.yaml` ja, `.yml` offen) |

Vorgehen bei Unbekanntem: **step by step**. Nur das umwandeln, was die Fehlermeldung
explizit nennt, Rest drin lassen, erneut hochladen. Jede Runde erweitert die Tabelle.
Die Fehlermeldung listet alle Verstöße auf einmal — im Dialog ist sie oft abgeschnitten,
also nicht auf die sichtbaren drei Zeilen verlassen.

## Progressive Disclosure

Cowork lädt Skills in Ebenen — dieselbe Ökonomie wie in Claude Code:

| Ebene | Wann geladen | Zielgröße |
|---|---|---|
| Frontmatter (`name` + `description`) | immer, beim Start | ~100 Token |
| `SKILL.md`-Body | wenn der Skill auslöst | < 5.000 Token (1.500–2.000 Wörter) |
| `references/` | on demand durch den Agenten | unbegrenzt |
| `scripts/` | ausgeführt, nicht in den Kontext geladen | — |

Unterverzeichnisse müssen in `SKILL.md` explizit erwähnt werden, sonst weiß der Agent
nicht, dass es sie gibt.

## Connectors (MCP)

Nur nötig, wenn der Skill Live-Daten aus einem externen System braucht.

```json
"agentConnectors": [{
  "id": "eindeutig-im-manifest",
  "displayName": "Anzeigename",
  "description": "...",
  "toolSource": {
    "remoteMcpServer": {
      "mcpServerUrl": "https://...",
      "mcpToolDescription": { "file": "./tools/meine-tools.json" },
      "authorization": { "type": "OAuthPluginVault", "referenceId": "..." }
    }
  }
}]
```

- Transport: streambares HTTP über HTTPS (TLS 1.2+), JSON-RPC 2.0, `tools/list` + `tools/call`.
- `mcpToolDescription` ist **Pflicht**, und die referenzierte JSON-Datei muss im ZIP liegen —
  sonst HTTP 400 `Required properties are missing from object: mcpToolDescription`.
- Auth: `None`, `OAuthPluginVault`, `ApiKeyPluginVault`. API-Key ist in Cowork noch nicht
  nutzbar — stattdessen OAuth oder Dynamic Client Registration (dann entfällt `authorization`).
- `referenceId` ist die OAuth-Client-Registrierungs-ID aus dem Agents Toolkit; bei der
  Registrierung „Any Microsoft 365 Organization" wählen, sonst bricht es mandantenübergreifend.
- Dateien aus dem Workspace: Parameter mit `contentEncoding: base64` deklarieren. Cowork
  löst Pfade auf und übergibt Base64. Max. 8 Dateien und 150 MiB pro Aufruf, nur
  Top-Level-Parameter, höchstens ein Array-Parameter.
- Ohne `annotations` gilt ein Tool als destruktiv und fordert jedes Mal Bestätigung.
  `readOnlyHint: true` für sichere Leseoperationen setzen.

## Lokalen MCP-Server testen

`mcpServerUrl` muss HTTPS sein, also Dev-Tunnel:

```bash
devtunnel port create <tunnel> -p <port> --protocol http
```

`--protocol http` beschreibt den **lokalen** Dienst, nicht die öffentliche URL.
Mit `https` liefert jeder Request 502. Zweite 502-Falle auf macOS: Server an `::`
binden statt `0.0.0.0`, sonst löst der Tunnel `localhost` nach IPv6 auf und findet nichts.

## Offizieller Importweg für vollständige Plugins

Microsoft dokumentiert zusätzlich `atk import openplugin` im [aktuellen Entwicklungsleitfaden](https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development) (geprüft 2026-09-10). Nutze diesen Weg für vollständige Plugin-Strukturen; die lokalen Python-Helfer hier bauen einzelne Skill-Ordner. Prüfe die CLI-Hilfe auf der tatsächlich installierten Version. Der lokale Validator ersetzt nicht die Herstellerprüfung.

## Sideloading und Tenant-Veröffentlichung

```bash
npm install -g @microsoft/m365agentstoolkit-cli
atk auth login
atk install --file-path "paket.zip" --scope Personal
```

Tenant-weit: M365 Admin Center → Apps → Benutzerdefinierte App hochladen → **…** → Agent hinzufügen.
Öffentlich: Einreichung über Partner Center.

Bekannte Einschränkung: In Tenants mit aktiven Microsoft-Purview-Informationsbarrieren sind
Uploads eingebetteter Wissensdateien blockiert — betroffene Pakete lassen sich nicht veröffentlichen.
