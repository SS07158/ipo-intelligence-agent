import json

from app.retrieval.hybrid_retriever import HybridRetriever


QUESTIONS_PATH = "evaluation/answer_questions.json"


def main():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    retriever = HybridRetriever()

    for item in questions:

        print("\n" + "=" * 80)
        print(item["id"])
        print("Question:", item["question"])

        results = retriever.retrieve(
            item["question"],
            top_k=5,
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):
            metadata = result["metadata"]

            print("\n" + "-" * 70)

            print(
                f"Rank: {rank}"
            )

            print(
                f"ID: {result['id']}"
            )

            print(
                f"Section: "
                f"{metadata.get('section')}"
            )

            print(
                f"Subsection: "
                f"{metadata.get('subsection')}"
            )

            print(
                f"Page: "
                f"{metadata.get('page_number')}"
            )

            print(
                f"Fusion: "
                f"{result.get('fusion_score')}"
            )

            print(
                result["text"][:1200]
            )


if __name__ == "__main__":
    main()