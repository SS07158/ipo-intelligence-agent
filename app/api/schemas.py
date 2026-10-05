from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    company_name: str | None = None
    ipo_id: str | None = None


class Source(BaseModel):
    company: str | None = None
    document_type: str | None = None
    source: str | None = None
    page_number: int | None = None
    section: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []

class AdminIPORequest(BaseModel):

    ipo_id: str

    company_name: str

    document_id: str

    document_type: str = "DRHP"

    version: str | None = None

    published_at: str | None = None


class AdminIPOResponse(BaseModel):

    success: bool

    ipo_id: str | None = None

    document_id: str | None = None

    company_name: str

    document_type: str

    message: str | None = None

    source: str | None = None

    indexed_chunks: int | None = None

class IPOListItem(BaseModel):
    ipo_id: str
    company_name: str
