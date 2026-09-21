from datetime import datetime

import requests

from app.config import settings
from ingestion.news.provider import (
    NewsArticleData,
    NewsProvider,
)


class AlphaVantageProvider(NewsProvider):
    """
    Alpha Vantage NEWS_SENTIMENT provider.
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 15,
    ):
        self.api_key = (
            api_key
            or settings.alpha_vantage_api_key
        )

        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key is not configured."
            )

        self.timeout = timeout

    def fetch(
        self,
        query: str,
        limit: int = 20,
    ) -> list[NewsArticleData]:
        """
        Fetch IPO-related news from Alpha Vantage.

        For ticker-like queries, use the ticker filter.
        Otherwise fetch IPO-topic articles and filter locally
        using the query text.
        """

        params = {
            "function": "NEWS_SENTIMENT",
            "topics": "ipo",
            "sort": "LATEST",
            "limit": min(limit, 1000),
            "apikey": self.api_key,
        }

        ticker = None

        if self._looks_like_ticker(query):
            ticker = query.strip()

        if ticker:
            params.pop("topics", None)
            params["tickers"] =  ticker

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if "Error Message" in data:
            raise RuntimeError(
                data["Error Message"]
            )

        if "Information" in data:
            raise RuntimeError(
                data["Information"]
            )

        feed = data.get("feed", [])

        articles = []

        for item in feed:
            article = self._parse_article(item)

            if article is None:
                continue

            if query and not ticker:
                if not self._matches_company_query(
                    article,
                    query,
                ):
                    continue

            articles.append(article)

            if len(articles) >= limit:
                break

        return articles

    @staticmethod
    def _parse_article(
        item: dict,
    ) -> NewsArticleData | None:
        title = item.get("title")

        if not title:
            return None

        return NewsArticleData(
            title=title,
            summary=item.get("summary"),
            url=item.get("url"),
            source=item.get("source"),
            author=(
                item.get("authors", [None])[0]
                if item.get("authors")
                else None
            ),
            published_at=(
                AlphaVantageProvider._parse_datetime(
                    item.get("time_published")
                )
            ),
            external_id=item.get("url"),
        )

    @staticmethod
    def _parse_datetime(
        value: str | None,
    ) -> datetime | None:
        if not value:
            return None

        try:
            return datetime.strptime(
                value,
                "%Y%m%dT%H%M%S",
            )
        except ValueError:
            return None

    @staticmethod
    def _matches_query(
        article: NewsArticleData,
        query: str,
    ) -> bool:
        query = query.lower().strip()

        text = " ".join(
            [
                article.title or "",
                article.summary or "",
            ]
        ).lower()

        normalized_query = (
            query
            .replace(".", " ")
            .replace(",", " ")
        )

        return (
            query in text
            or normalized_query in text
        )

    @staticmethod
    def _matches_company_query(
        article: NewsArticleData,
        query: str,
    ) -> bool:
        """
        Match a company-name query against article text
        using normalized company-name variants.
        """

        text = " ".join(
            [
                article.title or "",
                article.summary or "",
            ]
        ).lower()

        normalized_query = (
            query.lower()
            .replace(".", " ")
            .replace(",", " ")
        )

        company_tokens = [
            token
            for token in normalized_query.split()
            if token not in {
                "limited",
                "ltd",
                "private",
                "pvt",
                "company",
                "corporation",
            }
        ]

        if not company_tokens:
            return False

        normalized_text = (
            text
            .replace(".", " ")
            .replace(",", " ")
        )

        company_name = " ".join(company_tokens)

        return company_name in normalized_text

    @staticmethod
    def _looks_like_ticker(
        query: str,
    ) -> bool:
        """
        Detect common ticker-style inputs such as:
        IBM, RELIANCE.BSE, AAPL.
        """

        value = query.strip()

        if not value:
            return False

        return (
            len(value) <= 20
            and " " not in value
            and any(
                character.isalpha()
                for character in value
            )
        )