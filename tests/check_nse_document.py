from ingestion.nse.offer_documents import (
    NSEOfferDocumentSource,
)


source = NSEOfferDocumentSource(
    
)

result = source.resolve_document(
    company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        document_url=(
            "https://nsearchives.nseindia.com/"
            "corporate/"
            "Registration_07072026083041_DRHP.pdf"
        ),
)

print(
    "RESULT:"
)

print(
    result
)