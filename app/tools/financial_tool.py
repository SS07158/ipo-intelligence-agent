from database.database import SessionLocal
from database.ipo_repository import (
    get_financial_metrics,
    get_ipo_by_company,
    compare_ipo_financials,
    get_documents_for_ipo,
)

from app.tools.financial_calculator import (
    cagr,
    percentage_change,
)

from app.tools.ipo_tool import (
    normalize_company_name,
)


def normalize_metric_name(
    metric_name: str | None,
) -> str | None:
    """
    Convert natural-language metric descriptions into
    canonical database metric names.
    """

    if metric_name is None:
        return None

    normalized = (
        metric_name
        .strip()
        .lower()
    )

    aliases = {
        "revenue": (
            "revenue_from_operations"
        ),
        "revenue from operations": (
            "revenue_from_operations"
        ),
        "revenue from operations fy2026": (
            "revenue_from_operations"
        ),
        "revenue from operations fy2025": (
            "revenue_from_operations"
        ),
        "revenue from operations fy2024": (
            "revenue_from_operations"
        ),
    }

    return aliases.get(
        normalized,
        normalized,
    )


def lookup_financials(
    company_name: str,
    metric_name: str | None = None,
    period: str | None = None,
) -> dict:
    """
    Retrieve structured financial metrics for a company.

    metric_name is normalized to the canonical database name.
    period is filtered separately.
    """

    session = SessionLocal()

    try:
        company_name = normalize_company_name(
            company_name
        )

        metric_name = normalize_metric_name(
            metric_name
        )

        ipo = get_ipo_by_company(
            session,
            company_name,
        )

        if ipo is None:
            return {
                "found": False,
                "message": (
                    f"No IPO found for "
                    f"'{company_name}'."
                ),
            }

        metrics = get_financial_metrics(
            session,
            ipo.id,
            metric_name,
        )

        # Filter by period separately.
        if period is not None:
            metrics = [
                metric
                for metric in metrics
                if metric.period == period
            ]

        documents = get_documents_for_ipo(
            session,
            ipo.id,
        )

        documents_by_id = {
            document.id: document
            for document in documents
        }

        formatted_metrics = []

        for metric in metrics:

            document = documents_by_id.get(
                metric.source_document_id
            )

            citation = None

            if document is not None:
                citation = {
                    "company": (
                        ipo.company_name
                    ),
                    "document_id": (
                        document.document_id
                    ),
                    "document_type": (
                        document.document_type
                    ),
                    "source": (
                        document.source
                    ),
                    "source_url": (
                        document.source_url
                    ),
                    "page_number": (
                        metric.page_number
                    ),
                }

            formatted_metrics.append(
                {
                    "metric_name": (
                        metric.metric_name
                    ),
                    "period": metric.period,
                    "value": metric.value,
                    "unit": metric.unit,
                    "citation": citation,
                }
            )

        return {
            "found": True,
            "company_name": ipo.company_name,
            "metrics": formatted_metrics,
        }

    finally:
        session.close()


def analyze_revenue_growth(
    company_name: str,
) -> dict:
    """
    Retrieve revenue data and calculate growth metrics.
    """

    result = lookup_financials(
        company_name,
        "revenue_from_operations",
    )

    if not result["found"]:
        return result

    metrics = result["metrics"]

    if len(metrics) < 2:
        return {
            "found": True,
            "company_name": company_name,
            "message": (
                "Not enough revenue periods "
                "for growth analysis."
            ),
            "metrics": metrics,
            "citations": [
                metric["citation"]
                for metric in metrics
                if metric.get("citation") is not None
            ],
        }

    metrics = sorted(
        metrics,
        key=lambda item: item["period"],
    )

    first = metrics[0]
    last = metrics[-1]

    first_value = first["value"]
    last_value = last["value"]

    years = len(metrics) - 1

    total_growth = percentage_change(
        first_value,
        last_value,
    )

    revenue_cagr = cagr(
        first_value,
        last_value,
        years,
    )

    return {
        "found": True,
        "company_name": company_name,
        "start_period": first["period"],
        "end_period": last["period"],
        "start_value": first_value,
        "end_value": last_value,
        "unit": first["unit"],
        "total_growth_percent": total_growth,
        "cagr_percent": revenue_cagr,
        "metrics": metrics,
        "citations": [
            metric["citation"]
            for metric in metrics
            if metric.get("citation") is not None
        ],
    }


def compare_financial_metrics(
    first_company: str,
    second_company: str,
    metric_name: str,
) -> dict:
    """
    Compare a financial metric between two companies.
    """

    session = SessionLocal()

    try:
        first_company = normalize_company_name(
            first_company
        )

        second_company = normalize_company_name(
            second_company
        )

        metric_name = normalize_metric_name(
            metric_name
        )

        first_ipo = get_ipo_by_company(
            session,
            first_company,
        )

        second_ipo = get_ipo_by_company(
            session,
            second_company,
        )

        if first_ipo is None:
            return {
                "found": False,
                "message": (
                    f"No IPO found for "
                    f"'{first_company}'."
                ),
            }

        if second_ipo is None:
            return {
                "found": False,
                "message": (
                    f"No IPO found for "
                    f"'{second_company}'."
                ),
            }

        comparison = compare_ipo_financials(
            session,
            first_ipo.id,
            second_ipo.id,
            metric_name,
        )

        return {
            "found": True,
            **comparison,
        }

    finally:
        session.close()