from app.retrieval.retriever import Retriever


class FakeEmbeddingService:
    def embed_query(self, query: str):
        return [1.0, 0.0]


class FakeVectorStore:
    def query(
        self,
        query_embedding,
        top_k,
        where=None,
    ):
        return {
            "ids": [
                ["chunk-1"]
            ],
            "documents": [
                ["A sample risk factor."]
            ],
            "metadatas": [
                [
                    {
                        "page_number": 142,
                        "section": "RISK FACTORS",
                    }
                ]
            ],
            "distances": [
                [0.12]
            ],
        }


def test_retriever():
    retriever = Retriever(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
    )

    results = retriever.retrieve(
        "What are the risks?"
    )

    assert len(results) == 1
    assert results[0]["id"] == "chunk-1"
    assert (
        results[0]["citation"]["section"]
        == "RISK FACTORS"
    )