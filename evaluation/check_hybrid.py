from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)


retriever = HybridRetriever()

queries = [
    {
        "id": "q7",
        "question": "What financial information is disclosed about the company?",
        "expected_sections": [
            "FINANCIAL INFORMATION",
            "SUMMARY OF FINANCIAL INFORMATION",
            "RESTATED CONSOLIDATED FINANCIAL INFORMATION",
        ],
    },
    {
        "id": "q11",
        "question": "What are the company's main operations?",
        "expected_sections": [
            "OUR OPERATIONS",
        ],
    },
]


for item in queries:

    query = item["question"]
    expected_sections = item["expected_sections"]

    print("\n" + "=" * 80)
    print(item["id"])
    print("QUERY:", query)
    print("EXPECTED SECTIONS:", expected_sections)

    results = retriever.retrieve(
        query,
        top_k=5,
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):
        metadata = result["metadata"]

        section = metadata.get(
            "section",
            "",
        )

        matched = section in expected_sections

        print(
            f"{rank}. "
            f"{section} | "
            f"page={metadata.get('page_number')} | "
            f"fusion={result['fusion_score']:.4f} | "
            f"EXPECTED={matched}"
        )

        text = result.get(
            "text",
            "",
        ).replace("\n", " ")

        print(
            f"   TEXT: {text[:300]}"
        )