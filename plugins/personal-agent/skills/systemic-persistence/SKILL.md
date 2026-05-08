---
name: systemic-persistence
description: >
  Zwingt den Agenten dazu, aus gelösten Problemen nachhaltig zu lernen. Stellt sicher, dass Fixes Reboots überleben, dokumentiert sind und nicht zu neuen Problemen (wie vollen Festplatten) führen.
metadata:
  author: Moss
  version: "1.0"
  category: platform
compatibility: Any Linux/Unix system with systemd or cron.
---

# Systemic Persistence 💾🛡️

> **"Ein Fix, der einen Reboot nicht überlebt, ist kein Fix, sondern ein Workaround."**
>
> Nutze diesen Skill IMMER, nachdem du ein technisches Problem gelöst, einen Dienst gestartet oder einen Fehler behoben hast. Er zwingt dich, die Lösung nachhaltig und systemweit zu verankern.

## Usage

Wende diese Checkliste *unaufgefordert* an, sobald du ein Problem für den User erfolgreich gelöst hast.

## The Persistence Checklist ✅

Gehe diese Punkte systematisch durch. Wenn einer fehlt, setze ihn um oder informiere den User.

### 1. REBOOT_SURVIVAL 🔄
- **Definition:** Überlebt der Fix einen Systemneustart?
- **Rule:** Manuell gestartete Hintergrundprozesse (z.B. Webserver, Skripte) MÜSSEN als `systemd`-Service (User oder System) oder `@reboot` Cronjob eingerichtet werden.
- **Why:** Ein Stromausfall darf nicht dazu führen, dass der User den gleichen Fehler erneut melden muss.
- **Action:** Schreibe eine `.service`-Datei, führe `systemctl daemon-reload` und `systemctl enable --now` aus.

### 2. LOG_ROTATION 📜
- **Definition:** Produziert die Lösung kontinuierlich Logs oder Datenmüll?
- **Rule:** Kein Dienst darf endlos in eine Datei schreiben, ohne dass ein Rotations-Mechanismus existiert.
- **Why:** Eine vollgeschriebene Festplatte (100% Auslastung) in 3 Monaten ist schlimmer als das ursprüngliche Problem.
- **Action:** Richte `logrotate` ein oder konfiguriere den Dienst so, dass er alte Logs nach X Tagen löscht/überschreibt.

### 3. EXPLICIT_MEMORY 🧠
- **Definition:** Ist die Lösung für die Zukunft dokumentiert?
- **Rule:** Jede signifikante Architektur-Entscheidung, jeder Workaround und jeder gefixte Bug MUSS in der Datei `MEMORY.md` oder der projektspezifischen Dokumentation festgehalten werden.
- **Why:** Wenn ein anderer Agent (oder du selbst nach einem Reset) den Code sieht, muss der Kontext klar sein.
- **Action:** Hänge einen Eintrag unter "Lessons Learned" oder "Architektur" in der `MEMORY.md` an.

### 4. SCRIPTED_REPRODUCTION 🛠️
- **Definition:** Wenn das Problem auf einem anderen Rechner auftritt, lässt es sich mit einem Befehl lösen?
- **Rule:** Komplexe Kommandozeilen-Hacks (z.B. Rechte vergeben, Pakete installieren, Configs patchen) sollten in ein kurzes Bash-Skript (`fix_issue.sh` oder `setup.sh`) gegossen werden.
- **Why:** Automatisierung schlägt manuelles Tippen.
- **Action:** Erstelle ein Skript, mache es ausführbar (`chmod +x`) und committe es ins Projekt-Repository.

## Anti-Patterns 🚫

- **THE_FORGETFUL_DAEMON:** Einen Dienst mit `nohup ... &` starten und dem User sagen "Es läuft jetzt".
- **THE_SILENT_PATCH:** Eine Datei in `/etc/` bearbeiten, ohne den Grund dafür irgendwo zu dokumentieren.

---

*Authored by Moss (Level 99 IT-Erzmagier).* 👓