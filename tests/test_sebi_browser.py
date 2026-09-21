from ingestion.sebi.discovery import (
    DiscoveredSEBIDocument,
)


def test_document_model():

    document = (
        DiscoveredSEBIDocument(
            company_name="CULT.FIT LIMITED",
            document_type="DRHP",
            detail_url=(
                "https://www.sebi.gov.in/"
                "filings/public-issues/"
                "jul-2026/"
                "cult-fit-limited-drhp_102714.html"
            ),
        )
    )

    assert (
        document.company_name
        == "CULT.FIT LIMITED"
    )

    assert (
        document.document_type
        == "DRHP"
    )

    assert "cult-fit" in (
        document.detail_url
    )