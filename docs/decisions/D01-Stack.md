---
id: D01
status: bestaetigt
bestaetigt_von: Atakan (Teamzustimmung)
bestaetigt_am: 2026-10-14
---

# D01 – Technischer Stack und Repository

**Status: Bestätigt am 14.10.2026 durch Atakan (Teamzustimmung).** Eine formale Einschätzung der Betreuung steht wie bei D08 noch aus.

## Beschluss

| Teil | Wahl | Warum |
| --- | --- | --- |
| Backend | Python 3.12 + FastAPI | LLM-, FHIR- und Datenwerkzeuge sind in Python am besten verfügbar. FastAPI erzeugt das API-Schema (OpenAPI) automatisch. |
| Validierung | Pydantic | Gleiche Modelle für API-Eingaben und LLM-Ausgabeschemas. |
| Frontend | React + TypeScript + Vite | Verbreitet, viele Teammitglieder finden Hilfe, Typen fangen Vertragsfehler früh. |
| Frontend (optional, nicht bestätigt) | PHP + JavaScript | Zugelassen als Alternative. PHP liefert nur Seiten aus und ruft die FastAPI über HTTP auf; keine Fachlogik, kein eigener Datenbank-, LLM- oder FHIR-Zugriff. Wahl und Bestätigung durch das Team stehen aus. |
| API-Client im Frontend | aus OpenAPI generiert | Kein manuelles Abtippen des Vertrags. |
| Datenbank | PostgreSQL (lokal per Docker) | Siehe D06. |
| Tests | pytest (API), Vitest (Web), Playwright (Ende-zu-Ende) | Standardwerkzeuge der gewählten Sprachen. |
| Importregeln | import-linter | Prüft die Abhängigkeitsregeln aus `docs/Architektur.md` automatisch. |
| Lokale Dienste | Docker Compose in `infra/`, nur PostgreSQL | Ein Befehl startet die Datenbank. Docker ist Voraussetzung, es gibt keinen Weg ohne. |
| LLM-Laufzeit | Ollama nativ auf dem Host | Kein Container, damit die GPU ohne Durchreichen nutzbar bleibt. Siehe D03. |
| FHIR-Testserver | noch nicht aufgenommen | Kommt mit der Umsetzung von D02 in einem eigenen Task. |
| Repo | Ein Repository, `apps/web` + `apps/api` | Siehe `AGENTS.md`, Tabelle „Wo gehört was hin“. |

## Verworfene Alternativen

- **Java + Spring Boot** als Backend: passt zum FH-Hintergrund, aber LLM- und FHIR-Hilfswerkzeuge sind in Python einfacher. Mit der Teamzustimmung zu Python nicht weiter verfolgt.
- **Alles in TypeScript (Next.js)**: eine Sprache weniger, aber schwächeres Ökosystem für Datenanalyse (M4).

## Geklärte Punkte

- Teamumfrage Python/TypeScript: mit der Zustimmung vom 14.10.2026 erledigt, Java-Alternative entfällt.
- Docker: ist Voraussetzung für die Entwicklung. Eine Startanleitung ohne Docker wird nicht gepflegt.

## Offene Punkte

- Formale Einschätzung der Betreuung zum bestätigten Stack noch einholen.
- Optionales Frontend PHP + JavaScript (ergänzt 2026-10-21): Ob es statt oder neben React genutzt wird, entscheidet das Team. Bis dahin gilt React + TypeScript.

## Betroffen

`apps/`, `infra/`, `.github/workflows/`, Task F001, F002, F004.
