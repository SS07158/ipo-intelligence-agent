from ingestion.sebi.pdf_extractor import extract_pages


PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"


pages = extract_pages(PDF_PATH)

print(f"Total pages: {len(pages)}")

for page in pages:
    text = page["text"]

    if text:
        print("\n" + "=" * 80)
        print(f"PAGE {page['page_number']}")
        print("=" * 80)
        print(text[:500])