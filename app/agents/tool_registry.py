from langchain_core.tools import tool

from app.tools.ipo_tool import lookup_ipo
from app.tools.financial_tool import (
    lookup_financials,
    analyze_revenue_growth,
)
from app.tools.rag_tools import search_ipo_documents
from app.tools.financial_analysis import analyze_financial_performance_tool
from app.tools.news_tool import lookup_news


@tool
def lookup_ipo_tool(company_name: str) -> dict:
    """
    Retrieve structured IPO information such as issue size,
    price band, dates, lot size, and fresh issue details.
    """

    return lookup_ipo(company_name)


@tool
def lookup_financials_tool(
    company_name: str,
    metric_name: str | None = None,
    period: str | None = None,
) -> dict:
    """
    Retrieve structured financial metrics.

    Use canonical metric concepts such as:
    revenue_from_operations.

    Use period separately, for example:
    FY2026.
    """

    return lookup_financials(
        company_name,
        metric_name,
        period
    )


@tool
def analyze_revenue_growth_tool(
    company_name: str,
) -> dict:
    """
    Calculate revenue growth and CAGR.
    """

    return analyze_revenue_growth(
        company_name
    )


@tool
def search_ipo_documents_tool(
    question: str,
    top_k: int = 5,
    section: str | None = None,
    company_name: str | None = None,
) -> dict:
    """
    Search the IPO documents and return
    evidence-grounded answers.
    """

    return search_ipo_documents(
        question,
        top_k=top_k,
        section=section,
        company_name=company_name,
    )

@tool
def lookup_news_tool(
    company_name: str,
    limit: int = 10,
    sentiment: str | None = None,
    topic: str | None = None
) -> dict:
    """
    Retrieve recent news articles associated with an IPO.
    """

    return lookup_news(
        company_name,
        limit=limit,
        sentiment=sentiment,
        topic=topic,
    )


TOOLS = [
    lookup_ipo_tool,
    lookup_financials_tool,
    analyze_revenue_growth_tool,
    search_ipo_documents_tool,
    analyze_financial_performance_tool,
    lookup_news_tool,
]