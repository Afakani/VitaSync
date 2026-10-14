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

Start- und Testbefehle folgen mit Task F002/F004.
