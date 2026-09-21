import json

from app.retrieval.hybrid_retriever import HybridRetriever


QUESTIONS_PATH = "evaluation/retrieval_questions.json"


def main():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    retriever = HybridRetriever()

    for item in questions:
        if item["id"] not in {"q13", "q21"}:
            continue

        results = retriever.retrieve(
            item["question"],
            top_k=10,
        )

        print("\n" + "=" * 80)
        print(item["id"])
        print("Question:", item["question"])
        print("Expected:", item["expected_sections"])

        print("\nRetrieved:")

        for rank, result in enumerate(
            results,
            start=1,
        ):
            metadata = result["metadata"]

            print(
                f"{rank}. "
                f"Section={metadata.get('section')} | "
                f"Subsection={metadata.get('subsection')} | "
                f"Page={metadata.get('page_number')} | "
                f"Fusion={result.get('fusion_score')}"
            )


if __name__ == "__main__":
    main()