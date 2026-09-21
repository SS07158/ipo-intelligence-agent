from database.ipo_repository import (
    get_ipo_by_id,
)

from database.database import (
    SessionLocal,
)

from ingestion.structured_data import (
    StructuredIPORecord,
)

from ingestion.structured_persistence import (
    persist_ipo_record,
)


def test_structured_ipo_upsert():

    record = StructuredIPORecord(
        ipo_id="cultfit-2026",
        company_name="CULT.FIT LIMITED",
        fresh_issue=950.0,
        offer_for_sale_shares=178609200,
        source="SEBI",
    )

    first = persist_ipo_record(
        record
    )

    second = persist_ipo_record(
        record
    )

    assert first["success"] is True
    assert second["success"] is True

    session = SessionLocal()

    try:

        ipo = get_ipo_by_id(
            session,
            "cultfit-2026",
        )

        assert ipo is not None

        assert (
            ipo.fresh_issue
            == 950.0
        )

        assert (
            ipo.offer_for_sale_shares
            == 178609200
        )

    finally:

        session.close()