import logging
import os

import streamlit as st
from dotenv import load_dotenv

from data_processor import DataProcessor
from evaluator import EvaluationResult, QAEvalChain
from memory_manager import MemoryManager
from rag_system import RAGSystem
from visualizations import (
    plot_age_groups,
    plot_product_breakdown,
    plot_region_comparison,
    plot_sales_trend,
    plot_satisfaction_heatmap,
)

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

CSV_PATH = "sales_data.csv"
MAX_QUERY_LENGTH = 1000


# ── Input validation ────────────────────────────────────────────────────────

def validate_input(query: str) -> tuple[bool, str | None]:
    stripped = query.strip()
    if not stripped:
        return False, "Please enter a question."
    if len(stripped) > MAX_QUERY_LENGTH:
        return False, (
            f"Query too long ({len(stripped)} chars). "
            f"Limit: {MAX_QUERY_LENGTH} characters."
        )
    return True, None


# ── Evaluation display ───────────────────────────────────────────────────────

def render_evaluation(evaluation: EvaluationResult) -> None:
    if evaluation.score is not None:
        st.info(f"⭐ **Score: {evaluation.score}/5** — {evaluation.reasoning}")
    else:
        st.warning("⚠️ Evaluation unavailable")


# ── Cached initialisation (once per server process) ──────────────────────────

@st.cache_resource
def get_data_processor() -> DataProcessor | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.session_state["init_error"] = (
            "ANTHROPIC_API_KEY is not set. "
            "Please copy .env.example to .env and add your key."
        )
        return None
    try:
        dp = DataProcessor(CSV_PATH)
        dp.load_data()
        dp.compute_statistics()
        return dp
    except Exception as e:
        logger.warning("DataProcessor init failed: %s", type(e).__name__)
        st.session_state["init_error"] = (
            "Failed to load sales data. "
            "Please ensure sales_data.csv is present in the application directory."
        )
        return None


@st.cache_resource
def get_rag_system(_dp: DataProcessor) -> RAGSystem | None:
    try:
        docs = _dp.create_documents()
        return RAGSystem(docs)
    except Exception as e:
        logger.warning("RAGSystem init failed: %s", type(e).__name__)
        st.session_state["init_error"] = (
            "Failed to initialise the AI system. Please restart the application."
        )
        return None


# ── Per-session initialisation ───────────────────────────────────────────────

def init_session() -> None:
    if "memory" not in st.session_state:
        st.session_state["memory"] = MemoryManager()
    if "evaluator" not in st.session_state:
        st.session_state["evaluator"] = QAEvalChain()
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "init_error" not in st.session_state:
        st.session_state["init_error"] = None


# ── Main application ─────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="InsightForge — Business Intelligence Assistant",
        page_icon="📊",
        layout="wide",
    )

    init_session()

    dp = get_data_processor()
    rag = get_rag_system(dp) if dp is not None else None

    if st.session_state.get("init_error"):
        st.error(st.session_state["init_error"])
        st.stop()

    stats = dp.stats

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("📈 Key Metrics")
        col1, col2 = st.columns(2)
        col1.metric("Total Sales", f"${stats['total_sales']:,.0f}")
        col2.metric("Total Records", f"{stats['total_records']:,}")
        col1.metric("Top Product", stats["top_product"])
        col2.metric("Top Region", stats["top_region"])

        st.divider()
        st.subheader("Sales Dashboard")
        st.plotly_chart(
            plot_sales_trend(stats["monthly_sales"]),
            use_container_width=True,
        )
        st.plotly_chart(
            plot_product_breakdown(stats["product_breakdown"]),
            use_container_width=True,
        )
        st.plotly_chart(
            plot_region_comparison(stats["regional_breakdown"]),
            use_container_width=True,
        )
        st.plotly_chart(
            plot_age_groups(stats["age_group_breakdown"]),
            use_container_width=True,
        )
        st.plotly_chart(
            plot_satisfaction_heatmap(stats["satisfaction_pivot"]),
            use_container_width=True,
        )

    # ── Main area ─────────────────────────────────────────────────────────────
    st.title("InsightForge 📊")
    st.caption(
        "AI-Powered Business Intelligence Assistant — "
        "Powered by Claude + LangChain"
    )
    st.divider()

    # Replay chat history
    for entry in st.session_state["chat_history"]:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])
            if entry["role"] == "assistant" and entry.get("evaluation"):
                render_evaluation(entry["evaluation"])

    # Chat input handler
    user_input = st.chat_input(
        "Ask a business question about your sales data..."
    )

    if user_input:
        is_valid, error_msg = validate_input(user_input)
        if not is_valid:
            st.warning(error_msg)
            return

        with st.chat_message("human"):
            st.markdown(user_input)

        history = st.session_state["memory"].get_messages()
        evaluation = EvaluationResult(score=None, reasoning="Evaluation unavailable")
        response_text = ""

        with st.chat_message("assistant"):
            try:
                response_text = st.write_stream(
                    rag.get_response(user_input, history)
                )
            except Exception:
                st.error(
                    "An error occurred while processing your request. "
                    "Please try again."
                )
                return

            with st.spinner("Evaluating response quality..."):
                evaluation = st.session_state["evaluator"].evaluate(
                    user_input, response_text
                )
            render_evaluation(evaluation)

        st.session_state["memory"].add_interaction(user_input, response_text)
        st.session_state["chat_history"].append(
            {"role": "human", "content": user_input, "evaluation": None}
        )
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": response_text, "evaluation": evaluation}
        )


if __name__ == "__main__":
    main()
