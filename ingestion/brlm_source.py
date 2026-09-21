from ingestion.document_source import (
    ResolvedDocument,
)

from ingestion.official_source import (
    OfficialOfferDocumentSource,
)


class ConfiguredOfficialSource(
    OfficialOfferDocumentSource
):
    """
    Official BRLM/issuer source backed by
    explicitly configured document URLs.

    This avoids uncontrolled web searching.
    """

    def __init__(
        self,
        documents: dict[
            tuple[str, str],
            ResolvedDocument,
        ] | None = None,
    ):
        self.documents = (
            documents or {}
        )

    def find_document(
        self,
        company_name: str,
        document_type: str,
    ) -> ResolvedDocument | None:

        key = (
            company_name.strip().upper(),
            document_type.strip().upper(),
        )

        return self.documents.get(
            key
        )