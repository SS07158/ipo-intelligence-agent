from app.retrieval.citation_validator import (
    extract_evidence_references,
    validate_citations,
)


def test_extract_evidence_references():
    answer = (
        "The company faces several risks "
        "(Evidence 1) and operational concerns "
        "(Evidence 3)."
    )

    assert extract_evidence_references(answer) == [
        1,
        3,
    ]


def test_valid_citations():
    evidence = [
        {"id": "chunk-1"},
        {"id": "chunk-2"},
        {"id": "chunk-3"},
    ]

    answer = "This is supported by Evidence 1 and Evidence 3."

    result = validate_citations(
        answer,
        evidence,
    )

    assert result["valid"] is True
    assert result["invalid_references"] == []


def test_invalid_citations():
    evidence = [
        {"id": "chunk-1"},
        {"id": "chunk-2"},
    ]

    answer = "This is supported by Evidence 7."

    result = validate_citations(
        answer,
        evidence,
    )

    assert result["valid"] is False
    assert result["invalid_references"] == [7]

def test_extract_evidence_id_reference():
    answer = (
        "The answer is supported by "
        "Evidence ID: 1."
    )

    assert extract_evidence_references(
        answer
    ) == [1]

def test_evidence_id_format():
    answer = (
        "The answer is supported by "
        "Evidence ID: 1."
    )

    assert extract_evidence_references(
        answer
    ) == [1]


def test_mixed_evidence_formats():
    answer = (
        "Evidence 1 supports this. "
        "Evidence ID: 3 also supports it."
    )

    assert extract_evidence_references(
        answer
    ) == [1, 3]