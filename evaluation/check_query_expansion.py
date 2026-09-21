from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)


retriever = HybridRetriever()

queries = [
    "What does the DRHP say about India's fitness and active lifestyle market?",
    "What are the key characteristics of the Indian fitness market?",
    "What factors are expected to support growth in the fitness market?",
]

for query in queries:
    print("\n" + "=" * 80)
    print("QUERY:", query)

    results = retriever.retrieve(
        query,
        top_k=5,
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
            f"fusion={result['fusion_score']:.4f}"
        )