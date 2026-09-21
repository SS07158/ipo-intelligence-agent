from database.database import SessionLocal
from langchain_core.tools import tool

from database.ipo_repository import (
    get_financial_metrics,
    get_ipo_by_company,
)

from app.tools.ipo_tool import (
    normalize_company_name,
)


def _metric_values(
    metrics,
    metric_name: str,
) -> dict[str, dict]:
    """
    Convert FinancialMetric rows into:

        {
            "FY2024": {
                "value": 9266.62,
                "unit": "INR million",
                "source_document_id": 1,
                "page_number": 38,
            },
            ...
        }
    """

    return {
        metric.period: {
            "value": metric.value,
            "unit": metric.unit,
            "source_document_id": metric.source_document_id,
            "page_number": metric.page_number,
        }
        for metric in metrics
        if metric.metric_name == metric_name
    }


def _percentage_change(
    start: float,
    end: float,
) -> float:
    """
    Calculate percentage change.
    """

    if start == 0:
        return 0.0

    return (
        (end - start)
        / abs(start)
    ) * 100


def analyze_financial_performance(
    company_name: str,
) -> dict:
    """
    Analyze the direction of key financial metrics
    using only persisted structured data.

    Metrics:
        revenue_from_operations
        profit_or_loss
        adjusted_ebitda
        operating_cash_flow
    """

    session = SessionLocal()

    try:

        company_name = (
            normalize_company_name(
                company_name
            )
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
        )

        if not metrics:
            return {
                "found": False,
                "company_name": (
                    ipo.company_name
                ),
                "message": (
                    "No financial metrics "
                    "were found."
                ),
            }

        grouped = {
            "revenue_from_operations": (
                _metric_values(
                    metrics,
                    "revenue_from_operations",
                )
            ),
            "profit_or_loss": (
                _metric_values(
                    metrics,
                    "profit_or_loss",
                )
            ),
            "adjusted_ebitda": (
                _metric_values(
                    metrics,
                    "adjusted_ebitda",
                )
            ),
            "operating_cash_flow": (
                _metric_values(
                    metrics,
                    "operating_cash_flow",
                )
            ),
        }

        result = {
            "found": True,
            "company_name": (
                ipo.company_name
            ),
            "metrics": {
                metric_name: {
                    period: details["value"]
                    for period, details
                    in values.items()
                }
                for metric_name, values
                in grouped.items()
            },
            "metric_details": grouped,
            "analysis": {},
        }

        # ---------------------------------------------
        # Revenue
        # ---------------------------------------------

        revenue = grouped[
            "revenue_from_operations"
        ]

        if (
            "FY2024" in revenue
            and "FY2026" in revenue
        ):
            result["analysis"][
                "revenue_growth_percent"
            ] = _percentage_change(
                revenue["FY2024"]["value"],
                revenue["FY2026"]["value"],
            )

        # ---------------------------------------------
        # Profit/Loss
        # ---------------------------------------------

        profit_loss = grouped[
            "profit_or_loss"
        ]

        if (
            "FY2024" in profit_loss
            and "FY2026" in profit_loss
        ):

            result["analysis"][
                "loss_reduction_percent"
            ] = _percentage_change(
                abs(
                    profit_loss["FY2024"]["value"]
                ),
                abs(
                    profit_loss["FY2026"]["value"]
                ),
            )

            result["analysis"][
                "profit_loss_direction"
            ] = (
                "improving"
                if profit_loss["FY2026"]["value"]
                > profit_loss["FY2024"]["value"]
                else "worsening"
            )

        # ---------------------------------------------
        # Adjusted EBITDA
        # ---------------------------------------------

        ebitda = grouped[
            "adjusted_ebitda"
        ]

        if (
            "FY2024" in ebitda
            and "FY2026" in ebitda
        ):

            result["analysis"][
                "adjusted_ebitda_change"
            ] = (
                ebitda["FY2026"]["value"]
                - ebitda["FY2024"]["value"]
            )

            result["analysis"][
                "adjusted_ebitda_direction"
            ] = (
                "improving"
                if ebitda["FY2026"]["value"]
                > ebitda["FY2024"]["value"]
                else "worsening"
            )

        # ---------------------------------------------
        # Operating cash flow
        # ---------------------------------------------

        cash_flow = grouped[
            "operating_cash_flow"
        ]

        if (
            "FY2024" in cash_flow
            and "FY2026" in cash_flow
        ):

            result["analysis"][
                "operating_cash_flow_change"
            ] = (
                cash_flow["FY2026"]["value"]
                - cash_flow["FY2024"]["value"]
            )

            result["analysis"][
                "operating_cash_flow_direction"
            ] = (
                "improving"
                if cash_flow["FY2026"]["value"]
                > cash_flow["FY2024"]["value"]
                else "worsening"
            )

        return result

    finally:
        session.close()


@tool
def analyze_financial_performance_tool(company_name: str) -> dict:
        
        """
        Analyze the company's financial performance across
        revenue, profit/loss, adjusted EBITDA, and operating cash flow.

        Use this tool for questions asking how the company's
        financial performance has changed over time.
        """


        return analyze_financial_performance(company_name)