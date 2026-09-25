from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.retrieval.bm25_store import BM25Store
from app.retrieval.query_expander import expand_query
from app.config import settings


class HybridRetriever:
    """
    Combine dense semantic retrieval with BM25 retrieval.
    """

    def __init__(
        self,
        embedding_service=None,
        vector_store=None,
        bm25_store=None,
    ):
        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.vector_store = (
            vector_store
            or VectorStore()
        )

        self.bm25_store = (
            bm25_store
            or BM25Store()
        )

        self._build_bm25_index()

    def _build_bm25_index(self):
        data = self.vector_store.collection.get(
            include=[
                "documents",
                "metadatas",
            ]
        )

        self.bm25_store.build(
            ids=data["ids"],
            documents=data["documents"],
            metadatas=data["metadatas"],
        )

    def _select_diverse_risk_ids(
        self,
        ranked_ids: list[str],
        candidate_texts: dict[str, str],
        top_k: int,
    ) -> list[str]:
        """
        Select risk documents while maximizing coverage
        across distinct risk themes.

        The candidates are already ordered by RRF score.
        We select at most one document per theme during
        the diversity pass, then fill remaining slots
        using the original ranking.
        """

        risk_themes = {
            "insurance": [
                "insurance coverage",
                "insurance policy",
                "under-insured",
                "uninsured liability",
            ],
            "payment": [
                "third-party payment gateway",
                "third-party payment gateways",
                "payment gateway providers",
                "payment systems",
                "prepaid payment mechanisms",
                "digital wallets",
            ],
            "expansion": [
                "open, expand",
                "open, expand and/or profitably operate",
                "new fitness centers",
                "new fitness centres",
                "construction",
                "leasing",
                "lease terms",
            ],
            "vendor_supply": [
                "vendor",
                "vendors",
                "supplier",
                "suppliers",
                "supply chain",
                "contractors",
            ],
        }

        selected = []
        covered_themes = set()

        # ---------------------------------------------
        # Pass 1: one document for each new theme
        # ---------------------------------------------

        for doc_id in ranked_ids:

            text = candidate_texts.get(
                doc_id,
                "",
            ).lower()

            matched_themes = {
                theme
                for theme, terms in risk_themes.items()
                if any(
                    term in text
                    for term in terms
                )
            }

            new_themes = (
                matched_themes - covered_themes
            )

            if not new_themes:
                continue

            # Prefer this document when it introduces
            # the largest number of previously uncovered
            # themes.
            selected.append(doc_id)

            covered_themes.update(
                matched_themes
            )

            if len(selected) >= top_k:
                return selected

        # ---------------------------------------------
        # Pass 2: fill remaining slots using RRF
        # ---------------------------------------------

        for doc_id in ranked_ids:

            if doc_id in selected:
                continue

            selected.append(doc_id)

            if len(selected) >= top_k:
                break

        return selected
        
    def _resolve_risk_section(
    self,
    ipo_id: str | None,
    query: str,
    ) -> str | None:
        """
        Resolve the risk section dynamically from the
        sections actually present for the selected IPO.
        """

        if ipo_id is None:
            return None

        data = self.vector_store.collection.get(
            where={"ipo_id": ipo_id},
            include=["metadatas"],
        )

        sections = {
            (metadata.get("section") or "").strip()
            for metadata in data.get("metadatas", [])
            if metadata.get("section")
        }

        risk_sections = [
            section
            for section in sections
            if "risk" in section.lower()
        ]

        if not risk_sections:
            return None

        normalized_query = query.lower()

        # Prefer an explicitly requested internal-risk section.
        if "internal" in normalized_query:
            internal_sections = [
                section
                for section in risk_sections
                if "internal" in section.lower()
            ]

            if internal_sections:
                return internal_sections[0]

        # If there is only one risk section, use it.
        if len(risk_sections) == 1:
            return risk_sections[0]

        # Otherwise prefer a conventional "risk factors" section.
        risk_factor_sections = [
            section
            for section in risk_sections
            if "risk factors" in section.lower()
        ]

        if risk_factor_sections:
            return risk_factor_sections[0]

        return risk_sections[0]

    def _resolve_risk_category(
        self,
        ipo_id: str | None,
        section: str | None,
        query: str,
    ) -> str | None:
        """
        Resolve the internal/external risk category
        dynamically from metadata.
        """

        if ipo_id is None or section is None:
            return None

        data = self.vector_store.collection.get(
            where={
                "ipo_id": ipo_id,
            },
            include=["metadatas"],
        )

        categories = {
            (metadata.get("risk_category") or "").strip()
            for metadata in data.get(
                "metadatas",
                [],
            )
            if (
                metadata.get("section") == section
                and metadata.get("risk_category")
            )
        }

        normalized_query = query.lower()

        if "internal" in normalized_query:
            for category in categories:
                if "internal" in category.lower():
                    return category

        if "external" in normalized_query:
            for category in categories:
                if "external" in category.lower():
                    return category

        return None

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        where: dict | None = None
    ) -> list[dict]:

        candidate_k = max(top_k * 4, 20)

        if settings.query_expansion_enabled:
            expanded_query = expand_query(query)
        else:
            expanded_query = query

        normalized_query = query.lower()

        is_broad_risk_query = (
            "risk" in normalized_query
            and any(
                phrase in normalized_query
                for phrase in [
                    "major risks",
                    "major internal risks",
                    "risks mentioned",
                    "key risks",
                    "main risks",
                    "section II: risk factors",
                ]
            )
        )

        retrieval_section = None

        retrieval_ipo_id = None

        retrieval_risk_category = None

        if where is not None:
            where_section = where.get(
                "section"
            )

            if where_section is not None:
                retrieval_section = (
                    where_section
                )

            where_risk_category = where.get(
                "risk_category"
            )

            if where_risk_category is not None:
                retrieval_risk_category = (
                    where_risk_category
                )

            # if where_subsection is not None:
            #     retrieval_subsection = (
            #         where_subsection
            #     )

            retrieval_ipo_id = where.get(
                "ipo_id"
            )

        if (
            is_broad_risk_query
            and retrieval_section is None
        ):
            retrieval_section = self._resolve_risk_section(
                ipo_id=retrieval_ipo_id,
                query=query,
            )

        if (
            is_broad_risk_query
            and retrieval_risk_category is None
            and retrieval_section is not None
        ):
            retrieval_risk_category = (
                self._resolve_risk_category(
                    ipo_id=retrieval_ipo_id,
                    section=retrieval_section,
                    query=query,
                )
    )

        if (
            is_broad_risk_query
            and retrieval_section is None
            and "internal" in normalized_query
        ):
            retrieval_risk_category = (
                self._resolve_risk_category(
                    ipo_id=retrieval_ipo_id,
                    section=retrieval_section,
                    query=query,
                )
            )



        if is_broad_risk_query:
            candidate_k = max(
                top_k * 8,
                40,
            )

        dense_filters = []

        if retrieval_section is not None:
            dense_filters.append(
                {
                    "section": retrieval_section
                }
            )

        if retrieval_ipo_id is not None:
            dense_filters.append(
                {
                    "ipo_id": retrieval_ipo_id
                }
            )

        if retrieval_risk_category is not None:
            dense_filters.append(
                {
                    "risk_category": retrieval_risk_category
                }
            )

        if len(dense_filters) == 1:
            dense_where = dense_filters[0]

        elif len(dense_filters) > 1:
            dense_where = {
                "$and": dense_filters
            }

        else:
            dense_where = None

        dense_results = self.vector_store.query(
            query_embedding=(
                self.embedding_service.embed_query(
                    expanded_query
                )
            ),
            top_k=candidate_k,
            where=(
                dense_where
                if dense_where
                else None
            ),
        )

        dense_ids = dense_results["ids"][0]

        dense_rank = {
            doc_id: rank
            for rank, doc_id in enumerate(
                dense_ids,
                start=1,
            )
        }

        bm25_results = self.bm25_store.search(
            expanded_query,
            top_k=candidate_k,
            section=retrieval_section,
            ipo_id=retrieval_ipo_id,
            risk_category=retrieval_risk_category,
        )

        bm25_rank = {
            result["id"]: rank
            for rank, result in enumerate(
                bm25_results,
                start=1,
            )
        }

        all_ids = set(
            dense_rank
        ) | set(
            bm25_rank
        )

        # Reciprocal Rank Fusion
        fusion_scores = {}

        for doc_id in all_ids:
            dense_score = (
                1 / (60 + dense_rank[doc_id])
                if doc_id in dense_rank
                else 0.0
            )

            bm25_score = (
                1 / (60 + bm25_rank[doc_id])
                if doc_id in bm25_rank
                else 0.0
            )

            fusion_scores[doc_id] = (
                dense_score + bm25_score
            )

        ranked_ids = sorted(
            fusion_scores,
            key=fusion_scores.get,
            reverse=True,
        )

        dense_documents = (
            dense_results["documents"][0]
        )

        dense_metadatas = (
            dense_results["metadatas"][0]
        )

        dense_distances = (
            dense_results.get("distances", [[]])[0]
        )

        dense_lookup = {
            doc_id: index
            for index, doc_id in enumerate(
                dense_ids
            )
        }

        bm25_lookup = {
            result["id"]: result
            for result in bm25_results
        }

        candidate_texts = {}

        for doc_id in ranked_ids:

            if doc_id in dense_lookup:
                index = dense_lookup[doc_id]

                candidate_texts[doc_id] = (
                    dense_documents[index]
                )

            elif doc_id in bm25_lookup:
                candidate_texts[doc_id] = (
                    bm25_lookup[doc_id]["text"]
                )

        
        ranked_ids = ranked_ids[:top_k]

        results = []

        for doc_id in ranked_ids:

            if doc_id in dense_lookup:
                index = dense_lookup[doc_id]

                results.append(
                    {
                        "id": doc_id,
                        "text": dense_documents[index],
                        "metadata": dense_metadatas[index],
                        "citation": {
                            "company": dense_metadatas[index].get(
                                "company"
                            ),
                            "document_id": dense_metadatas[index].get(
                                "document_id"
                            ),
                            "document_type": dense_metadatas[index].get(
                                "document_type"
                            ),
                            "source": dense_metadatas[index].get(
                                "source"
                            ),
                            "page_number": dense_metadatas[index].get(
                                "page_number"
                            ),
                            "section": dense_metadatas[index].get(
                                "section"
                            ),
                        },
                        "fusion_score": fusion_scores[doc_id],
                        "dense_distance": (
                            dense_distances[index]
                            if index < len(dense_distances)
                            else None
                        ),
                    }
                )

            else:
                result = bm25_lookup[doc_id]

                results.append(
                    {
                        "id": doc_id,
                        "text": result["text"],
                        "metadata": result["metadata"],
                        "citation": {
                            "company": result["metadata"].get(
                                "company"
                            ),
                            "document_id": result["metadata"].get(
                                "document_id"
                            ),
                            "document_type": result["metadata"].get(
                                "document_type"
                            ),
                            "source": result["metadata"].get(
                                "source"
                            ),
                            "page_number": result["metadata"].get(
                                "page_number"
                            ),
                            "section": result["metadata"].get(
                                "section"
                            ),
                        },
                        "fusion_score": fusion_scores[doc_id],
                        "dense_distance": None,
                    }
                )

        return results