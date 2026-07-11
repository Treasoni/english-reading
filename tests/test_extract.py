from kaoyan_reading.extract import extract_reading_passages


SAMPLE = """
Part A
Directions: Read the following four texts.

Text 1

A history of long and effortless success can be a dreadful handicap, but, if properly handled, it may become a driving force.

When the United States entered just such a glowing period after the end of the Second World War, it had a market eight times larger than any competitor.

21. The U.S. achieved its predominance after World War II because
[A] it had made painstaking efforts towards this goal
[B] its domestic market was eight times larger than before
[C] the war had destroyed the economies of most potential competitors
[D] its workforce was unparalleled

22. What can be inferred from the passage?
[A] Success always causes failure.
[B] Competition may contribute to progress.
[C] Economic revival depends only on cooperation.
[D] History repeats itself exactly.

Text 2

Some experts argue that technology changes education, while others say schools change more slowly than expected.

26. The passage mainly discusses
[A] technology and education
[B] sports
[C] music
[D] tourism
"""


def test_extracts_text_sections_and_questions():
    passages = extract_reading_passages(SAMPLE, year="2000")

    assert len(passages) == 2
    assert passages[0].index == 1
    assert passages[0].title == "2000 Text 1"
    assert "Directions" not in passages[0].article
    assert len(passages[0].questions) == 2
    assert passages[0].questions[0].number == "21"
    assert passages[0].questions[0].options[2].label == "C"
    assert "destroyed" in passages[0].questions[0].options[2].text

