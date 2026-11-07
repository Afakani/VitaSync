"""Command line entry point: validate everything, run, export.

Example:
    python -m vitasync_benchmark.cli --input data/prompts.example.xlsx \
        --rules rules.example.json --config config.json --output-dir outputs --limit 5
"""
from __future__ import annotations

import argparse
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Callable

from .config import Config, ConfigError, load_config, load_rules, sha256_file
from .cp1 import Cp1
from .excel_io import InputError, read_prompts, write_results
from .llm_client import LLMClient, OllamaClient
from .prompt import template_sha256
from .runlock import RunLock, RunLocked
from .schemas import DECISION_PROCEDURE, ROUTE_PROCEDURE
from .reporting import OVERVIEW_NOTE, cp1_rows, overview, quality_rows, router_rows, summarize
from .runner import CaseResult, JsonlWriter, run_cases, utc_now, warmup

MEASUREMENT_NOTE = (
    "request_duration_ms = perf_counter_ns direkt vor bis direkt nach dem nicht streamenden Modellaufruf. "
    "Enthält Client-Aufruf, Übertragung, Server-Wartezeit, Modellverarbeitung und Empfang. "
    "Nicht enthalten: Excel-Ein-/Ausgabe, Aufbau des Requests, eigene JSON-Validierung. "
    "Keine reine Modell-Rechenzeit und keine Zeit je Regel.")
CASCADE_NOTE = (
    "Das Modell bewertet in EINEM Aufruf jede Regel: 1 = pass, 0 = block, ? = unclear. Die Entscheidung "
    "berechnet der Code: Die erste Regel in order-Reihenfolge, die nicht pass ist, entscheidet. Eine 0 hinter "
    "blocked_by heißt, dass diese Regel auch angeschlagen hätte. Die Werte sind ausgegebene "
    "Modellentscheidungen, keine bestätigte fachliche Richtigkeit. Bei Fehlern bleiben die Regelzellen leer.")
AUTHORIZATION_NOTE = (
    "decision ist nur eine Einstufung der Anfrage. allow gewährt keine Zugriffs-, Schreib- oder Löschrechte. "
    "Dieser Benchmark führt keine Datenzugriffe und keine Löschungen aus. Im Backend müssen Identität, "
    "Zugriffsrechte und Löschziel unabhängig vom Modell geprüft werden; Anlegen und Ändern ist technisch "
    "gesperrt (siehe README, Integrationsanforderungen).")


