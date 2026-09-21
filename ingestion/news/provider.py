from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsArticleData:
    """
    Normalized representation of a news article
    returned by any news provider.
    """

    title: str
    summary: str | None
    url: str | None
    source: str | None
    author: str | None
    published_at: datetime | None
    external_id: str | None
    provider : str | None = None


class NewsProvider(ABC):
    """
    Common interface for all news providers.
    """

    @abstractmethod
    def fetch(
        self,
        query: str,
        limit: int = 20,
    ) -> list[NewsArticleData]:
        """
        Fetch and normalize news articles.
        """
        raise NotImplementedError