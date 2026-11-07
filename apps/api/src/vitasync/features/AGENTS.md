# Fachbereiche

Ein Ordner = ein Fachbereich mit eigenem Verantwortlichen.

| Ordner | Inhalt |
| --- | --- |
| `chat/` | M4: Orchestrierung einer Nachricht (`route_message`: CP1 → Erkennung → Regeln → Routing), Kontext, Rückfragen |
| `recognition/` | M2: Flags vom LLM, streng gegen Schema geprüft |
| `input_guard/` | CP1: feste Muster für Notfall, Krise, Injection vor dem Modell |
| `rule_pipeline/` | Flags → Regelergebnis (Regel-JSON, R1–R6) |
| `routing/` | Regelergebnis → Route (Entscheidung des Safety-Routers M3) |
| `guidance/` | Allgemeine Information, Zuständigkeiten, fester Notfallhinweis |
| `consent/` | Einwilligung, Widerruf, Löschung |
| `health_data/` | Eigene Daten abrufen und normalisieren |
| `analysis/` | Rechnerische Auswertungen ohne Bewertung |

Weitere Ordner erst anlegen, wenn die Arbeit angesagt ist.

## Neuer Fachbereich
1. Ordner anlegen, `AGENTS.md` nach `docs/vorlagen/MODUL_AGENTS.md`.
2. `python scripts/check_structure.py --fix` legt `CLAUDE.md` an.
3. Zeile in dieser Tabelle und Knoten in `docs/Architektur.md` ergänzen.

Fachbereiche koppeln sich nur über öffentliche Funktionen in `__init__.py`.
