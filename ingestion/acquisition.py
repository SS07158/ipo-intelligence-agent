from pathlib import Path

from ingestion.document_resolver import (
    DocumentResolver,
)

from ingestion.download import (
    download_offer_document,
)

from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from ingestion.sebi.ingest_document import (
    ingest_document,
)
from database.database import SessionLocal
from database.ipo_repository import (
    get_or_create_ipo,
)


RAW_ROOT = Path(
    "data/raw"
)


class IPOAcquisitionService:
    """
    End-to-end IPO document acquisition service.

    Flow:

        resolve
          ↓
        download
          ↓
        validate
          ↓
        register
          ↓
        idempotent ingestion
    """

    def __init__(
        self,
        resolver: DocumentResolver,
    ):
        self.resolver = resolver

    def acquire(
        self,
        *,
        ipo_id: str,
        company_name: str,
        document_id: str,
        document_type: str,
        version: str | None = None,
        published_at=None,
    ) -> dict:
        """
        Acquire and ingest one IPO document.
        """
        session = SessionLocal()

        try:
            ipo = get_or_create_ipo(
                session,
                ipo_id=ipo_id,
                company_name=company_name,
                issue_size=None,
                price_band_low=None,
                price_band_high=None,
                lot_size=None,
                issue_open_date=None,
                issue_close_date=None,
                listing_date=None,
                fresh_issue=None,
                offer_for_sale=None,
                offer_for_sale_shares=None,
            )

            print(
                f"IPO registered: "
                f"{ipo.company_name} "
                f"({ipo.ipo_id})"
            )

        finally:
            session.close()
            
        resolved = self.resolver.resolve(
            company_name=company_name,
            document_type=document_type,
        )

        if resolved is None:
            return {
                "success": False,
                "company_name": company_name,
                "document_type": document_type,
                "message": (
                    f"Could not find an official "
                    f"{document_type} document for "
                    f"{company_name}."
                ),
            }

        company_slug = (
            company_name
            .strip()
            .lower()
            .replace(".", "")
            .replace(",", "")
            .replace(" ", "_")
        )

        filename = (
            f"{company_slug}_"
            f"{document_type.lower()}.pdf"
        )

        destination = (
            RAW_ROOT
            / resolved.source.lower()
            / company_slug
            / filename
        )

        download_result = (
            download_offer_document(
                url=resolved.document_url,
                destination=destination,
                document_type=document_type,
            )
        )

        config = SEBIDocumentConfig(
            ipo_id=ipo_id,
            document_id=document_id,
            company_name=company_name,
            document_type=document_type,

            # Regulatory/filling provenance.
            source="SEBI",

            # The filing page discovered through SEBI.
            source_url=None,

            # The actual source that supplied the file.
            acquisition_source=resolved.source,

            # The actual PDF/ZIP URL.
            document_url=resolved.document_url,

            local_path=download_result[
                "local_path"
            ],

            version=version,
            published_at=published_at,
        )

        indexed_chunks = ingest_document(
            config
        )

        return {
            "success": True,
            "ipo_id": ipo_id,
            "document_id": document_id,
            "company_name": company_name,
            "document_type": document_type,
            "source": resolved.source,
            "source_url": resolved.document_url,
            "local_path": download_result[
                "local_path"
            ],
            "archive_type": download_result[
                "archive_type"
            ],
            "sha256": download_result[
                "sha256"
            ],
            "size_bytes": download_result[
                "size_bytes"
            ],
            "indexed_chunks": indexed_chunks,
        }