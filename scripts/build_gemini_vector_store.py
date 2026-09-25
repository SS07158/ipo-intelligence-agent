import time
from pathlib import Path

from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore
from ingestion.sebi.chunk_builder import build_chunks
from ingestion.sebi.document_parser import parse_document
from ingestion.sebi.metadata import add_metadata
from ingestion.sebi.document_config import SEBIDocumentConfig
from ingestion.sebi.register_document import mark_document_indexed


CHROMA_PATH = Path("data/chroma")

GEMINI_COLLECTION_NAME = "ipo_documents_gemini"

BATCH_SIZE = 24

RATE_LIMIT_PAUSE = 16

documents = [
    SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="cultfit-drhp-2026",
        company_name="CULT.FIT LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url=(
            "https://www.sebi.gov.in/"
            "filings/public-issues/jul-2026/"
            "cult-fit-limited-drhp_102714.html"
        ),
        local_path=(
            "data/raw/sebi/cultfit/"
            "cultfit_drhp.pdf"
        ),
        version="2026-07",
    ),
    SEBIDocumentConfig(
        ipo_id="sterlite-electric-2026",
        document_id="sterlite-electric-drhp-2026",
        company_name="Sterlite Electric Limited",
        document_type="DRHP",
        source="NSE",
        source_url=None,
        local_path=(
            "data/raw/nse/"
            "sterlite_electric_limited/"
            "sbhatnagar_01102025164001_"
            "Sterlite_Electric_Limited_DRHP.pdf"
        ),
        version="2026-09",
    ),
]


def build_metadata(
    chunks: list[dict],
    config: SEBIDocumentConfig,
) -> list[dict]:
    """
    Build Chroma metadata for a batch of chunks.
    """

    enriched_chunks = add_metadata(
        chunks,
        config,
    )

    metadatas = []

    for chunk in enriched_chunks:
        metadatas.append(
            {
                "document_id": chunk["document_id"],
                "ipo_id": chunk["ipo_id"],
                "company": chunk["company"],
                "document_type": chunk["document_type"],
                "source": chunk["source"],
                "page_number": chunk["page_number"],
                "section": chunk["section"],
                "risk_category": (
                    chunk.get("risk_category")
                    or ""
                ),
                "subsection": (
                    chunk.get("subsection")
                    or ""
                ),
                "chunk_index": chunk["chunk_index"],
                "source_url": config.source_url or "",
                "version": config.version or "",
                "published_at": (
                    config.published_at.isoformat()
                    if config.published_at
                    else ""
                ),
            }
        )

    return enriched_chunks, metadatas


def index_document(
    embedding_service: EmbeddingService,
    vector_store: VectorStore,
    config: SEBIDocumentConfig,
) -> int:
    """
    Index one document in resumable batches.
    """

    print(
        f"\nINDEXING: {config.company_name}"
    )

    pages = parse_document(
        config.local_path
    )

    chunks = build_chunks(
        pages
    )

    if not chunks:
        print("No chunks found.")
        return 0

    enriched_chunks, metadatas = build_metadata(
        chunks,
        config,
    )

    ids = [
        (
            f"{chunk['document_id']}"
            f"-chunk-{chunk['chunk_index']}"
        )
        for chunk in enriched_chunks
    ]

    existing_ids = vector_store.existing_ids(
        ids
    )

    pending = []

    for index, chunk_id in enumerate(ids):
        if chunk_id not in existing_ids:
            pending.append(index)

    print(
        f"Total chunks: {len(ids)}"
    )

    print(
        f"Already indexed: {len(existing_ids)}"
    )

    print(
        f"Remaining: {len(pending)}"
    )

    indexed_now = 0

    for batch_number, start in enumerate(
        range(
            0,
            len(pending),
            BATCH_SIZE,
        ),
        start=1,
    ):
        batch_indexes = pending[
            start:start + BATCH_SIZE
        ]

        batch_chunks = [
            enriched_chunks[index]
            for index in batch_indexes
        ]

        batch_ids = [
            ids[index]
            for index in batch_indexes
        ]

        batch_texts = [
            chunk["text"]
            for chunk in batch_chunks
        ]

        batch_metadatas = [
            metadatas[index]
            for index in batch_indexes
        ]

        print(
            f"Embedding batch {batch_number}: "
            f"{len(batch_texts)} chunks"
        )

        while True:
            try:
                batch_embeddings = (
                    embedding_service.embed_documents(
                        batch_texts
                    )
                )

                break

            except Exception as exc:
                message = str(exc)

                if "RequestsPerDay" in message or "PerDayPerUser" in message:
                    raise RuntimeError(
                        "Gemini daily embedding quota has been exhausted. "
                        "Stop now and resume the indexing after the quota resets."
                    ) from exc

                if "429" not in message and "RESOURCE_EXHAUSTED" not in message:
                    raise

                print("Gemini rate limit reached.")
                print("Waiting 61 seconds before retry...")
                time.sleep(61)

        vector_store.add_documents(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
        )

        indexed_now += len(batch_ids)

        print(
            f"Persisted batch {batch_number}. "
            f"New chunks indexed: {indexed_now}"
        )

        if (
            start + BATCH_SIZE
            < len(pending)
        ):
            print(
                "Pausing briefly for Gemini "
                "free-tier rate limits..."
            )

            time.sleep(RATE_LIMIT_PAUSE)

    final_count = vector_store.count()

    print(
        f"Collection count now: {final_count}"
    )

    if (
        len(existing_ids) + indexed_now
        == len(ids)
    ):
        mark_document_indexed(
            config.document_id
        )

    return indexed_now


def main() -> None:
    print(
        f"Building Gemini vector index: "
        f"{GEMINI_COLLECTION_NAME}"
    )

    embedding_service = EmbeddingService(
    )

    vector_store = VectorStore(
        persist_directory=CHROMA_PATH,
        collection_name=GEMINI_COLLECTION_NAME,
    )

    for config in documents:
        index_document(
            embedding_service=embedding_service,
            vector_store=vector_store,
            config=config,
        )

    print(
        "\nFINAL GEMINI CHROMA COUNT:",
        vector_store.count(),
    )


if __name__ == "__main__":
    main()