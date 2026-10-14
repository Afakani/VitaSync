# Modul: Synthetische Daten

Zweck: Synthetische Testpatienten (z. B. aus Synthea) und handgeschriebene Fälle für Tests, Evals und Demo.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: nur erzeugte oder ausgedachte Daten.
- Darf nicht: Echte oder aus echten Akten abgeleitete Daten, auch nicht „anonymisiert“.

## Verträge
- FHIR-Daten entsprechen `contracts/fhir/`.
- Jede Datei nennt im Kopf oder in `README.md`, wie sie erzeugt wurde.

## Tests
- Wird von Tests und `infra/` als Startdaten geladen.

## Fallen
- Namen und Daten offensichtlich fiktiv halten (z. B. „Erika Testfrau“).
