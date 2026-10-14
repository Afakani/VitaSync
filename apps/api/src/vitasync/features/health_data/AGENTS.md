# Modul: Eigene Gesundheitsdaten

Zweck: Freigegebene Daten des angemeldeten Nutzers abrufen und normalisiert bereitstellen (Wert, Einheit, Zeitpunkt, Herkunft).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: FHIR-Port, DB-Port, `core/`, `security/`.
- Darf nicht: Werte interpretieren oder bewerten; Daten anderer Nutzer liefern; FHIR-Objekte nach außen geben.

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- Stories: U007, U011, U019, U020, U022

## Tests
- `apps/api/tests/features/health_data/`. Verhalten testen, nicht Implementierung spiegeln.

## Fallen
- Veraltete Werte als veraltet kennzeichnen.
- Einheiten nie stillschweigend umrechnen.
