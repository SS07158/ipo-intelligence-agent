from app.retrieval.embedding_service import EmbeddingService


def test_embedding_service():
    service = EmbeddingService()

    embeddings = service.embed_documents(
        [
            "What are the major risks?",
            "The company faces significant business risks.",
        ]
    )

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 1024


def test_query_embedding():
    service = EmbeddingService()

    embedding = service.embed_query(
        "What are the major risks?"
    )

    assert len(embedding) == 1024