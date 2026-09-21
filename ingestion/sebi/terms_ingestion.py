from pathlib import Path

from ingestion.sebi.structured_terms import (
    build_sebi_ipo_record,
)

from ingestion.sebi.terms_source import (
    SEBIIPOTermsSource,
)

from ingestion.structured_persistence import (
    persist_ipo_record,
)


class SEBIIPOTermsIngestion:
    """
    Extract structured IPO terms from a SEBI DRHP
    and persist them into the existing IPO table.
    """

    def __init__(
        self,
        source: SEBIIPOTermsSource | None = None,
    ):
        self.source = (
            source
            or SEBIIPOTermsSource()
        )

    def ingest(
        self,
        *,
        ipo_id: str,
        company_name: str,
        pdf_path: str | Path,
    ) -> dict:
        """
        Extract terms from a DRHP and persist them.
        """

        terms = self.source.extract(
            pdf_path
        )

        record = build_sebi_ipo_record(
            ipo_id=ipo_id,
            company_name=company_name,
            terms=terms,
        )

        return persist_ipo_record(
            record
        )