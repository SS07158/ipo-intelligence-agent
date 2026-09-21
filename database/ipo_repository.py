import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import (
    FinancialMetric,
    IPO,
    IPODocument,
    NewsArticle,
)

from ingestion.structured_data import (
    StructuredIPORecord,
)


def create_ipo(
    session: Session,
    *,
    ipo_id: str,
    company_name: str,
    symbol: str | None = None,
    issue_size: float | None = None,
    price_band_low: float | None = None,
    price_band_high: float | None = None,
    lot_size: int | None = None,
    issue_open_date=None,
    issue_close_date=None,
    listing_date=None,
    fresh_issue: float | None = None,
    offer_for_sale: float | None = None,
    offer_for_sale_shares: int | None = None,
) -> IPO:
    """
    Create and persist an IPO record.
    """

    ipo = IPO(
        ipo_id=ipo_id,
        company_name=company_name,
        symbol=symbol,
        issue_size=issue_size,
        price_band_low=price_band_low,
        price_band_high=price_band_high,
        lot_size=lot_size,
        issue_open_date=issue_open_date,
        issue_close_date=issue_close_date,
        listing_date=listing_date,
        fresh_issue=fresh_issue,
        offer_for_sale=offer_for_sale,
        offer_for_sale_shares=offer_for_sale_shares,
    )

    session.add(ipo)
    session.commit()
    session.refresh(ipo)

    return ipo


def get_ipo_by_id(
    session: Session,
    ipo_id: str,
) -> IPO | None:
    """
    Retrieve an IPO using its internal IPO identifier.
    """

    statement = select(IPO).where(
        IPO.ipo_id == ipo_id
    )

    return session.scalar(statement)

def get_or_create_ipo(
    session: Session,
    *,
    ipo_id: str,
    company_name: str,
    symbol: str | None = None,
    issue_size: float | None = None,
    price_band_low: float | None = None,
    price_band_high: float | None = None,
    lot_size: int | None = None,
    issue_open_date=None,
    issue_close_date=None,
    listing_date=None,
    fresh_issue: float | None = None,
    offer_for_sale: float | None = None,
    offer_for_sale_shares: int | None = None,
) -> IPO:
    """
    Return an existing IPO or create it if it does not exist.
    """

    existing = get_ipo_by_id(
        session,
        ipo_id,
    )

    if existing is not None:
        existing.company_name = company_name
        existing.symbol = symbol
        existing.issue_size = issue_size
        existing.price_band_low = price_band_low
        existing.price_band_high = price_band_high
        existing.lot_size = lot_size
        existing.issue_open_date = issue_open_date
        existing.issue_close_date = issue_close_date
        existing.listing_date = listing_date
        existing.fresh_issue = fresh_issue
        existing.offer_for_sale = offer_for_sale
        existing.offer_for_sale_shares = offer_for_sale_shares

        session.commit()
        session.refresh(existing)

        return existing

    return create_ipo(
        session,
        ipo_id=ipo_id,
        company_name=company_name,
        symbol=symbol,
        issue_size=issue_size,
        price_band_low=price_band_low,
        price_band_high=price_band_high,
        lot_size=lot_size,
        issue_open_date=issue_open_date,
        issue_close_date=issue_close_date,
        listing_date=listing_date,
        fresh_issue=fresh_issue,
        offer_for_sale=offer_for_sale,
        offer_for_sale_shares = offer_for_sale_shares
    )

