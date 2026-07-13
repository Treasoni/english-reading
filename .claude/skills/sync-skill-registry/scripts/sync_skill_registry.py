#!/usr/bin/env python3
"""
sync_skill_registry.py — 技能注册表同步工具

读取 .claude/skills/*/SKILL.md 的前置元数据，
更新 .claude/rules/common/skill-invocation.md 中的技能列表。

用法:
    python3 .claude/skills/sync-skill-registry/scripts/sync_skill_registry.py

效果:
    - 自动新增有 SKILL.md 但表格中缺失的技能
    - 自动更新已有条目的描述和触发词
    - 自动移除 SKILL.md 已删除的技能（保留非本地技能）
    - 非本地技能（无 SKILL.md 的现有条目）保持不变
"""

import argparse
import os
import re
import pathlib
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent.parent  # .claude/skills/
INVOCATION_FILE = SKILL_DIR.parent / "rules" / "common" / "skill-invocation.md"  # .claude/rules/common/skill-invocation.md

# 已知技能的默认分类回退（用于 symlink 技能或未声明 category 的情况）
FALLBACK_CATEGORIES = {
    "skill-creator": "代码质量",
}


# ── Frontmatter Parser ────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter (--- delimited) from SKILL.md content."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}

    frontmatter = {}
    for line in lines[1:end_idx]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()

    return frontmatter


def extract_triggers(description: str) -> str:
    """Extract trigger keywords from description.

    Priority:
    1. "触发词：" marker → comma/middle-dot separated list
    2. Quoted keywords in Chinese « » or ""
    3. Fallback: abbreviated summary
    """
    # 1. Explicit 触发词 marker
    for marker in ("触发词：", "触发词:", "Triggers:", "triggers:"):
        if marker in description:
            parts = description.split(marker, 1)
            triggers_raw = parts[1].strip()
            # Remove trailing punctuation
            triggers_raw = re.sub(r"[。，、；\.,;]+$", "", triggers_raw)
            return triggers_raw

    # 2. Quoted keywords — handle ASCII "..." and Chinese "“...”" and 「...」
    quoted = re.findall(r'"([^"]+)"|“([^”]+)”|「([^」]+)」', description)
    if quoted:
        keywords = [k for group in quoted for k in group if k]
        return "、".join(keywords[:8])  # Limit to top 8

    # 3. Fallback: use first sentence of description
    first_sentence = description.split("。")[0].split(". ")[0]
    if len(first_sentence) > 40:
        first_sentence = first_sentence[:40] + "…"
    return first_sentence


def extract_scene(description: str) -> str:
    """Extract the '触发场景' (use-case summary) from description."""
    # Remove explicit 触发词 part to avoid duplication
    for marker in ("触发词：", "触发词:", "Triggers:", "triggers:"):
        if marker in description:
            description = description.split(marker)[0].strip()

    # Use the description as-is (it's already the scene summary)
    # But trim if too long for a table
    if len(description) > 80:
        # Try to find a natural break point at sentence end
        for punct in ["。", "；"]:
            idx = description.find(punct)
            if 30 <= idx <= 80:
                return description[: idx + 1]
        # Fallback: break at comma, but trim trailing comma
        for punct in ["，", ","]:
            idx = description.rfind(punct, 30, 80)
            if idx != -1:
                return description[:idx]
        # Hard cut
        return description[:77] + "…"
    return description


# ── Skill Scanning ────────────────────────────────────────────────

def scan_local_skills(skills_dir: pathlib.Path) -> dict:
    """Scan .claude/skills/*/SKILL.md and return {name: metadata} dict."""
    skills = {}
    for skill_path in sorted(skills_dir.iterdir()):
        skill_md = skill_path / "SKILL.md"
        if not skill_md.is_file():
            continue

        text = skill_md.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)

        name = frontmatter.get("name", skill_path.name)
        description = frontmatter.get("description", "")
        category = frontmatter.get("category", "")
        triggers = extract_triggers(description)
        scene = extract_scene(description)

        skills[name] = {
            "name": name,
            "description": description,
            "category": category,
            "triggers": triggers,
            "scene": scene,
        }

    return skills


# ── skill-invocation.md Parser ────────────────────────────────────

