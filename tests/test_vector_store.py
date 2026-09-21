from app.retrieval.vector_store import VectorStore


def test_vector_store():
    store = VectorStore(
        persist_directory="data/chroma_test",
        collection_name="test_collection",
    )

    ids = ["test-1", "test-2"]

    documents = [
        "The company faces competition risks.",
        "The company operates fitness centers.",
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    metadatas = [
        {
            "company": "TEST",
            "page_number": 1,
            "section": "RISK FACTORS",
        },
        {
            "company": "TEST",
            "page_number": 2,
            "section": "OUR BUSINESS",
        },
    ]

    store.add_documents(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    assert store.count() == 2

    results = store.query(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=1,
    )

    assert len(results["documents"][0]) == 1
    assert results["documents"][0][0] == (
        "The company faces competition risks."
    )

    results = store.query(
        query_embedding=[0.0, 1.0, 0.0],
        top_k=5,
        where={
            "section": "OUR BUSINESS"
        },
    )

    assert len(results["documents"][0]) == 1
    assert results["documents"][0][0] == (
        "The company operates fitness centers."
    )