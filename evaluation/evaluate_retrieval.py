import json
from pathlib import Path

from app.retrieval.hybrid_retriever import HybridRetriever

from evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


QUESTIONS_PATH = Path(
    "evaluation/retrieval_questions.json"
)


def main() -> None:
    with QUESTIONS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    retriever = HybridRetriever()

    k = 5

    recalls = []
    precisions = []
    reciprocal_ranks = []

    for item in questions:
        results = retriever.retrieve(
            item["question"],
            top_k=k,
        )

        retrieved_sections = [
            result["metadata"].get("section")
            for result in results
        ]

        expected_sections = item[
            "expected_sections"
        ]

        recall = recall_at_k(
            retrieved_sections,
            expected_sections,
            k,
        )

        precision = precision_at_k(
            retrieved_sections,
            expected_sections,
            k,
        )

        mrr = reciprocal_rank(
            retrieved_sections,
            expected_sections,
        )

        recalls.append(recall)
        precisions.append(precision)
        reciprocal_ranks.append(mrr)

        print(
            f"{item['id']} | "
            f"Recall@{k}: {recall:.3f} | "
            f"Precision@{k}: {precision:.3f} | "
            f"MRR: {mrr:.3f}"
        )

    print("\nOverall")
    print("=" * 60)

    print(
        f"Mean Recall@{k}: "
        f"{sum(recalls) / len(recalls):.3f}"
    )

    print(
        f"Mean Precision@{k}: "
        f"{sum(precisions) / len(precisions):.3f}"
    )

    print(
        f"MRR: "
        f"{sum(reciprocal_ranks) / len(reciprocal_ranks):.3f}"
    )


if __name__ == "__main__":
    main()