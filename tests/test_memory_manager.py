from langchain_core.messages import AIMessage, HumanMessage

from memory_manager import MemoryManager


def test_add_interaction_increments_count():
    mm = MemoryManager()
    mm.add_interaction("Hello", "Hi there!")
    assert len(mm.get_messages()) == 2


def test_rolling_window_enforced():
    mm = MemoryManager(max_exchanges=10)
    for i in range(11):
        mm.add_interaction(f"Q{i}", f"A{i}")
    assert len(mm.get_messages()) <= 20


def test_rolling_window_drops_oldest():
    mm = MemoryManager(max_exchanges=2)
    mm.add_interaction("Q1", "A1")
    mm.add_interaction("Q2", "A2")
    mm.add_interaction("Q3", "A3")
    msgs = mm.get_messages()
    assert len(msgs) == 4
    assert msgs[0].content == "Q2"


def test_message_types():
    mm = MemoryManager()
    mm.add_interaction("question", "answer")
    msgs = mm.get_messages()
    assert isinstance(msgs[0], HumanMessage)
    assert isinstance(msgs[1], AIMessage)


def test_get_messages_empty():
    mm = MemoryManager()
    assert mm.get_messages() == []


def test_clear():
    mm = MemoryManager()
    mm.add_interaction("q", "a")
    mm.clear()
    assert mm.get_messages() == []
