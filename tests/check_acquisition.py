from ingestion.acquisition import (
    IPOAcquisitionService,
)


service = IPOAcquisitionService()

result = service.acquire(
    ipo_id="cultfit-2026",
    company_name="CULT.FIT LIMITED",
    document_id="cultfit-drhp-2026",
    document_type="DRHP",
    source="NSE",
    version="2026-07",
)

print(
    "ACQUISITION RESULT:"
)

print(
    result
)