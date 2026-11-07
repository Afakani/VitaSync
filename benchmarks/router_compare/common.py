"""Shared helpers for the router comparison scripts.

Loads question sets in the three formats used here and finds the team router.
Prints nothing; callers decide what to show (never question texts).
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RULE_CHECK = REPO / "benchmarks" / "rule_check"
GPT_BATCHES = RULE_CHECK / "data" / "router" / "gpt"
S310 = RULE_CHECK / "data" / "router" / "s3-10_v1.tsv"
PROMPTS_XLSX = RULE_CHECK / "data" / "prompts.xlsx"
RESULTS = HERE / "results"


def team_router_dir() -> Path:
    """Folder that contains the package `vitasync_router` (extracted vitasync-router.zip).

    Set VITASYNC_ROUTER_DIR, or extract the zip to benchmarks/router_compare/.team_router/.
    Raises SystemExit with a hint if the package is missing.
    """
    base = Path(os.environ.get("VITASYNC_ROUTER_DIR", HERE / ".team_router" / "vitasync-router"))
    if not (base / "vitasync_router").is_dir():
        raise SystemExit(f"Team-Router nicht gefunden unter {base}. vitasync-router.zip entpacken "
                         f"oder VITASYNC_ROUTER_DIR setzen (siehe README.md).")
    return base


def import_team_router() -> Path:
    """Put the team router on sys.path and return its folder."""
    base = team_router_dir()
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    return base


def load_questions(path: Path) -> list[dict]:
    """Return rows with at least `id`, `question`, `intent` (expected label).

    .tsv: team/ChatGPT batch format (id, question, intent, sub_label, use_case, symptomatic, note)
    .csv: same columns, comma separated
    .xlsx: rule_check format, sheet `Prompts`; `intent` = expected_decision, plus `category`,
           `expected_decision`, `expected_blocked_by`
    """
    path = Path(path)
    if path.suffix == ".xlsx":
        from openpyxl import load_workbook
        rows = list(load_workbook(path, read_only=True)["Prompts"].iter_rows(values_only=True))
        head = rows[0]
        out = []
        for r in rows[1:]:
            d = dict(zip(head, r))
            if not d.get("prompt_id"):
                continue
            out.append({"id": d["prompt_id"], "question": d["prompt"], "intent": d.get("expected_decision") or "",
                        "category": d.get("category") or "", "expected_decision": d.get("expected_decision") or "",
                        "expected_blocked_by": d.get("expected_blocked_by") or ""})
        return out
    delim = "\t" if path.suffix == ".tsv" else ","
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(fh, delimiter=delim)]
