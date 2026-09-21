import json
from pathlib import Path

from app.agents.langgraph_agent import (
    LangGraphIPOAgent,
)
from evaluation.agent_metrics import (
    tool_execution_success,
)




BASE_DIR = Path(
    __file__
).resolve().parent


def normalize_tools(
    tools: list[str],
) -> set[str]:
    """
    Normalize tool names into a set.
    """

    return {
        tool.strip()
        for tool in tools
    }


def tool_selection_correct(
    expected: list[str],
    actual: list[str],
) -> bool:
    """
    Exact tool-set match.
    """

    return (
        normalize_tools(expected)
        == normalize_tools(actual)
    )


def extract_tool_calls(
    result: dict,
) -> list[str]:
    """
    Extract tool names from the LangGraph
    execution trace.
    """

    names = []

    for message in result.get(
        "messages",
        [],
    ):
        tool_calls = getattr(
            message,
            "tool_calls",
            [],
        )

        for tool_call in tool_calls:

            name = tool_call.get(
                "name"
            )

            if name:
                names.append(
                    name
                )

    return names


def main():
    dataset_path = (
        BASE_DIR
        / "agent_questions.json"
    )

    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    agent = LangGraphIPOAgent()

    total = len(dataset)
    correct = 0

    print("=" * 70)
    print("AGENT EVALUATION")
    print("=" * 70)

    execution_success = 0

    for item in dataset:

        question = item["question"]
        expected = item[
            "expected_tools"
        ]

        print("\n" + "=" * 70)
        print(
            f"{item['id']} | "
            f"{question}"
        )

        result = agent.run(
            question
        )


        execution_ok = (
            tool_execution_success(
                result
            )
        )

        if execution_ok:
            execution_success += 1

        print(
            "Execution success: ",
            execution_ok
        )

        actual = extract_tool_calls(
            result
        )

        is_correct = (
            tool_selection_correct(
                expected,
                actual,
            )
        )

        if is_correct:
            correct += 1

        print(
            "Expected:",
            expected,
        )

        print(
            "Actual:",
            actual,
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
        f"Tool Selection Accuracy: "
        f"{accuracy:.3f}"
    )
    print(
        f"Correct: {correct}/{total}"
    )

    execution_rate = (
        execution_success / total
        if total
        else 0.0
    )

    print(
        f"Tool Execution Success: "
        f"{execution_rate:.3f}"
    )

def multi_tool_exact_match(
    expected: list[str],
    actual: list[str],
) -> bool:
    return (
        len(expected) > 1
        and tool_selection_correct(
            expected,
            actual,
        )
    )


if __name__ == "__main__":
    main()