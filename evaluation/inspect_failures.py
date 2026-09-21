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

        retrieved_sections = [
            result["metadata"].get("section")
            for result in results
        ]

        expected_sections = item[
            "expected_sections"
        ]

        hit = any(
            section in expected_sections
            for section in retrieved_sections
        )

        if not hit:
            print("\n" + "=" * 80)
            print(item["id"])
            print("Question:", item["question"])
            print("Expected:", expected_sections)

            print("\nRetrieved:")

            for rank, result in enumerate(
                results,
                start=1,
            ):
                metadata = result["metadata"]

                print(
                    f"{rank}. "
                    f"{metadata.get('section')} | "
                    f"page={metadata.get('page_number')} | "
                    f"distance={result.get('distance')}"
                )


if __name__ == "__main__":
    main()