from dataclasses import dataclass


@dataclass
class DiscoveredSEBIDocument:
    """
    A document filing discovered from an external source.
    """

    company_name: str

    document_type: str

    detail_url: str

    document_url: str | None = None

    source: str = "SEBI"

    discovered_date: str | None = None