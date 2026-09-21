from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.retrieval.evidence import format_evidence


class Retriever:
    """
    Retrieve relevant document chunks using semantic similarity.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.vector_store = (
            vector_store
            or VectorStore()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        where: dict | None = None,
    ) -> list[dict]:
        """
        Retrieve the most relevant chunks for a query.
        """

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        query_embedding = (
            self.embedding_service.embed_query(
                query
            )
        )

        results = self.vector_store.query(
            query_embedding=query_embedding,
            top_k=top_k,
            where=where,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        retrieved = []

        for index, document in enumerate(documents):
            retrieved.append(
                format_evidence(
            {
                 "id": ids[index],
                 "text": document,
                 "metadata": metadatas[index],
                 "distance": distances[index],
            }
                )
            )

        return retrieved