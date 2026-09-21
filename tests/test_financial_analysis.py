from unittest.mock import MagicMock, patch


def test_financial_performance_analysis():
    """
    Verify deterministic interpretation of the
    persisted CULT.FIT financial metrics.
    """

    mock_ipo = MagicMock()

    mock_ipo.company_name = (
        "CULT.FIT LIMITED"
    )
    mock_ipo.id = 1

    metrics = []

    values = {
        "revenue_from_operations": {
            "FY2024": 9266.62,
            "FY2025": 12155.36,
            "FY2026": 17206.06,
        },
        "profit_or_loss": {
            "FY2024": -8884.91,
            "FY2025": -4808.26,
            "FY2026": -2518.58,
        },
        "adjusted_ebitda": {
            "FY2024": -1401.90,
            "FY2025": -335.32,
            "FY2026": 1447.80,
        },
        "operating_cash_flow": {
            "FY2024": -2307.27,
            "FY2025": 119.91,
            "FY2026": 941.19,
        },
    }

    for metric_name, periods in values.items():

        for period, value in periods.items():

            metric = MagicMock()

            metric.metric_name = (
                metric_name
            )

            metric.period = period

            metric.value = value

            metrics.append(
                metric
            )

    with patch(
        "app.tools.financial_analysis.SessionLocal"
    ) as mock_session_factory, patch(
        "app.tools.financial_analysis.get_ipo_by_company",
        return_value=mock_ipo,
    ), patch(
        "app.tools.financial_analysis.get_financial_metrics",
        return_value=metrics,
    ):

        mock_session = (
            mock_session_factory.return_value
        )

        from app.tools.financial_analysis import (
            analyze_financial_performance,
        )

        result = (
            analyze_financial_performance(
                "CULT.FIT LIMITED"
            )
        )

    assert result["found"] is True

    assert (
        result["metrics"][
            "revenue_from_operations"
        ]["FY2026"]
        == 17206.06
    )

    assert (
        result["analysis"][
            "revenue_growth_percent"
        ]
        > 85
    )

    assert (
        result["analysis"][
            "profit_loss_direction"
        ]
        == "improving"
    )

    assert (
        result["analysis"][
            "adjusted_ebitda_direction"
        ]
        == "improving"
    )

    assert (
        result["analysis"][
            "operating_cash_flow_direction"
        ]
        == "improving"
    )

    mock_session.close.assert_called_once()