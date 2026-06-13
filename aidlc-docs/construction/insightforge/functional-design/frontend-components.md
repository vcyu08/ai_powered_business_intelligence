# InsightForge — Frontend Components

## Layout Overview (Q3=A: Sidebar)

```
+------------------------------------------+----------------------------------+
|  SIDEBAR                                  |  MAIN AREA                       |
|                                           |                                  |
|  [Key Metrics]                            |  InsightForge                    |
|  Total Sales: $X                          |  AI-Powered Business Intelligence|
|  Total Records: N                         |                                  |
|  Top Product: Widget X                    |  [Chat History]                  |
|  Top Region: X                            |   Human: ...                     |
|                                           |   Assistant: ...                 |
|  [Sales Trend Chart]                      |   ⭐ Score: N/5 — reasoning      |
|  [Product Breakdown Chart]                |   Human: ...                     |
|  [Region Comparison Chart]                |   ...                            |
|  [Age Group Chart]                        |                                  |
|  [Satisfaction Heatmap]                   |  [Chat Input Box]                |
|                                           |  "Ask a business question..."    |
+------------------------------------------+----------------------------------+
```

---

## Component Hierarchy

```
StreamlitApp (app.py)
├── PageConfig                    # st.set_page_config(layout="wide")
├── Sidebar
│   ├── KeyMetricsPanel           # 4 st.metric() widgets
│   └── ChartPanel
│       ├── SalesTrendChart       # plotly_chart: line chart
│       ├── ProductBreakdownChart # plotly_chart: bar chart
│       ├── RegionComparisonChart # plotly_chart: bar or pie chart
│       ├── AgeGroupChart         # plotly_chart: bar chart
│       └── SatisfactionHeatmap   # plotly_chart: heatmap
└── MainArea
    ├── PageHeader                # st.title() + st.caption()
    ├── ErrorBanner               # shown only on API key / data load failure
    ├── ChatHistory               # iterates st.session_state["chat_history"]
    │   └── MessageBubble (×N)
    │       ├── HumanMessage      # st.chat_message("human")
    │       └── AssistantMessage  # st.chat_message("assistant")
    │           └── EvaluationDisplay  # always shown (Q2=A)
    └── ChatInputBar              # st.chat_input("Ask a business question...")
```

---

## Component Definitions

### PageConfig

**Purpose**: Configure Streamlit page before any content renders.

**State**: None (called once on module load)

**Props/Parameters**:
```python
st.set_page_config(
    page_title = "InsightForge — Business Intelligence Assistant",
    page_icon  = "📊",
    layout     = "wide"    # enables sidebar + main area split
)
```

---

### Sidebar — KeyMetricsPanel

**Purpose**: Display 4 headline KPIs from pre-computed statistics.

**State**: Reads `st.session_state["stats"]` (set at startup)

**Rendered elements**:
```python
st.sidebar.header("📈 Key Metrics")
col1, col2 = st.sidebar.columns(2)
col1.metric("Total Sales",   f"${stats['total_sales']:,.0f}")
col2.metric("Total Records", f"{stats['total_records']:,}")
col1.metric("Top Product",   stats['top_product'])
col2.metric("Top Region",    stats['top_region'])
```

---

### Sidebar — ChartPanel

**Purpose**: Render all 5 Plotly charts in the sidebar.

**State**: Reads `st.session_state["stats"]` (DataFrames from statistics dict)

**Charts**:
| Chart | Visualizations Function | Data |
|---|---|---|
| Sales Trend | `plot_sales_trend(monthly_sales)` | monthly_sales dict |
| Product Breakdown | `plot_product_breakdown(product_breakdown)` | product_breakdown DataFrame |
| Region Comparison | `plot_region_comparison(regional_breakdown)` | regional_breakdown DataFrame |
| Age Group Distribution | `plot_age_groups(age_group_breakdown)` | age_group_breakdown DataFrame |
| Satisfaction Heatmap | `plot_satisfaction_heatmap(satisfaction_pivot)` | satisfaction_pivot DataFrame |

**Rendered with**:
```python
st.sidebar.plotly_chart(fig, use_container_width=True)
```

---

### MainArea — PageHeader

**Purpose**: Display app title and brief description.

**Rendered elements**:
```python
st.title("InsightForge 📊")
st.caption("AI-Powered Business Intelligence Assistant — Powered by Claude + LangChain")
st.divider()
```

---

### MainArea — ErrorBanner

**Purpose**: Surface initialization errors (missing API key, failed CSV load) prominently.

**Condition**: Only rendered when `st.session_state["init_error"]` is not None.

**Rendered elements**:
```python
if st.session_state.get("init_error"):
    st.error(st.session_state["init_error"])
    st.stop()    # halts further rendering
```

---

