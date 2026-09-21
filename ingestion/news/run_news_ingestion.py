from urllib.parse import quote_plus

from database.database import SessionLocal
from database.ipo_repository import get_all_ipos
from ingestion.news.ingestion_service import (
    NewsIngestionService,
)
from ingestion.news.news_service import (
    NewsService,
)
from ingestion.news.rss_provider import (
    RSSProvider,
)


def build_news_service(
    company_name: str,
) -> NewsService:
    """
    Build a NewsService for one company.

    Google News RSS is used as the current RSS source.
    """

    query = quote_plus(
        f'"{company_name}"'
    )

    feed_url = (
        "https://news.google.com/rss/search"
        f"?q={query}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    rss_provider = RSSProvider(
        feed_url=feed_url
    )

    return NewsService(
        providers=[
            ("GoogleNewsRSS", rss_provider),
        ]
    )


def ingest_company_news(
    company_name: str,
    limit: int = 20,
) -> int:
    """
    Fetch and persist news for a company.
    """

    news_service = build_news_service(
        company_name
    )

    ingestion_service = (
        NewsIngestionService(
            news_service
        )
    )

    session = SessionLocal()

    try:
        articles = ingestion_service.ingest(
            session=session,
            query=company_name,
            limit=limit,
        )

        print(
            f"Fetched and processed "
            f"{len(articles)} articles "
            f"for {company_name}."
        )

        return len(articles)

    finally:
        session.close()


if __name__ == "__main__":
    session = SessionLocal()

    try:
        ipos = get_all_ipos(session)

        companies = [
            ipo.company_name
            for ipo in ipos
            if ipo.company_name
        ]

    finally:
        session.close()

    for company_name in companies:
        print(
            f"\nIngesting news for: {company_name}"
        )

        ingest_company_news(
            company_name,
            limit=10,
        )