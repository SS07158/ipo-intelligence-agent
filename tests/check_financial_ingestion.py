from ingestion.sebi.financial_ingestion import (
    SEBIFinancialIngestion,
)


PDF_PATH = (
    "data/raw/nse/"
    "cultfit_limited/"
    "Registration_07072026083041_DRHP.pdf"
)


service = SEBIFinancialIngestion()

result = service.ingest_financials(
    ipo_id="cultfit-2026",
    pdf_path=PDF_PATH,
    document_id="cultfit-drhp-2026",
)

print(
    "FINANCIAL INGESTION RESULT:"
)

print(
    result
)