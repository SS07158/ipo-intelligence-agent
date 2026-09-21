import re

from evaluation.answer_metrics import normalize_numeric


def normalize_text(text: str) -> str:
    """
    Normalize text for simple lexical comparison.
    """
    return re.sub(
        r"\s+",
        " ",
        text.lower(),
    ).strip()


def claim_supported_by_evidence(
    claim: str,
    evidence_text: str,
) -> bool:
    """
    Conservative baseline check.

    Returns True when the important normalized
    claim text appears in the evidence.
    """
    claim_normalized = normalize_text(
        claim
    )

    evidence_normalized = normalize_text(
        evidence_text
    )

    return claim_normalized in evidence_normalized


def extract_numbers(text: str) -> set[float]:
    """
    Extract normalized numeric values from text.

    Monetary values expressed in crore are converted
    to INR million so equivalent values compare equal.

    Example:
        950 crore == 9500 million
    """
    number_pattern = r"\d[\d,]*(?:\.\d+)?"

    normalized = set()

    for match in re.finditer(
        number_pattern,
        text,
    ):
        raw_number = match.group(0)

        try:
            value = normalize_numeric(
                raw_number
            )
        except (ValueError, TypeError):
            continue

        start = match.start()
        end = match.end()

        context_after = text[
            end:end + 20
        ].lower()

        context_before = text[
            max(0, start - 20):start
        ].lower()

        # 1 crore = 10 million
        if re.search(
            r"\bcrore(s)?\b",
            context_after,
        ):
            value *= 10

        elif re.search(
            r"\bcrore(s)?\b",
            context_before,
        ):
            value *= 10

        normalized.add(value)

    return normalized


def claim_numeric_supported(
    claim: str,
    evidence_text: str,
) -> bool:
    """
    Check whether numeric values present in the claim
    are also supported by the evidence.

    Equivalent monetary units such as crore and million
    are normalized before comparison.
    """
    claim_numbers = extract_numbers(
        claim
    )

    if not claim_numbers:
        return False

    evidence_numbers = extract_numbers(
        evidence_text
    )

    return claim_numbers.issubset(
        evidence_numbers
    )