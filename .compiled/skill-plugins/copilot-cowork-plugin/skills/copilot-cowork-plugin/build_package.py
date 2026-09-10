#!/usr/bin/env python3
"""Baut aus einem oder mehreren Agent-Skill-Ordnern ein uploadfertiges
Microsoft-365-App-Paket (.zip) fuer Copilot Cowork.

    python3 build_package.py ~/.claude/skills/my-skill --out ~/Downloads

Uebernimmt automatisch:
  - Companion-Dateien mit von Cowork abgelehnter Endung -> .md mit Codeblock,
    inklusive Umbiegen aller internen Verweise
  - manifest.json (v1.28) aus dem SKILL.md-Frontmatter
  - Icons (color.png 192x192 / outline.png 32x32), generiert falls nicht vorhanden
  - ZIP auf Wurzelebene, ohne .DS_Store / __MACOSX

Danach immer validate_package.py laufen lassen.
"""
import argparse
import atexit
import json
import re
import shutil
import struct
import zlib
import binascii
import fnmatch
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

# Cowork veroeffentlicht keine Allowlist. Stand siehe REFERENCE.md.
BLOCKED_EXT = {".svg", ".css"}     # belegt abgelehnt
# .png/.jpg/.py/.json/.yaml/.txt/.csv/.sh: Upload-Test 2026-08-23 (ext-test-Paket),
# alle acht in einem Paket akzeptiert, Binärinhalt (Bilder) intakt angekommen.
SAFE_EXT = {".md", ".html", ".png", ".jpg", ".py", ".json", ".yaml", ".txt", ".csv", ".sh"}
LANG = {".svg": "svg", ".css": "css", ".js": "js", ".json": "json",
        ".yaml": "yaml", ".yml": "yaml", ".ts": "ts", ".sh": "bash"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def die(msg):
    sys.exit(f"FEHLER: {msg}")


def frontmatter(skill_md: Path) -> dict:
    """Liest name + description aus dem YAML-Frontmatter."""
    m = re.match(r"^---\n(.*?)\n---\n", skill_md.read_text(), re.S)
    if not m:
        die(f"{skill_md} hat keinen YAML-Frontmatter zwischen ---")
    raw = m.group(1)
    try:
        import yaml
        return yaml.safe_load(raw) or {}
    except ImportError:
        out = {}
        name = re.search(r"^name:\s*(.+)$", raw, re.M)
        if name:
            out["name"] = name.group(1).strip().strip("\"'")
        desc = re.search(r"^description:\s*(>-|>|\|-|\|)?\s*\n?((?:.|\n)*?)"
                         r"(?=^\w+:|\Z)", raw, re.M)
        if desc:
            out["description"] = " ".join(desc.group(2).split())
        return out


def fence_for(text: str) -> str:
    """Codeblock-Zaun, der laenger ist als jede Backtick-Folge im Inhalt."""
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def png_bytes(size, rgb, outline=False):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(
            ">I", binascii.crc32(kind + data) & 0xffffffff)
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            edge = min(x, y, size - 1 - x, size - 1 - y)
            if outline:
                pixel = (255, 255, 255, 255 if 3 <= edge < 5 else 0)
            else:
                pixel = (*rgb, 255)
            rows.extend(pixel)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b""))


def make_icons(pkg: Path, letter: str, accent: str, given_color, given_outline):
    if bool(given_color) != bool(given_outline):
        die("Both --icon-color and --icon-outline are required together")
    if given_color:
        shutil.copyfile(given_color, pkg / "color.png")
        shutil.copyfile(given_outline, pkg / "outline.png")
        return "supplied"
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        die("--accent must be a six-digit hex color")
    rgb = tuple(int(accent[i:i + 2], 16) for i in (1, 3, 5))
    (pkg / "color.png").write_bytes(png_bytes(192, rgb))
    (pkg / "outline.png").write_bytes(png_bytes(32, rgb, outline=True))
    return "generated placeholders; replace before distribution"


