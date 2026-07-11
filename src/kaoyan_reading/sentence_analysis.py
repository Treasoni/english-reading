import re
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List

from .io import normalize_text

CLAUSE_MARKERS = {
    "although",
    "because",
    "if",
    "when",
    "while",
    "unless",
    "whereas",
    "as",
    "since",
    "that",
    "which",
    "who",
    "whom",
    "whose",
    "where",
    "whether",
    "what",
}


@dataclass
class SentenceCandidate:
    sentence: str
    score: int
    reasons: List[str]


def find_complex_sentences(text: str, limit: int = 8) -> List[SentenceCandidate]:
    candidates = []
    for sentence in split_sentences(strip_markdown(text)):
        words = re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", sentence)
        if len(words) < 18:
            continue
        score, reasons = score_sentence(sentence, len(words))
        if score >= 4:
            candidates.append(SentenceCandidate(sentence=sentence, score=score, reasons=reasons))
    candidates.sort(key=lambda item: (-item.score, -len(item.sentence)))
    return candidates[:limit]


def render_sentence_prompt(candidates: Iterable[SentenceCandidate], topic: str) -> str:
    today = date.today().isoformat()
    lines = [
        "---",
        f'title: "{topic} 长难句分析任务"',
        "type: sentence-analysis-task",
        f"topic: {topic}",
        "tags:",
        "  - english-reading",
        "  - sentence-analysis",
        f"created: {today}",
        f"updated: {today}",
        "---",
        "",
        f"# {topic} 长难句分析任务",
        "",
        "请使用 `analyze-sentence` 技能分析以下候选句，并把结果插入 `formatted-article.md` 的原文对应段落之后。",
        "",
        "输出要求：每个 `> [!abstract]- 长难句分析` 块第一行必须是 `> **原句**：...`；callout 内所有表格前必须留空行。",
        "",
    ]
    for index, candidate in enumerate(candidates, start=1):
        reasons = "、".join(candidate.reasons)
        lines.extend(
            [
                f"## 句子 {index}",
                "",
                f"> {candidate.sentence}",
                "",
                f"- 复杂度分数：{candidate.score}",
                f"- 命中线索：{reasons}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def split_sentences(text: str) -> List[str]:
    normalized = re.sub(r"\s+", " ", normalize_text(text))
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", normalized)
    return [part.strip() for part in parts if part.strip()]


def score_sentence(sentence: str, word_count: int) -> tuple:
    lower = sentence.lower()
    score = 0
    reasons = []
    if word_count >= 28:
        score += 3
        reasons.append("词数较长")
    elif word_count >= 22:
        score += 2
        reasons.append("词数中长")
    comma_count = sentence.count(",")
    if comma_count >= 2:
        score += 2
        reasons.append("多重逗号分隔")
    elif comma_count == 1:
        score += 1
        reasons.append("含逗号分隔")
    if ";" in sentence or ":" in sentence:
        score += 1
        reasons.append("含分号/冒号")
    markers = sorted(marker for marker in CLAUSE_MARKERS if re.search(rf"\b{marker}\b", lower))
    if markers:
        score += min(3, len(markers))
        reasons.append("从句线索 " + "/".join(markers[:4]))
    if re.search(r"\bto\s+[a-z]+", lower):
        score += 1
        reasons.append("不定式结构")
    if re.search(r"\b(?:giving|making|leading|including|according|compared)\b", lower):
        score += 1
        reasons.append("非谓语/分词结构")
    return score, reasons or ["长句候选"]


def strip_markdown(text: str) -> str:
    text = re.sub(r"^---.*?---", "", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"==([^=]+)==", r"\1", text)
    text = re.sub(r"^#+\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    return text

