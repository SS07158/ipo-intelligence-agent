from fastapi import FastAPI

from functools import lru_cache
import re

from app.agents.langgraph_agent import LangGraphIPOAgent
from app.api.schemas import ChatRequest, ChatResponse

from app.retrieval.vector_store import VectorStore

app = FastAPI(
    title="Indian IPO Intelligence API",
    description="Backend API for the Indian IPO Intelligence Agent",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ipo-intelligence-api",
    }

@lru_cache
def get_agent() -> LangGraphIPOAgent:
    return LangGraphIPOAgent()

def _extract_sources(result: dict) -> list[dict]:
    sources = []
    seen = set()

    answer = result.get(
        "answer",
        "",
    )

    # Extract internal chunk IDs from the
    # agent's grounded answer.
    chunk_ids = re.findall(
        r"[A-Za-z0-9._-]+-chunk-\d+",
        answer,
    )

    if chunk_ids:
        vector_store = VectorStore()

        data = vector_store.collection.get(
            ids=list(dict.fromkeys(chunk_ids)),
            include=["metadatas"],
        )

        for metadata in data.get(
            "metadatas",
            [],
        ):
            source = {
                "company": metadata.get("company"),
                "document_type": metadata.get(
                    "document_type"
                ),
                "source": metadata.get("source"),
                "page_number": metadata.get(
                    "page_number"
                ),
                "section": metadata.get("section"),
            }

            key = (
                source["company"],
                source["document_type"],
                source["source"],
                source["page_number"],
                source["section"],
            )

            if key not in seen:
                seen.add(key)
                sources.append(source)

    # Also collect structured financial citations.
    for tool_result in result.get(
        "tool_results",
        [],
    ):
        tool_output = tool_result.get(
            "result",
            {},
        )

        if not isinstance(
            tool_output,
            dict,
        ):
            continue

        for metric in tool_output.get(
            "metrics",
            [],
        ):
            citation = metric.get(
                "citation"
            )

            if not citation:
                continue

            source = {
                "company": citation.get(
                    "company"
                ),
                "document_type": citation.get(
                    "document_type"
                ),
                "source": citation.get(
                    "source"
                ),
                "page_number": citation.get(
                    "page_number"
                ),
                "section": citation.get(
                    "section"
                ),
            }

            key = (
                source["company"],
                source["document_type"],
                source["source"],
                source["page_number"],
                source["section"],
            )

            if key not in seen:
                seen.add(key)
                sources.append(source)

    return sources


@app.post(
    "/api/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):
    question = request.question.strip()

    if request.company_name:
        company = request.company_name.strip()

        if (
            company
            and company.lower()
            not in question.lower()
        ):
            question = (
                f"Regarding {company}: "
                f"{question}"
            )

    result = get_agent().run(question)

    answer = result.get(
        "answer",
        "No answer returned.",
    )

    sources = _extract_sources(
        result
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
    )