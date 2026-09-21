import re


NUMBERED_EVIDENCE_PATTERN = re.compile(
    r"Evidence\s+(\d+)",
    re.IGNORECASE,
)

EVIDENCE_ID_PATTERN = re.compile(
    r"Evidence\s+ID\s*:\s*([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)


def extract_evidence_references(
    answer: str,
    evidence: list[dict],
) -> list[int]:
    """
    Extract evidence references from an answer.

    Supports both:

        Evidence 1

    and:

        Evidence ID: cultfit-drhp-2026-chunk-201

    Returned references are always 1-based evidence positions
    so downstream evaluation remains compatible.
    """

    references = []

    # -------------------------------------------------
    # Numbered evidence references
    # -------------------------------------------------

    for match in NUMBERED_EVIDENCE_PATTERN.finditer(
        answer
    ):
        references.append(
            int(match.group(1))
        )

    # -------------------------------------------------
    # Full evidence IDs
    # -------------------------------------------------

    evidence_index = {
        item["id"]: index
        for index, item in enumerate(
            evidence,
            start=1,
        )
    }

    for match in EVIDENCE_ID_PATTERN.finditer(
        answer
    ):
        evidence_id = match.group(1)

        reference = evidence_index.get(
            evidence_id
        )

        if reference is not None:
            references.append(
                reference
            )

    return references


def validate_citations(
    answer: str,
    evidence: list[dict],
) -> dict:
    """
    Validate that cited evidence references actually exist.

    Supports both numbered references and full evidence IDs.
    """

    references = extract_evidence_references(
        answer,
        evidence,
    )

    valid_numbers = set(
        range(
            1,
            len(evidence) + 1,
        )
    )

    invalid_references = [
        reference
        for reference in references
        if reference not in valid_numbers
    ]

    return {
        "valid": len(
            invalid_references
        ) == 0,
        "references": references,
        "invalid_references": invalid_references,
    }