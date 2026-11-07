"""Answer contract of the model and the deterministic decision derived from it.

The model fills in one status per rule; the JSON schema lists every rule as a
required key in rule order, so structured output forces all rules in that order.
``validate_verdict`` checks shape, keys and order. ``decide`` then derives the
decision in code: the first rule (in order) that is not "pass" decides. Nothing
is repaired: any deviation is an error.

``request_understood`` is false when the request's concern cannot be made out.
It only turns an all-pass result into "unclear"; it never hides a rule violation.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, ValidationError

Status = Literal["pass", "block", "unclear"]
Decision = Literal["allow", "block", "unclear"]
ProposedRoute = Literal["messdaten", "allgemein", "beides", "app"]
ROUTES = ("messdaten", "allgemein", "beides", "app", "weiterleitung", "notfall", "rueckfrage")


class RouterInfo(BaseModel):
    """Facts copied from the request for the next step; never an assessment."""
    model_config = ConfigDict(extra="forbid", strict=True)

    messgroessen: list[str]
    zeitraum: str | None
    symptome_genannt: bool
    fuer_andere_person: bool


class RouterInfoSmall(BaseModel):
    """Reduced facts for layout "vor_regeln_klein": only what the next step needs."""
    model_config = ConfigDict(extra="forbid", strict=True)

    messgroessen: list[str]
    symptome_genannt: bool


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    checks: dict[str, Status]
    request_understood: bool | None = None
    route: ProposedRoute | None = None
    info: RouterInfo | RouterInfoSmall | None = None


UNDERSTOOD_REASON = "Anliegen unverständlich"
DECISION_PROCEDURE = (
    "Erste nicht-pass-Regel entscheidet: Die Regeln werden in order-Reihenfolge durchgegangen; die erste "
    "Regel mit block oder unclear bestimmt das Ergebnis. Meldet eine frühere Regel unclear und eine spätere "
    "block, lautet das Ergebnis unclear (unclear_at = frühere Regel); der spätere block bleibt in den "
    "Regelspalten sichtbar und wird in der Übersicht gezählt. Das Verfahren 'jeder block hat Vorrang' wird "
    "NICHT verwendet. Sind alle pass und request_understood = false, lautet das Ergebnis unclear "
    "(Anliegen unverständlich).")


class VerdictError(Exception):
    """The model answer is not a valid verdict (stored as invalid_response)."""


@dataclass(frozen=True)
class Outcome:
    decision: Decision
    blocked_by: str | None
    unclear_at: str | None
    reason: str


def response_json_schema(rule_ids: Sequence[str], with_understood: bool = False,
                         with_router: bool = False, router_first: bool = False) -> dict:
    """JSON schema for structured output: every rule ID required, in rule order.

    Optional parts follow the checks, so the rules are rated before anything else is
    generated; with ``router_first`` route and a reduced info come before the checks.
    """
    status = {"type": "string", "enum": ["pass", "block", "unclear"]}
    schema = {
        "type": "object",
        "properties": {"checks": {"type": "object",
                                  "properties": {rid: status for rid in rule_ids},
                                  "required": list(rule_ids),
                                  "additionalProperties": False}},
        "required": ["checks"],
        "additionalProperties": False,
    }
    if with_understood:
        schema["properties"]["request_understood"] = {"type": "boolean"}
        schema["required"].append("request_understood")
    if with_router:
        schema["properties"]["route"] = {"type": "string", "enum": list(ProposedRoute.__args__)}
        schema["properties"]["info"] = {
            "type": "object",
            "properties": {"messgroessen": {"type": "array", "items": {"type": "string"}},
                           "zeitraum": {"type": ["string", "null"]},
                           "symptome_genannt": {"type": "boolean"},
                           "fuer_andere_person": {"type": "boolean"}},
            "required": ["messgroessen", "zeitraum", "symptome_genannt", "fuer_andere_person"],
            "additionalProperties": False,
        }
        schema["required"] += ["route", "info"]
        if router_first:
            info = schema["properties"]["info"]
            for name in ("zeitraum", "fuer_andere_person"):
                del info["properties"][name]
                info["required"].remove(name)
            # Ollama generates keys in schema order: put route and info first.
            order = ["route", "info"] + [k for k in schema["properties"] if k not in ("route", "info")]
            schema["properties"] = {k: schema["properties"][k] for k in order}
            schema["required"] = [k for k in order if k in schema["required"]]
    return schema


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys):
        raise VerdictError(f"doppelte Schlüssel: {sorted({k for k in keys if keys.count(k) > 1})}")
    return dict(pairs)


def validate_verdict(raw: str, rule_ids: Sequence[str], with_understood: bool = False,
                     with_router: bool = False, router_first: bool = False) -> Verdict:
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

    if with_understood and verdict.request_understood is None:
        raise VerdictError("request_understood fehlt oder ist kein Boolean")
    if not with_understood and "request_understood" in data:
        raise VerdictError("unerwartetes Feld request_understood")
    for name in ("route", "info"):
        if with_router and getattr(verdict, name) is None:
            raise VerdictError(f"{name} fehlt")
        if not with_router and name in data:
            raise VerdictError(f"unerwartetes Feld {name}")
    if with_router and isinstance(verdict.info, RouterInfo if router_first else RouterInfoSmall):
        raise VerdictError("info hat nicht die Felder dieses Router-Aufbaus")

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
    """First non-pass rule in rule order decides; all pass and understood means allow.

    All pass but request_understood false gives "unclear" without a rule ID.
    """
    for rid in rule_ids:
        status = verdict.checks[rid]
        if status == "block":
            return Outcome("block", rid, None, f"Regel {rid}")
        if status == "unclear":
            return Outcome("unclear", None, rid, f"Regel {rid} unklar")
    if verdict.request_understood is False:
        return Outcome("unclear", None, None, UNDERSTOOD_REASON)
    return Outcome("allow", None, None, "alle Regeln pass")


ROUTE_PROCEDURE = (
    "Der Weg wird im Code festgelegt, der Modellvorschlag nur gelesen: block durch die Notfallregel (order 1) "
    "-> notfall; jeder andere "
    "block -> weiterleitung (feste Vorlage); unclear -> rueckfrage; allow -> vorgeschlagener Weg, außer "
    "messdaten/beides ohne genannte Messgröße -> rueckfrage. Der Vorschlag kann keinen block aufheben. Im Produkt "
    "erkennt den Notfall zuerst die feste Stichwortliste (CP1) vor jedem Modellaufruf; hier gibt es sie nicht.")


def route_for(outcome: Outcome, verdict: Verdict, emergency_rule: str = "R01") -> tuple[str, str]:
    """Final route and the reason, derived from the decision; the model's route is only a proposal."""
    if outcome.decision == "block":
        if outcome.blocked_by == emergency_rule:
            return "notfall", "Regel R01"
        return "weiterleitung", f"Regel {outcome.blocked_by}"
    if outcome.decision == "unclear":
        return "rueckfrage", outcome.reason
    if verdict.route in ("messdaten", "beides") and not verdict.info.messgroessen:
        return "rueckfrage", "Messdaten ohne genannte Messgröße"
    return verdict.route, "Vorschlag übernommen"
