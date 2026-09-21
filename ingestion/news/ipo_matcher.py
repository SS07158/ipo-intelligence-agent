import re

from database.ipo_repository import get_all_ipos
from ingestion.news.provider import NewsArticleData


LEGAL_SUFFIXES = {
    "limited",
    "ltd",
    "private",
    "pvt",
    "llp",
    "inc",
    "corporation",
    "corp",
}


def normalize_company_text(value: str) -> str:
    """
    Normalize company text for deterministic matching.
    """

    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    tokens = value.split()

    tokens = [
        token
        for token in tokens
        if token not in LEGAL_SUFFIXES
    ]

    return " ".join(tokens)


def generate_company_aliases(
    company_name: str,
) -> set[str]:
    """
    Generate conservative aliases for a company name.
    """

    normalized = normalize_company_text(
        company_name
    )

    if not normalized:
        return set()

    aliases = {
        normalized,
    }

    compact = normalized.replace(
        " ",
        "",
    )

    if len(compact) >= 5:
        aliases.add(compact)

    return aliases


def match_article_to_ipo(
    session,
    article: NewsArticleData,
):
    """
    Match a news article to an IPO using deterministic
    company-name aliases.

    Returns:
        IPO object if a match is found, otherwise None.
    """

    ipos = get_all_ipos(session)

    text = " ".join(
        [
            article.title or "",
            article.summary or "",
        ]
    )

    normalized_text = normalize_company_text(
        text
    )

    compact_text = normalized_text.replace(
        " ",
        "",
    )

    for ipo in ipos:
        aliases = generate_company_aliases(
            ipo.company_name or ""
        )

        for alias in aliases:
            if alias in normalized_text:
                return ipo

            if alias in compact_text:
                return ipo

        symbol = (ipo.symbol or "").strip().lower()

        if symbol:
            normalized_symbol = re.sub(
                r"[^a-z0-9]",
                "",
                symbol,
            )

            if (
                normalized_symbol
                and normalized_symbol in compact_text
            ):
                return ipo

    return None