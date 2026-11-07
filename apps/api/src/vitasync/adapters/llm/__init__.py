"""Adapter fuer die lokale LLM-Laufzeit."""
from vitasync.adapters.llm.fake import FakeIntentExtractor, flags_json
from vitasync.adapters.llm.ollama import OllamaIntentExtractor

__all__ = ["FakeIntentExtractor", "OllamaIntentExtractor", "flags_json"]
