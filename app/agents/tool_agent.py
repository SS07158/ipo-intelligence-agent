from langchain_ollama import ChatOllama

from app.agents.synthesizer import synthesize_tool_results
from app.agents.tool_registry import TOOLS
from app.config import settings


class ToolAgent:
    """
    LLM agent capable of selecting and executing IPO tools.
    """

    def __init__(
        self,
        model: str | None = None,
        default_company: str = "CULT.FIT LIMITED",
    ):
        self.default_company = default_company

        self.llm = ChatOllama(
            model=model or settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

        self.llm_with_tools = self.llm.bind_tools(
            TOOLS
        )

        self.tools_by_name = {
            tool.name: tool
            for tool in TOOLS
        }

    def run(
    self,
    question: str,
    max_iterations: int = 3,
) -> dict:
        """
        Run a multi-step tool-calling loop.
        """

        messages = [
            (
                "system",
                f"""
    You are an Indian IPO research assistant.

    Current company context:
    {self.default_company}

    Use tools whenever the answer requires factual IPO,
    financial, or DRHP information.

    Rules:
    - Use IPO lookup for structured IPO facts.
    - Use financial lookup for financial data.
    - Use revenue analysis for calculations.
    - Use document search for DRHP/RHP evidence.
    - Use the news tool for questions about recent or latest
    IPO/company news, headlines, or reported updates.
    - Use financial performance analysis for questions asking about
    overall financial performance, including revenue, profit/loss,
    adjusted EBITDA, and operating cash flow.
    -For questions about overall financial performance or changes
    across multiple financial metrics, prefer the financial
    performance analysis tool.
    - You may call multiple tools when the question requires
    multiple sources.
    - Use the company context when the user does not specify
    a company.
    - Do not invent facts.
    - Do not provide buy/sell recommendations.
    - Base factual conclusions on tool results.
    - Treat tool results as authoritative for factual claims.
    - Do not add external facts that are not present in the tool results.
    - For questions asking how revenue changed, prefer
    analyze_revenue_growth_tool.
    - Do not query individual periods unless the user explicitly
    asks for a specific period.
    - Never invent or probe an unavailable period such as FY2023
    just to obtain more context.
    """,
            ),
            (
                "human",
                question,
            ),
        ]

        tool_calls = []
        tool_results = []

        for _ in range(max_iterations):

            response = self.llm_with_tools.invoke(
                messages
            )

            messages.append(response)

            if not response.tool_calls:

                synthesis_tools = {
                    "analyze_financial_performance_tool",
                    "analyze_revenue_growth_tool",
                    "lookup_financials_tool",
                    "search_ipo_documents_tool",
                    "lookup_news_tool"
                }

                should_synthesize = any(
                    item["tool"] in synthesis_tools
                    for item in tool_results
                )

                if should_synthesize:

                    final_answer = synthesize_tool_results(
                        question,
                        tool_results,
                    )

                    return {
                        "answer": final_answer.answer,
                        "tool_calls": tool_calls,
                        "tool_results": tool_results,
                    }

                return {
                    "answer": response.content,
                    "tool_calls": tool_calls,
                    "tool_results": tool_results,
                }

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]

                tool_args = dict(
                    tool_call["args"]
                )

                if (
                    tool_name
                    in {
                        "lookup_ipo_tool",
                        "lookup_financials_tool",
                        "analyze_revenue_growth_tool",
                        "analyze_financial_performance_tool",
                        "lookup_news",
                    }
                    and not tool_args.get(
                        "company_name"
                    )
                ):
                    tool_args["company_name"] = (
                        self.default_company
                    )

                tool = self.tools_by_name.get(
                    tool_name
                )

                if tool is None:
                    raise ValueError(
                        f"Unknown tool: {tool_name}"
                    )

                tool_calls.append(
                    {
                        "name": tool_name,
                        "args": tool_args,
                        "id": tool_call["id"],
                    }
                )

                result = tool.invoke(
                    tool_args
                )

                tool_results.append(
                    {
                        "tool": tool_name,
                        "result": result,
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": tool_call["id"],
                    }
                )

        raise RuntimeError(
            "Agent reached maximum iterations "
            "without producing a final answer."
        )