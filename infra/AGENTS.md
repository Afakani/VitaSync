# Modul: Lokale Infrastruktur

Zweck: Lokale Dienste für Entwicklung: Datenbank, FHIR-Testserver, LLM-Laufzeit (Docker Compose, Task F002).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Konfiguration über `.env`.
- Darf nicht: Secrets einchecken; Dienste für andere Projekte mitbenutzen; Produktion.

## Verträge
- Siehe D01, D02, D03, D06.

## Tests
- Frischer Checkout + `.env` aus `.env.example` muss bei einer zweiten Person starten (Abnahme F002).

## Fallen
- Modell-Dateien (`*.gguf`) nie einchecken.
