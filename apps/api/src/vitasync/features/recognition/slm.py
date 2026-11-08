"""SLM recognition: embedding vector -> 17 flags, intent, sub-label, confidence.

Inference of the team router v0.5 (`slm_extractor.SLMExtractor.predict_lr`), pure Python:
  - one logistic-regression head per flag (sigmoid), flag set if probability >= its threshold
  - intent head (softmax); confidence = probability of the chosen intent
  - sub-label head only when the intent is OUT_OF_SCOPE
Thresholds (team v0.5): safety flags 0.35 (a missed forbidden ask is worse than an extra block),
flags also covered by CP2 0.7, all others 0.5.
Weights: JSON with `flags` {name: {w, b}}, `intent` {classes, W, b}, `sub` {classes, W, b}.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

from vitasync.core import intent as I
from vitasync.core.intent import Extraction
from vitasync.core.ports import EmbedderPort

MAX_CHARS = 1000
SAFETY_FLAGS = frozenset({
    "asks_cause_or_diagnosis", "asks_value_evaluation", "asks_score_or_rating", "asks_color_coding",
    "asks_medication_advice", "asks_pharmacy_interpretation", "symptom_mentioned", "acute_danger_signs",
    "self_harm_or_crisis",
})
CP2_COVERED = {"asks_value_evaluation": 0.7, "asks_score_or_rating": 0.7, "asks_color_coding": 0.7}
SAFETY_THRESHOLD = 0.35
FLAG_THRESHOLD = 0.5
#: Calibrated class probability, not a self-rating: team v0.5 uses 0.5 instead of 0.6 for the SLM.
SLM_MIN_CONFIDENCE = 0.5


def threshold(flag: str) -> float:
    """Decision threshold for one flag (team v0.5, fixed mode)."""
    if flag in CP2_COVERED:
        return CP2_COVERED[flag]
    return SAFETY_THRESHOLD if flag in SAFETY_FLAGS else FLAG_THRESHOLD


def _dot(a, b) -> float:
    # math.sumprod (Python 3.12) as in the team router: identical results at the thresholds.
    return math.sumprod(a, b)


def _softmax(z: list[float]) -> list[float]:
    m = max(z)
    e = [math.exp(x - m) for x in z]
    t = sum(e)
    return [x / t for x in e]


class SlmWeights:
    """Loaded classifier heads. Raises ValueError if a flag head or a class is unknown."""

    def __init__(self, data: dict):
        self.flags = data["flags"]
        self.intent = data["intent"]
        self.sub = data["sub"]
        self.dim = data.get("dim")
        self.source = {k: data.get(k) for k in ("backend", "train_hash", "C")}
        unknown = set(self.flags) - set(I.FLAGS)
        if unknown:
            raise ValueError(f"weights contain unknown flags {sorted(unknown)}")
        if set(self.intent["classes"]) - set(I.INTENTS) or set(self.sub["classes"]) - set(I.SUB_LABELS):
            raise ValueError("weights contain unknown intent or sub-label classes")

    @classmethod
    def from_file(cls, path: Path | str) -> "SlmWeights":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))


def classify_vector(vector: list[float], weights: SlmWeights) -> tuple[dict[str, bool], dict[str, float], str,
                                                                         str | None, float]:
    """Return (flags, flag probabilities, intent, sub_label, confidence) for one normalised vector."""
    probs = {}
    for name in I.FLAGS:
        head = weights.flags.get(name)
        probs[name] = 0.0 if head is None else 1 / (1 + math.exp(-(_dot(head["w"], vector) + head["b"])))
    flags = {name: probs[name] >= threshold(name) for name in I.FLAGS}
    p = _softmax([_dot(w, vector) + b for w, b in zip(weights.intent["W"], weights.intent["b"])])
    k = max(range(len(p)), key=p.__getitem__)
    intent, confidence = weights.intent["classes"][k], p[k]
    sub = None
    if intent == I.OUT_OF_SCOPE:
        scores = [_dot(w, vector) + b for w, b in zip(weights.sub["W"], weights.sub["b"])]
        sub = weights.sub["classes"][max(range(len(scores)), key=scores.__getitem__)]
    return flags, probs, intent, sub, confidence


class SlmRecognizer:
    """Text -> Extraction via embedding + classifier heads.

    Args:
        embedder: implementation of core.ports.EmbedderPort.
        weights: loaded classifier heads; their dimension must match the embedder's vectors.
    """

    def __init__(self, embedder: EmbedderPort, weights: SlmWeights):
        self.embedder = embedder
        self.weights = weights
        self.model = f"slm:{getattr(embedder, 'model', '?')}"

    def __call__(self, text: str) -> Extraction:
        """Raises ConnectionError if the embedding service fails; ValueError on a dimension mismatch."""
        t0 = time.perf_counter()
        vector = self.embedder.embed([(text or "")[:MAX_CHARS]])[0]
        if self.weights.dim and len(vector) != self.weights.dim:
            raise ValueError(f"embedding has {len(vector)} dimensions, weights expect {self.weights.dim}")
        flags, _, intent, sub, conf = classify_vector(vector, self.weights)
        return Extraction(flags=flags, suggested_intent=intent, suggested_sub_label=sub, confidence=conf,
                          latency_s=time.perf_counter() - t0, model=self.model)
