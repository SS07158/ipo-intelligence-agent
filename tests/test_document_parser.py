from ingestion.sebi.document_parser import parse_document


PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"


def test_parse_document():
    pages = parse_document(PDF_PATH)

    assert len(pages) > 0

    first_page = pages[0]

    assert "page_number" in first_page
    assert "section" in first_page
    assert "text" in first_page

    assert first_page["page_number"] == 1
    assert isinstance(first_page["section"], str)
    assert isinstance(first_page["text"], str)