import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from .io import normalize_text, paragraphs
from .models import Option, Passage, Question

TEXT_MARKER = re.compile(r"(?im)^\s*(?:Text|Passage)\s+([1-5])\b[^\n]*$")
QUESTION_START = re.compile(r"(?m)^\s*(\d{1,3})[\.\u3001]\s+(.+)$")
OPTION_START = re.compile(r"^\s*(?:[\[\(]?([A-D])[\]\)\.、])\s*(.+)$")


def extract_reading_passages(text: str, year: Optional[str] = None) -> List[Passage]:
    normalized = normalize_text(text)
    sections = _split_sections(normalized)
    passages = []
    for fallback_index, (index, block) in enumerate(sections, start=1):
        passage_index = index or fallback_index
        article, questions = _split_article_and_questions(block)
        title = _make_title(year, passage_index)
        passages.append(Passage(index=passage_index, title=title, article=article, questions=questions))
    return passages


def write_passage_json(passage: Passage, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(passage), ensure_ascii=False, indent=2), encoding="utf-8")


def _split_sections(text: str) -> Sequence[Tuple[Optional[int], str]]:
    matches = list(TEXT_MARKER.finditer(text))
    if not matches:
        return [(None, text)]

    sections = []
    for position, match in enumerate(matches):
        start = match.end()
        end = matches[position + 1].start() if position + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        if block:
            sections.append((int(match.group(1)), block))
    return sections


def _split_article_and_questions(block: str) -> Tuple[str, List[Question]]:
    question_offsets = _find_question_offsets(block)
    if not question_offsets:
        return _clean_article(block), []

    article = _clean_article(block[: question_offsets[0]])
    question_text = block[question_offsets[0] :].strip()
    return article, _parse_questions(question_text)


def _find_question_offsets(block: str) -> List[int]:
    offsets = []
    for match in QUESTION_START.finditer(block):
        tail = block[match.start() :]
        next_question = QUESTION_START.search(tail, match.end() - match.start())
        sample_end = next_question.start() if next_question else min(len(tail), 1200)
        sample = tail[:sample_end]
        option_count = sum(1 for line in sample.splitlines() if OPTION_START.match(line))
        if option_count >= 2:
            offsets.append(match.start())
    return offsets


def _parse_questions(text: str) -> List[Question]:
    starts = list(QUESTION_START.finditer(text))
    questions = []
    for position, start in enumerate(starts):
        end = starts[position + 1].start() if position + 1 < len(starts) else len(text)
        chunk = text[start.start() : end]
        question = _parse_question_chunk(chunk)
        if question:
            questions.append(question)
    return questions


def _parse_question_chunk(chunk: str) -> Optional[Question]:
    lines = [line.strip() for line in chunk.splitlines() if line.strip()]
    if not lines:
        return None
    first = QUESTION_START.match(lines[0])
    if not first:
        return None

    number = first.group(1)
    stem_parts = [first.group(2).strip()]
    options: List[Option] = []
    current_option: Optional[Option] = None

    for line in lines[1:]:
        option = OPTION_START.match(line)
        if option:
            current_option = Option(label=option.group(1), text=option.group(2).strip())
            options.append(current_option)
        elif current_option:
            current_option.text = f"{current_option.text} {line}".strip()
        else:
            stem_parts.append(line)

    return Question(number=number, stem=" ".join(stem_parts), options=options)


def _clean_article(text: str) -> str:
    ignored_patterns = [
        r"(?i)^part\s+[a-d]\b.*$",
        r"(?i)^directions?:.*$",
        r"(?i)^read\s+the\s+following.*$",
        r"(?i)^choose\s+the\s+best.*$",
    ]
    cleaned = []
    for paragraph in paragraphs(text):
        if any(re.match(pattern, paragraph) for pattern in ignored_patterns):
            continue
        cleaned.append(paragraph)
    return "\n\n".join(cleaned).strip()


def _make_title(year: Optional[str], index: int) -> str:
    if year:
        return f"{year} Text {index}"
    return f"Text {index}"

