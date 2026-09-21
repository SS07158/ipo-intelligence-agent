from database.database import SessionLocal

from database.ipo_repository import (
    update_document_provenance,
)


DOCUMENT_ID = "cultfit-drhp-2026"


session = SessionLocal()

try:

    document = update_document_provenance(
        session,
        document_id=DOCUMENT_ID,
        acquisition_source="NSE",
        document_url=(
            "https://nsearchives.nseindia.com/"
            "corporate/Cultfit.zip"
        ),
        local_path=(
            "data/raw/nse/"
            "cultfit_limited/"
            "Registration_07072026083041_DRHP.pdf"
        ),
    )

    if document is None:
        print(
            "Document not found."
        )

    else:
        print(
            "Updated provenance:"
        )

        print(
            "document_id:",
            document.document_id,
        )

        print(
            "source:",
            document.source,
        )

        print(
            "source_url:",
            document.source_url,
        )

        print(
            "acquisition_source:",
            document.acquisition_source,
        )

        print(
            "document_url:",
            document.document_url,
        )

finally:

    session.close()