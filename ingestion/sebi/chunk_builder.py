from ingestion.sebi.chunker import chunk_text


def build_chunks(
    pages: list[dict],
    chunk_size: int = 350,
    overlap: int = 50,
) -> list[dict]:
    """
    Convert section-aware pages into searchable chunks.

    Each chunk preserves:
        - page number
        - section
        - chunk index
        - text
    """

    chunks = []
    chunk_index = 0

    for page in pages:
        text = page["text"].strip()

        if not text:
            continue

        page_chunks = chunk_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in page_chunks:
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "page_number": page["page_number"],
                    "section": page["section"],
                    "risk_category": page.get("risk_category"),
                    "subsection": page.get("subsection"),
                    "text": chunk,
                }
            )

            chunk_index += 1

    return chunks