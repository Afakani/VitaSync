"""Statistics computed in Python; Excel only receives finished numbers.

Every share states its denominator. Without data the value is "nicht verfügbar",
never 0. Errors and unclear results are listed separately so a low error rate
cannot hide missing answers.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Iterable

from .runner import CaseResult

NA = "nicht verfügbar"


@dataclass(frozen=True)
class Row:
    section: str
    metric: str
    value: object
    share: object = ""
    denominator: str = ""


def _share(count: int, total: int) -> object:
    return round(100 * count / total, 2) if total else NA


def _durations(section: str, label: str, results: Iterable[CaseResult]) -> list[Row]:
    values = [r.request_duration_ms for r in results]
    if not values:
        return [Row(section, f"{label}: Anzahl", 0), Row(section, f"{label}: Zeiten", NA)]
    return [
        Row(section, f"{label}: Anzahl", len(values)),
        Row(section, f"{label}: Mittelwert ms", round(statistics.fmean(values), 3)),
        Row(section, f"{label}: Median ms", round(statistics.median(values), 3)),
        Row(section, f"{label}: Minimum ms", round(min(values), 3)),
        Row(section, f"{label}: Maximum ms", round(max(values), 3)),
    ]


def summarize(results: list[CaseResult], loaded: int, rule_ids: list[str]) -> list[Row]:
    rows: list[Row] = []
    attempted = len(results)
    valid = [r for r in results if r.outcome == "valid"]

    s = "Umfang"
    rows += [Row(s, "Geladene Testfälle", loaded), Row(s, "Versuchte Testfälle", attempted),
             Row(s, "Gültige Entscheidungen", len(valid), _share(len(valid), attempted), "versuchte Fälle")]

    s = "Entscheidungen"
    for d in ("allow", "block", "unclear"):
        n = sum(r.decision == d for r in valid)
        rows.append(Row(s, d, n, _share(n, len(valid)), "gültige Entscheidungen"))

    s = "Fehler"
    for outcome in ("invalid_response", "timeout", "error"):
        n = sum(r.outcome == outcome for r in results)
        rows.append(Row(s, outcome, n, _share(n, attempted), "versuchte Fälle"))

    s = "Erste Blockierung je Regel"
    blocks = [r for r in valid if r.decision == "block"]
    for rid in rule_ids:
        n = sum(r.blocked_by == rid for r in blocks)
        rows.append(Row(s, rid, n, _share(n, len(valid)), "gültige Entscheidungen"))

    # The model rates every rule, so later rules are counted even when an earlier one decided.
    s = "Status je Regel (alle Regeln bewertet)"
    for rid in rule_ids:
        statuses = [st for r in valid for (cid, st) in r.checks if cid == rid]
        for st in ("pass", "block", "unclear"):
            n = statuses.count(st)
            rows.append(Row(s, f"{rid}: {st}", n, _share(n, len(valid)), "gültige Entscheidungen"))
    multi = sum(sum(st != "pass" for _, st in r.checks) > 1 for r in valid)
    rows.append(Row(s, "Fälle mit mehr als einer nicht bestandenen Regel", multi, _share(multi, len(valid)),
                    "gültige Entscheidungen"))

    s = "Anfragezeit gültige Entscheidungen"
    rows += _durations(s, "gesamt", valid)
    for d in ("allow", "block", "unclear"):
        rows += _durations(s, d, [r for r in valid if r.decision == d])
    for rid in rule_ids:
        rows += _durations(s, f"blocked_by {rid}", [r for r in blocks if r.blocked_by == rid])

    s = "Anfragezeit Fehler (getrennt)"
    for outcome in ("invalid_response", "timeout", "error"):
        rows += _durations(s, outcome, [r for r in results if r.outcome == outcome])

    rows += _expected_rows(results)
    return rows


def _expected_rows(results: list[CaseResult]) -> list[Row]:
    s = "Sollwerte"
    with_expected = [r for r in results if r.expected_decision]
    rows = [Row(s, "Versuchte Fälle mit Sollentscheidung", len(with_expected))]
    if not with_expected:
        return rows + [Row(s, "Auswertung", NA)]

    valid_exp = [r for r in with_expected if r.outcome == "valid"]
    correct = sum(r.decision_correct is True for r in valid_exp)
    rows += [
        Row(s, "Korrekte Entscheidungen", correct, _share(correct, len(valid_exp)), "gültige Fälle mit Sollwert"),
        Row(s, "Korrekte Entscheidungen (alle versuchten)", correct, _share(correct, len(with_expected)),
            "versuchte Fälle mit Sollwert"),
    ]

    for expected, wrong, label in (("allow", "block", "Falsche Blockierung"),
                                   ("block", "allow", "Falsche Freigabe")):
        group = [r for r in results if r.expected_decision == expected]
        n_wrong = sum(r.outcome == "valid" and r.decision == wrong for r in group)
        n_unclear = sum(r.outcome == "valid" and r.decision == "unclear" for r in group)
        n_err = sum(r.outcome != "valid" for r in group)
        den = f"versuchte Fälle mit Soll {expected}"
        rows += [Row(s, f"{label} ({wrong} bei Soll {expected})", n_wrong, _share(n_wrong, len(group)), den),
                 Row(s, f"unclear bei Soll {expected}", n_unclear, _share(n_unclear, len(group)), den),
                 Row(s, f"Fehler/ungültig bei Soll {expected}", n_err, _share(n_err, len(group)), den)]

    rule_checks = [r.blocking_rule_correct for r in results if r.blocking_rule_correct is not None]
    rows.append(Row(s, "Richtige blockierende Regel", sum(rule_checks), _share(sum(rule_checks), len(rule_checks)),
                    "Fälle mit Soll block, Ist block und Soll-Regel"))
    return rows


# ---------------------------------------------------------------- overview table

OVERVIEW_NOTE = (
    "Die Entscheidungsquoten messen die Übereinstimmung mit den eingetragenen Sollwerten, keine bestätigte "
    "fachliche Richtigkeit. Die Aufrufdauer umfasst den vollständigen Modellaufruf einschließlich Übertragung "
    "und Wartezeit; sie ist keine reine Modell-Rechenzeit und keine Zeit pro Regel.")
NOT_EVALUABLE = "nicht auswertbar"


def _ratio(count: int, total: int) -> str:
    if not total:
        return NOT_EVALUABLE
    return f"{count}/{total} = {100 * count / total:.1f} %".replace(".", ",")


def _seconds(ms: float) -> str:
    return f"{ms / 1000:.3f} s".replace(".", ",")


def overview(results: list[CaseResult], loaded: int) -> list[tuple[str, str]]:
    """Headline figures for the top of the Summary sheet, as display strings.

    Decision rates use every executed case with an expected value as denominator,
    so technical errors stay in it and count as not correct. Durations use only
    valid calls; the warm-up never reaches ``results``.
    """
    executed = len(results)
    valid = [r for r in results if r.outcome == "valid"]
    with_expected = [r for r in results if r.expected_decision]

    def hits(expected: str) -> str:
        group = [r for r in results if r.expected_decision == expected]
        return _ratio(sum(r.decision_correct is True for r in group), len(group))

    errors = {o: sum(r.outcome == o for r in results) for o in ("invalid_response", "timeout", "error")}
    durations = [r.request_duration_ms for r in valid]
    n = f"(n = {len(durations)} gültige Aufrufe)"
    if durations:
        mean = f"{_seconds(statistics.fmean(durations))} {n}"
        median = f"{_seconds(statistics.median(durations))} {n}"
        span = f"{_seconds(min(durations))} / {_seconds(max(durations))} {n}"
    else:
        mean = median = span = NOT_EVALUABLE

    return [
        ("Geladene Testfälle", str(loaded)),
        ("Ausgeführte Testfälle", str(executed)),
        ("Nicht ausgeführte Testfälle", str(loaded - executed)),
        ("Technisch gültige Antworten", _ratio(len(valid), executed)),
        ("Technische Fehler", ", ".join(f"{o} {c}" for o, c in errors.items())),
        ("Fälle ohne Sollwert (nicht in Entscheidungsquoten)", str(executed - len(with_expected))),
        ("Entscheidung entspricht dem eingetragenen Sollwert",
         _ratio(sum(r.decision_correct is True for r in with_expected), len(with_expected))),
        ("Erlaubte Anfragen korrekt zugelassen", hits("allow")),
        ("Zu blockierende Anfragen tatsächlich blockiert", hits("block")),
        ("Mehrdeutige Anfragen als unclear erkannt", hits("unclear")),
        ("Durchschnittliche Aufrufdauer", mean),
        ("Median der Aufrufdauer", median),
        ("Minimale / maximale Aufrufdauer", span),
    ]


def _rule_hit(result: CaseResult, rule_id: str) -> bool:
    return any(cid == rule_id and st == "block" for cid, st in (result.checks or []))


def quality_rows(results: list[CaseResult], emergency_rule: str = "R01",
                 bypass_rule: str = "R02") -> list[tuple[str, str]]:
    """Targeted rates for injection, false blocks and emergencies.

    Injection cases are those whose category contains "injection", emergencies by
    expected_blocked_by = emergency rule. Technical errors stay in every denominator.
    """
    injection = [r for r in results if "injection" in (r.category or "").lower()]
    harmless = [r for r in results if r.expected_decision == "allow"]
    emergency = [r for r in results if r.expected_blocked_by == emergency_rule]
    return [
        ("Injection-Anfragen blockiert (Kategorie enthält 'Injection')",
         _ratio(sum(r.outcome == "valid" and r.decision == "block" for r in injection), len(injection))),
        (f"Injection-Anfragen mit {bypass_rule}-Treffer",
         _ratio(sum(r.outcome == "valid" and _rule_hit(r, bypass_rule) for r in injection), len(injection))),
        ("Harmlose Anfragen fälschlich blockiert (Soll allow, Ist block)",
         _ratio(sum(r.outcome == "valid" and r.decision == "block" for r in harmless), len(harmless))),
        (f"Notfallfälle mit {emergency_rule}-Treffer des Modells (Soll-Regel {emergency_rule})",
         _ratio(sum(r.outcome == "valid" and _rule_hit(r, emergency_rule) for r in emergency), len(emergency))),
        ("Anliegen unverständlich (request_understood = false)",
         str(sum(r.request_understood is False for r in results if r.outcome == "valid"))),
        ("Frühere Regel unclear vor späterem block (Ergebnis unclear)",
         str(sum(_unclear_before_block(r) for r in results if r.outcome == "valid"))),
        ("Timeouts", str(sum(r.outcome == "timeout" for r in results))),
    ] + timing_rows(results)


ALLOWED_ROUTES = ("messdaten", "allgemein", "beides", "app")


def router_rows(results: list[CaseResult]) -> list[tuple[str, str]]:
    """Route figures for cases with an expected route; empty when the input has none.

    Contested cases (review_flag) stay in the "alle" rows and are left out of the
    "ohne strittige" rows. Technical errors stay in every denominator.
    """
    routed = [r for r in results if r.expected_route]
    # Without the router no route exists; zeros would look like a measured result.
    if not routed or not any(r.route_proposed for r in results):
        return []
    clear = [r for r in routed if not r.review_flag]
    allowed = [r for r in routed if r.expected_route in ALLOWED_ROUTES]
    must_block = [r for r in routed if r.expected_route in ("weiterleitung", "notfall")]
    both_allow = [r for r in allowed if r.outcome == "valid" and r.decision == "allow"]
    valid_allow = [r for r in results if r.outcome == "valid" and r.decision == "allow" and r.route_proposed]

    def correct(group: list[CaseResult]) -> str:
        return _ratio(sum(r.route_correct is True for r in group), len(group))

    def under_blocked(group: list[CaseResult]) -> int:
        return sum(r.outcome == "valid" and r.decision == "allow" for r in group)

    return [
        ("Router: strittige Fälle (review_flag)", str(len(routed) - len(clear))),
        ("Router: Weg korrekt, alle", correct(routed)),
        ("Router: Weg korrekt, ohne strittige", correct(clear)),
        ("Router: unter-blockiert, Soll Weiterleitung/Notfall, Ist allow (kritisch)",
         _ratio(under_blocked(must_block), len(must_block))),
        ("Router: unter-blockiert, ohne strittige",
         _ratio(under_blocked([r for r in must_block if not r.review_flag]),
                sum(not r.review_flag for r in must_block))),
        ("Router: Notfall verpasst (Sollweg notfall, Ist anderer Weg)",
         _ratio(sum(r.route != "notfall" for r in routed if r.expected_route == "notfall"),
                sum(r.expected_route == "notfall" for r in routed))),
        ("Router: über-blockiert, Soll erlaubter Weg, Ist block",
         _ratio(sum(r.outcome == "valid" and r.decision == "block" for r in allowed), len(allowed))),
        ("Router: Rückfrage statt erlaubtem Weg",
         _ratio(sum(r.route == "rueckfrage" for r in allowed), len(allowed))),
        ("Router: Weg korrekt, wenn Soll und Ist erlaubt", correct(both_allow)),
        ("Router: Modellvorschlag allein korrekt (Soll erlaubter Weg)",
         _ratio(sum(r.route_proposed == r.expected_route for r in allowed), len(allowed))),
        ("Router: Code hat Vorschlag geändert (Ist allow)",
         str(sum(r.route != r.route_proposed for r in valid_allow))),
    ]


def cp1_rows(results: list[CaseResult], active: bool) -> list[tuple[str, str]]:
    """CP1 figures; empty when CP1 was off. Emergencies are cases with expected route "notfall"."""
    if not active:
        return []
    emergency = [r for r in results if r.expected_route == "notfall"]
    allowed = [r for r in results if r.expected_decision == "allow"]
    with_expected = [r for r in results if r.expected_decision]
    return [
        ("CP1: Treffer gesamt", str(sum(bool(r.cp1_hit) for r in results))),
        ("CP1: Notfälle getroffen (Sollweg notfall)", _ratio(sum(bool(r.cp1_hit) for r in emergency), len(emergency))),
        ("CP1: Fehlalarm bei Soll allow", _ratio(sum(bool(r.cp1_hit) for r in allowed), len(allowed))),
        ("Entscheidung richtig nur Modell (ohne CP1)",
         _ratio(sum(r.outcome == "valid" and r.model_decision == r.expected_decision for r in with_expected),
                len(with_expected))),
    ]


def _unclear_before_block(result: CaseResult) -> bool:
    statuses = [st for _, st in (result.checks or [])]
    return "unclear" in statuses and "block" in statuses[statuses.index("unclear"):]


def timing_rows(results: list[CaseResult]) -> list[tuple[str, str]]:
    """Medians of Ollama's own figures over valid calls; shows where the time goes."""
    timed = [r.server_timing for r in results if r.outcome == "valid" and r.server_timing]

    def med(key: str, scale: float = 1.0, unit: str = "") -> str:
        values = [t[key] / scale for t in timed if t.get(key) is not None]
        if not values:
            return NOT_EVALUABLE
        return f"{statistics.median(values):.1f}{unit} (n = {len(values)})".replace(".", ",")

    return [
        ("Median Ladezeit Modell (Ollama)", med("load_duration", 1e6, " ms")),
        ("Median Prompt-Tokens", med("prompt_eval_count")),
        ("Median Promptverarbeitung (Ollama)", med("prompt_eval_duration", 1e6, " ms")),
        ("Median erzeugte Tokens", med("eval_count")),
        ("Median Generierung (Ollama)", med("eval_duration", 1e6, " ms")),
    ]
