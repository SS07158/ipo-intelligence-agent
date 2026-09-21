from app.agents.tool_registry import (
    lookup_financials_tool,
    lookup_ipo_tool,
)


print(
    lookup_ipo_tool.invoke(
        {
            "company_name": "CULT.FIT",
        }
    )
)

print(
    lookup_financials_tool.invoke(
        {
            "company_name": "CULT.FIT LIMITED",
            "metric_name": "revenue_from_operations",
            "period": "FY2026",
        }
    )
)