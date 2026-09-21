from datetime import datetime

from sqlalchemy.orm import Session

from database.ipo_repository import (
    create_news_article,
    get_news_articles,
    update_news_sentiment,
    update_news_topic,
    )
from ingestion.news.provider import NewsArticleData
from ingestion.news.news_service import NewsService
from ingestion.news.ipo_matcher import match_article_to_ipo
from ingestion.sentiment.analyzer import SentimentAnalyzer
from ingestion.sentiment.topic_classifier import TopicClassifier


class NewsIngestionService:
    """
    Fetch news from a provider and persist normalized articles.
    """

    def __init__(
        self,
        news_service: NewsService
    ):
        self.news_service = news_service
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_classifier = TopicClassifier()


    def ingest(
        self,
        session: Session,
        query: str,
        limit: int = 20,
        ipo_id: int | None = None,
    ) -> list:
        """
        Fetch articles from the provider and persist them.

        Duplicate articles are ignored by the repository layer.
        """

        articles = self.news_service.fetch(
            query=query,
            limit=limit,
        )

        saved_articles = []

        for article in articles:
            matched_ipo = match_article_to_ipo(
                session,
                article,
            )

            article_ipo_id = ipo_id

            if matched_ipo is not None:
                article_ipo_id = matched_ipo.id

            text = article.title

            if article.summary:
                text = f"{article.title}. {article.summary}"

            sentiment = self.sentiment_analyzer.analyze(
                text
            )

            topic = self.topic_classifier.classify(
                text
            )

            saved_article = create_news_article(
                session,
                title=article.title,
                summary=article.summary,
                url=article.url,
                source=article.source,
                author=article.author,
                published_at=article.published_at,
                fetched_at=datetime.now(),
                external_id=article.external_id,
                provider=article.provider or "UNKNOWN",
                ipo_id=article_ipo_id,
                sentiment_label=sentiment.label,
                sentiment_score=sentiment.score,
                topic=topic,
            )

            saved_articles.append(saved_article)

        return saved_articles

def backfill_news_ipo_mapping(
    session: Session,
    limit: int = 100,
    ) -> int:
        """
        Match existing news articles to IPOs.

        Only articles that do not already have an ipo_id
        are considered.
        """

        articles = get_news_articles(
            session,
            limit=limit,
        )

        matched_count = 0

        for article in articles:
            if article.ipo_id is not None:
                continue

            news_article = NewsArticleData(
                title=article.title,
                summary=article.summary,
                url=article.url,
                source=article.source,
                author=article.author,
                published_at=article.published_at,
                external_id=article.external_id,
            )

            matched_ipo = match_article_to_ipo(
                session,
                news_article,
            )

            if matched_ipo is None:
                continue

            article.ipo_id = matched_ipo.id
            matched_count += 1

        session.commit()

        return matched_count