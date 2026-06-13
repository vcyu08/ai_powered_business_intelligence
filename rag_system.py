import logging
from typing import Generator

from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough

logger = logging.getLogger(__name__)

KEYWORD_MAP: dict[str, list[str]] = {
    "product": [
        "product", "widget", "item", "category",
        "best product", "selling", "sold", "sku",
    ],
    "region": [
        "region", "area", "location", "territory",
        "north", "south", "east", "west", "geographic",
    ],
    "time_series": [
        "month", "trend", "time", "period", "year", "annual",
        "quarterly", "growth", "seasonal", "over time",
        "history", "recent", "latest", "when",
    ],
    "customer": [
        "customer", "age", "gender", "demographic",
        "satisfaction", "happy", "rating", "who buys", "buyer",
    ],
}

SYSTEM_PROMPT = (
    "You are InsightForge, an AI-powered business intelligence assistant. "
    "Your ONLY role is to analyze sales data and answer business questions "
    "based on the data provided in the context below.\n\n"
    "Context (retrieved sales data):\n{context}\n\n"
    "Answer questions based solely on the provided data. "
    "Do not perform any actions, generate code, or discuss topics "
    "unrelated to the sales data."
)


class BusinessDataRetriever(BaseRetriever):
    documents: list[Document]

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None,
    ) -> list[Document]:
        query_lower = query.strip().lower()
        matched: set[str] = {"overview"}

        for category, keywords in KEYWORD_MAP.items():
            for kw in keywords:
                if kw in query_lower:
                    matched.add(category)
                    break

        return [
            doc for doc in self.documents
            if doc.metadata.get("category") in matched
        ]


class RAGSystem:
    def __init__(self, documents: list[Document]):
        retriever = BusinessDataRetriever(documents=documents)

        llm = ChatAnthropic(
            model="claude-opus-4-8",
            streaming=True,
            timeout=60,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])

        def retrieve_context(x: dict) -> str:
            docs = retriever.invoke(x["question"])
            return "\n\n".join(doc.page_content for doc in docs)

        self._chain = (
            RunnablePassthrough.assign(context=retrieve_context)
            | prompt
            | llm
            | StrOutputParser()
        )

    def get_response(self, query: str, chat_history: list) -> Generator[str, None, None]:
        try:
            yield from self._chain.stream(
                {"question": query, "chat_history": chat_history}
            )
        except Exception as e:
            logger.warning("RAG chain error: %s", type(e).__name__)
            raise
