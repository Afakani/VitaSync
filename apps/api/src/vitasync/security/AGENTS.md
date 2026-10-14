# Modul: Sicherheit

Zweck: Sitzung, Identität, Eigentumsprüfung, zentrale Consent-Prüfung.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `core/`, DB-Port.
- Darf nicht: Identität aus Request-Parametern oder Modellausgaben ableiten; Prüfungen in Features duplizieren.

## Verträge
- Siehe [D05](../../../../../docs/decisions/D05-Identitaet-Einwilligung.md).

## Tests
- Pflichtfälle: nicht angemeldet, fremde Ressource, fehlende Einwilligung, widerrufene Einwilligung.

## Fallen
- Verweigerung ist der Standard: Fehlt eine Information, wird abgelehnt.
