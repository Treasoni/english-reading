#!/usr/bin/env python3
"""Reject platform-bound shared agent assets before synchronization."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


AGENT_DIRECTORIES = (".agents", ".codex", ".claude", ".codebuddy", ".agent-sync")
GENERATED_HOOK_CONFIGS = {
    Path(".codex/hooks.json"),
    Path(".claude/settings.json"),
    Path(".codebuddy/settings.json"),
}
LOCAL_ONLY_FILES = {
    Path(".claude/settings.local.json"),
}
SCANNER_IMPLEMENTATIONS = {
    Path(directory_name) / "skills/multi-agent-sync/scripts/validate_portability.py"
    for directory_name in AGENT_DIRECTORIES
}
SCANNER_IMPLEMENTATIONS.add(Path(".agent-sync/validate_portability.py"))
PLATFORMS = ("windows", "macos", "linux")
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".txt"}
ABSOLUTE_PATH = re.compile(r"/Users/|/home/|(?<![A-Za-z0-9_])[A-Za-z]:[\\/]")
SHELL_SHEBANG = re.compile(r"^#!.*\b(?:zsh|bash|sh|cmd(?:\.exe)?|powershell(?:\.exe)?|pwsh(?:\.exe)?)(?:\s|$)", re.IGNORECASE)
SHELL_COMMAND = re.compile(r"(?<![A-Za-z0-9_.-])(?:zsh|bash|cmd\.exe|powershell(?:\.exe)?|pwsh(?:\.exe)?)(?![A-Za-z0-9_.-])", re.IGNORECASE)


def candidate_files(root: Path) -> Iterable[tuple[Path, Path]]:
    """Yield shared-source files in a stable, repository-relative order."""
    files: list[tuple[Path, Path]] = []
    for directory_name in AGENT_DIRECTORIES:
        directory = root / directory_name
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            relative_path = path.relative_to(root)
            if relative_path in GENERATED_HOOK_CONFIGS | LOCAL_ONLY_FILES:
                continue
            # Packaged copies contain the detector's own regex literals.
            if relative_path in SCANNER_IMPLEMENTATIONS:
                continue
            if relative_path.parts[:2] == (".agent-sync", "local"):
                continue
            files.append((relative_path, path))
    yield from sorted(files, key=lambda item: item[0].as_posix())


def is_hook(relative_path: Path) -> bool:
    return "hooks" in relative_path.parts


def validate_tree(root: Path, platform_name: str) -> list[str]:
    """Return deterministic portability findings for shared agent sources."""
    if platform_name not in PLATFORMS:
        raise ValueError(f"unsupported platform: {platform_name}")

    findings: list[str] = []
    for relative_path, path in candidate_files(root):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        content = path.read_bytes()
        display_path = relative_path.as_posix()
        if b"\r\n" in content:
            findings.append(f"{display_path}: crlf")

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(f"{display_path}: invalid-utf8")
            continue
        if ABSOLUTE_PATH.search(text):
            findings.append(f"{display_path}: absolute-path")
        if is_hook(relative_path) and (SHELL_SHEBANG.search(text) or SHELL_COMMAND.search(text)):
            findings.append(f"{display_path}: shell-hook")
    return findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="repository root")
    parser.add_argument("--platform", choices=PLATFORMS, default="windows", help="target platform")
    args = parser.parse_args(argv)

    try:
        findings = validate_tree(Path(args.root).resolve(), args.platform)
    except OSError as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2
    if not findings:
        print("[OK] shared agent sources are portable")
        return 0
    for finding in findings:
        print(f"[ERROR] {finding}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
