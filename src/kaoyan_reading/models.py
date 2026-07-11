from dataclasses import dataclass, field
from typing import List


@dataclass
class Option:
    label: str
    text: str


@dataclass
class Question:
    number: str
    stem: str
    options: List[Option] = field(default_factory=list)


@dataclass
class Passage:
    index: int
    title: str
    article: str
    questions: List[Question] = field(default_factory=list)

