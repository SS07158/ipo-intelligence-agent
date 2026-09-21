from ingestion.nse.ipo_data_source import (
    NSEStructuredIPODataSource,
)

from ingestion.structured_persistence import (
    persist_ipo_record,
)


class NSEStructuredIPOIngestion:
    """
    Fetch structured IPO data from NSE and
    persist it into the existing IPO table.
    """

    def __init__(
        self,
        source: NSEStructuredIPODataSource | None = None,
    ):
        self.source = (
            source
            or NSEStructuredIPODataSource()
        )

    def ingest(
        self,
        *,
        ipo_id: str,
        company_name: str,
    ) -> dict:

        record = self.source.fetch(
            ipo_id=ipo_id,
            company_name=company_name,
        )

        if record is None:
            return {
                "success": False,
                "message": (
                    f"NSE does not have a structured "
                    f"record for {company_name}."
                ),
            }

        return persist_ipo_record(
            record
        )