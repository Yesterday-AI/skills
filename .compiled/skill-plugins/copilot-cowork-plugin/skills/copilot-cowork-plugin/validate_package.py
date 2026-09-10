#!/usr/bin/env python3
"""Validiert ein Copilot-Cowork-Plugin-Paket (.zip) vor dem Upload.

Prueft die dokumentierten ASKILL-Regeln plus die empirisch ermittelte
Endungs-Allowlist (siehe REFERENCE.md).

    python3 validate_package.py mein-paket.zip
"""
import json
import posixpath
import re
import sys
import zipfile

ALLOWED_ROOT = {  # v1.28 setzt additionalProperties:false -> alles andere fliegt raus
    "$schema", "manifestVersion", "version", "id", "developer", "name",
    "description", "icons", "accentColor", "agentSkills", "agentConnectors",
}
RESERVED = {"CON", "AUX", "PRN", "NUL", *[f"COM{i}" for i in range(1, 10)],
            *[f"LPT{i}" for i in range(1, 10)]}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9 ._!-]+$")
# Cowork veroeffentlicht keine Allowlist. Empirisch belegt (Upload-Fehler
# 'InvalidAgentSkill: File extension X is not supported'):
BLOCKED_EXT = {".svg", ".css"}
# durch erfolgreiche Uploads belegt (.md/.html 2026-08-10; übrige 2026-08-23 ext-test)
SAFE_EXT = {".md", ".html", ".png", ".jpg", ".py", ".json", ".yaml", ".txt", ".csv", ".sh"}

errors, warnings, checks = [], [], []


def check(ok, code, msg):
    (checks if ok else errors).append(f"{'PASS' if ok else 'FAIL'}  {code}  {msg}")


