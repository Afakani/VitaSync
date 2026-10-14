# VitaSync

Chat-Prototyp für allgemeine Gesundheitsinformationen und allgemeine Zuständigkeiten im Gesundheitswesen. Hochschulprojekt der FH Aachen. Arbeitet nur mit synthetischen Daten. Kein Medizinprodukt: keine Diagnosen, keine Bewertung eigener Werte, keine Dringlichkeitseinstufung ([D08](docs/decisions/D08-Zweckbestimmung.md)).

**Stand:** Projektgerüst mit startbarer leerer API (Task F002). D01 (Stack) und D08 (Zweckbestimmung) sind bestätigt, D02–D07 und D09 noch nicht: [docs/decisions/](docs/decisions/README.md).

## Einstieg
1. [AGENTS.md](AGENTS.md) – Regeln für alle (Menschen und KI), Ordnerkarte, Ablauf.
2. [docs/Architektur.md](docs/Architektur.md) – Aufbau und Abhängigkeiten.
3. [docs/Arbeitsablauf.md](docs/Arbeitsablauf.md) – Issues, Branches, Review.
4. `python scripts/check_structure.py` – prüft Struktur, Links, Agenten-Dateien und Wissens-Kopfdaten.

## Ordner
| Ordner | Inhalt |
| --- | --- |
| `apps/web/` | Website |
| `apps/api/` | Server mit Fachbereichen unter `src/vitasync/features/` |
| `contracts/` | API-, LLM- und FHIR-Schemas |
| `knowledge/` | Fachlich freigegebene Inhalte |
| `evals/` | Testsätze für LLM-Funktionen |
| `data/synthetic/` | Synthetische Testdaten |
| `infra/` | Lokale Dienste |
| `docs/` | Architektur und Entscheidungen (Obsidian-Vault) |
| `planning/` | Backlog, Arbeitsaufträge, Übergaben |
| `scripts/` | Werkzeuge |

## Starten

Voraussetzungen: Python 3.12 und Docker. Vollständige Anleitung: [apps/api/README.md](apps/api/README.md).

```bash
cp .env.example .env                                                   # POSTGRES_PASSWORD setzen
docker compose --env-file .env -f infra/docker-compose.yml up -d db
cd apps/api && python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock -e ".[dev]"
.venv/Scripts/python.exe -m uvicorn vitasync.api.app:app --reload --host 127.0.0.1 --port 8000
```

Prüfen: `curl http://127.0.0.1:8000/healthz`. Tests: `cd apps/api && .venv/Scripts/python.exe -m pytest`.

Die Website (`apps/web`) folgt mit Task F006, CI und weitere Tests mit F004.
