from ingestion.sebi.document_resolver import (
    SEBIDocumentResolver,
)


resolver = SEBIDocumentResolver(
    headless=True
)

url = resolver.resolve(
    "CULT.FIT LIMITED",
    "DRHP",
)

print(
    "RESOLVED DOCUMENT URL:"
)

print(
    url
)