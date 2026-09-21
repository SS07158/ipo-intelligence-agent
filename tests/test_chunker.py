import pytest

from ingestion.sebi.chunker import chunk_text


def test_empty_text():
    assert chunk_text("") == []


def test_small_text():
    text = "one two three four five"

    chunks = chunk_text(
        text,
        chunk_size=3,
        overlap=1,
    )

    assert chunks == [
        "one two three",
        "three four five",
    ]


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=0)


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "some text",
            chunk_size=10,
            overlap=10,
        )