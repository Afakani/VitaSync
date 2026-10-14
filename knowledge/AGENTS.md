# Modul: Fachwissen

Zweck: Fachlich freigegebene Inhalte: Themen (`topics/`), Warnzeichen-Stichworte mit festem Notfallhinweis (`rules/`), Anlaufstellen (`care_paths/`).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Markdown mit Kopfdaten nach `TEMPLATE.md`.
- Darf nicht: Inhalte ohne Quelle; Status `geprueft` ohne Reviewer setzen; Diagnosen, Medikamente, Dosierungen, Referenzbereiche zur Bewertung, Dringlichkeitsstufen ([D08](../docs/decisions/D08-Zweckbestimmung.md)). Alles ist allgemein formuliert, für alle Nutzer gleich.

## Verträge
- Pflichtfelder im Kopf: `id`, `titel`, `status` (`entwurf` | `geprueft`), `quelle`, `reviewer`, `review_datum`.
- Der Code lädt nur `status: geprueft`.
- Siehe [D04](../docs/decisions/D04-Fachinhalte.md).

## Tests
- `python scripts/check_structure.py` prüft die Kopfdaten.

## Fallen
- KI darf Entwürfe schreiben, aber nie `status: geprueft` setzen. Das tut nur der benannte Reviewer.
