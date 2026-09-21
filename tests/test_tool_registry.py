from app.agents.tool_registry import TOOLS


def test_tools_registered():
    names = {
        tool.name
        for tool in TOOLS
    }

    assert "lookup_ipo_tool" in names
    assert "lookup_financials_tool" in names
    assert "analyze_revenue_growth_tool" in names
    assert "search_ipo_documents_tool" in names