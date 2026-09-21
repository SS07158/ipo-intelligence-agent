from app.retrieval.evidence import format_evidence


def test_format_evidence():
    result = {
        "id": "chunk-1",
        "text": "Example risk.",
        "distance": 0.15,
        "metadata": {
            "company": "CULT.FIT LIMITED",
            "document_id": "cultfit-drhp-2026",
            "document_type": "DRHP",
            "source": "SEBI",
            "page_number": 142,
            "section": "INTERNAL RISK",
        },
    }

    evidence = format_evidence(result)

    assert evidence["id"] == "chunk-1"
    assert evidence["text"] == "Example risk."
    assert evidence["citation"]["company"] == "CULT.FIT LIMITED"
    assert evidence["citation"]["page_number"] == 142
    assert evidence["citation"]["section"] == "INTERNAL RISK"