from evaluation.citation_evaluation import (
    citation_contains_claim,
    citation_points_to_evidence,
)


def test_citation_points_to_existing_evidence():
    evidence = [
        {
            "id": "chunk-1",
            "text": "Revenue was 9266.62 million.",
        }
    ]

    assert citation_points_to_evidence(
        "chunk-1",
        evidence,
    ) is True


def test_invalid_citation():
    evidence = [
        {
            "id": "chunk-1",
            "text": "Revenue was 9266.62 million.",
        }
    ]

    assert citation_points_to_evidence(
        "chunk-9",
        evidence,
    ) is False


def test_citation_supports_claim():
    evidence = [
        {
            "id": "chunk-1",
            "text": "Revenue was 9266.62 million.",
        }
    ]

    assert citation_contains_claim(
        "chunk-1",
        "9266.62",
        evidence,
    ) is True


def test_citation_does_not_support_claim():
    evidence = [
        {
            "id": "chunk-1",
            "text": "Revenue was 9266.62 million.",
        }
    ]

    assert citation_contains_claim(
        "chunk-1",
        "17206.06",
        evidence,
    ) is False