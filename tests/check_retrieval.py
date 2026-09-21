from app.retrieval.retriever import Retriever


retriever = Retriever()

query = "What risks does company face?"

results = retriever.retrieve(
    query,
    top_k=5,
    where={
        "section":"INTERNAL RISKS"
    }
)

print(f"\nQuery: {query}")
print(f"Results: {len(results)}")

for rank, result in enumerate(results, start=1):
    citation = result["citation"]

    print("\n" + "=" * 80)
    print(f"RANK: {rank}")
    print(f"ID: {result['id']}")
    print(f"DISTANCE: {result['retrieval_distance']}")
    print(f"COMPANY: {citation['company']}")
    print(f"DOCUMENT: {citation['document_type']}")
    print(f"SECTION: {citation['section']}")
    print(f"PAGE: {citation['page_number']}")
    print(f"SOURCE: {citation['source']}")
    print("=" * 80)
    print(result["text"][:1000])