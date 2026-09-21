from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    company_name: str | None = None


class Source(BaseModel):
    company: str | None = None
    document_type: str | None = None
    source: str | None = None
    page_number: int | None = None
    section: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []