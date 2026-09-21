from evaluation.citation_support import (
    claim_numeric_supported,
    claim_supported_by_evidence,
)


def test_claim_supported():
    evidence = (
        "Revenue from operations was "
        "₹9,266.62 million in FY2024."
    )

    claim = (
        "Revenue from operations was "
        "₹9,266.62 million in FY2024."
    )

    assert claim_supported_by_evidence(
        claim,
        evidence,
    ) is True


def test_claim_not_supported():
    evidence = (
        "Revenue from operations was "
        "₹9,266.62 million in FY2024."
    )

    claim = (
        "Revenue from operations was "
        "₹17,206.06 million in FY2026."
    )

    assert claim_supported_by_evidence(
        claim,
        evidence,
    ) is False


def test_numeric_support():
    evidence = (
        "Revenue increased from "
        "₹9,266.62 million to "
        "₹17,206.06 million."
    )

    claim = (
        "Revenue increased from "
        "₹9,266.62 million to "
        "₹17,206.06 million."
    )

    assert claim_numeric_supported(
        claim,
        evidence,
    ) is True