from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)


def add_metadata(
    chunks: list[dict],
    config: SEBIDocumentConfig,
) -> list[dict]:
    """
    Add canonical document and IPO metadata
    to extracted chunks.
    """

    enriched_chunks = []

    for chunk in chunks:

        enriched_chunks.append(
            {
                "document_id": config.document_id,
                "ipo_id": config.ipo_id,
                "company": config.company_name,
                "document_type": config.document_type,
                "source": config.source,
                "source_url": config.source_url,
                "version": config.version or "",
                "published_at": (
                    config.published_at.isoformat()
                    if config.published_at
                    else ""
                ),
                "acquisition_source": (
                    config.acquisition_source
                    or ""
                ),
                "document_url": (
                    config.document_url
                    or ""
                ),
                "page_number": chunk[
                    "page_number"
                ],
                "section": chunk[
                    "section"
                ],
                "risk_category": (
                    chunk.get("risk_category")
                    or ""
                ),
                "subsection": (
                    chunk.get("subsection")
                    or ""
                ),
                "chunk_index": chunk[
                    "chunk_index"
                ],
                "text": chunk["text"],
            }
        )

    return enriched_chunks