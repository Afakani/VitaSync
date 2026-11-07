"""Recognition (M2): validate the LLM's flag output and call the extractor with one retry.

The LLM only recognises WHAT is asked. It never decides a route and never names a cause.
Contract of the model output: contracts/llm/intent_flags.v1.schema.json (built by `flag_schema`).
"""
from __future__ import annotations

import json
import re

from vitasync.core import intent as I
from vitasync.core.intent import Extraction
from vitasync.core.ports import ExtractionError, IntentExtractorPort

NONE_SUB = "NONE"
_THINK = re.compile(r"<think>.*?</think>", re.S)
_FENCE = re.compile(r"^```(?:json)?|```$", re.M)


def flag_schema() -> dict:
    """JSON schema of the model output; identical to contracts/llm/intent_flags.v1.schema.json."""
    props: dict = {name: {"type": "boolean"} for name in I.FLAGS}
    props["suggested_intent"] = {"type": "string", "enum": list(I.INTENTS)}
    props["suggested_sub_label"] = {"type": "string", "enum": [*I.SUB_LABELS, NONE_SUB]}
    props["confidence"] = {"type": "number", "minimum": 0, "maximum": 1}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "intent_flags.v1",
        "type": "object",
        "properties": props,
        "required": [*I.FLAGS, "suggested_intent", "suggested_sub_label", "confidence"],
        "additionalProperties": False,
    }


def parse_and_validate(content: str, latency_s: float | None = None, model: str | None = None) -> Extraction:
    """Parse raw model text into an Extraction.

    Tolerates a <think> block and ```json fences. Every flag must be present and boolean.

    Raises:
        ExtractionError: not JSON, not an object, missing/extra field or wrong type. No user text in the message.
    """
    content = _FENCE.sub("", _THINK.sub("", content or "").strip()).strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ExtractionError(f"invalid JSON at position {e.pos}") from e
    if not isinstance(data, dict):
        raise ExtractionError("output is not a JSON object")
    extra = set(data) - set(flag_schema()["properties"])
    if extra:
        raise ExtractionError(f"unknown fields: {sorted(extra)}")

    flags = {}
    for name in I.FLAGS:
        value = data.get(name)
        if not isinstance(value, bool):
            raise ExtractionError(f"flag {name!r} missing or not boolean")
        flags[name] = value

    intent = data.get("suggested_intent")
    if intent not in I.INTENTS:
        raise ExtractionError("invalid suggested_intent")
    sub = data.get("suggested_sub_label")
    if sub in (None, "", NONE_SUB):
        sub = None
    elif sub not in I.SUB_LABELS:
        raise ExtractionError("invalid suggested_sub_label")
    conf = data.get("confidence")
    if isinstance(conf, bool) or not isinstance(conf, (int, float)):
        raise ExtractionError("confidence missing or not a number")
    return Extraction(flags=flags, suggested_intent=intent, suggested_sub_label=sub,
                      confidence=max(0.0, min(1.0, float(conf))), latency_s=latency_s, model=model)


def extract_flags(text: str, extractor: IntentExtractorPort, retries: int = 1) -> Extraction:
    """Ask the model for flags and validate them, retrying `retries` times on invalid output.

    Raises:
        ExtractionError: still invalid after all attempts (caller falls back to SAFE_DEFAULT).
        ConnectionError: model server not reachable (not retried).
    """
    last: ExtractionError | None = None
    for _ in range(retries + 1):
        try:
            raw = extractor.extract_raw(text)
            return parse_and_validate(raw.content, latency_s=raw.latency_s, model=raw.model)
        except ExtractionError as e:
            last = e
    assert last is not None
    raise last
