from dataclasses import dataclass
from datetime import date


@dataclass
class StructuredIPORecord:
    """
    Canonical representation of structured IPO data.
    """

    ipo_id: str

    company_name: str

    symbol: str | None = None

    issue_size: float | None = None

    price_band_low: float | None = None

    price_band_high: float | None = None

    lot_size: int | None = None

    issue_open_date: date | None = None

    issue_close_date: date | None = None

    listing_date: date | None = None

    fresh_issue: float | None = None

    offer_for_sale: float | None = None

    offer_for_sale_shares: int | None = None

    source: str | None = None


def normalize_ipo_record(
    record: StructuredIPORecord,
) -> StructuredIPORecord:
    """
    Normalize basic structured IPO fields.
    """

    company_name = (
        " ".join(
            record.company_name
            .strip()
            .upper()
            .split()
        )
    )

    symbol = (
        record.symbol.strip().upper()
        if record.symbol
        else None
    )

    return StructuredIPORecord(
        ipo_id=record.ipo_id.strip(),
        company_name=company_name,
        symbol=symbol,
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
        offer_for_sale=record.offer_for_sale,
        offer_for_sale_shares=(
            record.offer_for_sale_shares
        ),
        source=record.source,
    )