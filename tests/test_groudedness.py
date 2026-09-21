from evaluation.groundness import (
    numeric_groundedness,
)


def test_numeric_groundedness():
    evidence = [
        {
            "text": (
                "Revenue was ₹9,266.62 million."
            )
        }
    ]

    answer = (
        "Revenue was ₹9,266.62 million."
    )

    assert numeric_groundedness(
        answer,
        evidence,
    ) is True


def test_numeric_hallucination():
    evidence = [
        {
            "text": (
                "Revenue was ₹9,266.62 million."
            )
        }
    ]

    answer = (
        "Revenue was ₹12,000 million."
    )

    assert numeric_groundedness(
        answer,
        evidence,
    ) is False