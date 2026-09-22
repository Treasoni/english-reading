#!/usr/bin/env python3
# Assemble the final 精读笔记 for 2015 Passage 3 from intermediate sources.
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))


def read_lines(name):
    with open(os.path.join(BASE, name), encoding="utf-8") as fh:
        return fh.read().split("\n")


def slice_join(name, start, end):
    """1-indexed inclusive slice, stripped of trailing blanks."""
    lines = read_lines(name)[start - 1:end]
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def normalize(block):
    """Ensure a blank line before headings and table rows (RULES.md)."""
    out = []
    for line in block.split("\n"):
        stripped = line.lstrip()
        needs_gap = stripped.startswith("#") or stripped.startswith("|")
        if needs_gap and out and out[-1].strip():
            out.append("")
        out.append(line)
    return "\n".join(out)


HEAD = slice_join("_gen-head.md", 1, 10 ** 6)
TAIL = slice_join("_gen-tail.md", 1, 10 ** 6)

HEAD = normalize(HEAD)
TAIL = normalize(TAIL)

ARTICLE = slice_join("formatted-article.md", 14, 380)
QUESTIONS = slice_join("formatted-article.md", 385, 417)
TRANSLATION = slice_join("translation.md", 16, 10 ** 6)
GRAMMAR = slice_join("grammar-notes.md", 37, 10 ** 6)
COLLOCATION = slice_join("固定搭配与词组笔记.md", 38, 10 ** 6)

for name, block in (("ARTICLE", ARTICLE), ("QUESTIONS", QUESTIONS),
                    ("TRANSLATION", TRANSLATION), ("GRAMMAR", GRAMMAR),
                    ("COLLOCATION", COLLOCATION)):
    assert block.strip(), "empty block: " + name

parts = [
    HEAD,
    "",
    "## 文章原文",
    "",
    ARTICLE,
    "",
    "---",
    "",
    "## 题目",
    "",
    QUESTIONS,
    "",
    "---",
    "",
    "## 翻译对照",
    "",
    TRANSLATION,
    "",
    "---",
    "",
    "## 语法要点",
    "",
    GRAMMAR,
    "",
    "---",
    "",
    "## 固定搭配与词组",
    "",
    COLLOCATION,
    "",
    "---",
    "",
    "<!-- VOCABULARY_SLOT -->",
    "",
    "---",
    "",
    TAIL,
    "",
]

target = os.path.join(ROOT, "2015阅读", "2015-passage3-office-speak-精读笔记.md")
with open(target, "w", encoding="utf-8") as fh:
    fh.write("\n".join(parts))

print("written:", target)
print("lines:", len(parts) and sum(p.count("\n") + 1 for p in parts))
print("callouts:", sum(1 for p in parts if "[!abstract]- 长难句分析" in p
                      for _ in [0]) or "\n".join(parts).count("> [!abstract]- 长难句分析"))