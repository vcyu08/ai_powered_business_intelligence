# InsightForge — Business Logic Model

## Overview

InsightForge's business logic consists of four coordinated pipelines:
1. **Data Processing Pipeline** — CSV ingestion → statistics → LangChain Documents
2. **RAG Retrieval Pipeline** — keyword extraction → category matching → document retrieval
3. **Inference Pipeline** — retrieved context + memory → LLM streaming → response
4. **Evaluation Pipeline** — AI response + question → Anthropic SDK → score

---

## 1. Data Processing Pipeline

### 1.1 CSV Ingestion

`DataProcessor.load_data(csv_path)` reads `sales_data.csv` into a pandas DataFrame. Column schema:

| Column | Type | Description |
|---|---|---|
| Date | string → datetime | Transaction date |
| Product | string | Widget A / B / C / D |
| Region | string | North / South / East / West |
| Sales | float | Revenue for the transaction |
| Customer_Age | int | Age of purchaser |
| Customer_Gender | string | Male / Female |
| Customer_Satisfaction | float | Satisfaction score (1–5) |

After loading: Date column is cast to `datetime64`, sorted ascending.

### 1.2 Statistics Computation

`DataProcessor.compute_statistics()` derives the following from the DataFrame:

```
total_sales      = df['Sales'].sum()
total_records    = len(df)
avg_sales        = df['Sales'].mean()

top_product      = df.groupby('Product')['Sales'].sum().idxmax()
top_region       = df.groupby('Region')['Sales'].sum().idxmax()

product_breakdown   = df.groupby('Product')['Sales'].agg(['sum', 'mean', 'count']).reset_index()
regional_breakdown  = df.groupby('Region')['Sales'].agg(['sum', 'mean', 'count']).reset_index()

monthly_sales       = df.resample('ME', on='Date')['Sales'].sum()  # DatetimeIndex → float Series
                       formatted as {YYYY-MM: float} dict

age_groups          = pd.cut(df['Customer_Age'], bins=[0,25,35,45,55,100],
                             labels=['18–25','26–35','36–45','46–55','55+'])
age_group_breakdown = df.assign(AgeGroup=age_groups).groupby('AgeGroup').agg(
                        count=('Sales','count'),
                        avg_satisfaction=('Customer_Satisfaction','mean')
                      ).reset_index()

satisfaction_pivot  = df.pivot_table(
                        values='Customer_Satisfaction',
                        index='Product',
                        columns='Region',
                        aggfunc='mean'
                      )
```

Returns a `dict` containing all of the above keyed by the names above.

### 1.3 Knowledge Base Document Construction

`DataProcessor.create_documents()` converts statistics into LangChain `Document` objects grouped by category. Categories map to retrieval buckets:

| Category | Document Content | Count |
|---|---|---|
| `overview` | Total sales, record count, avg sales, top product, top region, month with highest sales | 1 |
| `product` | Per-product: Widget A/B/C/D — total sales, avg sales, transaction count, % of total | 4 |
| `region` | Per-region: North/South/East/West — total sales, avg sales, transaction count, % of total | 4 |
| `time_series` | Month-by-month sales totals in ranked order; growth trend description | 1 |
| `customer` | Age group distribution with counts and avg satisfaction; gender split; overall avg satisfaction | 1 |

Each Document: `Document(page_content=<text>, metadata={"category": <cat>, "source": "sales_data.csv"})`

---

## 2. RAG Retrieval Pipeline

### 2.1 KEYWORD_MAP Definition

```python
KEYWORD_MAP = {
    "product": [
        "product", "widget", "item", "category", "best product",
        "selling", "sold", "sku"
    ],
    "region": [
        "region", "area", "location", "territory",
        "north", "south", "east", "west", "geographic"
    ],
    "time_series": [
        "month", "trend", "time", "period", "year", "annual",
        "quarterly", "growth", "seasonal", "over time", "history",
        "recent", "latest", "when"
    ],
    "customer": [
        "customer", "age", "gender", "demographic",
        "satisfaction", "happy", "rating", "who buys", "buyer"
    ],
}
```

### 2.2 Category Matching Algorithm

`BusinessDataRetriever._get_relevant_documents(query)`:

