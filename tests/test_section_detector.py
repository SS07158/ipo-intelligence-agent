from ingestion.sebi.section_detector import is_heading


def test_uppercase_heading():
    assert is_heading("RISK FACTORS")


def test_normal_sentence():
    assert not is_heading(
        "The company operates fitness centers across multiple cities."
    )


def test_empty_text():
    assert not is_heading("")


def test_long_text():
    text = "A" * 200
    assert not is_heading(text)