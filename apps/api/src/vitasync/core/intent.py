"""Shared types for message intake: flags, rule result, route decision, policy.

Labels follow the team's labelling guide (VC-69) and flowcharts (S3-07a/b).
The logic is taken from the team router (vitasync-router) and split into
modules: recognition -> rule_pipeline -> routing. This file only holds the
data types every module agrees on; no module logic lives here.

Standard library only (see core/AGENTS.md).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Literal

# --- Routes (labelling guide 1.1 + flowchart paths) -----------------------
DATA_QUERY = "DATA_QUERY"
HEALTH_QUESTION = "HEALTH_QUESTION"
COMBINED = "COMBINED"
APP_HELP = "APP_HELP"
OUT_OF_SCOPE = "OUT_OF_SCOPE"
EMERGENCY = "EMERGENCY"
CRISIS = "CRISIS"      # crisis path, fixed S3-08 texts, no LLM
CLARIFY = "CLARIFY"    # one clarifying question (CB-32)

#: Intents the LLM may suggest (CRISIS and CLARIFY are routes only).
INTENTS = (DATA_QUERY, HEALTH_QUESTION, COMBINED, APP_HELP, OUT_OF_SCOPE, EMERGENCY)
ROUTES = INTENTS + (CRISIS, CLARIFY)
ALLOWED_ROUTES = frozenset({DATA_QUERY, HEALTH_QUESTION, COMBINED, APP_HELP})
BLOCKED_ROUTES = frozenset({OUT_OF_SCOPE, EMERGENCY, CRISIS})

#: Higher = more conservative. EMERGENCY > OUT_OF_SCOPE > CLARIFY > HEALTH > COMBINED > APP/DATA.
CONSERVATIVE_RANK = {EMERGENCY: 6, CRISIS: 6, OUT_OF_SCOPE: 5, CLARIFY: 4, HEALTH_QUESTION: 3,
                     COMBINED: 2, APP_HELP: 1, DATA_QUERY: 1}

# --- OUT_OF_SCOPE sub-labels and the rule (R1-R6) behind each -------------
SCORE_REQUEST = "SCORE_REQUEST"
VALUE_EVALUATION = "VALUE_EVALUATION"
MEDICATION = "MEDICATION"
DIAGNOSIS_TRIAGE = "DIAGNOSIS_TRIAGE"
PHARMACY_SUMMARY = "PHARMACY_SUMMARY"
COLOR_REQUEST = "COLOR_REQUEST"

SUB_LABELS = (SCORE_REQUEST, VALUE_EVALUATION, MEDICATION, DIAGNOSIS_TRIAGE, PHARMACY_SUMMARY, COLOR_REQUEST)
SUB_LABEL_RULE = {SCORE_REQUEST: "R1", VALUE_EVALUATION: "R2", MEDICATION: "R4", DIAGNOSIS_TRIAGE: "R4",
                  PHARMACY_SUMMARY: "R5", COLOR_REQUEST: "R6"}
#: If several sub-labels apply, the first one here picks the template.
SUB_LABEL_PRIORITY = (MEDICATION, DIAGNOSIS_TRIAGE, PHARMACY_SUMMARY, COLOR_REQUEST, SCORE_REQUEST,
                      VALUE_EVALUATION)

# --- Flags the LLM sets (it recognises WHAT is asked, never decides) -------
FLAGS = (
    "symptom_mentioned",
    "asks_cause_or_diagnosis",
    "asks_value_evaluation",
    "asks_score_or_rating",
    "asks_color_coding",
    "asks_medication_advice",
    "asks_pharmacy_interpretation",
    "asks_own_data",
    "asks_symptom_logging",
    "asks_compilation_for_appointment",
    "asks_general_knowledge",
    "asks_lifestyle_tip",
    "asks_app_help",
    "own_condition_named",
    "acute_danger_signs",
    "self_harm_or_crisis",
    "message_unclear",
)


def more_conservative(a: str, b: str) -> str:
    """Return the more conservative of two routes; ties keep `a`."""
    return a if CONSERVATIVE_RANK[a] >= CONSERVATIVE_RANK[b] else b


@dataclass(frozen=True)
class Extraction:
    """Validated LLM output: flags plus the model's own (untrusted) suggestion.

    Attributes:
        flags: one bool per name in FLAGS.
        suggested_intent: one of INTENTS.
        suggested_sub_label: one of SUB_LABELS or None.
        confidence: 0..1, self-reported by the model.
        latency_s: wall time of the model call in seconds, if measured.
        model: model name from configuration, if known.
    """

    flags: dict[str, bool]
    suggested_intent: str
    suggested_sub_label: str | None
    confidence: float
    latency_s: float | None = None
    model: str | None = None

    def true_flags(self) -> list[str]:
        return [name for name in FLAGS if self.flags.get(name)]


@dataclass(frozen=True)
class GuardResult:
    """CP1 hits as pattern ids per section. No user text is kept."""

    emergency: tuple[str, ...] = ()
    crisis: tuple[str, ...] = ()
    injection: tuple[str, ...] = ()

    @property
    def blocked(self) -> bool:
        """True if the message goes straight to a fixed template without the LLM."""
        return bool(self.emergency or self.crisis)

    def to_dict(self) -> dict:
        return {"emergency": list(self.emergency), "crisis": list(self.crisis), "injection": list(self.injection)}


Decision = Literal["crisis", "emergency", "block", "allow", "unclear"]


@dataclass(frozen=True)
class RuleResult:
    """Output of the rule pipeline: which rule applies, before any routing.

    Attributes:
        decision: crisis | emergency | block | allow | unclear.
        rule: R1-R6 for a block, None otherwise.
        sub_label: OUT_OF_SCOPE sub-label for a block, None otherwise.
        reasons: machine-readable reasons (flag names, policy switches); no user text.
        add_referral: allowed, but the answer must add a referral (condition named).
        flags: the true flags the decision was based on.
    """

    decision: Decision
    rule: str | None = None
    sub_label: str | None = None
    reasons: tuple[str, ...] = ()
    add_referral: bool = False
    flags: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """The rule JSON handed to routing and to the audit trail."""
        d = asdict(self)
        d["reasons"] = list(self.reasons)
        d["flags"] = list(self.flags)
        return d


Stage = Literal["CP1", "ROUTER", "FALLBACK"]


@dataclass(frozen=True)
class RouteDecision:
    """Final route of one message.

    Attributes:
        route: one of ROUTES.
        sub_label: only for OUT_OF_SCOPE; None there means generic referral (SAFE_DEFAULT).
        stage: CP1 (fixed pattern, no LLM), ROUTER (rules + routing) or FALLBACK (LLM output invalid).
        reasons: machine-readable reasons, no user text.
        add_referral: answer on an allowed path must add a referral.
        rule: the rule result this route came from (None for CP1 and FALLBACK).
        llm_intent / llm_sub_label / confidence: the model's suggestion, for evaluation only.
        cp1: CP1 pattern ids.
        model: model name, if the LLM was called.
        error: short error text for FALLBACK, never user text.
    """

    route: str
    sub_label: str | None = None
    stage: Stage = "ROUTER"
    reasons: tuple[str, ...] = ()
    add_referral: bool = False
    rule: RuleResult | None = None
    llm_intent: str | None = None
    llm_sub_label: str | None = None
    confidence: float | None = None
    cp1: GuardResult = field(default_factory=GuardResult)
    model: str | None = None
    error: str | None = None

    @property
    def template(self) -> str:
        """Flowchart node (S3-07a/b) that handles this route."""
        if self.route == EMERGENCY:
            return "TEMPLATE_EMERGENCY"
        if self.route == CRISIS:
            return "TEMPLATE_CRISIS"
        if self.route == CLARIFY:
            return "TEMPLATE_CLARIFY"
        if self.route == OUT_OF_SCOPE:
            return f"TEMPLATE_OOS_{self.sub_label}" if self.sub_label else "SAFE_DEFAULT"
        return f"PATH_{self.route}"

    def audit_record(self) -> dict:
        """Labels and decisions only: no user text, no flags, no values (I5)."""
        return {
            "stage": self.stage,
            "route": self.route,
            "sub_label": self.sub_label,
            "rule": SUB_LABEL_RULE.get(self.sub_label) if self.sub_label else None,
            "template": self.template,
            "cp1_pattern_ids": list(self.cp1.emergency) + list(self.cp1.crisis),
            "injection_suspected": bool(self.cp1.injection),
            "fallback": self.stage == "FALLBACK",
            "model": self.model,
        }


@dataclass(frozen=True)
class Policy:
    """Switches for open team decisions (ADR-0004 open items, VC-84).

    Defaults are the conservative team defaults.

    Attributes:
        symptom_with_data: "route" (DIAGNOSIS_TRIAGE) or "allow" for symptom + own data.
        symptom_with_tip: "route" or "allow" for symptom + general tip.
        condition_named: "route" or "general_plus_referral" when the user names an own condition.
        llm_can_escalate: the LLM suggestion may make the route more conservative (never less).
        min_confidence: below this, an allowed route becomes CLARIFY.
        clarify_enabled: off -> CLARIFY becomes OUT_OF_SCOPE.
        injection_fail_closed: CP1 injection hit + allowed route -> OUT_OF_SCOPE.
    """

    symptom_with_data: Literal["route", "allow"] = "route"
    symptom_with_tip: Literal["route", "allow"] = "route"
    condition_named: Literal["route", "general_plus_referral"] = "route"
    llm_can_escalate: bool = True
    min_confidence: float = 0.6
    clarify_enabled: bool = True
    injection_fail_closed: bool = True

    @classmethod
    def from_string(cls, spec: str) -> "Policy":
        """Build from 'key=value,key=value' (e.g. from ROUTER_POLICY). Empty -> defaults.

        Raises:
            ValueError: unknown key or invalid value.
        """
        known = {f.name: f for f in fields(cls)}
        values: dict = {}
        for item in filter(None, (part.strip() for part in (spec or "").split(","))):
            key, sep, raw = item.partition("=")
            key, raw = key.strip(), raw.strip()
            if not sep or key not in known:
                raise ValueError(f"unknown policy entry {item!r}")
            default = getattr(cls, key)
            if isinstance(default, bool):
                if raw.lower() not in ("true", "false"):
                    raise ValueError(f"{key} must be true or false")
                values[key] = raw.lower() == "true"
            elif isinstance(default, float):
                values[key] = float(raw)
            else:
                values[key] = raw
        policy = cls(**values)
        policy.validate()
        return policy

    def validate(self) -> None:
        """Raises ValueError if a switch has a value the rules do not know."""
        if self.symptom_with_data not in ("route", "allow"):
            raise ValueError("symptom_with_data must be route or allow")
        if self.symptom_with_tip not in ("route", "allow"):
            raise ValueError("symptom_with_tip must be route or allow")
        if self.condition_named not in ("route", "general_plus_referral"):
            raise ValueError("condition_named must be route or general_plus_referral")
        if not 0 <= self.min_confidence <= 1:
            raise ValueError("min_confidence must be between 0 and 1")
