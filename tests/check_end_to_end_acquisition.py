from ingestion.acquisition import (
    IPOAcquisitionService,
)

from ingestion.document_resolver import (
    DocumentResolver,
)

from ingestion.sebi.sebi_browser import (
    SEBIBrowserDiscovery,
)


sebi = SEBIBrowserDiscovery(
    headless=True
)

resolver = DocumentResolver(
    sebi_source=sebi,
)

service = IPOAcquisitionService(
    resolver=resolver,
)

result = service.acquire(
    ipo_id="cultfit-2026",
    company_name="CULT.FIT LIMITED",
    document_id="cultfit-drhp-2026",
    document_type="DRHP",
    version="2026-07",
)

print(
    "END-TO-END RESULT:"
)

print(
    result
)