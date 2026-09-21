SYSTEM_PROMPT = """
You are an IPO research assistant.

Answer the user's question using ONLY the provided evidence.

Rules:
1. Do not invent facts.
2. Do not use outside knowledge when answering factual questions.
3. If the evidence is insufficient, clearly say that the evidence is insufficient.
4. Keep facts separate from interpretation.
5. Do not provide buy, sell, or investment recommendations.
6. Cite important factual claims using the evidence identifiers provided.
"""


def build_rag_messages(
    question: str,
    evidence: list[dict],
) -> list[tuple[str, str]]:
    """
    Build grounded LLM messages from retrieved evidence.
    """

    evidence_blocks = []

    for index, item in enumerate(evidence, start=1):
        citation = item["citation"]

        evidence_blocks.append(
            f"""
Evidence {index}
ID: {item["id"]}
Company: {citation.get("company")}
Document: {citation.get("document_type")}
Section: {citation.get("section")}
Page: {citation.get("page_number")}
Source: {citation.get("source")}

Text:
{item["text"]}
"""
        )

    context = "\n".join(evidence_blocks)

    user_message = f"""
Question:
{question}

Retrieved evidence:
{context}

Answer the question using only this evidence.
For factual claims, cite the relevant Evidence ID.
"""

    return [
        ("system", SYSTEM_PROMPT),
        ("human", user_message),
    ]