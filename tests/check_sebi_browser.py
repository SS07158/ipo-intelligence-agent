import ingestion.sebi.sebi_browser as module

print(
    "LOADED MODULE:",
    module.__file__,
)

from ingestion.sebi.sebi_browser import (
    SEBIBrowserDiscovery,
)


discovery = SEBIBrowserDiscovery(
    headless=True
)



documents = discovery.discover(
    "CULT.FIT LIMITED"
)

if documents:

    pdf_url = discovery.extract_document_url(
        documents[0].detail_url,
        document_type=".pdf"
    )

    print(
        "\nPDF URL:"
    )

    print(
        pdf_url
    )

print(
    f"Found {len(documents)} documents."
)

for document in documents:

    print()
    print(
        "COMPANY:",
        document.company_name,
    )

    print(
        "TYPE:",
        document.document_type,
    )

    print(
        "DETAIL URL:",
        document.detail_url,
    )