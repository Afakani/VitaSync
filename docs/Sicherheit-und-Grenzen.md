---
tags: [vitasync, sicherheit]
---

# Sicherheit und fachliche Grenzen

Verbindlich sind R1–R6 und die Seiten „What the bot is allowed and not allowed to do“ und „Forbidden and allowed actions“ in Confluence. Kurzfassung in der Root-`AGENTS.md`. Diese Notiz zeigt, wo sie im Prototyp und im Team-Modul umgesetzt werden.

| Regel | Team-Modul | Prototyp |
| --- | --- | --- |
| Notfall, Krise, Injection vor dem Modell erkennen | Input Guard / CP1, M3 | `features/guidance`, `knowledge/rules` |
| Weiterleiten statt urteilen (R4) | M3 Safety-Router | `features/guidance` |
| Keine Bewertung von Werten (R2), kein Score (R1), keine wertenden Farben (R6) | M5, M8 | `features/analysis`, `apps/web` |
| Nur Lifestyle-Formulierungen (R3) | M6, M8 | `knowledge/`, Prompts |
| Keine Deutung für die Apotheke (R5) | M4, M8 | – |
| Rechnen nicht im LLM | M5 | `features/analysis`, `core/` |
| Modellausgabe validieren | M2, M7 | `contracts/llm/`, `features/recognition` |
| Keine Inhalte in Logs | I5 | Logging-Konfiguration in `apps/api` |
| Datenschutz | – | [[Compliance]] |

## Grundsatz
Beobachten ist erlaubt: Werte zeigen, rechnen, mit eigenen früheren Werten vergleichen, exportieren. Deuten ist es nicht: niedrig/normal, Ursachen, Scores, wertende Farben, Auswahl „auffälliger“ Werte.

## Verknüpft
- [[Architektur]]
