from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)


def test_document_config_has_ipo_id():

    config = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-drhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url="https://example.com/drhp",
        local_path="data/raw/cultfit/drhp.pdf",
    )

    assert (
        config.ipo_id
        == "cultfit-2026"
    )

    assert (
        config.document_id
        == "cultfit-drhp-2026"
    )

from unittest.mock import MagicMock, patch

from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from ingestion.sebi.register_document import (
    register_document,
)


def test_register_document_existing():
    config = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-drhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url="https://example.com/drhp",
        local_path="data/raw/cultfit/drhp.pdf",
    )

    # We will expand this test once we inspect
    # the database session behavior in the project.
    assert config.ipo_id == "cultfit-2026"