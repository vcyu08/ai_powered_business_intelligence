# Unit Test Execution — InsightForge

## Overview

| Test File | Module Tested | Tests | Mocks LLM? |
|---|---|---|---|
| `tests/test_data_processor.py` | `DataProcessor` | 9 | No |
| `tests/test_memory_manager.py` | `MemoryManager` | 6 | No |
| `tests/test_evaluator.py` | `QAEvalChain` | 5 | Yes — `anthropic.Anthropic` |
| `tests/test_rag_system.py` | `BusinessDataRetriever`, `RAGSystem` | 5 | Yes — `ChatAnthropic` |

Total unit tests: **25**. No real API calls are made during unit test execution.

---

## Prerequisites

- Virtual environment activated (see `build-instructions.md`)
- Dev dependencies installed: `pip install -r requirements-dev.txt`
- Working directory: workspace root (`ai_powered_business_intelligence/`)
- `sales_data.csv` present (required by `test_data_processor.py` fixtures via `tmp_path`)

**Note**: Unit tests do NOT require `ANTHROPIC_API_KEY` — all LLM calls are mocked.

---

## Run All Unit Tests with Coverage

```bash
pytest tests/test_data_processor.py tests/test_memory_manager.py tests/test_evaluator.py tests/test_rag_system.py \
  --cov=. \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  --cov-omit="app.py,tests/*" \
  -v
```

**Expected output**:
```
tests/test_data_processor.py ..........  [ 40%]
tests/test_memory_manager.py ......     [ 64%]
tests/test_evaluator.py .....           [ 84%]
tests/test_rag_system.py .....          [100%]

---------- coverage: platform ... ----------
Name                   Stmts   Miss  Cover
------------------------------------------
data_processor.py         XX     XX    XX%
evaluator.py              XX     XX    XX%
memory_manager.py         XX     XX    XX%
rag_system.py             XX     XX    XX%
visualizations.py         XX     XX    XX%
------------------------------------------
TOTAL                     XX     XX    XX%

25 passed in X.XXs
```

**Pass criteria**: 25 tests pass, 0 failures, coverage ≥ 80%.

---

## Run Individual Test Files

```bash
# DataProcessor only
pytest tests/test_data_processor.py -v

# MemoryManager only
pytest tests/test_memory_manager.py -v

# Evaluator only
pytest tests/test_evaluator.py -v

# RAG system only
pytest tests/test_rag_system.py -v
```

---

## Run Property-Based Tests (Hypothesis)

Property-based tests are in a separate file and take longer to run (100 examples × 11 properties).

```bash
pytest tests/test_properties.py -v --timeout=300
```

**Expected output**:
```
tests/test_properties.py::test_prop_01_total_sales_accuracy PASSED
tests/test_properties.py::test_prop_02_record_count_accuracy PASSED
tests/test_properties.py::test_prop_03_top_product_validity PASSED
tests/test_properties.py::test_prop_04_top_region_validity PASSED
tests/test_properties.py::test_prop_05_avg_sales_bounds PASSED
tests/test_properties.py::test_prop_06_exchange_count_growth PASSED
tests/test_properties.py::test_prop_07_rolling_window_cap PASSED
tests/test_properties.py::test_prop_08_message_alternation PASSED
tests/test_properties.py::test_prop_09_overview_always_present PASSED
tests/test_properties.py::test_prop_10_results_subset_of_input PASSED
tests/test_properties.py::test_prop_11_category_coherence PASSED

11 passed in XX.XXs
```

**Expected duration**: 30–120 seconds (DataProcessor PBT tests write temp CSV files per example).

---

## Run Full Test Suite (All 36 Tests)

```bash
pytest tests/ \
  --cov=. \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  --cov-omit="app.py,tests/*" \
  -v
```

---

## Fixing Failing Tests

### `ImportError: No module named 'data_processor'`
**Cause**: Python cannot find the source files in the workspace root.
**Fix**: Verify `tests/conftest.py` exists and `sys.path.insert(0, ...)` points to the workspace root. Run pytest from the workspace root directory.

### `test_data_processor.py` fails with `resample` error
**Cause**: pandas version mismatch — `"ME"` frequency alias requires pandas ≥ 2.2.
**Fix**: Confirm `pandas==2.2.3` is installed: `pip show pandas`.

### `test_evaluator.py` fails with `AttributeError` on mock
**Cause**: Mock structure mismatch with `message.content[0].text` access pattern.
**Fix**: Verify `evaluator.py` accesses `message.content[0].text` (not `message.text` directly).

### Coverage below 80%
**Cause**: New code paths not covered by tests.
**Fix**: Check `--cov-report=term-missing` output; add targeted tests for uncovered lines.
