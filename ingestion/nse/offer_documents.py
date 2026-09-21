from dataclasses import dataclass


NSE_ARCHIVE_BASE = (
    "https://nsearchives.nseindia.com/"
)


@dataclass
class NSEDocument:
    """
    Official NSE offer document.
    """

    company_name: str

    document_type: str

    document_url: str

    document_date: str | None = None

    source: str = "NSE"

    archive_type: str = "direct"


class NSEOfferDocumentSource:
    """
    NSE offer-document source.

    This class is responsible for representing and
    validating official NSE document URLs.

    Discovery of the URL itself is handled separately.
    """

    SUPPORTED_DOCUMENT_TYPES = {
        "DRHP",
        "RHP",
    }

    def resolve_document(
        self,
        company_name: str,
        document_type: str,
        document_url: str,
        document_date: str | None = None,
    ) -> NSEDocument:
        """
        Validate and construct an NSEDocument.

        The URL must already have been discovered from
        an official NSE source.
        """

        company_name = (
            company_name.strip()
        )

        document_type = (
            document_type.strip().upper()
        )

        document_url = (
            document_url.strip()
        )

        if not company_name:
            raise ValueError(
                "company_name cannot be empty."
            )

        if (
            document_type
            not in self.SUPPORTED_DOCUMENT_TYPES
        ):
            raise ValueError(
                "document_type must be "
                "DRHP or RHP."
            )

        if not document_url:
            raise ValueError(
                "document_url cannot be empty."
            )

        if not self.is_nse_archive_url(
            document_url
        ):
            raise ValueError(
                "document_url must belong to "
                "the NSE archive domain."
            )

        archive_type = (
            "zip"
            if document_url.lower().endswith(
                ".zip"
            )else "direct"
        )

        return NSEDocument(
            company_name=company_name,
            document_type=document_type,
            document_url=document_url,
            document_date=document_date,
            archive_type=archive_type,
        )

    @staticmethod
    def is_nse_archive_url(
        document_url: str,
    ) -> bool:
        """
        Check whether a URL belongs to the
        official NSE archive domain.
        """

        return document_url.startswith(
            NSE_ARCHIVE_BASE
        )