def create_document(
    session: Session,
    *,
    document_id: str,
    ipo_id: int,
    document_type: str,
    title: str,
    source: str,
    source_url: str | None = None,
    local_path: str | None = None,
    acquisition_source: str | None = None,
    document_url: str | None = None,
) -> IPODocument:
    """
    Create and persist an IPO document record.
    """
    exisiting = get_document_by_id(
        session,
        document_id
    )

    if exisiting is not None:
        return exisiting


    document = IPODocument(
        document_id=document_id,
        ipo_id=ipo_id,
        document_type=document_type,
        title=title,
        source=source,
        source_url=source_url,
        local_path=local_path,
        acquisition_source = acquisition_source,
        document_url=document_url,
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    return document

def update_document_provenance(
    session: Session,
    *,
    document_id: str,
    source: str | None = None,
    source_url: str | None = None,
    acquisition_source: str | None = None,
    document_url: str | None = None,
    local_path: str | None = None,
) -> IPODocument | None:
    """
    Update document provenance without replacing
    existing values with None.
    """

    document = get_document_by_id(
        session,
        document_id,
    )

    if document is None:
        return None

    if source is not None:
        document.source = source

    if source_url is not None:
        document.source_url = source_url

    if acquisition_source is not None:
        document.acquisition_source = (
            acquisition_source
        )

    if document_url is not None:
        document.document_url = document_url

    if local_path is not None:
        document.local_path = local_path

    session.commit()
    session.refresh(document)

    return document

def get_document_by_id(
    session: Session,
    document_id: str,
)-> IPODocument | None:
    """
    Retrieve a document by its internal document identifier.
    """

    statement = select(IPODocument).where(
        IPODocument.document_id == document_id
    )

    return session.scalar(statement)

def get_ipo_by_company(
    session: Session,
    company_name: str,
) -> IPO | None:
    """
    Retrieve an IPO using the company Name
    """

    statement = select(IPO).where(
        IPO.company_name.ilike(company_name)
    )

    return session.scalar(statement)

def get_documents_for_ipo(
    session: Session,
    ipo_id: int,
) -> list[IPODocument]:
    """
    Retrieve all documents associated with an IPO.
    """

    statement = (
        select(IPODocument)
        .where(IPODocument.ipo_id == ipo_id)
        .order_by(IPODocument.id)
    )

    return list(session.scalars(statement).all())

def create_financial_metric(
    session: Session,
    *,
    ipo_id: int,
    metric_name: str,
    period: str,
    value: float,
    unit: str,
    source_document_id: int | None = None,
    page_number: int | None = None,
) -> FinancialMetric:
    """
    Create and persist a financial metric
    """

    metric = FinancialMetric(
    ipo_id = ipo_id,
    metric_name=metric_name,
    period=period,
    value=value,
    unit=unit,
    source_document_id= source_document_id,
    page_number=page_number
    )

    session.add(metric)
    session.commit()
    session.refresh(metric)

    return metric

def get_financial_metrics(
    session: Session,
    ipo_id: int,
    metric_name: str | None = None,
    period: str | None = None,
) -> list[FinancialMetric]:
    """
    Retrieve financial metrics for an IPO.

    Optionally filter by metric name and period.
    """

    statement = (
        select(FinancialMetric)
        .where(
            FinancialMetric.ipo_id == ipo_id
        )
        .order_by(
            FinancialMetric.period
        )
    )

    if metric_name is not None:
        statement = statement.where(
            FinancialMetric.metric_name
            == metric_name
        )

    if period is not None:
        statement = statement.where(
            FinancialMetric.period
            == period
        )

    return list(
        session.scalars(
            statement
        ).all()
    )


def get_or_create_financial_metric(
    session: Session,
    *,
    ipo_id: int,
    metric_name: str,
    period: str,
    value: float,
    unit: str,
    source_document_id: int | None = None,
    page_number: int | None = None,
) -> FinancialMetric:
    """
    Return an existing metric or create it if it does not exist.
    """

    existing_metrics = get_financial_metrics(
    session,
    ipo_id=ipo_id,
    metric_name=metric_name,
    period=period,
)

    if existing_metrics:
        existing = existing_metrics[0]

        existing.value = value
        existing.unit = unit
        existing.source_document_id = (
            source_document_id
        )
        existing.page_number = page_number

        session.commit()
        session.refresh(existing)

        return existing

    return create_financial_metric(
        session,
        ipo_id=ipo_id,
        metric_name=metric_name,
        period=period,
        value=value,
        unit=unit,
        source_document_id=source_document_id,
        page_number=page_number,
    )

def compare_ipo_financials(
    session: Session,
    first_ipo_id: int,
    second_ipo_id: int,
    metric_name: str,
) -> dict:
    """
    Compare one financial metric between two IPOs
    """

    first_ipo = session.get(IPO, first_ipo_id)
    second_ipo = session.get(IPO, second_ipo_id)

    if first_ipo is None:
        raise ValueError(
            f"IPO not found: {first_ipo_id}"
        )

    if second_ipo is None:
        raise ValueError(
            f"IPO not found: {second_ipo_id}"
        )

    first_metrics = get_financial_metrics(
        session,
        first_ipo.id,
        metric_name
    )

    second_metrics = get_financial_metrics(
        session,
        second_ipo.id,
        metric_name,
    )

    first_values = {
        metric.period: metric.value
        for metric in first_metrics
    }

    second_values = {
        metric.period: metric.value
        for metric in second_metrics
    }

    common_periods = sorted(
        set(first_values) & set(second_values)
    )

    return {
        "first_ipo": first_ipo.company_name,
        "second_ipo": second_ipo.company_name,
        "metric_name": metric_name,
        "common_periods": common_periods,
        "first_values": {
            period: first_values[period]
            for period in common_periods
        },
        "second_values": {
            period: second_values[period]
            for period in common_periods
        },
    }

def upsert_structured_ipo(
    session: Session,
    record: StructuredIPORecord,
) -> IPO:
    """
    Insert or update an IPO using canonical structured data.
    """

    existing = get_ipo_by_id(
        session,
        record.ipo_id,
    )

    if existing is None:

        return create_ipo(
            session,
            ipo_id=record.ipo_id,
            company_name=record.company_name,
            symbol=record.symbol,
            issue_size=record.issue_size,
            price_band_low=(
                record.price_band_low
            ),
            price_band_high=(
                record.price_band_high
            ),
            lot_size=record.lot_size,
            issue_open_date=(
                record.issue_open_date
            ),
            issue_close_date=(
                record.issue_close_date
            ),
            listing_date=record.listing_date,
            fresh_issue=record.fresh_issue,
            offer_for_sale=(
                record.offer_for_sale
            ),
            offer_for_sale_shares=(
                record.offer_for_sale_shares
            ),
        )

    # Update only values supplied by the source.
    existing.company_name = (
        record.company_name
    )

    if record.symbol is not None:
        existing.symbol = record.symbol

    if record.issue_size is not None:
        existing.issue_size = record.issue_size

    if record.price_band_low is not None:
        existing.price_band_low = (
            record.price_band_low
        )

    if record.price_band_high is not None:
        existing.price_band_high = (
            record.price_band_high
        )

    if record.lot_size is not None:
        existing.lot_size = record.lot_size

    if record.issue_open_date is not None:
        existing.issue_open_date = (
            record.issue_open_date
        )

    if record.issue_close_date is not None:
        existing.issue_close_date = (
            record.issue_close_date
        )

    if record.listing_date is not None:
        existing.listing_date = (
            record.listing_date
        )

    if record.fresh_issue is not None:
        existing.fresh_issue = (
            record.fresh_issue
        )

    if record.offer_for_sale is not None:
        existing.offer_for_sale = (
            record.offer_for_sale
        )

    if (
        record.offer_for_sale_shares
        is not None
    ):
        existing.offer_for_sale_shares = (
            record.offer_for_sale_shares
        )

    session.commit()
    session.refresh(existing)

    return existing

def get_financial_document_id(
    session: Session,
    document_id: str,
) -> int | None:
    """
    Resolve the public document_id to the internal
    IPODocument primary key.
    """

    document = get_document_by_id(
        session,
        document_id,
    )

    if document is None:
        return None

    return document.id

def generate_article_hash(
    *,
    title: str,
    url: str | None = None,
) -> str:
    """
    Generate a stable fingerprint for a news article.

    URL is preferred because it is usually unique.
    Title is used as a fallback.
    """

    identity = url or title

    return hashlib.sha256(
        identity.strip().lower().encode("utf-8")
    ).hexdigest()


def get_news_article_by_hash(
    session: Session,
    article_hash: str,
) -> NewsArticle | None:
    """
    Retrieve a news article using its unique hash.
    """

    statement = select(NewsArticle).where(
        NewsArticle.article_hash == article_hash
    )

    return session.scalar(statement)


def create_news_article(
    session: Session,
    *,
    title: str,
    summary: str | None = None,
    url: str | None = None,
    source: str | None = None,
    author: str | None = None,
    published_at=None,
    fetched_at=None,
    external_id: str | None = None,
    provider: str,
    ipo_id: int | None = None,
    sentiment_label: str | None = None,
    sentiment_score: float | None = None,
    topic: str | None = None,
) -> NewsArticle:
    """
    Create and persist a news article.
    """

    article_hash = generate_article_hash(
        title=title,
        url=url,
    )

    existing = get_news_article_by_hash(
        session,
        article_hash,
    )

    if existing is not None:
        return existing

    article = NewsArticle(
        ipo_id=ipo_id,
        provider=provider,
        source=source,
        title=title,
        summary=summary,
        url=url,
        author=author,
        published_at=published_at,
        fetched_at=fetched_at,
        external_id=external_id,
        article_hash=article_hash,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
        topic=topic,
    )

    session.add(article)
    session.commit()
    session.refresh(article)

    return article

def get_news_articles_for_ipo(
    session: Session,
    ipo_id: int,
    limit: int = 20,
    sentiment: str | None = None,
    topic: str | None = None,
) -> list[NewsArticle]:
    """
    Retrieve recent news articles associated with an IPO.

    Optionally filter by sentiment and topic.
    """

    statement = (
        select(NewsArticle)
        .where(
            NewsArticle.ipo_id == ipo_id
        )
        .order_by(
            NewsArticle.published_at.desc()
        )
    )

    if sentiment is not None:
        statement = statement.where(
            NewsArticle.sentiment_label
            == sentiment.lower()
        )

    if topic is not None:
        statement = statement.where(
            NewsArticle.topic
            == topic.lower()
        )

    statement = statement.limit(limit)

    return list(
        session.scalars(
            statement
        ).all()
    )

def get_all_ipos(
    session: Session,
) -> list[IPO]:
    """
    Retrieve all IPO records.
    """

    statement = (
        select(IPO)
        .order_by(IPO.company_name)
    )

    return list(
        session.scalars(statement).all()
    )

def get_news_articles(
    session: Session,
    limit: int = 100,
) -> list[NewsArticle]:
    """
    Retrieve news articles for processing.
    """

    statement = (
        select(NewsArticle)
        .order_by(NewsArticle.id)
        .limit(limit)
    )

    return list(
        session.scalars(statement).all()
    )

def update_news_sentiment(
    session: Session,
    article_id: int,
    sentiment_label: str,
    sentiment_score: float,
) -> NewsArticle | None:
    """
    Update sentiment fields for a news article.
    """

    article = session.get(
        NewsArticle,
        article_id,
    )

    if article is None:
        return None

    article.sentiment_label = sentiment_label
    article.sentiment_score = sentiment_score

    session.commit()
    session.refresh(article)

    return article

def update_news_topic(
    session: Session,
    article_id: int,
    topic: str,
) -> NewsArticle | None:
    """
    Update the topic for a news article.
    """

    article = session.get(
        NewsArticle,
        article_id,
    )

    if article is None:
        return None

    article.topic = topic

    session.commit()
    session.refresh(article)

    return article