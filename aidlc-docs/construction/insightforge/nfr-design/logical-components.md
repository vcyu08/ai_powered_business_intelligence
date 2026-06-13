# InsightForge — Logical Components

## Overview

Logical components are named design elements that implement one or more NFR patterns. They are not necessarily separate Python classes — some map to functions, decorators, or code patterns within existing modules.

| Component | Pattern(s) | Lives In | Type |
|---|---|---|---|
| InputValidator | Guard-Clause Validation (4) | `app.py` | Helper function |
| AppCache | Process-Scoped Singleton (2) | `app.py` | `@st.cache_resource` decorators |
| SessionInitializer | — | `app.py` | Init function |
| TimeoutConfig | Configure-Once Timeout (1) | `rag_system.py`, `evaluator.py` | Constructor parameters |
| ErrorShield | Exception Shield (5) | `rag_system.py`, `evaluator.py`, `app.py` | try/except blocks |
| ModuleLogger | Logger-Per-Module (6) | All modules | `logging.getLogger(__name__)` |
| SystemPrompt | Contextual Grounding (8) | `rag_system.py` | `ChatPromptTemplate` |
| EvaluationInvoker | Sequential Post-Processing (7) | `app.py` | Inline call with `st.spinner` |
| PropertyTestSuite | Generative Property Verification (9) | `tests/test_properties.py` | Hypothesis `@given` functions |

---

## Component Definitions

### InputValidator

**Purpose**: Enforce BR-01 (non-empty) and BR-02 (≤1,000 chars) before any chat history mutation.

**Interface**:
```python
def validate_input(query: str) -> tuple[bool, str | None]:
    """Returns (is_valid, error_message_or_None)."""
```

**Behavior**:
- Strips leading/trailing whitespace before checking
- Returns `(False, "Please enter a question.")` if result is empty
- Returns `(False, "Query too long (N chars). Limit: 1,000 characters.")` if `len(stripped) > 1000`
- Returns `(True, None)` otherwise

**Caller**: `app.py` interaction flow, immediately after `st.chat_input()` yields a value

**Dependencies**: None (pure function)

---

### AppCache

**Purpose**: Ensure DataProcessor and RAGSystem are initialized once per server process (not per page load or per user).

**Interface**:
```python
@st.cache_resource
def get_data_processor() -> DataProcessor: ...

@st.cache_resource
def get_rag_system(dp: DataProcessor) -> RAGSystem: ...
```

**Behavior**:
- On first call: executes the full initialization chain; caches the result
- On subsequent calls: returns the cached object immediately
- If initialization raises: `st.session_state["init_error"]` is set; `ErrorBanner` halts the app

**Scope**: Process-wide. If Streamlit runs with multiple workers, each worker has its own cache.

**Not cached** (per-session instead): `MemoryManager`, `QAEvalChain`, `chat_history`

---

### SessionInitializer

**Purpose**: Ensure per-session state is created exactly once (on first page load per browser tab).

**Interface**:
```python
def init_session() -> None:
    """Idempotent: only initializes keys not already in st.session_state."""
```

**Behavior**:
```python
def init_session():
    if "memory" not in st.session_state:
        st.session_state["memory"] = MemoryManager()
    if "evaluator" not in st.session_state:
        st.session_state["evaluator"] = QAEvalChain()
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
```

**Called**: At the top of `app.py` main execution, after `AppCache` initialization

---

### TimeoutConfig

**Purpose**: Enforce RESILIENCY-10 (60-second LLM call timeout) at client construction, so every call inherits it automatically.

**RAG System configuration** (in `RAGSystem.__init__`):
```python
llm = ChatAnthropic(
    model="claude-opus-4-8",
    streaming=True,
    request_timeout=60,       # ← TimeoutConfig
)
```

**Evaluator configuration** (in `QAEvalChain.__init__`):
```python
import httpx
self._client = anthropic.Anthropic(
    timeout=httpx.Timeout(60.0),   # ← TimeoutConfig
)
```

**Failure pathway**: `httpx.TimeoutException` → caught by ErrorShield → WARNING log + user-facing generic message

---

### ErrorShield

**Purpose**: Prevent raw API exception details from reaching the user (SECURITY-15).

**Two-layer design**:

**Layer 1 — Component shield** (in `QAEvalChain.evaluate()`):
- Catches all exceptions internally
- Returns `EvaluationResult(score=None, reasoning="Evaluation unavailable")`
- Logs: `logger.warning("Evaluation error: %s", type(e).__name__)`
- Never re-raises

