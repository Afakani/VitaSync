# Modul: Kern (core)

Zweck: Interne Modelle (z. B. Messwert mit Wert, Einheit, Zeitpunkt, Herkunft), Fehlerarten und Ports (Schnittstellen für LLM, FHIR, DB).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Standardbibliothek, Validierungsbibliothek.
- Darf nicht: HTTP, Datenbank, LLM, FHIR-Bibliotheken importieren.

## Verträge
- `ports.py` definiert die Schnittstellen, die `adapters/` implementieren (`IntentExtractorPort`, `RawModelOutput`, `ExtractionError`).
- `intent.py`: gemeinsame Typen der Nachrichtenannahme (Routen, Sub-Labels mit Regel R1–R6, Flags, `Extraction`, `GuardResult`, `RuleResult`, `RouteDecision`, `Policy`). Keine Logik der Module.
- `config.py`: Einstellungen aus der Umgebung, u. a. `LLM_*`, `CP1_PATTERNS`, `ROUTER_POLICY`.

## Tests
- Reine Unit-Tests ohne Infrastruktur.

## Fallen
- Änderungen an Modellen hier betreffen fast alle Module: nur mit Task, der das verlangt.
