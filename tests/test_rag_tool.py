from unittest.mock import patch

from app.tools.rag_tools import search_ipo_documents


def test_rag_tool_rejects_unscoped_search():
    import pytest

    with pytest.raises(
        ValueError,
        match="Unfiltered document search is not permitted",
    ):
        search_ipo_documents(
            "What are the risks?",
            top_k=3,
            section="INTERNAL RISK",
        )


def test_rag_tool_filters_by_selected_ipo():
    from types import SimpleNamespace
    from unittest.mock import MagicMock, patch

    expected = {
        "answer": "Example answer.",
        "evidence": [],
        "citation_validation": {
            "valid": True,
            "references": [],
            "invalid_references": [],
        },
    }

    fake_ipo = SimpleNamespace(
        ipo_id="koolking-industries-2026",
        company_name="Koolking Industries India Limited",
    )
    fake_session = MagicMock()

    with (
        patch(
            "database.database.SessionLocal",
            return_value=fake_session,
        ),
        patch(
            "database.ipo_repository.get_ipo_by_id",
            return_value=fake_ipo,
        ),
        patch(
            "app.tools.rag_tools.get_rag_service"
        ) as mock_get_service,
    ):
        mock_get_service.return_value.answer.return_value = expected

        result = search_ipo_documents(
            "What are the risks?",
            top_k=3,
            section="INTERNAL RISK",
            ipo_id="koolking-industries-2026",
        )

    assert result == expected

    mock_get_service.return_value.answer.assert_called_once_with(
        "What are the risks?",
        top_k=3,
        where={
            "section": "INTERNAL RISKS",
            "ipo_id": "koolking-industries-2026",
        },
    )

    fake_session.close.assert_called_once()

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