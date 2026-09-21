class FakeEmbeddingService:
    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [
            [1.0, 0.0]
            for _ in texts
        ]


class FakeVectorStore:
    def __init__(self):
        self.ids = []
        self.documents = []
        self.embeddings = []
        self.metadatas = []

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas,
    ):
        self.ids.extend(ids)
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)
        self.metadatas.extend(metadatas)

    def count(self):
        return len(self.ids)


def test_document_indexer():
    from app.retrieval.document_indexer import (
        DocumentIndexer,
    )

    indexer = DocumentIndexer(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
    )

    count = indexer.index_document(
        "data/raw/sebi/cultfit/cultfit_drhp.pdf"
    )

    assert count > 0

from unittest.mock import MagicMock, patch

from app.retrieval.document_indexer import (
    DocumentIndexer,
)

from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)


def test_document_indexer_passes_config_metadata():
    config = SEBIDocumentConfig(
        ipo_id="cultfit-2026",
        document_id="test-drhp-2026",
        company_name="TEST LIMITED",
        document_type="DRHP",
        source="SEBI",
        source_url=(
            "https://example.com/drhp"
        ),
        local_path=(
            "data/test/drhp.pdf"
        ),
    )

    mock_embedding_service = (
        MagicMock()
    )

    mock_vector_store = MagicMock()

    mock_embedding_service.embed_documents.return_value = [
        [0.1, 0.2],
    ]

    with patch(
        "app.retrieval.document_indexer.parse_document"
    ) as mock_parse, patch(
        "app.retrieval.document_indexer.build_chunks"
    ) as mock_build, patch(
        "app.retrieval.document_indexer.add_metadata"
    ) as mock_metadata:

        mock_parse.return_value = [
            {"page": 1}
        ]

        mock_build.return_value = [
            {
                "text": "Example text",
            }
        ]

        mock_metadata.return_value = [
            {
                "text": "Example text",
                "document_id": "old-id",
                "ipo_id": "old-ipo",
                "company": "OLD COMPANY",
                "document_type": "DRHP",
                "source": "OLD SOURCE",
                "page_number": 1,
                "section": "INTERNAL RISKS",
                "subsection": "",
                "chunk_index": 0,
            }
        ]

        indexer = DocumentIndexer(
            embedding_service=(
                mock_embedding_service
            ),
            vector_store=(
                mock_vector_store
            ),
        )

        count = indexer.index_document(
            config.local_path,
            config=config,
        )

        assert count == 1

        kwargs = (
            mock_vector_store
            .add_documents.call_args.kwargs
        )

        metadata = kwargs[
            "metadatas"
        ][0]

        assert (
            metadata["document_id"]
            == "test-drhp-2026"
        )

        assert (
            metadata["company"]
            == "TEST LIMITED"
        )

        assert (
            metadata["document_type"]
            == "DRHP"
        )

        assert (
            metadata["source"]
            == "SEBI"
        )

        assert (
            metadata["source_url"]
            == "https://example.com/drhp"
        )

        assert (
            metadata["section"]
            == "INTERNAL RISKS"
        )