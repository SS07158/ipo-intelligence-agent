from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)


def test_different_document_types_have_distinct_ids():

    drhp = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-drhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url="https://example.com/drhp",
        local_path="data/raw/drhp.pdf",
        version="2026-07",
    )

    rhp = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-rhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="RHP",
        source="SEBI",
        source_url="https://example.com/rhp",
        local_path="data/raw/rhp.pdf",
        version="2026-08",
    )

    assert (
        drhp.document_id
        != rhp.document_id
    )

    assert (
        drhp.document_type
        != rhp.document_type
    )

    assert (
        drhp.version
        != rhp.version
    )