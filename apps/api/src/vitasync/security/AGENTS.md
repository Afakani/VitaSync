# Modul: Sicherheit

Zweck: Sitzung, Identität, Eigentumsprüfung, zentrale Consent-**Prüfung**.

Zuständig: <GitHub-Handle eintragen>

Abgrenzung zu [`features/consent`](../features/consent/AGENTS.md): `security` **prüft nur lesend**, ob für
einen Zweck eine gültige Einwilligung vorliegt, und gibt frei oder lehnt ab. Es erteilt, ändert, widerruft
und löscht keine Einwilligungen – das macht ausschließlich `features/consent`.

## Grenzen
- Darf nutzen: `core/`, DB-Port.
- Darf nicht: Identität aus Request-Parametern oder Modellausgaben ableiten; Prüfungen in Features duplizieren; Einwilligungen schreiben, ändern oder löschen (das macht `features/consent`).

## Verträge
- Siehe [Identität und Einwilligung (I2/I3)](../../../../../docs/decisions/README.md).

## Tests
- Pflichtfälle: nicht angemeldet, fremde Ressource, fehlende Einwilligung, widerrufene Einwilligung.

## Fallen
- Verweigerung ist der Standard: Fehlt eine Information, wird abgelehnt.
