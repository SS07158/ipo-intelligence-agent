from ingestion.nse.offer_documents import (
    NSEOfferDocumentSource,
)


source = NSEOfferDocumentSource()


CULTFIT_DRHP = source.resolve_document(
    company_name="CULT.FIT LIMITED",
    document_type="DRHP",
    document_url=(
        "https://nsearchives.nseindia.com/"
        "corporate/"
        "Registration_07072026083041_DRHP.pdf"
    ),
    document_date="2026-07-06",
)