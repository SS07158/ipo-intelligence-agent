import re


def answer_value_retrieved(
    gold_answer: str,
    retrieved_results: list[dict],
) -> bool:
    """
    Check whether the gold factual value appears
    in the retrieved evidence.
    """
    if gold_answer is None:
        return False

    target = gold_answer.replace(
        ",",
        "",
    )

    for result in retrieved_results:
        text = result["text"].replace(
            ",",
            "",
        )

        if target in text:
            return True

    return False


def evidence_section_hit(
    expected_sections: list[str],
    retrieved_results: list[dict],
) -> bool:
    """
    Check whether any retrieved result belongs to
    an expected evidence section.
    """
    expected = set(
        expected_sections
    )

    for result in retrieved_results:
        section = result["metadata"].get(
            "section"
        )

        if section in expected:
            return True

    return False


def normalize_numeric(
    text: str,
) -> float:
    """
    Convert a formatted numeric string into a float.
    """
    cleaned = re.sub(
        r"[^\d.]",
        "",
        text,
    )

    if not cleaned:
        raise ValueError(
            f"Could not parse numeric value: {text}"
        )

    return float(cleaned)


def answer_contains_value(
    expected_value: str,
    answer: str,
) -> bool:
    """
    Check whether the expected numeric value appears
    in the answer, allowing formatting differences.
    """
    expected = normalize_numeric(
        expected_value
    )

    actual_numbers = re.findall(
        r"\d[\d,]*(?:\.\d+)?",
        answer,
    )

    for number in actual_numbers:
        try:
            actual = normalize_numeric(
                number
            )
        except ValueError:
            continue

        if actual == expected:
            return True

    return False


def answer_contains_points(
    expected_points: list[str],
    answer: str,
) -> dict:
    """
    Check whether expected qualitative concepts
    are represented in the generated answer.

    Supports controlled aliases so that semantically
    equivalent terminology is treated as a match.
    """

    normalized_answer = answer.lower()

    aliases = {
        "third-party payment systems": [
            "third-party payment systems",
            "third-party payment gateway",
            "third-party payment gateway providers",
            "payment gateway",
            "payment gateways",
            "upi infrastructure",
            "payment mechanisms",
        ],
        "expansion and operational risks": [
            "expansion and operational risks",
            "expansion and capital expenditure risks",
            "expansion risks",
            "expansion plans",
            "opening new fitness centers",
            "opening new fitness centres",
        ],
        "vendor": [
            "vendor",
            "vendors",
            "third-party vendor",
            "third-party vendors",
            "supplier",
            "suppliers",
        ],
        "supply chain": [
            "supply chain",
            "logistics network",
            "logistics operations",
            "logistics partners",
        ],
    }

    matched = []
    missing = []

    for point in expected_points:

        normalized_point = (
            point.lower().strip()
        )

        candidate_terms = aliases.get(
            normalized_point,
            [normalized_point],
        )

        if any(
            term in normalized_answer
            for term in candidate_terms
        ):
            matched.append(point)
        else:
            missing.append(point)

    total = len(expected_points)

    score = (
        len(matched) / total
        if total
        else 1.0
    )

    return {
        "matched": matched,
        "missing": missing,
        "score": score,
    }