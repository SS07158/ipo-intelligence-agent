from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    """
    Standard provenance information for a factual result.
    """

    company: str

    document_id: str | None = None

    document_type: str | None = None

    source: str | None = None

    page_number: int | None = None

    section: str | None = None

    source_url: str | None = None


class ProvenancedValue(BaseModel):
    """
    A factual value together with its source.
    """

    value: object

    citation: SourceCitation

def format_citation(
    citation: dict,
) -> str:
    """
    Convert provenance metadata into a readable citation
    with a navigable source link when available.
    """

    company = citation.get(
        "company",
        "Unknown company",
    )

    document_type = citation.get(
        "document_type"
    )

    source = citation.get(
        "source"
    )

    page_number = citation.get(
        "page_number"
    )

    section = citation.get(
        "section"
    )

    source_url = citation.get(
        "source_url"
    )

    parts = [company]

    if document_type:
        parts.append(
            document_type
        )

    if source:
        parts.append(
            source
        )

    text = " — ".join(parts)

    if page_number is not None:
        text += (
            f", p. {page_number}"
        )

    if section:
        text += (
            f", {section}"
        )

    if source_url:
        text += (
            f" — [Open document]"
            f"({source_url})"
        )

    return text


class AnswerCitation(BaseModel):
    """
    Citation attached to a final factual claim.
    """

    claim: str

    citation: SourceCitation


class FinalAnswer(BaseModel):
    """
    Final answer plus its supporting citations.
    """

    answer: str

    citations: list[AnswerCitation] = Field(
        default_factory=list
    )


def render_answer(
    final_answer: FinalAnswer,
) -> str:
    """
    Render final answer with grouped human-readable citations.
    """

    lines = [
        final_answer.answer
    ]

    if not final_answer.citations:
        return "\n".join(lines)

    lines.append(
        "\nSources:"
    )

    grouped = {}

    for item in final_answer.citations:

        citation = item.citation.model_dump()

        company = citation.get(
            "company",
            "Unknown company",
        )

        document_type = citation.get(
            "document_type"
        )

        source = citation.get(
            "source"
        )

        source_url = citation.get(
            "source_url"
        )

        document_id = citation.get(
            "document_id"
        )

        page_number = citation.get(
            "page_number"
        )

        section = citation.get(
            "section"
        )

        key = (
            company,
            document_id,
            document_type,
            source,
            source_url,
        )

        if key not in grouped:
            grouped[key] = {
                "company": company,
                "document_type": document_type,
                "source": source,
                "source_url": source_url,
                "pages": set(),
                "sections": set(),
            }

        if page_number is not None:
            grouped[key]["pages"].add(
                page_number
            )

        if section:
            grouped[key]["sections"].add(
                section
            )

    for data in grouped.values():

        parts = [
            data["company"]
        ]

        if data["document_type"]:
            parts.append(
                data["document_type"]
            )

        if data["source"]:
            parts.append(
                data["source"]
            )

        lines.append(
            "- " + " — ".join(parts)
        )

        if data["pages"]:
            pages = sorted(
                data["pages"]
            )

            page_text = ", ".join(
                str(page)
                for page in pages
            )

            lines.append(
                f"  Pages: {page_text}"
            )

        if data["sections"]:
            sections = sorted(
                data["sections"]
            )

            section_text = ", ".join(
                sections
            )

            lines.append(
                f"  Sections: {section_text}"
            )

        if data["source_url"]:
            lines.append(
                f"  [Open document]({data['source_url']})"
            )

    return "\n".join(lines)