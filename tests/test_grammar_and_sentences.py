from kaoyan_reading.grammar import detect_grammar
from kaoyan_reading.sentence_analysis import find_complex_sentences


ARTICLE = """
When the United States entered just such a glowing period after the end of the Second World War,
it had a market eight times larger than any competitor, giving its industries unparalleled economies of scale.

For a while it looked as though the making of semiconductors, which America had invented and which sat at the heart
of the new computer age, was going to be the next casualty.
"""


def test_finds_complex_sentence_candidates():
    candidates = find_complex_sentences(ARTICLE, limit=3)

    assert candidates
    assert candidates[0].score >= 4
    assert any("从句线索" in reason for reason in candidates[0].reasons)


def test_detects_grammar_hits():
    grouped = detect_grammar(ARTICLE)

    assert "从句 (Clauses)" in grouped
    assert "非谓语动词 (Non-finite Verbs)" in grouped
    assert any("which" in hit.example for hit in grouped["从句 (Clauses)"])

