r"""Vergleicht mehrere Läufe nebeneinander (gleiche Eingabedatei vorausgesetzt).

Aufruf: .venv\Scripts\python.exe compare_runs.py outputs\<lauf1> outputs\<lauf2> ...
Der erste Lauf ist die Basis für die Laufzeitveränderung. Liest nur results.jsonl.
"""
import dataclasses
import json
import statistics
import sys
from pathlib import Path

from vitasync_benchmark.reporting import overview, quality_rows
from vitasync_benchmark.runner import CaseResult

FIELDS = {f.name for f in dataclasses.fields(CaseResult)}
KEEP = ("Technisch gültige Antworten", "Entscheidung entspricht dem eingetragenen Sollwert",
        "Erlaubte Anfragen korrekt zugelassen", "Zu blockierende Anfragen tatsächlich blockiert",
        "Mehrdeutige Anfragen als unclear erkannt", "Median der Aufrufdauer")


def load(run_dir: Path) -> list[CaseResult]:
    lines = (run_dir / "results.jsonl").read_text(encoding="utf-8").splitlines()
    return [CaseResult(**{k: v for k, v in json.loads(line).items() if k in FIELDS}) for line in lines]


def main(dirs: list[str]) -> None:
    base_mean = None
    for d in map(Path, dirs):
        results = load(d)
        rows = dict(overview(results, len(results)))
        print(f"== {d.name}  ({len(results)} Fälle)")
        for key in KEEP:
            print(f"  {key}: {rows[key]}")
        for key, value in quality_rows(results):
            print(f"  {key}: {value}")
        valid = [r.request_duration_ms for r in results if r.outcome == "valid"]
        if valid:
            mean = statistics.fmean(valid)
            delta = "" if base_mean is None else f"  ({(mean - base_mean) / 1000:+.3f} s, {100 * (mean / base_mean - 1):+.1f} %)"
            base_mean = base_mean or mean
            print(f"  Mittlere Aufrufdauer: {mean / 1000:.3f} s{delta}".replace(".", ","))


if __name__ == "__main__":
    main(sys.argv[1:])
