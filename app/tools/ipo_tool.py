from database.database import SessionLocal
from database.ipo_repository import (
    get_documents_for_ipo,
    get_ipo_by_company,
)


def lookup_ipo(company_name: str) -> dict:
    """
    Look up structured IPO information for a company.
    """

    session = SessionLocal()

    try:

        company_name = normalize_company_name(
            company_name
        )
        
        ipo = get_ipo_by_company(
            session,
            company_name,
        )

        if ipo is None:
            return {
                "found": False,
                "message": f"No IPO found for '{company_name}'.",
            }

        documents = get_documents_for_ipo(
            session,
            ipo.id,
        )

        return {
            "found": True,
            "ipo": {
                "ipo_id": ipo.ipo_id,
                "company_name": ipo.company_name,
                "symbol": ipo.symbol,
                "issue_size": ipo.issue_size,
                "price_band_low": ipo.price_band_low,
                "price_band_high": ipo.price_band_high,
                "lot_size": ipo.lot_size,
                "issue_open_date": ipo.issue_open_date,
                "issue_close_date": ipo.issue_close_date,
                "listing_date": ipo.listing_date,
                "fresh_issue": ipo.fresh_issue,
                "offer_for_sale": ipo.offer_for_sale,
                "offer_for_sale_shares": ipo.offer_for_sale_shares,
            },
            "documents": [
                {
                    "document_id": document.document_id,
                    "document_type": document.document_type,
                    "title": document.title,
                    "source": document.source,
                    "source_url": document.source_url,
                }
                for document in documents
            ],
        }

    finally:
        session.close()

def normalize_company_name(
    company_name: str,
) -> str:
    """
    Normalize a company name for lookup.
    """

    normalized = (
        " ".join(
            company_name
            .strip()
            .upper()
            .split()
        )
    )

    aliases = {
        "CULT.FIT": "CULT.FIT LIMITED",
        "CULTFIT": "CULT.FIT LIMITED",
    }

    return aliases.get(
        normalized,
        normalized,
    )