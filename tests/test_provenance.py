from app.agents.provenance import (
    format_citation,
)


def test_format_citation_with_page():

    citation = {
        "company": "CULT.FIT LIMITED",
        "document_type": "DRHP",
        "source": "SEBI",
        "page_number": 40,
    }

    result = format_citation(
        citation
    )

    assert (
        result
        == "CULT.FIT LIMITED — DRHP — SEBI, p. 40"
    )


def test_format_citation_without_page():

    citation = {
        "company": "CULT.FIT LIMITED",
        "document_type": "DRHP",
        "source": "SEBI",
        "page_number": None,
    }

    result = format_citation(
        citation
    )

    assert (
        result
        == "CULT.FIT LIMITED — DRHP — SEBI"
    )