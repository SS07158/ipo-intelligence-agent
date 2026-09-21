from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IPOConfig:
    """
    Configuration for ingesting one IPO.
    """

    ipo_id: str
    company_name: str

    fresh_issue: float | None = None
    issue_size: float | None = None
    price_band_low: float | None = None
    price_band_high: float | None = None
    lot_size: int | None = None

    issue_open_date: object | None = None
    issue_close_date: object | None = None
    listing_date: object | None = None

    offer_for_sale: float | None = None
    offer_for_sale_shares: int | None = None

    document_id: str | None = None
    document_type: str | None = None
    document_title: str | None = None
    source: str | None = None
    source_url: str | None = None
    local_path: str | None = None

    version: str | None = None
    published_at: datetime | None = None