def parse_invocation_tables(text: str) -> list:
    """Parse existing skill tables from skill-invocation.md.

    Returns list of dicts: {category, rows: [{name, scene, triggers}]}
    """
    # Locate the tables section
    section_start = text.find("## 技能列表")
    section_end = text.find("### 1. 分析意图")

    if section_start == -1 or section_end == -1:
        return []

    section = text[section_start:section_end]
    lines = section.split("\n")

    tables = []
    current_category = None
    in_table = False
    header_seen = False

    for line in lines:
        # Category header
        if line.startswith("#### "):
            current_category = line[5:].strip()
            in_table = False
            header_seen = False
            continue

        # Table row
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]

            # Skip table separator lines (|---|)
            if cells and all(re.match(r'^-{3,}$', c) for c in cells if c.strip()):
                header_seen = True
                continue

            if not header_seen and len(cells) >= 3:
                header_seen = True
                continue

            if header_seen and len(cells) >= 3:
                if current_category:
                    name = cells[0].strip("`").strip()
                    tables.append({
                        "name": name,
                        "category": current_category,
                        "scene": cells[1].strip() if len(cells) > 1 else "",
                        "triggers": cells[2].strip() if len(cells) > 2 else "",
                    })
                continue

        # Other separator line
        if line.startswith("|---"):
            continue

        # Non-table line resets
        if line.strip() == "":
            in_table = False
        elif not line.startswith("|"):
            in_table = False
            header_seen = False

    return tables


# ── Table Generation ──────────────────────────────────────────────

def generate_tables(
    managed_skills: dict,
    preserved_rows: list,
    category_order: list,
) -> str:
    """Generate the markdown tables section.

    Args:
        managed_skills: {name: {name, category, triggers, scene}} from SKILL.md
        preserved_rows: [{name, category, scene, triggers}] from existing tables (non-local)
        category_order: ordered list of category names

    Returns:
        Markdown string for the tables section (including the ## 技能列表 header)
    """
    # Group managed skills by category
    managed_by_category: dict[str, list] = {}
    for name, info in managed_skills.items():
        cat = info["category"] or "未分类"
        if cat not in managed_by_category:
            managed_by_category[cat] = []
        managed_by_category[cat].append(info)

    # Group preserved rows by category
    preserved_by_category: dict[str, list] = {}
    for row in preserved_rows:
        cat = row["category"]
        if cat not in preserved_by_category:
            preserved_by_category[cat] = []
        preserved_by_category[cat].append(row)

    # Build all categories that have content
    all_categories = []
    seen = set()
    for cat in category_order:
        has_managed = cat in managed_by_category
        has_preserved = cat in preserved_by_category
        if has_managed or has_preserved:
            all_categories.append(cat)
            seen.add(cat)

    # Add any remaining categories
    for cat in managed_by_category:
        if cat not in seen:
            all_categories.append(cat)
            seen.add(cat)
    for cat in preserved_by_category:
        if cat not in seen:
            all_categories.append(cat)
            seen.add(cat)

    # Generate markdown
    lines = ["## 技能列表\n"]
    for cat in all_categories:
        cat_skills = managed_by_category.get(cat, [])
        pres_skills = preserved_by_category.get(cat, [])

        # Sort: managed skills first (alphabetically), then preserved (alphabetically)
        cat_skills.sort(key=lambda s: s["name"])
        pres_skills.sort(key=lambda s: s["name"])

        all_entries = cat_skills + pres_skills
        if not all_entries:
            continue

        lines.append(f"#### {cat}\n")
        lines.append("| 技能 | 触发场景 | 关键触发词 |")
        lines.append("|------|----------|-----------|")

        for entry in all_entries:
            name = f"`{entry['name']}`"
            scene = entry.get("scene", "")
            triggers = entry.get("triggers", "")
            # Escape pipe characters in content
            scene = scene.replace("|", "\\|")
            triggers = triggers.replace("|", "\\|")
            lines.append(f"| {name} | {scene} | {triggers} |")

        lines.append("")  # empty line after each section

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="同步技能注册表：读取 .claude/skills/*/SKILL.md，更新 skill-invocation.md",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览变更，不写入文件",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出详细调试信息",
    )
    return parser.parse_args(argv)


