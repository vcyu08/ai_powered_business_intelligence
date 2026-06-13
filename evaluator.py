import json
import logging
from dataclasses import dataclass

import anthropic
import httpx

logger = logging.getLogger(__name__)

_EVAL_PROMPT = """\
You are a QA evaluator for a business intelligence assistant.
Rate the following answer on a scale of 1-5 where:
1 = Completely irrelevant or incorrect
2 = Mostly irrelevant with minor useful elements
3 = Partially relevant but missing key information
4 = Mostly accurate and relevant
5 = Highly accurate, complete, and well-explained

Question: {question}
Answer: {answer}

Respond with ONLY a JSON object in this exact format:
{{"score": <integer 1-5>, "reasoning": "<brief explanation>"}}\
"""


@dataclass
class EvaluationResult:
    score: int | None
    reasoning: str


class QAEvalChain:
    def __init__(self):
        self._client = anthropic.Anthropic(
            timeout=httpx.Timeout(60.0),
        )

    @classmethod
    def from_llm(cls) -> "QAEvalChain":
        return cls()

    def evaluate(self, question: str, answer: str) -> EvaluationResult:
        try:
            prompt = _EVAL_PROMPT.format(question=question, answer=answer)
            message = self._client.messages.create(
                model="claude-opus-4-8",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text
            data = json.loads(text)
            score = int(data["score"])
            if score not in range(1, 6):
                raise ValueError(f"Score {score} outside [1, 5]")
            return EvaluationResult(
                score=score,
                reasoning=str(data.get("reasoning", "")),
            )
        except Exception as e:
            logger.warning("Evaluation error: %s", type(e).__name__)
            return EvaluationResult(score=None, reasoning="Evaluation unavailable")
