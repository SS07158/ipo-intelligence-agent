from database.database import SessionLocal
from database.ipo_repository import (
    get_document_by_id,
)


TEST_DOCUMENT_ID = "test-drhp"


session = SessionLocal()

try:

    document = get_document_by_id(
        session,
        TEST_DOCUMENT_ID,
    )

    if document is None:
        print(
            "No test document found."
        )

    else:
        session.delete(
            document
        )

        session.commit()

        print(
            f"Deleted test document: "
            f"{TEST_DOCUMENT_ID}"
        )

finally:

    session.close()