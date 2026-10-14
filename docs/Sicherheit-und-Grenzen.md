---
tags: [vitasync, sicherheit]
---

# Sicherheit und fachliche Grenzen

Die verbindlichen Regeln stehen in der Root-`AGENTS.md` („Harte Regeln“). Diese Notiz erklärt, wo sie im Code umgesetzt werden.

| Regel | Umgesetzt in |
| --- | --- |
| Identität nur aus Sitzung | `apps/api/src/vitasync/security/` |
| Consent vor Datenzugriff und Modellaufruf | `security/` + Aufruf in `api/`-Routen |
| Keine erfundenen Fachregeln | `knowledge/` mit Status `geprueft`, geladen von `features/guidance/` |
| Rechnen nicht im LLM | `features/analysis/`, `core/` |
| Modellausgabe validieren | `contracts/llm/`, `features/recognition/` |
| Fester Notfallhinweis bei Stichwort, keine Einstufung | `features/guidance/`, `knowledge/rules/` |
| Keine Bewertung eigener Werte | `features/analysis/`, `evals/answers/` |
| Keine Inhalte in Logs | Logging-Konfiguration in `apps/api` |
| KI-Kennzeichnung sichtbar und maschinenlesbar | `apps/web/src/features/chat/`, `contracts/api/` (T-U028-03) |
| Datenschutz-Pflichten | [[Compliance]] |

## Was VitaSync darf und nicht darf
Verbindlich in [[D08-Zweckbestimmung]]. Kurz: allgemeine Information, Zuständigkeiten, fester Notfallhinweis, eigene Daten anzeigen und rechnen, dokumentieren. Keine Aussage über den Gesundheitszustand einer konkreten Person.

## Verknüpft
- [[Architektur]]
- [[D04-Fachinhalte]] · [[D05-Identitaet-Einwilligung]] · [[D08-Zweckbestimmung]]
