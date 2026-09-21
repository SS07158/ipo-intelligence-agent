from app.retrieval.document_indexer import (
    DocumentIndexer,
)

from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from ingestion.sebi.register_document import (
    is_document_indexed,
    mark_document_indexed,
    register_document,
)
from database.ipo_repository import (
    create_document,
)


def ingest_document(
    config: SEBIDocumentConfig,
) -> int:
    """
    Register and index a SEBI IPO document.

    Repeated ingestion of the same document is safe.
    """
    
    register_document(
        config
    )

    if is_document_indexed(
        config.document_id
    ):
        print(
            f"Document already indexed: "
            f"{config.document_id}"
        )

        return 0

    indexer = DocumentIndexer()

    count = indexer.index_document(
        config.local_path,
        config=config,
    )

    mark_document_indexed(
        config.document_id
    )

    print(
        f"Indexed {count} chunks "
        f"for {config.company_name}."
    )

    return count