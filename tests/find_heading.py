from ingestion.sebi.pdf_extractor import extract_pages
from ingestion.sebi.section_detector import is_heading


PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"


pages = extract_pages(PDF_PATH)

for page in pages:
    lines = page["text"].splitlines()

    for line in lines:
        if is_heading(line):
            print(
                f"Page {page['page_number']:>4} | {line.strip()}"
            )