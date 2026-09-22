from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer

from app.config import settings


BGE_MODEL_NAME = "BAAI/bge-m3"

GEMINI_EMBEDDING_MODEL = "gemini-embedding-2"
GEMINI_OUTPUT_DIMENSIONS = 1024



class EmbeddingService:
    """
    Embedding service supporting both local BGE-M3 and
    cloud Gemini Embedding 2.

    Provider is selected through settings.llm_provider:
        - ollama -> local BGE-M3
        - gemini -> Gemini Embedding 2
    """

    def __init__(
        self,
        model_name: str = BGE_MODEL_NAME,
    ):
        self.provider = settings.llm_provider.lower().strip()

        if self.provider == "ollama":
            self.model = SentenceTransformer(model_name)

        elif self.provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError(
                    "GEMINI_API_KEY is required when LLM_PROVIDER=gemini"
                )

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

        else:
            raise ValueError(
                f"Unsupported embedding provider: {settings.llm_provider}. "
                "Use 'ollama' or 'gemini'."
            )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Embed documents for storage in the vector database.
        """

        if not texts:
            return []

        if self.provider == "ollama":
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=True,
            )

            return embeddings.tolist()

        embeddings: list[list[float]] = []

        embeddings: list[list[float]] = []

        for text in texts:
            document_text = f"title: none | text: {text}"

            result = self.client.models.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                contents=document_text,
                config=types.EmbedContentConfig(
                    output_dimensionality=GEMINI_OUTPUT_DIMENSIONS,
                ),
            )

            embeddings.append(result.embeddings[0].values)

        return embeddings

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Embed a user query for vector retrieval.
        """

        if self.provider == "ollama":
            embedding = self.model.encode(
                query,
                normalize_embeddings=True,
            )

            return embedding.tolist()

        query_text = f"task: question answering | query: {query}"

        result = self.client.models.embed_content(
            model=GEMINI_EMBEDDING_MODEL,
            contents=query_text,
            config=types.EmbedContentConfig(
                output_dimensionality=GEMINI_OUTPUT_DIMENSIONS,
            ),
        )

        return result.embeddings[0].values