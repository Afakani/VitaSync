# Modul: Datenbank-Adapter

Zweck: Speichern und Laden eigener App-Daten (Chats, Einwilligungen, Profil).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `core/`.
- Darf nicht: Schema ohne Migration ändern; gegen gemeinsam genutzte Datenbanken testen.

## Verträge
- Schema über `apps/api/migrations/`.
- Siehe [D06](../../../../../../docs/decisions/D06-Speicherung.md).

## Tests
- Integrationstests gegen Test-Datenbank aus `infra/`.

## Fallen
- Jede Abfrage nach Nutzer filtern.
