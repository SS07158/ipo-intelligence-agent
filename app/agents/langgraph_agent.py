from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agents.router import (
    classify_question,
)

from app.agents.state import AgentState
from app.agents.tool_registry import TOOLS
from app.config import settings
from app.agents.synthesizer import (
    synthesize_tool_results,
)
from app.agents.provenance import (
    render_answer,
)

from app.agents.company_resolver import (
    resolve_company_from_question,
)

from database.database import SessionLocal


class LangGraphIPOAgent:
    """
    IPO agent implemented with LangGraph.
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

        self.llm_with_tools = (
            self.llm.bind_tools(TOOLS)
        )

        self.tools_by_name = {
            tool.name: tool
            for tool in TOOLS
        }

        

        self.graph = self._build_graph()

    def agent_node(
    self,
    state: AgentState,
    ):
        question = state["messages"][1].content

        session = SessionLocal()

        try:
            company_name = resolve_company_from_question(
                question,
                session,
            )
        finally:
            session.close()

        fallback_calls = self._fallback_tool_calls(
            question,
        )

        if not fallback_calls:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "I could not determine the appropriate "
                            "tool for this question."
                        )
                    )
                ]
            }

        tool_calls = [
            {
                "name": call["tool"],
                "args": call["args"],
                "id": f"router_{index}",
                "type": "tool_call",
            }
            for index, call in enumerate(
                fallback_calls
            )
        ]

        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=tool_calls,
                )
            ]
        }

    def tool_node(
    self,
    state: AgentState,
    ):
        last_message = state["messages"][-1]

        tool_messages = []
        results = []

        for tool_call in last_message.tool_calls:

            tool = self.tools_by_name.get(
                tool_call["name"]
            )

            if tool is None:
                raise ValueError(
                    f"Unknown tool: "
                    f"{tool_call['name']}"
                )

            try:
                result = tool.invoke(
                    tool_call["args"]
                )

            except Exception as exc:
                result = {
                    "found": False,
                    "error": True,
                    "tool": tool_call["name"],
                    "message": (
                        "Tool execution failed: "
                        f"{str(exc)}"
                    ),
                }

            results.append(
                {
                    "tool": tool_call["name"],
                    "args": tool_call["args"],
                    "result": result,
                }
            )

            tool_messages.append(
                {
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call["id"],
                }
            )

        return {
            "messages": tool_messages,
            "tool_results": (
                state["tool_results"] + results
            ),
        }

    def synthesizer_node(
    self,
    state: AgentState,
    ):
        question = state["messages"][1].content

        result = synthesize_tool_results(
            question=question,
            tool_results=state["tool_results"],
        )

        answer = render_answer(
            result
        )

        return {
            "final_answer": answer,
            "tool_results": state["tool_results"],
        }

    def should_continue(
    self,
    state: AgentState,
    ):
        last_message = state["messages"][-1]

        if getattr(
            last_message,
            "tool_calls",
            None,
        ):
            return "tools"

        return "synthesizer"

    def _resolve_company(
        self,
        question: str,
    ) -> str:
        session = SessionLocal()

        try:
            resolved = resolve_company_from_question(
                question,
                session,
            )

            return resolved or self.default_company

        finally:
            session.close()

    def _fallback_tool_calls(
        self,
        question: str,
    ) -> list[dict]:

        company_name = self._resolve_company(
            question
        )

        normalized = question.lower()

        # -------------------------------------------------
        # MARKET SHARE
        # -------------------------------------------------

        market_share_terms = [
            "market share",
            "share of the market",
            "market position",
            "industry share",
        ]

        if any(
            term in normalized
            for term in market_share_terms
        ):
            return [
                {
                    "tool": "search_ipo_documents_tool",
                    "args": {
                        "question": question,
                        "top_k": 5,
                        "section": "INDUSTRY OVERVIEW",
                        "company_name": company_name,
                    },
                }
            ]

        # -------------------------------------------------
        # POST-LISTING
        # -------------------------------------------------

        post_listing_terms = [
            "after ipo listing",
            "after listing",
            "post ipo listing",
            "post-listing",
            "post listing",
            "listing outcome",
            "expected outcome after ipo",
        ]

        if any(
            term in normalized
            for term in post_listing_terms
        ):
            return [
                {
                    "tool": "lookup_ipo_tool",
                    "args": {
                        "company_name": company_name,
                    },
                },
                {
                    "tool": "search_ipo_documents_tool",
                    "args": {
                        "question": (
                            "What does the DRHP state about trading, liquidity, "
                            "market development, and possible share-price fluctuations "
                            "after the IPO listing?"
                        ),
                        "top_k": 5,
                        "section": "SECTION II: RISK FACTORS",
                        "company_name": company_name,
                    },
                },
            ]

        # -------------------------------------------------
        # OVERVIEW
        # -------------------------------------------------

        if (
            "give an overview" in normalized
            or "quick overview" in normalized
            or "overview of" in normalized
        ):
            return [
                {
                    "tool": "lookup_ipo_tool",
                    "args": {
                        "company_name": company_name,
                    },
                },
                {
                    "tool": "search_ipo_documents_tool",
                    "args": {
                        "question": (
                            f"What business does "
                            f"{company_name} operate in, "
                            f"what products or services does "
                            f"it offer, and what key IPO or "
                            f"offer details are disclosed "
                            f"in the DRHP?"
                        ),
                        "top_k": 5,
                        "company_name": company_name,
                    },
                },
            ]

        # -------------------------------------------------
        # MARKET SHARE
        # -------------------------------------------------

        market_share_terms = [
            "market share",
            "market size",
            "market position",
            "share of the market",
        ]

        if any(
            term in normalized
            for term in market_share_terms
        ):
            return [
                {
                    "tool": "search_ipo_documents_tool",
                    "args": {
                        "question": (
                            f"What is the market share, "
                            f"market position, or relevant "
                            f"competitive share of "
                            f"{company_name} according to "
                            f"the industry information in "
                            f"the DRHP?"
                        ),
                        "top_k": 5,
                        "section": "INDUSTRY OVERVIEW",
                        "company_name": company_name,
                    },
                }
            ]

        # -------------------------------------------------
        # POST-LISTING QUESTIONS
        # -------------------------------------------------

        listing_terms = [
            "after ipo listing",
            "after the ipo listing",
            "post listing",
            "post-listing",
            "listing outcome",
            "expected outcome after ipo",
            "expected outcome after listing",
            "what happens after listing",
            "impact after listing",
            "after listing",
        ]

        if any(
            term in normalized
            for term in listing_terms
        ):
            return [
                {
                    "tool": "lookup_ipo_tool",
                    "args": {
                        "company_name": company_name,
                    },
                },
                {
                    "tool": "search_ipo_documents_tool",
                    "args": {
                        "question": (
                            f"What does the DRHP of "
                            f"{company_name} disclose about "
                            f"the post-listing situation, "
                            f"including trading, liquidity, "
                            f"market-price factors, and "
                            f"relevant risks or expectations "
                            f"after the IPO?"
                        ),
                        "top_k": 5,
                        "company_name": company_name,
                    },
                },
            ]

        # -------------------------------------------------
        # NORMAL CATEGORY ROUTING
        # -------------------------------------------------

        category = classify_question(
            question
        )

        if category == "financial":

            growth_terms = [
                "revenue growth",
                "revenue change",
                "revenue increased",
                "revenue decreased",
                "revenue changed",
                "cagr",
                "growth rate",
            ]

            if any(
                term in normalized
                for term in growth_terms
            ):
                return [
                    {
                        "tool":
                            "analyze_revenue_growth_tool",
                        "args": {
                            "company_name":
                                company_name,
                        },
                    }
                ]

            return [
                {
                    "tool":
                        "lookup_financials_tool",
                    "args": {
                        "company_name":
                            company_name,
                    },
                }
            ]

        if category == "ipo":
            return [
                {
                    "tool": "lookup_ipo_tool",
                    "args": {
                        "company_name":
                            company_name,
                    },
                }
            ]

        if category == "news":
            return [
                {
                    "tool": "lookup_news_tool",
                    "args": {
                        "company_name":
                            company_name,
                    },
                }
            ]

        if category == "rag":
            return [
                {
                    "tool":
                        "search_ipo_documents_tool",
                    "args": {
                        "question": question,
                        "top_k": 5,
                        "company_name":
                            company_name,
                    },
                }
            ]

        # -------------------------------------------------
        # MIXED QUESTIONS
        # -------------------------------------------------

        if category == "mixed":

            calls = []

            news_terms = [
                "news",
                "recent news",
                "latest news",
                "recent update",
                "latest update",
                "headlines",
            ]

            financial_terms = [
                "financial",
                "revenue",
                "profit",
                "margin",
                "growth",
                "ebitda",
                "cash flow",
                "profitability",
            ]

            document_terms = [
                "risk",
                "risks",
                "drhp",
                "rhp",
                "industry",
                "business model",
                "competitive",
                "operations",
                "strategy",
                "accounting",
            ]

            if any(
                term in normalized
                for term in news_terms
            ):
                calls.append(
                    {
                        "tool":
                            "lookup_news_tool",
                        "args": {
                            "company_name":
                                company_name,
                        },
                    }
                )

            if any(
                term in normalized
                for term in financial_terms
            ):
                calls.append(
                    {
                        "tool":
                            "lookup_financials_tool",
                        "args": {
                            "company_name":
                                company_name,
                        },
                    }
                )

            if any(
                term in normalized
                for term in document_terms
            ):
                calls.append(
                    {
                        "tool":
                            "search_ipo_documents_tool",
                        "args": {
                            "question": question,
                            "top_k": 5,
                            "company_name":
                                company_name,
                        },
                    }
                )

            return calls

        return []

    def _build_graph(self):
        graph = StateGraph(
            AgentState
        )

        graph.add_node(
            "agent",
            self.agent_node,
        )

        graph.add_node(
            "tools",
            self.tool_node,
        )

        graph.add_node(
            "synthesizer",
            self.synthesizer_node,
        )

        graph.add_edge(
            START,
            "agent",
        )

        graph.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "tools": "tools",
                "synthesizer": "synthesizer",
            },
        )

        graph.add_edge(
            "tools",
            "synthesizer",
        )

        graph.add_edge(
            "synthesizer",
            END,
        )

        return graph.compile()

    def run(
        self,
        question: str,
    ) -> dict:

        system_message = f"""
        You are an Indian IPO research assistant.

        Current company context:
        {self.default_company}

        Your job is to answer the user's question using ONLY information
        returned by the tools in this conversation.

        Rules:

        1. Use IPO lookup for structured IPO facts.
        2. Use financial lookup for structured financial data.
        3. Use revenue analysis for calculations.
        4. Use document search for DRHP/RHP evidence.
        5. You may call multiple tools when necessary.
        6. For revenue-change questions, prefer the revenue-analysis tool.
        7. Treat tool results as the only authoritative source for factual claims.
        8. Do NOT use outside knowledge.
        9. Do NOT invent facts, examples, company names, products,
        strategies, regulations, or numbers.
        10. Do NOT introduce companies, brands, or entities that are not
            present in the user's question or tool results.
        11. When combining multiple tools, synthesize ONLY the information
            returned by those tools.
        12. If a tool returns no evidence, explicitly say that the evidence
            was not found. Do NOT replace the missing evidence with generic
            industry knowledge.
        13. For financial questions, preserve the exact values and units
            returned by the tool.
        14. For document questions, distinguish clearly between:
            - facts explicitly stated in the document
            - calculations derived from structured data
        15. Do not provide investment advice or buy/sell recommendations.

        Final answer requirements:
        - Answer the user's exact question.
        - Be concise and factual.
        - Do not create a narrative unrelated to the user's question.
        - Do not mention unsupported mitigation strategies or company actions.
        - Treat tool results with found=false or an explicit error
        as tool failures.
        - Do not invent a replacement answer.
        - Explain the failure clearly and continue when another tool
        can still answer the question.
        """
        

        result = self.graph.invoke(
            {
                "messages": [
                    (
                        "system",
                        system_message,
                    ),
                    (
                        "human",
                        question,
                    ),
                ],
                "tool_results":[],
                "final_answer":"",
            }
        )



        return {
            "answer": result["final_answer"],
            "messages": result["messages"],
            "tool_results": result["tool_results"],
        }
        