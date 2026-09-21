from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore


QUESTIONS = [
    (
        "q4",
        "What are the company's key competitive strengths?",
        "OUR STRENGTHS",
    ),
    (
        "q6",
        "What industry does the company operate in?",
        "INDUSTRY OVERVIEW",
    ),
    (
        "q7",
        "What financial information is disclosed about the company?",
        "FINANCIAL INFORMATION",
    ),
    (
        "q10",
        "What are the key factors affecting the company's industry?",
        "INDUSTRY OVERVIEW",
    ),
]


def main():
    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    for question_id, question, section in QUESTIONS:

        query_embedding = embedding_service.embed_query(
            question
        )

        results = vector_store.query(
            query_embedding=query_embedding,
            top_k=5,
            where={
                "section": section,
            },
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        print("\n" + "=" * 80)
        print(question_id)
        print("Question:", question)
        print("Section filter:", section)
        print("Retrieved:", len(documents))

        for rank, (document, metadata) in enumerate(
            zip(documents, metadatas),
            start=1,
        ):
            print("\n" + "-" * 60)
            print(f"Rank: {rank}")
            print(f"Page: {metadata.get('page_number')}")
            print(f"Section: {metadata.get('section')}")
            print(document[:700])


if __name__ == "__main__":
    main()