from pathlib import Path

from kaoyan_reading.workflow import build_from_exam


SAMPLE = """
Text 1

When the United States entered a glowing period after the war, it had a market larger than any competitor, giving its industries economies of scale.

21. The passage mainly discusses
[A] economic change
[B] sports
[C] music
[D] food

Text 2

Some people believe that standardized tests are fair, while others argue that they reward narrow training rather than understanding.

26. The passage mainly discusses
[A] testing and education
[B] travel
[C] farming
[D] painting
"""


def test_build_from_exam_with_parallel_jobs(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text(SAMPLE, encoding="utf-8")

    count = build_from_exam(str(source), str(tmp_path / "out"), year="2000", jobs=2)

    assert count == 2
    assert (tmp_path / "out" / "2000-text1" / "reading.json").exists()
    assert (tmp_path / "out" / "2000-text1" / "sentence-analysis-task.md").exists()
    assert (tmp_path / "out" / "2000-text2" / "grammar-notes.md").exists()
