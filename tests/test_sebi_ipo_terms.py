from ingestion.sebi.ipo_terms import (
    extract_ipo_terms,
)


def test_extract_cultfit_terms():

    text = """
    The Fresh Issue comprises Equity Shares
    aggregating up to ₹9,500.00 million by our Company.

    The Offer for Sale comprises up to
    178,609,200 Equity Shares by the Selling
    Shareholders.
    """

    result = extract_ipo_terms(
        text
    )

    assert (
        result["fresh_issue"]
        == 950.0
    )

    assert (
        result["offer_for_sale_shares"]
        == 178609200
    )