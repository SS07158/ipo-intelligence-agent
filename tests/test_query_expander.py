from app.retrieval.query_expander import expand_query


def test_industry_expansion():
    query = "What industry does the company operate in?"

    expanded = expand_query(query)

    assert "fitness industry" in expanded
    assert "fitness market" in expanded


def test_financial_expansion():
    query = "What financial information is disclosed?"

    expanded = expand_query(query)

    assert "financial information" in expanded
    assert "profit" in expanded


def test_no_expansion():
    query = "What is the company name?"

    expanded = expand_query(query)

    assert expanded == query