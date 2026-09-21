from app.retrieval.hybrid_retriever import (
    HybridRetriever,
)
from app.retrieval.reranker import Reranker


class RerankedRetriever:
    """
    Hybrid retrieval followed by cross-encoder reranking.
    """

    def __init__(
        self,
        hybrid_retriever=None,
        reranker=None,
    ):
        self.hybrid_retriever = (
            hybrid_retriever
            or HybridRetriever()
        )

        self.reranker = (
            reranker
            or Reranker()
        )

    def retrieve(
    self,
    query: str,
    top_k: int = 5,
    candidate_k: int = 20,
    where: dict | None = None,
    ) -> list[dict]:

        candidates = (
            self.hybrid_retriever.retrieve(
                query,
                top_k=candidate_k,
                where=where,
            )
        )

        if not candidates:
            return []

        reranked = self.reranker.rerank(
            query,
            candidates,
            top_k=candidate_k,
        )

        # -------------------------------------------------
        # Rank maps
        # -------------------------------------------------

        hybrid_rank = {
            result["id"]: rank
            for rank, result in enumerate(
                candidates,
                start=1,
            )
        }

        reranker_rank = {
            result["id"]: rank
            for rank, result in enumerate(
                reranked,
                start=1,
            )
        }

        # -------------------------------------------------
        # Reciprocal Rank Fusion
        # -------------------------------------------------

        combined = []

        for result in reranked:

            doc_id = result["id"]

            h_rank = hybrid_rank.get(
                doc_id
            )

            r_rank = reranker_rank.get(
                doc_id
            )

            hybrid_rrf = (
                1 / (60 + h_rank)
                if h_rank is not None
                else 0.0
            )

            reranker_rrf = (
                1 / (60 + r_rank)
                if r_rank is not None
                else 0.0
            )

            updated = dict(result)

            updated["hybrid_rank"] = h_rank
            updated["reranker_rank"] = r_rank

            updated["combined_score"] = (
                hybrid_rrf
                + reranker_rrf
            )

            combined.append(
                updated
            )

        combined.sort(
            key=lambda item: item["combined_score"],
            reverse=True,
        )

        return combined[:top_k]