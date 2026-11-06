# VitaSync – Arbeitsrepo

Arbeitsrepo für den VitaSync-Chatbot (Team VC, FH Aachen): Prototypen, Benchmarks, Experimente. Arbeitet nur mit synthetischen Daten. VitaSync ist ein Wellness- und Präventionsprodukt, kein Medizinprodukt: keine Diagnosen, keine Bewertung von Werten, keine Triage (Regeln R1–R6).

**Maßgeblich sind Jira (Projekt VC) und Confluence (Space VC).** Das Team-Repo mit den Modulen M1–M9 entsteht separat (VC-74).

## Einstieg
1. [AGENTS.md](AGENTS.md) – Regeln für alle (Menschen und KI), Quellen, Ordnerkarte, Ablauf.
2. [docs/decisions/README.md](docs/decisions/README.md) – Wegweiser zu den Entscheidungen in Confluence.
3. [docs/Architektur.md](docs/Architektur.md) – Pipeline M1–M9 und Aufbau des Prototyps.
4. `python scripts/check_structure.py` – prüft Struktur, Links, Agenten-Dateien und Wissens-Kopfdaten.

## Ordner
| Ordner | Inhalt |
| --- | --- |
| `apps/web/` | Prototyp-Oberfläche, Designentwürfe |
| `apps/api/` | Prototyp-Server mit Fachbereichen unter `src/vitasync/features/` |
| `benchmarks/` | Messwerkzeuge: Regelprüfung, Router-Vergleich |
| `contracts/` | API-, LLM- und FHIR-Schemas (Entwürfe) |
| `knowledge/` | Inhalte mit Status |
| `evals/` | Testsätze |
| `data/synthetic/` | Synthetische Testdaten |
| `infra/` | Lokale Dienste |
| `docs/` | Architektur, Ablauf, Wegweiser (Obsidian-Vault) |
| `planning/` | Übergaben (Backlog ist Jira) |
| `scripts/` | Werkzeuge |

## Starten (Prototyp-API)

Voraussetzungen: Python 3.12 und Docker. Vollständige Anleitung: [apps/api/README.md](apps/api/README.md).

```bash
cp .env.example .env                                                   # POSTGRES_PASSWORD setzen
docker compose --env-file .env -f infra/docker-compose.yml up -d db
cd apps/api && python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock -e ".[dev]"
.venv/Scripts/python.exe -m uvicorn vitasync.api.app:app --reload --host 127.0.0.1 --port 8000
```

Prüfen: `curl http://127.0.0.1:8000/healthz`. Tests: `cd apps/api && .venv/Scripts/python.exe -m pytest`.

Benchmark: [benchmarks/rule_check/README.md](benchmarks/rule_check/README.md).
