#!/usr/bin/env python3
"""Check or mirror shared skills between Codex (.agents) and Claude Code (.claude)."""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


PLATFORMS = {
    "agents": {
        "skills_dir": ".agents/skills",
        "other": "claude",
        "display": "Codex",
        "ignored_rel_prefixes": ("agents/",),
    },
    "claude": {
        "skills_dir": ".claude/skills",
        "other": "agents",
        "display": "Claude Code",
        "ignored_rel_prefixes": (),
    },
}

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".sh",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
}

PLATFORM_FRONTMATTER_FIELDS = {"category"}


@dataclass
class Finding:
    level: str
    message: str


def platform_root(root: Path, platform: str) -> Path:
    return root / PLATFORMS[platform]["skills_dir"]


def skill_dir(root: Path, platform: str, skill: str) -> Path:
    return platform_root(root, platform) / skill


def iter_skills(root: Path, platform: str) -> set[str]:
    base = platform_root(root, platform)
    if not base.exists():
        return set()
    return {
        path.name
        for path in base.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    }


def ignored(platform: str, rel: Path) -> bool:
    rel_posix = rel.as_posix()
    return any(
        rel_posix == prefix.rstrip("/") or rel_posix.startswith(prefix)
        for prefix in PLATFORMS[platform]["ignored_rel_prefixes"]
    )


def files_for_skill(root: Path, platform: str, skill: str) -> dict[str, Path]:
    base = skill_dir(root, platform, skill)
    if not base.exists():
        return {}
    files: dict[str, Path] = {}
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(base)
        if ignored(platform, rel):
            continue
        files[rel.as_posix()] = path
    return files


def normalized_text(text: str) -> str:
    replacements = {
        ".agents/skills": "{SKILLS_DIR}",
        ".claude/skills": "{SKILLS_DIR}",
        ".codex/hooks/read-learnings.sh": "{HOOK_READ_LEARNINGS}",
        ".claude/hooks/read-learnings.sh": "{HOOK_READ_LEARNINGS}",
        ".codex/hooks": "{HOOKS_DIR}",
        ".claude/hooks": "{HOOKS_DIR}",
        ".codex/hooks.json": "{PLATFORM_SETTINGS}",
        ".claude/settings.json": "{PLATFORM_SETTINGS}",
        ".claude/settings.local.json": "{PLATFORM_SETTINGS_LOCAL}",
        "Codex hook": "{PLATFORM_HOOK}",
        "Claude Code hook": "{PLATFORM_HOOK}",
        "codex-hook": "{PLATFORM_HOOK_CLUSTER}",
        "claude-hook": "{PLATFORM_HOOK_CLUSTER}",
        "`AGENTS.md`": "`{PROJECT_RULES}`",
        "`CLAUDE.md` / `AGENTS.md`": "`{PROJECT_RULES}`",
        "`CLAUDE.md`": "`{PROJECT_RULES}`",
        "AGENTS.md": "{PROJECT_RULES}",
        "CLAUDE.md": "{PROJECT_RULES}",
        "同步 Claude Code 语义": "同步平台语义",
        "同步 Codex 语义": "同步平台语义",
        "`{PROJECT_RULES}` / `{PROJECT_RULES}`": "`{PROJECT_RULES}`",
        "保留 Claude 专属说明": "保留平台专属说明",
        "保留 Claude Code 专属命令、Hook、工具说明和平台限制": "保留平台专属说明",
    }
    normalized = text.replace("\r\n", "\n")
    if normalized.startswith("---\n"):
        frontmatter, separator, body = normalized[4:].partition("\n---\n")
        if separator:
            frontmatter = "\n".join(
                line
                for line in frontmatter.splitlines()
                if not re.match(r"^([A-Za-z][A-Za-z0-9_-]*):", line)
                or line.split(":", 1)[0] not in PLATFORM_FRONTMATTER_FIELDS
            )
            normalized = f"---\n{frontmatter}{separator}{body}"
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized.strip()


def compare_file(left: Path, right: Path) -> bool:
    if left.suffix.lower() in TEXT_SUFFIXES and right.suffix.lower() in TEXT_SUFFIXES:
        return normalized_text(left.read_text(encoding="utf-8")) == normalized_text(
            right.read_text(encoding="utf-8")
        )
    return filecmp.cmp(left, right, shallow=False)


