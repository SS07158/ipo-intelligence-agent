from unittest.mock import MagicMock

from ingestion.document_resolver import (
    DocumentResolver,
)

from ingestion.document_source import (
    ResolvedDocument,
)


def test_sebi_has_priority():

    sebi = MagicMock()

    sebi.discover.return_value = [
        MagicMock(
            document_type="DRHP",
            detail_url="sebi-detail",
            discovered_date="2026-07-09",
        )
    ]

    sebi.extract_document_url.return_value = (
        "https://sebi.example/drhp.pdf"
    )

    nse = MagicMock()

    official = MagicMock()

    resolver = DocumentResolver(
        sebi_source=sebi,
        nse_source=nse,
        official_source=official,
    )

    result = resolver.resolve(
        "CULT.FIT LIMITED",
        "DRHP",
    )

    assert result is not None

    assert (
        result.source
        == "SEBI"
    )

    assert (
        result.document_url
        == "https://sebi.example/drhp.pdf"
    )

    nse.find_document.assert_not_called()

    official.find_document.assert_not_called()


def test_nse_is_used_when_sebi_has_no_pdf():

    sebi = MagicMock()

    sebi.discover.return_value = [
        MagicMock(
            document_type="DRHP",
            detail_url="sebi-detail",
            discovered_date="2026-07-09",
        )
    ]

    sebi.extract_document_url.return_value = None

    nse = MagicMock()

    nse.find_document.return_value = (
        MagicMock(
            company_name="CULT.FIT LIMITED",
            document_type="DRHP",
            document_url=(
                "https://nsearchives.nseindia.com/"
                "corporate/Cultfit.zip"
            ),
            document_date="06-Jul-2026",
            archive_type="zip",
        )
    )

    official = MagicMock()

    resolver = DocumentResolver(
        sebi_source=sebi,
        nse_source=nse,
        official_source=official,
    )

    result = resolver.resolve(
        "CULT.FIT LIMITED",
        "DRHP",
    )

    assert result is not None

    assert (
        result.source
        == "NSE"
    )

    assert (
        result.archive_type
        == "zip"
    )

    official.find_document.assert_not_called()


def test_official_source_is_final_fallback():

    sebi = MagicMock()

    sebi.discover.return_value = []

    nse = MagicMock()

    nse.find_document.return_value = None

    official = MagicMock()

    official.find_document.return_value = (
        ResolvedDocument(
            company_name="TEST LIMITED",
            document_type="DRHP",
            document_url=(
                "https://official.example/drhp.pdf"
            ),
            source="BRLM",
        )
    )

    resolver = DocumentResolver(
        sebi_source=sebi,
        nse_source=nse,
        official_source=official,
    )

    result = resolver.resolve(
        "TEST LIMITED",
        "DRHP",
    )

    assert result is not None

    assert (
        result.source
        == "BRLM"
    )

    assert (
        result.document_url
        == "https://official.example/drhp.pdf"
    )


def test_no_fourth_source():

    sebi = MagicMock()
    sebi.discover.return_value = []

    nse = MagicMock()
    nse.find_document.return_value = None

    official = MagicMock()
    official.find_document.return_value = None

    resolver = DocumentResolver(
        sebi_source=sebi,
        nse_source=nse,
        official_source=official,
    )

    result = resolver.resolve(
        "UNKNOWN LIMITED",
        "DRHP",
    )

    assert result is None