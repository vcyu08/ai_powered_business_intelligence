import json
from unittest.mock import MagicMock, patch

import pytest

from evaluator import EvaluationResult, QAEvalChain


def _mock_response(score: int, reasoning: str = "Looks good") -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock()]
    msg.content[0].text = json.dumps({"score": score, "reasoning": reasoning})
    return msg


@pytest.fixture
def evaluator():
    with patch("evaluator.anthropic.Anthropic"):
        chain = QAEvalChain()
    return chain


def test_evaluate_returns_evaluation_result(evaluator):
    evaluator._client.messages.create.return_value = _mock_response(4)
    result = evaluator.evaluate("What is the top product?", "Widget A leads sales.")
    assert isinstance(result, EvaluationResult)
    assert result.score == 4


@pytest.mark.parametrize("score", [1, 2, 3, 4, 5])
def test_evaluate_score_range(evaluator, score):
    evaluator._client.messages.create.return_value = _mock_response(score)
    result = evaluator.evaluate("Q", "A")
    assert result.score == score


def test_evaluate_handles_api_error(evaluator):
    evaluator._client.messages.create.side_effect = Exception("Connection failed")
    result = evaluator.evaluate("Q", "A")
    assert result.score is None
    assert result.reasoning == "Evaluation unavailable"


def test_evaluate_handles_invalid_json(evaluator):
    bad = MagicMock()
    bad.content = [MagicMock()]
    bad.content[0].text = "not valid json"
    evaluator._client.messages.create.return_value = bad
    result = evaluator.evaluate("Q", "A")
    assert result.score is None


def test_from_llm_returns_instance():
    with patch("evaluator.anthropic.Anthropic"):
        chain = QAEvalChain.from_llm()
    assert isinstance(chain, QAEvalChain)
