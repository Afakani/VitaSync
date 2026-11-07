import json

import pytest

from vitasync.core import intent as I
from vitasync.core.intent import Policy
from vitasync.features.rule_pipeline import check_rules

RELAXED = Policy(symptom_with_data="allow", symptom_with_tip="allow", condition_named="general_plus_referral")


def flags(*true):
    return {name: name in true for name in I.FLAGS}


def test_crisis_wins_over_everything():
    r = check_rules(flags("self_harm_or_crisis", "acute_danger_signs", "asks_medication_advice"))
    assert r.decision == "crisis"
    assert r.rule is None and r.sub_label is None


def test_emergency_wins_over_forbidden_ask():
    r = check_rules(flags("acute_danger_signs", "asks_cause_or_diagnosis"))
    assert r.decision == "emergency"


@pytest.mark.parametrize("flag,sub,rule", [
    ("asks_score_or_rating", I.SCORE_REQUEST, "R1"),
    ("asks_value_evaluation", I.VALUE_EVALUATION, "R2"),
    ("asks_medication_advice", I.MEDICATION, "R4"),
    ("asks_cause_or_diagnosis", I.DIAGNOSIS_TRIAGE, "R4"),
    ("asks_pharmacy_interpretation", I.PHARMACY_SUMMARY, "R5"),
    ("asks_color_coding", I.COLOR_REQUEST, "R6"),
])
def test_each_forbidden_ask_blocks_with_its_rule(flag, sub, rule):
    r = check_rules(flags(flag, "asks_own_data"))
    assert (r.decision, r.sub_label, r.rule) == ("block", sub, rule)


def test_several_forbidden_asks_use_priority():
    r = check_rules(flags("asks_value_evaluation", "asks_medication_advice"))
    assert r.sub_label == I.MEDICATION
    assert "flag:asks_value_evaluation" in r.reasons


def test_symptom_alone_is_routed():
    r = check_rules(flags("symptom_mentioned"))
    assert (r.decision, r.sub_label) == ("block", I.DIAGNOSIS_TRIAGE)


@pytest.mark.parametrize("ask,switch", [("asks_own_data", "symptom_with_data"),
                                        ("asks_lifestyle_tip", "symptom_with_tip")])
def test_symptom_policy_switches(ask, switch):
    strict = check_rules(flags("symptom_mentioned", ask))
    relaxed = check_rules(flags("symptom_mentioned", ask), RELAXED)
    assert strict.decision == "block"
    assert relaxed.decision == "allow"
    assert f"policy:{switch}=allow" in relaxed.reasons


def test_symptom_diary_entry_is_allowed():
    r = check_rules(flags("symptom_mentioned", "asks_symptom_logging"))
    assert r.decision == "allow"


def test_symptom_with_app_question_is_allowed():
    assert check_rules(flags("symptom_mentioned", "asks_app_help")).decision == "allow"


def test_condition_named_strict_and_relaxed():
    strict = check_rules(flags("own_condition_named", "asks_general_knowledge"))
    relaxed = check_rules(flags("own_condition_named", "asks_general_knowledge"), RELAXED)
    assert strict.sub_label == I.DIAGNOSIS_TRIAGE
    assert relaxed.decision == "allow" and relaxed.add_referral


def test_no_intent_flag_is_unclear():
    r = check_rules(flags())
    assert r.decision == "unclear" and "no_intent_flag" in r.reasons


def test_unclear_flag_makes_allowed_unclear():
    assert check_rules(flags("asks_own_data", "message_unclear")).decision == "unclear"


def test_plain_data_question_is_allowed():
    r = check_rules(flags("asks_own_data"))
    assert r.decision == "allow" and r.flags == ("asks_own_data",)


def test_rule_json_is_serialisable_and_has_no_text():
    d = check_rules(flags("asks_value_evaluation")).to_dict()
    assert json.loads(json.dumps(d)) == d
    assert set(d) == {"decision", "rule", "sub_label", "reasons", "add_referral", "flags"}


def test_missing_flag_raises():
    with pytest.raises(KeyError):
        check_rules({"asks_own_data": True})


def test_policy_from_string():
    p = Policy.from_string("symptom_with_data=allow, min_confidence=0.5, clarify_enabled=false")
    assert (p.symptom_with_data, p.min_confidence, p.clarify_enabled) == ("allow", 0.5, False)
    assert Policy.from_string("") == Policy()
    with pytest.raises(ValueError):
        Policy.from_string("symptom_with_data=maybe")
    with pytest.raises(ValueError):
        Policy.from_string("unknown=1")
