import json
from pathlib import Path

from app.agents.langgraph_agent import (
    LangGraphIPOAgent,
)


BASE_DIR = Path(
    __file__
).resolve().parent


def main():

    with (
        BASE_DIR
        / "failure_questions.json"
    ).open(
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    agent = LangGraphIPOAgent()

    total = len(dataset)
    graceful = 0

    for item in dataset:

        print("\n" + "=" * 70)
        print(
            item["id"],
            "|",
            item["question"],
        )

        try:
            result = agent.run(
                item["question"]
            )

            answer = result.get(
                "answer",
                "",
            )

            print("\nANSWER:")
            print(answer)

            # A graceful answer should exist rather
            # than the graph crashing.
            if answer.strip():
                graceful += 1
                print(
                    "Graceful: True"
                )
            else:
                print(
                    "Graceful: False"
                )

        except Exception as exc:

            print(
                "Graceful: False"
            )

            print(
                "ERROR:",
                exc,
            )

    rate = (
        graceful / total
        if total
        else 0.0
    )

    print("\n" + "=" * 70)
    print(
        "Failure Handling Success:",
        f"{rate:.3f}",
    )

    print(
        f"Graceful: {graceful}/{total}"
    )


if __name__ == "__main__":
    main()