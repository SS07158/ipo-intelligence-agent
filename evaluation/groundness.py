import re

from evaluation.answer_metrics import normalize_numeric


STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "was",
    "were",
    "are",
    "of",
    "to",
    "from",
    "in",
    "on",
    "for",
    "and",
    "or",
    "as",
    "by",
    "with",
    "that",
    "this",
    "it",
    "its",
    "their",
    "has",
    "have",
    "had",
    "be",
    "been",
    "being",
}


def clean_numeric_text(text: str) -> str:
    """
    Remove citation/reference identifiers before extracting numbers.

    Examples removed:
    - Evidence 1
    - Evidence 12
    - ID: cultfit-drhp-2026-chunk-1091
    - chunk-1091
    """
    text = re.sub(
        r"\bEvidence\s+\d+\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\bchunk-\d+\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\bID:\s*[A-Za-z0-9_-]+\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    return text


def extract_numbers(text: str) -> set[float]:
    """
    Extract meaningful numeric values from text.

    Monetary values expressed in crore are normalized to
    INR million so that:

        ₹950 crore == ₹9,500 million

    Enumeration numbers such as:
        1. Risk A
        2. Risk B

    are ignored because they are list markers, not
    factual numeric claims.
    """
    text = clean_numeric_text(text)

    # Remove numbered-list markers such as:
    # 1. Risk
    # 2. Risk
    # 3. Risk
    text = re.sub(
        r"(?m)^\s*\d+\.\s+",
        " ",
        text,
    )

    number_pattern = r"\d[\d,]*(?:\.\d+)?"

    result: set[float] = set()

    for match in re.finditer(number_pattern, text):
        raw_number = match.group(0)

        try:
            value = normalize_numeric(raw_number)
        except (ValueError, TypeError):
            continue

        start = match.start()
        end = match.end()

        context_after = text[end:end + 20].lower()
        context_before = text[max(0, start - 20):start].lower()

        # Normalize crore -> million.
        #
        # 1 crore = 10 million
        if re.search(r"\bcrore(s)?\b", context_after):
            value *= 10

        elif re.search(r"\bcrore(s)?\b", context_before):
            value *= 10

        result.add(value)

    return result


def numeric_groundedness(
    answer: str,
    evidence: list[dict],
) -> bool:
    """
    Check whether every meaningful numeric value in the
    answer occurs somewhere in the retrieved evidence.

    Citation identifiers are ignored.
    Monetary values expressed in crore/million are
    normalized before comparison.
    """
    answer_numbers = extract_numbers(answer)

    if not answer_numbers:
        return True

    evidence_text = "\n".join(
        item.get("text", "")
        for item in evidence
    )

    evidence_numbers = extract_numbers(evidence_text)

    return answer_numbers.issubset(evidence_numbers)


def normalize_claim_tokens(
    text: str,
) -> set[str]:
    """
    Convert text into meaningful lexical tokens.

    Citation references and markdown formatting are removed
    because they are metadata rather than factual content.
    """
    text = re.sub(
        r"\bEvidence\s+\d+\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\bID:\s*[A-Za-z0-9_-]+\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\bchunk-\d+\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\*\*",
        " ",
        text,
    )

    tokens = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    return {
        token
        for token in tokens
        if token not in STOPWORDS
        and len(token) > 1
    }


def claim_supported(
    claim: str,
    evidence_text: str,
    threshold: float = 0.60,
) -> bool:
    """
    Check whether a substantial portion of the
    claim's meaningful tokens occur in the evidence.

    This allows simple paraphrasing while remaining
    conservative.
    """
    claim_tokens = normalize_claim_tokens(
        claim
    )

    evidence_tokens = normalize_claim_tokens(
        evidence_text
    )

    if not claim_tokens:
        return True

    overlap = (
        len(
            claim_tokens
            & evidence_tokens
        )
        / len(claim_tokens)
    )

    return overlap >= threshold


def extract_claims(
    answer: str,
) -> list[str]:
    """
    Split an answer into substantive claim-like units.

    Citation-only and section-label lines are ignored because
    they are not factual claims.
    """
    claims = re.split(
        r"(?<=[.!?])\s+|\n+",
        answer.strip(),
    )

    cleaned_claims = []

    for claim in claims:
        claim = claim.strip()

        if not claim:
            continue

        normalized = claim.lower().strip()

        # Ignore citation-only / section-label text.
        if normalized in {
            "key evidence:",
            "citations",
            "expected answer terms",
        }:
            continue

        if normalized.startswith(
            "**citation:**"
        ):
            continue

        if normalized.startswith(
            "citation:"
        ):
            continue

        cleaned_claims.append(claim)

    return cleaned_claims


def claim_level_groundedness(
    answer: str,
    evidence: list[dict],
) -> float:
    """
    Measure the fraction of substantive answer claims
    supported by the retrieved evidence.

    All retrieved evidence is considered together because
    an answer may legitimately synthesize information
    across multiple chunks.
    """
    claims = extract_claims(answer)

    if not claims:
        return 1.0

    combined_evidence = "\n".join(
        item.get("text", "")
        for item in evidence
    )

    grounded_claims = 0

    for claim in claims:
        claim_normalized = claim.lower().strip()

        # Skip generic synthesis / citation commentary.
        if (
            "explicitly stated in evidence" in claim_normalized
            or "sources collectively confirm" in claim_normalized
            or "evidence consistently identifies" in claim_normalized
        ):
            continue

        claim_tokens = normalize_claim_tokens(
            claim
        )

        if not claim_tokens:
            continue

        evidence_tokens = normalize_claim_tokens(
            combined_evidence
        )

        overlap = (
            len(
                claim_tokens
                & evidence_tokens
            )
            / len(claim_tokens)
        )

        # A claim is grounded when at least 60% of
        # its meaningful tokens appear in the retrieved evidence.
        if overlap >= 0.60:
            grounded_claims += 1

    substantive_claims = [
        claim
        for claim in claims
        if normalize_claim_tokens(claim)
        and not (
            "explicitly stated in evidence"
            in claim.lower()
            or "sources collectively confirm"
            in claim.lower()
            or "evidence consistently identifies"
            in claim.lower()
        )
    ]

    if not substantive_claims:
        return 1.0

    return (
        grounded_claims
        / len(substantive_claims)
    )