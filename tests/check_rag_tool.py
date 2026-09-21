from app.tools.rag_tools import search_ipo_documents


result = search_ipo_documents(
    "What are the major risks mentioned in the CULT.FIT DRHP?",
    top_k=5,
)

print("\nANSWER")
print("=" * 80)
print(result["answer"])

print("\nCITATION VALIDATION")
print("=" * 80)
print(result["citation_validation"])

print("\nEVIDENCE")
print("=" * 80)

for evidence in result["evidence"]:
    citation = evidence["citation"]

    print(
        f"{evidence['id']} | "
        f"{citation['section']} | "
        f"Page {citation['page_number']}"
    )