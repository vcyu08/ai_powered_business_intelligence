# InsightForge — NFR Requirements

## Summary

InsightForge is a single-user local Streamlit application. Scalability and availability NFRs are N/A. The applicable NFR domains are: Performance, Security, Reliability, Maintainability, and Testing.

---

## Performance Requirements

### NFR-PERF-01: Streaming Response Latency
- **Requirement**: First token of AI response must appear within 10 seconds of query submission
- **Rationale**: Streaming via `st.write_stream()` masks total generation latency; time-to-first-token is the user-perceived wait
- **Implementation**: `ChatAnthropic(streaming=True)` + LCEL chain stream; no buffering before display
- **Measurement**: Visual inspection during testing

### NFR-PERF-02: Chart Render Time
- **Requirement**: All 5 Plotly charts in the sidebar must render within 3 seconds of app startup
- **Rationale**: Charts are static (computed once from pre-loaded CSV); render time should be near-instant
- **Implementation**: Charts rendered synchronously at startup; data pre-computed in `compute_statistics()`

### NFR-PERF-03: Statistics Computation Time
- **Requirement**: `DataProcessor.compute_statistics()` must complete within 5 seconds for the provided `sales_data.csv`
- **Rationale**: Computation runs once at startup via `@st.cache_resource`; acceptable to take a few seconds

---

## Security Requirements

All applicable security rules from the Security Baseline extension are enforced. Rules marked N/A are excluded.

| Rule ID | Requirement | Implementation |
|---|---|---|
| SECURITY-03 | Structured logging — all components use Python `logging` module | `logging.getLogger(__name__)` in each module; WARNING level default |
| SECURITY-05 | Input validation — user query capped at 1,000 characters; empty input rejected | Checked in app.py before LLM call (BR-01, BR-02) |
| SECURITY-09 | Dependency security scan — `pip audit` run before release; no known CVEs in dependencies | Enforced in build instructions |
| SECURITY-10 | Pinned dependency versions — all packages pinned with `==` in requirements.txt | requirements.txt uses exact versions |
| SECURITY-12 | Secrets management — `ANTHROPIC_API_KEY` loaded via `python-dotenv` from `.env` file; never hardcoded | `load_dotenv()` in app.py; `.env` in `.gitignore` |
| SECURITY-15 | Generic error messages — all LLM/API exceptions caught; internal details never shown to user | try/except in `get_response()` and `evaluate()` per BR-13 |

**N/A Rules** (local app with no network exposure, no auth, no database):
- SECURITY-01 (authentication) — no user accounts
- SECURITY-02 (authorization) — single-user
- SECURITY-04 (HTTPS) — local process
- SECURITY-06 (SQL injection) — no database
- SECURITY-07 (XSS) — Streamlit sanitizes output
- SECURITY-08 (CSRF) — no web form submissions
- SECURITY-11 (rate limiting) — local app
- SECURITY-13 (audit logging) — operational concern; N/A for local app
- SECURITY-14 (encryption at rest) — no persistent storage

---

## Reliability Requirements

### NFR-REL-01: LLM Call Timeout (RESILIENCY-10)
- **Requirement**: All Anthropic API calls must have a 60-second timeout
- **Implementation**: `anthropic.Anthropic(timeout=60.0)` for evaluator; `ChatAnthropic(request_timeout=60)` for RAG chain
- **On timeout**: Caught as exception; generic error message shown (BR-13)

### NFR-REL-02: Graceful Startup Failure
- **Requirement**: If CSV load or API key check fails at startup, the app must display a clear error and halt further execution
- **Implementation**: `init_error` in session state; `ErrorBanner` component calls `st.stop()` (BR-11, BR-14)

### NFR-REL-03: Evaluation Failure Tolerance
- **Requirement**: Evaluation failure must not block the main chat interaction
- **Implementation**: `evaluate()` returns `EvaluationResult(score=None, reasoning="Evaluation unavailable")` on any exception (BR-09)

---

## Maintainability Requirements

### NFR-MAINT-01: Python Version
- **Requirement**: Python 3.11 minimum (Q1=B)
- **Rationale**: ~25% faster startup than 3.10; `tomllib` built-in; improved error messages; broadly available

### NFR-MAINT-02: Test Coverage
- **Requirement**: ≥ 80% line coverage measured by `pytest-cov` (Q2=B)
- **Enforcement**: `pytest --cov=. --cov-fail-under=80` in CI/build instructions
- **Scope**: Coverage measured across `data_processor.py`, `rag_system.py`, `memory_manager.py`, `visualizations.py`, `evaluator.py`; Streamlit `app.py` excluded from coverage measurement (UI code not unit-testable without mocking)

### NFR-MAINT-03: Module Isolation
- **Requirement**: Each module (`data_processor.py`, `rag_system.py`, `memory_manager.py`, `visualizations.py`, `evaluator.py`) must be independently importable and testable without running Streamlit
- **Rationale**: Enables isolated unit testing; Streamlit dependency confined to `app.py`

---

## Testing Requirements

### NFR-TEST-01: Unit Tests (pytest)
- **Requirement**: pytest unit tests for all public methods in `DataProcessor`, `MemoryManager`, `QAEvalChain`
- **Framework**: pytest
- **Location**: `tests/test_data_processor.py`, `tests/test_memory_manager.py`, `tests/test_evaluator.py`

### NFR-TEST-02: Property-Based Tests (Hypothesis — PBT-09)
- **Requirement**: Hypothesis PBT tests covering all 11 properties defined in business-logic-model.md (PROP-01 to PROP-11)
- **Framework**: Hypothesis `@given` decorator with appropriate strategies
- **Location**: `tests/test_properties.py`
- **Properties covered**: DataProcessor (PROP-01 to PROP-05), MemoryManager (PROP-06 to PROP-08), BusinessDataRetriever (PROP-09 to PROP-11)

### NFR-TEST-03: RAG Integration Tests
- **Requirement**: Integration tests verifying end-to-end RAG pipeline behavior with real Documents (no mocking of retriever or LLM chain structure)
- **Location**: `tests/test_rag_system.py`
- **Note**: LLM API calls may be mocked in integration tests to avoid API cost and flakiness

---

## Logging Requirements

### NFR-LOG-01: Log Level
- **Requirement**: Default log level is WARNING (Q3=A)
- **Configuration**: `logging.basicConfig(level=logging.WARNING)` in app.py at startup
- **Per-module loggers**: Each module uses `logger = logging.getLogger(__name__)`

### NFR-LOG-02: No Sensitive Data in Logs
- **Requirement**: API keys, user queries, and AI responses must never appear in log output (SECURITY-03)
- **Implementation**: Log only exception type and non-sensitive context; never log `ANTHROPIC_API_KEY` value or full query/response content

---

## N/A Domains (Local Application)

| Domain | Status | Rationale |
|---|---|---|
| Scalability | N/A | Single-user local process; no concurrent users |
| Availability / SLA | N/A | No uptime requirements; local development tool |
| Disaster Recovery | N/A | No persistent data; restart loads fresh from CSV |
| Distributed Systems | N/A | Single process; no microservices |
| Load Balancing | N/A | Single-user |
| RESILIENCY-02 (retry policies) | N/A | Confirmed in Requirements Analysis; local app |
| RESILIENCY-03 (circuit breakers) | N/A | Confirmed in Requirements Analysis; local app |
