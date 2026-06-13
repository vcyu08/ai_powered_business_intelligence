# InsightForge — Business Rules

## Input Validation Rules

### BR-01: Non-Empty Input
- **Rule**: User query must not be empty or consist solely of whitespace
- **Check**: `query.strip() == ""` → reject with message "Please enter a question."
- **Applies to**: App.py before invoking the RAG chain

### BR-02: Maximum Input Length
- **Rule**: User query must not exceed 1,000 characters (Q4=B)
- **Check**: `len(query) > 1000` → reject with message "Query too long. Please limit your question to 1,000 characters."
- **Applies to**: App.py before invoking the RAG chain
- **Rationale**: Prevents prompt injection bloat and excessive API token consumption (SECURITY-05)

---

## Retrieval Rules

### BR-03: Overview Always Included
- **Rule**: The `overview` category document is ALWAYS included in retrieval results, regardless of query content
- **Rationale**: Overview provides grounding context for every response; ensures LLM is always aware of top-level statistics
- **Implementation**: After keyword matching, `matched_categories` always contains `"overview"`

### BR-04: Multi-Category Retrieval (Q1=A)
- **Rule**: When a query matches keywords from multiple categories, documents from ALL matched categories are returned
- **Rationale**: Richest possible context for the LLM; avoids false negatives from single-category selection
- **Example**: "What's the best product in the North region?" → retrieves `product` docs + `region` docs + `overview` doc
- **No priority ordering**: Categories are treated equally; no single category takes precedence

### BR-05: No Match Fallback
- **Rule**: If no keyword matches any category, return only the `overview` document
- **Rationale**: Overview always provides a meaningful starting point for any business question

---

## Memory Rules

### BR-06: Rolling Window Enforcement
- **Rule**: Memory retains at most the last 10 exchanges (human + AI message pairs = 20 messages total)
- **Check**: After `add_interaction(human, ai)`, if `len(messages) > 20`, remove the two oldest messages
- **Applies to**: `MemoryManager.add_interaction()`
- **Rationale**: Keeps context window manageable; prevents token overflow on long sessions (FR-06)

### BR-07: Message Order Invariant
- **Rule**: Messages in memory must always alternate: HumanMessage → AIMessage → HumanMessage → ...
- **Enforced by**: `add_interaction()` always appends both messages atomically as a pair

---

## Evaluation Rules

### BR-08: Automatic Evaluation (Q2=A)
- **Rule**: `QAEvalChain.evaluate()` is called automatically after every AI response
- **Timing**: Called after streaming completes, before the response is stored in memory
- **Applies to**: App.py interaction flow

### BR-09: Score Range Validation
- **Rule**: Evaluation score must be an integer in `[1, 5]`
- **On failure**: If score is outside `[1, 5]` or cannot be parsed, score is set to `None` and reasoning is set to "Evaluation unavailable"
- **User-facing behavior**: Score `None` → display "Evaluation unavailable" instead of a numeric score

### BR-10: Evaluation Score Display
- **Rule**: Evaluation result (score + reasoning) is always displayed immediately below the AI response
- **Format**: Score shown as `⭐ Score: N/5` followed by reasoning text in an info box
- **Rationale**: Q2=A — always show; no toggle or button required

---

## API Key Rules

### BR-11: API Key Required at Startup
- **Rule**: `ANTHROPIC_API_KEY` must be present in environment variables at application startup
- **Check**: `os.getenv("ANTHROPIC_API_KEY")` returns a non-empty string
- **On failure**: Display error message "ANTHROPIC_API_KEY is not set. Please configure your .env file." and halt; do not attempt LLM calls
- **Loaded from**: `.env` file via `python-dotenv` (SECURITY-12)

### BR-12: API Key Never Logged or Displayed
- **Rule**: The API key value must never appear in log output, error messages, or UI text
- **Implementation**: Only check for presence (`bool(key)`) — never log the key value

---

## Error Handling Rules

### BR-13: Generic LLM Error Messages (SECURITY-15)
- **Rule**: Any exception from LLM or Anthropic API calls is caught; a generic message is shown to the user
- **User-facing message**: "An error occurred while processing your request. Please try again."
- **Internal logging**: Full exception details logged at WARNING level with context (no API key or user data in log)
- **Applies to**: `RAGSystem.get_response()`, `QAEvalChain.evaluate()`

### BR-14: Data Load Failure
- **Rule**: If `sales_data.csv` cannot be loaded (file missing, corrupt, wrong schema), the app displays an error and halts
- **User-facing message**: "Failed to load sales data. Please ensure sales_data.csv is present in the application directory."
- **Column validation**: After load, verify all required columns exist: Date, Product, Region, Sales, Customer_Age, Customer_Gender, Customer_Satisfaction

### BR-15: LLM Timeout (RESILIENCY-10)
- **Rule**: LLM API calls are subject to a 60-second timeout
- **On timeout**: Treat as a generic error (BR-13); display generic error message
- **Implementation**: Rely on `httpx` default timeout configured via `anthropic.Anthropic(timeout=60.0)` for the evaluator; LangChain `ChatAnthropic` timeout via `request_timeout=60`

---

## Data Integrity Rules

### BR-16: Statistics Computed Once
- **Rule**: `DataProcessor.compute_statistics()` is called once at startup and cached; statistics are not recomputed per query
- **Rationale**: Sales data is static during a session; recomputing wastes resources

### BR-17: Knowledge Base Immutable at Runtime
- **Rule**: The list of Documents produced by `DataProcessor.create_documents()` is not modified after RAGSystem initialization
- **Rationale**: Document list is injected into `BusinessDataRetriever` at construction; mutation would silently break retrieval
