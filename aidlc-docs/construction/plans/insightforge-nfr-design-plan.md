# NFR Design Plan — InsightForge

## Plan Checkboxes

- [x] Gather user answers to NFR design questions below
- [x] Generate nfr-design-patterns.md
- [x] Generate logical-components.md
- [x] Update plan checkboxes and aidlc-state.md
- [x] Present completion message

---

## NFR Design Questions

Most NFR patterns are directly derivable from the NFR requirements (timeout, caching, error masking, structured logging). Three design-level decisions remain open before generating the pattern artifacts.

**N/A Categories** (documented for completeness):
- **Scalability Patterns** — N/A: single-user local app; no horizontal scaling, load balancing, or sharding needed
- **Availability Patterns** — N/A: local app; no HA, failover, or DR design required

---

### Question 1: Input Validation Timing (Resilience / UX Pattern)

When a user submits a query, should input validation happen before or after the human message appears in the chat history?

A) **Validate before displaying** — check length + non-empty first; only add human message to chat if valid; invalid queries show a warning banner without adding to chat history (recommended — keeps chat history clean)

B) **Display then validate** — append the human message to chat immediately, then validate; show error inline if invalid

[Answer]:A

---

### Question 2: QA Evaluation Execution Mode (Performance / Reliability Pattern)

After the AI finishes streaming its response, `QAEvalChain.evaluate()` is called. This is a second Anthropic API call that adds latency. How should it execute?

A) **Synchronous** — evaluation blocks the UI after streaming until the score is ready; user sees spinner briefly; simpler code (recommended)

B) **Background thread** — evaluation runs in a `threading.Thread` while the UI renders the response; score appears asynchronously; slightly more complex

[Answer]:A

---

### Question 3: Prompt Injection Defense (Security Pattern)

The user's query is embedded directly into the LLM prompt. Beyond length-capping (SECURITY-05), should we add an explicit blocklist check for common prompt injection markers?

A) **No explicit blocklist** — rely on Claude's built-in safety measures and the framing of the system prompt; a tight system prompt (business analytics context only) is sufficient defense (recommended)

B) **Add a blocklist check** — before sending to LLM, scan for strings like "ignore previous instructions", "system:", "you are now", etc.; reject with a warning if detected

[Answer]:A
