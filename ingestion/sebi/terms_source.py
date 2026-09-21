from pathlib import Path

from ingestion.sebi.document_parser import (
    parse_document,
)

from ingestion.sebi.ipo_terms import (
    extract_ipo_terms,
)


class SEBIIPOTermsSource:
    """
    Extract structured IPO terms from a SEBI DRHP.
    """

    def extract(
        self,
        pdf_path: str | Path,
    ) -> dict:
        """
        Parse a DRHP and extract structured IPO terms.
        """

        pages = parse_document(
            pdf_path
        )

        text = "\n".join(
            page["text"]
            for page in pages
            if page.get("text")
        )

        return extract_ipo_terms(
            text
        )