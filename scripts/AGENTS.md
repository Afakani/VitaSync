# Modul: Entwicklungswerkzeuge

Zweck: Prüfskripte, die außerhalb der Anwendungen laufen: Strukturcheck (`check_structure.py`) und
Vertragsprüfung (`validate_contracts.py`). Keine Fachlogik, kein Produktcode.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Standardbibliothek und die in `requirements.txt` gepinnten Werkzeuge.
- Darf nicht: das Paket `vitasync` importieren; Dateien in `contracts/`, `knowledge/` oder `docs/` ändern (nur `check_structure.py --fix` legt `CLAUDE.md`-Stubs an); Gesundheitsinhalte oder fachliche Regeln enthalten.

## Verträge
- `check_structure.py` trennt **Fehler** (Exit 1) von **Warnungen** (Exit 0). Siehe [D10](../docs/decisions/D10-Testlauf.md).
- `validate_contracts.py` prüft jedes Beispiel gegen das Schema, unter dem es im Vertrag per `externalValue` eingetragen ist. Ein Beispiel ohne Eintrag ist ein Fehler, damit nichts ungeprüft durchrutscht.
- Abhängigkeiten: `requirements.txt` (direkt, mit Begründung) und `requirements.lock` (aufgelöst, inklusive transitiver Pakete). Beide gepinnt, damit lokal und in CI derselbe Stand läuft.
- `import-linter` gehört **nicht** hierher, sondern in die dev-Extras von `apps/api`: es importiert das Paket `vitasync` und braucht dessen Umgebung. Konfiguration: `apps/api/.importlinter`.

## Tests
- `python -m pytest scripts/tests` – Selbsttests der Prüfer: Sie müssen bei kaputten Eingaben rot werden, nicht nur bei guten grün.
- Kaputte Beispiele liegen in `tests/fixtures/invalid/`, nie in `contracts/`.
- `scripts/tests/test_import_rules.py` braucht die Umgebung von `apps/api` und überspringt sich sonst selbst. In CI laufen beide Umgebungen, damit nichts stillschweigend übersprungen wird.

## Fallen
- Ändert sich der Vertrag, müssen die kaputten Fixtures mitwachsen – sonst prüfen sie eine Form, die es nicht mehr gibt.
- `python -m importlinter.cli` liefert wortlos 0. Nur das Konsolenskript `lint-imports` prüft wirklich.
