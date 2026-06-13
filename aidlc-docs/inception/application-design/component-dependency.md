# InsightForge — Component Dependencies

## Dependency Matrix

| Component | Depends On | Communication Pattern |
|---|---|---|
| `app.py` | `DataProcessor`, `RAGSystem`, `MemoryManager`, `QAEvalChain`, `visualizations` | Direct import and function call |
| `RAGSystem` | `BusinessDataRetriever`, `langchain_anthropic.ChatAnthropic`, `langchain_core.*` | Constructor injection (`documents` list) |
| `BusinessDataRetriever` | `langchain_core.retrievers.BaseRetriever` | Inheritance; `documents` injected via Pydantic field |
| `DataProcessor` | `pandas`, `langchain_core.documents.Document` | Pure computation; no runtime dependencies on other components |
| `MemoryManager` | `langchain_core.messages.*` | Pure data structure; no runtime dependencies on other components |
| `QAEvalChain` | `anthropic.Anthropic` | Direct SDK calls; no LangChain dependency |
| `visualizations` | `plotly`, `pandas` | Stateless functions; no dependencies on other components |

---

## Data Flow Diagram

```
sales_data.csv
      |
      v
[DataProcessor]
  - load_data()
  - compute_statistics()
  - create_documents()
      |
      |--- DataFrame ---------> [app.py] --------> [visualizations]
      |                                                   |
      |--- List[Document] ---> [RAGSystem]               |
                                    |             Plotly Figures
                               [BusinessDataRetriever]   |
                                    |                     v
                               [ChatAnthropic]      Streamlit UI
                               (claude-opus-4-8)
                                    |
                               LCEL Chain
                                    |
                              query / stream
                                    |
                               [app.py] <-------> [MemoryManager]
                                    |              (st.session_state)
                                    |
                               [QAEvalChain]
                               (Anthropic SDK)
                                    |
                             evaluation scores
                                    |
                               Streamlit UI
```

---

## Initialization Order

1. `DataProcessor.__init__(csv_path)` — no dependencies
2. `DataProcessor.load_data()` — reads CSV
3. `DataProcessor.compute_statistics()` — pure computation
4. `DataProcessor.create_documents()` — produces `List[Document]`
5. `RAGSystem.__init__(documents)` — receives Documents; builds chain
6. `MemoryManager.__init__()` — no dependencies (session-scoped)
7. `QAEvalChain.__init__()` — no dependencies (session-scoped)

---

## External Dependencies

| Library | Used By | Purpose |
|---|---|---|
| `anthropic` | `QAEvalChain` | Direct API calls for evaluation |
| `langchain-anthropic` | `RAGSystem` | `ChatAnthropic` LLM wrapper |
| `langchain-core` | `RAGSystem`, `BusinessDataRetriever`, `MemoryManager` | Documents, retrievers, messages, LCEL |
| `pandas` | `DataProcessor`, `visualizations` | Data loading and transformation |
| `plotly` | `visualizations` | Interactive chart generation |
| `streamlit` | `app.py` | UI rendering and session state |
| `python-dotenv` | `app.py` | `.env` file loading |
