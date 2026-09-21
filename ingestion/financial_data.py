from dataclasses import dataclass


@dataclass
class StructuredFinancialMetric:
    """
    Canonical financial metric extracted from an
    authoritative IPO document.
    """

    metric_name: str

    period: str

    value: float

    unit: str

    source_document_id: str | None = None

    page_number: int | None = None


def normalize_metric_name(
    metric_name: str,
) -> str:
    """
    Normalize financial metric names.
    """

    normalized = (
        " ".join(
            metric_name
           .strip()
            .lower()
            .split()
        )
    )

    aliases = {
        "revenue": (
            "revenue_from_operations"
        ),
        "revenue from operations": (
            "revenue_from_operations"
        ),
        "revenue from operations - total": (
            "revenue_from_operations"
        ),
        "loss for the year": (
            "profit_or_loss"
        ),

        "profit for the year": (
            "profit_or_loss"
        ),

        "profit/(loss) for the year": (
            "profit_or_loss"
        ),

        "loss/(profit) for the year": (
            "profit_or_loss"
        ),
        "adjusted ebitda": (
            "adjusted_ebitda"
        ),

        "adjusted ebitda(1)": (
            "adjusted_ebitda"
        ),

        "net cash generated from/(used in) operating activities": (
            "operating_cash_flow"
        ),

        "net cash generated from/ (used in) operating activities": (
            "operating_cash_flow"
        ),

        "net cash generated from operating activities": (
            "operating_cash_flow"
        ),
    }

    return aliases.get(
        normalized,
        normalized.replace(
            " ",
            "_",
        ),
    )