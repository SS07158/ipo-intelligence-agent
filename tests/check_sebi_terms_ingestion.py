from ingestion.sebi.terms_ingestion import (
    SEBIIPOTermsIngestion,
)


PDF_PATH = (
    "data/raw/nse/"
    "cultfit_limited/"
    "Registration_07072026083041_DRHP.pdf"
)


service = SEBIIPOTermsIngestion()

result = service.ingest(
    ipo_id="cultfit-2026",
    company_name="CULT.FIT LIMITED",
    pdf_path=PDF_PATH,
)

print(
    "STRUCTURED TERMS RESULT:"
)

print(
    result
)