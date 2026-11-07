"""Erzeugt eine leere Eingabe-Excel mit Auswahllisten passend zu einer Regeldatei.

Aufruf: .venv\\Scripts\\python.exe make_template.py [--rules rules.json] [--output data\\prompts.xlsx] [--rows 500]
Eine vorhandene Ausgabedatei wird nicht überschrieben.
"""
import argparse
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation

from vitasync_benchmark.config import ConfigError, load_rules

HERE = Path(__file__).parent
COLUMNS = [
    ("prompt_id", 12, "Pflicht. Eindeutige ID, z. B. P001."),
    ("prompt", 70, "Pflicht. Die Nutzernachricht, die geprüft wird. Nur synthetische Texte, keine echten Daten."),
    ("category", 20, "Optional. Freie Gruppe für die Auswertung, z. B. Diagnose, Daten anzeigen, Lifestyle."),
    ("expected_decision", 18, "Optional. Sollwert: allow, block oder unclear. Leer = wird nicht bewertet."),
    ("expected_blocked_by", 20, "Optional. Nur bei block: ID der Regel, die zuerst blockieren soll."),
    ("context_json", 40, 'Optional. Vorheriger Verlauf als JSON, z. B. [{"role": "user", "content": "Hallo"}]. '
                         "Nur Rollen user und assistant."),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rules", type=Path, default=HERE / "rules.json")
    parser.add_argument("--output", type=Path, default=HERE / "data" / "prompts.xlsx")
    parser.add_argument("--rows", type=int, default=500, help="Zeilen mit Auswahllisten (Standard 500)")
    args = parser.parse_args()

    if args.output.exists():
        print(f"Abbruch: {args.output} existiert bereits und wird nicht überschrieben.", file=sys.stderr)
        return 2
    try:
        ruleset, _ = load_rules(args.rules)
    except ConfigError as exc:
        print(f"Regeldatei ungültig: {exc}", file=sys.stderr)
        return 2
    rules = ruleset.input_rules

    wb = Workbook()
    ws = wb.active
    ws.title = "Prompts"
    ws.append([name for name, _, _ in COLUMNS])
    for index, (_, width, _) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=index)
        cell.font = Font(bold=True)
        ws.column_dimensions[cell.column_letter].width = width
    last = args.rows + 1
    # Text format: an entry like "=1+1" stays text instead of becoming a formula.
    for row in ws.iter_rows(min_row=2, max_row=last, max_col=len(COLUMNS)):
        for cell in row:
            cell.number_format = "@"
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"

    lists = wb.create_sheet("Listen")
    lists.append(["decision", "rule_id", "title"])
    for i, value in enumerate(["allow", "block", "unclear"], start=2):
        lists.cell(row=i, column=1, value=value)
    for i, rule in enumerate(rules, start=2):
        lists.cell(row=i, column=2, value=rule.id)
        lists.cell(row=i, column=3, value=rule.title)
    lists.sheet_state = "hidden"

    decision = DataValidation(type="list", formula1="=Listen!$A$2:$A$4", allow_blank=True,
                              error="Nur allow, block oder unclear.", showErrorMessage=True)
    blocked_by = DataValidation(type="list", formula1=f"=Listen!$B$2:$B${len(rules) + 1}", allow_blank=True,
                                error="Nur Regel-IDs aus der Regeldatei.", showErrorMessage=True)
    decision.add(f"D2:D{last}")
    blocked_by.add(f"E2:E{last}")
    ws.add_data_validation(decision)
    ws.add_data_validation(blocked_by)

    info = wb.create_sheet("Hinweise")
    info.append(["Spalte", "Bedeutung"])
    for name, _, text in COLUMNS:
        info.append([name, text])
    info.append([])
    info.append(["Regeln", f"{args.rules.name}, Version {ruleset.version}"])
    for rule in rules:
        info.append([rule.id, rule.title])
    info.append([])
    info.append(["Hinweis", "Nur das Blatt 'Prompts' wird eingelesen. Spaltennamen in Zeile 1 nicht ändern."])
    info.column_dimensions["A"].width = 22
    info.column_dimensions["B"].width = 100
    for cell in info[1]:
        cell.font = Font(bold=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
