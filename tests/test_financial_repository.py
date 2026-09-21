from database.ipo_repository import (
    create_financial_metric,
    get_financial_metrics,
    get_or_create_ipo,
)


def test_revenue_metrics(test_session):
    ipo = get_or_create_ipo(
        test_session,
        ipo_id="test-cultfit",
        company_name="CULT.FIT LIMITED",
    )

    values_to_insert = {
        "FY2024": 9266.62,
        "FY2025": 12155.36,
        "FY2026": 17206.06,
    }

    for period, value in values_to_insert.items():
        create_financial_metric(
            test_session,
            ipo_id=ipo.id,
            metric_name="revenue_from_operations",
            period=period,
            value=value,
            unit="INR million",
        )

    metrics = get_financial_metrics(
        test_session,
        ipo.id,
        "revenue_from_operations",
    )

    assert len(metrics) == 3

    values = {
        metric.period: metric.value
        for metric in metrics
    }

    assert values["FY2024"] == 9266.62
    assert values["FY2025"] == 12155.36
    assert values["FY2026"] == 17206.06