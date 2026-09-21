from pathlib import Path

from ingestion.sebi.pdf_extractor import extract_pages
from ingestion.sebi.section_detector import is_heading
from ingestion.sebi.major_sections import MAJOR_SECTIONS


def parse_document(pdf_path: str | Path) -> list[dict]:
    """
    Convert a PDF into page-level records with
    major-section and subsection information.
    """

    pages = extract_pages(pdf_path)

    parsed_pages = []

    current_section = "UNKNOWN"
    current_risk_category = None
    current_subsection = None

    for page in pages:
        page_number = page["page_number"]
        text = page["text"]

        lines = text.splitlines()
        content_lines = []

        for line in lines:
            stripped_line = line.strip()

            if not stripped_line:
                continue

            if is_heading(stripped_line):

                normalized_heading = (
                    " ".join(stripped_line.split())
                )

                if normalized_heading in MAJOR_SECTIONS:
                    current_section = normalized_heading
                    current_risk_category = None
                    current_subsection = None

                elif (
                    current_section == "SECTION II: RISK FACTORS"
                    and normalized_heading
                    in {
                        "INTERNAL RISK FACTORS",
                        "EXTERNAL RISK FACTORS",
                    }
                ):
                    current_risk_category = normalized_heading
                    current_subsection = None

                else:
                    current_subsection = normalized_heading

            else:
                content_lines.append(stripped_line)

        parsed_pages.append(
            {
                "page_number": page_number,
                "section": current_section,
                "risk_category": current_risk_category,
                "subsection": current_subsection,
                "text": "\n".join(content_lines),
            }
        )

    return parsed_pages