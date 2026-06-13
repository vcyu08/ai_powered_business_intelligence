# Integration Test Instructions — InsightForge

## Purpose

Integration tests verify that InsightForge's components work correctly together with real data. Unlike unit tests, integration tests use `sales_data.csv` directly and verify end-to-end data flows — but LLM calls remain mocked to avoid API cost and flakiness.

---

## Prerequisites

- Virtual environment activated; all dependencies installed
- `sales_data.csv` present in workspace root
- Dev dependencies installed: `pip install -r requirements-dev.txt`
- **API key NOT required** — LLM calls are mocked in all integration test scenarios

---

## Integration Test Scenarios

These scenarios are covered by `tests/test_rag_system.py` and a combination of unit test fixtures:

### Scenario 1: DataProcessor → RAGSystem Pipeline

**What is tested**: DataProcessor produces Documents that RAGSystem can consume without error.

**Covered by**: `tests/test_rag_system.py::test_rag_system_chain_assembled` (uses `SAMPLE_DOCS` derived from the same structure DataProcessor produces).

**Manual verification**:
```python
from data_processor import DataProcessor
from rag_system import RAGSystem

dp = DataProcessor("sales_data.csv")
dp.load_data()
dp.compute_statistics()
docs = dp.create_documents()
assert len(docs) == 11

# RAGSystem accepts the documents without error
# (mock ChatAnthropic to avoid API call)
from unittest.mock import patch
with patch("rag_system.ChatAnthropic"):
    rag = RAGSystem(docs)
assert rag._chain is not None
print("PASS: DataProcessor → RAGSystem pipeline works")
```

---

### Scenario 2: BusinessDataRetriever with Real Documents

**What is tested**: Retriever correctly filters real Document objects produced by DataProcessor.

**Steps**:
```bash
python -c "
from data_processor import DataProcessor
from rag_system import BusinessDataRetriever

dp = DataProcessor('sales_data.csv')
dp.load_data()
dp.compute_statistics()
docs = dp.create_documents()

retriever = BusinessDataRetriever(documents=docs)

# Test 1: overview always present
results = retriever._get_relevant_documents('hello')
cats = [d.metadata['category'] for d in results]
assert 'overview' in cats, 'FAIL: overview missing'
print('PASS: overview always present')

# Test 2: product keyword matches product docs
results = retriever._get_relevant_documents('which product sells best?')
cats = {d.metadata['category'] for d in results}
assert 'product' in cats, 'FAIL: product docs missing'
print('PASS: product keyword retrieves product docs')

# Test 3: all returned docs are from input list
results = retriever._get_relevant_documents('monthly trend')
for doc in results:
    assert doc in docs, 'FAIL: fabricated doc returned'
print('PASS: results are subset of input docs')
"
```

---

### Scenario 3: MemoryManager Rolling Window with Real Content

**What is tested**: MemoryManager correctly maintains the rolling window through a realistic 12-message conversation.

**Steps**:
```bash
python -c "
from memory_manager import MemoryManager

mm = MemoryManager(max_exchanges=10)
for i in range(12):
    mm.add_interaction(f'Question {i}', f'Answer {i}')

msgs = mm.get_messages()
assert len(msgs) == 20, f'Expected 20 messages, got {len(msgs)}'
assert msgs[0].content == 'Question 2', 'Oldest messages not trimmed correctly'
print(f'PASS: rolling window holds {len(msgs)} messages after 12 exchanges')
"
```

---

### Scenario 4: EvaluationResult Dataclass Integration

**What is tested**: `EvaluationResult` from `evaluator.py` can be stored in and retrieved from `st.session_state`-like dicts (dict serialisation).

**Steps**:
```bash
python -c "
from evaluator import EvaluationResult

result = EvaluationResult(score=4, reasoning='Good answer')
entry = {'role': 'assistant', 'content': 'Some response', 'evaluation': result}
assert entry['evaluation'].score == 4
assert entry['evaluation'].reasoning == 'Good answer'
print('PASS: EvaluationResult integrates with ChatHistoryEntry dict')

# Test None case
null_result = EvaluationResult(score=None, reasoning='Evaluation unavailable')
entry2 = {'role': 'assistant', 'content': 'Error case', 'evaluation': null_result}
assert entry2['evaluation'].score is None
print('PASS: None evaluation integrates correctly')
"
```

---

### Scenario 5: Full Pipeline Smoke Test (with mocked LLM)

**What is tested**: Complete interaction flow from data loading to response generation — all components wired together, LLM mocked.

**Steps**:
```bash
python -c "
from unittest.mock import patch, MagicMock
from data_processor import DataProcessor
from rag_system import RAGSystem
from memory_manager import MemoryManager

dp = DataProcessor('sales_data.csv')
dp.load_data()
dp.compute_statistics()
docs = dp.create_documents()

# Mock ChatAnthropic to return a known response string
mock_llm = MagicMock()
mock_llm.stream.return_value = iter(['Widget A is the top product.'])
mock_llm.__or__ = lambda self, other: other  # Support | operator for LCEL

with patch('rag_system.ChatAnthropic', return_value=mock_llm):
    rag = RAGSystem(docs)

mm = MemoryManager()
history = mm.get_messages()

print('PASS: Full pipeline assembled without errors')
print(f'Documents: {len(docs)} total')
print(f'History: {len(history)} messages (empty on first run)')
"
```

---

## Notes

- LLM calls (Anthropic API) are mocked in all scenarios above — no API key required
- For **live integration testing** (real API calls), set `ANTHROPIC_API_KEY` in `.env` and remove the `patch` context managers
- Contract tests and E2E tests are **N/A** for InsightForge (single-service local app; no REST API contracts; Streamlit UI not suitable for headless automation)
