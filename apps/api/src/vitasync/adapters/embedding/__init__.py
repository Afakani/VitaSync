"""Embedding clients for the SLM recognizer. Public API of this adapter."""
from vitasync.adapters.embedding.clients import ApiEmbedder, FakeEmbedder, OllamaEmbedder, normalise

__all__ = ["ApiEmbedder", "FakeEmbedder", "OllamaEmbedder", "normalise"]
