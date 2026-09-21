from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ingestion.download import (
    DocumentDownloadError,
    download_document,
    download_offer_document,
)


def test_download_document(
    tmp_path: Path,
):

    pdf_content = (
        b"%PDF-1.7\n"
        b"test pdf content"
    )

    mock_response = MagicMock()

    mock_response.status = 200

    mock_response.read.return_value = (
        pdf_content
    )

    mock_response.headers = {
        "Content-Type": "application/pdf"
    }

    # Important:
    # urlopen(...) is used inside a `with` block.
    mock_response.__enter__.return_value = (
        mock_response
    )

    mock_response.__exit__.return_value = None

    with patch(
        "ingestion.download.urlopen",
        return_value=mock_response,
    ):

        result = download_document(
            "https://example.com/test.pdf",
            tmp_path / "test.pdf",
        )

    assert (
        result["size_bytes"]
        == len(pdf_content)
    )

    assert (
        result["content_type"]
        == "application/pdf"
    )

    assert result["sha256"]

    assert (
        Path(
            result["local_path"]
        ).exists()
    )


def test_reject_invalid_pdf(
    tmp_path: Path,
):

    mock_response = MagicMock()

    mock_response.status = 200

    mock_response.read.return_value = (
        b"<html>error page</html>"
    )

    mock_response.headers = {
        "Content-Type": "text/html"
    }

    mock_response.__enter__.return_value = (
        mock_response
    )

    mock_response.__exit__.return_value = None

    with patch(
        "ingestion.download.urlopen",
        return_value=mock_response,
    ):

        with pytest.raises(
            DocumentDownloadError
        ):
            download_document(
                "https://example.com/test.pdf",
                tmp_path / "test.pdf",
            )

def test_download_offer_document_zip(
    tmp_path: Path,
):
    from zipfile import ZipFile
    from io import BytesIO

    buffer = BytesIO()

    with ZipFile(
        buffer,
        "w",
    ) as archive:

        archive.writestr(
            "Cultfit_DRHP.pdf",
            b"%PDF-1.7\nDRHP content",
        )

    zip_content = buffer.getvalue()

    mock_response = MagicMock()

    mock_response.status = 200

    mock_response.read.return_value = (
        zip_content
    )

    mock_response.headers = {
        "Content-Type": "application/zip"
    }

    mock_response.__enter__.return_value = (
        mock_response
    )

    mock_response.__exit__.return_value = None

    with patch(
        "ingestion.download.urlopen",
        return_value=mock_response,
    ):

        result = download_offer_document(
            "https://nsearchives.nseindia.com/"
            "corporate/Cultfit.zip",
            tmp_path / "cultfit_drhp.pdf",
            "DRHP",
        )

    assert (
        result["archive_type"]
        == "zip"
    )

    assert (
        Path(
            result["local_path"]
        ).exists()
    )

    assert (
        Path(
            result["local_path"]
        ).read_bytes()
        .startswith(b"%PDF")
    )

    assert result["sha256"]