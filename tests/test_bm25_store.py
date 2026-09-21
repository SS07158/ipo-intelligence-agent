from app.retrieval.bm25_store import BM25Store


def test_bm25_store():
    store = BM25Store()

    store.build(
        ids=[
            "a",
            "b",
            "c",
        ],
        documents=[
            "fitness industry overview",
            "financial information revenue profit",
            "company operates fitness centers",
        ],
        metadatas=[
            {"section": "INDUSTRY OVERVIEW"},
            {"section": "FINANCIAL INFORMATION"},
            {"section": "OUR BUSINESS",}
        ],
    )

    results = store.search(
        "financial information",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == "b"


def test_bm25_matches_section_name():
    store = BM25Store()

    store.build(
        ids=[
            "a",
            "b",
            "c",
            "d",
        ],
        documents=[
            "The company operates across India.",
            "Revenue and profit information is disclosed.",
            "The business has several fitness centers.",
            "The company has a large customer base.",
        ],
        metadatas=[
            {
                "section": "INDUSTRY OVERVIEW"
            },
            {
                "section": "FINANCIAL INFORMATION"
            },
            {
                "section": "OUR BUSINESS"
            },
            {
                "section": "OUR STRATEGIES"
            },
        ],
    )

    results = store.search(
        "financial information",
        top_k=1,
    )

    assert results[0]["id"] == "b"

def test_section_score_is_returned():
    store = BM25Store()

    store.build(
        ids=[
            "a",
            "b",
            "c",
            "d",
        ],
        documents=[
            "The company operates across India.",
            "Revenue and profit information is disclosed.",
            "The business has several fitness centers.",
            "The company has a large customer base.",
        ],
        metadatas=[
            {
                "section": "INDUSTRY OVERVIEW"
            },
            {
                "section": "FINANCIAL INFORMATION"
            },
            {
                "section": "OUR BUSINESS"
            },
            {
                "section": "OUR STRATEGIES"
            },
        ],
    )

    results = store.search(
        "financial information",
        top_k=1,
    )

    assert results[0]["id"] == "b"
    assert "section_score" in results[0]
    assert "document_score" in results[0]
    