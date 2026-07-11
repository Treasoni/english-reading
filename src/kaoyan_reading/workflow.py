from pathlib import Path
from typing import Optional

from .extract import extract_reading_passages, write_passage_json
from .grammar import detect_grammar, render_grammar_notes
from .io import read_source
from .markdown import render_formatted_article
from .sentence_analysis import find_complex_sentences, render_sentence_prompt


def build_from_exam(source_path: str, output_dir: str, year: Optional[str] = None, sentence_limit: int = 8) -> int:
    text = read_source(source_path)
    passages = extract_reading_passages(text, year=year)
    base = Path(output_dir)
    for passage in passages:
        topic = _topic_name(year, passage.index)
        target = base / topic
        target.mkdir(parents=True, exist_ok=True)
        source_label = f"{year}年考研英语阅读 Text {passage.index}" if year else f"考研英语阅读 Text {passage.index}"

        write_passage_json(passage, target / "reading.json")
        (target / "formatted-article.md").write_text(
            render_formatted_article(passage, topic=topic, source=source_label),
            encoding="utf-8",
        )

        candidates = find_complex_sentences(passage.article, limit=sentence_limit)
        (target / "sentence-analysis-task.md").write_text(
            render_sentence_prompt(candidates, topic=topic),
            encoding="utf-8",
        )

        grammar = detect_grammar(passage.article)
        (target / "grammar-notes.md").write_text(
            render_grammar_notes(grammar, topic=topic, source=source_label),
            encoding="utf-8",
        )
    return len(passages)


def _topic_name(year: Optional[str], index: int) -> str:
    prefix = year or "exam"
    return f"{prefix}-text{index}"

