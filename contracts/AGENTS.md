# Modul: Verträge

Zweck: Einzige Quelle für Schnittstellen zwischen Teilen: `api/` (OpenAPI), `llm/` (JSON-Schemas für Modellausgaben), `fhir/` (Profile, Beispiele).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: nur Schema- und Beispieldateien.
- Darf nicht: Ausführbaren Code ablegen; dieselbe Definition zusätzlich von Hand im Code pflegen.

## Verträge
- `api/openapi.json` wird aus `apps/api` erzeugt, nicht von Hand geändert.
- `api/draft/` enthält handgepflegte Vertragsentwürfe aus Research-Tasks. Jeder trägt seinen Status
  (`Vorschlag` | `bestätigt vorbehaltlich Review` | `bestätigt`) in `info.x-vitasync-status` und in der
  Tabelle in `api/draft/README.md`. Der Code liest sie nicht; verbindlich ist das generierte
  `api/openapi.json`.
- `llm/*.schema.json` sind die Quelle; der Code lädt oder generiert daraus.
- `fhir/examples/` nur synthetisch.

## Tests
- Beispiele müssen gegen ihr Schema valide sein: `python scripts/validate_contracts.py`, läuft bei jedem Pull Request.
- Jedes Beispiel muss im Vertrag unter `examples:` mit `externalValue` eingetragen sein. Eine Datei in `examples/` ohne Eintrag lässt die Prüfung scheitern, damit nichts ungeprüft liegen bleibt.

## Fallen
- Vertragsänderung bricht Verbraucher: alle im selben PR anpassen und im PR auflisten.
- Ändert sich ein Schema, müssen die absichtlich kaputten Beispiele in `scripts/tests/fixtures/invalid/` mitwachsen. Sonst prüfen sie eine Form, die es nicht mehr gibt, und der Selbsttest wird wertlos.
