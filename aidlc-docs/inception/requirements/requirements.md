# InsightForge — Requirements Document

## Intent Analysis

| Field | Value |
|---|---|
| **User Request** | Build an AI-Powered Business Intelligence Assistant following the Capstone PDF |
| **Request Type** | New Project (Greenfield) |
| **Scope Estimate** | Single application — multiple components (data processor, RAG system, memory, visualizations, evaluator, UI) |
| **Complexity Estimate** | Moderate-to-Complex — multi-component LLM application with RAG pipeline, custom retriever, conversation memory, evaluation, and Streamlit UI |
| **Primary Technology** | Python, LangChain, Anthropic Claude API, Streamlit, pandas, Plotly |

---

## Functional Requirements

### FR-01: Data Preparation (Step 1)
The system SHALL load `sales_data.csv` and compute comprehensive statistics covering:
- Sales by time period (daily, monthly, quarterly, yearly)
- Sales by product
- Sales by region
- Customer segmentation by age group and gender
- Statistical measures: mean, median, standard deviation, min, max
- Customer satisfaction averages by product and region

### FR-02: Knowledge Base Creation (Step 2)
The system SHALL organize computed statistics into LangChain `Document` objects structured as a retrieval-ready knowledge base with the following categories:
- `overview` — overall business metrics
- `time_series` — temporal sales data
- `product` — product performance
- `regional` — regional analysis
- `demographics` — customer segmentation

### FR-03: Custom RAG Retriever (Step 3 — RAG Integration)
The system SHALL implement a custom LangChain `BaseRetriever` subclass that:
- Accepts a natural language query
- Maps keywords to relevant document categories
- Returns relevant `Document` objects to the LLM chain
- Always includes the overview document for grounding

### FR-04: LLM Application with Prompt Engineering (Steps 3 & 4)
The system SHALL build a LangChain LCEL chain that:
- Uses `claude-opus-4-8` as the LLM via `langchain-anthropic`
- Uses a system prompt that instructs the LLM to act as InsightForge BI Assistant
- Injects retrieved context into the system prompt
- Supports conversation history injection (step 6)
- Uses `StrOutputParser` for string output
- Supports both `.invoke()` and `.stream()` for real-time streaming in the UI

### FR-05: RAG System (Step 5)
The system SHALL integrate the custom retriever with the LLM chain using LangChain LCEL (`RunnablePassthrough.assign`) so that for every query:
1. The retriever fetches relevant documents
2. Documents are formatted and injected as context
3. The LLM generates a response grounded in the data

### FR-06: Conversation Memory (Step 6)
The system SHALL maintain a `MemoryManager` that:
- Stores `HumanMessage` and `AIMessage` objects (LangChain message types)
- Passes history to the chain on each query
- Enforces a configurable maximum history window (default: 10 exchanges)
- Provides a method to clear history
- Persists within a Streamlit session via `st.session_state`

### FR-07: Model Evaluation — QAEvalChain (Step 7)
The system SHALL implement a `QAEvalChain` class that:
- Mirrors the LangChain `QAEvalChain` API (`from_llm()`, `evaluate(examples, predictions)`)
- Uses `claude-opus-4-8` via the Anthropic SDK to score each Q&A pair
- Scores responses on: relevance, clarity, specificity, actionability (0–10 each)
- Computes an overall average score
- Returns a summary with count, mean, min, max scores
- Ships with **5 pre-built test cases** covering: total revenue, product performance, regional comparison, satisfaction analysis, demographic segmentation

### FR-08: Data Visualizations (Step 7)
The system SHALL provide the following Plotly visualizations:
1. **Sales Trends Over Time** — monthly line chart with data point markers
2. **Product Performance** — horizontal bar charts for total sales and avg satisfaction
3. **Regional Analysis** — donut pie chart (revenue share) + bar chart (avg transaction)
4. **Customer Demographics** — 2×2 subplot grid: sales by gender, sales by age group, age histogram, satisfaction vs sales scatter
5. **Quarterly Heatmap** — product × quarter sales heatmap

### FR-09: Streamlit UI (Step 7)
The system SHALL provide a Streamlit application (`app.py`) with:
- **Chat Assistant page** — streaming chat interface with suggestion buttons, conversation history display, and clear history control
- **Visualizations page** — tabbed interface for all 5 chart types with supporting data tables
- **Model Evaluation page** — batch evaluation runner with per-test-case result display and summary metrics
- **Data Overview page** — raw dataset sample, statistical summary, and knowledge base summary
- **Sidebar** — navigation, live key metrics (total revenue, transactions, satisfaction, top product/region), and clear chat button

---

## Non-Functional Requirements

### NFR-01: LLM Model
The application SHALL use `claude-opus-4-8` as the default Claude model via `langchain-anthropic.ChatAnthropic` for the RAG chain and directly via `anthropic.Anthropic` for evaluation.

### NFR-02: API Key Management (SECURITY-12 applicable)
- The Anthropic API key SHALL be loaded from environment variable `ANTHROPIC_API_KEY`
- The application SHALL use `python-dotenv` to load a `.env` file
- No API key SHALL be hardcoded in source code
- The application SHALL display a clear error and stop if the key is missing

