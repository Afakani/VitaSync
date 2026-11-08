---
tags: [vitasync, architektur]
---

# Architektur

## Pipeline des Teams (maßgeblich: Jira + Confluence)

Pipeline aus Confluence „Ethical boundaries in the pipeline“ (VC-60): Input Guard → Router → Datenpfad / Wissenspfad → Antwort-LLM → Output Guard.
Die Umsetzung ist im Sprintplan in Module zerlegt:

| Modul | Aufgabe | Jira |
| --- | --- | --- |
| M1 Chat-API | Endpunkt nach I1 (OpenAPI) | VC-86 |
| M2 Klassifikator | Anfrage-Typ erkennen; v1 regelbasiert, v2 später | VC-87, VC-109 |
| M3 Safety-Router | feste Antworten für Weiterleitung, Notfall, Krisenpfad; ohne Nutzerdaten, ohne LLM | VC-89 |
| M4 Orchestrator | ein Flow je Typ (quantitativ, präventiv, FAQ …) | VC-88, VC-100, VC-108 |
| M5 Rechenwerkzeuge | erlaubte Berechnungen nach S3-05 | VC-99 |
| M6 RAG / Wissensbasis | FAQ und Impulse, Schema | VC-77, VC-97 |
| M7 LLM-Gateway | Modellaufruf, selbst gehostet | VC-75 |
| M8 Output Guard | Antwort gegen R1–R6 prüfen | VC-110 |
| M9 Testrunner | Testsätze, Trefferquoten | VC-79 |

Schnittstellen zur App von Johnny Bytes: I1 Chat-API, I2 Kontext (Gesundheitsdaten kommen von der App), I3 Einwilligung, I5 Audit-Ereignisse.

## Prototyp in diesem Repo

Ein Repository, `apps/api` (Server) und `apps/web` (Oberfläche, Entwürfe). Keine Microservices. Der Stack des Teams ist noch offen (VC-73).

| Prototyp-Ordner | entspricht etwa |
| --- | --- |
| `api/` | M1 |
| `features/input_guard` | Input Guard (CP1) |
| `features/recognition` | M2 |
| `features/rule_pipeline`, `features/routing` | M3 (Entscheidung) |
| `features/guidance` | M3 (Texte), M6 |
| `features/chat` | M4 |
| `features/analysis` | M5 |
| `adapters/llm` | M7 |
| `evals/`, `benchmarks/` | M9 |

## Ablauf einer Nachricht bis zur Route (umgesetzt)

```
Nutzertext
  -> features/input_guard   CP1-Muster: Notfall/Krise -> feste Route, kein LLM; Injection merken
  -> features/recognition   SLM: Qwen3-Embedding-8B (adapters/embedding) + Klassifikator -> 17 Flags
                            (oder LLM über adapters/llm, Schema contracts/llm/intent_flags.v1)
  -> features/rule_pipeline Flags -> Regelergebnis (crisis | emergency | block + R1-R6 | allow | unclear)
  -> features/routing       Regelergebnis + Modell-Vorschlag (nur verschärfend) + Confidence + Injection -> Route
  -> features/safety_net    CP2-Wortmuster: erlaubte Route -> Weiterleitung bei Treffer (nur sperren)
```

Zusammengesetzt in `features/chat.route_message`. Logik aus dem Team-Router (v0.1, dann v0.5 von Tolga), aufgeteilt in Regeln und Routing; Gleichheit mit v0.1 auf 1000 aufgezeichneten Fällen und mit v0.5 auf Batch 1 (250/250) geprüft.

## Abhängigkeitsregeln

| Von | Darf importieren |
| --- | --- |
| `api` | `features/*` (öffentlich), `security`, `core` |
| `features/<x>` | `core`, `core/ports`, `security`, andere `features/*` nur öffentlich |
| `adapters/*` | `core` |
| `security` | `core`, DB-Port |
| `core` | nichts aus dem Projekt |

Keine Zyklen.

## Warum so

- **Kleine Module mit klarer Ein- und Ausgabe:** Regelprüfung, Routing und Modellaufruf sind getrennt und einzeln testbar und austauschbar.
- **Ports in `core`:** LLM, Datenquellen und Datenbank sind austauschbar und in Tests durch Fakes ersetzbar.
- **Inhalte getrennt vom Code:** `knowledge/` lässt sich prüfen, ohne Code zu lesen.

## Verknüpft
- [[Sicherheit-und-Grenzen]]
- [[Arbeitsablauf]]
