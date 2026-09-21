from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from ingestion.sebi.ingest_document import (
    ingest_document,
)


CONFIG = SEBIDocumentConfig(
    document_id="example-ipo-drhp-2026",
    company_name="EXAMPLE LIMITED",
    document_type="DRHP",
    source="SEBI",
    source_url="https://example.com/drhp",
    local_path="data/raw/sebi/example/drhp.pdf",
)


def main() -> None:
    ingest_document(
        CONFIG
    )


if __name__ == "__main__":
    main()