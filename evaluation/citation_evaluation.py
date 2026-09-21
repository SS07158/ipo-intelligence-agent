def citation_points_to_evidence(
    evidence_id: str,
    evidence: list[dict],
) -> bool:
    """
    Check whether a cited evidence ID exists.
    """

    return any(
        item["id"] == evidence_id
        for item in evidence
    )


def citation_contains_claim(
    evidence_id: str,
    claim: str,
    evidence: list[dict],
) -> bool:
    """
    Simple lexical citation-support check.

    This is intentionally conservative and is only
    a baseline before we add semantic claim checking.
    """

    for item in evidence:
        if item["id"] != evidence_id:
            continue

        normalized_claim = (
            claim.lower()
            .replace(",", "")
        )

        normalized_text = (
            item["text"]
            .lower()
            .replace(",", "")
        )

        return normalized_claim in normalized_text

    return False