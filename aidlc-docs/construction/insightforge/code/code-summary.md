# InsightForge — Code Generation Summary

## File Inventory

### Production Source Files (workspace root)

| File | Lines | Purpose |
|---|---|---|
| `app.py` | ~165 | Streamlit entry point; UI, orchestration, all 9 NFR patterns |
| `data_processor.py` | ~120 | DataProcessor — CSV ingestion, statistics, 11 LangChain Documents |
| `rag_system.py` | ~95 | BusinessDataRetriever (BaseRetriever) + RAGSystem (LCEL chain) |
| `memory_manager.py` | ~25 | MemoryManager — rolling window, LangChain messages |
| `visualizations.py` | ~65 | 5 stateless Plotly chart functions |
| `evaluator.py` | ~60 | QAEvalChain + EvaluationResult dataclass (Anthropic SDK direct) |

### Configuration & Environment

| File | Purpose |
|---|---|
| `requirements.txt` | Pinned production dependencies (SECURITY-10) |
| `requirements-dev.txt` | Pinned dev/test dependencies |
| `.env.example` | API key template (copy to .env — SECURITY-12) |
| `.gitignore` | Excludes .env, __pycache__, .coverage, .hypothesis/ |

### Test Files (`tests/`)

| File | Tests | Coverage Target |
|---|---|---|
| `conftest.py` | — | sys.path setup for imports |
| `test_data_processor.py` | 9 | DataProcessor load, stats, documents |
| `test_memory_manager.py` | 6 | MemoryManager window, types, clear |
| `test_evaluator.py` | 5 | QAEvalChain scores, error handling |
| `test_rag_system.py` | 5 | Retriever behavior, RAGSystem chain |
| `test_properties.py` | 11 | Hypothesis PBT — PROP-01 to PROP-11 |

---

## Requirements Coverage

| Requirement | File(s) | Status |
|---|---|---|
| FR-01 Streamlit UI | `app.py` | ✅ |
| FR-02 Streaming responses | `app.py`, `rag_system.py` | ✅ |
| FR-03 RAG retrieval | `rag_system.py` | ✅ |
| FR-04 Sales data loading | `data_processor.py` | ✅ |
| FR-05 Statistics + charts | `data_processor.py`, `visualizations.py` | ✅ |
| FR-06 Conversation memory | `memory_manager.py` | ✅ |
| FR-07 LangChain + Claude | `rag_system.py` | ✅ |
| FR-08 QA evaluation | `evaluator.py` | ✅ |
| FR-09 End-to-end integration | `app.py` | ✅ |

---

## NFR Pattern Implementation

| Pattern | File | Code Element |
|---|---|---|
| Configure-Once Timeout | `rag_system.py`, `evaluator.py` | `request_timeout=60`, `httpx.Timeout(60.0)` |
| Process-Scoped Singleton | `app.py` | `@st.cache_resource` on `get_data_processor()` and `get_rag_system()` |
| Streaming Delivery | `app.py`, `rag_system.py` | `st.write_stream()` + `chain.stream()` |
| Guard-Clause Validation | `app.py` | `validate_input()` function |
| Exception Shield | `rag_system.py`, `evaluator.py`, `app.py` | try/except in `get_response()`, `evaluate()`, chat handler |
| Logger-Per-Module | All modules | `logging.getLogger(__name__)` |
| Contextual Grounding | `rag_system.py` | `SYSTEM_PROMPT` constant in `ChatPromptTemplate` |
| Sequential Post-Processing | `app.py` | `st.spinner()` wrapping synchronous `evaluate()` call |
| Generative Property Verification | `tests/test_properties.py` | Hypothesis `@given` — 11 properties |

---

## Key Design Decisions (Implemented)

| Decision | Implementation |
|---|---|
| Q1=A Multi-category retrieval | `BusinessDataRetriever` accumulates all matched categories into a set |
| Q2=A Auto-evaluate every response | `evaluator.evaluate()` called after every `st.write_stream()` completes |
| Q3=A No injection blocklist | Tight system prompt framing only; reliance on Claude's safety |
| Q4=B 1,000 char limit | `MAX_QUERY_LENGTH = 1000` in `validate_input()` |
| BR-03 Overview always included | `matched: set[str] = {"overview"}` initialisation in retriever |
| BR-06 Rolling window | `self._messages = self._messages[-max_messages:]` in `add_interaction()` |
| BR-11 API key check | `os.getenv("ANTHROPIC_API_KEY")` guard in `get_data_processor()` |

---

## Known Limitations

1. **Dependency versions**: Pinned versions in `requirements.txt` were set at design time. Run `pip install -r requirements.txt` and verify no conflicts before first use; re-pin if needed with `pip freeze > requirements.txt`.
2. **Streamlit session isolation**: `@st.cache_resource` is process-scoped. Multiple users connecting to the same Streamlit server share one `DataProcessor` + `RAGSystem` instance; `MemoryManager` is per-tab.
3. **No persistent storage**: Chat history is in `st.session_state` only. Refreshing the browser tab clears all history.
4. **PBT test speed**: Hypothesis tests write temporary CSV files per example. With `max_examples=100`, DataProcessor PBT tests may take 30–60 seconds to run. This is expected and within the `deadline=5000` per-example budget.
5. **Evaluation adds latency**: Each AI response triggers a second Anthropic API call for evaluation (synchronous). Expect 1–3 seconds of visible spinner after streaming completes.

---

## How to Run

```bash
# 1. Copy environment file
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Run the application
streamlit run app.py

# 4. Run tests
pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=80 \
       --ignore=tests/test_properties.py

# 5. Run PBT tests separately (slower)
pytest tests/test_properties.py -v
```
