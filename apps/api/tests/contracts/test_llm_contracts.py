"""The LLM contract file, the code and the prompt must describe the same flags."""
import json
from pathlib import Path

from vitasync.adapters.llm.ollama import PROMPT_FILE, SCHEMA_FILE, OllamaIntentExtractor
from vitasync.core import intent as I
from vitasync.features.recognition import flag_schema


def test_schema_file_matches_code():
    assert json.loads(SCHEMA_FILE.read_text(encoding="utf-8")) == flag_schema()


def test_prompt_names_every_flag():
    prompt = PROMPT_FILE.read_text(encoding="utf-8")
    missing = [name for name in I.FLAGS if f"- {name}:" not in prompt]
    assert missing == []


def test_ollama_payload_uses_contract_and_settings():
    ext = OllamaIntentExtractor(model="m", base_url="http://x/")
    body = ext.payload("Testnachricht")
    assert body["model"] == "m" and body["think"] is False and body["options"]["temperature"] == 0
    assert body["format"]["required"] == flag_schema()["required"]
    assert "Testnachricht" in body["messages"][1]["content"]
    assert ext.base_url == "http://x"


def test_empty_model_name_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        OllamaIntentExtractor(model="", base_url="http://x")


def test_schema_path_points_into_contracts():
    assert SCHEMA_FILE.parent == Path(__file__).resolve().parents[4] / "contracts" / "llm"
