from ingestion.acquisition import (
    IPOAcquisitionService,
)


service = IPOAcquisitionService()

result = service.acquire_from_nse(
    ipo_id="cultfit-2026",
    company_name="Cult.Fit Limited",
    document_id="cultfit-drhp-2026",
    document_type="DRHP",
    version="2026-07",
)

print(
    "ACQUISITION RESULT:"
)

print(
    result
)