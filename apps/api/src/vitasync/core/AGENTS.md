# Modul: Kern (core)

Zweck: Interne Modelle (z. B. Messwert mit Wert, Einheit, Zeitpunkt, Herkunft), Fehlerarten und Ports (Schnittstellen für LLM, FHIR, DB).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Standardbibliothek, Validierungsbibliothek.
- Darf nicht: HTTP, Datenbank, LLM, FHIR-Bibliotheken importieren.

## Verträge
- `ports.py` definiert die Schnittstellen, die `adapters/` implementieren.

## Tests
- Reine Unit-Tests ohne Infrastruktur.

## Fallen
- Änderungen an Modellen hier betreffen fast alle Module: nur mit Task, der das verlangt.
