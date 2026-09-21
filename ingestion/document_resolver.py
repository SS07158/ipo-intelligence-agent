from ingestion.document_source import (
    ResolvedDocument,
)

from ingestion.nse.discovery import (
    NSEOfferDocumentDiscovery,
)

from ingestion.official_source import (
    OfficialOfferDocumentSource,
)


class DocumentResolver:
    """
    Resolve an official IPO document using
    at most three source families:

    1. SEBI
    2. NSE/BSE
    3. Official BRLM/issuer
    """

    def __init__(
        self,
        sebi_source,
        nse_source: NSEOfferDocumentDiscovery | None = None,
        official_source: (
            OfficialOfferDocumentSource
            | None
        ) = None,
    ):
        self.sebi_source = sebi_source

        self.nse_source = (
            nse_source
            or NSEOfferDocumentDiscovery()
        )

        self.official_source = (
            official_source
        )

    def resolve(
        self,
        company_name: str,
        document_type: str,
    ) -> ResolvedDocument | None:
        """
        Resolve a DRHP/RHP document.

        Source priority:
            SEBI → NSE/BSE → BRLM/issuer
        """

        company_name = (
            company_name.strip()
        )

        document_type = (
            document_type.strip().upper()
        )

        if not company_name:
            raise ValueError(
                "company_name cannot be empty."
            )

        if document_type not in {
            "DRHP",
            "RHP",
        }:
            raise ValueError(
                "document_type must be "
                "DRHP or RHP."
            )

        # -------------------------------------------------
        # SOURCE 1 — SEBI
        # -------------------------------------------------

        sebi_document = (
            self._resolve_from_sebi(
                company_name,
                document_type,
            )
        )

        if sebi_document is not None:
            return  ResolvedDocument(
                company_name=sebi_document.company_name,
                document_type=sebi_document.document_type,
                document_url=sebi_document.document_url,
                source="SEBI",
                source_url=sebi_document.source_url,
                document_date=sebi_document.document_date,
            )

        # -------------------------------------------------
        # SOURCE 2 — NSE/BSE
        # -------------------------------------------------

        nse_document = (
            self.nse_source.find_document(
                company_name,
                document_type,
            )
        )

        if nse_document is not None:
            return ResolvedDocument(
            company_name=(
                nse_document.company_name
            ),
            document_type=(
                nse_document.document_type
            ),
            document_url=(
                nse_document.document_url
            ),
            source="NSE",
            document_date=(
                nse_document.document_date
            ),
            archive_type=(
                nse_document.archive_type
            ),
        )

        # -------------------------------------------------
        # SOURCE 3 — OFFICIAL BRLM / ISSUER
        # -------------------------------------------------

        if self.official_source is not None:

            official_document = (
                self.official_source.find_document(
                    company_name,
                    document_type,
                )
            )

            if official_document is not None:
                return official_document

        # -------------------------------------------------
        # NOTHING FOUND
        # -------------------------------------------------

        return None

    def _resolve_from_sebi(
        self,
        company_name: str,
        document_type: str,
    ) -> ResolvedDocument | None:
        """
        Resolve from the existing SEBI discovery layer.
        """

        documents = (
            self.sebi_source.discover(
                company_name
            )
        )

        for document in documents:

            if (
                document.document_type.upper()
                != document_type
            ):
                continue

            document_url = (
                self.sebi_source
                .extract_document_url(
                    document.detail_url,
                    document_type,
                )
            )

            if document_url is None:
                continue

            return ResolvedDocument(
                company_name=(
                    company_name
                ),
                document_type=(
                    document_type
                ),
                document_url=(
                    document_url
                ),
                source="SEBI",
                document_date=(
                    document.discovered_date
                ),
            )

        return None