from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"

class EmbeddingService:
    """
    Generate embeddings using a local Hugging Face model
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ):
        self.model = SentenceTransformer(model_name)

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        """
        Generate embeddings for multiple documents
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()


    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a query
        """

        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        return embedding.tolist()
        