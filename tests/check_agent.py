from app.agents.ipo_agent import IPOAgent


agent = IPOAgent()

questions = [
    "What is the issue size?",
    "How has revenue changed?",
    "What are the biggest risks?",
]

for question in questions:
    print("\n" + "=" * 80)
    print("QUESTION:", question)

    result = agent.run(question)

    print("ROUTE:", result["route"])
    print("RESULT:", result["result"])