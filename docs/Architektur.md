---
tags: [vitasync, architektur]
---

# Architektur

Ein Repository, zwei Anwendungen: `apps/web` (Website) und `apps/api` (Server). Keine Microservices. Stack: [[D01-Stack]].

## Ablauf einer Chatnachricht

```mermaid
flowchart LR
  W[apps/web] -->|HTTP| R[api/ Routen]
  R --> S[security/ Sitzung + Consent-Prüfung]
  R --> CO[features/consent]
  R --> C[features/chat]
  C --> REC[features/recognition]
  C --> G[features/guidance]
  C --> H[features/health_data]
  C --> A[features/analysis]
  REC --> LLM[adapters/llm]
  G --> K[(knowledge/ geprüft)]
  H --> F[adapters/fhir]
  H --> DB[adapters/db]
  A --> H
  S --> DB
  CO --> DB
  C --> LLM
```

1. Website sendet Nachricht an die API.
2. Route prüft Sitzung und Einwilligung (`security/`, nur lesend), ruft `features/chat` auf. Das Erteilen, Widerrufen und Löschen von Einwilligungen liegt in `features/consent` und läuft über eigene Routen, nicht über den Chat.
3. `recognition` lässt das LLM die Anfrage klassifizieren; Ausgabe wird gegen `contracts/llm/` validiert.
4. Enthält die Nachricht ein Warnzeichen-Stichwort, setzt `guidance` den festen Notfallhinweis an den Anfang.
5. Fragt der Nutzer nach eigenen Daten und ist das freigegeben: `health_data` liefert Werte, `analysis` rechnet ohne Bewertung.
6. `guidance` wählt allgemeine geprüfte Inhalte aus `knowledge/`; das LLM formuliert nur ([[D08-Zweckbestimmung]]).
7. Antwort mit KI-Kennzeichnung zurück an die Website.

## Abhängigkeitsregeln

| Von | Darf importieren |
| --- | --- |
| `api` | `features/*` (öffentlich), `security`, `core` |
| `features/<x>` | `core`, `core/ports`, `security`, andere `features/*` nur öffentlich |
| `adapters/*` | `core` |
| `security` | `core`, DB-Port |
| `core` | nichts aus dem Projekt |

Keine Zyklen. Wird mit import-linter geprüft: `apps/api/.importlinter`, bei jedem Pull Request (F004).

Geprüft werden Modulgrenzen. Dass ein Fachbereich einen anderen **nur über dessen `__init__.py`** anspricht, lässt sich damit nicht prüfen und bleibt Sache des Reviews. Dass niemand `adapters/*` importieren darf, ist bewusst streng umgesetzt: Braucht ein späterer Task die Verdrahtung der Adapter, wird die CI rot und erzwingt eine Änderung dieser Tabelle statt eines stillen Durchgriffs.

## Warum so

- **Fachbereiche als Ordner:** Eine Story betrifft meist einen Fachbereich. Weniger Merge-Konflikte, klare Zuständigkeit.
- **Ports in `core`:** LLM, FHIR und Datenbank sind austauschbar und in Tests durch Fakes ersetzbar.
- **Wissen getrennt vom Code:** Fachliche Reviewer prüfen `knowledge/`, ohne Code lesen zu müssen.

## Verknüpft
- [[Sicherheit-und-Grenzen]]
- [[Arbeitsablauf]]
- [[D02-FHIR]] · [[D03-Modell]] · [[D04-Fachinhalte]] · [[D05-Identitaet-Einwilligung]] · [[D06-Speicherung]]
