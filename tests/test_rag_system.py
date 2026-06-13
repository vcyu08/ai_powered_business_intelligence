from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from rag_system import BusinessDataRetriever, RAGSystem

SAMPLE_DOCS = [
    Document(page_content="Overview content", metadata={"category": "overview", "source": "test"}),
    Document(page_content="Widget A data", metadata={"category": "product", "source": "test"}),
    Document(page_content="Widget B data", metadata={"category": "product", "source": "test"}),
    Document(page_content="North region data", metadata={"category": "region", "source": "test"}),
    Document(page_content="Monthly trend data", metadata={"category": "time_series", "source": "test"}),
    Document(page_content="Customer demographics", metadata={"category": "customer", "source": "test"}),
]


@pytest.fixture
def retriever():
    return BusinessDataRetriever(documents=SAMPLE_DOCS)


def test_retriever_overview_always_present(retriever):
    results = retriever._get_relevant_documents("random unrelated query xyz123")
    categories = [d.metadata["category"] for d in results]
    assert "overview" in categories


def test_retriever_multi_category(retriever):
    results = retriever._get_relevant_documents("best product in the north region")
    categories = {d.metadata["category"] for d in results}
    assert "product" in categories
    assert "region" in categories
    assert "overview" in categories


def test_retriever_no_match_returns_overview_only(retriever):
    results = retriever._get_relevant_documents("zzz no matching keywords zzz")
    assert len(results) == 1
    assert results[0].metadata["category"] == "overview"


def test_retriever_results_subset_of_input(retriever):
    results = retriever._get_relevant_documents("product sales trend month")
    for doc in results:
        assert doc in SAMPLE_DOCS


def test_rag_system_chain_assembled():
    with patch("rag_system.ChatAnthropic"):
        rag = RAGSystem(SAMPLE_DOCS)
    assert rag._chain is not None
