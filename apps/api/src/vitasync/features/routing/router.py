"""Rule result (+ LLM suggestion, CP1) -> route. Deterministic.

Principles (team router, ethical boundaries paper):
  - The rule result decides; routing never weakens a block.
  - The LLM suggestion may only escalate to a more conservative blocked route.
  - Fail closed: low confidence -> CLARIFY, injection -> OUT_OF_SCOPE, invalid output -> SAFE_DEFAULT.
"""
from __future__ import annotations

from vitasync.core import intent as I
from vitasync.core.intent import Extraction, GuardResult, Policy, RouteDecision, RuleResult


def path_for_allowed(flags: tuple[str, ...]) -> str | None:
    """Pick the allowed path from the true flags; None if no intent flag is set."""
    f = set(flags)
    wants_data = bool(f & {"asks_own_data", "asks_compilation_for_appointment"})
    wants_general = bool(f & {"asks_general_knowledge", "asks_lifestyle_tip"})
    has_data = wants_data or "asks_symptom_logging" in f
    if "asks_compilation_for_appointment" in f:
        return I.COMBINED
    if has_data and (wants_general or "asks_app_help" in f):
        return I.COMBINED
    if has_data:
        return I.DATA_QUERY
    if "asks_app_help" in f:
        return I.APP_HELP
    if wants_general:
        return I.HEALTH_QUESTION
    return None


def _base_route(rule: RuleResult) -> tuple[str, str | None]:
    if rule.decision == "crisis":
        return I.CRISIS, None
    if rule.decision == "emergency":
        return I.EMERGENCY, None
    if rule.decision == "block":
        return I.OUT_OF_SCOPE, rule.sub_label
    if rule.decision == "unclear":
        return I.CLARIFY, None
    path = path_for_allowed(rule.flags)
    return (path, None) if path else (I.CLARIFY, None)


def route(rule: RuleResult, extraction: Extraction, guard: GuardResult | None = None,
          policy: Policy | None = None) -> RouteDecision:
    """Choose the route for a message that went through the LLM.

    Args:
        rule: result of rule_pipeline.check_rules.
        extraction: validated LLM output (only suggestion and confidence are used here).
        guard: CP1 result (only injection matters here; emergency/crisis never reach this point).
        policy: same policy object the rule pipeline used.

    Returns:
        RouteDecision with stage ROUTER.
    """
    policy = policy or Policy()
    guard = guard or GuardResult()
    reasons = list(rule.reasons)
    current, sub = _base_route(rule)
    llm_route, llm_sub = extraction.suggested_intent, extraction.suggested_sub_label

    if (policy.llm_can_escalate and llm_route in I.BLOCKED_ROUTES
            and I.CONSERVATIVE_RANK[llm_route] > I.CONSERVATIVE_RANK[current]):
        current = llm_route
        sub = llm_sub if llm_route == I.OUT_OF_SCOPE else None
        reasons.append(f"llm_escalated:{llm_route}" + (f"/{sub}" if sub else ""))
    elif current == I.OUT_OF_SCOPE and sub is None and llm_route == I.OUT_OF_SCOPE:
        sub = llm_sub

    if current in I.ALLOWED_ROUTES and extraction.confidence < policy.min_confidence:
        reasons.append(f"low_confidence:{extraction.confidence:.2f}")
        current, sub = I.CLARIFY, None

    if guard.injection and policy.injection_fail_closed and current not in I.BLOCKED_ROUTES:
        reasons.append("cp1:injection_fail_closed")
        current, sub = I.OUT_OF_SCOPE, None

    if current == I.CLARIFY and not policy.clarify_enabled:
        reasons.append("clarify_disabled")
        current, sub = I.OUT_OF_SCOPE, None

    return RouteDecision(
        route=current,
        sub_label=sub if current == I.OUT_OF_SCOPE else None,
        stage="ROUTER",
        reasons=tuple(reasons),
        add_referral=rule.add_referral and current in I.ALLOWED_ROUTES,
        rule=rule,
        llm_intent=llm_route,
        llm_sub_label=llm_sub,
        confidence=extraction.confidence,
        cp1=guard,
        model=extraction.model,
    )


def route_from_guard(guard: GuardResult) -> RouteDecision | None:
    """CP1 hit -> fixed route without calling the LLM; None if CP1 did not block."""
    if not guard.blocked:
        return None
    current = I.CRISIS if guard.crisis else I.EMERGENCY
    return RouteDecision(route=current, stage="CP1",
                         reasons=tuple(f"cp1:{pid}" for pid in guard.crisis + guard.emergency), cp1=guard)


def route_fallback(guard: GuardResult, error: str, model: str | None = None) -> RouteDecision:
    """LLM output invalid after retry -> generic referral (SAFE_DEFAULT)."""
    return RouteDecision(route=I.OUT_OF_SCOPE, stage="FALLBACK", reasons=("extraction_failed",),
                         cp1=guard, model=model, error=error)
