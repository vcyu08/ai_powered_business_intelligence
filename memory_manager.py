import logging

from langchain_core.messages import AIMessage, HumanMessage

logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self, max_exchanges: int = 10):
        self._messages: list = []
        self._max_exchanges = max_exchanges

    def add_interaction(self, human: str, ai: str) -> None:
        self._messages.append(HumanMessage(content=human))
        self._messages.append(AIMessage(content=ai))
        max_messages = self._max_exchanges * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]

    def get_messages(self) -> list:
        return list(self._messages)

    def clear(self) -> None:
        self._messages = []
