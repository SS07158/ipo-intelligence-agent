from database.database import SessionLocal
from database.ipo_repository import (
    upsert_structured_ipo,
)

from ingestion.structured_data import (
    StructuredIPORecord,
    normalize_ipo_record,
)


def persist_ipo_record(
    record: StructuredIPORecord,
) -> dict:
    """
    Normalize and persist structured IPO data.
    """

    record = normalize_ipo_record(
        record
    )

    session = SessionLocal()

    try:
        ipo = upsert_structured_ipo(
            session,
            record,
        )

        return {
            "success": True,
            "ipo_id": ipo.ipo_id,
            "company_name": (
                ipo.company_name
            ),
            "symbol": ipo.symbol,
            "fresh_issue": (
                ipo.fresh_issue
            ),
            "offer_for_sale": (
                ipo.offer_for_sale
            ),
            "offer_for_sale_shares": (
                ipo.offer_for_sale_shares
            ),
            "price_band_low": (
                ipo.price_band_low
            ),
            "price_band_high": (
                ipo.price_band_high
            ),
            "lot_size": ipo.lot_size,
            "issue_open_date": (
                ipo.issue_open_date
            ),
            "issue_close_date": (
                ipo.issue_close_date
            ),
            "listing_date": (
                ipo.listing_date
            ),
        }

    finally:
        session.close()