def copy_payload(src, dst, excludes):
    # Validate the full selected tree before copying; never dereference companions.
    entries = []
    for f in sorted(src.rglob("*")):
        rel = f.relative_to(src)
        if any(part.startswith(".") or part in {"__pycache__", "node_modules"}
               for part in rel.parts):
            continue
        if any(fnmatch.fnmatch(part.as_posix(), pattern)
               for part in (rel, *rel.parents) for pattern in excludes):
            continue
        if f.is_symlink():
            die("Symlinks are not allowed in skill payloads")
        if f.is_file():
            entries.append((f, rel))
    for f, rel in entries:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("skills", nargs="+", help="Pfad(e) zu Skill-Ordnern mit SKILL.md")
    p.add_argument("--out", default=".", help="Zielverzeichnis fuer die .zip")
    p.add_argument("--package-name", help="Anzeigename (Default: erster Skillname)")
    p.add_argument("--publisher", required=True)
    p.add_argument("--website", required=True)
    p.add_argument("--privacy", required=True)
    p.add_argument("--terms", required=True)
    p.add_argument("--accent", default="#FC4E14")
    p.add_argument("--version", default="1.0.0")
    p.add_argument("--app-id", help="GUID erzwingen (Default: uuid5, stabil)")
    p.add_argument("--icon-color"), p.add_argument("--icon-outline")
    p.add_argument("--exclude", action="append", default=[],
                   help="Glob relativ zum Skill-Ordner, mehrfach nutzbar "
                        "(z.B. --exclude 'agents/*')")
    p.add_argument("--convert-unknown", action="store_true",
                   help="Auch Endungen ohne Erlaubnis-Beleg in .md wandeln "
                        "(Default: nur warnen)")
    p.add_argument("--bundle", action="append", default=[],
                   help="Glob auf Verzeichnisse: jedes wird zu EINER .md "
                        "zusammengefasst. Gegen das 20-Companion-Limit, "
                        "z.B. --bundle 'kit/components/*'")
    p.add_argument("--allow-auto-invocation", action="store_true",
                   help="Explicitly permit converting manual-only skills to automatic invocation")
    a = p.parse_args()
    for url in (a.website, a.privacy, a.terms):
        if not url.startswith("https://"):
            die("Publisher URLs must use HTTPS")
    blocked = BLOCKED_EXT.copy()

    sources = [Path(s).expanduser().resolve() for s in a.skills]
    if len(sources) > 20:
        die("Maximal 20 Skills pro Paket (ASKILL-M002).")

    stage = Path(tempfile.mkdtemp()) / "pkg"
    atexit.register(shutil.rmtree, stage.parent, ignore_errors=True)
    (stage / "skills").mkdir(parents=True)
    entries, log = [], []

    for src in sources:
        if not (src / "SKILL.md").exists():
            die(f"{src} enthaelt keine SKILL.md")
        if (src / "SKILL.md").is_symlink():
            die("SKILL.md must be a regular file")
        if any(entry["folder"] == f"./skills/{src.name}" for entry in entries):
            die("Duplicate skill names are not allowed")
        fm = frontmatter(src / "SKILL.md")
        name = fm.get("name", src.name)
        if name != src.name:
            die(f"ASKILL-P006: name '{name}' != Ordnername '{src.name}'")
        if not KEBAB.fullmatch(name):
            die(f"ASKILL-P007: '{name}' ist nicht kebab-case")

        dst = stage / "skills" / name
        if (src / "SKILL.md").is_symlink():
            die("SKILL.md must be a regular file")
        copy_payload(src, dst, a.exclude)
        if not (dst / "SKILL.md").is_file():
            die("SKILL.md must not be excluded")

        # Cowork aktiviert Skills ausschliesslich automatisch - ein Skill mit
        # disable-model-invocation wuerde dort nie ausloesen (stiller Fehler).
        md = dst / "SKILL.md"
        text = md.read_text()
        cleaned = re.sub(r"^disable-model-invocation:.*\n", "", text, flags=re.M)
        if cleaned != text:
            if not a.allow_auto_invocation:
                die("Manual-only skill: review side effects before using --allow-auto-invocation")
            md.write_text(cleaned)
            print(f"  entfernt: disable-model-invocation (Cowork kennt kein "
                  f"manuelles Aufrufen - Skill wuerde sonst nie ausloesen)")

        # Verzeichnisse zu je einer .md buendeln (gegen das 20-Dateien-Limit)
        bundled = {}
        for pattern in a.bundle:
            for d in sorted(dst.glob(pattern)):
                if not d.is_dir():
                    continue
                parts = []
                for f in sorted(d.rglob("*")):
                    if not f.is_file() or f.name.startswith("."):
                        continue
                    text, sub = f.read_text(), f.relative_to(d)
                    if f.suffix.lower() == ".md":  # Markdown direkt, Ebene tiefer
                        parts.append(f"## {sub}\n\n"
                                     + re.sub(r"^(#+ )", r"#\1", text, flags=re.M).strip())
                    else:
                        fence = fence_for(text)
                        parts.append(f"## {sub}\n\n{fence}{LANG.get(f.suffix.lower(), '')}"
                                     f"\n{text.rstrip()}\n{fence}")
                rel = d.relative_to(dst)
                out = d.with_suffix(".md")
                out.write_text(f"# {d.name}\n\nGebuendelte Komponente, im Original "
                               f"`{rel}/` mit {len(parts)} Dateien. Alle Teile stehen "
                               f"unten in einer Datei, weil Copilot Cowork pro Skill nur "
                               f"20 Begleitdateien erlaubt.\n\n" + "\n\n".join(parts) + "\n")
                bundled[str(rel)] = str(out.relative_to(dst))
                shutil.rmtree(d)

        # Verweise auf gebuendelte Verzeichnisse umbiegen
        if bundled:
            for f in dst.rglob("*"):
                if not (f.is_file() and f.suffix in (".md", ".html", ".txt")):
                    continue
                text = t0 = f.read_text()
                for old, new in bundled.items():
                    variants = {old, "./" + old}
                    segs = old.split("/")
                    variants |= {"/".join(segs[i:]) for i in range(1, len(segs))
                                 if len(segs) - i > 1}
                    for v in sorted(variants, key=len, reverse=True):
                        target = new if v == old or v == "./" + old else \
                            "/".join(new.split("/")[-(len(v.split("/"))):])
                        text = re.sub(re.escape(v) + r"/[^\s)\]\"'`]*",
                                      target, text)
                if text != t0:
                    f.write_text(text)

        # Endungen ohne Erlaubnis-Beleg: warnen oder mitkonvertieren
        unknown = {f.suffix.lower() for f in dst.rglob("*")
                   if f.is_file() and f.name != "SKILL.md"} - SAFE_EXT - blocked
        if unknown:
            if a.convert_unknown:
                blocked |= unknown
            else:
                print(f"  WARNUNG {name}: Endungen ohne Erlaubnis-Beleg: "
                      f"{', '.join(sorted(unknown))}\n"
                      f"    Belegt erlaubt sind nur {', '.join(sorted(SAFE_EXT))}. "
                      f"Bei InvalidAgentSkill: --convert-unknown oder --exclude nutzen.")

        # Abgelehnte Formate in .md mit Codeblock ueberfuehren
        renamed = {}
        for f in sorted(dst.rglob("*")):
            if not f.is_file() or f.suffix.lower() not in blocked:
                continue
            body = f.read_text()
            fence = fence_for(body)
            new = f.with_suffix(".md")
            i = 1
            while new.exists():  # foo.svg + foo.md kollidieren
                new, i = f.with_name(f"{f.stem}-{i}.md"), i + 1
            new.write_text(
                f"# {f.stem}\n\nOriginal: `{f.name}`. Diese Endung wird von "
                f"Copilot Cowork abgelehnt, der Inhalt steht deshalb hier als "
                f"Codeblock. Inline verwenden, nicht zur Laufzeit verlinken.\n\n"
                f"{fence}{LANG.get(f.suffix.lower(), '')}\n{body.rstrip()}\n{fence}\n")
            renamed[str(f.relative_to(dst))] = str(new.relative_to(dst))
            f.unlink()

        # Interne Verweise auf die alten Pfade umbiegen
        for f in dst.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".html", ".txt"):
                text = t0 = f.read_text()
                for old, new in renamed.items():
                    text = text.replace(old, new).replace(
                        Path(old).name, Path(new).name)
                if text != t0:
                    f.write_text(text)

        comps = [f for f in dst.rglob("*") if f.is_file() and f.name != "SKILL.md"]
        total = sum(f.stat().st_size for f in comps)
        if len(comps) > 20:
            die(f"{name}: {len(comps)} Companion-Dateien, Limit ist 20")
        if total > 10 * 1024**2:
            die(f"{name}: Companions {total/1024**2:.1f} MB, Limit ist 10 MB")
        for f in comps:
            if f.stat().st_size > 5 * 1024**2:
                die(f"{f.name}: {f.stat().st_size/1024**2:.1f} MB, Limit ist 5 MB")

        entries.append({"folder": f"./skills/{name}"})
        log.append((name, fm.get("description", ""), renamed, len(comps), total))

    pkg_name = a.package_name or sources[0].name.replace("-", " ").title()
    full_desc = log[0][1] or pkg_name
    short_desc = full_desc.split(". ")[0][:80].rstrip(" ,;–-")
    guid = a.app_id or str(uuid.uuid5(
        uuid.NAMESPACE_DNS, f"{sources[0].name}.{a.website.split('//')[-1]}"))

    icon_note = make_icons(stage, pkg_name.strip()[:1].lower(), a.accent,
                           a.icon_color, a.icon_outline)

    (stage / "manifest.json").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.28/"
                   "MicrosoftTeams.schema.json",
        "manifestVersion": "1.28",
        "version": a.version,
        "id": guid,
        "developer": {"name": a.publisher, "websiteUrl": a.website,
                      "privacyUrl": a.privacy, "termsOfUseUrl": a.terms},
        "name": {"short": pkg_name[:30], "full": f"{pkg_name} for Copilot Cowork"[:100]},
        "description": {"short": short_desc, "full": full_desc[:4000]},
        "icons": {"color": "color.png", "outline": "outline.png"},
        "accentColor": a.accent,
        "agentSkills": entries,
    }, indent=2) + "\n")

    # ZIP: alles auf Wurzelebene, keine macOS-Metadaten
    out = Path(a.out).expanduser().resolve() / f"{sources[0].name}-cowork.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(stage.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                z.write(f, f.relative_to(stage))

    print(f"Paket:   {out}  ({out.stat().st_size/1024:.0f} KB)")
    print(f"GUID:    {guid}  (stabil - bei Updates NICHT aendern)")
    print(f"Version: {a.version}   Icons: {icon_note}")
    for name, _, renamed, n, total in log:
        print(f"\nSkill '{name}': {n} Companions, {total/1024:.0f} KB")
        for old, new in renamed.items():
            print(f"  umgewandelt: {old} -> {new}")
    print(f"\nJetzt pruefen:\n  python3 {Path(__file__).parent}/validate_package.py {out}")


if __name__ == "__main__":
    main()
