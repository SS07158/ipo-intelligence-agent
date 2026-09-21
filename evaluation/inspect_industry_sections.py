from ingestion.sebi.document_parser import parse_document


PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"


def main():
    pages = parse_document(PDF_PATH)

    for page in pages:
        if 219 <= page["page_number"] <= 247:
            print(
                f"Page {page['page_number']} | "
                f"Section: {page['section']} | "
                f"Subsection: {page.get('subsection')}"
            )


if __name__ == "__main__":
    main()