def main(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()

    # --- Paketwurzel: keine Wrapper-Ordner, keine macOS-Metadaten ---
    check("manifest.json" in names, "ROOT-01",
          "manifest.json liegt auf Paket-Wurzelebene (kein umschliessender Ordner)")
    junk = [n for n in names if n.startswith("__MACOSX") or n.endswith(".DS_Store")]
    check(not junk, "ROOT-02", f"keine macOS-Metadaten im ZIP {junk if junk else ''}")

    if "manifest.json" not in names:
        wrapped = [n for n in names if n.endswith("/manifest.json")]
        errors.append("ABBRUCH: ohne manifest.json auf Wurzelebene lehnt Cowork das Paket ab "
                      "('Dies sieht nicht wie ein unterstuetztes Plug-In aus')."
                      + (f" Gefunden in Unterordner: {wrapped[0]} -> ZIP ohne umschliessenden "
                         "Ordner neu packen." if wrapped else
                         " Das ist ein reiner Skill-Ordner, kein Plugin-Paket."))
        print("\n".join(sorted(set(checks))))
        print(f"\n{'='*60}\n{len(set(checks))} Checks bestanden, {len(errors)} Fehler")
        print("\n".join(errors))
        return 1

    m = json.loads(z.read("manifest.json"))

    # --- Manifest-Ebene ---
    extra = set(m) - ALLOWED_ROOT
    check(not extra, "MANIFEST-01",
          f"keine unerlaubten Root-Felder (additionalProperties:false) {extra if extra else ''}")
    check(m.get("manifestVersion") == "1.28", "MANIFEST-02", "manifestVersion == 1.28")
    check(bool(re.fullmatch(r"[0-9a-f-]{36}", str(m.get("id", "")))), "MANIFEST-03", "id ist eine GUID")
    for f in ("name", "websiteUrl", "privacyUrl", "termsOfUseUrl"):
        check(f in m.get("developer", {}), "MANIFEST-04", f"developer.{f} gesetzt")
    check(len(m.get("name", {}).get("short", "")) <= 30, "MANIFEST-05", "name.short <= 30 Zeichen")
    check(len(m.get("description", {}).get("short", "")) <= 80, "MANIFEST-06",
          "description.short <= 80 Zeichen")

    # --- Icons ---
    for key, want in (("color", "color.png"), ("outline", "outline.png")):
        ref = m.get("icons", {}).get(key)
        check(ref in names, "ICON-01", f"icons.{key} -> '{ref}' liegt im ZIP")

    # --- agentSkills ---
    skills = m.get("agentSkills", [])
    check(len(skills) <= 20, "ASKILL-M002", f"agentSkills <= 20 Eintraege (ist: {len(skills)})")
    folders = [s.get("folder") for s in skills]
    check(all(folders), "ASKILL-M001", "jeder agentSkills-Eintrag hat 'folder'")
    check(all(len(f) <= 256 for f in folders if f), "ASKILL-M003", "folder-Pfad <= 256 Zeichen")
    check(len(folders) == len(set(folders)), "ASKILL-P008", "keine doppelten folder-Werte")

    for folder in filter(None, folders):
        rel = folder.lstrip("./").rstrip("/")
        skill_md = f"{rel}/SKILL.md"
        check(any(n.startswith(rel + "/") for n in names), "ASKILL-P001",
              f"'{folder}' existiert im ZIP")
        if skill_md not in names:
            check(False, "ASKILL-P002", f"{skill_md} fehlt")
            continue
        check(True, "ASKILL-P002", f"{skill_md} vorhanden")

        body = z.read(skill_md).decode("utf-8")
        fm = re.match(r"^---\n(.*?)\n---\n", body, re.S)
        check(bool(fm), "ASKILL-P003", "SKILL.md hat YAML-Frontmatter zwischen ---")
        if not fm:
            continue
        raw = fm.group(1)
        name = re.search(r"^name:\s*(.+)$", raw, re.M)
        desc = re.search(r"^description:\s*(.+)$", raw, re.M | re.S)
        check(bool(name), "ASKILL-P004", "Frontmatter enthaelt 'name'")
        check(bool(desc), "ASKILL-P005", "Frontmatter enthaelt 'description'")
        if name:
            n = name.group(1).strip().strip("\"'")
            check(n == rel.split("/")[-1], "ASKILL-P006",
                  f"name '{n}' == Ordnername '{rel.split('/')[-1]}'")
            check(bool(KEBAB.fullmatch(n)) and 1 <= len(n) <= 64, "ASKILL-P007",
                  f"name '{n}' ist kebab-case, 1-64 Zeichen")

        # --- Companion-Dateien ---
        comps = [n for n in names if n.startswith(rel + "/")
                 and not n.endswith("/") and n != skill_md]
        total = sum(z.getinfo(n).file_size for n in comps)
        check(len(comps) <= 20, "COMP-01", f"<= 20 Companion-Dateien (ist: {len(comps)})")
        check(all(z.getinfo(n).file_size <= 5 * 1024**2 for n in comps), "COMP-02",
              "jede Companion-Datei <= 5 MB")
        check(total <= 10 * 1024**2, "COMP-03",
              f"Companions gesamt <= 10 MB (ist: {total/1024:.0f} KB)")
        for n in comps:
            base = n.split("/")[-1]
            check(not base.startswith("."), "COMP-04", f"keine versteckte Datei: {base}")
            check(".." not in n.split("/"), "COMP-05", f"kein Path-Traversal: {n}")
            check("\\" not in n and "\x00" not in n, "COMP-06", f"keine Backslashes/NUL: {n}")
            check(base.split(".")[0].upper() not in RESERVED, "COMP-07",
                  f"kein reservierter Windows-Name: {base}")
            check(bool(SAFE_NAME.fullmatch(base)), "COMP-08", f"sichere Zeichen im Namen: {base}")
            ext = ("." + base.rsplit(".", 1)[-1].lower()) if "." in base else ""
            if ext in BLOCKED_EXT:
                check(False, "COMP-09",
                      f"Endung '{ext}' wird von M365 Copilot abgelehnt: {base}")
            elif ext not in SAFE_EXT:
                warnings.append(f"WARN  COMP-09  Endung '{ext}' ({base}) ist nicht als "
                                "unterstuetzt belegt - Cowork hat keine oeffentliche "
                                "Allowlist. Sicher ist nur .md")
            else:
                check(True, "COMP-09", f"Endung '{ext}' ist belegt unterstuetzt: {base}")

        # --- Interne Verweise in SKILL.md muessen auf existierende Dateien zeigen ---
        for link in re.findall(r"\]\(([^)#:]+?)\)", body):
            if link.startswith(("http", "/")):
                continue
            target = posixpath.normpath(f"{rel}/{link}")
            check(target in names, "LINK-01",
                  f"SKILL.md verweist auf vorhandene Datei: {link}")

    # --- agentConnectors (optional) ---
    for c in m.get("agentConnectors", []):
        check(bool(c.get("id")) and bool(c.get("displayName")), "CONN-01",
              "Connector hat id + displayName")
        src = c.get("toolSource", {})
        check(len([k for k in ("plugin", "remoteMcpServer") if k in src]) == 1, "CONN-02",
              "genau eines von plugin | remoteMcpServer")
        rms = src.get("remoteMcpServer")
        if rms:
            check(str(rms.get("mcpServerUrl", "")).startswith("https://"), "CONN-03",
                  "mcpServerUrl ist HTTPS")
            f = rms.get("mcpToolDescription", {}).get("file")
            check(bool(f), "CONN-04", "mcpToolDescription.file gesetzt")
            if f:
                check(f.lstrip("./") in names, "CONN-05", f"Tool-Description '{f}' liegt im ZIP")

    print("\n".join(sorted(set(checks))))
    if warnings:
        print("\n".join(warnings))
    print(f"\n{'='*60}\n{len(set(checks))} Checks bestanden, {len(errors)} Fehler")
    if errors:
        print("\n".join(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
