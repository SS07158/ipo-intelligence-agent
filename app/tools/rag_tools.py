from app.retrieval.rag_service import RAGService

RAG_SERVICE = None


def get_rag_service() -> RAGService:
    global RAG_SERVICE

    if RAG_SERVICE is None:
        RAG_SERVICE = RAGService()

    return RAG_SERVICE


def search_ipo_documents(
    question: str,
    top_k: int = 5,
    section: str | None = None,
    company_name: str | None = None,
    ipo_id: str | None = None,
) -> dict:
    """
    Search IPO documents using a mandatory, validated IPO scope.
    Refuses to perform an unfiltered document search.
    """
    from app.tools.ipo_tool import normalize_company_name
    from database.database import SessionLocal
    from database.ipo_repository import (
        get_all_ipos,
        get_ipo_by_id,
    )

    normalized_section = normalize_section(section)
    where_values = {}

    if normalized_section is not None:
        where_values["section"] = normalized_section

    session = SessionLocal()

    try:
        selected_ipo = None

        # The selected ID takes precedence over company-name matching.
        if ipo_id is not None:
            selected_ipo = get_ipo_by_id(session, ipo_id)

            if selected_ipo is None:
                raise ValueError(
                    f"IPO scope '{ipo_id}' was not found. "
                    "Document search was blocked."
                )

        elif company_name is not None:
            canonical_company = normalize_company_name(
                company_name
            )

            matches = [
                ipo
                for ipo in get_all_ipos(session)
                if normalize_company_name(
                    ipo.company_name or ""
                ) == canonical_company
            ]

            if len(matches) != 1:
                raise ValueError(
                    "Could not uniquely resolve the IPO from "
                    "the company name. Provide a valid ipo_id. "
                    "Document search was blocked."
                )

            selected_ipo = matches[0]

        else:
            raise ValueError(
                "Document search requires a valid ipo_id. "
                "Unfiltered document search is not permitted."
            )

        where_values["ipo_id"] = selected_ipo.ipo_id

    finally:
        session.close()

    return get_rag_service().answer(
        question,
        top_k=top_k,
        where=where_values,
    )


def normalize_section(
    section: str | None,
) -> str | None:
    """
    Normalize natural-language section names into
    canonical indexed section names.
    """

    if section is None:
        return None

    normalized = (
        section
        .strip()
        .upper()
    )

    aliases = {
    "RISK FACTORS": "INTERNAL RISKS",
    "RISK_FACTOR": "INTERNAL RISKS",
    "RISK_FACTORS": "INTERNAL RISKS",
    "INTERNAL RISK": "INTERNAL RISKS",
    "INTERNAL RISKS": "INTERNAL RISKS",

    "EXTERNAL RISK": "EXTERNAL RISKS",
    "EXTERNAL RISKS": "EXTERNAL RISKS",

    "INDUSTRY": "INDUSTRY OVERVIEW",
    "INDUSTRY OVERVIEW": "INDUSTRY OVERVIEW",

    "BUSINESS": "OVERVIEW",
    "BUSINESS OVERVIEW": "OVERVIEW",

    "COMPETITIVE ADVANTAGE":
        "THE ECOSYSTEM-LED MODEL : COMPETITIVE ADVANTAGE THROUGH INTEGRATION",
    }

    return aliases.get(
        normalized,
        normalized,
    )