#!/usr/bin/env python3
"""Audit .learnings for recurring errors and likely source files to repair."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ACTIVE_FILES = ("LEARNINGS.md", "ERRORS.md", "RULES.md")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$", re.MULTILINE)
ISSUE_WORDS = (
    "错误",
    "问题",
    "反馈",
    "纠正",
    "根因",
    "遗漏",
    "缺少",
    "跳过",
    "复发",
    "重复",
    "异常",
    "不能",
    "不得",
    "error",
    "failed",
    "missing",
    "skip",
)
GENERIC_TITLES = {"会话概要", "改进记录", "修复", "预防措施"}
KEYWORD_CLUSTERS = {
    "markdown": ("markdown", "frontmatter", "yaml", "table", "表格", "标题", "callout"),
    "interaction": ("askuserquestion", "other", "路径", "文件名", "用户反馈", "提问"),
    "hook": ("hook", "hooks", "read-learnings", "上下文", "经验库提醒"),
    "tooling": ("write 工具", "read 工具", "apply_patch", "sandbox", "权限"),
}


@dataclass
class Record:
    file: str
    line: int
    title: str
    text: str
    active: bool
    kind: str
    clusters: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def discover_skills(root: Path, skills_dir: str) -> list[str]:
    base = root / skills_dir
    if not base.exists():
        return []
    return sorted(path.name for path in base.iterdir() if (path / "SKILL.md").exists())


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text.lower())


def find_clusters(text: str, skills: list[str]) -> list[str]:
    normalized = normalize(text)
    clusters = [skill for skill in skills if normalize(skill) in normalized]
    lowered = text.lower()
    for cluster, terms in KEYWORD_CLUSTERS.items():
        if any(term.lower() in lowered for term in terms):
            clusters.append(cluster)
    return sorted(set(clusters)) or ["general"]


def split_records(path: Path, display_path: str, active: bool, skills: list[str]) -> list[Record]:
    text = read_text(path)
    if not text:
        return []
    kind = "rules" if display_path.endswith("RULES.md") else "entry"
    matches = list(HEADING_RE.finditer(text))
    records: list[Record] = []
    if not matches:
        if kind == "rules" or (len(text.strip()) > 120 and any(word in text.lower() for word in ISSUE_WORDS)):
            return [Record(display_path, 1, path.name, text, active, kind, find_clusters(text, skills))]
        return []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        title = match.group(2).strip()
        if kind != "rules" and title in GENERIC_TITLES:
            continue
        if kind != "rules" and not any(word in block.lower() for word in ISSUE_WORDS):
            continue
        if len(block) < 80 and kind != "rules":
            continue
        records.append(
            Record(
                display_path,
                line_number(text, start),
                title,
                block,
                active,
                kind,
                find_clusters(block, skills),
            )
        )
    return records


def collect_records(root: Path, skills_dir: str, include_archive: bool) -> list[Record]:
    skills = discover_skills(root, skills_dir)
    learnings = root / ".learnings"
    records: list[Record] = []
    for name in ACTIVE_FILES:
        records.extend(split_records(learnings / name, f".learnings/{name}", True, skills))
    if include_archive:
        archive = learnings / "archive"
        for path in sorted(archive.glob("*.md")) if archive.exists() else []:
            records.extend(split_records(path, f".learnings/archive/{path.name}", False, skills))
    return records


def source_candidates(root: Path, cluster: str, skills_dir: str, rules_file: str, hooks_path: str) -> list[str]:
    candidates: list[str] = []
    skill_file = root / skills_dir / cluster / "SKILL.md"
    if skill_file.exists():
        candidates.append(f"{skills_dir}/{cluster}/SKILL.md")
        refs = root / skills_dir / cluster / "references"
        if refs.exists():
            candidates.append(f"{skills_dir}/{cluster}/references/")
    if cluster == "hook":
        candidates.append(hooks_path)
    elif cluster in {"markdown", "interaction", "tooling", "general"}:
        candidates.append(rules_file)
    return list(dict.fromkeys(candidates))


def active_line_counts(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in ACTIVE_FILES:
        text = read_text(root / ".learnings" / name)
        counts[f".learnings/{name}"] = len(text.splitlines()) if text else 0
    return counts


def summarize(root: Path, records: list[Record], args: argparse.Namespace) -> dict:
    line_counts = active_line_counts(root)
    grouped: dict[str, list[Record]] = defaultdict(list)
    for record in records:
        for cluster in record.clusters:
            grouped[cluster].append(record)

    clusters = []
    for cluster, items in grouped.items():
        active_count = sum(1 for item in items if item.active and item.kind != "rules")
        total_count = sum(1 for item in items if item.kind != "rules")
        rule_count = sum(1 for item in items if item.kind == "rules")
        repeated = active_count >= 2 or total_count >= 3 or (rule_count > 0 and active_count > 0)
        over_threshold = any(count > args.line_threshold for count in line_counts.values())
        if not repeated and active_count == 0:
            continue
        titles = Counter(item.title for item in items)
        clusters.append(
            {
                "cluster": cluster,
                "severity": "high" if repeated else "medium" if over_threshold else "low",
                "active_records": active_count,
                "total_records": total_count,
                "rule_records": rule_count,
                "sources_to_inspect": source_candidates(root, cluster, args.skills_dir, args.rules_file, args.hooks_path),
                "sample_titles": [title for title, _ in titles.most_common(5)],
                "active_locations": [
                    {"file": item.file, "line": item.line, "title": item.title}
                    for item in items
                    if item.active and item.kind != "rules"
                ][:8],
            }
        )
    clusters.sort(key=lambda item: (item["severity"] == "high", item["active_records"], item["total_records"]), reverse=True)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_line_counts": line_counts,
        "over_threshold": {path: count for path, count in line_counts.items() if count > args.line_threshold},
        "clusters": clusters,
    }


def render_markdown(summary: dict) -> str:
    lines = ["# Learnings Audit Report", "", f"Generated: {summary['generated_at']}", "", "## Active File Health", ""]
    for path, count in summary["active_line_counts"].items():
        lines.append(f"- `{path}`: {count} lines")
    lines.extend(["", "## Hotspot Clusters", ""])
    if not summary["clusters"]:
        lines.append("- No recurring clusters found.")
        return "\n".join(lines) + "\n"
    lines.append("| Cluster | Severity | Active | Total | Rules | Inspect |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for cluster in summary["clusters"]:
        inspect = ", ".join(f"`{item}`" for item in cluster["sources_to_inspect"]) or "-"
        lines.append(
            f"| `{cluster['cluster']}` | {cluster['severity']} | {cluster['active_records']} | "
            f"{cluster['total_records']} | {cluster['rule_records']} | {inspect} |"
        )
    lines.extend(["", "## Candidate Records", ""])
    for cluster in summary["clusters"]:
        lines.append(f"### {cluster['cluster']}")
        if cluster["sample_titles"]:
            lines.append("Titles: " + "; ".join(cluster["sample_titles"]))
        for item in cluster["active_locations"]:
            lines.append(f"- `{item['file']}:{item['line']}` {item['title']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--skills-dir", default=".agents/skills")
    parser.add_argument("--rules-file", default="AGENTS.md")
    parser.add_argument("--hooks-path", default=".codex/hooks")
    parser.add_argument("--line-threshold", type=int, default=100)
    parser.add_argument("--active-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    records = collect_records(root, args.skills_dir, include_archive=not args.active_only)
    summary = summarize(root, records, args)
    print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
