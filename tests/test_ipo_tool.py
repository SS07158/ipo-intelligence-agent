from app.tools.ipo_tool import lookup_ipo

def test_lookup_exisiting_ipo():
    result = lookup_ipo("CULT.FIT LIMITED")

    assert result["found"] is True

    ipo = result["ipo"]

    assert ipo["company_name"] == "CULT.FIT LIMITED"
    assert ipo["fresh_issue"] == 950.0
    assert ipo["offer_for_sale_shares"] == 178_609_200

def test_lookup_missing_ipo():
    result = lookup_ipo("Nonexistent Company")

    assert result["found"] is False