from datetime import datetime, timezone

from app.ingestion.models import (
    RawDocument,
    StructuredIPOData,
)

from app.ingestion.source import (
    IPODataSource,
)


class FakeIPODataSource(
    IPODataSource
):
    """
    Development source used to verify
    the ingestion architecture.
    """

    def fetch_ipo(
        self,
        company_name: str,
    ) -> StructuredIPOData | None:

        if company_name.upper() != (
            "CULT.FIT LIMITED"
        ):
            return None

        return StructuredIPOData(
            ipo_id="cultfit-2026",
            company_name="CULT.FIT LIMITED",
            source="FAKE",
            discovered_at=datetime.now(
                timezone.utc
            ),
            data={
                "fresh_issue": 950.0,
                "offer_for_sale_shares": 178609200,
            },
        )

    def fetch_documents(
        self,
        company_name: str,
    ) -> list[RawDocument]:

        if company_name.upper() != (
            "CULT.FIT LIMITED"
        ):
            return []

        return [
            RawDocument(
                document_id=(
                    "cultfit-drhp-2026"
                ),
                company_name=(
                    "CULT.FIT LIMITED"
                ),
                document_type="DRHP",
                source="FAKE",
                source_url=(
                    "https://example.com/drhp"
                ),
                discovered_at=datetime.now(
                    timezone.utc
                ),
            )
        ]