import json

from app.retrieval.retriever import Retriever


QUESTIONS_PATH = "evaluation/retrieval_questions.json"


def main():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    retriever = Retriever()

    for item in questions:
        results = retriever.retrieve(
            item["question"],
            top_k=5,
        )

        sections = [
            result["metadata"].get("section")
            for result in results
        ]

        print("\n" + "=" * 80)
        print(item["id"])
        print("Question:", item["question"])
        print("Expected:", item["expected_sections"])
        print("Retrieved sections:")

        for rank, section in enumerate(
            sections,
            start=1,
        ):
            print(f"{rank}. {section}")


if __name__ == "__main__":
    main()