# InsightForge — NFR Design Patterns

## Pattern Catalogue

Nine design patterns cover all applicable NFR requirements. Scalability and Availability patterns are N/A (local single-user app).

---

## 1. Configure-Once Timeout Pattern
**Addresses**: RESILIENCY-10 (60-second timeout on all LLM API calls)

**Problem**: Unresponsive Anthropic API calls would block the Streamlit UI indefinitely.

**Solution**: Configure timeout at client construction time so every call inherits it automatically; no per-call wrapping needed.

**Design**:
```
Evaluator:     anthropic.Anthropic(timeout=httpx.Timeout(60.0))
               → applies to all messages.create() calls on this client

RAG chain:     ChatAnthropic(model="claude-opus-4-8", streaming=True, request_timeout=60)
               → applies to all chain.stream() / chain.invoke() calls
```

**Failure mode**: `httpx.TimeoutException` → caught by Error Shield Pattern (Pattern 5) → generic user message shown.

---

## 2. Process-Scoped Singleton Pattern
**Addresses**: NFR-PERF-02, NFR-PERF-03 (charts render in ≤3s; stats computed in ≤5s at startup)

**Problem**: `DataProcessor.load_data()`, `compute_statistics()`, and `RAGSystem.__init__()` are expensive. Running them on every Streamlit page rerender would be unacceptable.

**Solution**: Wrap initialization functions with `@st.cache_resource`. Streamlit calls these functions once per server process and caches the result; all page rerenders and all browser tabs share the same instance.

**Design**:
```
@st.cache_resource
def get_data_processor() -> DataProcessor:
    dp = DataProcessor("sales_data.csv")
    dp.load_data()
    dp.compute_statistics()
    return dp

@st.cache_resource
def get_rag_system(dp: DataProcessor) -> RAGSystem:
    docs = dp.create_documents()
    return RAGSystem(docs)
```

**Scope boundary**: `MemoryManager` and `QAEvalChain` are NOT cached this way — they are per-session (per browser tab) and live in `st.session_state`.

---

## 3. Streaming Delivery Pattern
**Addresses**: NFR-PERF-01 (first token ≤ 10 seconds)

**Problem**: Full LLM response generation can take 10–30 seconds. Waiting for the complete response before displaying anything creates a poor user experience.

**Solution**: Use LCEL `chain.stream()` to receive tokens incrementally; use `st.write_stream()` to push each token to the browser as it arrives.

**Design**:
```
# In app.py interaction flow:
with st.chat_message("assistant"):
    response_text = st.write_stream(
        rag_system.get_response(query, chat_history)
    )
    # st.write_stream() consumes the generator and returns the full assembled string
```

**Timeout interaction**: The `request_timeout=60` configured in Pattern 1 governs the initial connection; mid-stream token delivery is not subject to a per-chunk timeout (acceptable for this app).

---

## 4. Guard-Clause Validation Pattern
**Addresses**: SECURITY-05, BR-01, BR-02 (input validation); Q1=A (validate before displaying)

**Problem**: Invalid queries (empty or over-length) must be rejected without polluting the chat history.

**Solution**: Validate input at the entry point before any chat history mutation. Return early with a warning if invalid; the chat history is never modified for rejected inputs.

**Design**:
```
def validate_input(query: str) -> tuple[bool, str | None]:
    query = query.strip()
    if not query:
        return False, "Please enter a question."
    if len(query) > 1000:
        return False, f"Query too long ({len(query)} chars). Limit: 1,000 characters."
    return True, None

# In interaction flow:
is_valid, error_msg = validate_input(user_input)
if not is_valid:
    st.warning(error_msg)
    return          # ← guard clause: exit before any chat_history mutation
```

**Pattern**: Validate → fail fast → no side effects. Chat history remains clean.

---

## 5. Exception Shield Pattern
**Addresses**: SECURITY-15, BR-13 (generic error messages); BR-09 (evaluation failure tolerance)

**Problem**: Raw exception messages from the Anthropic API may expose internal details (model names, endpoint URLs, error codes) that should not reach the user.

**Solution**: Each public method that makes external API calls wraps its implementation in try/except. Exceptions are logged at WARNING level (no sensitive data); a safe default is returned to the caller.

**Design**:
```
# In RAGSystem.get_response():
def get_response(self, query: str, chat_history: list) -> Generator[str, None, None]:
    try:
        yield from self._chain_stream(query, chat_history)
    except Exception as e:
        logger.warning("RAG chain error: %s", type(e).__name__)
        raise   # re-raise so app.py can display the generic error

# In app.py:
try:
    response_text = st.write_stream(rag_system.get_response(query, history))
except Exception:
    st.error("An error occurred while processing your request. Please try again.")
    return

# In QAEvalChain.evaluate():
def evaluate(self, question: str, answer: str) -> EvaluationResult:
    try:
        ...
        return EvaluationResult(score=score, reasoning=reasoning)
    except Exception as e:
        logger.warning("Evaluation error: %s", type(e).__name__)
        return EvaluationResult(score=None, reasoning="Evaluation unavailable")
```