```
1. Normalize: query_lower = query.strip().lower()
2. matched_categories = {}
3. For each (category, keywords) in KEYWORD_MAP:
       For each keyword in keywords:
           If keyword in query_lower:
               Add category to matched_categories (set — deduplicated)
               Break inner loop (one match per category is sufficient)
4. Always add "overview" to matched_categories (rule BR-03)
5. Collect results:
       retrieved = []
       For each doc in self.documents:
           If doc.metadata["category"] in matched_categories:
               Append doc to retrieved
6. Return retrieved
```

**Multi-category behavior (Q1=A)**: ALL matched categories are retrieved. A query matching both `product` and `region` returns product documents + region documents + overview document.

### 2.3 LCEL Chain Assembly

`RAGSystem.__init__` builds the chain:

```
chain = (
    RunnablePassthrough.assign(
        context = (lambda x: x["question"]) | retriever | (lambda docs: "\n\n".join(d.page_content for d in docs))
    )
    | prompt
    | llm           # ChatAnthropic(model="claude-opus-4-8", streaming=True)
    | StrOutputParser()
)
```

System prompt template injects `{context}` and `{chat_history}` into the request. The chain is invoked via `chain.stream({"question": q, "chat_history": history})`.

---

## 3. Inference Pipeline

`RAGSystem.get_response(query, chat_history)` flow:

```
1. Call chain.stream({"question": query, "chat_history": chat_history})
2. Yield each token chunk from the stream (caller iterates and renders to UI)
3. On completion, return the full assembled response string
```

Streaming is the primary mode. The caller (`app.py`) uses `st.write_stream()` to render tokens incrementally.

---

## 4. Evaluation Pipeline

`QAEvalChain.evaluate(question, answer)` flow:

```
1. Build evaluation prompt:
   "You are a QA evaluator. Rate the following answer to a business intelligence
    question on a scale of 1-5 where:
    1 = Completely irrelevant or incorrect
    2 = Mostly irrelevant with minor useful elements
    3 = Partially relevant but missing key information
    4 = Mostly accurate and relevant
    5 = Highly accurate, complete, and well-explained

    Question: {question}
    Answer: {answer}

    Respond with ONLY a JSON object: {"score": <integer 1-5>, "reasoning": "<brief explanation>"}"

2. Call anthropic.Anthropic().messages.create(
       model="claude-opus-4-8",
       max_tokens=200,
       messages=[{"role": "user", "content": prompt}]
   )
3. Extract response text from message.content[0].text
4. Parse JSON: json.loads(response_text) → {"score": int, "reasoning": str}
5. Validate: score must be int in range [1, 5]
6. Return EvaluationResult(score=score, reasoning=reasoning)
7. On any exception: log warning; return EvaluationResult(score=None, reasoning="Evaluation unavailable")
```

---

## 5. Testable Properties (PBT-01)

The following properties are invariants that must hold for ALL valid inputs. These are the seeds for Hypothesis-based property-based tests.

### DataProcessor Properties

| ID | Property | Invariant |
|---|---|---|
| PROP-01 | Total sales accuracy | `stats['total_sales'] == df['Sales'].sum()` — exact equality for any non-empty DataFrame |
| PROP-02 | Record count accuracy | `stats['total_records'] == len(df)` — always matches DataFrame length |
| PROP-03 | Top product validity | `stats['top_product'] in df['Product'].unique()` — must be a real product in the data |
| PROP-04 | Top region validity | `stats['top_region'] in df['Region'].unique()` — must be a real region in the data |
| PROP-05 | Average sales bounds | `df['Sales'].min() <= stats['avg_sales'] <= df['Sales'].max()` — mean is bounded by data range |

### MemoryManager Properties

| ID | Property | Invariant |
|---|---|---|
| PROP-06 | Exchange count growth | After N interactions (N ≤ 10): `len(messages) == N * 2` — two messages per exchange |
| PROP-07 | Rolling window cap | After >10 interactions: `len(messages) <= 20` — hard cap enforced |
| PROP-08 | Message alternation | Messages always alternate HumanMessage → AIMessage — never two consecutive of same type |

### BusinessDataRetriever Properties

| ID | Property | Invariant |
|---|---|---|
| PROP-09 | Overview always present | For any non-empty query: at least one document with `metadata['category'] == 'overview'` in results |
| PROP-10 | Results subset of input | All returned documents are members of the original input document list (no fabrication) |
| PROP-11 | Category coherence | When query contains a keyword matching category X: at least one document with `metadata['category'] == X` is returned |
