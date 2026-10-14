# Fachbereiche

Ein Ordner = ein Fachbereich mit eigenem Verantwortlichen.

| Ordner | Inhalt |
| --- | --- |
| `chat/` | Orchestrierung einer Nachricht, Kontext, Rückfragen |
| `recognition/` | Anfrageerkennung über LLM mit Schema |
| `guidance/` | Allgemeine Information, Zuständigkeiten, fester Notfallhinweis |
| `consent/` | Einwilligung, Widerruf, Löschung |
| `health_data/` | Eigene Daten abrufen und normalisieren |
| `analysis/` | Rechnerische Auswertungen ohne Bewertung |

Geplant (Ordner bei Start anlegen): `summary/` (U014), `reminders/` (U016), `documents/` (U032).

## Neuer Fachbereich
1. Ordner anlegen, `AGENTS.md` nach `docs/vorlagen/MODUL_AGENTS.md`.
2. `python scripts/check_structure.py --fix` legt `CLAUDE.md` an.
3. Zeile in dieser Tabelle und Knoten in `docs/Architektur.md` ergänzen.

Fachbereiche koppeln sich nur über öffentliche Funktionen in `__init__.py`.
