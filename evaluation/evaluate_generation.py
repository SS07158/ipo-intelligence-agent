import json

from app.retrieval.rag_service import RAGService
from evaluation.answer_metrics import (
    answer_contains_value,
)
from evaluation.citation_support import (
    claim_numeric_supported,
)
from evaluation.answer_relevance import (
    keyword_relevance,
)

from evaluation.groundness import (
    numeric_groundedness,
    claim_level_groundedness,
)


QUESTIONS_PATH = (
    "evaluation/generation_questions.json"
)


def main():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    rag = RAGService()

    for item in questions:

        print("\n" + "=" * 80)
        print(item["id"])
        print("Question:", item["question"])

        result = rag.answer(
            item["question"],
            top_k=5,
        )

        answer = result["answer"]

        relevance = keyword_relevance(
            item["question"],
            answer,
        )

        grounded = numeric_groundedness(
            answer,
            result["evidence"],
        )

        claim_grounded = claim_level_groundedness(
            answer,
            result["evidence"],
        )

        print(
            "Answer relevance:",
            round(relevance, 3),
        )

        print(
            "Numeric groundedness:",
            grounded,
        )

        print(
            "Claim-level groundness:",
            round(
                claim_grounded,
                3,  
            ),
        )

        citation_support = None

        if item["expected_answer_contains"]:
            cited_numbers = []

            for reference in result[
                "citation_validation"
            ]["references"]:

                if 1 <= reference <= len(
                    result["evidence"]
                ):
                    evidence_item = result[
                        "evidence"
                    ][reference - 1]

                    cited_numbers.append(
                        evidence_item["text"]
                    )

            combined_evidence = "\n".join(
                cited_numbers
            )

            expected_terms = item[
                "expected_answer_contains"
            ]

            # Some values can have equivalent representations,
            # such as ₹950 crore and ₹9,500 million.
            # Only validate the representation actually used
            # by the generated answer.
            matched_terms = [
                term
                for term in expected_terms
                if answer_contains_value(
                    term,
                    answer,
                )
            ]

            citation_support = bool(
                matched_terms
            ) and all(
                claim_numeric_supported(
                    term,
                    combined_evidence,
                )
                for term in matched_terms
            )

        print("\nANSWER")
        print(answer)

        print("\nCITATIONS")
        print(
            result["citation_validation"]
        )

        print("\nEXPECTED ANSWER TERMS")

        for term in item[
            "expected_answer_contains"
        ]:
            print(
                term,
                "→",
                answer_contains_value(
                    term,
                    answer,
                ),
            )

            print(
                "Citation numeric support:",
                citation_support,
            )


if __name__ == "__main__":
    main()