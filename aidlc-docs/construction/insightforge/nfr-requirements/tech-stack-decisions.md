# InsightForge — Tech Stack Decisions

## Decision Summary

| Layer | Technology | Version | Decision Basis |
|---|---|---|---|
| Language | Python | ≥ 3.11 | Q1=B; performance + error messages |
| UI Framework | Streamlit | ≥ 1.40.0 | Requirements (FR-01 to FR-09); capstone spec |
| LLM Orchestration | LangChain Core | ≥ 0.3.0 | Capstone spec; LCEL chain requirement |
| LLM Provider | langchain-anthropic | ≥ 0.3.0 | Capstone spec; `ChatAnthropic` wrapper |
| LLM Model | claude-opus-4-8 | — | Q1=A in Requirements (model selection) |
| Direct SDK | anthropic | ≥ 0.42.0 | Evaluator component (Q3=B in App Design) |
| Data Processing | pandas | ≥ 2.2.0 | Capstone spec; tabular data + groupby |
| Visualization | plotly | ≥ 5.24.0 | Q5=A in Requirements (visualization library) |
| Env Vars | python-dotenv | ≥ 1.0.0 | SECURITY-12; API key via .env file |
| Unit Testing | pytest | ≥ 8.3.0 | Q4=A in Requirements |
| Coverage | pytest-cov | ≥ 5.0.0 | Q2=B (≥80% enforcement) |
| PBT Framework | hypothesis | ≥ 6.115.0 | PBT-09 selected; PROP-01 to PROP-11 |

---

## Detailed Decisions

### Python 3.11+ (Q1=B)

**Decision**: Python 3.11 is the minimum supported version.

**Rationale**:
- ~25% faster CPython interpreter than 3.10 (measured startup and per-call overhead)
- Better exception tracebacks with improved error messages
- `tomllib` built-in (no extra dependency for config parsing)
- Available on all major platforms; conda and pyenv support excellent

**Constraints**:
- `match/case` statements (3.10+) may be used in evaluator response parsing
- `datetime.fromisoformat()` extended format support (3.11+) used in date parsing

---

### Streamlit ≥ 1.40.0

**Decision**: Streamlit is the UI layer with wide layout enabled.

**Rationale**: Capstone specification explicitly requires Streamlit. Version 1.40.0+ required for:
- `st.write_stream()` — streaming token display (FR-02 streaming requirement)
- `st.chat_message()` / `st.chat_input()` — native chat UI components
- Stable `@st.cache_resource` API for per-process caching

---

### LangChain Core ≥ 0.3.0 + langchain-anthropic ≥ 0.3.0

**Decision**: Use LangChain's LCEL (LangChain Expression Language) for the RAG pipeline.

**Rationale**: Capstone specification explicitly requires LangChain. LCEL components used:
- `BaseRetriever` — custom `BusinessDataRetriever` base class
- `ChatPromptTemplate` + `MessagesPlaceholder` — prompt with history injection
- `RunnablePassthrough.assign` — context injection into chain
- `StrOutputParser` — stream-friendly text extraction
- `ChatAnthropic` — Claude integration with streaming support

**Note**: `langchain-community` is NOT included — only `langchain-core` and `langchain-anthropic`. This keeps the dependency footprint minimal (SECURITY-10).

---

### anthropic SDK ≥ 0.42.0 (Direct)

**Decision**: `QAEvalChain` uses the Anthropic Python SDK directly (not via LangChain wrapper).

**Rationale**: Application Design Q3=B — evaluator always uses Anthropic SDK directly. This:
- Avoids LangChain dependency in the evaluator module
- Gives direct access to structured `messages.create()` API
- Simplifies JSON response parsing
- Maintains clean separation between evaluation and RAG chain

---

### pandas ≥ 2.2.0

**Decision**: pandas for all tabular data operations.

**Rationale**: Capstone specification requires pandas. Version 2.2.0+ required for:
- `DataFrame.resample()` stability with `ME` (month-end) frequency alias
- Copy-on-write mode (performance improvement for groupby operations)
- Stable `pd.cut()` behavior for age group binning

---

### plotly ≥ 5.24.0

**Decision**: Plotly for interactive charts in Streamlit sidebar.

**Rationale**: Q5=A in Requirements Analysis selected Plotly. Streamlit's `st.plotly_chart()` renders Plotly figures natively with zoom, pan, and hover tooltips. Chart types used:
- `plotly.express.line` — sales trend
- `plotly.express.bar` — product breakdown, region comparison, age groups
- `plotly.express.imshow` — satisfaction heatmap

---

### python-dotenv ≥ 1.0.0

**Decision**: API key loaded via `.env` file at startup.

**Rationale**: SECURITY-12 compliance. `load_dotenv()` called once in `app.py` before any component initialization. `.env` file must be listed in `.gitignore`.

---

### pytest ≥ 8.3.0 + pytest-cov ≥ 5.0.0

**Decision**: pytest as the unit test runner; pytest-cov for coverage enforcement.

**Rationale**: Industry standard; Q4=A in Requirements selected unit tests. pytest-cov integrates with `--cov-fail-under=80` to enforce the Q2=B threshold.

**Test run command**: `pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=80`

**Coverage exclusions** (in `.coveragerc` or `pyproject.toml`):
```
[coverage:run]
omit = app.py, tests/*
```

---

### hypothesis ≥ 6.115.0

**Decision**: Hypothesis for property-based testing (PBT-09).

**Rationale**: PBT extension selected at Full enforcement. Hypothesis `@given` strategy with `st.dataframes()` from hypothesis-pandas or manual strategies to test PROP-01 to PROP-11.

**Key strategies**:
- `st.floats(min_value=0.0, max_value=1e9)` — Sales values
- `st.sampled_from(["Widget A","Widget B","Widget C","Widget D"])` — Products
- `st.sampled_from(["North","South","East","West"])` — Regions
- `st.text(min_size=1, max_size=1000)` — User query inputs

---

## Dependencies NOT Included

| Package | Reason Excluded |
|---|---|
| `langchain-community` | Not needed; no community retrievers or tools used |
| `faiss-cpu` / `chromadb` | Not needed; custom in-memory retriever replaces vector store |
| `openai` | Not needed; Claude-only application |
| `flask` / `fastapi` | Not needed; Streamlit handles the web layer |
| `pydantic` (direct) | Pulled in transitively by LangChain; not directly imported |
| `celery` / `redis` | Not needed; no background task queue |
| `sqlalchemy` | Not needed; no database persistence |

---

## requirements.txt Strategy (SECURITY-10)

All production dependencies pinned with `==` (exact versions):

```
streamlit==<version>
langchain-core==<version>
langchain-anthropic==<version>
anthropic==<version>
pandas==<version>
plotly==<version>
python-dotenv==<version>
```

Development/test dependencies in a separate `requirements-dev.txt`:

```
pytest==<version>
pytest-cov==<version>
hypothesis==<version>
```

Exact version strings determined at Code Generation stage via `pip install` + `pip freeze`.
