import json
from pathlib import Path

from app.tools.news_tool import lookup_news


BASE_DIR = Path(__file__).resolve().parent


def main():
    dataset_path = BASE_DIR / "news_questions.json"

    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    total = len(questions)
    correct = 0

    print("=" * 70)
    print("NEWS EVALUATION")
    print("=" * 70)

    for item in questions:

        question = item["question"]
        expected_company = item["expected_company"]
        expected_count = item["expected_article_count"]

        print("\n" + "=" * 70)
        print(
            f"{item['id']} | "
            f"{question}"
        )

        result = lookup_news(
            expected_company
        )

        actual_company = result.get(
            "company_name"
        )

        actual_count = len(
            result.get(
                "articles",
                [],
            )
        )

        company_correct = (
            actual_company
            == expected_company
        )

        count_correct = (
            actual_count
            == expected_count
        )

        is_correct = (
            company_correct
            and count_correct
        )

        if is_correct:
            correct += 1

        print(
            "Expected company:",
            expected_company,
        )

        print(
            "Actual company:",
            actual_company,
        )

        print(
            "Expected articles:",
            expected_count,
        )

        print(
            "Actual articles:",
            actual_count,
        )

        print(
            "Correct:",
            is_correct,
        )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    print("\n" + "=" * 70)
    print(
        f"News Lookup Accuracy: "
        f"{accuracy:.3f}"
    )

    print(
        f"Correct: {correct}/{total}"
    )


if __name__ == "__main__":
    main()