def _gpu_snapshot() -> str:
    """Load of the GPU from nvidia-smi, if present; diagnostics only."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu",
                              "--format=csv,noheader"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or "fehlend"
    except (OSError, subprocess.TimeoutExpired):
        return "fehlend (nvidia-smi nicht verfügbar)"


def _versions() -> dict[str, str]:
    out = {"python": platform.python_version()}
    for pkg in ("openpyxl", "pydantic", "ollama", "httpx"):
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            out[pkg] = "nicht installiert"
    return out


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="vitasync_benchmark", description="LLM-Regelprüfung mit Excel-Auswertung")
    p.add_argument("--input", required=True, type=Path, help="Eingabe-XLSX mit Blatt 'Prompts'")
    p.add_argument("--rules", required=True, type=Path, help="Regeldatei (JSON)")
    p.add_argument("--config", required=True, type=Path, help="Konfiguration (JSON)")
    p.add_argument("--output-dir", required=True, type=Path, help="Oberordner für Läufe")
    p.add_argument("--limit", type=int, help="nur die ersten N Testfälle (Probelauf)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None,
         client_factory: Callable[[Config], LLMClient] = OllamaClient, lock_path: Path | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        ruleset, rules_hash = load_rules(args.rules)
        rules = ruleset.input_rules
        rule_ids = [r.id for r in rules]
        cases = read_prompts(args.input, rule_ids)
        if config.cp1_patterns:
            Cp1.load(Path(config.cp1_patterns))  # fail before any model call
    except (ConfigError, InputError) as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 2
    if args.limit is not None:
        if args.limit < 1:
            print("FEHLER: --limit muss mindestens 1 sein", file=sys.stderr)
            return 2
        cases_to_run = cases[: args.limit]
    else:
        cases_to_run = cases

    lock = RunLock(lock_path)
    try:
        lock.acquire()
    except RunLocked as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 2

    started = datetime.now(timezone.utc)
    run_id = f"{started:%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
    run_dir = args.output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    client = client_factory(config)
    info: list[tuple[str, object]] = [
        ("run_id", run_id), ("Beginn UTC", started.isoformat(timespec="seconds")),
        ("Ausführung", "sequenziell, ein Modellaufruf pro Testfall, keine Wiederholungen, keine Historie zwischen Fällen"),
        ("Messfenster", MEASUREMENT_NOTE), ("Regelspalten", CASCADE_NOTE),
        ("Bedeutung von allow", AUTHORIZATION_NOTE),
        ("Provider", config.provider), ("Server", config.base_url),
        ("Modell", client.describe_model(config.model)),
        ("Modellparameter", {"temperature": config.temperature, "think": config.think, "num_ctx": config.num_ctx}),
        ("Hinweis Temperatur", "Temperatur 0 reduziert Variation, garantiert aber keine identischen Entscheidungen."),
        ("Timeout s", config.timeout_seconds), ("Warm-up", config.warmup),
        ("Regelversion", ruleset.version), ("Regeldatei SHA-256", rules_hash),
        ("Geprüfte Eingaberegeln", rule_ids),
        ("Nicht geprüfte Antwortregeln", [r.id for r in ruleset.answer_rules] or "keine"),
        ("Eingabedatei", str(args.input)), ("Eingabedatei SHA-256", sha256_file(args.input)),
        ("Prüfauftrag-Variante", config.prompt_variant), ("request_understood aktiv", config.request_understood),
        ("Entscheidungsverfahren", DECISION_PROCEDURE),
        ("Router aktiv", config.router), ("Router-Aufbau", config.router_layout if config.router else "–"),
        ("Wegeverfahren", ROUTE_PROCEDURE if config.router else "nicht aktiv"),
        ("CP1 (feste Notfallmuster vor dem Modell)",
         f"{config.cp1_patterns}, SHA-256 {sha256_file(Path(config.cp1_patterns))}. Treffer -> block 'CP1' und Weg "
         "notfall; das Modell wird trotzdem aufgerufen, sein Ergebnis steht in model_decision"
         if config.cp1_patterns else "nicht aktiv"),
        ("GPU vor dem Lauf (nvidia-smi)", _gpu_snapshot()),
        ("Prüfauftrag-Template SHA-256", template_sha256(config)), ("Paketversionen", _versions()),
        ("Limit", args.limit if args.limit is not None else "keins"),
    ]

    results: list[CaseResult] = []
    status = "abgeschlossen"
    writer = JsonlWriter(run_dir / "results.jsonl")
    try:
        if config.warmup:
            print("Warm-up ...")
            info.append(("Warm-up-Ergebnis (nicht in Statistik)", warmup(config, rules, client)))
        status_fn = getattr(client, "runtime_status", None)
        if status_fn:
            info.append(("Ollama-Status nach Warm-up (ollama ps)", status_fn(config.model)))
        print(f"{len(cases_to_run)} Testfälle, Modell {config.model}, Ausgabe {run_dir}")
        run_cases(cases_to_run, run_id, config, rules, client, writer, results,
                  progress=lambda i, n, r: print(f"[{i}/{n}] {r.prompt_id}: "
                                                 f"{r.decision or r.outcome} ({r.request_duration_ms:.0f} ms)"))
    except KeyboardInterrupt:
        status = f"unterbrochen nach {len(results)} von {len(cases_to_run)} Fällen (Ctrl+C)"
        print(f"\n{status}; exportiere bisherige Ergebnisse ...")
    finally:
        writer.close()
        info[2:2] = [("Ende UTC", utc_now()), ("Abschlussstatus", status)]
        xlsx = run_dir / "results.xlsx"
        write_results(xlsx, results, rule_ids, summarize(results, len(cases), rule_ids), info,
                      overview(results, len(cases)) + quality_rows(results, rule_ids[0], rule_ids[1])
                      + router_rows(results) + cp1_rows(results, bool(config.cp1_patterns)), OVERVIEW_NOTE)
        print(f"Fertig: {xlsx}\n        {run_dir / 'results.jsonl'}")
        lock.release()
    return 0 if status == "abgeschlossen" else 130


if __name__ == "__main__":
    sys.exit(main())
