from app.agents.router import classify_question
from app.agents.tool_registry import TOOLS
from app.tools.news_tool import lookup_news


class IPOAgent:
    """
    Initial IPO agent facade.
    Uses deterministic routing for now.
    """

    def run(self, question: str) -> dict:
        route = classify_question(question)

        if route == "ipo":
            result = TOOLS["lookup_ipo"](
                "CULT.FIT LIMITED"
            )

        elif route == "financial":
            result = TOOLS["lookup_financials"](
                "CULT.FIT LIMITED"
            )

        elif route == "rag":
            result = TOOLS[
                "search_ipo_documents"
            ](
                question
            )

        elif route == "news":
            result = lookup_news(
                "CULT.FIT LIMITED"
            )
        
        else:
            result = {
                "message": (
                    "Mixed questions will be "
                    "handled in the next agent step."
                )
            }

        return {
            "route": route,
            "result": result,
        }