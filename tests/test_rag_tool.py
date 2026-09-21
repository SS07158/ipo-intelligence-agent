from unittest.mock import patch

from app.tools.rag_tools import search_ipo_documents


def test_rag_tool():
    expected = {
        "answer": "Example answer.",
        "evidence": [],
        "citation_validation": {
            "valid": True,
            "references": [],
            "invalid_references": [],
        },
    }

    with patch(
        "app.tools.rag_tools.RAGService"
    ) as mock_service:

        mock_service.return_value.answer.return_value = (
            expected
        )

        result = search_ipo_documents(
            "What are the risks?",
            top_k=3,
            section="INTERNAL RISK",
        )

        assert result == expected

        mock_service.return_value.answer.assert_called_once_with(
            "What are the risks?",
            top_k=3,
            where={
                "section": "INTERNAL RISKS",
            },
        )

def test_normalize_risk_section():
    from app.tools.rag_tools import normalize_section

    assert (
        normalize_section("Risk Factors")
        == "INTERNAL RISKS"
    )


def test_normalize_industry_section():
    from app.tools.rag_tools import normalize_section

    assert (
        normalize_section("industry")
        == "INDUSTRY OVERVIEW"
    )

def test_normalize_risk_factors():
    from app.tools.rag_tools import normalize_section

    assert (
        normalize_section("risk_factors")
        == "INTERNAL RISKS"
    )