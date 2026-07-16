#!/usr/bin/env python3
"""Validate the structural consistency of this Obsidian learning vault."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


FINAL_NOTE_PATTERN = re.compile(r"^(?P<topic>\d{4}-passage\d+(?:-[a-z0-9-]+)?)-精读笔记\.md$")


@dataclass
class Finding:
    level: str
    message: str


def read_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return values
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"\'')
    return {}


def final_notes(root: Path) -> dict[str, Path]:
    notes: dict[str, Path] = {}
    for path in root.glob("20??阅读/*-精读笔记.md"):
        match = FINAL_NOTE_PATTERN.match(path.name)
        if match:
            notes[match.group("topic")] = path
    return notes


def validate(root: Path, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    notes = final_notes(root)
    intermediate = root / "intermediate"

    for topic_dir in sorted(path for path in intermediate.iterdir() if path.is_dir()):
        topic = topic_dir.name
        status_path = topic_dir / "STATUS.md"
        status = read_frontmatter(status_path) if status_path.exists() else {}
        in_progress = status.get("status") == "in_progress"

        for filename in ("formatted-article.md", "translation.md"):
            if not (topic_dir / filename).is_file():
                findings.append(Finding("ERROR", f"{topic}: missing {filename}"))
        if not (topic_dir / "grammar-notes.md").is_file() and not in_progress:
            findings.append(Finding("ERROR", f"{topic}: missing grammar-notes.md"))
        if topic not in notes and not in_progress:
            findings.append(Finding("ERROR", f"{topic}: missing final study note"))
        if in_progress:
            level = "ERROR" if strict else "WARN"
            findings.append(Finding(level, f"{topic}: marked in progress"))
            if status.get("topic") != topic:
                findings.append(Finding("ERROR", f"{topic}: STATUS.md topic does not match directory"))

    for topic, note in sorted(notes.items()):
        if not (intermediate / topic).is_dir():
            findings.append(Finding("ERROR", f"{note}: no matching intermediate directory"))
        parent_year = note.parent.name.removesuffix("阅读")
        if parent_year != topic[:4]:
            findings.append(Finding("ERROR", f"{note}: stored under {parent_year}阅读, expected {topic[:4]}阅读"))
        frontmatter = read_frontmatter(note)
        if frontmatter.get("topic") != topic:
            actual = frontmatter.get("topic", "missing")
            findings.append(Finding("ERROR", f"{note}: topic is {actual!r}, expected {topic!r}"))

    if not findings:
        findings.append(Finding("OK", "vault note structure is consistent"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Vault root (default: current directory)")
    parser.add_argument("--strict", action="store_true", help="Treat in-progress articles as errors")
    args = parser.parse_args()

    findings = validate(args.root.resolve(), args.strict)
    for finding in findings:
        print(f"[{finding.level}] {finding.message}")
    return 1 if any(finding.level == "ERROR" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