### MainArea — ChatHistory

**Purpose**: Replay all past conversation turns from session state.

**State**: Reads `st.session_state["chat_history"]` (list of `ChatHistoryEntry` dicts)

**Interaction flow** (render-time, not event-time):
```python
for entry in st.session_state["chat_history"]:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])
        if entry["role"] == "assistant" and entry.get("evaluation"):
            render_evaluation(entry["evaluation"])
```

---

### MainArea — MessageBubble (per turn)

**Purpose**: Render a single chat turn (human or assistant).

**HumanMessage**:
```python
with st.chat_message("human"):
    st.markdown(user_text)
```

**AssistantMessage** (streaming new responses):
```python
with st.chat_message("assistant"):
    response_text = st.write_stream(rag_system.get_response(query, history))
    evaluation = evaluator.evaluate(query, response_text)
    render_evaluation(evaluation)
```

**AssistantMessage** (replaying history):
```python
with st.chat_message("assistant"):
    st.markdown(entry["content"])
    render_evaluation(entry["evaluation"])
```

---

### EvaluationDisplay (always shown — Q2=A)

**Purpose**: Display `EvaluationResult` below every assistant message.

**Props**: `evaluation: EvaluationResult`

**Rendered elements**:
```python
def render_evaluation(evaluation: EvaluationResult):
    if evaluation.score is not None:
        st.info(f"⭐ **Score: {evaluation.score}/5** — {evaluation.reasoning}")
    else:
        st.warning("⚠️ Evaluation unavailable")
```

---

### MainArea — ChatInputBar

**Purpose**: Capture new user queries and trigger the full interaction flow.

**State**: Writes to `st.session_state["chat_history"]`, `st.session_state["memory"]`

**Rendered element**:
```python
user_input = st.chat_input("Ask a business question about your sales data...")
```

**Event handling** (when `user_input` is not None):
```
1. Validate: strip whitespace, check non-empty (BR-01), check length ≤ 1000 (BR-02)
   → On failure: st.warning(message); return
2. Append human entry to chat_history and display immediately
3. Retrieve chat history messages from memory
4. Stream response via rag_system.get_response() with st.write_stream()
5. On streaming error: st.error("An error occurred...") per BR-13; return
6. Call evaluator.evaluate(user_input, response_text)
7. Call memory.add_interaction(user_input, response_text)
8. Append assistant entry (with evaluation) to chat_history
9. st.rerun() not needed — Streamlit rerenders automatically
```

---

## Session State Schema

All session state is keyed under `st.session_state`. Initialized in `init_session()` on first run.

```python
st.session_state = {
    # Cached at startup (shared across all users in same server process)
    "rag_system":    RAGSystem | None,      # None if init failed
    "data_processor": DataProcessor | None, # None if init failed
    "stats":          dict | None,          # Statistics dict; None if init failed
    "init_error":     str | None,           # Error message from startup; None if OK

    # Per-session (per browser tab)
    "memory":        MemoryManager,         # initialized to empty MemoryManager()
    "evaluator":     QAEvalChain,           # initialized to QAEvalChain()
    "chat_history":  list[ChatHistoryEntry] # initialized to []
}
```

**Cache decorators**:
- `DataProcessor` and `RAGSystem` initialization is wrapped in `@st.cache_resource` to execute once per server process, not once per page load.

---

## User Interaction Flows

### Flow 1: Application Startup

```
1. st.set_page_config()
2. @st.cache_resource: load DataProcessor, load_data(), compute_statistics(), create_documents()
3. @st.cache_resource: initialize RAGSystem(documents)
4. If any step fails: set init_error, continue to render (ErrorBanner will halt)
5. init_session(): if first visit, initialize memory, evaluator, chat_history in session_state
6. Render Sidebar (metrics + 5 charts)
7. Render MainArea header
8. ErrorBanner check (halts if init_error is set)
9. Render ChatHistory (empty on first visit)
10. Render ChatInputBar
```

### Flow 2: User Asks a Question

```
1. User types query in ChatInputBar and presses Enter
2. Validate: strip + length + non-empty
3. Display human message in chat
4. Retrieve history = memory.get_messages()
5. Open assistant chat_message context
6. Stream: response_text = st.write_stream(rag_system.get_response(query, history))
7. Evaluate: evaluation = evaluator.evaluate(query, response_text)
8. Display evaluation via render_evaluation(evaluation)
9. Store: memory.add_interaction(query, response_text)
10. Append entries to chat_history
```

### Flow 3: Error During LLM Call

```
1. Exception raised in get_response() or evaluate()
2. Caught in app.py
3. Exception details logged at WARNING level (internal — never shown to user)
4. st.error("An error occurred while processing your request. Please try again.")
5. No entry added to chat_history (incomplete turn discarded)
```
