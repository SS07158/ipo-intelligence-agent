from database.database import SessionLocal
from database.ipo_repository import (
    get_ipo_by_company,
    get_documents_for_ipo,
)

session = SessionLocal()

try:
    ipo = get_ipo_by_company(
        session,
        "CULT.FIT LIMITED"
    )

    if ipo is None:
        raise RuntimeError("IPO not found")

    print("Company: ", ipo.company_name)
    print("IPO ID", ipo.ipo_id)
    print("Fresh Issue", ipo.fresh_issue)
    print("OFS Shares: ", ipo.offer_for_sale_shares)

    documents = get_documents_for_ipo(
        session,
        ipo.id,
    )

    print("\nDocuments")

    for document in documents:
        print(
            f"- {document.document_type}: "
            f"{document.title}"
        )

finally:
    session.close()