"""Flags -> rule result. Deterministic; no LLM, no route choice.

Order of checks (taken from the team router, `rule_route`):
  1. crisis, 2. emergency (safety net behind CP1, always win),
  3. explicit forbidden asks (R1, R2, R4, R5, R6),
  4. symptom described without a forbidden ask (policy switches),
  5. own condition named (policy switch),
  6. otherwise allowed - or unclear if no intent flag is set or the message is unclear.
"""
from __future__ import annotations

from vitasync.core import intent as I
from vitasync.core.intent import Policy, RuleResult

# Flag -> sub-label for explicit forbidden asks, in the team's order.
_FORBIDDEN_ASKS = (
    ("asks_medication_advice", I.MEDICATION),
    ("asks_cause_or_diagnosis", I.DIAGNOSIS_TRIAGE),
    ("asks_pharmacy_interpretation", I.PHARMACY_SUMMARY),
    ("asks_color_coding", I.COLOR_REQUEST),
    ("asks_score_or_rating", I.SCORE_REQUEST),
    ("asks_value_evaluation", I.VALUE_EVALUATION),
)
_INTENT_FLAGS = ("asks_own_data", "asks_compilation_for_appointment", "asks_symptom_logging",
                 "asks_general_knowledge", "asks_lifestyle_tip", "asks_app_help")


def check_rules(flags: dict[str, bool], policy: Policy | None = None) -> RuleResult:
    """Apply R1-R6 and the crisis/emergency safety net to validated flags.

    Args:
        flags: one bool per name in core.intent.FLAGS (validated by recognition).
        policy: switches for open team decisions; defaults are conservative.

    Returns:
        RuleResult with decision crisis | emergency | block | allow | unclear.

    Raises:
        KeyError: a flag is missing (flags must be validated first).
    """
    policy = policy or Policy()
    f = {name: bool(flags[name]) for name in I.FLAGS}
    used = tuple(name for name in I.FLAGS if f[name])

    if f["self_harm_or_crisis"]:
        return RuleResult("crisis", reasons=("flag:self_harm_or_crisis",), flags=used)
    if f["acute_danger_signs"]:
        return RuleResult("emergency", reasons=("flag:acute_danger_signs",), flags=used)

    subs: list[str] = []
    reasons: list[str] = []
    for flag, sub in _FORBIDDEN_ASKS:
        if f[flag]:
            subs.append(sub)
            reasons.append(f"flag:{flag}")

    wants_data = f["asks_own_data"] or f["asks_compilation_for_appointment"]
    wants_general = f["asks_general_knowledge"] or f["asks_lifestyle_tip"]

    if f["symptom_mentioned"] and not subs:
        if f["asks_symptom_logging"] and not wants_general:
            reasons.append("symptom:diary_entry_allowed")
        elif wants_data:
            if policy.symptom_with_data == "route":
                subs.append(I.DIAGNOSIS_TRIAGE)
            reasons.append(f"policy:symptom_with_data={policy.symptom_with_data}")
        elif wants_general:
            if policy.symptom_with_tip == "route":
                subs.append(I.DIAGNOSIS_TRIAGE)
            reasons.append(f"policy:symptom_with_tip={policy.symptom_with_tip}")
        elif f["asks_app_help"]:
            reasons.append("symptom:app_question_allowed")
        else:
            subs.append(I.DIAGNOSIS_TRIAGE)
            reasons.append("symptom:only_symptom")

    add_referral = False
    if f["own_condition_named"] and not subs:
        if policy.condition_named == "route":
            subs.append(I.DIAGNOSIS_TRIAGE)
        else:
            add_referral = True
        reasons.append(f"policy:condition_named={policy.condition_named}")

    if subs:
        sub = next(s for s in I.SUB_LABEL_PRIORITY if s in subs)
        return RuleResult("block", rule=I.SUB_LABEL_RULE[sub], sub_label=sub, reasons=tuple(reasons), flags=used)

    if not any(f[name] for name in _INTENT_FLAGS):
        return RuleResult("unclear", reasons=(*reasons, "no_intent_flag"), flags=used)
    if f["message_unclear"]:
        return RuleResult("unclear", reasons=(*reasons, "flag:message_unclear"), flags=used)
    return RuleResult("allow", reasons=tuple(reasons), add_referral=add_referral, flags=used)
