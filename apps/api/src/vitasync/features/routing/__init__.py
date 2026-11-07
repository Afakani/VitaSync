"""Routing: rule result + LLM suggestion + CP1 -> RouteDecision. Public API of this module."""
from vitasync.features.routing.router import path_for_allowed, route, route_fallback, route_from_guard

__all__ = ["path_for_allowed", "route", "route_fallback", "route_from_guard"]
