from abc import ABC, abstractmethod

from app.ingestion.models import (
    RawDocument,
    StructuredIPOData,
)


class IPODataSource(ABC):
    """
    Common interface for external IPO sources.
    """

    @abstractmethod
    def fetch_ipo(
        self,
        company_name: str,
    ) -> StructuredIPOData | None:
        """
        Fetch structured IPO information.
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_documents(
        self,
        company_name: str,
    ) -> list[RawDocument]:
        """
        Fetch IPO-related documents.
        """
        raise NotImplementedError