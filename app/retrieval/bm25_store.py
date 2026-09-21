import re

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    """
    Normalize text into lowercase lexical tokens.
    """

    return re.findall(
        r"\b[a-zA-Z0-9₹]+\b",
        text.lower(),
    )


class BM25Store:
    """
    BM25 indexes for both document text and section names.
    """

    def __init__(self):
        self.ids: list[str] = []
        self.documents: list[str] = []
        self.metadatas: list[dict] = []

        self.document_bm25: BM25Okapi | None = None
        self.section_bm25: BM25Okapi | None = None

    def build(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:

        if not (
            len(ids)
            == len(documents)
            == len(metadatas)
        ):
            raise ValueError(
                "ids, documents, and metadatas "
                "must have the same length."
            )

        self.ids = ids
        self.documents = documents
        self.metadatas = metadatas

        document_tokens = [
            tokenize(document)
            for document in documents
        ]

        section_tokens = [
            tokenize(
                metadata.get("section", "")
            )
            for metadata in metadatas
        ]

        self.document_bm25 = BM25Okapi(
            document_tokens
        )

        self.section_bm25 = BM25Okapi(
            section_tokens
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        section: str | None = None,
        ipo_id: str | None = None,
        risk_category: str | None = None,
    ) -> list[dict]:

        if self.document_bm25 is None:
            raise RuntimeError(
                "BM25 index has not been built."
            )

        if self.section_bm25 is None:
            raise RuntimeError(
                "Section BM25 index has not been built."
            )

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        query_tokens = tokenize(query)

        allowed_indices = range(
            len(self.ids)
        )

        if section is not None:
            allowed_indices = [
                index
                for index, metadata in enumerate(
                    self.metadatas
                )
                if metadata.get("section") == section
            ]

        if ipo_id is not None:
            allowed_indices = [
                index
                for index in allowed_indices
                if self.metadatas[index].get(
                    "ipo_id"
                ) == ipo_id
            ]

        if risk_category is not None:
            allowed_indices = [
                index
                for index in allowed_indices
                if self.metadatas[index].get(
                    "risk_category"
                ) == risk_category
            ]

        document_scores = (
            self.document_bm25.get_scores(
                query_tokens
            )
        )

        section_scores = (
            self.section_bm25.get_scores(
                query_tokens
            )
        )

        combined_scores = (
            document_scores
            + (2.0 * section_scores)
        )

        ranked_indices = sorted(
            allowed_indices,
            key=lambda index: combined_scores[index],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:
            results.append(
                {
                    "id": self.ids[index],
                    "text": self.documents[index],
                    "metadata": self.metadatas[index],
                    "score": float(
                        combined_scores[index]
                    ),
                    "document_score": float(
                        document_scores[index]
                    ),
                    "section_score": float(
                        section_scores[index]
                    ),
                }
            )

        return results