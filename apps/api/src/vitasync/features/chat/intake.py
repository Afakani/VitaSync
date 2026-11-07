"""Message intake (part of M4): CP1 -> recognition -> rule pipeline -> routing.

The only place that combines these modules, each through its public __init__.
"""
from __future__ import annotations

from vitasync.core.intent import Policy, RouteDecision
from vitasync.core.ports import ExtractionError, IntentExtractorPort
from vitasync.features.input_guard import InputGuard
from vitasync.features.recognition import extract_flags
from vitasync.features.routing import route, route_fallback, route_from_guard
from vitasync.features.rule_pipeline import check_rules


def route_message(text: str, guard: InputGuard, extractor: IntentExtractorPort,
                  policy: Policy | None = None, retries: int = 1) -> RouteDecision:
    """Route one user message.

    1. CP1 patterns; on an emergency or crisis hit the LLM is not called.
    2. LLM recognises flags (validated, one retry).
    3. Rule pipeline turns flags into the rule result.
    4. Routing picks the route.

    Args:
        text: the user message; treated as data, never as instructions. Not stored or logged here.
        guard: loaded CP1 patterns.
        extractor: implementation of the LLM port.
        policy: switches for open team decisions; defaults are conservative.
        retries: extra attempts on invalid model output.

    Returns:
        RouteDecision (stage CP1, ROUTER or FALLBACK).

    Raises:
        ConnectionError: model server not reachable.
    """
    policy = policy or Policy()
    g = guard.check(text)
    fixed = route_from_guard(g)
    if fixed is not None:
        return fixed
    try:
        extraction = extract_flags(text, extractor, retries=retries)
    except ExtractionError as e:
        return route_fallback(g, error=str(e), model=getattr(extractor, "model", None))
    rule = check_rules(extraction.flags, policy)
    return route(rule, extraction, g, policy)
