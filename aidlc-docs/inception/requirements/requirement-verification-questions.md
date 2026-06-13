# InsightForge — Requirements Verification Questions

The capstone PDF provides a clear project description. The questions below clarify
implementation details needed before code generation begins. Please fill in each
`[Answer]:` tag with the letter that best matches your preference.

---

## Question 1
Which Claude model should InsightForge use for the AI assistant and evaluation?

A) claude-opus-4-8 — most capable, best reasoning (recommended for this capstone)

B) claude-sonnet-4-6 — faster and lower cost, still high quality

C) claude-haiku-4-5 — fastest and cheapest, suitable for prototyping

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 2
How should the Anthropic API key be provided to the application?

A) Environment variable via a `.env` file (recommended — keeps key out of source code)

B) Entered by the user directly in the Streamlit sidebar at runtime

C) Both — `.env` file as default, with a Streamlit sidebar override

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 3
Which Python package manager / environment setup should be used?

A) pip with `requirements.txt` (simplest setup)

B) conda with `environment.yml`

C) Poetry with `pyproject.toml`

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 4
Should the application include unit tests in addition to the build/run instructions?

A) Yes — include pytest-based unit tests for data processing and RAG components

B) No — application code only; tests are out of scope for this capstone

X) Other (please describe after [Answer]: tag below)

[Answer]: Yes

---

## Question 5
For data visualizations, which charting library should be used?

A) Plotly — interactive, browser-based charts (recommended for Streamlit)

B) Matplotlib / Seaborn — static charts, widely familiar

C) Both — Plotly for primary charts, Matplotlib as fallback

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 6
How many pre-built evaluation test cases should the QAEvalChain section include?

A) 3 test cases — minimal, quick to run

B) 5 test cases — covers main query types (recommended)

C) 10 test cases — comprehensive evaluation suite

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question: Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)

B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question: Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips

C) No — skip all PBT rules (suitable for simple CRUD applications or educational projects)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question: Resiliency Extensions
Should the resiliency baseline be applied to this project?

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental/educational projects)

X) Other (please describe after [Answer]: tag below)

[Answer]: A
