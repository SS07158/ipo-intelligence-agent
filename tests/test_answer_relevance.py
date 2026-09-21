import pytest

from evaluation.answer_relevance import (
    keyword_relevance,
)


def test_relevant_answer():
    score = keyword_relevance(
        "What industry does the company operate in?",
        (
            "The company operates in the fitness "
            "and active lifestyle industry."
        ),
    )

    assert score >= 0.2


def test_unrelated_answer():
    score = keyword_relevance(
        "What industry does the company operate in?",
        "The company's revenue increased.",
    )

    assert score < 0.3