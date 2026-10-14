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
- Beispiele müssen gegen ihr Schema valide sein (Check folgt mit F004).

## Fallen
- Vertragsänderung bricht Verbraucher: alle im selben PR anpassen und im PR auflisten.
