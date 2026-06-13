# Code Generation Plan — InsightForge

## Unit Context

- **Unit**: InsightForge (single unit — entire application)
- **Type**: Greenfield, single-unit Python application
- **Workspace Root**: `c:\Users\vcyu0\Documents\learning\Purdue AI\Course 7 - Capstone Projects\ai_powered_business_intelligence`
- **Code Location Pattern**: Flat workspace root — all source files directly in workspace root; tests in `tests/` subdirectory
- **Requirements Covered**: FR-01 through FR-09 (all functional requirements)

## Plan Checkboxes

- [x] Step 1: Project Setup files
- [x] Step 2: `data_processor.py`
- [x] Step 3: `memory_manager.py`
- [x] Step 4: `rag_system.py`
- [x] Step 5: `visualizations.py`
- [x] Step 6: `evaluator.py`
- [x] Step 7: `app.py`
- [x] Step 8: `tests/__init__.py` + `tests/test_data_processor.py`
- [x] Step 9: `tests/test_memory_manager.py`
- [x] Step 10: `tests/test_evaluator.py`
- [x] Step 11: `tests/test_rag_system.py`
- [x] Step 12: `tests/test_properties.py` (Hypothesis PBT — PROP-01 to PROP-11)
- [x] Step 13: Documentation summary (`aidlc-docs/construction/insightforge/code/code-summary.md`)

---

## Requirements Traceability

| Step | File(s) | Requirements |
|---|---|---|
| 1 | requirements.txt, .env.example, .gitignore | NFR-TEST-01, SECURITY-10, SECURITY-12 |
| 2 | data_processor.py | FR-04 (sales data loading), FR-05 (statistics) |
| 3 | memory_manager.py | FR-06 (conversation memory, rolling window) |
| 4 | rag_system.py | FR-03 (RAG retrieval), FR-07 (LangChain + Claude) |
| 5 | visualizations.py | FR-05 (charts: trend, product, region, age, satisfaction) |
| 6 | evaluator.py | FR-08 (QA evaluation 1–5) |
| 7 | app.py | FR-01 (Streamlit UI), FR-02 (streaming), FR-09 (integration) |
| 8 | test_data_processor.py | NFR-TEST-01, PROP-01–PROP-05 |
| 9 | test_memory_manager.py | NFR-TEST-01, PROP-06–PROP-08 |
| 10 | test_evaluator.py | NFR-TEST-01 |
| 11 | test_rag_system.py | NFR-TEST-03, PROP-09–PROP-11 |
| 12 | test_properties.py | NFR-TEST-02, PBT-09, PROP-01–PROP-11 |
| 13 | code-summary.md | Documentation |

---

## Step Details

### Step 1: Project Setup Files

**Files to create**:
- `requirements.txt` — pinned production dependencies (SECURITY-10)
- `requirements-dev.txt` — pinned dev/test dependencies
- `.env.example` — API key template (SECURITY-12)
- `.gitignore` — exclude .env, __pycache__, .coverage, etc.

**Production dependencies** (requirements.txt):
```
streamlit==1.43.2
langchain-core==0.3.52
langchain-anthropic==0.3.7
anthropic==0.49.0
pandas==2.2.3
plotly==5.24.1
python-dotenv==1.0.1
```

**Dev dependencies** (requirements-dev.txt):
```
pytest==8.3.5
pytest-cov==5.0.0
hypothesis==6.131.14
```

---

### Step 2: `data_processor.py`

**Class**: `DataProcessor`
**Location**: workspace root

**Methods to implement**:
- `__init__(self, csv_path: str)` — store path; init logger
- `load_data(self) -> pd.DataFrame` — read CSV; parse Date; sort ascending; validate columns; store as `self.df`
- `compute_statistics(self) -> dict` — compute all 10 statistics fields (total_sales, total_records, avg_sales, top_product, top_region, product_breakdown, regional_breakdown, monthly_sales, age_group_breakdown, satisfaction_pivot)
- `create_documents(self) -> list[Document]` — build 11 LangChain Documents (1 overview + 4 product + 4 region + 1 time_series + 1 customer)

**NFR patterns applied**: ModuleLogger, Exception Shield (raise on load failure → BR-14), TimeoutConfig (N/A — no LLM calls)

---

### Step 3: `memory_manager.py`

**Class**: `MemoryManager`
**Location**: workspace root

