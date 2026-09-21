from app.tools.financial_tool import (
    analyze_revenue_growth,
)


def test_revenue_growth_analysis():
    result = analyze_revenue_growth(
        "CULT.FIT LIMITED",
    )

    assert result["found"] is True

    assert result["start_period"] == "FY2024"
    assert result["end_period"] == "FY2026"

    assert result["total_growth_percent"] > 0
    assert result["cagr_percent"] > 0