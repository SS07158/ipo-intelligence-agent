from database.ipo_repository import (
    create_financial_metric,
    get_or_create_ipo,
)


def test_compare_ipo_financials(test_session):
    ipo_a = get_or_create_ipo(
        test_session,
        ipo_id="test-ipo-a",
        company_name="Test IPO A",
    )

    ipo_b = get_or_create_ipo(
        test_session,
        ipo_id="test-ipo-b",
        company_name="Test IPO B",
    )

    create_financial_metric(
        test_session,
        ipo_id=ipo_a.id,
        metric_name="revenue",
        period="FY2025",
        value=1000.0,
        unit="INR million",
    )

    create_financial_metric(
        test_session,
        ipo_id=ipo_a.id,
        metric_name="revenue",
        period="FY2026",
        value=1200.0,
        unit="INR million",
    )

    create_financial_metric(
        test_session,
        ipo_id=ipo_b.id,
        metric_name="revenue",
        period="FY2025",
        value=800.0,
        unit="INR million",
    )

    create_financial_metric(
        test_session,
        ipo_id=ipo_b.id,
        metric_name="revenue",
        period="FY2026",
        value=1000.0,
        unit="INR million",
    )

    from database.ipo_repository import compare_ipo_financials

    result = compare_ipo_financials(
        test_session,
        ipo_a.id,
        ipo_b.id,
        "revenue",
    )

    assert result["first_ipo"] == "Test IPO A"
    assert result["second_ipo"] == "Test IPO B"

    assert result["common_periods"] == [
        "FY2025",
        "FY2026",
    ]

    assert result["first_values"]["FY2025"] == 1000.0
    assert result["second_values"]["FY2025"] == 800.0