"""Ports: interfaces that adapters implement. No infrastructure here."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ExtractionError(Exception):
    """The model output was missing, not JSON, or did not match the flag schema.

    A normal case, not a crash: callers retry once and then fall back.
    The message never contains user text.
    """


@dataclass(frozen=True)
class RawModelOutput:
    """Unvalidated model answer. Validation happens in features/recognition, never in the adapter.

    Attributes:
        content: raw text returned by the model (expected: JSON per contracts/llm/intent_flags.v1.schema.json).
        latency_s: wall time of the call in seconds.
        model: model name from configuration.
        prompt_tokens / output_tokens: token counts reported by the runtime, if any.
    """

    content: str
    latency_s: float
    model: str
    prompt_tokens: int | None = None
    output_tokens: int | None = None


class EmbedderPort(Protocol):
    """Turns texts into embedding vectors (one list of floats per text, same order)."""

    model: str

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per text.

        Raises:
            ConnectionError: embedding service not reachable or answered with an error.
        """
        ...


class IntentExtractorPort(Protocol):
    """Asks the model for the intent flags of one message (prompt and schema live in the adapter)."""

    model: str

    def extract_raw(self, text: str) -> RawModelOutput:
        """Return the raw model answer for `text`.

        Raises:
            ExtractionError: the runtime answered with an error.
            ConnectionError: model server not reachable.
        """
        ...
