---
id: D01
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D01 – Technischer Stack und Repository

**Status: Empfohlen, nicht bestätigt.** Das Team muss zustimmen und hier Name und Datum eintragen.

## Empfehlung

| Teil | Wahl | Warum |
| --- | --- | --- |
| Backend | Python 3.12 + FastAPI | LLM-, FHIR- und Datenwerkzeuge sind in Python am besten verfügbar. FastAPI erzeugt das API-Schema (OpenAPI) automatisch. |
| Validierung | Pydantic | Gleiche Modelle für API-Eingaben und LLM-Ausgabeschemas. |
| Frontend | React + TypeScript + Vite | Verbreitet, viele Teammitglieder finden Hilfe, Typen fangen Vertragsfehler früh. |
| API-Client im Frontend | aus OpenAPI generiert | Kein manuelles Abtippen des Vertrags. |
| Datenbank | PostgreSQL (lokal per Docker) | Siehe D06. |
| Tests | pytest (API), Vitest (Web), Playwright (Ende-zu-Ende) | Standardwerkzeuge der gewählten Sprachen. |
| Importregeln | import-linter | Prüft die Abhängigkeitsregeln aus `docs/Architektur.md` automatisch. |
| Lokale Dienste | Docker Compose in `infra/` | Ein Befehl startet DB, FHIR-Testserver und LLM-Laufzeit. |
| Repo | Ein Repository, `apps/web` + `apps/api` | Siehe `AGENTS.md`, Tabelle „Wo gehört was hin“. |

## Alternativen

- **Java + Spring Boot** als Backend: passt zum FH-Hintergrund, aber LLM- und FHIR-Hilfswerkzeuge sind in Python einfacher. Sinnvoll, wenn die Mehrheit des Teams kein Python kann.
- **Alles in TypeScript (Next.js)**: eine Sprache weniger, aber schwächeres Ökosystem für Datenanalyse (M4).

## Offene Punkte

- Teamumfrage: Wer kann Python, wer TypeScript? Bei klarer Java-Mehrheit Alternative 1 neu bewerten.
- Laufen alle Rechner mit Docker? Sonst Startanleitung ohne Docker ergänzen.

## Betroffen

`apps/`, `infra/`, `.github/workflows/`, Task F001, F002, F004.
