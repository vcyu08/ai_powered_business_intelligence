# NFR Requirements Plan — InsightForge

## Plan Checkboxes

- [x] Gather user answers to NFR questions below
- [x] Generate nfr-requirements.md
- [x] Generate tech-stack-decisions.md
- [x] Update plan checkboxes and aidlc-state.md
- [x] Present completion message

---

## NFR Questions

Most NFR decisions were established in Requirements Analysis (extensions: Security=Full, PBT=Full, Resiliency=mostly N/A). Three remaining implementation-level decisions need confirmation before generating NFR artifacts.

---

### Question 1: Minimum Python Version

The application uses `match/case`, walrus operator, and `datetime.fromisoformat()` patterns available in Python 3.10+. Which should be the declared minimum?

A) **Python 3.10** — broadest compatibility; all required features available

B) **Python 3.11** — ~25% faster interpreter startup; `tomllib` built-in; slightly better error messages (recommended)

C) **Python 3.12** — latest stable; improved f-string handling; strictest but narrowest compatibility

[Answer]:B

---

### Question 2: Test Coverage Target

The test suite will include pytest unit tests and Hypothesis property-based tests (PBT-09 already selected). What is the target code coverage threshold?

A) **No numeric target** — cover all business logic paths and all 11 PBT properties (PROP-01 to PROP-11); quality over percentage

B) **≥ 80% line coverage** — standard industry threshold; enforced via `pytest-cov` with `--cov-fail-under=80` (recommended)

C) **≥ 90% line coverage** — high confidence threshold; may require additional edge-case tests for Streamlit UI code

[Answer]:B

---

### Question 3: Default Logging Level

The application uses Python's built-in `logging` module (SECURITY-03 — structured logging). What log level should be active by default when the app runs?

A) **WARNING** — only errors and warnings; minimal output for normal use (recommended)

B) **INFO** — includes startup messages, initialization steps, and key events; useful for demos and debugging

C) **DEBUG** — verbose; logs every retrieval result, memory state, and API call metadata; development only

[Answer]:A
