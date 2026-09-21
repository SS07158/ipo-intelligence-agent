from database.ipo_repository import (
    create_financial_metric,
    get_financial_metrics,
    get_or_create_ipo,
)


def test_financial_metric_create_and_query(test_session):
    ipo = get_or_create_ipo(
        test_session,
        ipo_id="test-cultfit",
        company_name="CULT.FIT LIMITED",
    )

    metric = create_financial_metric(
        test_session,
        ipo_id=ipo.id,
        metric_name="test_metric",
        period="TEST",
        value=123.45,
        unit="INR crore",
    )

    assert metric.value == 123.45

    metrics = get_financial_metrics(
        test_session,
        ipo.id,
        "test_metric",
    )

    assert len(metrics) == 1
    assert metrics[0].value == 123.45