# InsightForge — AI-Powered Business Intelligence Assistant

A conversational BI assistant that lets you query sales data in plain English. Built with Claude, LangChain, and Streamlit.

## Features

- **Conversational Q&A** — ask questions about products, regions, trends, and customers; answers are grounded in the actual data via RAG
- **Streaming responses** — Claude's answer streams to the screen token-by-token
- **Auto-evaluation** — every response is automatically scored 1–5 for quality
- **Conversation memory** — retains the last 10 exchanges for natural follow-up questions
- **Visual dashboard** — sidebar with 5 interactive Plotly charts and 4 key metrics

## Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/) with access to `claude-opus-4-8`
- `sales_data.csv` in the project root (columns: `Date`, `Product`, `Region`, `Sales`, `Customer_Age`, `Customer_Gender`, `Customer_Satisfaction`)

## Setup

```powershell
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure your API key
copy .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

## Running the App

```powershell
streamlit run app.py
```

Opens at `http://localhost:8501`. Use the chat input to ask business questions; charts load automatically in the sidebar.

**Example questions:**
- "Which product generates the most revenue?"
- "How have sales trended over the past few months?"
- "Which region has the highest customer satisfaction?"
- "What is the age breakdown of our customers?"

## Running Tests

```powershell
# Install dev dependencies (first time only)
pip install -r requirements-dev.txt

# Unit tests with coverage
pytest tests/test_data_processor.py tests/test_memory_manager.py `
       tests/test_evaluator.py tests/test_rag_system.py tests/test_visualizations.py `
       '--cov=.' '--cov-fail-under=80' -v

# Property-based tests
pytest tests/test_properties.py -v
```

> **PowerShell note:** Single-quote `--` arguments (e.g. `'--cov=.'`) to prevent PowerShell from misreading them as operators.

Current results: **34 unit tests** passing · **11 PBT properties** passing · **93% coverage**

## Project Structure

```
.
├── app.py                 # Streamlit entry point
├── data_processor.py      # CSV loading, statistics, RAG document creation
├── rag_system.py          # LangChain LCEL chain and keyword retriever
├── memory_manager.py      # Rolling-window conversation memory
├── evaluator.py           # Response quality scorer (1–5)
├── visualizations.py      # Five Plotly chart functions
├── sales_data.csv         # Input dataset
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── tests/
```

## Tech Stack

| | Library | Version |
|---|---|---|
| UI | Streamlit | 1.43.2 |
| LLM orchestration | LangChain Core | 0.3.52 |
| Claude integration | langchain-anthropic | 0.3.7 |
| Anthropic SDK | anthropic | 0.49.0 |
| Data processing | pandas | 2.2.3 |
| Visualisations | Plotly | 5.24.1 |
| Unit testing | pytest + pytest-cov | 8.3.5 / 5.0.0 |
| Property-based testing | Hypothesis | 6.131.14 |
