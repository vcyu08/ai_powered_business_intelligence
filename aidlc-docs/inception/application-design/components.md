# InsightForge — Component Definitions

## Component Overview

InsightForge is structured as six Python modules, each with a single responsibility. `app.py` orchestrates them directly (no intermediate service layer).

```
app.py (Streamlit UI + orchestration)
 ├── data_processor.py   → DataProcessor
 ├── rag_system.py       → BusinessDataRetriever + RAGSystem
 ├── memory_manager.py   → MemoryManager
 ├── visualizations.py   → chart functions
 └── evaluator.py        → QAEvalChain
```

---

## C-01: DataProcessor (`data_processor.py`)

**Purpose**: Load, enrich, and summarize the sales dataset; produce LangChain Documents for the knowledge base.

**Responsibilities**:
- Parse `sales_data.csv` with pandas; derive time-period and age-group columns
- Compute aggregated statistics (overall, monthly, quarterly, yearly, product, regional, demographic)
- Serialize statistics into five categorized `langchain_core.documents.Document` objects
- Expose the processed DataFrame and knowledge-base dict for downstream use

**Interfaces**:
- Input: CSV file path (constructor)
- Output: `pd.DataFrame`, `Dict[str, Any]` statistics, `List[Document]` knowledge base

---

## C-02: BusinessDataRetriever (`rag_system.py`)

**Purpose**: Custom LangChain `BaseRetriever` that maps query keywords to relevant knowledge-base Documents.

**Responsibilities**:
- Accept the list of `Document` objects produced by `DataProcessor`
- On each `invoke(query)`, scan query text for domain keywords and return matching document categories
- Always include the `overview` document for grounding regardless of query content

**Interfaces**:
- Input: natural-language query string
- Output: `List[Document]` (filtered subset of knowledge base)
- Extends: `langchain_core.retrievers.BaseRetriever`

---

## C-03: RAGSystem (`rag_system.py`)

**Purpose**: Assemble and expose the LangChain LCEL chain — retriever → prompt → LLM → parser.

**Responsibilities**:
- Instantiate `ChatAnthropic` (claude-opus-4-8) and `BusinessDataRetriever`
- Build a system prompt that instructs the LLM to act as InsightForge BI assistant
- Construct an LCEL chain using `RunnablePassthrough.assign` + `ChatPromptTemplate` + `StrOutputParser`
- Expose `query()` (blocking) and `stream()` (generator) for the Streamlit UI

**Interfaces**:
- Input: `List[Document]` (constructor), question string, conversation history
- Output: answer string (blocking) or string chunk generator (streaming)

---

## C-04: MemoryManager (`memory_manager.py`)

**Purpose**: Maintain per-session conversation history as LangChain message objects.

**Responsibilities**:
- Append `HumanMessage` / `AIMessage` pairs on each interaction
- Enforce a configurable rolling window (default 10 exchanges)
- Expose history for injection into the RAG chain's `MessagesPlaceholder`
- Provide `clear()` and an `exchange_count` property for the UI

**Interfaces**:
- Input: human/AI text strings (per interaction)
- Output: `List[BaseMessage]` (for chain), `List[Tuple[str, str]]` (for display log)

---

## C-05: QAEvalChain (`evaluator.py`)

**Purpose**: Evaluate InsightForge response quality using Claude as an AI judge, mirroring the LangChain `QAEvalChain` API.

**Responsibilities**:
- Use the Anthropic SDK directly (`anthropic.Anthropic`) to score Q&A pairs
- Score each response on: relevance, clarity, specificity, actionability (0–10 each), overall
- Accept batched `examples` / `predictions` lists via `evaluate()`, mirroring LangChain's API
- Accumulate results and expose a `get_summary()` with count/mean/min/max

**Interfaces**:
- Input: list of `{query, answer}` examples and `{result}` predictions
- Output: list of score dicts; summary dict

---

## C-06: Visualizations (`visualizations.py`)

**Purpose**: Produce Plotly figures from the processed DataFrame; one function per chart type.

**Responsibilities**:
- Accept `pd.DataFrame` and return `plotly.graph_objects.Figure`
- Cover five chart types: sales trend, product performance, regional analysis, customer demographics, quarterly heatmap
- Keep all chart logic stateless (no class needed)

**Interfaces**:
- Input: `pd.DataFrame` (processed, with derived columns)
- Output: `plotly.graph_objects.Figure`

---

## C-07: Streamlit App (`app.py`)

**Purpose**: User interface and top-level orchestration — the application entry point.

**Responsibilities**:
- Initialize and cache `DataProcessor` and `RAGSystem` via `@st.cache_resource`
- Manage `MemoryManager` and `QAEvalChain` in `st.session_state`
- Provide four pages: Chat Assistant, Visualizations, Model Evaluation, Data Overview
- Stream chat responses using LangChain `.stream()` + `st.write_stream()`
- Enforce API key presence at startup; display user-friendly errors (no stack traces)

**Interfaces**:
- Input: user interaction via Streamlit widgets / chat input
- Output: rendered Streamlit pages (charts, chat messages, evaluation results)
