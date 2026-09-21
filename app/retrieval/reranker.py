from sentence_transformers import CrossEncoder


MODEL_NAME = "BAAI/bge-reranker-v2-m3"


class Reranker:
    """
    Cross-encoder reranker for query-document pairs.
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ):
        self.model = CrossEncoder(
            model_name
        )

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Rerank retrieved candidates using a cross-encoder.
        """

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if not results:
            return []

        pairs = [
            [
                query,
                (
                    f"Section: "
                    f"{result['metadata'].get('section', '')}\n"
                    f"{result['text']}"
                ),
            ]
            for result in results
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = []

        for result, score in zip(
            results,
            scores,
        ):
            updated = dict(result)

            updated["rerank_score"] = float(
                score
            )

            ranked.append(updated)

        ranked.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return ranked[:top_k]