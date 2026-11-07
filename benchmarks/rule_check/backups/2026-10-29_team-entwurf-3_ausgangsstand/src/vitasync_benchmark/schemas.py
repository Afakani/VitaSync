"""Answer contract of the model and the deterministic decision derived from it.

The model fills in one status per rule; the JSON schema lists every rule as a
required key in rule order, so structured output forces all rules in that order.
``validate_verdict`` checks shape, keys and order. ``decide`` then derives the
decision in code: the first rule (in order) that is not "pass" decides. Nothing
is repaired: any deviation is an error.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, ValidationError

Status = Literal["pass", "block", "unclear"]
Decision = Literal["allow", "block", "unclear"]


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    checks: dict[str, Status]


class VerdictError(Exception):
    """The model answer is not a valid verdict (stored as invalid_response)."""


@dataclass(frozen=True)
class Outcome:
    decision: Decision
    blocked_by: str | None
    unclear_at: str | None


def response_json_schema(rule_ids: Sequence[str]) -> dict:
    """JSON schema for structured output: every rule ID required, in rule order."""
    status = {"type": "string", "enum": ["pass", "block", "unclear"]}
    return {
        "type": "object",
        "properties": {"checks": {"type": "object",
                                  "properties": {rid: status for rid in rule_ids},
                                  "required": list(rule_ids),
                                  "additionalProperties": False}},
        "required": ["checks"],
        "additionalProperties": False,
    }


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys):
        raise VerdictError(f"doppelte Schlüssel: {sorted({k for k in keys if keys.count(k) > 1})}")
    return dict(pairs)


def validate_verdict(raw: str, rule_ids: Sequence[str]) -> Verdict:
    """Parse and check one raw model answer against the ordered rule IDs.

    Raises VerdictError with a readable reason; never returns a corrected verdict.
    """
    try:
        data = json.loads(raw, object_pairs_hook=_no_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise VerdictError(f"kein gültiges JSON: {exc.msg}") from exc
    try:
        verdict = Verdict.model_validate(data, strict=True)
    except ValidationError as exc:
        reasons = "; ".join(f"{'.'.join(map(str, e['loc'])) or 'JSON'}: {e['msg']}" for e in exc.errors())
        raise VerdictError(f"Schema verletzt: {reasons}") from exc

    ids = list(verdict.checks)
    unknown = [i for i in ids if i not in rule_ids]
    if unknown:
        raise VerdictError(f"unbekannte Regel-IDs: {unknown}")
    missing = [i for i in rule_ids if i not in verdict.checks]
    if missing:
        raise VerdictError(f"Regeln fehlen: {missing}")
    if ids != list(rule_ids):
        raise VerdictError(f"Regeln nicht in Regelreihenfolge: {ids}")
    return verdict


def decide(verdict: Verdict, rule_ids: Sequence[str]) -> Outcome:
    """First non-pass rule in rule order decides; all pass means allow."""
    for rid in rule_ids:
        status = verdict.checks[rid]
        if status == "block":
            return Outcome("block", rid, None)
        if status == "unclear":
            return Outcome("unclear", None, rid)
    return Outcome("allow", None, None)
