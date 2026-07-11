from datetime import date
from typing import Iterable

from .io import paragraphs
from .models import Passage, Question


def render_formatted_article(passage: Passage, topic: str, source: str = "考研英语真题") -> str:
    today = date.today().isoformat()
    body = [
        "---",
        f'title: "{passage.title}"',
        "type: article",
        f"topic: {topic}",
        "tags:",
        "  - english-reading",
        "  - formatted-article",
        f"created: {today}",
        f"updated: {today}",
        "sources:",
        f'  - "{source}"',
        "---",
        "",
        f"# {passage.title}",
        "",
    ]

    for index, paragraph in enumerate(paragraphs(passage.article), start=1):
        body.append(f"**({index})** {paragraph}")
        body.append("")

    if passage.questions:
        body.extend(["---", "", "## 阅读理解 Questions", ""])
        body.extend(_render_questions(passage.questions))

    return "\n".join(body).rstrip() + "\n"


def _render_questions(questions: Iterable[Question]) -> list:
    lines = []
    for question in questions:
        lines.append(f"**{question.number}.** {question.stem}")
        lines.append("")
        for option in question.options:
            lines.append(f"- [{option.label}] {option.text}")
        lines.append("")
    return lines

