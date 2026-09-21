from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from ingestion.sebi.ingest_document import (
    ingest_document,
)


CONFIG = SEBIDocumentConfig(
    ipo_id="cultfit-2026",
    document_id="cultfit-drhp-2026",
    company_name="CULT.FIT LIMITED",
    document_type="DRHP",
    source="SEBI",
    source_url=(
        "https://www.sebi.gov.in/"
        "filings/public-issues/jul-2026/"
        "cult-fit-limited-drhp_102714.html"
    ),
    local_path=(
        "data/raw/sebi/cultfit/"
        "cultfit_drhp.pdf"
    ),
    version="2026-07",
    published_at=None
)


def main() -> None:
    ingest_document(
        CONFIG
    )


if __name__ == "__main__":
    main()