from sqlalchemy import inspect

from database.database import engine
from database.database import SessionLocal
from database.ipo_repository import (
    get_documents_for_ipo,
    get_ipo_by_company,
    get_ipo_by_id,
    get_or_create_ipo,
    create_document
)


def test_ipo_ingestion_is_idempotent():
    session = SessionLocal()

    try:
        first = get_or_create_ipo(
            session,
            ipo_id="test-ipo",
            company_name="Test Company",
        )

        second = get_or_create_ipo(
            session,
            ipo_id="test-ipo",
            company_name="Test Company",
        )

        assert first.id == second.id

    finally:
        session.close()

def test_get_ipo_by_company(test_session):
    ipo = get_or_create_ipo(
        test_session,
        ipo_id="test-cultfit",
        company_name="CULT.FIT LIMITED",
    )

    result = get_ipo_by_company(
        test_session,
        "CULT.FIT LIMITED",
    )

    assert result is not None
    assert result.id == ipo.id

def test_get_documents_for_ipo(test_session):
    ipo = get_or_create_ipo(
        test_session,
        ipo_id="test-cultfit",
        company_name="CULT.FIT LIMITED",
    )

    create_document(
        test_session,
        document_id="test-drhp",
        ipo_id=ipo.id,
        document_type="DRHP",
        title="Test DRHP",
        source="SEBI",
        source_url="https://example.com",
        local_path="test.pdf",
    )

    documents = get_documents_for_ipo(
        test_session,
        ipo.id,
    )

    assert len(documents) == 1
    assert documents[0].document_id == "test-drhp"