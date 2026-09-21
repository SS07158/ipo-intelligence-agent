from collections import Counter

from app.retrieval.vector_store import VectorStore
from ingestion.sebi.document_parser import parse_document


IPO_ID = "sterlite-electric-2026"

PDF_PATH = (
    r"data\raw\nse\sterlite_electric_limited"
    r"\sbhatnagar_01102025164001_Sterlite_Electric_Limited_DRHP.pdf"
)


def main():
    print("Parsing Sterlite document...")
    parsed_pages = parse_document(PDF_PATH)

    page_metadata = {}

    for page in parsed_pages:
        page_number = int(page["page_number"])

        page_metadata[page_number] = {
            "section": page.get("section") or "UNKNOWN",
            "risk_category": page.get("risk_category") or "",
            "subsection": page.get("subsection") or "",
        }

    print(f"Parsed {len(page_metadata)} pages.")

    vector_store = VectorStore()
    collection = vector_store.collection

    print("Loading Sterlite chunks from Chroma...")

    data = collection.get(
        where={"ipo_id": IPO_ID},
        include=["metadatas"],
    )

    ids = data["ids"]
    metadatas = data["metadatas"]

    print(f"Found {len(ids)} Sterlite chunks.")

    if not ids:
        raise RuntimeError(
            f"No Chroma records found for ipo_id={IPO_ID}"
        )

    updated_metadatas = []
    missing_pages = []

    for chunk_id, metadata in zip(ids, metadatas):
        page_number = int(metadata["page_number"])

        if page_number not in page_metadata:
            missing_pages.append(
                (chunk_id, page_number)
            )
            updated_metadatas.append(metadata)
            continue

        updated_metadata = {
            **metadata,
            "section": page_metadata[page_number]["section"],
            "risk_category": page_metadata[page_number]["risk_category"],
            "subsection": page_metadata[page_number]["subsection"],
        }

        updated_metadatas.append(updated_metadata)

    print("Updating metadata...")

    collection.update(
        ids=ids,
        metadatas=updated_metadatas,
    )

    print("Metadata update complete.")

    if missing_pages:
        print(
            f"WARNING: {len(missing_pages)} chunks had "
            "page numbers missing from parsed document."
        )

    # -----------------------------------------
    # Verification
    # -----------------------------------------

    verify = collection.get(
        where={"ipo_id": IPO_ID},
        include=["metadatas"],
    )

    section_counts = Counter(
        metadata.get("section", "UNKNOWN")
        for metadata in verify["metadatas"]
    )

    print("\nSECTION COUNTS:")
    for section, count in section_counts.most_common():
        print(f"{count:4} | {section}")

    print("\nRISK SECTION SAMPLE:")

    for chunk_id, metadata in zip(
        verify["ids"],
        verify["metadatas"],
    ):
        if metadata.get("section") == "SECTION II: RISK FACTORS":
            print(
                chunk_id,
                "| page=",
                metadata.get("page_number"),
                "| risk_category=",
                metadata.get("risk_category"),
                "| subsection=",
                metadata.get("subsection"),
            )

            break


if __name__ == "__main__":
    main()