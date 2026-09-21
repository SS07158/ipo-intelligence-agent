from sqlalchemy.orm import Session

from database.ipo_repository import (
    get_news_articles,
    update_news_sentiment,
)
from ingestion.sentiment.analyzer import SentimentAnalyzer


def process_news_sentiment(
    session: Session,
    analyzer: SentimentAnalyzer,
    limit: int = 100,
) -> int:
    
    """
    Analyze news articles that do not have sentiment yet
    and persist the results.
    """

    articles = get_news_articles(
        session,
        limit=limit,
    )

    processed_count = 0

    for article in articles:
        if article.sentiment_label is not None:
            continue

        text = article.title

        if article.summary:
            text = f"{article.title}. {article.summary}"

        result = analyzer.analyze(text)

        update_news_sentiment(
            session,
            article_id=article.id,
            sentiment_label=result.label,
            sentiment_score=result.score,
        )

        processed_count += 1

    return processed_count