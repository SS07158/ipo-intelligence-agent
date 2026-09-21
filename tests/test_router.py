from app.agents.router import classify_question


def test_financial_question():
    assert (
        classify_question(
            "How has revenue changed?"
        )
        == "financial"
    )


def test_ipo_question():
    assert (
        classify_question(
            "What is the issue size?"
        )
        == "ipo"
    )


def test_rag_question():
    assert (
        classify_question(
            "What are the biggest risks?"
        )
        == "rag"
    )


def test_mixed_question():
    assert (
        classify_question(
            "How has revenue changed and what risks does the company face?"
        )
        == "mixed"
    )