from database.database import SessionLocal
from database.ipo_repository import (
    get_ipo_by_id,
)


session = SessionLocal()

try:

    ipo = get_ipo_by_id(
        session,
        "cultfit-2026",
    )

    if ipo is None:
        print(
            "CULT.FIT IPO not found."
        )

    else:
        print(
            "CULT.FIT IPO:"
        )

        print(
            "company_name:",
            ipo.company_name,
        )

        print(
            "symbol:",
            ipo.symbol,
        )

        print(
            "fresh_issue:",
            ipo.fresh_issue,
        )

        print(
            "offer_for_sale:",
            ipo.offer_for_sale,
        )

        print(
            "offer_for_sale_shares:",
            ipo.offer_for_sale_shares,
        )

        print(
            "price_band_low:",
            ipo.price_band_low,
        )

        print(
            "price_band_high:",
            ipo.price_band_high,
        )

        print(
            "lot_size:",
            ipo.lot_size,
        )

        print(
            "issue_open_date:",
            ipo.issue_open_date,
        )

        print(
            "issue_close_date:",
            ipo.issue_close_date,
        )

        print(
            "listing_date:",
            ipo.listing_date,
        )

finally:

    session.close()