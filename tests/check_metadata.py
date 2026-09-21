from ingestion.sebi.document_parser import parse_document
from ingestion.sebi.chunk_builder import build_chunks
from ingestion.sebi.metadata import add_metadata


PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"


pages = parse_document(PDF_PATH)

chunks = build_chunks(pages)

enriched_chunks = add_metadata(chunks)

print(f"Pages: {len(pages)}")
print(f"Chunks: {len(chunks)}")
print(f"Enriched chunks: {len(enriched_chunks)}")

for chunk in enriched_chunks[:3]:
    print("\n" + "=" * 80)
    print(chunk)