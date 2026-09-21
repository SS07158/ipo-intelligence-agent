from ingestion.sebi.document_parser import parse_document
from ingestion.sebi.chunk_builder import build_chunks


PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"


pages = parse_document(PDF_PATH)

chunks = build_chunks(pages)

print(f"Pages: {len(pages)}")
print(f"Chunks: {len(chunks)}")

for chunk in chunks[:5]:
    print("\n" + "=" * 80)
    print(f"CHUNK: {chunk['chunk_index']}")
    print(f"PAGE: {chunk['page_number']}")
    print(f"SECTION: {chunk['section']}")
    print("=" * 80)
    print(chunk["text"][:500])