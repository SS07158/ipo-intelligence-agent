import json

from app.agents.langgraph_agent import (
    LangGraphIPOAgent,
)

from evaluation.answer_metrics import (
    answer_contains_value,
    answer_contains_points,
    evidence_section_hit,
)


QUESTIONS_PATH = (
    "evaluation/answer_questions.json"
)


def collect_document_evidence(
    tool_results: list[dict],
) -> list[dict]:
    """
    Collect document-search evidence from agent tool results.

    Only document-search results are considered for
    section-based evaluation.
    """
    evidence = []

    for item in tool_results:
        if item.get("tool") != "search_ipo_documents_tool":
            continue

        result = item.get(
            "result",
            {},
        )

        if not isinstance(result, dict):
            continue

        documents = result.get(
            "evidence",
            []
        )

        if not isinstance(
            documents,
            list,
        ):
            continue

        for document in documents:
            if not isinstance(
                document,
                dict,
            ):
                continue

            evidence.append(
                document
            )

    return evidence


def main():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    agent = LangGraphIPOAgent()

    total_questions = 0

    numeric_questions = 0
    numeric_hits = 0

    qualitative_questions = 0
    qualitative_scores = []

    section_evaluable_questions = 0
    section_hits = 0

    for item in questions:

        total_questions += 1

        import time 

        print(f"\n[{item['id']}] START: {item["question"]}", flush=True)

        start_time = time.time()  

        result = agent.run(
            item["question"]
        )

        elapsed = time.time() - start_time

        print(
            f"[{item['id']}] DONE in {elapsed:.2f}s",
            flush=True,
        )

        print(
            f"[{item['id']}] TOOLS: "
            f"{[x['tool'] for x in result['tool_results']]}",
            flush=True,
        )

        answer = result.get(
            "answer",
            "",
        )

        tool_results = result.get(
            "tool_results",
            [],
        )

        document_evidence = (
            collect_document_evidence(
                tool_results
            )
        )

        print("\n" + "=" * 80)
        print(item["id"])
        print(
            "Question:",
            item["question"],
        )

        # -------------------------------------------------
        # Tool execution
        # -------------------------------------------------

        print(
            "Tools used:",
            [
                item.get("tool")
                for item in tool_results
            ],
        )

        # -------------------------------------------------
        # Evidence section evaluation
        # -------------------------------------------------

        expected_sections = item.get(
            "expected_sections",
            [],
        )

        is_rag_question = (
            "search_ipo_documents_tool"
            in [
                tool_result.get("tool")
                for tool_result in tool_results
            ]
        )

        if expected_sections and is_rag_question:

            section_evaluable_questions += 1

            section_hit = evidence_section_hit(
                expected_sections,
                document_evidence,
            )

            if section_hit:
                section_hits += 1

            print(
                "Evidence section hit:",
                section_hit,
            )

        # -------------------------------------------------
        # Numeric answer evaluation
        # -------------------------------------------------

        gold_answer = item.get(
            "gold_answer"
        )

        if gold_answer is not None:

            numeric_questions += 1

            numeric_hit = answer_contains_value(
                gold_answer,
                answer,
            )

            if numeric_hit:
                numeric_hits += 1

            print(
                "Expected value:",
                gold_answer,
                item.get("unit"),
            )

            print(
                "Answer value hit:",
                numeric_hit,
            )

        # -------------------------------------------------
        # Qualitative answer evaluation
        # -------------------------------------------------

        expected_points = item.get(
            "expected_answer_points",
            [],
        )

        if expected_points:

            qualitative_questions += 1

            point_result = answer_contains_points(
                expected_points,
                answer,
            )

            qualitative_scores.append(
                point_result["score"]
            )

            print(
                "Expected answer points:",
                expected_points,
            )

            print(
                "Matched points:",
                point_result["matched"],
            )

            print(
                "Missing points:",
                point_result["missing"],
            )

            print(
                "Answer point coverage:",
                round(
                    point_result["score"],
                    3,
                ),
            )

        print("\nANSWER")
        print(answer)

    # -----------------------------------------------------
    # Overall metrics
    # -----------------------------------------------------

    print("\n" + "=" * 80)
    print("OVERALL ANSWER EVALUATION")
    print("=" * 80)

    print(
        f"Questions evaluated: "
        f"{total_questions}"
    )

    if section_evaluable_questions:

        print(
            f"Document Evidence Section Recall: "
            f"{section_hits / section_evaluable_questions:.3f}"
        )

    if numeric_questions:

        print(
            f"Numeric Answer Accuracy: "
            f"{numeric_hits / numeric_questions:.3f}"
        )

    if qualitative_questions:

        print(
            f"Qualitative Answer Point Coverage: "
            f"{sum(qualitative_scores) / len(qualitative_scores):.3f}"
        )


if __name__ == "__main__":
    main()