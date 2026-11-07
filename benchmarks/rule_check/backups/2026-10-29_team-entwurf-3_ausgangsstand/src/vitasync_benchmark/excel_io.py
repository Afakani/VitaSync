"""Read the input workbook and write the result workbook.

The input file is opened read-only and never saved. Untrusted texts (prompts,
model output, error messages) are written as plain strings so Excel does not
evaluate them as formulas.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError

if TYPE_CHECKING:
    from .reporting import Row
    from .runner import CaseResult

SHEET = "Prompts"
REQUIRED = ("prompt_id", "prompt")
OPTIONAL = ("category", "expected_decision", "expected_blocked_by", "context_json")
DECISIONS = {"allow", "block", "unclear"}


class InputError(Exception):
    """The input workbook is unusable; raised before any model call."""


class ContextMessage(BaseModel):
    # Only user/assistant turns; a "system" turn could smuggle in instructions.
    model_config = ConfigDict(extra="forbid", strict=True)
    role: str
    content: str


@dataclass(frozen=True)
class PromptCase:
    row: int
    prompt_id: str
    prompt: str
    category: str | None = None
    expected_decision: str | None = None
    expected_blocked_by: str | None = None
    context: tuple[dict[str, str], ...] = ()


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_context(raw: str) -> tuple[dict[str, str], ...]:
    try:
        items = TypeAdapter(list[ContextMessage]).validate_json(raw)
    except ValidationError as exc:
        raise ValueError(f"context_json ungültig: {exc.errors()[0]['msg']}") from exc
    for item in items:
        if item.role not in ("user", "assistant"):
            raise ValueError(f"context_json: Rolle '{item.role}' nicht erlaubt (nur user/assistant)")
    return tuple({"role": i.role, "content": i.content} for i in items)


def read_prompts(path: Path, rule_ids: Iterable[str]) -> list[PromptCase]:
    """Validate the whole sheet first and report all problems at once."""
    rule_ids = set(rule_ids)
    try:
        wb = load_workbook(path, read_only=True, data_only=False)
    except FileNotFoundError as exc:
        raise InputError(f"Eingabedatei nicht gefunden: {path}") from exc
    try:
        if SHEET not in wb.sheetnames:
            raise InputError(f"Blatt '{SHEET}' fehlt in {path} (vorhanden: {wb.sheetnames})")
        rows = list(wb[SHEET].iter_rows(values_only=True))
    finally:
        wb.close()
    if not rows:
        raise InputError(f"Blatt '{SHEET}' ist leer")

    header = [(_text(h) or "") for h in rows[0]]
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        raise InputError(f"Pflichtspalten fehlen: {missing}")
    col = {name: header.index(name) for name in (*REQUIRED, *OPTIONAL) if name in header}

    errors: list[str] = []
    cases: list[PromptCase] = []
    seen: dict[str, int] = {}
    for number, values in enumerate(rows[1:], start=2):
        get = lambda name: _text(values[col[name]]) if name in col and col[name] < len(values) else None
        if all(_text(v) is None for v in values):
            continue
        pid, prompt = get("prompt_id"), get("prompt")
        exp, exp_by, ctx_raw = get("expected_decision"), get("expected_blocked_by"), get("context_json")
        row_errors = []
        if pid is None:
            row_errors.append("prompt_id leer")
        elif pid in seen:
            row_errors.append(f"prompt_id '{pid}' doppelt (zuerst Zeile {seen[pid]})")
        if prompt is None:
            row_errors.append("prompt leer")
        if exp is not None and exp not in DECISIONS:
            row_errors.append(f"expected_decision '{exp}' ungültig (allow, block, unclear)")
        if exp_by is not None:
            if exp != "block":
                row_errors.append("expected_blocked_by gesetzt, aber expected_decision ist nicht block")
            if exp_by not in rule_ids:
                row_errors.append(f"expected_blocked_by '{exp_by}' ist keine geprüfte Regel-ID")
        context: tuple[dict[str, str], ...] = ()
        if ctx_raw is not None:
            try:
                context = _parse_context(ctx_raw)
            except ValueError as exc:
                row_errors.append(str(exc))
        if row_errors:
            errors.append(f"Zeile {number}: " + "; ".join(row_errors))
            continue
        seen[pid] = number
        cases.append(PromptCase(number, pid, prompt, get("category"), exp, exp_by, context))

    if errors:
        raise InputError("Eingabedatei fehlerhaft:\n" + "\n".join(errors))
    if not cases:
        raise InputError("Keine Testfälle in der Eingabedatei")
    return cases


# ---------------------------------------------------------------- export

SYMBOL = {"pass": 1, "block": 0, "unclear": "?"}
NOT_SHOWN = "–"
WRAP = Alignment(wrap_text=True, vertical="top")


def _put(ws, row: int, col: int, value: object) -> None:
    cell = ws.cell(row=row, column=col)
    cell.value = value
    if isinstance(value, str):
        cell.data_type = "s"  # store as text even if it starts with "=" (no formula)


def _format(ws, widths: dict[int, int], wrap_cols: Iterable[int] = ()) -> None:
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "A2"
    if ws.max_row >= 1 and ws.max_column >= 1:
        ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width
    for col in wrap_cols:
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=col).alignment = WRAP


def _yes_no(value: bool | None) -> str:
    return "n/a" if value is None else ("ja" if value else "nein")


def write_results(path: Path, results: list["CaseResult"], rule_ids: list[str],
                  summary: list["Row"], run_info: list[tuple[str, object]],
                  overview: list[tuple[str, str]] = (), overview_note: str = "") -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"
    head = ["run_id", "prompt_id", "prompt", "category", "expected_decision", "expected_blocked_by",
            "decision", *rule_ids, "blocked_by", "unclear_at", "request_duration_ms", "started_at_utc",
            "decision_correct", "blocking_rule_correct", "outcome", "error_type", "error_message"]
    for c, name in enumerate(head, 1):
        _put(ws, 1, c, name)
    for r, res in enumerate(results, 2):
        statuses = dict(res.checks or [])
        rule_cells = ([SYMBOL[statuses[i]] if i in statuses else NOT_SHOWN for i in rule_ids]
                      if res.outcome == "valid" else [None] * len(rule_ids))
        values = [res.run_id, res.prompt_id, res.prompt, res.category, res.expected_decision,
                  res.expected_blocked_by, res.decision, *rule_cells, res.blocked_by, res.unclear_at,
                  round(res.request_duration_ms, 3), res.started_at_utc,
                  _yes_no(res.decision_correct), _yes_no(res.blocking_rule_correct),
                  res.outcome, res.error_type, res.error_message]
        for c, v in enumerate(values, 1):
            _put(ws, r, c, v)
        ws.cell(row=r, column=head.index("request_duration_ms") + 1).number_format = "0.000"
    widths = {i + 1: 14 for i in range(len(head))}
    widths.update({3: 60, head.index("error_message") + 1: 50, head.index("started_at_utc") + 1: 26})
    _format(ws, widths, wrap_cols=(3, head.index("error_message") + 1))

    ws = wb.create_sheet("Summary")
    # Overview first, then the unchanged detail table below it.
    _put(ws, 1, 1, "Kennzahl")
    _put(ws, 1, 2, "Ergebnis")
    for r, (metric, result) in enumerate(overview, 2):
        _put(ws, r, 1, metric)
        _put(ws, r, 2, result)
    row = len(overview) + 2
    if overview_note:
        _put(ws, row + 1, 1, overview_note)
        ws.cell(row=row + 1, column=1).alignment = WRAP
        ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=5)
        ws.row_dimensions[row + 1].height = 45
        row += 3
    detail_header = row
    for c, name in enumerate(("Bereich", "Kennzahl", "Wert", "Anteil %", "Nenner"), 1):
        _put(ws, detail_header, c, name)
    for r, item in enumerate(summary, detail_header + 1):
        for c, v in enumerate((item.section, item.metric, item.value, item.share, item.denominator), 1):
            _put(ws, r, c, v)
    for cell in (*ws[1], *ws[detail_header]):
        cell.font = Font(bold=True)
    for col, width in {1: 50, 2: 44, 3: 16, 4: 12, 5: 44}.items():
        ws.column_dimensions[get_column_letter(col)].width = width

    ws = wb.create_sheet("Run_Info")
    _put(ws, 1, 1, "Feld")
    _put(ws, 1, 2, "Wert")
    for r, (key, value) in enumerate(run_info, 2):
        _put(ws, r, 1, key)
        _put(ws, r, 2, value if isinstance(value, (int, float)) or value is None
             else (json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)))
    _format(ws, {1: 34, 2: 110}, wrap_cols=(2,))

    wb.save(path)
