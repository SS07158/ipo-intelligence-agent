from ingestion.sebi.official_offer_source import (
    OfferDocumentSource,
)
from ingestion.sebi.sebi_browser import (
    SEBIBrowserDiscovery,
)


class SEBIDocumentResolver:
    """
    Resolve the actual document URL using SEBI first,
    then an official offer-document source.
    """

    def __init__(
        self,
        headless: bool = True,
    ):
        self.sebi = SEBIBrowserDiscovery(
            headless=headless
        )

        self.offer_docs = (
            OfferDocumentSource(
                headless=headless
            )
        )

    def resolve(
        self,
        company_name: str,
        document_type: str,
    ) -> str | None:

        # Step 1: discover the SEBI filing.
        documents = self.sebi.discover(
            company_name
        )

        for document in documents:

            if (
                document.document_type.upper()
                != document_type.upper()
            ):
                continue

            url = self.sebi.extract_document_url(
                document.detail_url,
                document_type,
            )

            if url:
                return url

        # Step 2: official fallback.
        return self.offer_docs.find_document(
            company_name,
            document_type,
        )