**Methods to implement**:
- `__init__(self, max_exchanges: int = 10)` — initialize empty messages list; store max
- `add_interaction(self, human: str, ai: str) -> None` — append HumanMessage + AIMessage pair; enforce rolling window (remove oldest pair if > max_exchanges)
- `get_messages(self) -> list` — return current message list (HumanMessage + AIMessage objects)
- `clear(self) -> None` — reset messages list

**NFR patterns applied**: ModuleLogger; rolling window per BR-06; message alternation per BR-07

---

### Step 4: `rag_system.py`

**Classes**: `BusinessDataRetriever` (inner), `RAGSystem`
**Location**: workspace root

**BusinessDataRetriever** (extends `BaseRetriever`):
- `documents: list[Document]` — Pydantic field
- `_get_relevant_documents(self, query: str, *, run_manager=None) -> list[Document]` — KEYWORD_MAP matching; always include overview; multi-category (Q1=A)

**RAGSystem**:
- `__init__(self, documents: list[Document])` — build `BusinessDataRetriever`; build `ChatAnthropic` with `request_timeout=60`; build `ChatPromptTemplate` (system prompt + MessagesPlaceholder + human); assemble LCEL chain via `RunnablePassthrough.assign`
- `get_response(self, query: str, chat_history: list) -> Generator` — stream chain via `chain.stream()`; yield chunks; re-raise exceptions after logging

**NFR patterns applied**: TimeoutConfig (`request_timeout=60`), ModuleLogger, Exception Shield (re-raise), Contextual Grounding (system prompt), Streaming Delivery

---

### Step 5: `visualizations.py`

**Functions** (5 stateless chart functions):
**Location**: workspace root

- `plot_sales_trend(monthly_sales: dict) -> go.Figure` — Plotly line chart; x=month string, y=sales value; title "Monthly Sales Trend"
- `plot_product_breakdown(product_breakdown: pd.DataFrame) -> go.Figure` — Plotly bar chart; x=Product, y=sum (total sales); title "Sales by Product"
- `plot_region_comparison(regional_breakdown: pd.DataFrame) -> go.Figure` — Plotly bar chart; x=Region, y=sum; title "Sales by Region"
- `plot_age_groups(age_group_breakdown: pd.DataFrame) -> go.Figure` — Plotly bar chart; x=AgeGroup, y=count; title "Customer Age Distribution"
- `plot_satisfaction_heatmap(satisfaction_pivot: pd.DataFrame) -> go.Figure` — Plotly imshow heatmap; index=Product, columns=Region, values=avg satisfaction; title "Customer Satisfaction by Product & Region"

**NFR patterns applied**: ModuleLogger; no external API calls; no error shield needed (pure computation)

---

### Step 6: `evaluator.py`

**Class**: `QAEvalChain`
**Location**: workspace root

**Methods to implement**:
- `__init__(self)` — init Anthropic client with `httpx.Timeout(60.0)`; init logger
- `from_llm(cls) -> QAEvalChain` — classmethod (mirrors LangChain API); delegates to `__init__`
- `evaluate(self, question: str, answer: str) -> EvaluationResult` — build eval prompt; call `messages.create()`; parse JSON response; validate score in [1,5]; return `EvaluationResult`; on any exception: log + return safe default

**EvaluationResult dataclass**: `score: int | None`, `reasoning: str`

**NFR patterns applied**: TimeoutConfig (`httpx.Timeout(60.0)`), Exception Shield (returns safe default), ModuleLogger

---

### Step 7: `app.py`

**Location**: workspace root (Streamlit entry point)

**Sections to implement**:
1. Imports + logging setup (`logging.basicConfig(level=logging.WARNING, ...)`)
2. `load_dotenv()` + API key validation (BR-11, SECURITY-12)
3. `validate_input(query: str) -> tuple[bool, str | None]` — Guard-Clause Validation (Pattern 4)
4. `render_evaluation(evaluation: EvaluationResult) -> None` — display score + reasoning
5. `@st.cache_resource get_data_processor()` — init DataProcessor (Process-Scoped Singleton)
6. `@st.cache_resource get_rag_system(dp)` — init RAGSystem
7. `init_session()` — initialize memory, evaluator, chat_history in session_state
8. `st.set_page_config(layout="wide")` + page header
9. Sidebar: metrics (4 KPI) + 5 charts via `st.sidebar.plotly_chart()`
10. ErrorBanner check (`st.session_state["init_error"]`)
11. Chat history replay loop
12. `st.chat_input()` handler — validate → stream → evaluate → store → display

