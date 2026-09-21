from unittest.mock import patch

from app.tools.financial_analysis import (
    analyze_financial_performance,
    analyze_financial_performance_tool,
)


def test_financial_performance_tool_exists():
    assert analyze_financial_performance_tool.name == (
        "analyze_financial_performance_tool"
    )


def test_financial_performance_tool_calls_analysis():

    expected = {
        "found": True,
        "company_name": "CULT.FIT LIMITED",
        "revenue_growth_percent": 85.68,
        "profit_loss_direction": "loss narrowed",
        "adjusted_ebitda_direction": "improved",
        "operating_cash_flow_direction": "improved",
    }

    with patch(
        "app.tools.financial_analysis.analyze_financial_performance",
        return_value=expected,
    ) as mock_analysis:

        result = analyze_financial_performance_tool.invoke(
            {"company_name": "CULT.FIT LIMITED"}
        )

    mock_analysis.assert_called_once_with("CULT.FIT LIMITED")
    assert result == expected