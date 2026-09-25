import re
import streamlit as st
from pathlib import Path

from app.frontend.agent_client import ask_agent

def clean_answer_for_display(answer: str) -> str:
    """Remove internal retrieval IDs from the user-facing answer."""

    answer = re.sub(
        r"\s*\(Evidence ID:\s*[^)]+\)",
        "",
        answer,
    )

    answer = re.sub(
        r"\s*\[Evidence ID:\s*[^\]]+\]",
        "",
        answer,
    )

    answer = re.sub(
        r"\s*\[[^\]\n]*-chunk-\d+\]",
        "",
        answer,
        flags=re.IGNORECASE,
    )

    return answer.strip()
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IPO Intelligence Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD CSS
# ============================================================

css_path = Path(__file__).parent / "styles" / "theme.css"

if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "selected_company" not in st.session_state:
    st.session_state.selected_company = "CULT.FIT LIMITED"

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # Brand
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="brand">
            <div class="brand-title">IPO Intelligence</div>
            <div class="brand-subtitle">Research Assistant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # Company Selection
    # --------------------------------------------------------

    st.markdown("### Company")

    company = st.selectbox(
        "Select IPO",
        [
            "CULT.FIT LIMITED",
            "Sterlite Electric Limited",
        ],
        label_visibility="collapsed",
    )

    st.session_state.selected_company = company

    # --------------------------------------------------------
    # Quick Research
    # --------------------------------------------------------

    st.markdown("### Quick Research")

    quick_prompt = None

    quick_col1, quick_col2 = st.columns(2)

    with quick_col1:

        if st.button(
            "Overview",
            use_container_width=True,
        ):
            quick_prompt = (
                f"Give an overview of "
                f"{st.session_state.selected_company}, "
                f"including its business and IPO details."
            )

        if st.button(
            "Risks",
            use_container_width=True,
        ):
            quick_prompt = (
                f"What are the major internal risks "
                f"of {st.session_state.selected_company}?"
            )

    with quick_col2:

        if st.button(
            "Financials",
            use_container_width=True,
        ):
            quick_prompt = (
                f"What are the key financial metrics "
                f"of {st.session_state.selected_company}?"
            )

        if st.button(
            "News",
            use_container_width=True,
        ):
            quick_prompt = (
                f"What is the latest news about "
                f"{st.session_state.selected_company}?"
            )

    st.divider()

    # --------------------------------------------------------
    # System Status
    # --------------------------------------------------------

    st.markdown("### System")

    st.markdown(
        """
        <div class="status-row">
            <span class="status-dot"></span>
            <span>Frontend ready</span>
        </div>

        <div class="status-muted">
            Backend connection pending
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN HERO SECTION
# ============================================================

selected_company = st.session_state.selected_company

st.html(
    f"""
    <div class="hero-card">

        <div class="hero-eyebrow">
            IPO RESEARCH WORKSPACE
        </div>

        <div class="hero-title">
            {selected_company}
        </div>

        <div class="hero-subtitle">
            Research this IPO across filings, financial data,
            risks and recent news using the IPO Intelligence Agent.
        </div>

        <div class="hero-status-row">

            <span class="status-chip">
                <span class="chip-dot"></span>
                Documents
            </span>

            <span class="status-chip">
                <span class="chip-dot"></span>
                Financials
            </span>

            <span class="status-chip">
                <span class="chip-dot"></span>
                News
            </span>

        </div>

    </div>
    """
)


# ============================================================
# RESEARCH ASSISTANT HEADER
# ============================================================

st.html(
    """
    <div class="section-heading">

        <div class="section-title">
            Research Assistant
        </div>

        <div class="section-subtitle">
            Ask questions about the selected IPO.
        </div>

    </div>
    """
)


# ============================================================
# EMPTY CHAT STATE
# ============================================================

if not st.session_state.messages:

    st.html(
        """
        <div class="empty-state">

            <div class="empty-icon">
                💬
            </div>

            <div class="empty-title">
                Ask about this IPO
            </div>

            <div class="empty-text">
                Research risks, financials, IPO documents and news.
            </div>

        </div>
        """
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # ----------------------------------------------------
        # Display Sources
        # ----------------------------------------------------

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            sources = message["sources"]

            with st.expander(
                f"Sources ({len(sources)})",
                expanded=False,
            ):

                for source in sources:

                    title = source.get("title")
                    document_type = source.get("document_type")

                    source_name = source.get(
                        "source",
                        "Unknown source",
                    )

                    page = source.get("page_number")

                    url = (
                        source.get("source_url")
                        or source.get("url")
                    )

                    # ----------------------------------------
                    # Source Label
                    # ----------------------------------------

                    if title:
                        label = title

                    elif document_type:
                        label = document_type

                    else:
                        label = "Source"

                    # ----------------------------------------
                    # Source Details
                    # ----------------------------------------

                    details = [
                        label,
                        source_name,
                    ]

                    if page is not None:
                        details.append(
                            f"p. {page}"
                        )

                    st.markdown(
                        f"**{' — '.join(details)}**"
                    )

                    # ----------------------------------------
                    # Source URL
                    # ----------------------------------------

                    if url:
                        st.markdown(
                            f"[Open source]({url})"
                        )

                    st.divider()


# ============================================================
# QUICK QUERY HANDLING
# ============================================================

quick_query = st.session_state.pop(
    "quick_query",
    None,
)


# ============================================================
# CHAT INPUT
# ============================================================

chat_prompt = st.chat_input(
    "Ask about this IPO..."
)

prompt = chat_prompt or quick_prompt


# ============================================================
# PROCESS USER QUERY
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Store User Message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    # --------------------------------------------------------
    # Call Backend Agent
    # --------------------------------------------------------

    with st.spinner(
        "Researching IPO documents..."
    ):

        sources = []

        try:

            response = ask_agent(
                prompt,
                st.session_state.selected_company,
            )

            answer = clean_answer_for_display(
                response["answer"]
            )

            sources = response.get(
                "sources",
                [],
            )

        except Exception as e:

            answer = (
                f"Backend error: {e}"
            )

    # --------------------------------------------------------
    # Store Assistant Response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )

    # --------------------------------------------------------
    # Refresh UI
    # --------------------------------------------------------

    st.rerun()

