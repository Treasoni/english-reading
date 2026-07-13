#!/usr/bin/env python3
"""Check or mirror shared skills between Codex and Claude Code skill folders."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from dataclasses import dataclass
from pathlib import Path


DEFAULT_PLATFORMS = {
    "agents": ".agents/skills",
    "claude": ".claude/skills",
}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt"}


@dataclass
class Finding:
    level: str
    message: str


def skill_root(root: Path, platform: str, dirs: dict[str, str]) -> Path:
    return root / dirs[platform]


def skill_dir(root: Path, platform: str, skill: str, dirs: dict[str, str]) -> Path:
    return skill_root(root, platform, dirs) / skill


def iter_skills(root: Path, platform: str, dirs: dict[str, str]) -> set[str]:
    base = skill_root(root, platform, dirs)
    if not base.exists():
        return set()
    return {path.name for path in base.iterdir() if path.is_dir() and (path / "SKILL.md").exists()}


def ignored(platform: str, rel: Path) -> bool:
    rel_posix = rel.as_posix()
    return platform == "agents" and (rel_posix == "agents" or rel_posix.startswith("agents/"))


def files_for_skill(root: Path, platform: str, skill: str, dirs: dict[str, str]) -> dict[str, Path]:
    base = skill_dir(root, platform, skill, dirs)
    if not base.exists():
        return {}
    files: dict[str, Path] = {}
    for path in base.rglob("*"):
        if path.is_file():
            rel = path.relative_to(base)
            if not ignored(platform, rel):
                files[rel.as_posix()] = path
    return files


def normalized_text(text: str, dirs: dict[str, str]) -> str:
    replacements = {
        dirs["agents"]: "{CODEX_SKILLS}",
        dirs["claude"]: "{CLAUDE_SKILLS}",
        ".codex/hooks": "{CODEX_HOOKS}",
        ".claude/hooks": "{CLAUDE_HOOKS}",
        ".codex/hooks.json": "{CODEX_SETTINGS}",
        ".claude/settings.json": "{CLAUDE_SETTINGS}",
        "Codex": "{CODEX}",
        "Claude Code": "{CLAUDE}",
        "codex-hook": "{CODEX_HOOK}",
        "claude-hook": "{CLAUDE_HOOK}",
    }
    normalized = text.replace("\r\n", "\n")
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized.strip()


def compare_file(left: Path, right: Path, dirs: dict[str, str]) -> bool:
    if left.suffix.lower() in TEXT_SUFFIXES and right.suffix.lower() in TEXT_SUFFIXES:
        return normalized_text(left.read_text(encoding="utf-8"), dirs) == normalized_text(
            right.read_text(encoding="utf-8"), dirs
        )
    return filecmp.cmp(left, right, shallow=False)


def check_skill(root: Path, skill: str, dirs: dict[str, str], strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    left = skill_dir(root, "agents", skill, dirs)
    right = skill_dir(root, "claude", skill, dirs)
    if not left.exists():
        findings.append(Finding("ERROR", f"missing Codex skill: {left}"))
    if not right.exists():
        findings.append(Finding("ERROR", f"missing Claude Code skill: {right}"))
    if findings:
        return findings

    left_files = files_for_skill(root, "agents", skill, dirs)
    right_files = files_for_skill(root, "claude", skill, dirs)
    for rel in sorted(set(left_files) - set(right_files)):
        findings.append(Finding("ERROR", f"{skill}: missing in Claude Code: {rel}"))
    for rel in sorted(set(right_files) - set(left_files)):
        findings.append(Finding("ERROR", f"{skill}: missing in Codex: {rel}"))

    drift_level = "ERROR" if strict else "WARN"
    for rel in sorted(set(left_files) & set(right_files)):
        if not compare_file(left_files[rel], right_files[rel], dirs):
            findings.append(Finding(drift_level, f"{skill}: content differs: {rel}"))
    if not findings:
        findings.append(Finding("OK", f"{skill}: synced"))
    return findings


def transform_text(text: str, source: str, target: str, dirs: dict[str, str]) -> str:
    transformed = text.replace(dirs[source], dirs[target])
    if source == "agents" and target == "claude":
        transformed = transformed.replace(".codex/hooks", ".claude/hooks")
        transformed = transformed.replace(".codex/hooks.json", ".claude/settings.json")
        transformed = transformed.replace("Codex hook", "Claude Code hook")
        transformed = transformed.replace("codex-hook", "claude-hook")
    elif source == "claude" and target == "agents":
        transformed = transformed.replace(".claude/hooks", ".codex/hooks")
        transformed = transformed.replace(".claude/settings.json", ".codex/hooks.json")
        transformed = transformed.replace("Claude Code hook", "Codex hook")
        transformed = transformed.replace("claude-hook", "codex-hook")
    return transformed


def copy_file(source_path: Path, target_path: Path, source: str, target: str, dirs: dict[str, str], apply: bool) -> str:
    if source_path.suffix.lower() in TEXT_SUFFIXES:
        content = transform_text(source_path.read_text(encoding="utf-8"), source, target, dirs)
        if apply:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
    elif apply:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
    return f"{source_path} -> {target_path}"


def sync_skill(root: Path, source: str, target: str, skill: str, dirs: dict[str, str], apply: bool) -> list[Finding]:
    source_dir = skill_dir(root, source, skill, dirs)
    target_dir = skill_dir(root, target, skill, dirs)
    if not source_dir.exists():
        return [Finding("ERROR", f"source skill missing: {source_dir}")]
    findings = [Finding("INFO", f"{'apply' if apply else 'dry-run'} sync {source}:{skill} -> {target}:{skill}")]
    for rel, source_path in sorted(files_for_skill(root, source, skill, dirs).items()):
        if target == "claude" and rel.startswith("agents/"):
            continue
        findings.append(Finding("INFO", copy_file(source_path, target_dir / rel, source, target, dirs, apply)))
    return findings


def print_findings(findings: list[Finding]) -> None:
    for finding in findings:
        print(f"[{finding.level}] {finding.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--agents-dir", default=DEFAULT_PLATFORMS["agents"])
    parser.add_argument("--claude-dir", default=DEFAULT_PLATFORMS["claude"])
    parser.add_argument("--skill", action="append")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--from-platform", choices=("agents", "claude"))
    parser.add_argument("--to-platform", choices=("agents", "claude"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    dirs = {"agents": args.agents_dir, "claude": args.claude_dir}

    if args.from_platform or args.to_platform:
        if not args.from_platform or not args.to_platform or args.from_platform == args.to_platform:
            parser.error("--from-platform and --to-platform must be used together and differ")
        if not args.skill:
            parser.error("--skill is required for sync")
        findings: list[Finding] = []
        for skill in args.skill:
            findings.extend(sync_skill(root, args.from_platform, args.to_platform, skill, dirs, args.apply))
        print_findings(findings)
        return 1 if any(item.level == "ERROR" for item in findings) else 0

    skills = set(args.skill or []) or (iter_skills(root, "agents", dirs) | iter_skills(root, "claude", dirs))
    findings = []
    for skill in sorted(skills):
        findings.extend(check_skill(root, skill, dirs, args.strict))
    print_findings(findings)
    return 1 if any(item.level == "ERROR" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
