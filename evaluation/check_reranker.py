from app.retrieval.reranked_retriever import (
    RerankedRetriever,
)


retriever = RerankedRetriever()

queries = [
    "What are the company's key competitive strengths?",
    "What industry does the company operate in?",
    "What financial information is disclosed about the company?",
    "What are the key factors affecting the company's industry?",
]


for query in queries:

    print("\n" + "=" * 80)
    print("QUERY:", query)

    results = retriever.retrieve(
        query,
        top_k=5,
        candidate_k=20,
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
            f"rerank={result['rerank_score']:.4f}"
        )