from app.retrieval.hybrid_retriever import HybridRetriever


retriever = HybridRetriever()

queries = [
    "What industry does the company operate in?",
    "What financial information is disclosed about the company?",
]

for query in queries:
    print("\n" + "=" * 80)
    print("QUERY:", query)

    results = retriever.bm25_store.search(
        query,
        top_k=10,
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):
        metadata = result["metadata"]

        print(
            f"{rank}. "
            f"{metadata.get('section')} | "
            f"page={metadata.get('page_number')} | "
            f"score={result['score']:.4f}"
        )