**Hierarchy**: Evaluator shields itself (returns safe default). RAG chain logs and re-raises (app.py shows generic message).

---

## 6. Logger-Per-Module Pattern
**Addresses**: SECURITY-03, NFR-LOG-01, NFR-LOG-02

**Problem**: Centralized logging configuration is hard to trace by module; ad-hoc `print()` statements leak sensitive data and lack timestamps.

**Solution**: One `logging.Logger` instance per Python module, named by `__name__`. Root logger configured once at WARNING level in `app.py`.

**Design**:
```
# app.py (once at module top):
import logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(name)s %(levelname)s %(message)s"
)

# Every other module:
logger = logging.getLogger(__name__)   # e.g., "data_processor", "rag_system"

# Usage:
logger.warning("DataProcessor load failed: %s", type(e).__name__)
#              ↑ never log: API key, query text, response text
```

---

## 7. Sequential Post-Processing Pattern
**Addresses**: Q2=A (synchronous evaluation); NFR-TEST-01 (testability)

**Problem**: Evaluation could be async for lower latency, but threading in Streamlit is error-prone and evaluation failures are non-fatal.

**Solution**: Call `evaluate()` synchronously after `st.write_stream()` completes. The evaluation call is fast (≈1–3 seconds) and the blocking is acceptable given the chat context. Simplicity outweighs the minor latency reduction of threading.

**Design**:
```
# After streaming:
response_text = st.write_stream(rag_system.get_response(query, history))

# Synchronous evaluation (no thread):
with st.spinner("Evaluating response..."):
    evaluation = evaluator.evaluate(query, response_text)

render_evaluation(evaluation)
```

---

## 8. Contextual Grounding Pattern
**Addresses**: Q3=A (prompt injection defense); SECURITY-05

**Problem**: User queries are embedded in the LLM prompt. A malicious user could attempt to override the system prompt.

**Solution**: Write a tightly-scoped system prompt that establishes the business analytics context as an inviolable frame. Rely on Claude's built-in safety mechanisms for injection resistance. No keyword blocklist is added (Q3=A).

**Design** (system prompt skeleton):
```
You are InsightForge, an AI-powered business intelligence assistant.
Your ONLY role is to analyze sales data and answer business questions
about the data provided in the context below.

Context (retrieved sales data):
{context}

Conversation history:
{chat_history}

Answer the following business question based solely on the context above.
Do not perform any actions, generate code, or discuss topics unrelated to
the provided sales data.
```

**Rationale**: The system prompt's explicit role constraint + Claude's safety training provides adequate injection resistance for a single-user local prototype.

---

## 9. Generative Property Verification Pattern
**Addresses**: PBT extension — PBT-01 (11 identified properties), PBT-09 (Hypothesis framework)

**Problem**: Unit tests with fixed examples cannot verify invariants across the full input space; bugs emerge in edge cases not thought of during test authoring.

**Solution**: Express business-logic invariants as universally quantified properties using Hypothesis `@given` strategies. Each property from business-logic-model.md (PROP-01 to PROP-11) maps to a Hypothesis test.

**Design** (example):
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@given(
    sales=st.lists(st.floats(min_value=0.01, max_value=1e6), min_size=1),
    products=st.lists(st.sampled_from(["Widget A","Widget B","Widget C","Widget D"]), min_size=1)
)
def test_total_sales_accuracy(sales, products):
    # PROP-01: total_sales == df['Sales'].sum()
    df = make_test_df(sales=sales, products=products)
    stats = DataProcessor._compute_from_df(df)
    assert abs(stats["total_sales"] - sum(sales)) < 1e-6
```

**Coverage target**: All 11 PBT properties (PROP-01 to PROP-11) across DataProcessor, MemoryManager, and BusinessDataRetriever.

---

## Extension Compliance Summary

| Extension Rule | Status | Rationale |
|---|---|---|
| SECURITY-03 | ✅ Compliant | Logger-Per-Module Pattern (Pattern 6) |
| SECURITY-05 | ✅ Compliant | Guard-Clause Validation Pattern (Pattern 4) |
| SECURITY-09 | N/A at design stage | Enforced in Build and Test stage |
| SECURITY-10 | N/A at design stage | Enforced in Code Generation stage |
| SECURITY-12 | N/A at design stage | Enforced in Code Generation stage |
| SECURITY-15 | ✅ Compliant | Exception Shield Pattern (Pattern 5) |
| PBT-01 | ✅ Compliant | 11 properties identified (Functional Design); Pattern 9 maps them |
| PBT-09 | ✅ Compliant | Hypothesis framework selected; Pattern 9 |
| RESILIENCY-10 | ✅ Compliant | Configure-Once Timeout Pattern (Pattern 1) |
| RESILIENCY-02 | N/A | Confirmed in Requirements Analysis; local app |
| RESILIENCY-03 | N/A | Confirmed in Requirements Analysis; local app |
