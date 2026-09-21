from ingestion.sebi.metadata import add_metadata

def test_add_metadata():
    chunks = [
        {
            "chunk_index": 0,
            "page_number": 10,
            "section": "RISK FACTORS",
            "text": "Example risk text."
        }
    ]

    result = add_metadata(chunks)

    assert len(result) == 1

    chunk = result[0]

    assert chunk["document_id"] == "cultfit-drhp-2026"
    assert chunk["ipo_id"] == "cultfit-2026"
    assert chunk["company"] == "CULT.FIT LIMITED"
    assert chunk["document_type"] == "DRHP"
    assert chunk["source"] == "SEBI"
    assert chunk["page_number"] == 10
    assert chunk["section"] == "RISK FACTORS"