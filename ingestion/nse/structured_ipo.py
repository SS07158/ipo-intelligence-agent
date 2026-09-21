from datetime import datetime, date
from typing import Any

from ingestion.structured_data import (
    StructuredIPORecord,
    normalize_ipo_record,
)


def parse_nse_date(
    value: str | None,
) -> date | None:
    """
    Parse dates returned by NSE.

    Expected format:
        DD-Mon-YYYY

    NSE may use "-", "", or null to represent
    an unavailable date.
    """

    if value is None:
        return None

    value = value.strip()

    if value in {
        "",
        "-",
        "--",
        "NA",
        "N/A",
        "NULL",
    }:
        return None

    try:
        return datetime.strptime(
            value,
            "%d-%b-%Y",
        ).date()

    except ValueError as exc:
        raise ValueError(
            f"Invalid NSE date: {value}"
        ) from exc


def _clean_value(
    value: Any,
) -> str | None:
    """
    Convert common NSE missing-value markers to None.
    """

    if value is None:
        return None

    value = str(value).strip()

    if value.upper() in {
        "",
        "-",
        "--",
        "NA",
        "N/A",
        "NULL",
    }:
        return None

    return value


def build_structured_ipo_record(
    raw: dict[str, Any],
    *,
    ipo_id: str,
    source: str = "NSE",
) -> StructuredIPORecord:
    """
    Convert an NSE offer-document record into the
    canonical StructuredIPORecord.

    Source-specific formatting is normalized before
    the record leaves the NSE adapter.
    """

    company = _clean_value(
        raw.get("company")
    )

    if company is None:
        raise ValueError(
            "NSE record is missing company."
        )

    symbol = _clean_value(
        raw.get("symbol")
    )

    record = StructuredIPORecord(
        ipo_id=ipo_id.strip(),
        company_name=company,
        symbol=symbol,
        issue_size=None,
        price_band_low=None,
        price_band_high=None,
        lot_size=None,
        issue_open_date=parse_nse_date(
            _clean_value(
                raw.get("issue_open_date")
            )
        ),
        issue_close_date=parse_nse_date(
            _clean_value(
                raw.get("issue_close_date")
            )
        ),
        listing_date=None,
        fresh_issue=None,
        offer_for_sale=None,
        offer_for_sale_shares=None,
        source=source,
    )

    return normalize_ipo_record(
        record
    )