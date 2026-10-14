"""Selbsttest fuer die Abhaengigkeitsregeln in apps/api/.importlinter.

Prueft zweierlei:
1. Die Vertragsdatei deckt die Tabelle in docs/Architektur.md ab.
2. import-linter schlaegt bei einem verbotenen Import tatsaechlich an. Dafuer
   wird in einer Kopie des Pakets ein Verstoss eingebaut - nie im echten Code.

Die Tests ueberspringen sich selbst, wenn import-linter nicht installiert ist
(es gehoert zu den dev-Extras von apps/api, nicht zu scripts/requirements).
"""
from __future__ import annotations

import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "apps/api"
CONFIG = API / ".importlinter"

importlinter = pytest.importorskip("importlinter", reason="import-linter nur in der apps/api-Umgebung")


def lese_vertraege() -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.read(CONFIG, encoding="utf-8")
    return parser


def test_lint_befehl_existiert() -> None:
    assert lint_befehl().is_file(), f"import-linter fehlt: {lint_befehl()}"


def test_vertragsdatei_deckt_die_architekturtabelle_ab() -> None:
    parser = lese_vertraege()
    assert parser["importlinter"]["root_package"] == "vitasync"

    namen = [parser[a]["name"] for a in parser.sections() if a.startswith("importlinter:contract:")]
    assert len(namen) == 4, namen

    inhalt = CONFIG.read_text(encoding="utf-8")
    # Jede Zeile der Tabelle aus docs/Architektur.md muss vorkommen.
    for modul in ("vitasync.core", "vitasync.adapters", "vitasync.api",
                  "vitasync.features", "vitasync.security"):
        assert modul in inhalt, modul


def lint_befehl() -> Path:
    """Konsolenskript von import-linter neben dem laufenden Interpreter.

    `python -m importlinter.cli` tut nichts und liefert 0 - nur das
    Konsolenskript `lint-imports` fuehrt die Pruefung wirklich aus.
    """
    name = "lint-imports.exe" if os.name == "nt" else "lint-imports"
    return Path(sys.executable).parent / name


def lint(verzeichnis: Path, quellpfad: Path | None = None) -> subprocess.CompletedProcess[str]:
    umgebung = dict(os.environ)
    if quellpfad is not None:
        # Der zu pruefende Baum muss vor der editierbaren Installation stehen.
        umgebung["PYTHONPATH"] = str(quellpfad)
    return subprocess.run(
        [str(lint_befehl()), "--config", str(verzeichnis / ".importlinter")],
        cwd=verzeichnis, capture_output=True, text=True, env=umgebung,
    )


def test_echter_code_haelt_die_regeln() -> None:
    ergebnis = lint(API)
    assert ergebnis.returncode == 0, ergebnis.stdout + ergebnis.stderr
    assert "Contracts: 4 kept, 0 broken." in ergebnis.stdout


def test_verbotener_import_faellt_durch(tmp_path: Path) -> None:
    """core darf nichts aus dem Projekt importieren - eingebaut in einer Kopie."""
    kopie = tmp_path / "api"
    shutil.copytree(API, kopie, ignore=shutil.ignore_patterns(
        ".venv", "__pycache__", "*.egg-info", ".pytest_cache"))

    verstoss = kopie / "src/vitasync/core/verstoss.py"
    verstoss.write_text(
        '"""Nur fuer den Selbsttest: core importiert api, das ist verboten."""\n'
        "from vitasync.api import app  # noqa: F401\n",
        encoding="utf-8",
    )

    ergebnis = lint(kopie, quellpfad=kopie / "src")

    assert ergebnis.returncode != 0, "verbotener Import haette auffallen muessen"
    assert "broken" in ergebnis.stdout
    assert "core importiert nichts aus dem Projekt" in ergebnis.stdout
