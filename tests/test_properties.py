"""
Property-based tests using Hypothesis — covers PROP-01 to PROP-11.
"""
import os
import tempfile

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage

from data_processor import DataProcessor
from memory_manager import MemoryManager
from rag_system import BusinessDataRetriever

PRODUCTS = ["Widget A", "Widget B", "Widget C", "Widget D"]
REGIONS = ["North", "South", "East", "West"]

_COMMON_SETTINGS = dict(
    max_examples=100,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow],
)

_SAMPLE_DOCS = [
    Document(page_content=f"{c} content", metadata={"category": c, "source": "test"})
    for c in ["overview", "product", "region", "time_series", "customer"]
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_csv(records: list[dict]) -> str:
    df = pd.DataFrame(records)
    tf = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    )
    df.to_csv(tf.name, index=False)
    tf.close()
    return tf.name


def _make_records(n: int, sales: list[float]) -> list[dict]:
    return [
        {
            "Date": f"2024-{(i % 12) + 1:02d}-01",
            "Product": PRODUCTS[i % 4],
            "Region": REGIONS[i % 4],
            "Sales": sales[i],
            "Customer_Age": 30,
            "Customer_Gender": "Male",
            "Customer_Satisfaction": 3.0,
        }
        for i in range(n)
    ]


# ── DataProcessor properties (PROP-01 to PROP-05) ────────────────────────────

@settings(**_COMMON_SETTINGS)
@given(
    sales=st.lists(
        st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=40,
    )
)
def test_prop_01_total_sales_accuracy(sales):
    """PROP-01: total_sales == df['Sales'].sum()"""
    path = _write_csv(_make_records(len(sales), sales))
    try:
        dp = DataProcessor(path)
        dp.load_data()
        dp.compute_statistics()
        assert abs(dp.stats["total_sales"] - sum(sales)) < 1e-4
    finally:
        os.unlink(path)


@settings(**_COMMON_SETTINGS)
@given(n=st.integers(min_value=1, max_value=40))
def test_prop_02_record_count_accuracy(n):
    """PROP-02: total_records == len(df)"""
    sales = [100.0] * n
    path = _write_csv(_make_records(n, sales))
    try:
        dp = DataProcessor(path)
        dp.load_data()
        dp.compute_statistics()
        assert dp.stats["total_records"] == n
    finally:
        os.unlink(path)


@settings(**_COMMON_SETTINGS)
@given(
    sales=st.lists(
        st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=20,
    )
)
def test_prop_03_top_product_validity(sales):
    """PROP-03: top_product in {Widget A, Widget B, Widget C, Widget D}"""
    path = _write_csv(_make_records(len(sales), sales))
    try:
        dp = DataProcessor(path)
        dp.load_data()
        dp.compute_statistics()
        assert dp.stats["top_product"] in set(PRODUCTS)
    finally:
        os.unlink(path)


@settings(**_COMMON_SETTINGS)
@given(
    sales=st.lists(
        st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=20,
    )
)
def test_prop_04_top_region_validity(sales):
    """PROP-04: top_region in {North, South, East, West}"""
    path = _write_csv(_make_records(len(sales), sales))
    try:
        dp = DataProcessor(path)
        dp.load_data()
        dp.compute_statistics()
        assert dp.stats["top_region"] in set(REGIONS)
    finally:
        os.unlink(path)


@settings(**_COMMON_SETTINGS)
@given(
    sales=st.lists(
        st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=20,
    )
)
def test_prop_05_avg_sales_bounds(sales):
    """PROP-05: min(sales) <= avg_sales <= max(sales)"""
    path = _write_csv(_make_records(len(sales), sales))
    try:
        dp = DataProcessor(path)
        dp.load_data()
        dp.compute_statistics()
        assert min(sales) - 1e-6 <= dp.stats["avg_sales"] <= max(sales) + 1e-6
    finally:
        os.unlink(path)


# ── MemoryManager properties (PROP-06 to PROP-08) ────────────────────────────

@settings(max_examples=100, deadline=5000)
@given(n=st.integers(min_value=1, max_value=10))
def test_prop_06_exchange_count_growth(n):
    """PROP-06: N interactions (N<=10) -> len(messages) == N*2"""
    mm = MemoryManager(max_exchanges=10)
    for i in range(n):
        mm.add_interaction(f"Q{i}", f"A{i}")
    assert len(mm.get_messages()) == n * 2


@settings(max_examples=100, deadline=5000)
@given(n=st.integers(min_value=11, max_value=50))
def test_prop_07_rolling_window_cap(n):
    """PROP-07: N>10 interactions -> len(messages) <= 20"""
    mm = MemoryManager(max_exchanges=10)
    for i in range(n):
        mm.add_interaction(f"Q{i}", f"A{i}")
    assert len(mm.get_messages()) <= 20


@settings(max_examples=100, deadline=5000)
@given(n=st.integers(min_value=1, max_value=15))
def test_prop_08_message_alternation(n):
    """PROP-08: messages always alternate HumanMessage / AIMessage"""
    mm = MemoryManager(max_exchanges=10)
    for i in range(n):
        mm.add_interaction(f"Q{i}", f"A{i}")
    msgs = mm.get_messages()
    for i, msg in enumerate(msgs):
        if i % 2 == 0:
            assert isinstance(msg, HumanMessage), f"Expected HumanMessage at index {i}"
        else:
            assert isinstance(msg, AIMessage), f"Expected AIMessage at index {i}"


# ── BusinessDataRetriever properties (PROP-09 to PROP-11) ────────────────────

@settings(max_examples=100, deadline=5000)
@given(query=st.text(min_size=1, max_size=200))
def test_prop_09_overview_always_present(query):
    """PROP-09: any non-empty query -> overview doc always in results"""
    retriever = BusinessDataRetriever(documents=_SAMPLE_DOCS)
    results = retriever._get_relevant_documents(query)
    cats = [d.metadata["category"] for d in results]
    assert "overview" in cats


@settings(max_examples=100, deadline=5000)
@given(query=st.text(min_size=1, max_size=200))
def test_prop_10_results_subset_of_input(query):
    """PROP-10: all returned docs are members of input list"""
    retriever = BusinessDataRetriever(documents=_SAMPLE_DOCS)
    results = retriever._get_relevant_documents(query)
    for doc in results:
        assert doc in _SAMPLE_DOCS


_KEYWORD_TO_CATEGORY = {
    "product": "product",
    "widget": "product",
    "region": "region",
    "north": "region",
    "month": "time_series",
    "trend": "time_series",
    "customer": "customer",
    "age": "customer",
    "satisfaction": "customer",
}


@settings(max_examples=50, deadline=5000)
@given(
    keyword=st.sampled_from(list(_KEYWORD_TO_CATEGORY.keys())),
    suffix=st.text(max_size=30),
)
def test_prop_11_category_coherence(keyword, suffix):
    """PROP-11: query with keyword for category X -> at least one doc with category X"""
    expected = _KEYWORD_TO_CATEGORY[keyword]
    query = f"{keyword} {suffix}"
    retriever = BusinessDataRetriever(documents=_SAMPLE_DOCS)
    results = retriever._get_relevant_documents(query)
    result_cats = {d.metadata["category"] for d in results}
    assert expected in result_cats
