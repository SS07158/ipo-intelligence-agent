import json

from app.retrieval.hybrid_retriever import HybridRetriever

from evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


QUESTIONS_PATH = (
    "evaluation/retrieval_questions.json"
)


def main():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    retriever = HybridRetriever()

    k = 5

    recalls = []
    precisions = []
    reciprocal_ranks = []
    category_scores = {}

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

        # print(
        #     f"\nDEBUG {item['id']}"
        # )
        # print(
        #     "Expected:",
        #     [repr(section) for section in expected_sections],
        # )
        # print(
        #     "Retrieved:",
        #     [repr(section) for section in retrieved_sections],
        # )

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

        category = item["category"]

        if category not in category_scores:
            category_scores[category] = {
                "recall": [],
                "precision": [],
                "mrr": [],
            }

        category_scores[category]["recall"].append(
            recall
        )

        category_scores[category]["precision"].append(
            precision
        )

        category_scores[category]["mrr"].append(
            mrr
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

    print("\nBy Category")
    print("=" * 60)

    for category, scores in category_scores.items():
        recall = (
            sum(scores["recall"])
            / len(scores["recall"])
        )

        precision = (
            sum(scores["precision"])
            / len(scores["precision"])
        )

        mrr = (
            sum(scores["mrr"])
            / len(scores["mrr"])
        )

        print(
            f"{category:12s} | "
            f"Recall@{k}: {recall:.3f} | "
            f"Precision@{k}: {precision:.3f} | "
            f"MRR: {mrr:.3f}"
        )


if __name__ == "__main__":
    main()