**Layer 2 — App shield** (in `app.py` interaction flow):
- Wraps `st.write_stream(rag_system.get_response(...))` in try/except
- On exception: `st.error("An error occurred while processing your request. Please try again.")`
- Logs: `logger.warning("RAG error: %s", type(e).__name__)`
- Returns early without modifying chat history

**What is never logged**: API key values, full user query text, full response text, internal stack traces beyond the exception type name

---

### ModuleLogger

**Purpose**: Structured, traceable logging across all modules (SECURITY-03); WARNING level (Q3=A).

**Setup** (in `app.py`, executed once at startup):
```python
import logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
```

**Per-module declaration** (top of each Python file):
```python
logger = logging.getLogger(__name__)
```

**Module logger names** (resolved from `__name__`):
- `data_processor`
- `rag_system`
- `memory_manager`
- `visualizations`
- `evaluator`

**Log call rules**:
- Log only: exception type, module context, non-sensitive metadata (e.g., document count)
- Never log: `ANTHROPIC_API_KEY`, user query text, LLM response text

---

### SystemPrompt

**Purpose**: Establish business analytics framing that constrains Claude's behavior (Contextual Grounding Pattern).

**Implementation** (in `RAGSystem.__init__`):
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are InsightForge, an AI-powered business intelligence assistant. "
     "Your ONLY role is to analyze sales data and answer business questions "
     "based on the data provided in the context below.\n\n"
     "Context (retrieved sales data):\n{context}\n\n"
     "Answer questions based solely on the provided data. "
     "Do not perform any actions, generate code, or discuss topics "
     "unrelated to the sales data."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])
```

**Variables injected at runtime**:
- `{context}` — concatenated page_content of retrieved Documents
- `{chat_history}` — list of `HumanMessage` / `AIMessage` from `MemoryManager.get_messages()`
- `{question}` — the validated user query

---

### EvaluationInvoker

**Purpose**: Call `QAEvalChain.evaluate()` synchronously after streaming completes, with a spinner for user feedback (Q2=A).

**Interface**: Not a class — an inline code block in `app.py`.

**Implementation**:
```python
# After streaming:
response_text = st.write_stream(rag_system.get_response(query, history))

# Synchronous evaluation with spinner:
with st.spinner("Evaluating response quality..."):
    evaluation = st.session_state["evaluator"].evaluate(query, response_text)

render_evaluation(evaluation)
```

**Sequencing**: Evaluation always runs after streaming, before `memory.add_interaction()` and before appending to `chat_history`.

---

### PropertyTestSuite

**Purpose**: Verify all 11 PBT properties (PROP-01 to PROP-11) using Hypothesis generative testing.

**Location**: `tests/test_properties.py`

**Strategy map**:
| PROP | Target | Hypothesis Strategy |
|---|---|---|
| PROP-01 to PROP-05 | `DataProcessor.compute_statistics()` | `st.lists(st.floats(...))` for Sales; `st.sampled_from(...)` for Products/Regions |
| PROP-06 to PROP-08 | `MemoryManager.add_interaction()` | `st.lists(st.text(...))` for message sequences |
| PROP-09 to PROP-11 | `BusinessDataRetriever._get_relevant_documents()` | `st.text(...)` for query strings |

**Settings**: `@settings(max_examples=100, deadline=5000)` — 100 examples per property; 5-second per-test deadline

---

## Component Interaction Diagram

```
Startup:
  AppCache.get_data_processor() → DataProcessor (cached)
  AppCache.get_rag_system()      → RAGSystem (cached)
  SessionInitializer.init_session() → MemoryManager, QAEvalChain, chat_history (session)

Interaction flow:
  ChatInputBar
      ↓
  InputValidator.validate_input()
      ↓ valid
  ModuleLogger (app.py) ← logs WARNING events only
      ↓
  ErrorShield (Layer 2 — app.py try/except)
      ↓
  RAGSystem.get_response()  ←  TimeoutConfig (60s)
      ↓ stream
  st.write_stream()  →  response_text
      ↓
  EvaluationInvoker
      ↓
  QAEvalChain.evaluate()  ←  TimeoutConfig (60s)
                           ←  ErrorShield (Layer 1 — returns safe default)
      ↓
  render_evaluation(evaluation)
      ↓
  MemoryManager.add_interaction()
      ↓
  chat_history.append(entry)
```
