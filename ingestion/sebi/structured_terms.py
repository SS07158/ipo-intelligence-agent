from ingestion.structured_data import (
    StructuredIPORecord,
)


def build_sebi_ipo_record(
    *,
    ipo_id: str,
    company_name: str,
    terms: dict,
) -> StructuredIPORecord:
    """
    Build the canonical structured IPO record
    from extracted SEBI terms.
    """

    return StructuredIPORecord(
        ipo_id=ipo_id,
        company_name=company_name,
        symbol=None,
        issue_size=None,
        price_band_low=None,
        price_band_high=None,
        lot_size=None,
        issue_open_date=None,
        issue_close_date=None,
        listing_date=None,
        fresh_issue=terms.get(
            "fresh_issue"
        ),
        offer_for_sale=None,
        offer_for_sale_shares=terms.get(
            "offer_for_sale_shares"
        ),
        source="SEBI",
    )