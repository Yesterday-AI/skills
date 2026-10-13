#!/usr/bin/env python3
"""Recall visible prose from recent local Codex and Claude Code transcripts."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


STOP_WORDS = {
    "aber",
    "alle",
    "and",
    "auf",
    "aus",
    "bei",
    "das",
    "dem",
    "den",
    "der",
    "die",
    "ein",
    "eine",
    "einer",
    "einem",
    "einen",
    "for",
    "from",
    "für",
    "haben",
    "hat",
    "hier",
    "ich",
    "ist",
    "mit",
    "oder",
    "the",
    "this",
    "und",
    "von",
    "was",
    "wir",
    "with",
    "wie",
    "zu",
    "zum",
    "zur",
}
INJECTED_BLOCK = re.compile(
    r"<(?P<tag>environment_context|system-reminder|user_instructions|"
    r"local-command-caveat|ide_opened_file)>.*?</(?P=tag)>",
    re.IGNORECASE | re.DOTALL,
)
TOKEN = re.compile(r"[\w-]{2,}", re.UNICODE)


@dataclass
class Message:
    role: str
    text: str
    timestamp: str | None = None


@dataclass
class Transcript:
    platform: str
    path: Path
    session_id: str | None = None
    cwd: str | None = None
    updated_at: datetime | None = None
    messages: list[Message] = field(default_factory=list)


def parse_args(argv: list[str]) -> argparse.Namespace:
    home = Path.home()
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))

    parser = argparse.ArgumentParser(
        description="Search recent Codex and Claude Code JSONL transcripts without tool payloads."
    )
    parser.add_argument("--query", required=True, help="Topic or discriminative search terms")
    parser.add_argument("--days", type=int, default=30, help="Recent file window (default: 30)")
    parser.add_argument("--limit", type=int, default=5, help="Maximum result sessions (default: 5)")
    parser.add_argument("--snippets", type=int, default=2, help="Snippets per result (default: 2)")
    parser.add_argument(
        "--platform",
        choices=("both", "codex", "claude"),
        default="both",
        help="Authorized transcript platform",
    )
    parser.add_argument("--codex-root", type=Path, default=codex_home / "sessions")
    parser.add_argument("--claude-root", type=Path, default=claude_home / "projects")
    parser.add_argument("--max-files", type=int, default=1000, help="Newest files to parse")
    parser.add_argument("--transcript", type=Path, help="Open one bounded matching transcript")
    parser.add_argument("--max-messages", type=int, default=12)
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    for name in ("days", "limit", "snippets", "max_files", "max_messages", "max_chars"):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be at least 1")
    ceilings = {
        "limit": 5,
        "snippets": 3,
        "max_files": 1000,
        "max_messages": 12,
        "max_chars": 12000,
    }
    for name, ceiling in ceilings.items():
        if getattr(args, name) > ceiling:
            parser.error(f"--{name.replace('_', '-')} must not exceed {ceiling}")
    return args


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_visible_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    value = INJECTED_BLOCK.sub(" ", value)
    return re.sub(r"\s+", " ", value).strip()


def claude_text(content: Any) -> str:
    if isinstance(content, str):
        return clean_visible_text(content)
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return clean_visible_text("\n".join(parts))


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            try:
                value = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                yield value


def parse_claude(path: Path) -> Transcript:
    transcript = Transcript(platform="claude", path=path)
    latest = None
    for entry in read_jsonl(path):
        transcript.session_id = transcript.session_id or entry.get("sessionId")
        transcript.cwd = transcript.cwd or entry.get("cwd")
        timestamp = parse_datetime(entry.get("timestamp"))
        if timestamp is not None and (latest is None or timestamp > latest):
            latest = timestamp
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = claude_text(message.get("content"))
        if text:
            transcript.messages.append(Message(role=role, text=text, timestamp=iso(timestamp)))
    transcript.updated_at = latest
    return transcript


def parse_codex(path: Path) -> Transcript:
    transcript = Transcript(platform="codex", path=path)
    visible_events: list[Message] = []
    latest = None

    for entry in read_jsonl(path):
        timestamp = parse_datetime(entry.get("timestamp"))
        if timestamp is not None and (latest is None or timestamp > latest):
            latest = timestamp
        payload = entry.get("payload")
        if not isinstance(payload, dict):
            continue
        entry_type = entry.get("type")

        if entry_type == "session_meta":
            transcript.session_id = transcript.session_id or payload.get("id")
            transcript.cwd = transcript.cwd or payload.get("cwd")
            continue
        if entry_type == "turn_context":
            transcript.cwd = payload.get("cwd") or transcript.cwd
            continue
        if entry_type == "event_msg":
            event_type = payload.get("type")
            role = {"user_message": "user", "agent_message": "assistant"}.get(event_type)
            text = clean_visible_text(payload.get("message"))
            if role and text:
                visible_events.append(Message(role=role, text=text, timestamp=iso(timestamp)))

    # Fail closed: only Codex UI events positively identified as visible prose
    # are eligible. response_item records can contain reinjected context between
    # turns, so they are never treated as transcript messages.
    transcript.messages = visible_events
    transcript.updated_at = latest
    return transcript


def roots_for(args: argparse.Namespace) -> dict[str, Path]:
    roots = {"codex": args.codex_root, "claude": args.claude_root}
    if args.platform == "both":
        return roots
    return {args.platform: roots[args.platform]}


def within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def parse_path(platform: str, path: Path) -> Transcript:
    return parse_codex(path) if platform == "codex" else parse_claude(path)


def discover(args: argparse.Namespace) -> tuple[list[tuple[str, Path]], dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    candidates: list[tuple[float, str, Path]] = []
    selected_roots = roots_for(args)
    availability = {}

    for platform, root in selected_roots.items():
        availability[platform] = root.is_dir()
        if not root.is_dir():
            continue
        for path in root.rglob("*.jsonl"):
            if not path.is_file() or not within(path, root):
                continue
            try:
                modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            except OSError:
                continue
            if modified >= cutoff:
                candidates.append((modified.timestamp(), platform, path))

    candidates.sort(key=lambda item: item[0], reverse=True)
    truncated = len(candidates) > args.max_files
    selected = [(platform, path) for _, platform, path in candidates[: args.max_files]]
    scope = {
        "platforms": list(selected_roots),
        "days": args.days,
        "roots": {platform: str(root) for platform, root in selected_roots.items()},
        "available": availability,
        "files_considered": len(candidates),
        "files_parsed": len(selected),
        "file_scan_truncated": truncated,
    }
    return selected, scope


def query_terms(query: str) -> tuple[str, list[str]]:
    phrase = re.sub(r"\s+", " ", query).strip().casefold()
    raw = TOKEN.findall(phrase)
    terms = list(dict.fromkeys(token for token in raw if token not in STOP_WORDS))
    if not terms:
        terms = list(dict.fromkeys(raw))
    return phrase, terms


def score_message(text: str, phrase: str, terms: list[str]) -> float:
    haystack = text.casefold()
    term_counts = [haystack.count(term) for term in terms]
    unique = sum(count > 0 for count in term_counts)
    if unique == 0:
        return 0.0
    exact = 12.0 if len(phrase) >= 4 and phrase in haystack else 0.0
    frequency = sum(min(count, 4) for count in term_counts)
    return exact + unique * 4.0 + frequency


def excerpt(text: str, phrase: str, terms: list[str], limit: int = 420) -> str:
    if len(text) <= limit:
        return text
    folded = text.casefold()
    needles = [phrase, *terms]
    positions = [folded.find(needle) for needle in needles if needle and folded.find(needle) >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - limit // 3)
    end = min(len(text), start + limit)
    start = max(0, end - limit)
    prefix = "…" if start else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


def rank_transcript(
    transcript: Transcript, phrase: str, terms: list[str], snippet_limit: int
) -> dict[str, Any] | None:
    matches = []
    covered = set()
    total_hits = 0
    for index, message in enumerate(transcript.messages):
        score = score_message(message.text, phrase, terms)
        if score <= 0:
            continue
        folded = message.text.casefold()
        covered.update(term for term in terms if term in folded)
        total_hits += sum(folded.count(term) for term in terms)
        matches.append((score, index, message))
    if not matches:
        return None

    updated = transcript.updated_at
    if updated is None:
        updated = datetime.fromtimestamp(transcript.path.stat().st_mtime, timezone.utc)
    age_days = max(0.0, (datetime.now(timezone.utc) - updated).total_seconds() / 86400)
    recency = max(0.0, 4.0 - age_days / 10.0)
    score = max(item[0] for item in matches) + len(covered) * 5 + min(total_hits, 10) + recency
    selected = sorted(matches, key=lambda item: (-item[0], item[1]))[:snippet_limit]

    return {
        "platform": transcript.platform,
        "session_id": transcript.session_id,
        "path": str(transcript.path),
        "cwd": transcript.cwd,
        "updated_at": iso(updated),
        "score": round(score, 2),
        "matched_messages": len(matches),
        "snippets": [
            {
                "role": message.role,
                "timestamp": message.timestamp,
                "text": excerpt(message.text, phrase, terms),
            }
            for _, _, message in selected
        ],
    }


def search(args: argparse.Namespace) -> dict[str, Any]:
    phrase, terms = query_terms(args.query)
    files, scope = discover(args)
    results = []
    skipped = 0
    for platform, path in files:
        try:
            transcript = parse_path(platform, path)
            ranked = rank_transcript(transcript, phrase, terms, args.snippets)
        except (OSError, UnicodeError):
            skipped += 1
            continue
        if ranked is not None:
            results.append(ranked)
    # Files are discovered newest-first; Python's stable sort preserves that
    # recency order when two sessions have the same relevance score.
    results.sort(key=lambda item: -item["score"])
    scope["files_skipped"] = skipped
    return {"query": args.query, "terms": terms, "scope": scope, "results": results[: args.limit]}


def transcript_platform(path: Path, selected_roots: dict[str, Path]) -> str:
    matches = [platform for platform, root in selected_roots.items() if within(path, root)]
    if len(matches) != 1:
        raise ValueError("Transcript must be inside exactly one authorized transcript root")
    return matches[0]


def open_transcript(args: argparse.Namespace) -> dict[str, Any]:
    path = args.transcript.resolve()
    selected_roots = roots_for(args)
    platform = transcript_platform(path, selected_roots)
    if not path.is_file() or path.suffix != ".jsonl":
        raise ValueError("Transcript must be an existing JSONL file")
    transcript = parse_path(platform, path)
    phrase, terms = query_terms(args.query)
    scored = [
        (score_message(message.text, phrase, terms), index)
        for index, message in enumerate(transcript.messages)
    ]
    matches = [item for item in scored if item[0] > 0]
    matches.sort(key=lambda item: (-item[0], item[1]))

    chosen = set()
    for _, index in matches:
        for nearby in (index - 1, index, index + 1):
            if 0 <= nearby < len(transcript.messages):
                chosen.add(nearby)
            if len(chosen) >= args.max_messages:
                break
        if len(chosen) >= args.max_messages:
            break

    rendered = []
    remaining = args.max_chars
    for index in sorted(chosen)[: args.max_messages]:
        message = transcript.messages[index]
        if remaining <= 0:
            break
        text = message.text[:remaining]
        remaining -= len(text)
        rendered.append(
            {"index": index, "role": message.role, "timestamp": message.timestamp, "text": text}
        )

    updated = transcript.updated_at
    if updated is None:
        updated = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return {
        "query": args.query,
        "terms": terms,
        "scope": {
            "platforms": [platform],
            "roots": {platform: str(selected_roots[platform])},
            "max_messages": args.max_messages,
            "max_chars": args.max_chars,
        },
        "transcript": {
            "platform": platform,
            "session_id": transcript.session_id,
            "path": str(path),
            "cwd": transcript.cwd,
            "updated_at": iso(updated),
            "matching_messages": len(matches),
            "messages": rendered,
        },
    }


def render_human(payload: dict[str, Any]) -> str:
    if "transcript" in payload:
        transcript = payload["transcript"]
        lines = [
            f"[{transcript['platform']}] {transcript['updated_at'] or 'unknown date'} "
            f"{transcript['cwd'] or transcript['session_id'] or ''}".rstrip()
        ]
        lines.extend(f"- {item['role']}: {item['text']}" for item in transcript["messages"])
        lines.append(transcript["path"])
        return "\n".join(lines)

    scope = payload["scope"]
    lines = [
        f"Checked {scope['files_parsed']} recent transcript(s) across "
        f"{', '.join(scope['platforms'])}."
    ]
    if not payload["results"]:
        lines.append("no relevant prior work found")
        return "\n".join(lines)
    for index, result in enumerate(payload["results"], 1):
        label = result["cwd"] or result["session_id"] or result["path"]
        lines.append(f"{index}. [{result['platform']}] {result['updated_at']} {label}")
        lines.extend(f"   {item['role']}: {item['text']}" for item in result["snippets"])
        lines.append(f"   {result['path']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        payload = open_transcript(args) if args.transcript else search(args)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_human(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
