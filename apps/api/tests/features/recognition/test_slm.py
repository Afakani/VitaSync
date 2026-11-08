import math
from pathlib import Path

import pytest

from vitasync.adapters.embedding import FakeEmbedder, normalise
from vitasync.core import intent as I
from vitasync.features.recognition import SlmRecognizer, SlmWeights, classify_vector
from vitasync.features.recognition.slm import threshold

WEIGHTS_FILE = Path(__file__).resolve().parents[3] / "models" / "slm_lr_qwen3-embedding-8b.json"
DIM = 4


def weights(flag_bias: dict[str, float], intent_scores=(0.0, 1.0), sub=I.VALUE_EVALUATION):
    """Flag probability = sigmoid(bias); vector is ignored by zero weights."""
    return SlmWeights({
        "dim": DIM,
        "flags": {f: {"w": [0.0] * DIM, "b": b} for f, b in flag_bias.items()},
        "intent": {"classes": [I.DATA_QUERY, I.OUT_OF_SCOPE], "W": [[0.0] * DIM, [0.0] * DIM],
                   "b": list(intent_scores)},
        "sub": {"classes": [I.MEDICATION, sub], "W": [[0.0] * DIM, [0.0] * DIM], "b": [0.0, 1.0]},
    })


def logit(p):
    return math.log(p / (1 - p))


def test_thresholds_match_team_v05():
    assert threshold("acute_danger_signs") == 0.35
    assert threshold("asks_value_evaluation") == 0.7
    assert threshold("asks_own_data") == 0.5


def test_safety_flag_set_from_035_other_from_05():
    w = weights({"asks_cause_or_diagnosis": logit(0.4), "asks_own_data": logit(0.4)})
    flags, probs, *_ = classify_vector([0.0] * DIM, w)
    assert flags["asks_cause_or_diagnosis"] and not flags["asks_own_data"]
    assert probs["symptom_mentioned"] == 0.0  # missing head -> probability 0


def test_intent_confidence_and_sub_label():
    _, _, intent, sub, conf = classify_vector([0.0] * DIM, weights({}, intent_scores=(0.0, 1.0)))
    assert intent == I.OUT_OF_SCOPE and sub == I.VALUE_EVALUATION
    assert conf == pytest.approx(math.exp(1) / (1 + math.exp(1)))
    _, _, intent, sub, _ = classify_vector([0.0] * DIM, weights({}, intent_scores=(1.0, 0.0)))
    assert intent == I.DATA_QUERY and sub is None


def test_recognizer_cuts_text_and_checks_dimension():
    long_text = "x" * 1500
    rec = SlmRecognizer(FakeEmbedder({"x" * 1000: [1, 0, 0, 0]}), weights({}))
    assert rec(long_text).suggested_intent == I.OUT_OF_SCOPE
    bad = SlmRecognizer(FakeEmbedder({}, default=[1, 0, 0]), weights({}))
    with pytest.raises(ValueError):
        bad("Hallo")


def test_unknown_classes_are_rejected():
    with pytest.raises(ValueError):
        SlmWeights({"flags": {"unknown": {"w": [], "b": 0}}, "intent": {"classes": []}, "sub": {"classes": []}})


def test_normalise():
    assert normalise([3, 4]) == [0.6, 0.8]


def test_team_weights_load():
    w = SlmWeights.from_file(WEIGHTS_FILE)
    assert w.dim == 4096 and set(w.flags) == set(I.FLAGS)
    assert w.source["backend"] == "api:qwen-qwen3-embedding-8b"
