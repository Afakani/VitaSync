# Modul: Lokale Infrastruktur

Zweck: Lokale Dienste für Entwicklung. Stand: nur PostgreSQL per Docker Compose (`docker-compose.yml`). Die LLM-Laufzeit (Ollama) läuft nativ auf dem Host, ein FHIR-Testserver kommt mit der Umsetzung von I2.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Konfiguration über `.env`.
- Darf nicht: Secrets einchecken; Dienste für andere Projekte mitbenutzen; Produktion.

## Verträge
- Siehe Stack, I2, Modell-ADR, Speicherkonzept.

## Tests
- Frischer Checkout + `.env` aus `.env.example` muss bei einer zweiten Person starten.

## Fallen
- Modell-Dateien (`*.gguf`) nie einchecken.
- Compose sucht `.env` neben der Compose-Datei. Die Vorlage liegt aber im Wurzelverzeichnis, deshalb immer mit `--env-file .env` vom Repo-Wurzelverzeichnis aufrufen.
- Ports immer an `127.0.0.1` binden. Ohne Präfix veröffentlicht Docker auf allen Schnittstellen.
