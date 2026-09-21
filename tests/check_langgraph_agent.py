from app.agents.langgraph_agent import (
    LangGraphIPOAgent,
)


agent = LangGraphIPOAgent()

question = (
    "How has CULT.FIT's revenue changed, "
    "and what risks could affect that growth?"
)

result = agent.run(question)

print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(result["answer"])

print("\nMESSAGE TRACE:")

for message in result["messages"]:
    print(
        type(message).__name__,
        "→",
        getattr(message, "content", ""),
    )