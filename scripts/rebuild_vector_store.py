from pathlib import Path

import chromadb

from app.retrieval.document_indexer import DocumentIndexer
from app.retrieval.vector_store import VectorStore
from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)
from ingestion.sebi.register_document import (
    mark_document_indexed,
)


CHROMA_PATH = Path(
    "data/chroma"
)

COLLECTION_NAME = (
    "ipo_documents"
)


def reset_collection() -> None:
    """
    Delete the current vector collection.

    This removes only vector-store records.
    SQL records and source PDFs are untouched.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )
        print(
            f"Deleted Chroma collection: "
            f"{COLLECTION_NAME}"
        )

    except Exception as exc:
        print(
            f"Collection reset skipped: {exc}"
        )


def main() -> None:

    reset_collection()

    vector_store = VectorStore(
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME,
    )

    indexer = DocumentIndexer(
        vector_store=vector_store
    )

    documents = [
        (
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
            "CULT.FIT LIMITED",
        ),
        (
            SEBIDocumentConfig(
                ipo_id="sterlite-electric-2026",
                document_id=(
                    "sterlite-electric-drhp-2026"
                ),
                company_name=(
                    "Sterlite Electric Limited"
                ),
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
            "Sterlite Electric Limited",
        ),
    ]

    for config, company_name in documents:

        print(
            f"\nINDEXING: {company_name}"
        )

        count = indexer.index_document(
            config.local_path,
            config=config,
        )

        print(
            f"Indexed {count} chunks "
            f"for {company_name}."
        )

        if count > 0:
            mark_document_indexed(
                config.document_id
            )

    print(
        "\nFINAL CHROMA COUNT:",
        vector_store.count(),
    )


if __name__ == "__main__":
    main()