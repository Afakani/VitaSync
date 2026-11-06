---
tags: [vitasync]
---

# Glossar

| Begriff | Bedeutung |
| --- | --- |
| R1–R6 | Die sechs Regeln aus Confluence „The 6 rules“. Kurzfassung in der Root-`AGENTS.md`. |
| CB-xx | Use Case aus der Masterliste CB-01 bis CB-35 (Confluence). |
| M1–M9 | Module des Chatbots laut Sprintplan, siehe [[Architektur]]. |
| I1–I5 | Schnittstellen zur App: I1 Chat-API, I2 Kontext, I3 Einwilligung, I5 Audit. |
| Route | Ergebnis des Routings: DATA_QUERY, HEALTH_QUESTION, COMBINED, APP_HELP, OUT_OF_SCOPE, EMERGENCY, Krisenpfad, CLARIFY. |
| Sub-Label | Grund einer Weiterleitung bei OUT_OF_SCOPE, z. B. VALUE_EVALUATION, MEDICATION, DIAGNOSIS_TRIAGE. |
| CP1 | Erster Prüfpunkt (Input Guard): feste Muster für Notfall, Krise, Injection vor jedem Modellaufruf. |
| VitaSync-Index | Neutrale Kennzahl der App; nie als Ampel oder Urteil (R1). |
| ADR | Architekturentscheidung, im Confluence-Space VC. |
| Johnny Bytes | Firma, die die VitaSync-App baut; der Chatbot läuft in der App. |
| FHIR | Standard für den Austausch von Gesundheitsdaten. |
| LOINC / UCUM | Codes für Messgrößen bzw. Einheiten. |
| Port | Schnittstelle in `core/ports.py`, die ein Adapter implementiert. |
| Adapter | Code, der einen externen Dienst anbindet. |
| Eval | Testfall mit Soll-Ergebnis für LLM-gestützte Funktionen. |
| VC-xx | Jira-Ticket im Projekt VC. |

## Verknüpft
- [[Start]]
