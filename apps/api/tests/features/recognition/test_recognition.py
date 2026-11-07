import json

import pytest

from vitasync.adapters.llm import FakeIntentExtractor, flags_json
from vitasync.core import intent as I
from vitasync.core.ports import ExtractionError
from vitasync.features.recognition import extract_flags, parse_and_validate


def test_valid_output():
    e = parse_and_validate(flags_json(["asks_own_data"], intent=I.DATA_QUERY, confidence=1.5))
    assert e.true_flags() == ["asks_own_data"]
    assert e.suggested_sub_label is None and e.confidence == 1.0


def test_think_block_and_fence_are_tolerated():
    raw = "<think>x</think>\n```json\n" + flags_json(["asks_app_help"], intent=I.APP_HELP) + "\n```"
    assert parse_and_validate(raw).suggested_intent == I.APP_HELP


@pytest.mark.parametrize("mutate", [
    lambda d: d.pop("asks_own_data"),
    lambda d: d.__setitem__("asks_own_data", "yes"),
    lambda d: d.__setitem__("suggested_intent", "CRISIS"),
    lambda d: d.__setitem__("suggested_sub_label", "OTHER"),
    lambda d: d.__setitem__("confidence", True),
    lambda d: d.__setitem__("extra_field", 1),
])
def test_invalid_output_is_rejected(mutate):
    data = json.loads(flags_json())
    mutate(data)
    with pytest.raises(ExtractionError):
        parse_and_validate(json.dumps(data))


def test_not_json_is_rejected():
    with pytest.raises(ExtractionError):
        parse_and_validate("Das ist keine JSON-Antwort")


def test_retry_once_then_success():
    fake = FakeIntentExtractor("kaputt", flags_json(["asks_own_data"], intent=I.DATA_QUERY))
    assert extract_flags("Frage", fake).suggested_intent == I.DATA_QUERY
    assert fake.calls == 2


def test_retry_exhausted_raises():
    fake = FakeIntentExtractor("kaputt")
    with pytest.raises(ExtractionError):
        extract_flags("Frage", fake, retries=1)
    assert fake.calls == 2
