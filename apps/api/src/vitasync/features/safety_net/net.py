"""CP2 safety net: fixed word patterns applied AFTER routing (team router v0.5, safety_net.py).

A hit moves an allowed route or CLARIFY to OUT_OF_SCOPE/<sub_label>. It can only block, never allow.
Pattern file: {"version", "rules": [{id, sub_label, pattern, requires?, unless?}]}, regex on the same
normalised text as CP1. A miss is not a confirmation that the request is allowed.
"""
from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path

from vitasync.core import intent as I
from vitasync.core.intent import Policy, RouteDecision
from vitasync.features.input_guard import normalise  # same normalisation as CP1


class SafetyNet:
    """Loaded CP2 rules. Build once, call `apply` per routed message."""

    def __init__(self, patterns: dict):
        """Raises ValueError on a missing field, an unknown sub-label or a bad regex."""
        self.version = str(patterns.get("version", "?"))
        self.rules = []
        for r in patterns.get("rules", []):
            if r.get("sub_label") not in I.SUB_LABELS:
                raise ValueError(f"CP2 rule {r.get('id')}: unknown sub_label")
            try:
                self.rules.append((r["id"], r["sub_label"], re.compile(r["pattern"]),
                                   re.compile(r["requires"]) if r.get("requires") else None,
                                   re.compile(r["unless"]) if r.get("unless") else None))
            except (KeyError, re.error) as e:
                raise ValueError(f"CP2 rule {r.get('id')} invalid: {e}") from e

    @classmethod
    def from_file(cls, path: Path | str) -> "SafetyNet":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def check(self, text: str) -> list[tuple[str, str]]:
        """Return (rule id, sub_label) of every rule that hits. The text is not stored."""
        norm = normalise(text)
        return [(rid, sub) for rid, sub, rx, req, unless in self.rules
                if rx.search(norm) and (req is None or req.search(norm)) and not (unless and unless.search(norm))]

    def apply(self, decision: RouteDecision, text: str, policy: Policy | None = None) -> RouteDecision:
        """Block an allowed route or CLARIFY on a hit; blocked routes and policy.safety_net=false pass unchanged."""
        policy = policy or Policy()
        if not policy.safety_net or decision.route in I.BLOCKED_ROUTES:
            return decision
        hits = self.check(text)
        if not hits:
            return decision
        return replace(decision, route=I.OUT_OF_SCOPE, sub_label=hits[0][1], add_referral=False,
                       reasons=(*decision.reasons, "cp2:" + ",".join(h[0] for h in hits)))
