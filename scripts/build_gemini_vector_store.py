from pathlib import Path

from app.retrieval.document_indexer import DocumentIndexer
from app.retrieval.vector_store import VectorStore
from ingestion.sebi.document_config import SEBIDocumentConfig
from ingestion.sebi.register_document import mark_document_indexed


CHROMA_PATH = Path("data/chroma")

GEMINI_COLLECTION_NAME = "ipo_documents_gemini"


def main() -> None:
    print(
        f"Building Gemini vector index: "
        f"{GEMINI_COLLECTION_NAME}"
    )

    vector_store = VectorStore(
        persist_directory=CHROMA_PATH,
        collection_name=GEMINI_COLLECTION_NAME,
    )

    indexer = DocumentIndexer(
        vector_store=vector_store
    )

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

    total_chunks = 0

    for config in documents:
        print(
            f"\nINDEXING: {config.company_name}"
        )

        count = indexer.index_document(
            config.local_path,
            config=config,
        )

        print(
            f"Indexed {count} chunks "
            f"for {config.company_name}."
        )

        if count > 0:
            mark_document_indexed(
                config.document_id
            )

        total_chunks += count

    print(
        "\nGEMINI CHROMA COUNT:",
        vector_store.count(),
    )

    print(
        "TOTAL CHUNKS INDEXED:",
        total_chunks,
    )


if __name__ == "__main__":
    main()