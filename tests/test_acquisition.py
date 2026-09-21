from pathlib import Path
from unittest.mock import MagicMock, patch

from ingestion.acquisition import (
    IPOAcquisitionService,
)

from ingestion.document_source import (
    ResolvedDocument,
)


def test_acquisition_uses_resolved_source(
    tmp_path: Path,
):

    resolver = MagicMock()

    resolver.resolve.return_value = (
        ResolvedDocument(
            company_name="TEST LIMITED",
            document_type="DRHP",
            document_url=(
                "https://nsearchives.nseindia.com/"
                "corporate/test.zip"
            ),
            source="NSE",
            archive_type="zip",
        )
    )

    service = IPOAcquisitionService(
        resolver=resolver
    )

    download_result = {
        "local_path": str(
            tmp_path / "test.pdf"
        ),
        "archive_type": "zip",
        "sha256": "abc123",
        "size_bytes": 100,
    }

    with patch(
        "ingestion.acquisition.download_offer_document",
        return_value=download_result,
    ), patch(
        "ingestion.acquisition.ingest_document",
        return_value=10,
    ):

        result = service.acquire(
            ipo_id="test-ipo",
            company_name="TEST LIMITED",
            document_id="test-drhp",
            document_type="DRHP",
        )

    assert result["success"] is True

    assert (
        result["source"]
        == "NSE"
    )

    assert (
        result["indexed_chunks"]
        == 10
    )

    resolver.resolve.assert_called_once_with(
        company_name="TEST LIMITED",
        document_type="DRHP",
    )