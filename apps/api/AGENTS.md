# Modul: Server (apps/api)

Zweck: HTTP-API, Fachlogik und Adapter. Paket `vitasync` unter `src/`.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: siehe Abhängigkeitsregeln in der Root-`AGENTS.md` und `docs/Architektur.md`.
- Darf nicht: Geschäftslogik in Routen; Fachbereiche über interne Dateien koppeln; Infrastruktur in `core/` importieren.

## Verträge
- API-Schema wird aus dem Code erzeugt und nach `contracts/api/openapi.json` exportiert; Änderungen daran im PR sichtbar machen.

## Tests
- `tests/` spiegelt `src/vitasync/` (z. B. `tests/features/chat/`).
- Unit-Tests nutzen den Fake-LLM-Adapter, nie das echte Modell.
- Integrationstests gegen Test-Datenbank aus `infra/`.
- Befehl: `cd apps/api && .venv/Scripts/python.exe -m pytest` (Windows; sonst `.venv/bin/python`). Konfiguration in `pyproject.toml` unter `[tool.pytest.ini_options]`.
- Jeder Pull Request laeuft automatisch: Tests, Vertragsbeispiele, Importregeln und Strukturcheck (`.github/workflows/checks.yml`, F004).
- Importregeln: `cd apps/api && .venv/Scripts/lint-imports.exe --config .importlinter` prueft die Tabelle aus `docs/Architektur.md`. Nicht pruefbar ist damit, ob ein Fachbereich einen anderen nur ueber dessen `__init__.py` anspricht - das bleibt Sache des Reviews.
- Abdeckungsmessung gibt es bewusst noch nicht; sie kommt erst, wenn es Fachlogik zu messen gibt.

## Aufbau
| Ordner | Inhalt |
| --- | --- |
| `src/vitasync/api/` | HTTP-Routen, Request/Response-Modelle |
| `src/vitasync/features/` | Fachbereiche, je ein Ordner |
| `src/vitasync/core/` | Interne Modelle, Fehler, Ports (Schnittstellen) |
| `src/vitasync/security/` | Sitzung, Identität, Eigentum, Consent-Prüfung |
| `src/vitasync/adapters/` | LLM, FHIR, Datenbank |
| `migrations/` | Datenbankmigrationen |
| `tests/` | Tests, gespiegelt zu `src/vitasync/` |

Einstiegspunkt: `vitasync.api.app:app`. Projektdatei: `pyproject.toml`, aufgelöste Versionen in `requirements.lock`.

## Fallen
- Konfiguration nur über Umgebungsvariablen (`.env`), Vorlage `.env.example` im Root.