def check_skill(root: Path, skill: str, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    left = skill_dir(root, "agents", skill)
    right = skill_dir(root, "claude", skill)
    if not left.exists():
        findings.append(Finding("ERROR", f"missing Codex skill: {left}"))
    if not right.exists():
        findings.append(Finding("ERROR", f"missing Claude Code skill: {right}"))
    if findings:
        return findings

    left_files = files_for_skill(root, "agents", skill)
    right_files = files_for_skill(root, "claude", skill)
    for rel in sorted(set(left_files) - set(right_files)):
        findings.append(Finding("ERROR", f"{skill}: missing in Claude Code: {rel}"))
    for rel in sorted(set(right_files) - set(left_files)):
        findings.append(Finding("ERROR", f"{skill}: missing in Codex: {rel}"))

    drift_level = "ERROR" if strict else "WARN"
    for rel in sorted(set(left_files) & set(right_files)):
        if not compare_file(left_files[rel], right_files[rel]):
            findings.append(Finding(drift_level, f"{skill}: content differs: {rel}"))

    if not findings:
        findings.append(Finding("OK", f"{skill}: synced"))
    return findings


def transform_text(text: str, source: str, target: str) -> str:
    if source == target:
        return text
    pairs = [
        (PLATFORMS[source]["skills_dir"], PLATFORMS[target]["skills_dir"]),
        (".codex/hooks/read-learnings.sh", ".claude/hooks/read-learnings.sh"),
        (".claude/hooks/read-learnings.sh", ".codex/hooks/read-learnings.sh"),
        (".codex/hooks.json", ".claude/settings.json"),
        (".claude/settings.json", ".codex/hooks.json"),
        ("Codex hook", "Claude Code hook"),
        ("Claude Code hook", "Codex hook"),
        ("codex-hook", "claude-hook"),
        ("claude-hook", "codex-hook"),
    ]
    transformed = text
    for old, new in pairs:
        if source == "agents" and old.startswith(".claude"):
            continue
        if source == "claude" and old.startswith(".codex"):
            continue
        transformed = transformed.replace(old, new)
    return transformed


def copy_file(source_path: Path, target_path: Path, source: str, target: str, apply: bool) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.suffix.lower() in TEXT_SUFFIXES:
        content = transform_text(source_path.read_text(encoding="utf-8"), source, target)
        if apply:
            target_path.write_text(content, encoding="utf-8")
    elif apply:
        shutil.copy2(source_path, target_path)
    return f"{source_path} -> {target_path}"


def sync_skill(root: Path, source: str, target: str, skill: str, apply: bool) -> list[Finding]:
    source_dir = skill_dir(root, source, skill)
    target_dir = skill_dir(root, target, skill)
    if not source_dir.exists():
        return [Finding("ERROR", f"source skill missing: {source_dir}")]

    findings = [Finding("INFO", f"{'apply' if apply else 'dry-run'} sync {source}:{skill} -> {target}:{skill}")]
    source_files = files_for_skill(root, source, skill)
    for rel, source_path in sorted(source_files.items()):
        if target == "claude" and rel.startswith("agents/"):
            continue
        target_path = target_dir / rel
        findings.append(Finding("INFO", copy_file(source_path, target_path, source, target, apply)))
    return findings


def print_findings(findings: list[Finding]) -> None:
    for finding in findings:
        print(f"[{finding.level}] {finding.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Vault root. Defaults to current directory.")
    parser.add_argument("--skill", action="append", help="Skill to check or sync. Repeatable.")
    parser.add_argument("--strict", action="store_true", help="Treat normalized content drift as an error.")
    parser.add_argument("--from-platform", choices=sorted(PLATFORMS), help="Source platform for sync.")
    parser.add_argument("--to-platform", choices=sorted(PLATFORMS), help="Target platform for sync.")
    parser.add_argument("--apply", action="store_true", help="Apply sync. Omit for dry-run.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.from_platform or args.to_platform:
        if not args.from_platform or not args.to_platform:
            parser.error("--from-platform and --to-platform must be used together")
        if args.from_platform == args.to_platform:
            parser.error("--from-platform and --to-platform must differ")
        if not args.skill:
            parser.error("--skill is required for sync")
        findings: list[Finding] = []
        for skill in args.skill:
            findings.extend(sync_skill(root, args.from_platform, args.to_platform, skill, args.apply))
        print_findings(findings)
        return 1 if any(f.level == "ERROR" for f in findings) else 0

    skills = set(args.skill or [])
    if not skills:
        skills = iter_skills(root, "agents") | iter_skills(root, "claude")

    findings = []
    for skill in sorted(skills):
        findings.extend(check_skill(root, skill, args.strict))
    print_findings(findings)
    return 1 if any(f.level == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
