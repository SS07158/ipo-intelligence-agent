from app.tools.rag_tools import search_ipo_documents


result = search_ipo_documents(
    question="What risks could affect CULT.FIT's revenue growth?",
    section="risk_factors",
    top_k=5,
)

print(result)