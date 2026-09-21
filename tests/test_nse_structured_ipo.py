from datetime import date

from ingestion.nse.structured_ipo import (
    build_structured_ipo_record,
)


def test_build_nse_structured_record():

    raw = {
        "company": "Cult.Fit Limited",
        "symbol": "-",
        "issue_open_date": "-",
        "issue_close_date": "-",
        "drhpDate": "06-Jul-2026",
        "drhpStatus": "Under Process",
    }

    result = build_structured_ipo_record(
        raw,
        ipo_id="cultfit-2026",
    )

    assert (
        result.ipo_id
        == "cultfit-2026"
    )

    assert (
        result.company_name
        == "CULT.FIT LIMITED"
    )

    assert (
        result.symbol
        is None
    )

    assert (
        result.issue_open_date
        is None
    )

    assert (
        result.fresh_issue
        is None
    )

    assert (
        result.source
        == "NSE"
    )