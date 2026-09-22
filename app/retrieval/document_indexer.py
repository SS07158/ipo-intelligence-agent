from pathlib import Path

from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore
from ingestion.sebi.chunk_builder import build_chunks
from ingestion.sebi.document_parser import parse_document
from ingestion.sebi.metadata import add_metadata
from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)


class DocumentIndexer:
    """
    Convert an IPO PDF into searchable vector-store documents.
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

    def index_document(
        self,
        pdf_path: str | Path,
        config: SEBIDocumentConfig | None = None,
    ) -> int:
        """
        Extract, chunk, embed, and index a PDF.

        Args:
            pdf_path:
                Path to the PDF.

            config:
                Optional SEBI document configuration used
                to attach canonical document metadata.

        Returns:
            Number of chunks indexed.
        """

        pages = parse_document(
            pdf_path
        )

        chunks = build_chunks(
            pages
        )

        
        if config is not None:
            enriched_chunks = add_metadata(
                chunks,
                config,
            )
        else:
            enriched_chunks = chunks

        if config is not None:

            for chunk in enriched_chunks:

                chunk["document_id"] = (
                    config.document_id
                )

                chunk["ipo_id"] = (
                    config.ipo_id
                )

                chunk["company"] = (
                    config.company_name
                )

                chunk["document_type"] = (
                    config.document_type
                )

                chunk["source"] = (
                    config.source
                )

        if not enriched_chunks:
            return 0

        texts = [
            chunk["text"]
            for chunk in enriched_chunks
        ]

        embeddings = (
            self.embedding_service.embed_documents(
                texts
            )
        )

        ids = [
            (
                f"{chunk.get('document_id', 'document')}"
                f"-chunk-{chunk['chunk_index']}"
            )
            for chunk in enriched_chunks
        ]

        metadatas = []

        for chunk in enriched_chunks:

            metadata = {
                "document_id": chunk.get("document_id", ""),
                "ipo_id": chunk.get("ipo_id", ""),
                "company": chunk.get("company", ""),
                "document_type": chunk.get("document_type", ""),
                "source": chunk.get("source", ""),
                "page_number": chunk[
                    "page_number"
                ],
                "section": chunk[
                    "section"
                ],
                "subsection": (
                    chunk["subsection"]
                    or ""
                ),
                "chunk_index": chunk[
                    "chunk_index"
                ],
            }

            if config is not None:
                metadata.update(
                    {
                        "document_id": (
                            config.document_id
                        ),
                        "ipo_id": (
                            config.ipo_id
                        ),
                        "company": (
                            config.company_name
                        ),
                        "document_type": (
                            config.document_type
                        ),
                        "source": (
                            config.source
                        ),
                        "source_url": (
                            config.source_url
                        ),
                        "version": config.version or "",
                        "published_at": (
                            config.published_at.isoformat()
                            if config.published_at
                            else ""
                        )
                    }
                )

            metadatas.append(
                metadata
            )

        self.vector_store.add_documents(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(
            enriched_chunks
        )