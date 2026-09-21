from database.database import SessionLocal
from database.ipo_repository import (
    get_ipo_by_company,
    get_news_articles_for_ipo,
)
from app.tools.ipo_tool import normalize_company_name


def lookup_news(
    company_name: str,
    limit: int = 10,
    sentiment: str | None = None,
    topic: str | None = None,
) -> dict:
    """
    Retrieve recent news articles associated with an IPO.
    """

    session = SessionLocal()

    try:
        company_name = normalize_company_name(
            company_name
        )

        ipo = get_ipo_by_company(
            session,
            company_name,
        )

        if ipo is None:
            return {
                "found": False,
                "message": (
                    f"No IPO found for '{company_name}'."
                ),
                "articles": [],
            }

        articles = get_news_articles_for_ipo(
            session,
            ipo.id,
            limit=limit,
            sentiment=sentiment,
            topic=topic,
        )

        return {
            "found": True,
            "company_name": ipo.company_name,
            "article_count": len(articles),
            "articles": [
                {
                    "title": article.title,
                    "summary": article.summary,
                    "source": article.source,
                    "provider": article.provider,
                    "published_at": (
                        article.published_at.isoformat()
                        if article.published_at
                        else None
                    ),
                    "url": article.url,
                    "sentiment": {
                        "label": article.sentiment_label,
                        "score": article.sentiment_score,
                    },
                    "topic": article.topic,
                }
                for article in articles
            ],
        }

    finally:
        session.close()