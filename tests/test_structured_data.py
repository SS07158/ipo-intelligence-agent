from ingestion.structured_data import (
    StructuredIPORecord,
    normalize_ipo_record,
)


def test_normalize_ipo_record():

    record = StructuredIPORecord(
        ipo_id=" cultfit-2026 ",
        company_name="  Cult.Fit   Limited ",
        symbol=" cultfit ",
        fresh_issue=950.0,
        source="NSE",
    )

    normalized = normalize_ipo_record(
        record
    )

    assert (
        normalized.ipo_id
        == "cultfit-2026"
    )

    assert (
        normalized.company_name
        == "CULT.FIT LIMITED"
    )

    assert (
        normalized.symbol
        == "CULTFIT"
    )

    assert (
        normalized.fresh_issue
        == 950.0
    )

    assert (
        normalized.source
        == "NSE"
    )