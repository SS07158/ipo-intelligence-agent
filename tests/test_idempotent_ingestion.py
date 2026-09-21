from unittest.mock import patch

from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from ingestion.sebi.ingest_document import (
    ingest_document,
)


def test_second_ingestion_is_skipped():

    config = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-drhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url="https://example.com",
        local_path="data/test/drhp.pdf",
    )

    with patch(
        "ingestion.sebi.ingest_document.register_document"
    ), patch(
        "ingestion.sebi.ingest_document.is_document_indexed",
        return_value=True,
    ), patch(
        "ingestion.sebi.ingest_document.DocumentIndexer"
    ) as mock_indexer:

        count = ingest_document(
            config
        )

        assert count == 0

        mock_indexer.return_value.index_document.assert_not_called()