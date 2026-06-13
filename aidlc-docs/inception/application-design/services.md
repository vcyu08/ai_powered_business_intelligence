# InsightForge — Service Layer

## Architecture Decision

Per design decision Q2 (Answer: A), InsightForge uses **direct orchestration** in `app.py`. There is no intermediate service class — `app.py` imports and coordinates all components directly.

This is appropriate because:
- The application has a single user-facing surface (Streamlit)
- Components are loosely coupled and stateless (except MemoryManager)
- Streamlit's `@st.cache_resource` already provides an initialization boundary
- A service wrapper would add indirection without benefit at this scale

---

## Orchestration Flow (inside `app.py`)

### Startup (once per Streamlit server process)
```
init_system() [@st.cache_resource]
  └── DataProcessor(csv_path)
        .load_data()
        .compute_statistics()
        .create_documents()
        → documents: List[Document]
  └── RAGSystem(documents)
        → rag: RAGSystem (chain built)
```

### Per-Session State (once per browser session)
```
st.session_state
  ├── memory    = MemoryManager()
  ├── evaluator = QAEvalChain()
  └── chat      = []  (display log)
```

### Chat Interaction (per user message)
```
user query
  → memory.get_history()          # load LangChain message history
  → rag.stream(query, history)    # LCEL chain: retrieve → prompt → LLM → parse
  → st.write_stream(...)          # stream tokens to Streamlit UI
  → memory.add_interaction(...)   # persist to session history
  → session_state.chat.append()   # persist to display log
```

### Evaluation Flow (on "Run Evaluation" button)
```
for each test_case in test_cases:
  → rag.query(test_case.question, [])   # isolated query, no history
  → evaluator.evaluate_pair(...)        # Claude scores the response
→ evaluator.get_summary()               # aggregate metrics
```

---

## Shared Resources

| Resource | Owner | Shared With |
|---|---|---|
| `pd.DataFrame` (processed) | `DataProcessor` | `app.py` (visualizations, data overview) |
| `List[Document]` (knowledge base) | `DataProcessor` | `RAGSystem` (constructor) |
| `RAGSystem` instance | `@st.cache_resource` | `page_chat`, `page_evaluation` |
| `MemoryManager` instance | `st.session_state` | `page_chat` |
| `QAEvalChain` instance | `st.session_state` | `page_evaluation` |
