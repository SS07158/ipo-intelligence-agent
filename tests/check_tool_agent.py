from app.agents.tool_agent import ToolAgent


agent = ToolAgent()


questions = [
    # "What is the fresh issue size of CULT.FIT?",
    # "What was revenue from operations in FY2026?",
    # "What are the major internal risks?",
    # "How has CULT.FIT's revenue changed, and what risks could affect that growth?",
    "What has been the financial performance of CULT.FIT and what are its major internal risks?"
]


for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:")
    print(question)

    result = agent.run(
        question
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nTOOL CALLS:")
    for tool_call in result["tool_calls"]:
        print(tool_call)

    print("\nTOOL RESULTS:")
    for tool_result in result["tool_results"]:
        print(
            tool_result["tool"]
        )
        print(
            tool_result["result"]
        )