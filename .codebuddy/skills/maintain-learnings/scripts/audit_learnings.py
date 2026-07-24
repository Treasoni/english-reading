#!/usr/bin/env python3
"""Audit a vault's .learnings directory for recurring repair targets."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


ACTIVE_FILES = ("LEARNINGS.md", "ERRORS.md", "RULES.md")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$", re.MULTILINE)
ACTIVE_LINE_THRESHOLD = 100
SKILLS_ROOT = next(
    (directory for directory in (".agents", ".claude") if directory in Path(__file__).parts),
    ".agents",
)
IS_CODEX = SKILLS_ROOT == ".agents"
PROJECT_RULES = ["CODEBUDDY.md"] if IS_CODEX else ["CLAUDE.md", "CODEBUDDY.md"]
HOOK_CLUSTER = "codebuddy-hook" if IS_CODEX else "claude-hook"
HOOK_SOURCES = (
    [".codebuddy/hooks/read-learnings.sh", ".codebuddy/settings.json"]
    if IS_CODEX
    else [".claude/hooks/read-learnings.sh", ".claude/settings.json"]
)

KEYWORD_CLUSTERS = {
    "obsidian-markdown": [
        "obsidian",
        "markdown",
        "callout",
        "frontmatter",
        "yaml",
        "table",
        "表格",
        "标题",
        "wikilink",
    ],
    "user-interaction": [
        "askuserquestion",
        "other",
        "路径",
        "文件名",
        "用户反馈",
        "提问",
    ],
    HOOK_CLUSTER: [
        "hook",
        SKILLS_ROOT,
        "read-learnings",
        "上下文",
        "经验库提醒",
    ],
    "tooling": [
        "write 工具",
        "read 工具",
        "apply_patch",
        "sandbox",
        "权限",
    ],
}

ISSUE_WORDS = [
    "错误",
    "问题",
    "反馈",
    "纠正",
    "根因",
    "遗漏",
    "缺少",
    "跳过",
    "位置",
    "复发",
    "重复",
    "异常",
    "不能",
    "不得",
    "must",
    "error",
    "failed",
    "missing",
    "skip",
]

GENERIC_TITLES = {
    "会话概要",
    "改进记录",
    "修复",
    "预防措施",
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
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def discover_skills(root: Path) -> list[str]:
    skills_dir = root / SKILLS_ROOT / "skills"
    if not skills_dir.exists():
        return []
    return sorted(p.name for p in skills_dir.iterdir() if (p / "SKILL.md").exists())


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", value.lower())


def find_clusters(text: str, skills: Iterable[str]) -> list[str]:
    normalized = normalize(text)
    clusters: list[str] = []

    for skill in skills:
        skill_token = normalize(skill)
        if skill_token and skill_token in normalized:
            clusters.append(skill)

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
    if not matches:
        return [
            Record(
                file=display_path,
                line=1,
                title=path.name,
                text=text,
                active=active,
                kind=kind,
                clusters=find_clusters(text, skills),
            )
        ]

    records: list[Record] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        if len(block) < 80 and not any(word in block.lower() for word in ISSUE_WORDS):
            continue
        title = match.group(2).strip()
        if kind != "rules" and title in GENERIC_TITLES:
            continue
        if kind != "rules" and not any(word in block.lower() for word in ISSUE_WORDS):
            continue
        records.append(
            Record(
                file=display_path,
                line=line_number(text, start),
                title=title,
                text=block,
                active=active,
                kind=kind,
                clusters=find_clusters(block, skills),
            )
        )
    return records


def collect_records(root: Path, include_archive: bool) -> list[Record]:
    skills = discover_skills(root)
    learnings_dir = root / ".learnings"
    records: list[Record] = []

    for name in ACTIVE_FILES:
        path = learnings_dir / name
        records.extend(split_records(path, f".learnings/{name}", True, skills))

    if include_archive:
        archive_dir = learnings_dir / "archive"
        if archive_dir.exists():
            for path in sorted(archive_dir.glob("*.md")):
                records.extend(
                    split_records(
                        path,
                        f".learnings/archive/{path.name}",
                        False,
                        skills,
                    )
                )

    return records


def active_line_counts(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    learnings_dir = root / ".learnings"
    for name in ACTIVE_FILES:
        text = read_text(learnings_dir / name)
        counts[f".learnings/{name}"] = len(text.splitlines()) if text else 0
    return counts


def source_candidates(root: Path, cluster: str) -> list[str]:
    candidates: list[str] = []
    skill_path = root / SKILLS_ROOT / "skills" / cluster / "SKILL.md"
    if skill_path.exists():
        candidates.append(f"{SKILLS_ROOT}/skills/{cluster}/SKILL.md")
        ref_path = root / SKILLS_ROOT / "skills" / cluster / "references"
        if ref_path.exists():
            candidates.append(f"{SKILLS_ROOT}/skills/{cluster}/references/")

    if cluster == "obsidian-markdown":
        candidates.extend([*PROJECT_RULES, f"{SKILLS_ROOT}/skills/obsidian-markdown/"])
    elif cluster == "user-interaction":
        candidates.extend(PROJECT_RULES)
    elif cluster == HOOK_CLUSTER:
        candidates.extend(HOOK_SOURCES)
    elif cluster == "tooling":
        candidates.extend([*PROJECT_RULES, f"{SKILLS_ROOT}/skills/"])
    elif cluster == "general":
        candidates.extend([*PROJECT_RULES, ".learnings/RULES.md"])

    return list(dict.fromkeys(candidates))


def summarize(root: Path, records: list[Record]) -> dict:
    line_counts = active_line_counts(root)
    cluster_records: dict[str, list[Record]] = defaultdict(list)
    for record in records:
        for cluster in record.clusters:
            cluster_records[cluster].append(record)

    clusters = []
    for cluster, items in cluster_records.items():
        active_count = sum(1 for item in items if item.active and item.kind != "rules")
        total_count = sum(1 for item in items if item.kind != "rules")
        rule_count = sum(1 for item in items if item.kind == "rules")
        repeated = active_count >= 2 or total_count >= 3 or (rule_count > 0 and active_count > 0)
        over_threshold = any(count > ACTIVE_LINE_THRESHOLD for count in line_counts.values())
        if not repeated and active_count == 0:
            continue
        titles = Counter(item.title for item in items)
        clusters.append(
            {
                "cluster": cluster,
                "active_records": active_count,
                "total_records": total_count,
                "rule_records": rule_count,
                "severity": "high" if repeated else "medium" if over_threshold else "low",
                "sources_to_inspect": source_candidates(root, cluster),
                "sample_titles": [title for title, _ in titles.most_common(5)],
                "active_locations": [
                    {"file": item.file, "line": item.line, "title": item.title}
                    for item in items
                    if item.active and item.kind != "rules"
                ][:8],
                "rule_locations": [
                    {"file": item.file, "line": item.line, "title": item.title}
                    for item in items
                    if item.kind == "rules"
                ][:8],
            }
        )

    clusters.sort(
        key=lambda item: (
            {"high": 2, "medium": 1, "low": 0}[item["severity"]],
            item["active_records"],
            item["total_records"],
        ),
        reverse=True,
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "active_line_counts": line_counts,
        "over_threshold": {
            file: count
            for file, count in line_counts.items()
            if count > ACTIVE_LINE_THRESHOLD
        },
        "clusters": clusters,
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Learnings Audit Report",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "## Active File Health",
        "",
    ]

    for file, count in summary["active_line_counts"].items():
        marker = "OVER" if count > ACTIVE_LINE_THRESHOLD else "ok"
        lines.append(f"- `{file}`: {count} lines ({marker})")

    if summary["over_threshold"]:
        lines.extend(
            [
                "",
                f"Threshold: {ACTIVE_LINE_THRESHOLD} lines. Over-threshold files should be audited before blind compression.",
            ]
        )

    lines.extend(["", "## Hotspot Clusters", ""])

    if not summary["clusters"]:
        lines.append("- No recurring clusters found.")
        return "\n".join(lines) + "\n"

    lines.append("| Cluster | Severity | Active | Total | Rules | Inspect |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for cluster in summary["clusters"]:
        inspect = ", ".join(f"`{item}`" for item in cluster["sources_to_inspect"]) or f"`{PROJECT_RULES[0]}`"
        lines.append(
            f"| `{cluster['cluster']}` | {cluster['severity']} | "
            f"{cluster['active_records']} | {cluster['total_records']} | "
            f"{cluster['rule_records']} | {inspect} |"
        )

    lines.extend(["", "## Candidate Records", ""])
    for cluster in summary["clusters"]:
        lines.append(f"### {cluster['cluster']}")
        if cluster["sample_titles"]:
            lines.append("Titles: " + "; ".join(cluster["sample_titles"]))
        if cluster["active_locations"]:
            for item in cluster["active_locations"]:
                lines.append(f"- `{item['file']}:{item['line']}` {item['title']}")
        else:
            lines.append("- No active records; only archive history contributed to this cluster.")
        if cluster.get("rule_locations"):
            lines.append("Rules already present:")
            for item in cluster["rule_locations"]:
                lines.append(f"- `{item['file']}:{item['line']}` {item['title']}")
        lines.append("")

    lines.extend(
        [
            "## Maintenance Rule",
            "",
            "Only archive active records after the corresponding skill, template, hook, or project rule has been fixed and verified.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Vault root. Defaults to current directory.")
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Ignore .learnings/archive when calculating recurrence.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    records = collect_records(root, include_archive=not args.active_only)
    summary = summarize(root, records)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
