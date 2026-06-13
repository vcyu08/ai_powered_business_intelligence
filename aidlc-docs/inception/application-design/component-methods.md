# InsightForge — Component Methods

Note: Detailed business rules and data contracts are defined in Functional Design (CONSTRUCTION phase). This document captures method signatures and high-level purpose.

---

## DataProcessor (`data_processor.py`)

| Method | Signature | Purpose |
|---|---|---|
| `__init__` | `(csv_path: str) -> None` | Store CSV path; initialize DataFrame and knowledge-base attributes to None |
| `load_data` | `() -> pd.DataFrame` | Read CSV; derive Month, Quarter, Year, Age_Group columns; store in `self.df` |
| `compute_statistics` | `() -> Dict[str, Any]` | Aggregate stats (overall, time-series, product, regional, demographic); store in `self.knowledge_base` |
| `create_documents` | `() -> List[Document]` | Serialize knowledge-base into 5 LangChain Documents; store in `self.documents` |
| `get_dataframe` | `() -> pd.DataFrame` | Return the processed DataFrame |
| `get_knowledge_base` | `() -> Dict[str, Any]` | Return computed statistics dict |
| `get_summary_text` | `() -> str` | Return a Markdown-formatted summary for the Data Overview page |

---

## BusinessDataRetriever (`rag_system.py`)

| Method | Signature | Purpose |
|---|---|---|
| `_get_relevant_documents` | `(query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]` | Map query keywords to document categories; return matching documents plus always-included overview |

---

## RAGSystem (`rag_system.py`)

| Method | Signature | Purpose |
|---|---|---|
| `__init__` | `(documents: List[Document]) -> None` | Instantiate LLM, retriever, and build LCEL chain |
| `_build_chain` | `() -> None` | Construct `RunnablePassthrough.assign` → `ChatPromptTemplate` → `ChatAnthropic` → `StrOutputParser` chain |
| `_format_docs` | `(docs: List[Document]) -> str` | Join document page_content with separator for context injection |
| `query` | `(question: str, history: List[BaseMessage] = None) -> str` | Invoke chain; return complete answer string |
| `stream` | `(question: str, history: List[BaseMessage] = None) -> Iterator[str]` | Stream chain output; yield token chunks for `st.write_stream()` |

---

## MemoryManager (`memory_manager.py`)

| Method | Signature | Purpose |
|---|---|---|
| `__init__` | `(max_exchanges: int = 10) -> None` | Initialize message list and interaction log; store window size |
| `add_interaction` | `(human: str, ai: str) -> None` | Append HumanMessage + AIMessage; enforce rolling window |
| `get_history` | `() -> List[BaseMessage]` | Return copy of message list for chain injection |
| `get_log` | `() -> List[Tuple[str, str]]` | Return copy of interaction log for UI display |
| `clear` | `() -> None` | Reset messages and log |
| `exchange_count` | `@property -> int` | Return number of completed exchanges |

---

## QAEvalChain (`evaluator.py`)

| Method | Signature | Purpose |
|---|---|---|
| `__init__` | `() -> None` | Initialize Anthropic SDK client; set model to claude-opus-4-8 |
| `from_llm` | `@classmethod () -> QAEvalChain` | Factory method mirroring LangChain API; returns new instance |
| `evaluate_pair` | `(question: str, prediction: str, reference: str = None) -> Dict` | Score one Q&A pair via Claude; return score dict |
| `evaluate` | `(examples: List[Dict], predictions: List[Dict]) -> List[Dict]` | Batch evaluation mirroring LangChain `QAEvalChain.evaluate()` signature |
| `get_summary` | `() -> Dict[str, Any]` | Return count/mean/min/max over accumulated results |
| `results` | `@property -> List[Dict]` | Return copy of all evaluation results |

---

## Visualizations (`visualizations.py`)

| Function | Signature | Purpose |
|---|---|---|
| `plot_sales_trend` | `(df: pd.DataFrame) -> go.Figure` | Monthly sales line chart with point markers |
| `plot_product_performance` | `(df: pd.DataFrame) -> go.Figure` | Side-by-side bar charts: total sales and avg satisfaction per product |
| `plot_regional_analysis` | `(df: pd.DataFrame) -> go.Figure` | Donut pie (revenue share) + bar (avg transaction) by region |
| `plot_customer_demographics` | `(df: pd.DataFrame) -> go.Figure` | 2×2 subplot: gender sales, age-group sales, age histogram, satisfaction scatter |
| `plot_quarterly_heatmap` | `(df: pd.DataFrame) -> go.Figure` | Product × Quarter sales heatmap |

---

## Streamlit App (`app.py`)

| Function | Signature | Purpose |
|---|---|---|
| `init_system` | `@st.cache_resource () -> Tuple[DataProcessor, RAGSystem]` | One-time initialization of processor and RAG system |
| `get_memory` | `() -> MemoryManager` | Get or create MemoryManager from `st.session_state` |
| `get_evaluator` | `() -> QAEvalChain` | Get or create QAEvalChain from `st.session_state` |
| `main` | `() -> None` | Entry point: API key check, init, sidebar, page routing |
| `page_chat` | `(rag: RAGSystem, memory: MemoryManager, df: pd.DataFrame) -> None` | Chat page with streaming responses and suggestion buttons |
| `page_visualizations` | `(df: pd.DataFrame) -> None` | Tabbed visualization page with supporting data tables |
| `page_evaluation` | `(rag: RAGSystem) -> None` | QA evaluation page with batch runner and result display |
| `page_overview` | `(processor: DataProcessor, df: pd.DataFrame) -> None` | Data overview page with raw sample and summary stats |
