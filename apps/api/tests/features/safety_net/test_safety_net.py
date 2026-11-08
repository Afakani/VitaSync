from pathlib import Path

import pytest

from vitasync.core import intent as I
from vitasync.core.intent import Policy, RouteDecision
from vitasync.features.safety_net import SafetyNet

TEAM_FILE = Path(__file__).resolve().parents[5] / "knowledge" / "rules" / "cp2_patterns.json"
NET = SafetyNet({"rules": [
    {"id": "V", "sub_label": I.VALUE_EVALUATION, "pattern": r"\bnormal\b", "requires": r"\bmein\b",
     "unless": r"^was ist normal"},
    {"id": "S", "sub_label": I.SCORE_REQUEST, "pattern": r"\bnote\b"},
]})


def test_hit_blocks_allowed_route():
    d = NET.apply(RouteDecision(route=I.DATA_QUERY), "Ist mein Puls normal?")
    assert (d.route, d.sub_label) == (I.OUT_OF_SCOPE, I.VALUE_EVALUATION)
    assert d.reasons[-1] == "cp2:V"


def test_requires_and_unless():
    assert NET.apply(RouteDecision(route=I.DATA_QUERY), "Ist der Puls normal?").route == I.DATA_QUERY
    assert NET.apply(RouteDecision(route=I.HEALTH_QUESTION), "Was ist normal fuer mein Alter?").route \
        == I.HEALTH_QUESTION


def test_clarify_is_also_blocked():
    assert NET.apply(RouteDecision(route=I.CLARIFY), "Welche Note?").sub_label == I.SCORE_REQUEST


@pytest.mark.parametrize("route", [I.OUT_OF_SCOPE, I.EMERGENCY, I.CRISIS])
def test_blocked_routes_unchanged(route):
    d = RouteDecision(route=route, sub_label=I.MEDICATION if route == I.OUT_OF_SCOPE else None)
    assert NET.apply(d, "Ist mein Puls normal?") is d


def test_switch_off():
    d = RouteDecision(route=I.DATA_QUERY)
    assert NET.apply(d, "Ist mein Puls normal?", Policy(safety_net=False)) is d


def test_bad_rules_rejected():
    with pytest.raises(ValueError):
        SafetyNet({"rules": [{"id": "X", "sub_label": "OTHER", "pattern": "a"}]})
    with pytest.raises(ValueError):
        SafetyNet({"rules": [{"id": "X", "sub_label": I.MEDICATION, "pattern": "("}]})


def test_team_file_loads():
    net = SafetyNet.from_file(TEAM_FILE)
    assert len(net.rules) == 10
