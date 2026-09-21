from sqlalchemy.orm import Session

from database.ipo_repository import (
    get_news_articles,
    update_news_topic,
)
from ingestion.sentiment.topic_classifier import TopicClassifier


def process_news_topics(
    session: Session,
    classifier: TopicClassifier,
    limit: int = 100,
) -> int:
    """
    Classify news articles that do not have a topic yet
    and persist the result.
    """

    articles = get_news_articles(
        session,
        limit=limit,
    )

    processed_count = 0

    for article in articles:
        if article.topic is not None:
            continue

        text = article.title

        if article.summary:
            text = f"{article.title}. {article.summary}"

        topic = classifier.classify(text)

        update_news_topic(
            session,
            article_id=article.id,
            topic=topic,
        )

        processed_count += 1

    return processed_count