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
) -> dict:
    """
    Search IPO documents and generate a grounded answer.
    """


    where = None

    normalized_section = normalize_section(
        section
    )

    where_values = {}

    if normalized_section is not None:
        where_values["section"] = (
            normalized_section
        )

    if company_name is not None:
        from database.database import SessionLocal
        from database.ipo_repository import (
            get_ipo_by_company,
        )
        from app.tools.ipo_tool import (
            normalize_company_name,
        )

        session = SessionLocal()

        try:
            canonical_company = (
                normalize_company_name(
                    company_name
                )
            )

            ipo = get_ipo_by_company(
                session,
                canonical_company,
            )

            if ipo is not None:
                where_values["ipo_id"] = (
                    ipo.ipo_id
                )

        finally:
            session.close()

    if where_values:
        where = where_values

    return get_rag_service().answer(
        question,
        top_k=top_k,
        where=where,
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