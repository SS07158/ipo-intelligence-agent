from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)


def test_sebi_document_config():

    config = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-drhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url="https://example.com/drhp",
        local_path="data/cultfit/drhp.pdf",
    )

    assert (
        config.document_id
        == "cultfit-drhp-2026"
    )

    assert (
        config.company_name
        == "CULT.FIT LIMITED"
    )

    assert (
        config.document_type
        == "DRHP"
    )

    assert (
        config.source
        == "SEBI"
    )

def test_document_version():

    config = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-drhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url="https://example.com/drhp",
        local_path="data/raw/drhp.pdf",
        version="2026-07",
    )

    assert config.version == "2026-07"