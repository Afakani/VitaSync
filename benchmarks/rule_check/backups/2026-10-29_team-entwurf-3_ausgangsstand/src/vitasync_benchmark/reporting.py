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
