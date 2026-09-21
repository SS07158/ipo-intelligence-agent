from app.agents.synthesizer import (
    synthesize_tool_results,
)


def test_multi_tool_synthesis_mentions_both_topics():

    tool_results = [
        {
            "tool": "analyze_revenue_growth_tool",
            "args": {
                "company_name": "CULT.FIT LIMITED",
            },
            "result": {
                "start_period": "FY2024",
                "end_period": "FY2026",
                "start_value": 9266.62,
                "end_value": 17206.06,
                "unit": "INR million",
                "total_growth_percent": 85.68,
                "cagr_percent": 36.26,
                "citations": [],
            },
        },
        {
            "tool": "search_ipo_documents_tool",
            "args": {},
            "result": {
                "answer": (
                    "Risks include product liability, "
                    "inventory management, regulatory "
                    "compliance, and brand reputation."
                ),
                "evidence": [
                    {
                        "citation": {
                            "company": "CULT.FIT LIMITED",
                            "document_type": "DRHP",
                            "source": "SEBI",
                            "page_number": 40,
                        }
                    }
                ],
            },
        },
    ]

    result = synthesize_tool_results(
        question=(
            "How has CULT.FIT's revenue changed, "
            "and what risks could affect that growth?"
        ),
        tool_results=tool_results,
    )

    assert result.answer

    assert (
        "9,266.62"
        in result.answer
    )

    assert (
        "17,206.06"
        in result.answer
    )

    assert "Risks:" in result.answer

    assert (
        "product liability"
        in result.answer.lower()
    )

def test_synthesis_includes_financial_performance():

    tool_results = [
        {
            "tool": "analyze_financial_performance_tool",
            "result": {
                "found": True,
                "company_name": "CULT.FIT LIMITED",
                "metrics": {
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
                },
                "analysis": {
                    "revenue_growth_percent": 85.67784154308691,
                    "loss_reduction_percent": -71.65328630228106,
                    "profit_loss_direction": "improving",
                    "adjusted_ebitda_change": 2849.70,
                    "adjusted_ebitda_direction": "improving",
                    "operating_cash_flow_change": 3248.46,
                    "operating_cash_flow_direction": "improving",
                },
            },
        }
    ]

    answer = synthesize_tool_results(
        "How has CULT.FIT's financial performance changed?",
        tool_results,
    )

    assert "Revenue from operations increased" in answer.answer
    assert "loss narrowed" in answer.answer.lower()
    assert "Adjusted EBITDA improved" in answer.answer
    assert "Operating cash flow improved" in answer.answer