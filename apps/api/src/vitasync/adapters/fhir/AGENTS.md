# Modul: FHIR-Adapter

Zweck: Liest FHIR-R4-Ressourcen und übersetzt sie in interne Modelle aus `core/`.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `core/`, Profile aus `contracts/fhir/`.
- Darf nicht: Schreiben in externe Akten; FHIR-Objekte an Features durchreichen.

## Verträge
- Siehe [D02](../../../../../../docs/decisions/D02-FHIR.md).

## Tests
- Mit Beispielen aus `contracts/fhir/examples/` und `data/synthetic/`.

## Fallen
- Einheit (UCUM) und Herkunft immer übernehmen.
