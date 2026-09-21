from ingestion.sebi.document_parser import parse_document


PDF_PATH = "data/raw/sebi/cultfit/cultfit_drhp.pdf"


def main():
    pages = parse_document(PDF_PATH)

    sections = {}

    for page in pages:
        section = page["section"]

        if section not in sections:
            sections[section] = []

        sections[section].append(
            page["page_number"]
        )

    print("DOCUMENT SECTIONS")
    print("=" * 80)

    for section, pages in sections.items():
        print(
            f"{section} | "
            f"pages {min(pages)}-{max(pages)}"
        )


if __name__ == "__main__":
    main()