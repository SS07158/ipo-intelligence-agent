from ingestion.nse.discovery import (
    NSEOfferDocumentDiscovery,
)

from ingestion.nse.structured_ipo import (
    build_structured_ipo_record,
)

from ingestion.structured_data import (
    StructuredIPORecord,
)


class NSEStructuredIPODataSource:
    """
    Retrieve structured IPO metadata from NSE.
    """

    def __init__(
        self,
        discovery: NSEOfferDocumentDiscovery | None = None,
    ):
        self.discovery = (
            discovery
            or NSEOfferDocumentDiscovery()
        )

    def fetch(
        self,
        *,
        ipo_id: str,
        company_name: str,
    ) -> StructuredIPORecord | None:
        """
        Fetch and normalize structured IPO data.
        """

        raw = self.discovery.get_company_record(
            company_name
        )

        if raw is None:
            return None

        return build_structured_ipo_record(
            raw,
            ipo_id=ipo_id,
            source="NSE",
        )