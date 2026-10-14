"""Selbsttest fuer scripts/validate_contracts.py.

Ein gruener Pruefer beweist nichts, solange niemand zeigt, dass er auch rot
wird. Diese Tests pruefen beides: die echten Beispiele gehen durch, und jedes
absichtlich kaputte Beispiel faellt durch.

Die kaputten Fixtures liegen bewusst nicht unter `contracts/`: dort gehoeren
laut contracts/AGENTS.md nur gueltige Schema- und Beispieldateien hin.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import validate_contracts

ROOT = Path(__file__).resolve().parents[2]
VERTRAG = ROOT / "contracts/api/draft/chat-v1.openapi.yaml"
KAPUTT = Path(__file__).parent / "fixtures/invalid"


def test_echte_beispiele_sind_gueltig() -> None:
    assert validate_contracts.main(["validate_contracts.py", str(ROOT / "contracts")]) == 0


def baue_vertragsbaum(ziel: Path) -> Path:
    """Kopiert den echten Vertrag samt Beispielen in einen Wegwerfordner."""
    quelle = VERTRAG.parent
    ziel_vertrag = ziel / "api/draft"
    shutil.copytree(quelle, ziel_vertrag)
    return ziel_vertrag


@pytest.mark.parametrize(
    "fixture",
    sorted(p.name for p in KAPUTT.glob("*.json")),
)
def test_kaputtes_beispiel_faellt_durch(fixture: str, tmp_path: Path, capsys) -> None:
    """Jede kaputte Datei muss den Pruefer rot machen, wenn sie ein echtes Beispiel ersetzt."""
    baum = baue_vertragsbaum(tmp_path)
    kaputt = json.loads((KAPUTT / fixture).read_text(encoding="utf-8"))

    # Das kaputte Beispiel ersetzt die Datei, deren Form es verletzt.
    ziel = "chat-request.json" if "anfrage" in fixture else "chat-response-general.json"
    (baum / "examples" / ziel).write_text(json.dumps(kaputt), encoding="utf-8")

    ergebnis = validate_contracts.main(["validate_contracts.py", str(tmp_path)])

    assert ergebnis == 1, f"{fixture} haette den Pruefer rot machen muessen"
    assert "FEHLER" in capsys.readouterr().out


def test_beispiel_ohne_eintrag_im_vertrag_faellt_auf(tmp_path: Path, capsys) -> None:
    """Eine Datei in examples/, die der Vertrag nicht nennt, bleibt sonst ungeprueft."""
    baum = baue_vertragsbaum(tmp_path)
    (baum / "examples" / "nicht-eingetragen.json").write_text("{}", encoding="utf-8")

    ergebnis = validate_contracts.main(["validate_contracts.py", str(tmp_path)])

    assert ergebnis == 1
    assert "nicht-eingetragen.json" in capsys.readouterr().out


def test_fehlende_beispieldatei_faellt_auf(tmp_path: Path, capsys) -> None:
    """Ein im Vertrag genanntes Beispiel muss es auch geben."""
    baum = baue_vertragsbaum(tmp_path)
    (baum / "examples" / "chat-request.json").unlink()

    ergebnis = validate_contracts.main(["validate_contracts.py", str(tmp_path)])

    assert ergebnis == 1
    assert "fehlt" in capsys.readouterr().out
