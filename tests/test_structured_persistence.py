from unittest.mock import MagicMock, patch

from ingestion.structured_data import (
    StructuredIPORecord,
)

from ingestion.structured_persistence import (
    persist_ipo_record,
)


def test_persist_ipo_record():

    record = StructuredIPORecord(
        ipo_id="test-ipo-2026",
        company_name="TEST LIMITED",
        symbol="TEST",
        fresh_issue=500.0,
        source="NSE",
    )

    mock_ipo = MagicMock()

    mock_ipo.ipo_id = "test-ipo-2026"
    mock_ipo.company_name = "TEST LIMITED"
    mock_ipo.symbol = "TEST"
    mock_ipo.fresh_issue = 500.0
    mock_ipo.offer_for_sale = None
    mock_ipo.offer_for_sale_shares = None
    mock_ipo.price_band_low = None
    mock_ipo.price_band_high = None
    mock_ipo.lot_size = None
    mock_ipo.issue_open_date = None
    mock_ipo.issue_close_date = None
    mock_ipo.listing_date = None

    mock_session = MagicMock()

    with patch(
        "ingestion.structured_persistence.SessionLocal",
        return_value=mock_session,
    ), patch(
        "ingestion.structured_persistence.upsert_structured_ipo",
        return_value=mock_ipo,
    ):

        result = persist_ipo_record(
            record
        )

    assert (
        result["success"]
        is True
    )

    assert (
        result["ipo_id"]
        == "test-ipo-2026"
    )

    assert (
        result["fresh_issue"]
        == 500.0
    )