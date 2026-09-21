from evaluation.answer_metrics import (
    answer_value_retrieved,
    evidence_section_hit,
    answer_contains_value,
)


def test_answer_value_retrieved():
    results = [
        {
            "text": (
                "Revenue from operations was "
                "₹9,266.62 million."
            )
        }
    ]

    assert answer_value_retrieved(
        "9266.62",
        results,
    ) is True


def test_answer_value_not_retrieved():
    results = [
        {
            "text": (
                "Revenue increased significantly."
            )
        }
    ]

    assert answer_value_retrieved(
        "9266.62",
        results,
    ) is False

def test_evidence_section_hit():
    results = [
        {
            "metadata": {
                "section": "OTHER"
            }
        },
        {
            "metadata": {
                "section": "INTERNAL RISKS"
            }
        },
    ]

    assert evidence_section_hit(
        ["INTERNAL RISKS"],
        results,
    ) is True


def test_evidence_section_miss():
    results = [
        {
            "metadata": {
                "section": "OTHER"
            }
        }
    ]

    assert evidence_section_hit(
        ["INTERNAL RISKS"],
        results,
    ) is False

def test_answer_contains_value():
    answer = (
        "Revenue was ₹9,266.62 million."
    )

    assert answer_contains_value(
        "9266.62",
        answer,
    ) is True


def test_answer_contains_large_value():
    answer = (
        "Revenue was ₹17,206.06 million."
    )

    assert answer_contains_value(
        "17206.06",
        answer,
    ) is True


def test_answer_contains_fresh_issue():
    answer = (
        "The fresh issue is "
        "₹9,500.00 million."
    )

    assert answer_contains_value(
        "9500",
        answer,
    ) is True

def test_formatted_numeric_values():
    assert answer_contains_value(
        "950",
        "The issue size is ₹950.00 crore.",
    )

    assert answer_contains_value(
        "9500",
        "The fresh issue aggregates up to ₹9,500.00 million.",
    )