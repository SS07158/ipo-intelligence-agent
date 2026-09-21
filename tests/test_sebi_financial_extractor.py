import pytest

from ingestion.financial_data import (
    StructuredFinancialMetric,
)

from ingestion.sebi.financial_extractor import (
    extract_total_revenue_metrics,
    validate_revenue_metrics,
    extract_loss_metrics,
    extract_adjusted_ebitda_metrics,
    extract_operating_cash_flow_metrics,
)


def test_extract_total_segment_revenue():

    text = """
    Revenue from Operations - Services
    11,978.32
    69.62%
    8,890.86
    73.14%
    6,698.86
    72.29%

    Revenue from Operations - Products
    5,227.74
    30.38%
    3,264.50
    26.86%
    2,567.76
    27.71%

    Total segment revenue
    17,206.06
    100.00%
    12,155.36
    100.00%
    9,266.62
    100.00%
    """

    metrics = (
        extract_total_revenue_metrics(
            text,
            source_document_id=(
                "cultfit-drhp-2026"
            ),
            page_number=38,
        )
    )

    assert len(metrics) == 3

    assert (
        metrics[0].period
        == "FY2026"
    )

    assert (
        metrics[0].value
        == 17206.06
    )

    assert (
        metrics[1].period
        == "FY2025"
    )

    assert (
        metrics[1].value
        == 12155.36
    )

    assert (
        metrics[2].period
        == "FY2024"
    )

    assert (
        metrics[2].value
        == 9266.62
    )

    assert all(
        metric.metric_name
        == "revenue_from_operations"
        for metric in metrics
    )

    assert all(
        metric.unit
        == "INR million"
        for metric in metrics
    )


def test_reject_invalid_revenue_periods():

    metrics = [
        StructuredFinancialMetric(
            metric_name=(
                "revenue_from_operations"
            ),
            period="FY2026",
            value=17206.06,
            unit="INR million",
        ),
    ]

    with pytest.raises(
        ValueError
    ):
        validate_revenue_metrics(
            metrics
        )

def test_extract_loss_for_year():

    text = """
    Particulars
    Fiscal year 2026
    Fiscal year 2025
    Fiscal year 2024
    (₹ million)

    Revenue from operations
    17,206.06
    12,155.36
    9,266.62

    Loss for the year
    (2,518.58)
    (4,808.26)
    (8,884.91)

    Adjusted EBITDA
    1,447.80
    (335.32)
    (1,401.90)
    """

    metrics = extract_loss_metrics(
        text,
        source_document_id=(
            "cultfit-drhp-2026"
        ),
        page_number=10,
    )

    assert len(metrics) == 3

    assert (
        metrics[0].metric_name
        == "profit_or_loss"
    )

    assert (
        metrics[0].period
        == "FY2026"
    )

    assert (
        metrics[0].value
        == -2518.58
    )

    assert (
        metrics[1].period
        == "FY2025"
    )

    assert (
        metrics[1].value
        == -4808.26
    )

    assert (
        metrics[2].period
        == "FY2024"
    )

    assert (
        metrics[2].value
        == -8884.91
    )

    assert (
        metrics[0].unit
        == "INR million"
    )

def test_extract_loss_for_year():

    text = """
    Particulars
    Fiscal year 2026
    Fiscal year 2025
    Fiscal year 2024
    (₹ million)

    Revenue from operations
    17,206.06
    12,155.36
    9,266.62

    Loss for the year
    (2,518.58)
    (4,808.26)
    (8,884.91)

    Adjusted EBITDA
    1,447.80
    (335.32)
    (1,401.90)

    Net cash generated from/ (used in)
    operating activities
    941.19
    119.91
    (2,307.27)
    """

    metrics = extract_loss_metrics(
        text,
        source_document_id="cultfit-drhp-2026",
        page_number=52,
    )

    assert len(metrics) == 3

    assert (
        metrics[0].metric_name
        == "profit_or_loss"
    )

    assert (
        metrics[0].period
        == "FY2026"
    )

    assert (
        metrics[0].value
        == -2518.58
    )

    assert (
        metrics[1].period
        == "FY2025"
    )

    assert (
        metrics[1].value
        == -4808.26
    )

    assert (
        metrics[2].period
        == "FY2024"
    )

    assert (
        metrics[2].value
        == -8884.91
    )

    assert (
        metrics[0].unit
        == "INR million"
    )

def test_extract_adjusted_ebitda():

    text = """
    Particulars
    Fiscal year 2026
    Fiscal year 2025
    Fiscal year 2024

    Adjusted EBITDA(1)
    1,447.80
    (335.32)
    (1,401.90)
    """

    metrics = extract_adjusted_ebitda_metrics(
        text,
        source_document_id="cultfit-drhp-2026",
        page_number=52,
    )

    assert len(metrics) == 3

    assert (
        metrics[0].metric_name
        == "adjusted_ebitda"
    )

    assert (
        metrics[0].value
        == 1447.80
    )

    assert (
        metrics[1].value
        == -335.32
    )

    assert (
        metrics[2].value
        == -1401.90
    )


def test_extract_operating_cash_flow():

    text = """
    Particulars
    Fiscal year 2026
    Fiscal year 2025
    Fiscal year 2024

    Net cash generated from/ (used in)
    operating activities
    941.19
    119.91
    (2,307.27)
    """

    metrics = extract_operating_cash_flow_metrics(
        text,
        source_document_id="cultfit-drhp-2026",
        page_number=52,
    )

    assert len(metrics) == 3

    assert (
        metrics[0].metric_name
        == "operating_cash_flow"
    )

    assert (
        metrics[0].value
        == 941.19
    )

    assert (
        metrics[1].value
        == 119.91
    )

    assert (
        metrics[2].value
        == -2307.27
    )