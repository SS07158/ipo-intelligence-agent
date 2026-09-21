from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class RawDocument:
    """
    Represents a document discovered from an external source.
    """

    document_id: str

    company_name: str

    document_type: str

    source: str

    source_url: str

    discovered_at: datetime

    content: bytes | None = None

    metadata: dict[str, Any] | None = None


@dataclass
class StructuredIPOData:
    """
    Structured IPO information obtained from an external source.
    """

    ipo_id: str

    company_name: str

    source: str

    discovered_at: datetime

    data: dict[str, Any]