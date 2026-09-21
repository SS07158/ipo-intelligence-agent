from dataclasses import dataclass
from datetime import datetime


@dataclass
class SEBIDocumentConfig:
    """
    Configuration required to ingest a SEBI IPO document.
    """

    ipo_id: str

    document_id: str

    company_name: str

    document_type: str

    source: str

    source_url: str

    local_path: str

    version: str | None = None

    published_at: datetime | None = None

    acquisition_source: str | None = None

    document_url: str | None = None