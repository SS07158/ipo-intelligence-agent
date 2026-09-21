from database.database import SessionLocal
from database.ipo_repository import (
    create_document,
    get_or_create_financial_metric,
    get_or_create_ipo,
)

from ingestion.ipo_config import IPOConfig


def seed_ipo(
    config: IPOConfig,
    financial_data: list[dict] | None = None,
) -> None:
    """
    Seed IPO metadata, document metadata,
    and optional financial metrics.
    """

    session = SessionLocal()

    try:
        ipo = get_or_create_ipo(
            session,
            ipo_id=config.ipo_id,
            company_name=config.company_name,
            issue_size=config.issue_size,
            price_band_low=config.price_band_low,
            price_band_high=config.price_band_high,
            lot_size=config.lot_size,
            issue_open_date=config.issue_open_date,
            issue_close_date=config.issue_close_date,
            listing_date=config.listing_date,
            fresh_issue=config.fresh_issue,
            offer_for_sale=config.offer_for_sale,
            offer_for_sale_shares=config.offer_for_sale_shares,
        )

        print(
            f"IPO: {ipo.company_name} "
            f"({ipo.ipo_id})"
        )

        document = None

        if config.document_id:
            document = create_document(
                session,
                document_id=config.document_id,
                ipo_id=ipo.id,
                document_type=(
                    config.document_type
                    or "UNKNOWN"
                ),
                title=(
                    config.document_title
                    or config.company_name
                ),
                source=(
                    config.source
                    or "UNKNOWN"
                ),
                source_url=config.source_url,
                local_path=config.local_path,
            )

            print(
                f"Document: "
                f"{document.document_id}"
            )

        for item in (
            financial_data or []
        ):
            metric = get_or_create_financial_metric(
                session,
                ipo_id=ipo.id,
                metric_name=item["metric_name"],
                period=item["period"],
                value=item["value"],
                unit=item["unit"],
                source_document_id=(
                    document.id
                    if document
                    else None
                ),
                page_number=item.get(
                    "page_number"
                ),
            )

            print(
                f"{metric.metric_name} | "
                f"{metric.period} | "
                f"{metric.value} "
                f"{metric.unit}"
            )

    finally:
        session.close()