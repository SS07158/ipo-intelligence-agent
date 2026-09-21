from abc import ABC, abstractmethod

from ingestion.document_source import (
    ResolvedDocument,
)


class OfficialOfferDocumentSource(
    ABC
):
    """
    Interface for the third and final
    official document source.

    This source should be an official
    BRLM or issuer offer-document page.
    """

    @abstractmethod
    def find_document(
        self,
        company_name: str,
        document_type: str,
    ) -> ResolvedDocument | None:
        """
        Find an official DRHP/RHP document.
        """
        raise NotImplementedError