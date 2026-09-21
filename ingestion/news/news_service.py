from ingestion.news.provider import (
    NewsArticleData,
    NewsProvider,
)


class NewsService:
    """
    Coordinate multiple news providers and return
    a single normalized collection of articles.
    """

    def __init__(
        self,
        providers: list[tuple[str, NewsProvider]],
    ):
        self.providers = providers

    def fetch(
        self,
        query: str,
        limit: int = 20,
    ) -> list[NewsArticleData]:
        """
        Fetch news from all configured providers.

        Articles are deduplicated using URL when available,
        otherwise title.
        """

        articles: list[NewsArticleData] = []
        seen: set[str] = set()

        for provider_name, provider in self.providers:
            try:
                provider_articles = provider.fetch(
                    query=query,
                    limit=limit,
                )

                for article in provider_articles:
                    article.provider = provider_name
                    
            except Exception:
                continue

            for article in provider_articles:
                key = self._article_key(article)

                if key in seen:
                    continue

                seen.add(key)
                articles.append(article)

                if len(articles) >= limit:
                    return articles

        return articles

    @staticmethod
    def _article_key(
        article: NewsArticleData,
    ) -> str:
        """
        Build a stable in-memory deduplication key.
        """

        if article.url:
            return article.url.strip().lower()

        return article.title.strip().lower()