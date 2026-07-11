import re
from dataclasses import dataclass
from datetime import date
from typing import Dict, List

from .sentence_analysis import split_sentences, strip_markdown


@dataclass
class GrammarHit:
    category: str
    structure: str
    usage: str
    example: str


PATTERNS = [
    (
        "从句 (Clauses)",
        re.compile(r"\b(which|that|who|whom|whose)\b", re.I),
        "定语从句/关系从句",
        "补充或限定名词信息",
    ),
    (
        "从句 (Clauses)",
        re.compile(r"\b(although|because|if|when|while|whereas|unless|as|since)\b", re.I),
        "状语从句",
        "表示时间、原因、条件、让步或对比",
    ),
    (
        "名词性从句 (Noun Clauses)",
        re.compile(r"\b(whether|what|that)\b.+\b(is|was|means|suggests|shows|believes?)\b", re.I),
        "名词性从句",
        "充当主语、宾语、表语或同位语",
    ),
    (
        "非谓语动词 (Non-finite Verbs)",
        re.compile(r"\bto\s+[a-z]+", re.I),
        "to V 不定式",
        "表示目的、结果、后置定语或补足语",
    ),
    (
        "非谓语动词 (Non-finite Verbs)",
        re.compile(r"(?:,\s*[a-z]+ing\b|\b[a-z]+ing\s+(?:of|to|from|with|by)\b)", re.I),
        "V-ing 分词/动名词",
        "表示主动、进行、结果、伴随或名词化动作",
    ),
    (
        "语态 (Voice)",
        re.compile(r"\b(?:is|are|was|were|be|been|being|had been|has been|have been)\s+[a-z]+ed\b", re.I),
        "be + V-ed",
        "被动语态或过去分词表状态",
    ),
    (
        "倒装与强调 (Inversion & Emphasis)",
        re.compile(r"\bit\s+(?:is|was)\s+.+?\bthat\b", re.I),
        "It is/was ... that",
        "强调句或形式主语结构，需要结合语义判断",
    ),
    (
        "介词与连词 (Prepositions & Conjunctions)",
        re.compile(r"\b(?:in spite of|because of|due to|according to|rather than|instead of|in terms of)\b", re.I),
        "介词短语/连接结构",
        "连接论证关系或承担状语功能",
    ),
]


def detect_grammar(text: str, max_examples_per_category: int = 6) -> Dict[str, List[GrammarHit]]:
    grouped: Dict[str, List[GrammarHit]] = {}
    seen = set()
    for sentence in split_sentences(strip_markdown(text)):
        for category, pattern, structure, usage in PATTERNS:
            if not pattern.search(sentence):
                continue
            key = (category, structure, sentence)
            if key in seen:
                continue
            seen.add(key)
            grouped.setdefault(category, [])
            if len(grouped[category]) < max_examples_per_category:
                grouped[category].append(
                    GrammarHit(category=category, structure=structure, usage=usage, example=sentence)
                )
    return grouped


def render_grammar_notes(grouped: Dict[str, List[GrammarHit]], topic: str, source: str) -> str:
    today = date.today().isoformat()
    concepts = [category.split(" ")[0] for category in grouped.keys()]
    lines = [
        "---",
        f'title: "{topic} 语法整理"',
        "type: grammar-reference",
        f"topic: {topic}",
        "tags:",
        "  - english-reading",
        "  - grammar",
        "  - reference",
        "difficulty: intermediate",
        f"created: {today}",
        f"updated: {today}",
        "sources:",
        f'  - "{source}"',
        "concepts:",
    ]
    if concepts:
        for concept in concepts:
            lines.append(f"  - {concept}")
    else:
        lines.append("  - 待补充")

    lines.extend(["---", "", f"# {topic} 语法要点整理", ""])

    if not grouped:
        lines.extend(["> [!note]", "> 暂未从文本中识别出高频语法结构，请手动补充语法笔记。", ""])
        return "\n".join(lines).rstrip() + "\n"

    for category, hits in grouped.items():
        lines.extend(["---", "", f"### {category}", ""])
        lines.extend(_category_tip(category))
        lines.extend(["| 结构 | 用法 | 例句 |", "|------|------|------|"])
        for hit in hits:
            lines.append(f"| **{hit.structure}** | {hit.usage} | {hit.example} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _category_tip(category: str) -> List[str]:
    if "从句" in category:
        return [
            "> [!tip] 解题技巧",
            "> 先找主句主干，再判断从句在句中充当定语、状语还是名词性成分。",
            "",
        ]
    if "非谓语" in category:
        return [
            "> [!tip] 解题技巧",
            "> 判断非谓语时先找逻辑主语，再看主动/被动和动作先后。",
            "",
        ]
    if "语态" in category:
        return [
            "> [!warning] 翻译注意",
            "> 英文被动语态翻译成中文时不必机械保留“被”，应按中文习惯转述。",
            "",
        ]
    return [
        "> [!note]",
        "> 以下条目由本地规则从原文中抽取，适合作为人工精修或 Agent 继续整理的草稿。",
        "",
    ]
