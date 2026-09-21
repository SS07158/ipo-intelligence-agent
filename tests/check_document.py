from ingestion.sebi.document_parser import parse_document

PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"

pages = parse_document(PDF_PATH)

print(f"Total pages: {len(pages)}")

for page in pages[:20]:
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print(f"PAGE: {page['page_number']}")
    print(f"SECTION: {page['section']}")
    print("=" * 80)
    print(page["text"][:500])