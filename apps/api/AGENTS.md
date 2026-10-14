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
- Befehl nach F004 hier eintragen. Bis dahin keinen erfinden.

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

## Fallen
- Konfiguration nur über Umgebungsvariablen (`.env`), Vorlage `.env.example` im Root.
