from pathlib import Path

import chromadb

from app.config import settings

class VectorStore:
    """
    Persistent Chroma vector store for IPO document chunks.
    """

    def __init__(
        self,
        persist_directory: str | Path = "data/chroma",
        collection_name: str | None = None,
    ):

        collection_name = (
            collection_name or settings.chroma_collection_name
        )

        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": "IPO document chunks"
            },
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """
        Add document chunks and their embeddings to Chroma.
        """

        if not (
            len(ids)
            == len(documents)
            == len(embeddings)
            == len(metadatas)
        ):
            raise ValueError(
                "ids, documents, embeddings, and metadatas "
                "must have the same length."
            )

        if not ids:
            return

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def count(self) -> int:
        """
        Return the number of stored chunks.
        """

        return self.collection.count()

    def existing_ids(
        self,
        ids: list[str],
    ) -> set[str]:
        """
        Return the IDs that already exist in the collection.
        """

        if not ids:
            return set()

        result = self.collection.get(
            ids=ids,
        )

        return set(result["ids"])

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict | None = None,
    ) -> dict:
        """
        Retrieve the most similar chunks.
        """

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where= where,
            include = [
                "documents",
                "metadatas",
                "distances", 
              ],
        )