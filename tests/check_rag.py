from app.retrieval.rag_service import RAGService


rag = RAGService()

question = (
    "Whats is the company's favorite football team?"
)

result = rag.answer(
    question,
    top_k=5,
)

print("\nANSWER")
print("=" * 80)
print(result["answer"])

print("\nEVIDENCE")
print("=" * 80)

for item in result["evidence"]:
    citation = item["citation"]

    print(
        f"{item['id']} | "
        f"{citation.get('section')} | "
        f"Page {citation.get('page_number')}"
    )

print("\nCITATION VALIDATION")
print("=" * 80)
print(result["citation_validation"])