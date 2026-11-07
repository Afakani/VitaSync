"""Model access behind a small interface so tests can use a fake client."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .config import Config


@dataclass(frozen=True)
class LLMRequest:
    model: str
    messages: tuple[dict[str, str], ...]
    format_schema: dict[str, Any]
    options: dict[str, Any]
    think: bool


@dataclass(frozen=True)
class LLMReply:
    content: str
    # Timing fields reported by the server itself (nanoseconds); kept apart from
    # the locally measured request duration and never mixed into it.
    server_timing: dict[str, Any] = field(default_factory=dict)


class LLMTimeout(Exception):
    """The call exceeded the configured timeout."""


class LLMError(Exception):
    """Any other technical failure of the call (connection, server error)."""


class LLMClient(Protocol):
    def chat(self, request: LLMRequest) -> LLMReply: ...

    def describe_model(self, model: str) -> dict[str, str]: ...


SERVER_TIMING_FIELDS = ("total_duration", "load_duration", "prompt_eval_count",
                        "prompt_eval_duration", "eval_count", "eval_duration")


class OllamaClient:
    """Talks to an already running Ollama server. Never pulls or downloads models."""

    def __init__(self, config: Config):
        import ollama  # imported lazily so tests run without the package being reachable

        self._ollama = ollama
        self._client = ollama.Client(host=config.base_url, timeout=config.timeout_seconds)

    def chat(self, request: LLMRequest) -> LLMReply:
        import httpx

        try:
            resp = self._client.chat(
                model=request.model,
                messages=list(request.messages),
                format=request.format_schema,
                options=request.options,
                think=request.think,
                stream=False,
            )
        except httpx.TimeoutException as exc:
            raise LLMTimeout(f"Zeitüberschreitung: {exc}") from exc
        except self._ollama.ResponseError as exc:
            raise LLMError(f"Serverfehler {exc.status_code}: {exc.error}") from exc
        except (httpx.HTTPError, ConnectionError) as exc:
            raise LLMError(f"Verbindungsfehler: {exc}") from exc
        timing = {k: getattr(resp, k, None) for k in SERVER_TIMING_FIELDS}
        return LLMReply(content=resp.message.content or "", server_timing=timing)

    def describe_model(self, model: str) -> dict[str, str]:
        try:
            for entry in self._client.list().models:
                if entry.model == model:
                    return {"model": model, "digest": entry.digest or "nicht verfügbar"}
        except Exception as exc:  # metadata only; a failure must not stop the run
            return {"model": model, "digest": f"nicht verfügbar ({type(exc).__name__})"}
        return {"model": model, "digest": "nicht verfügbar (Modell nicht in ollama list)"}
