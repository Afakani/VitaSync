# Modul: HTTP-Schicht

Zweck: Routen, Eingabevalidierung, Fehlerformat, Mapping auf Features.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `features/*` (öffentliche Funktionen), `security/`, `core/`.
- Darf nicht: Fachlogik, Datenbank- oder LLM-Zugriff direkt; Nutzer-ID aus Request-Body übernehmen.

## Verträge
- Einheitliches Fehlerformat und Fehlercodes aus Task F003 (`contracts/api/`).
- Maximale Eingabelänge serverseitig prüfen.

## Tests
- Pro Route: gültige Eingabe, ungültige Eingabe, nicht angemeldet, fremde Ressource.

## Fallen
- Jede Route, die Gesundheitsdaten oder das Modell berührt, braucht die Consent-Prüfung aus `security/`.
