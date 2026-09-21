def format_evidence(result: dict) -> dict:
    """
    Convert a raw retrieval result into a citation-ready
    evidence record.
    """

    metadata = result["metadata"]

    return {
        "id": result["id"],
        "text": result["text"],
        "metadata": metadata,
        "citation": {
            "company": metadata.get("company"),
            "document_id": metadata.get("document_id"),
            "document_type": metadata.get("document_type"),
            "source": metadata.get("source"),
            "page_number": metadata.get("page_number"),
            "section": metadata.get("section"),
        },
        "retrieval_distance": result.get("distance"),
    }

def citation_text(evidence: dict) -> str:
    """
    Create a human-readable citation string.
    """

    citation = evidence["citation"]

    parts = [
        citation.get("company"),
        citation.get("document_type"),
        citation.get("section"),
    ]

    page = citation.get("page_number")

    if page is not None:
        parts.append(f"Page {page}")

    parts = [
        str(part)
        for part in parts
        if part
    ]

    return " — ".join(parts)