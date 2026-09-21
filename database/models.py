from datetime import date, datetime

from sqlalchemy import Date, Float, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class IPO(Base):
    __tablename__ = "ipos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    ipo_id : Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    company_name: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    symbol: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Monetary values are stored in INR crore.

    issue_size: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    price_band_low: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    price_band_high: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    lot_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    issue_open_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    issue_close_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    listing_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # Monetary values are stored in INR crore.

    fresh_issue: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Monetary values are stored in INR crore.

    offer_for_sale: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    offer_for_sale_shares: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

class IPODocument(Base):
    __tablename__ = "ipo_documents"

    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    document_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    ipo_id: Mapped[int] = mapped_column(
        ForeignKey("ipos.id"),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    local_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    version: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    acquisition_source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    document_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    __table_args__ = (
        UniqueConstraint(
            "ipo_id",
            "metric_name",
            "period",
            name="uq_financial_metric_ipo_metric_period",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    ipo_id: Mapped[int] = mapped_column(
        ForeignKey("ipos.id"),
        nullable=False,
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    period: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipo_documents.id"),
        nullable=True,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # Link the article to an IPO when we can identify the company.
    # Nullable because some news may not yet be mapped to an IPO.
    ipo_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipos.id"),
        nullable=True,
    )

    # Provider that delivered the article.
    # Examples: RSS, AlphaVantage
    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Actual publisher/source of the article.
    # Examples: Business Standard, Economic Times
    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        String(5000),
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    author: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Provider-specific identifier when available.
    external_id: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Stable fingerprint used to detect duplicates
    # across different providers.
    article_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    # Filled later by the sentiment pipeline.
    sentiment_label: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    sentiment_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Filled later by topic classification.
    topic: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )