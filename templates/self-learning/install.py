#!/usr/bin/env python3
"""Install the self-learning skill templates into another project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parent
SKILLS = ("digest", "maintain-learnings")


def copytree(source: Path, target: Path, overwrite: bool) -> None:
    if target.exists():
        if not overwrite:
            print(f"[SKIP] exists: {target}")
            return
        shutil.rmtree(target)
    shutil.copytree(source, target)
    print(f"[OK] copied: {target}")


def copyfile(source: Path, target: Path, overwrite: bool) -> None:
    if target.exists() and not overwrite:
        print(f"[SKIP] exists: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    print(f"[OK] copied: {target}")


def install_skills(target_root: Path, platform_dir: str, include_openai_yaml: bool, overwrite: bool) -> None:
    skills_root = target_root / platform_dir / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    for skill in SKILLS:
        source = TEMPLATE_ROOT / "skills" / skill
        target = skills_root / skill
        copytree(source, target, overwrite)
        if not include_openai_yaml:
            agents_dir = target / "agents"
            if agents_dir.exists():
                shutil.rmtree(agents_dir)
                print(f"[OK] removed Codex UI metadata from: {agents_dir}")


def install_learnings(target_root: Path, overwrite: bool) -> None:
    learnings_root = target_root / ".learnings"
    learnings_root.mkdir(parents=True, exist_ok=True)
    (learnings_root / "archive").mkdir(parents=True, exist_ok=True)
    for name in ("LEARNINGS.md", "ERRORS.md", "RULES.md"):
        copyfile(TEMPLATE_ROOT / "learnings" / name, learnings_root / name, overwrite)


def install_hooks(target_root: Path, install_codex: bool, install_claude: bool, overwrite: bool) -> None:
    hook_source = TEMPLATE_ROOT / "hooks" / "read-learnings.sh"
    if install_codex:
        copyfile(hook_source, target_root / ".codex" / "hooks" / "read-learnings.sh", overwrite)
        codex_config = target_root / ".codex" / "hooks.json"
        if codex_config.exists() and not overwrite:
            print(f"[SKIP] exists: {codex_config}")
            print("[NEXT] Merge templates/self-learning/hooks/codex-hooks.json.template into .codex/hooks.json")
        else:
            content = (TEMPLATE_ROOT / "hooks" / "codex-hooks.json.template").read_text(encoding="utf-8")
            content = content.replace("{{PROJECT_ROOT}}", str(target_root))
            copyfile_from_text(content, codex_config)
    if install_claude:
        copyfile(hook_source, target_root / ".claude" / "hooks" / "read-learnings.sh", overwrite)
        claude_config = target_root / ".claude" / "settings.json"
        if claude_config.exists() and not overwrite:
            print(f"[SKIP] exists: {claude_config}")
            print("[NEXT] Merge templates/self-learning/hooks/claude-settings.json.template into .claude/settings.json")
        else:
            content = (TEMPLATE_ROOT / "hooks" / "claude-settings.json.template").read_text(encoding="utf-8")
            content = content.replace("{{PROJECT_ROOT}}", str(target_root))
            copyfile_from_text(content, claude_config)


def copyfile_from_text(content: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"[OK] wrote: {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Target project root.")
    parser.add_argument("--no-codex", action="store_true", help="Do not install .agents/skills.")
    parser.add_argument("--no-claude", action="store_true", help="Do not install .claude/skills.")
    parser.add_argument("--no-hooks", action="store_true", help="Do not install read-learnings hooks.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing template skills and learning files.")
    args = parser.parse_args()

    target_root = Path(args.target).resolve()
    if not target_root.exists():
        parser.error(f"target does not exist: {target_root}")

    if not args.no_codex:
        install_skills(target_root, ".agents", include_openai_yaml=True, overwrite=args.overwrite)
    if not args.no_claude:
        install_skills(target_root, ".claude", include_openai_yaml=False, overwrite=args.overwrite)

    install_learnings(target_root, overwrite=args.overwrite)
    if not args.no_hooks:
        install_hooks(target_root, install_codex=not args.no_codex, install_claude=not args.no_claude, overwrite=args.overwrite)
    print("")
    print("[NEXT] Merge templates/self-learning/AGENTS.snippet.md into the target project's AGENTS.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
