def classify_question(question: str) -> str:
    """
    Deterministic question router used as a fallback
    when the LLM does not produce tool calls.

    Returns one of:
    - ipo
    - financial
    - rag
    - news
    - mixed
    """

    normalized = question.lower()

    financial_terms = [
        "revenue",
        "profit",
        "financial",
        "margin",
        "cagr",
        "growth",
        "ebitda",
        "debt",
        "cash flow",
        "profitability",
        "results of operations",
        "accounting",
    ]

    ipo_terms = [
        "ipo",
        "price band",
        "issue size",
        "lot size",
        "issue date",
        "listing date",
        "fresh issue",
        "offer for sale",
        "ipo proceeds",
        "objects of the offer",
    ]

    document_terms = [
        "risk",
        "drhp",
        "rhp",
        "business model",
        "use of proceeds",
        "industry",
        "competitive advantage",
        "competitive strengths",
        "operating model",
        "business operations",
        "strategy",
        "accounting policies",
    ]

    news_terms = [
        "news",
        "recent news",
        "latest news",
        "recent update",
        "latest update",
        "headlines",
        "reported",
        "according to reports",
    ]

    has_financial = any(
        term in normalized
        for term in financial_terms
    )

    has_ipo = any(
        term in normalized
        for term in ipo_terms
    )

    has_document = any(
        term in normalized
        for term in document_terms
    )

    has_news = any(
        term in normalized
        for term in news_terms
    )

    detected_categories = sum(
        [
            has_financial,
            has_ipo,
            has_document,
            has_news,
        ]
    )

    if detected_categories > 1:
        return "mixed"

    if has_financial:
        return "financial"

    if has_ipo:
        return "ipo"

    if has_news:
        return "news"

    if has_document:
        return "rag"

    return "rag"