import requests
import re
import os

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)


def ask_agent(
    question: str,
    company_name: str | None = None,
) -> str:
    # payload = {
    #     "question": question,
    #     "company_name": company_name,
    # }

    question = (
        str(question).strip()
        if question is not None
        else ""
    )

    if not question:
        raise ValueError(
            "Quick Search produced an empty question."
        )

    payload = {
        "question": question,
        "company_name": company_name,
    }

    response = requests.post(
        f"{API_URL}/api/chat",
        json=payload,
        timeout=300,
    )

    if not response.ok:
        try:
            error_detail = response.json().get(
                "detail",
                response.text,
            )
        except Exception:
            error_detail = response.text

        raise RuntimeError(
            f"FastAPI returned {response.status_code}: "
            f"{error_detail}"
        )

        

    data = response.json()

    answer = data.get(
        "answer",
        "No answer returned.",
    )

    answer = re.sub(
        r"\s*\(Evidence ID:\s*[^)]+\)",
        "",
        answer,
    )

    answer = re.sub(
        r"\s*\(Evidence\s+\d+\)",
        "",
        answer,
    )

    return {
        "answer": answer,
        "sources": data.get(
            "sources",
            [],
        ),
    }