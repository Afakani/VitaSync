import json

import pytest

from vitasync.core import intent as I
from vitasync.core.intent import Extraction, GuardResult, Policy, RuleResult
from vitasync.features.routing import path_for_allowed, route, route_fallback, route_from_guard


def ext(intent=I.HEALTH_QUESTION, sub=None, confidence=0.9):
    return Extraction(flags={n: False for n in I.FLAGS}, suggested_intent=intent, suggested_sub_label=sub,
                      confidence=confidence, model="fake")


def allow(*flags, add_referral=False):
    return RuleResult("allow", flags=flags, add_referral=add_referral)


@pytest.mark.parametrize("flags,expected", [
    (("asks_own_data",), I.DATA_QUERY),
    (("asks_symptom_logging",), I.DATA_QUERY),
    (("asks_general_knowledge",), I.HEALTH_QUESTION),
    (("asks_lifestyle_tip",), I.HEALTH_QUESTION),
    (("asks_app_help",), I.APP_HELP),
    (("asks_own_data", "asks_lifestyle_tip"), I.COMBINED),
    (("asks_own_data", "asks_app_help"), I.COMBINED),
    (("asks_compilation_for_appointment",), I.COMBINED),
])
def test_allowed_paths(flags, expected):
    assert path_for_allowed(flags) == expected
    assert route(allow(*flags), ext()).route == expected


def test_block_keeps_sub_label_and_llm_cannot_weaken():
    rule = RuleResult("block", rule="R2", sub_label=I.VALUE_EVALUATION)
    d = route(rule, ext(intent=I.DATA_QUERY))
    assert (d.route, d.sub_label, d.template) == (I.OUT_OF_SCOPE, I.VALUE_EVALUATION, "TEMPLATE_OOS_VALUE_EVALUATION")


def test_llm_may_escalate_allowed_to_blocked():
    d = route(allow("asks_own_data"), ext(intent=I.OUT_OF_SCOPE, sub=I.MEDICATION))
    assert (d.route, d.sub_label) == (I.OUT_OF_SCOPE, I.MEDICATION)
    assert any(r.startswith("llm_escalated") for r in d.reasons)


def test_llm_escalation_can_be_switched_off():
    d = route(allow("asks_own_data"), ext(intent=I.OUT_OF_SCOPE), policy=Policy(llm_can_escalate=False))
    assert d.route == I.DATA_QUERY


def test_llm_choice_between_allowed_routes_is_ignored():
    assert route(allow("asks_own_data"), ext(intent=I.COMBINED)).route == I.DATA_QUERY


def test_low_confidence_asks_back():
    d = route(allow("asks_own_data"), ext(confidence=0.3))
    assert d.route == I.CLARIFY


def test_injection_never_takes_allowed_path():
    d = route(allow("asks_app_help"), ext(), guard=GuardResult(injection=("INJ-01",)))
    assert (d.route, d.sub_label, d.template) == (I.OUT_OF_SCOPE, None, "SAFE_DEFAULT")


def test_unclear_and_clarify_switch():
    rule = RuleResult("unclear")
    assert route(rule, ext()).route == I.CLARIFY
    assert route(rule, ext(), policy=Policy(clarify_enabled=False)).route == I.OUT_OF_SCOPE


@pytest.mark.parametrize("decision,expected", [("crisis", I.CRISIS), ("emergency", I.EMERGENCY)])
def test_safety_decisions(decision, expected):
    assert route(RuleResult(decision), ext(intent=I.DATA_QUERY, confidence=0.1)).route == expected


def test_referral_only_on_allowed_route():
    assert route(allow("asks_general_knowledge", add_referral=True), ext()).add_referral
    assert not route(allow("asks_general_knowledge", add_referral=True), ext(confidence=0.1)).add_referral


def test_guard_routes_without_llm():
    assert route_from_guard(GuardResult()) is None
    d = route_from_guard(GuardResult(emergency=("EM-01",), crisis=("CR-01",)))
    assert (d.route, d.stage) == (I.CRISIS, "CP1")
    assert route_from_guard(GuardResult(emergency=("EM-01",))).route == I.EMERGENCY


def test_fallback_is_safe_default():
    d = route_fallback(GuardResult(), error="invalid JSON at position 0", model="fake")
    assert (d.route, d.stage, d.template) == (I.OUT_OF_SCOPE, "FALLBACK", "SAFE_DEFAULT")


def test_audit_record_has_labels_only():
    d = route(RuleResult("block", rule="R4", sub_label=I.MEDICATION), ext(), GuardResult(injection=("INJ-02",)))
    rec = d.audit_record()
    assert json.loads(json.dumps(rec)) == rec
    assert set(rec) == {"stage", "route", "sub_label", "rule", "template", "cp1_pattern_ids",
                        "injection_suspected", "fallback", "model"}
    assert rec["rule"] == "R4" and rec["injection_suspected"] is True
