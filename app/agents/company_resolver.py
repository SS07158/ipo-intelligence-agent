from sqlalchemy.orm import Session

from database.ipo_repository import get_all_ipos


COMPANY_ALIASES = {
    "CULT.FIT": "CULT.FIT LIMITED",
    "CULTFIT": "CULT.FIT LIMITED",

    "STERLITE": "Sterlite Electric Limited",
    "STERLITE ELECTRIC": "Sterlite Electric Limited",
    "STERLITE POWER": "Sterlite Electric Limited",
}

def normalize_company_name(
    company_name: str,
) -> str:
    """
    Normalize a company name into a canonical form.
    """

    normalized = " ".join(
        company_name
        .strip()
        .upper()
        .split()
    )

    return COMPANY_ALIASES.get(
        normalized,
        normalized,
    )


def resolve_company_from_question(
    question: str,
    session: Session,
) -> str | None:
    """
    Resolve a company from the user question.

    Resolution order:
    1. Exact company name from the IPO database.
    2. IPO symbol from the database.
    3. Known aliases.
    """

    normalized_question = question.upper()

    ipos = get_all_ipos(session)

    # -------------------------------------------------
    # Database company names
    # -------------------------------------------------

    for ipo in ipos:

        company_name = (
            ipo.company_name or ""
        ).strip()

        if not company_name:
            continue

        if company_name.upper() in normalized_question:
            return company_name

        # -------------------------------------------------
        # Database symbols
        # -------------------------------------------------

        symbol = (
            ipo.symbol or ""
        ).strip()

        if (
            symbol
            and symbol.upper()
            in normalized_question
        ):
            return company_name

    # -------------------------------------------------
    # Known aliases
    # -------------------------------------------------

    for alias, canonical_name in COMPANY_ALIASES.items():

        if alias in normalized_question:
            return canonical_name

    return None