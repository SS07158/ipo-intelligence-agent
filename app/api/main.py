from fastapi import FastAPI, HTTPException, Header, Depends,BackgroundTasks
import secrets
from functools import lru_cache
from threading import Lock
from uuid import uuid4
import re
import time
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

# Temporary in-memory store for ingestion job status.
# This is suitable for local testing with a single API process.
_ipo_ingestion_jobs: dict[str, dict] = {}
_ipo_ingestion_jobs_lock = Lock()


def _update_ipo_ingestion_job(
    job_id: str,
    **updates,
) -> None:
    with _ipo_ingestion_jobs_lock:
        if job_id in _ipo_ingestion_jobs:
            _ipo_ingestion_jobs[job_id].update(updates)


def _run_ipo_ingestion_job(
    job_id: str,
    request: AdminIPORequest,
) -> None:
    _update_ipo_ingestion_job(
        job_id,
        status="processing",
        message="Discovering and indexing the IPO document.",
    )

    try:
        ingestion_service = get_ipo_ingestion_service()

        result = ingestion_service.add_ipo(
            ipo_id=request.ipo_id,
            company_name=request.company_name,
            document_id=request.document_id,
            document_type=request.document_type,
            version=request.version,
            published_at=request.published_at,
        )

        if not result.get("success"):
            _update_ipo_ingestion_job(
                job_id,
                status="failed",
                success=False,
                message=result.get(
                    "message",
                    "IPO ingestion failed.",
                ),
            )
            return

        _update_ipo_ingestion_job(
            job_id,
            status="completed",
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
            indexed_chunks=result.get("indexed_chunks"),
        )

    except Exception as exc:
        _update_ipo_ingestion_job(
            job_id,
            status="failed",
            success=False,
            message=f"Ingestion failed: {exc}",
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

    selected_company = company_name.strip()

    if (
        selected_company
        and selected_company.lower() not in question.lower()
    ):
        question = (
            f"Regarding {selected_company}: "
            f"{question}"
        )

    chat_started = time.perf_counter()

    print(
        f"[CHAT PERF] Started for IPO: {request.ipo_id}"
    )

    agent_started = time.perf_counter()

    agent = LangGraphIPOAgent(
        default_company=company_name,
        default_ipo_id=request.ipo_id,
    )

    print(
        "[CHAT PERF] Agent initialization: "
        f"{time.perf_counter() - agent_started:.2f}s"
    )

    run_started = time.perf_counter()

    result = agent.run(question)

    print(
        "[CHAT PERF] Agent execution: "
        f"{time.perf_counter() - run_started:.2f}s"
    )

    print(
        "[CHAT PERF] Total elapsed: "
        f"{time.perf_counter() - chat_started:.2f}s"
    )

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
    
@app.post("/admin/ipos", status_code=202)
def add_ipo(
    request: AdminIPORequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_admin_key),
):
    job_id = str(uuid4())

    job = {
        "job_id": job_id,
        "status": "queued",
        "success": False,
        "ipo_id": request.ipo_id,
        "document_id": request.document_id,
        "company_name": request.company_name,
        "document_type": request.document_type,
        "message": "IPO ingestion has been queued.",
        "source": None,
        "indexed_chunks": None,
    }

    with _ipo_ingestion_jobs_lock:
        _ipo_ingestion_jobs[job_id] = job

    background_tasks.add_task(
        _run_ipo_ingestion_job,
        job_id,
        request,
    )

    return dict(job)

@app.get("/admin/ipos/jobs/{job_id}")
def get_ipo_ingestion_job_status(
    job_id: str,
    _: None = Depends(verify_admin_key),
):
    with _ipo_ingestion_jobs_lock:
        job = _ipo_ingestion_jobs.get(job_id)

        if job is not None:
            job = dict(job)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Ingestion job not found.",
        )

    return job