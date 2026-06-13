# Performance Test Instructions — InsightForge

## Scope

InsightForge is a single-user local application. Automated load/stress/throughput testing is **not applicable**. The performance requirements (NFR-PERF-01/02/03) are verified manually during a smoke-test session.

---

## Performance Requirements (from NFR Requirements)

| ID | Requirement | Target | Test Method |
|---|---|---|---|
| NFR-PERF-01 | First AI token appears | ≤ 10 seconds after query | Manual observation |
| NFR-PERF-02 | All 5 sidebar charts render | ≤ 3 seconds at startup | Manual observation |
| NFR-PERF-03 | Statistics computation completes | ≤ 5 seconds at startup | Manual observation |

---

## Manual Performance Verification

### Prerequisites

- Application fully built (see `build-instructions.md`)
- `ANTHROPIC_API_KEY` set in `.env`
- Internet connection available (for Anthropic API)

### Step 1: Launch the Application

```bash
streamlit run app.py
```

Open the Streamlit URL (typically `http://localhost:8501`) in a browser.

### Step 2: Verify NFR-PERF-03 (Statistics Computation ≤ 5s)

**Observation**: On first launch, the sidebar metrics and charts should appear within 5 seconds of the page loading.

- ✅ Pass: Sidebar shows 4 KPI metrics and 5 charts within 5 seconds
- ❌ Fail: Sidebar remains blank for more than 5 seconds → investigate `DataProcessor.compute_statistics()` performance

### Step 3: Verify NFR-PERF-02 (Charts Render ≤ 3s)

**Observation**: After the sidebar appears, all 5 Plotly charts should be fully rendered with data (not blank frames) within 3 seconds.

- ✅ Pass: All charts visible with data
- ❌ Fail: Charts show blank frames → check `visualizations.py` for errors in `st.sidebar.plotly_chart()`

### Step 4: Verify NFR-PERF-01 (First AI Token ≤ 10s)

**Test query**: Type `"What is the total sales revenue?"` and press Enter.

**Observation**: The assistant chat bubble should begin displaying text within 10 seconds.

- ✅ Pass: First token appears within 10 seconds
- ❌ Fail: Chat bubble stays empty for more than 10 seconds → check API key validity and network connectivity

### Step 5: Verify RESILIENCY-10 (60s Timeout)

**This test is optional** and simulates a slow API response.

To verify timeout is configured, inspect the source:
```bash
python -c "import inspect; from rag_system import RAGSystem; print('request_timeout: 60' in inspect.getsource(RAGSystem))"
python -c "import inspect; from evaluator import QAEvalChain; print('Timeout(60.0)' in inspect.getsource(QAEvalChain.__init__))"
```

**Expected output**: `True` for both commands.

---

## N/A Testing Types

| Test Type | Status | Reason |
|---|---|---|
| Load testing | N/A | Single-user local app; no concurrent user requirements |
| Stress testing | N/A | No scalability or availability SLA |
| Throughput testing | N/A | No requests/second target |
| Latency percentiles | N/A | Single-user; no SLA percentile targets |
