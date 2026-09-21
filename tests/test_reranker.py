class FakeCrossEncoder:
    def predict(self, pairs):
        return [
            0.2,
            0.9,
            0.5,
        ]


def test_reranker():
    from app.retrieval.reranker import Reranker

    reranker = Reranker.__new__(
        Reranker
    )

    reranker.model = FakeCrossEncoder()

    results = [
        {
            "id": "a",
            "text": "Document A",
            "metadata": {
                "section": "SECTION A",
            },
        },
        {
            "id": "b",
            "text": "Document B",
            "metadata": {
                "section": "SECTION B",
            },
        },
        {
            "id": "c",
            "text": "Document C",
            "metadata": {
                "section": "SECTION C",
            },
        },
    ]

    ranked = reranker.rerank(
        "test query",
        results,
        top_k=2,
    )

    assert len(ranked) == 2
    assert ranked[0]["id"] == "b"
    assert ranked[1]["id"] == "c"