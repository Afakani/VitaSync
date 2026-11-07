"""Fake intent extractor for tests: returns prepared answers, never calls a model."""
from __future__ import annotations

import json

from vitasync.core import intent as I
from vitasync.core.ports import RawModelOutput


def flags_json(true_flags=(), intent: str = I.HEALTH_QUESTION, sub: str = "NONE", confidence: float = 0.9) -> str:
    """Build a valid model answer with the given flags set to true and all others false."""
    unknown = set(true_flags) - set(I.FLAGS)
    if unknown:
        raise ValueError(f"unknown flags {sorted(unknown)}")
    data = {name: name in true_flags for name in I.FLAGS}
    data.update(suggested_intent=intent, suggested_sub_label=sub, confidence=confidence)
    return json.dumps(data)


class FakeIntentExtractor:
    """Implements core.ports.IntentExtractorPort.

    Args:
        answers: raw answers returned in order; the last one repeats.
    """

    model = "fake"

    def __init__(self, *answers: str):
        if not answers:
            raise ValueError("at least one answer is required")
        self.answers = list(answers)
        self.calls = 0

    def extract_raw(self, text: str) -> RawModelOutput:
        content = self.answers[min(self.calls, len(self.answers) - 1)]
        self.calls += 1
        return RawModelOutput(content=content, latency_s=0.0, model=self.model)