### NFR-03: Python Environment
- Package manager: `pip` with a pinned `requirements.txt` (exact versions)
- All dependencies SHALL use exact version specifiers (e.g., `==x.y.z`) to comply with SECURITY-10 (supply chain security)
- Python 3.10+ required

### NFR-04: Unit Testing
- Framework: `pytest` + `hypothesis` (for property-based tests per PBT-09)
- Unit tests SHALL be provided for: `DataProcessor`, `BusinessDataRetriever`, `MemoryManager`, `QAEvalChain`
- Property-based tests SHALL be provided for data transformation invariants (per PBT-01 through PBT-03)

### NFR-05: Visualization Library
- Primary: Plotly (interactive, native Streamlit integration)
- All charts SHALL use `use_container_width=True` for responsive layout

### NFR-06: Structured Logging (SECURITY-03 applicable)
- The application SHALL use Python's `logging` module with structured output
- Log entries SHALL include: timestamp, module, log level, and message
- No secrets, API keys, or PII SHALL be logged

### NFR-07: Input Validation (SECURITY-05 applicable)
- User chat input SHALL have a maximum length enforced before being sent to the LLM
- Input SHALL be stripped of leading/trailing whitespace
- Empty queries SHALL be rejected with user feedback

### NFR-08: Exception Handling (SECURITY-15 applicable)
- All Anthropic API calls SHALL be wrapped in try/except blocks
- User-visible error messages SHALL be generic (no stack traces displayed to users)
- The application SHALL have a global error boundary at the Streamlit entry point
- API timeouts SHALL be handled gracefully with a user-friendly message

### NFR-09: Supply Chain Security (SECURITY-10 applicable)
- `requirements.txt` SHALL pin all dependencies to exact versions
- A `requirements.txt` with pinned versions SHALL be committed to version control

### NFR-10: Resiliency (mostly N/A — local application)
- RESILIENCY-02: **N/A** — Local development/educational deployment; no DR strategy required
- RESILIENCY-03: **N/A** — Exempt from formal change management (educational project)
- RESILIENCY-10 (timeouts): **Applicable** — All Anthropic API calls SHALL have explicit `timeout` parameters set
- All other RESILIENCY rules: **N/A** — Local single-machine deployment

---

## Security Compliance Scope (Requirements Stage)

| Rule | Status | Rationale |
|---|---|---|
| SECURITY-01 | N/A | No external data stores; data is a local CSV file |
| SECURITY-02 | N/A | No load balancers, API gateways, or CDN |
| SECURITY-03 | Applicable | Structured logging required in all components |
| SECURITY-04 | N/A | HTTP headers managed by Streamlit framework |
| SECURITY-05 | Applicable | User chat input must be validated before LLM call |
| SECURITY-06 | N/A | No IAM roles or cloud access policies |
| SECURITY-07 | N/A | No cloud network configuration |
| SECURITY-08 | N/A | No user authentication required for local app |
| SECURITY-09 | Applicable | No hardcoded secrets; generic error responses |
| SECURITY-10 | Applicable | Pinned dependencies in requirements.txt |
| SECURITY-11 | N/A | No public-facing rate-limited endpoints |
| SECURITY-12 | Applicable | API key via .env; no hardcoded credentials |
| SECURITY-13 | N/A | No CDN or untrusted deserialization |
| SECURITY-14 | N/A | No centralized log service for local app |
| SECURITY-15 | Applicable | All API calls wrapped; generic user-facing errors |

---

## PBT Compliance Scope (Requirements Stage)

| Rule | Status | Rationale |
|---|---|---|
| PBT-01 | Applicable | Property identification required in Functional Design |
| PBT-02 | Applicable | Data processing has serialization/parsing operations |
| PBT-03 | Applicable | Statistics computation has size/value invariants |
| PBT-04 | N/A | No explicitly idempotent API operations |
| PBT-05 | Applicable | Custom retriever can be verified against brute-force scan |
| PBT-06 | Applicable | MemoryManager is stateful |
| PBT-07 | Applicable | Domain generators needed for sales data records |
| PBT-08 | Applicable | Hypothesis provides shrinking and seed-based reproducibility |
| PBT-09 | Applicable | Hypothesis selected as PBT framework for Python |
| PBT-10 | Applicable | PBT complements, does not replace, example-based tests |

---

## Key Deliverables

1. `data_processor.py` — data loading, statistics, knowledge base creation
2. `rag_system.py` — LangChain LCEL chain, custom retriever, prompt engineering
3. `memory_manager.py` — conversation history management
4. `visualizations.py` — Plotly chart functions
5. `evaluator.py` — QAEvalChain model evaluation
6. `app.py` — Streamlit UI application
7. `requirements.txt` — pinned dependencies
8. `.env.example` — API key template
9. `tests/` — pytest + Hypothesis test suite

---

## Success Criteria

- Chat assistant answers natural language questions about the sales dataset using RAG
- Conversation history is maintained across multiple exchanges in a session
- All 5 visualization types render correctly in the Streamlit UI
- QAEvalChain evaluation runs successfully against 5 test cases and shows per-question scores
- No API keys appear in source code
- All applicable SECURITY and PBT rules are satisfied in generated code
