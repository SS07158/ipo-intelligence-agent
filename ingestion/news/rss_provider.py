from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests

from ingestion.news.provider import NewsArticleData, NewsProvider


class RSSProvider(NewsProvider):
    """
    News provider that fetches articles from an RSS feed.
    """

    def __init__(
        self,
        feed_url: str,
        timeout: int = 15,
    ):
        self.feed_url = feed_url
        self.timeout = timeout

    def fetch(
        self,
        query: str,
        limit: int = 20,
    ) -> list[NewsArticleData]:
        """
        Fetch articles from the RSS feed.

        The query is applied as a simple case-insensitive filter
        against the article title and summary.
        """

        response = requests.get(
            self.feed_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
                ),
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        root = ElementTree.fromstring(response.content)

        articles: list[NewsArticleData] = []

        for item in root.iter():
            if self._local_name(item.tag) != "item":
                continue

            article = self._parse_item(item)

            if article is None:
                continue

            # RSS feeds such as Google News are already
            # scoped by the search URL, so do not apply
            # another exact-string company filter here.

            articles.append(article)

            if len(articles) >= limit:
                break

        return articles

    def _parse_item(
        self,
        item,
    ) -> Optional[NewsArticleData]:
        values: dict[str, str] = {}

        for child in item:
            key = self._local_name(child.tag)
            value = (child.text or "").strip()

            if value:
                values[key] = value

        title = values.get("title")

        if not title:
            return None

        return NewsArticleData(
            title=title,
            summary=values.get("description"),
            url=values.get("link"),
            source=self._extract_source(values),
            author=values.get("author") or values.get("creator"),
            published_at=self._parse_datetime(
                values.get("pubDate") or values.get("published")
            ),
            external_id=values.get("guid"),
        )

    @staticmethod
    def _matches_query(
        article: NewsArticleData,
        query: str,
    ) -> bool:
        query_lower = query.lower()

        text = " ".join(
            [
                article.title or "",
                article.summary or "",
            ]
        ).lower()

        return query_lower in text

    @staticmethod
    def _parse_datetime(
        value: Optional[str],
    ) -> Optional[datetime]:
        if not value:
            return None

        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None

    @staticmethod
    def _extract_source(
        values: dict[str, str],
    ) -> Optional[str]:
        return (
            values.get("source")
            or values.get("publisher")
            or None
        )

    @staticmethod
    def _local_name(tag: str) -> str:
        """
        Handles both normal XML tags and namespaced tags.
        """
        if "}" in tag:
            return tag.rsplit("}", 1)[1]

        return tag