**NFR patterns applied**: All 9 patterns applied; Q1=A, Q2=A (sync eval with spinner), Q3=A (no blocklist); BR-01/02/11/12/13

---

### Step 8: `tests/__init__.py` + `tests/test_data_processor.py`

**`tests/__init__.py`**: Empty file (makes tests/ a package)

**`tests/test_data_processor.py`**:
- Fixture: `sample_df()` — small DataFrame with known values (4 products × 4 regions × 3 months = 48 rows)
- Fixture: `data_processor(tmp_path, sample_df)` — writes CSV to temp dir; creates DataProcessor
- `test_load_data_columns()` — verifies all 7 required columns present after load
- `test_load_data_row_count()` — verifies correct row count
- `test_compute_statistics_total_sales()` — total_sales equals known sum
- `test_compute_statistics_top_product()` — top_product is a valid product name
- `test_compute_statistics_avg_sales_bounds()` — avg between min and max
- `test_create_documents_count()` — returns exactly 11 documents
- `test_create_documents_overview_present()` — one document with category="overview"
- `test_create_documents_categories()` — all 5 categories present

---

### Step 9: `tests/test_memory_manager.py`

**Tests**:
- `test_add_interaction_increments_count()` — 1 interaction → 2 messages
- `test_rolling_window_enforced()` — 11 interactions → still max 20 messages
- `test_message_types()` — messages alternate HumanMessage/AIMessage
- `test_get_messages_empty()` — fresh manager returns []
- `test_clear()` — after clear, get_messages() returns []

---

### Step 10: `tests/test_evaluator.py`

**Tests** (mock `anthropic.Anthropic` to avoid API calls):
- `test_evaluate_returns_result()` — mock response with score=4; result has score=4
- `test_evaluate_score_range()` — mock responses with scores 1–5; all return correct scores
- `test_evaluate_handles_api_error()` — mock raises exception; result.score is None, reasoning is "Evaluation unavailable"
- `test_evaluate_handles_invalid_json()` — mock returns non-JSON text; result.score is None
- `test_from_llm_returns_instance()` — `QAEvalChain.from_llm()` returns a `QAEvalChain`

---

### Step 11: `tests/test_rag_system.py`

**Tests** (mock `ChatAnthropic` to avoid API calls):
- `test_retriever_overview_always_present()` — any query → at least one overview doc returned
- `test_retriever_multi_category()` — query with "product" and "region" keywords → docs from both categories returned
- `test_retriever_no_match_returns_overview()` — query with no keyword matches → only overview returned
- `test_retriever_results_subset_of_input()` — all returned docs are in the original document list
- `test_rag_system_chain_assembled()` — RAGSystem init succeeds; chain attribute is not None

---

### Step 12: `tests/test_properties.py`

**Hypothesis PBT tests covering PROP-01 to PROP-11**:

*DataProcessor properties (PROP-01 to PROP-05)*:
- `test_prop_01_total_sales_accuracy` — `@given` random sales values; `total_sales == sum(sales)`
- `test_prop_02_record_count_accuracy` — `total_records == len(generated_rows)`
- `test_prop_03_top_product_validity` — `top_product in {"Widget A","Widget B","Widget C","Widget D"}`
- `test_prop_04_top_region_validity` — `top_region in {"North","South","East","West"}`
- `test_prop_05_avg_sales_bounds` — `min(sales) <= avg_sales <= max(sales)`

*MemoryManager properties (PROP-06 to PROP-08)*:
- `test_prop_06_exchange_count_growth` — N interactions (N≤10) → `len(msgs) == N*2`
- `test_prop_07_rolling_window_cap` — N>10 interactions → `len(msgs) <= 20`
- `test_prop_08_message_alternation` — messages always alternate Human/AI

*BusinessDataRetriever properties (PROP-09 to PROP-11)*:
- `test_prop_09_overview_always_present` — any query text → overview doc in results
- `test_prop_10_results_subset_of_input` — all returned docs are members of input list
- `test_prop_11_category_coherence` — if keyword for category X in query → at least one doc with category X in results

**Settings**: `@settings(max_examples=100, deadline=5000)` on all property tests

---

### Step 13: Documentation Summary

**File**: `aidlc-docs/construction/insightforge/code/code-summary.md`

Content:
- File inventory with paths, sizes, and purpose
- Key design decisions implemented
- Known limitations
- How to run (brief)
