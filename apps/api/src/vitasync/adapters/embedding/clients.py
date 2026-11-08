"""Embedding clients (implement core.ports.EmbedderPort). Standard library HTTP only.

Behaviour taken from the team router v0.5 (slm_extractor.py): batches of 32, retry with back-off on
429/5xx and timeouts, every vector normalised to length 1. Texts are cut to 1000 characters by the
caller (recognition), not here.
"""
from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.request

BATCH_SIZE = 32


def normalise(vector: list[float]) -> list[float]:
    """Scale to unit length (zero vector stays zero)."""
    n = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [float(x) / n for x in vector]


def _post(url: str, payload: dict, headers: dict, timeout_s: float, retries: int = 4) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", **headers}, method="POST")
    delay = 2.0
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            raise ConnectionError(f"embedding service HTTP {e.code}") from e
        except urllib.error.URLError as e:
            raise ConnectionError("embedding service not reachable") from e
        except TimeoutError as e:
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            raise ConnectionError("embedding service timed out") from e
    raise ConnectionError("embedding service: too many retries")


class _Batched:
    model: str

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            vectors = self._embed_batch(batch)
            if len(vectors) != len(batch):
                raise ConnectionError(f"{len(vectors)} embeddings for {len(batch)} texts")
            out.extend(normalise(v) for v in vectors)
        return out


class ApiEmbedder(_Batched):
    """OpenAI-compatible /embeddings (e.g. KI:connect.nrw). Synthetic test data only (ADR: self-hosted).

    Args:
        model: embedding model id, e.g. `qwen-qwen3-embedding-8b`.
        api_base: base URL ending in /v1.
        api_key: bearer key; never logged, never part of an error message.
    """

    def __init__(self, model: str, api_base: str, api_key: str, timeout_s: float = 60.0):
        if not (model and api_base and api_key):
            raise ValueError("model, api_base and api_key are required (VITASYNC_API_BASE, VITASYNC_API_KEY)")
        self.model = model
        self.url = api_base.rstrip("/") + "/embeddings"
        self._headers = {"Authorization": "Bearer " + api_key}
        self.timeout_s = timeout_s

    def _embed_batch(self, texts):
        data = _post(self.url, {"model": self.model, "input": texts}, self._headers, self.timeout_s)["data"]
        return [d["embedding"] for d in sorted(data, key=lambda d: d.get("index", 0))]


class OllamaEmbedder(_Batched):
    """Ollama /api/embed for self-hosted operation."""

    def __init__(self, model: str, base_url: str, timeout_s: float = 120.0):
        self.model = model
        self.url = base_url.rstrip("/") + "/api/embed"
        self.timeout_s = timeout_s

    def _embed_batch(self, texts):
        return _post(self.url, {"model": self.model, "input": texts, "keep_alive": "15m", "truncate": True}, {},
                     self.timeout_s)["embeddings"]


class FakeEmbedder:
    """Test double: returns prepared vectors per text (unknown text -> `default`)."""

    model = "fake-embedding"

    def __init__(self, vectors: dict[str, list[float]], default: list[float] | None = None):
        self.vectors = vectors
        self.default = default
        self.calls = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        out = []
        for t in texts:
            v = self.vectors.get(t, self.default)
            if v is None:
                raise ConnectionError("no fake vector for this text")
            out.append(normalise(v))
        return out
