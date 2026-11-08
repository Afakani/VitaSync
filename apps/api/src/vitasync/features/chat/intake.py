"""Message intake (part of M4): CP1 -> recognition -> rule pipeline -> routing -> CP2.

The only place that combines these modules, each through its public __init__.
Same order as the team router v0.5 (pipeline.py).
"""
from __future__ import annotations

from typing import Callable

from vitasync.core.intent import Extraction, Policy, RouteDecision
from vitasync.core.ports import ExtractionError
from vitasync.features.input_guard import InputGuard
from vitasync.features.routing import route, route_fallback, route_from_guard
from vitasync.features.rule_pipeline import check_rules
from vitasync.features.safety_net import SafetyNet

Recognize = Callable[[str], Extraction]


def route_message(text: str, guard: InputGuard, recognize: Recognize, policy: Policy | None = None,
                  net: SafetyNet | None = None) -> RouteDecision:
    """Route one user message.

    1. CP1 patterns; on an emergency or crisis hit no model is called.
    2. Recognition (SlmRecognizer or LlmRecognizer from features/recognition) returns flags.
    3. Rule pipeline turns flags into the rule result.
    4. Routing picks the route.
    5. CP2 safety net may still block an allowed route (if `net` is given and policy.safety_net is on).

    Args:
        text: the user message; treated as data, never as instructions. Not stored or logged here.
        guard: loaded CP1 patterns.
        recognize: callable text -> Extraction.
        policy: switches for open team decisions; defaults are conservative.
        net: loaded CP2 patterns; None = no CP2.

    Returns:
        RouteDecision (stage CP1, ROUTER or FALLBACK).

    Raises:
        ConnectionError: model or embedding service not reachable.
    """
    policy = policy or Policy()
    g = guard.check(text)
    fixed = route_from_guard(g)
    if fixed is not None:
        return fixed
    try:
        extraction = recognize(text)
    except ExtractionError as e:
        return route_fallback(g, error=str(e), model=getattr(recognize, "model", None))
    decision = route(check_rules(extraction.flags, policy), extraction, g, policy)
    return net.apply(decision, text, policy) if net is not None else decision
