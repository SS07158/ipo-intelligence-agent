from fastapi import FastAPI, HTTPException, Header, Depends
import secrets
from functools import lru_cache
import re

from app.config import settings
from app.agents.langgraph_agent import LangGraphIPOAgent
from app.api.schemas import ChatRequest, ChatResponse, AdminIPORequest, AdminIPOResponse, IPOListItem

from app.retrieval.vector_store import VectorStore

from ingestion.document_resolver import DocumentResolver
from ingestion.ipo_ingestion_service import IPOIngestionService
from ingestion.sebi.sebi_browser import SEBIBrowserDiscovery

from database.database import SessionLocal
from database.ipo_repository import get_all_ipos, get_ipo_by_id

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

@lru_cache
def get_ipo_ingestion_service() -> IPOIngestionService:
    sebi_source = SEBIBrowserDiscovery(
        headless=True
    )

    resolver = DocumentResolver(
        sebi_source=sebi_source
    )

    return IPOIngestionService(
        resolver=resolver
    )

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

    # ------------------------------------------------------------
    # Resolve IPO context
    # ------------------------------------------------------------

    company_name = request.company_name

    if request.ipo_id:

        session = SessionLocal()

        try:
            ipo = get_ipo_by_id(
                session,
                request.ipo_id,
            )

        finally:
            session.close()

        if ipo is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"IPO not found: {request.ipo_id}"
                ),
            )

        company_name = ipo.company_name


    if not company_name:
        raise HTTPException(
            status_code=400,
            detail=(
                "Either ipo_id or company_name "
                "must be provided."
            ),
        )

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

def verify_admin_key(
    x_admin_key: str | None = Header(
        default=None,
        alias="X-Admin-Key",
    ),
):
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=503,
            detail="Admin API key is not configured.",
        )

    if (
        x_admin_key is None
        or not secrets.compare_digest(
            x_admin_key,
            settings.admin_api_key,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing admin API key.",
        )

@app.get(
    "/api/ipos",
    response_model=list[IPOListItem],
)
def list_ipos():
    session = SessionLocal()

    try:
        ipos = get_all_ipos(session)

        return [
            IPOListItem(
                ipo_id=ipo.ipo_id,
                company_name=ipo.company_name,
            )
            for ipo in ipos
        ]

    finally:
        session.close()
    
@app.post(
    "/admin/ipos",
    response_model=AdminIPOResponse,
)
def add_ipo(
    request: AdminIPORequest,
    _: None = Depends(verify_admin_key)
):
    ingestion_service = (
        get_ipo_ingestion_service()
    )

    try:
        result = ingestion_service.add_ipo(
            ipo_id=request.ipo_id,
            company_name=request.company_name,
            document_id=request.document_id,
            document_type=request.document_type,
            version=request.version,
            published_at=request.published_at,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get(
                "message",
                "IPO ingestion failed.",
            ),
        )

    return AdminIPOResponse(
        success=True,
        ipo_id=result.get("ipo_id"),
        document_id=result.get("document_id"),
        company_name=result.get(
            "company_name",
            request.company_name,
        ),
        document_type=result.get(
            "document_type",
            request.document_type,
        ),
        message="IPO added and indexed successfully.",
        source=result.get("source"),
        indexed_chunks=result.get(
            "indexed_chunks"
        ),
    )