from app.ingestion.fake_source import (
    FakeIPODataSource,
)


def test_fetch_ipo():

    source = FakeIPODataSource()

    result = source.fetch_ipo(
        "CULT.FIT LIMITED"
    )

    assert result is not None

    assert (
        result.company_name
        == "CULT.FIT LIMITED"
    )

    assert (
        result.data["fresh_issue"]
        == 950.0
    )


def test_unknown_company():

    source = FakeIPODataSource()

    result = source.fetch_ipo(
        "UNKNOWN IPO"
    )

    assert result is None