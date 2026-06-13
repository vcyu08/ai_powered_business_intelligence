# InsightForge — Domain Entities

## Entity Overview

| Entity | Lives In | Type | Notes |
|---|---|---|---|
| `SalesRecord` | DataFrame row | Conceptual only | Not a Python class; rows accessed via pandas |
| `Statistics` | `dict` | Value object | Returned by `DataProcessor.compute_statistics()` |
| `Document` | LangChain | `langchain_core.documents.Document` | Knowledge base unit |
| `KnowledgeBase` | `list[Document]` | Collection | All documents; produced by `DataProcessor.create_documents()` |
| `ConversationMessage` | LangChain messages | `HumanMessage` / `AIMessage` | Individual chat turns |
| `EvaluationResult` | dataclass | Value object | Score + reasoning from `QAEvalChain` |
| `ChatHistoryEntry` | `dict` | Session value | One entry per turn, stored in `st.session_state` |

---

## Entity Definitions

### SalesRecord (Conceptual)

Represents one row of `sales_data.csv`. Accessed only via the pandas DataFrame; never materialized as a Python object.

| Field | Python Type | Constraints |
|---|---|---|
| Date | `datetime64` | Parsed from string; sorted ascending |
| Product | `str` | One of: `Widget A`, `Widget B`, `Widget C`, `Widget D` |
| Region | `str` | One of: `North`, `South`, `East`, `West` |
| Sales | `float` | > 0 |
| Customer_Age | `int` | > 0 |
| Customer_Gender | `str` | `Male` or `Female` |
| Customer_Satisfaction | `float` | 1.0–5.0 |

---

### Statistics (Value Object)

Returned by `DataProcessor.compute_statistics()` as a Python `dict`. Immutable after construction.

```python
{
    "total_sales":          float,          # sum of all Sales values
    "total_records":        int,            # number of rows in DataFrame
    "avg_sales":            float,          # mean of Sales column
    "top_product":          str,            # product with highest total sales
    "top_region":           str,            # region with highest total sales

    "product_breakdown":    pd.DataFrame,   # columns: Product, sum, mean, count
    "regional_breakdown":   pd.DataFrame,   # columns: Region, sum, mean, count
    "monthly_sales":        dict,           # {YYYY-MM: float} ordered by month
    "age_group_breakdown":  pd.DataFrame,   # columns: AgeGroup, count, avg_satisfaction
    "satisfaction_pivot":   pd.DataFrame,   # index=Product, columns=Region, values=mean(Satisfaction)
}
```

**Constraints**:
- `total_sales` ≥ 0
- `total_records` ≥ 1 (empty DataFrame rejected at load time — BR-14)
- `top_product` ∈ `{Widget A, Widget B, Widget C, Widget D}`
- `top_region` ∈ `{North, South, East, West}`
- `avg_sales` ∈ [min(Sales), max(Sales)]

---

### Document

LangChain `Document` representing one knowledge base entry.

```python
Document(
    page_content: str,          # human-readable text describing the data slice
    metadata: {
        "category": str,        # one of: overview, product, region, time_series, customer
        "source":   str,        # always "sales_data.csv"
    }
)
```

**Constraints**:
- `category` must be one of the five defined values
- `page_content` is non-empty
- `source` is always `"sales_data.csv"` (all data from one file)

**Category distribution**: 1 overview + 4 product + 4 region + 1 time_series + 1 customer = **11 total Documents**

---

### KnowledgeBase

The ordered list of all Documents passed to `BusinessDataRetriever`.

```python
knowledge_base: list[Document]  # 11 documents, fixed after construction
```

**Constraints**:
- Length: always 11 (one overview + four per product + four per region + one time_series + one customer)
- Order: overview first, then products, then regions, then time_series, then customer
- Immutable at runtime (BR-17)

---

### ConversationMessage

LangChain message types used in the memory list. Not a custom class.

```python
HumanMessage(content: str)   # user's query
AIMessage(content: str)      # assistant's response
```

**Constraints**:
- Always appear in alternating pairs: [HumanMessage, AIMessage, HumanMessage, AIMessage, ...]
- At most 20 messages in the list at any time (10 exchanges × 2 messages — BR-06)

---

### EvaluationResult (Value Object)

Returned by `QAEvalChain.evaluate()`.

```python
@dataclass
class EvaluationResult:
    score:     int | None   # integer in [1, 5], or None if evaluation failed
    reasoning: str          # LLM explanation of the score, or "Evaluation unavailable"
```

**Constraints**:
- `score` ∈ {1, 2, 3, 4, 5, None}
- `reasoning` is non-empty string
- When `score is None`: `reasoning == "Evaluation unavailable"`

**Score semantics**:
| Score | Meaning |
|---|---|
| 1 | Completely irrelevant or incorrect |
| 2 | Mostly irrelevant with minor useful elements |
| 3 | Partially relevant but missing key information |
| 4 | Mostly accurate and relevant |
| 5 | Highly accurate, complete, and well-explained |

---

### ChatHistoryEntry (Session Value Object)

One entry per conversation turn stored in `st.session_state["chat_history"]`.

```python
{
    "role":       str,                # "human" or "assistant"
    "content":    str,                # message text
    "evaluation": EvaluationResult | None   # None for human messages
}
```

**Constraints**:
- Human entries always have `evaluation=None`
- Assistant entries always have an `EvaluationResult` (score may be None if evaluation failed)
- Entries are appended in pairs: human entry first, then assistant entry

---

## Entity Relationships

```
sales_data.csv
      |
      v
SalesRecord × N (DataFrame rows)
      |
      +--[compute_statistics()]--> Statistics (dict)
      |                                  |
      |                            [visualizations]
      |                             Plotly figures
      |
      +--[create_documents()]---> Document × 11 --> KnowledgeBase (list)
                                                         |
                                               [BusinessDataRetriever]
                                                         |
                                              filtered Document subset
                                                         |
                                                    [RAGSystem chain]
                                                         |
                                               response text (streamed)
                                                         |
                                      +------------------+------------------+
                                      |                                     |
                               [MemoryManager]                     [QAEvalChain]
                         ConversationMessage pair              EvaluationResult
                                      |                                     |
                                      +------------------+------------------+
                                                         |
                                               ChatHistoryEntry pair
                                              (stored in session_state)
```
