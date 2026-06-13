# InsightForge — Application Design (Consolidated)

## Architecture Summary

InsightForge is a single-unit, six-module Python application. The Streamlit app (`app.py`) directly orchestrates five supporting modules. There is no intermediate service layer.

## Module Map

| File | Component | Responsibility |
|---|---|---|
| `data_processor.py` | `DataProcessor` | Load CSV, compute stats, build LangChain knowledge base |
| `rag_system.py` | `BusinessDataRetriever` + `RAGSystem` | Custom retriever + LCEL chain (LangChain + Claude) |
| `memory_manager.py` | `MemoryManager` | Conversation history (LangChain messages) |
| `visualizations.py` | 5 chart functions | Plotly figures for all visualization types |
| `evaluator.py` | `QAEvalChain` | AI-powered response evaluation (Anthropic SDK) |
| `app.py` | Streamlit app | UI, session state, orchestration |

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Retriever location | Inside `rag_system.py` | Co-location keeps RAG code in one place |
| Orchestration | Direct in `app.py` | Simpler; no intermediate service class needed |
| Evaluator LLM | Anthropic SDK directly | Avoids LangChain dependency in evaluator module |
| Caching | `@st.cache_resource` | One-time init of DataProcessor + RAGSystem per server |
| Session state | `st.session_state` | Per-user MemoryManager and QAEvalChain instances |

## Component Details

See individual artifact files:
- [components.md](components.md) — component definitions and responsibilities
- [component-methods.md](component-methods.md) — method signatures
- [services.md](services.md) — orchestration flow
- [component-dependency.md](component-dependency.md) — dependency matrix and data flow

## Security Notes (Requirements Stage)

- API key loaded via `python-dotenv`; validated at startup (SECURITY-12)
- User input validated and length-capped before LLM calls (SECURITY-05)
- All LLM calls wrapped with exception handling; generic errors shown to user (SECURITY-15)
- Structured logging configured in all components (SECURITY-03)
- `requirements.txt` pins all dependency versions exactly (SECURITY-10)

## PBT Notes (Requirements Stage)

- Hypothesis selected as PBT framework (PBT-09)
- Properties to test: statistics computation invariants in `DataProcessor`, retriever category mapping, MemoryManager rolling-window behavior (PBT-01)
- Test suite in `tests/` directory alongside source files
