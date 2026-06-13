# Functional Design Plan — InsightForge

## Plan Checkboxes

- [x] Gather user answers to functional design questions below
- [x] Generate business-logic-model.md
- [x] Generate business-rules.md
- [x] Generate domain-entities.md
- [x] Generate frontend-components.md
- [x] Update plan checkboxes and aidlc-state.md
- [x] Present completion message

---

## Functional Design Questions

Four business-logic decisions need clarification before generating the detailed functional design.

---

### Question 1: Multi-Category Keyword Retrieval

The `BusinessDataRetriever` maps query keywords to document categories (e.g., "product" → `product`, "region" → `region`, "month/trend" → `time_series`). When the user asks a question that matches keywords from **multiple** categories — e.g., *"What's the best product in the North region?"* — which documents should be retrieved?

A) Retrieve documents from **ALL matched categories** — the chain receives the richest possible context (recommended)

B) Retrieve from the **first matched category only** — simpler logic; whichever keyword appears first in the KEYWORD_MAP wins

C) Use a **fixed priority order** — always prefer product > region > time_series > overview when multiple categories match

[Answer]:A

---

### Question 2: QA Evaluation Display Timing

The `QAEvalChain` scores each AI response 1–5. When should evaluation run and be shown to the user?

A) **Automatically after every response** — evaluation runs immediately after each AI answer and the score is always displayed below the response (recommended)

B) **On-demand via button** — an "Evaluate Last Response" button lets the user trigger evaluation manually; results appear when requested

C) **Auto-run but hidden by default** — evaluation runs automatically but scores are collapsed inside an expander element the user can expand to view

[Answer]:A

---

### Question 3: Chart Display Location

The 5 Plotly charts (sales trend, product breakdown, region comparison, customer age groups, satisfaction heatmap) need a home in the Streamlit UI. Where should they appear?

A) **Sidebar** — charts and key stat metrics render in the left sidebar, always visible alongside the chat window (recommended)

B) **Main area tabs** — a row of tabs (Overview | Charts | Chat) at the top of the main area lets users switch between the dashboard and chat

C) **Inline expander** — a "View Sales Dashboard" expander button in the main area shows/hides all charts on demand

[Answer]:A

---

### Question 4: Query Input Length Limit

For input validation (SECURITY-05 compliance), what is the maximum character length allowed for a user query?

A) **500 characters** — keeps prompts concise; sufficient for natural-language business questions

B) **1,000 characters** — allows detailed multi-part questions while still capping prompt size (recommended)

C) **2,000 characters** — maximum flexibility; user can paste substantial text as part of a question

[Answer]:B
