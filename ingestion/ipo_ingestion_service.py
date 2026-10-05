from ingestion.acquisition import IPOAcquisitionService
from ingestion.document_resolver import DocumentResolver


class IPOIngestionService:
    """
    High-level service for adding an IPO to the system.

    This is the operational entry point that the future
    admin API/UI will call.

    Flow:

        Admin
          ↓
        IPOIngestionService
          ↓
        IPOAcquisitionService
          ↓
        Resolve → Download → Register → Ingest → Index
    """

    def __init__(
        self,
        resolver: DocumentResolver,
    ):
        self.acquisition_service = IPOAcquisitionService(
            resolver=resolver,
        )

    def add_ipo(
        self,
        *,
        ipo_id: str,
        company_name: str,
        document_id: str,
        document_type: str = "DRHP",
        version: str | None = None,
        published_at=None,
    ) -> dict:
        """
        Add and ingest one IPO.
        """

        if not company_name.strip():
            raise ValueError(
                "company_name cannot be empty."
            )

        if not ipo_id.strip():
            raise ValueError(
                "ipo_id cannot be empty."
            )

        if not document_id.strip():
            raise ValueError(
                "document_id cannot be empty."
            )

        document_type = document_type.strip().upper()

        if document_type not in {"DRHP", "RHP"}:
            raise ValueError(
                "document_type must be DRHP or RHP."
            )

        return self.acquisition_service.acquire(
            ipo_id=ipo_id.strip(),
            company_name=company_name.strip(),
            document_id=document_id.strip(),
            document_type=document_type,
            version=version,
            published_at=published_at,
        )