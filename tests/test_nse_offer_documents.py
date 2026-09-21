import pytest

from ingestion.nse.offer_documents import (
    NSEOfferDocumentSource,
)


def test_resolve_nse_document():

    source = NSEOfferDocumentSource()

    result = source.resolve_document(
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        document_url=(
            "https://nsearchives.nseindia.com/"
            "corporate/"
            "Registration_07072026083041_DRHP.pdf"
        ),
        document_date="2026-07-06",
    )

    assert (
        result.company_name
        == "CULT.FIT LIMITED"
    )

    assert (
        result.document_type
        == "DRHP"
    )

    assert (
        result.document_date
        == "2026-07-06"
    )

    assert (
        result.document_url.startswith(
            "https://nsearchives.nseindia.com/"
        )
    )


def test_reject_non_nse_url():

    source = NSEOfferDocumentSource()

    with pytest.raises(ValueError):

        source.resolve_document(
            company_name="CULT.FIT LIMITED",
            document_type="DRHP",
            document_url=(
                "https://example.com/drhp.pdf"
            ),
        )