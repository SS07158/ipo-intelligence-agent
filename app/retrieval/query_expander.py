INDUSTRY_TERMS = [
    "industry",
    "market",
    "fitness industry",
    "fitness market",
    "fitness and active lifestyle market",
    "Indian fitness market",
    "industry overview",
]


BUSINESS_TERMS = [
    "business",
    "business model",
    "operations",
    "our operations",
    "main operations",
    "business operations",
    "services",
    "fitness services",
    "fitness products",
    "compete",
    "competition",
    "competitive advantage",
    "competitive strengths",
    "our strengths",
    "ecosystem-led model",
]


FINANCIAL_TERMS = [
    "financial information",
    "summary of financial information",
    "restated consolidated financial information",
    "financial statements",
    "financial performance",
    "revenue",
    "profit",
    "profitability",
    "results of operations",
]


RISK_TERMS = [
    "risk",
    "risks",
    "internal risks",
    "external risks",
    "offer risks",
    "risks related to this offer",
]

RISK_EXPANSION_TERMS = [
    "risk factors",
    "risk factor",
    "key risks",
    "major risks",
    "potential risks",
    "business risks",
    "operational risks",
    "financial risks",
    "market risks",
    "regulatory risks",
    "legal risks",
    "commercial risks",
    "strategic risks",
    "technology risks",
    "cybersecurity risks",
    "supply chain risks",
    "liquidity risks",
    "credit risks",
    "execution risks",
    "dependency risks",
    "uncertainties",
    "adverse impact",
    "materially adversely affect",
    "cannot assure",
    "there can be no assurance",
]


def expand_query(query: str) -> str:
    """
    Add deterministic domain and DRHP section terms
    based on query content.
    """

    normalized = query.lower()

    terms = []

    if any(
        word in normalized
        for word in [
            "industry",
            "market",
            "growth opportunity",
            "market trend",
            "industry factor",
            "factors affecting",
        ]
    ):
        terms.extend(INDUSTRY_TERMS)

    if any(
        word in normalized
        for word in [
            "business",
            "operations",
            "business model",
            "competitive",
            "strengths",
            "compete",
            "competition",
        ]
    ):
        terms.extend(BUSINESS_TERMS)

    is_competition_query = any(
        word in normalized
        for word in [
            "compete",
            "competition",
            "competitive",
            "competitive advantage",
            "competitive strengths",
        ]
    )

    if any(
        phrase in normalized
        for phrase in [
            "financial",
            "revenue",
            "profit",
            "profitability",
            "results of operations",
            "accounting",
        ]
    ) and not is_competition_query:

        terms.extend(FINANCIAL_TERMS)

    if any(
        word in normalized
        for word in [
            "risk",
            "risks",
            "negative",
        ]
    ):
        terms.extend(RISK_TERMS)
        terms.extend(RISK_EXPANSION_TERMS)

    if not terms:
        return query

    unique_terms = list(
        dict.fromkeys(terms)
    )

    return (
        f"{query}\n"
        + " ".join(unique_terms)
    )