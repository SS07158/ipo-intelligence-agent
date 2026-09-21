from ingestion.nse.discovery import (
    NSEOfferDocumentDiscovery,
)


discovery = (
    NSEOfferDocumentDiscovery()
)

result = discovery.find_document(
    "Cult.Fit Limited",
    "DRHP",
)

print(
    "RESULT:"
)

print(
    result
)