from unittest.mock import patch

from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from ingestion.sebi.ingest_document import (
    ingest_document,
)


def test_ingest_document():

    config = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="test-drhp",
        company_name="TEST LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url="https://example.com/drhp",
        local_path="data/raw/cultfit_drhp.pdf",
    )

    with patch(
        "ingestion.sebi.ingest_document.DocumentIndexer"
    ) as mock_indexer:

        mock_indexer.return_value.index_document.return_value = 42

        count = ingest_document(
            config
        )

        assert count == 42

        mock_indexer.return_value.index_document.assert_called_once_with(
            "data/raw/cultfit_drhp.pdf",
            config=config
        )