def main():
    args = parse_args()
    skills_dir = SKILL_DIR.resolve()
    invocation_file = INVOCATION_FILE.resolve()

    if not invocation_file.exists():
        print(f"Error: {invocation_file} not found")
        return 1

    # Step 1: Scan local skills
    print(f"扫描 {skills_dir}/*/SKILL.md ...")
    managed_skills = scan_local_skills(skills_dir)
    print(f"  发现 {len(managed_skills)} 个本地技能")

    # Step 2: Read current invocation file
    text = invocation_file.read_text(encoding="utf-8")

    # Step 3: Parse existing tables
    existing_rows = parse_invocation_tables(text)
    print(f"  表格中找到 {len(existing_rows)} 个现有条目")

    # Step 4: Determine preserved skills (in tables but no SKILL.md)
    managed_names = set(managed_skills.keys())
    preserved_rows = [r for r in existing_rows if r["name"] not in managed_names]
    managed_rows = [r for r in existing_rows if r["name"] in managed_names]

    if preserved_rows:
        preserved_names = set(r["name"] for r in preserved_rows)
        print(f"  保留 {len(preserved_rows)} 个非本地条目: {', '.join(sorted(preserved_names))}")
    if managed_rows:
        print(f"  更新 {len(managed_rows)} 个现有受管条目")

    # Step 5: Infer category for skills without frontmatter category
    # Priority: 1) fallback mapping 2) existing table position 3) "未分类"
    existing_category_map = {r["name"]: r["category"] for r in existing_rows}
    for name, info in managed_skills.items():
        if info["category"]:
            continue
        if name in FALLBACK_CATEGORIES:
            info["category"] = FALLBACK_CATEGORIES[name]
        elif name in existing_category_map:
            info["category"] = existing_category_map[name]
        else:
            info["category"] = "未分类"
        if args.verbose:
            print(f"  推断 {name} → 分类: {info['category']}")

    # Step 6: Check for removals
    removed_names = set()
    for row in managed_rows:
        if row["name"] not in managed_skills:
            removed_names.add(row["name"])
    if removed_names:
        print(f"  移除 {len(removed_names)} 个已删除条目: {', '.join(sorted(removed_names))}")

    # Step 6: Check for additions
    existing_names = set(r["name"] for r in existing_rows)
    added_names = set(managed_skills.keys()) - existing_names
    if added_names:
        print(f"  新增 {len(added_names)} 个条目: {', '.join(sorted(added_names))}")

    # Step 7: Build category order from existing tables
    seen_categories = []
    for row in existing_rows:
        if row["category"] not in seen_categories:
            seen_categories.append(row["category"])

    # Step 8: Generate new tables
    new_tables = generate_tables(managed_skills, preserved_rows, seen_categories)

    # Step 9: Replace section in file
    section_start = text.find("## 技能列表")
    section_end = text.find("### 1. 分析意图")

    if section_start == -1:
        print("Error: cannot find '## 技能列表' section marker")
        return 1
    if section_end == -1:
        print("Error: cannot find '### 1. 分析意图' section marker")
        return 1

    # Preserve the `\n` before ### 1. 分析意图
    new_text = text[:section_start] + new_tables + "\n" + text[section_end:]

    if args.dry_run:
        print("\n─── Dry Run ──────────────────────────────────────────")
        print(f"将更新 {invocation_file}")
        diff_lines = new_text.split("\n")
        orig_lines = text.split("\n")
        changes = 0
        for i, line in enumerate(diff_lines):
            if i >= len(orig_lines) or line != orig_lines[i]:
                if changes == 0:
                    print("\n变更预览（首个差异附近）:")
                if changes < 20:
                    context_before = min(3, i)
                    if i + context_before < len(orig_lines):
                        print(f"  行 {i+1}: {'→ ' + line}")
                changes += 1
        if changes:
            print(f"\n共 {changes} 行变更（按行级差异统计）")
            print("─── 未写入 ────────────────────────────────────────────")
        else:
            print("  无变更")
        return 0

    # Step 10: Write back
    invocation_file.write_text(new_text, encoding="utf-8")
    print(f"\n✓ 已更新 {invocation_file}")

    if added_names or removed_names:
        print("\n提示：建议运行 `.codex/scripts/sync-codex-to-claude.sh` 以同步 Codex 配置。")
    return 0


if __name__ == "__main__":
    exit(main())
