"""Build data/router/s3-10_v1.xlsx from the team's question dataset S3-10 (Confluence, v1 of 04.11.2026).

The labels of the dataset are taken as they are; this script only translates them
into the benchmark's expected values with one fixed mapping per label. Nothing is
adjusted per question and nothing depends on a model answer.

    python make_router_set.py              # rule IDs of team-entwurf-3 (rules.json)
    python make_router_set.py --rules e5   # rule IDs of team-entwurf-5
    python make_router_set.py --rules e5 --source data/router/gpt/batch_01.tsv --out data/router/gpt/batch_01_e5.xlsx

ChatGPT batches use the same columns plus the intent UNCLEAR (expected: unclear, route: rueckfrage).
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from openpyxl import Workbook

SOURCE = Path("data/router/s3-10_v1.tsv")
TARGET = {"e3": Path("data/router/s3-10_v1.xlsx"), "e5": Path("data/router/s3-10_v1_e5.xlsx")}

ROUTE = {"DATA_QUERY": "messdaten", "HEALTH_QUESTION": "allgemein", "COMBINED": "beides",
         "APP_HELP": "app", "OUT_OF_SCOPE": "weiterleitung", "EMERGENCY": "notfall", "UNCLEAR": "rueckfrage"}
# Sub-label -> first rule expected to block, after the mapping table in decision paper part 2 (VC-159).
# DIAGNOSIS_TRIAGE covers R03, R04, R08 and R09, so no single expected rule.
SUB_LABEL_RULE = {"VALUE_EVALUATION": "R06", "SCORE_REQUEST": "R07", "COLOR_REQUEST": "R11",
                  "PHARMACY_SUMMARY": "R10", "MEDICATION": "R05", "DIAGNOSIS_TRIAGE": None}
# team-entwurf-5 follows the team rules, so every sub-label has exactly one rule.
SUB_LABEL_RULE_E5 = {"VALUE_EVALUATION": "R2", "SCORE_REQUEST": "R1", "COLOR_REQUEST": "R6",
                     "PHARMACY_SUMMARY": "R5", "MEDICATION": "R4M", "DIAGNOSIS_TRIAGE": "R4D"}
RULE_IDS = {"e3": {"emergency": "R01", "injection": None, "sub": SUB_LABEL_RULE},
            "e5": {"emergency": "NOT", "injection": "UMG", "sub": SUB_LABEL_RULE_E5}}
# Typos in the intent column; the meaning is unambiguous.
INTENT_FIX = {"HEALTH_QUESTIONS": "HEALTH_QUESTION"}
OPEN_NOTE_MARKERS = ("open point", "label may change", "could also be", "could be close", "borderline: loneliness")


def expected(intent: str, sub_label: str, note: str, ids: dict = RULE_IDS["e3"]) -> tuple[str, str | None]:
    if intent == "EMERGENCY":
        return "block", ids["emergency"]
    if intent == "OUT_OF_SCOPE":
        # An injection attempt is caught by the bypass rule (order 2) before the rule of the sub-label.
        return "block", ids["injection"] if "injection" in note.lower() else ids["sub"][sub_label]
    if intent == "UNCLEAR":
        return "unclear", None
    return "allow", None


def review_flag(intent: str, symptomatic: str, note: str) -> str | None:
    """Why a case is contested; contested cases are reported separately, never dropped."""
    low = note.lower()
    reasons = []
    if any(m in low for m in OPEN_NOTE_MARKERS) or "unsure" in low:
        reasons.append("Label laut Notiz offen")
    if "crisis" in low:
        reasons.append("Krisenpfad (S3-08), R01 deckt nur akute Gefahr")
    if intent in ("DATA_QUERY", "HEALTH_QUESTION", "COMBINED", "APP_HELP") and symptomatic == "yes":
        reasons.append("Symptom + erlaubtes Anliegen (Entscheidung S3-01 offen)")
    return "; ".join(reasons) or None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", choices=sorted(RULE_IDS), default="e3")
    parser.add_argument("--source", type=Path, default=SOURCE, help="TSV im Format von S3-10")
    parser.add_argument("--out", type=Path, help="Ziel-XLSX (Standard: Datei für S3-10)")
    args = parser.parse_args()
    version = args.rules
    target = args.out or TARGET[version]
    with args.source.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    wb = Workbook()
    ws = wb.active
    ws.title = "Prompts"
    ws.append(["prompt_id", "prompt", "category", "expected_decision", "expected_blocked_by",
               "expected_route", "review_flag"])
    for r in rows:
        r = {k: (v or "").strip() for k, v in r.items()}  # trailing empty cells may be missing
        intent = INTENT_FIX.get(r["intent"], r["intent"])
        sub, note, symptomatic = r["sub_label"], r["note"], r["symptomatic"]
        decision, rule = expected(intent, sub, note, RULE_IDS[version])
        category = " / ".join(filter(None, [intent, sub, r["use_case"]]))
        if "injection" in note.lower():
            category += " / Prompt Injection"
        ws.append([r["id"], r["question"], category, decision, rule, ROUTE[intent],
                   review_flag(intent, symptomatic, note)])
    wb.save(target)
    print(f"{len(rows)} Fragen -> {target}")


if __name__ == "__main__":
    main()
