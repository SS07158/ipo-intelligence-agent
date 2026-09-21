import re
from typing import Any


def _normalize_text(
    text: str,
) -> str:
    """
    Normalize whitespace while preserving the
    numerical content of the document.
    """

    return " ".join(
        text.split()
    )


def _parse_number(
    value: str,
) -> float:
    """
    Convert numbers containing commas into float.
    """

    return float(
        value.replace(",", "")
        .strip()
    )


def extract_fresh_issue(
    text: str,
) -> float | None:
    """
    Extract fresh issue size from the DRHP.

    Returns:
        Value in INR million.
    """

    normalized = _normalize_text(
        text
    )

    patterns = [
        r"fresh issue.*?aggregating up to ₹?\s*"
        r"([0-9,]+(?:\.[0-9]+)?)\s*million",

        r"fresh issue.*?aggregating up to"
        r"\s*₹?\s*([0-9,]+(?:\.[0-9]+)?)"
        r"\s*million",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        )

        if match:
            return _parse_number(
                match.group(1)
            )

    return None


def extract_ofs_shares(
    text: str,
) -> int | None:
    """
    Extract the number of shares offered for sale.
    """

    normalized = _normalize_text(
        text
    )

    patterns = [
        r"offer for sale.*?"
        r"([0-9]{1,3}(?:,[0-9]{3})+)"
        r"\s*(?:equity )?shares",

        r"offer for sale.*?"
        r"([0-9]{6,})"
        r"\s*(?:equity )?shares",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        )

        if match:
            return int(
                match.group(1)
                .replace(",", "")
            )

    return None


def extract_ipo_terms(
    text: str,
) -> dict[str, Any]:
    """
    Extract and normalize structured IPO terms.
    """

    fresh_issue_million = (
        extract_fresh_issue(text)
    )

    return {
        "fresh_issue": million_to_crore(
            fresh_issue_million
        ),
        "offer_for_sale_shares": (
            extract_ofs_shares(text)
        ),
    }


def million_to_crore(
    value: float | None,
) -> float | None:
    """
    Convert INR million to INR crore.
    """

    if value is None:
        return None

    return value / 10