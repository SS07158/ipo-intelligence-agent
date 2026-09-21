from app.retrieval.llm_service import LLMService


llm = LLMService()

response = llm.generate(
    [
        (
            "system",
            "You are a concise assistant.",
        ),
        (
            "human",
            "Explain what an IPO is in one sentence.",
        ),
    ]
)

print(response)