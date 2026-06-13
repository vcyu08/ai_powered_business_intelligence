# Application Design Plan — InsightForge

## Plan Checkboxes

- [x] Gather user answers to design questions below
- [x] Generate components.md
- [x] Generate component-methods.md
- [x] Generate services.md
- [x] Generate component-dependency.md
- [x] Generate application-design.md (consolidated)
- [x] Validate design completeness
- [ ] Present completion message

---

## Design Questions

Three design decisions need clarification before generating artifacts.

---

### Question 1: Retriever Class Location
The `BusinessDataRetriever` (custom LangChain `BaseRetriever`) is a sub-component that only the RAG chain uses. Where should it live?

A) Inside `rag_system.py` — keeps all RAG-related code co-located in one file (recommended for simplicity)

B) In its own `retriever.py` — cleaner separation, easier to test in isolation

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: Orchestration Layer
The Streamlit app needs to coordinate the RAG system, memory manager, and data processor. How should this be organized?

A) Direct orchestration in `app.py` — `app.py` imports and coordinates all components directly (recommended — keeps it simple, fewer files)

B) Dedicated `InsightForgeService` class — a service object wraps RAG + memory into a single `ask(query)` interface, app.py only interacts with the service

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3: Evaluation Component
The `QAEvalChain` evaluator uses the Anthropic SDK directly. Should it also accept a LangChain LLM wrapper as a constructor parameter (mirroring the real LangChain `QAEvalChain.from_llm(llm)` API more closely)?

A) Yes — accept an optional LangChain LLM parameter in `from_llm()`, fall back to direct Anthropic SDK if not provided (closer to LangChain API)

B) No — always use the Anthropic SDK directly inside the evaluator (simpler, no LangChain dependency in evaluator)

X) Other (please describe after [Answer]: tag below)

[Answer]: B
