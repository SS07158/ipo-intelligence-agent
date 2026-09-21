from dataclasses import dataclass


@dataclass
class ResolvedDocument:
    """
    Canonical resolved IPO document.

    source_url:
        Filing/source page.

    document_url:
        Actual document/archive URL.
    """

    company_name: str

    document_type: str

    document_url: str

    source: str

    source_url: str | None = None

    document_date: str | None = None

    archive_type: str = "direct"

    