# Modul: Migrationen

Zweck: Versionierte Schemaänderungen der eigenen Datenbank.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Migrationswerkzeug aus D01.
- Darf nicht: Bestehende Migrationen nachträglich ändern; Testdaten hier einfügen (gehören nach `data/synthetic/`).

## Verträge
- Eine Migration pro Task, mit Rückweg.

## Tests
- Migration auf leerer Test-Datenbank hoch- und runterfahren.

## Fallen
- Zwei parallele Migrationen = Konflikt. Vor dem Merge auf `main` rebasen.
