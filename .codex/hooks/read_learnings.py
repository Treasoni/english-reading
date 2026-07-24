#!/usr/bin/env python3
"""Print .learnings context for agent session-start hooks."""

from __future__ import annotations

import argparse
from pathlib import Path


def default_project_root() -> Path:
    # Expected install shape: <project>/<agent-dir>/hooks/read_learnings.py
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def tail_lines(text: str, count: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-count:])


def print_section(title: str, body: str) -> None:
    if not body:
        return
    print(f"## {title}")
    print("")
    print(body.rstrip())
    print("")
    print("---")
    print("")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=None, help="Project root. Defaults to two directories above this hook.")
    parser.add_argument("--tail-lines", type=int, default=50, help="Number of recent LEARNINGS.md lines to include.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root else default_project_root()
    learnings_dir = project_root / ".learnings"

    print("<system-reminder>")
    print("# Learnings Reminder")
    print("")

    print_section("Rules (highest priority)", read_text(learnings_dir / "RULES.md"))
    print_section("Error Log (avoid repeating)", read_text(learnings_dir / "ERRORS.md"))

    learnings = read_text(learnings_dir / "LEARNINGS.md")
    if learnings:
        print("## Recent Learnings")
        print("")
        print(tail_lines(learnings, args.tail_lines).rstrip())
        print("")

    print("")
    print("Before doing task work, apply the rules and avoid repeating recorded errors.")
    print("</system-reminder>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
