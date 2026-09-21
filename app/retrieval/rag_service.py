from app.prompts.rag_prompt import build_rag_messages
from app.retrieval.llm_service import LLMService
# from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.citation_validator import (
    validate_citations,
)
from app.retrieval.reranked_retriever import (
    RerankedRetriever
)

class RAGService:
    """
    Retrieve evidence and generate a grounded answer.
    """

    def __init__(
        self,
        retriever: RerankedRetriever | None = None,
        llm_service: LLMService | None = None,
    ):
        self.retriever = (
            retriever
            or RerankedRetriever()
        )

        self.llm_service = (
            llm_service
            or LLMService()
        )

    def answer(
        self,
        question: str,
        top_k: int = 5,
        where: dict | None = None,
    ) -> dict:
        """
        Retrieve evidence and generate an answer.
        """

        evidence = self.retriever.retrieve(
            question,
            top_k=top_k,
            candidate_k=max(
                top_k * 8,
                40
            ),
            where=where,
        )

        if not evidence:
            return {
                "answer": (
                    "I could not find sufficient "
                    "evidence in the indexed documents."
                ),
                "evidence": [],
                "citation_validation": {
                    "valid": True,
                    "references": [],
                    "invalid_references": [],
                },
            }

        messages = build_rag_messages(
            question,
            evidence,
        )

        answer = self.llm_service.generate(
            messages
        )

        if not answer or not answer.strip():
            return {
                "answer": "",
                "evidence": evidence,
                "citation_validation": {
                    "valid": True,
                    "references": [],
                    "invalid_references": [],
                },
                "generation_failed": True,
            }

        citation_validation = validate_citations(
            answer,
            evidence
        )

        return {
            "answer": answer,
            "evidence": evidence,
            "citation_validation":citation_validation
        }