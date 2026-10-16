---
tags: [vitasync]
---

# Glossar

| Begriff | Bedeutung |
| --- | --- |
| Stack | Gewählte Sprachen und Werkzeuge (Website, Server, Datenbank, Tests). Siehe [[D01-Stack]]. |
| FHIR | Standard für den Austausch von Gesundheitsdaten. VitaSync nutzt R4. |
| LOINC | Codes für Messgrößen (z. B. 718-7 = Hämoglobin). |
| UCUM | Standard für Einheiten (z. B. `g/dL`). |
| Port | Schnittstelle in `core/ports.py`, die ein Adapter implementiert (LLM, FHIR, DB). |
| Adapter | Code, der einen externen Dienst anbindet. |
| Feature / Fachbereich | Ordner unter `features/`, der einen Teil der Fachlogik verantwortet. |
| Anfrageart (Intent) | Was der Nutzer mit seiner Nachricht will, z. B. allgemeine Gesundheitsfrage, eigene Werte ansehen, Zuständigkeit erfragen. Bestimmt, welche Information zurückkommt. Katalog als Enum in `contracts/llm/`, Herkunft sind die Anwendungsfälle. Keine Bewertung der Person. |
| Anwendungsfall (Use Case) | Eine User Story im Backlog (`U001`–`U033`). Quelle für die Anfragearten: Jede Anfrageart verweist auf ihren Anwendungsfall. |
| Entität | Aus der Nachricht erkannter Einzelwert, z. B. Symptom, Messgröße, Zeitangabe, Altersgruppe. Eine Entität ist eine Beobachtung am Text, keine Aussage über die Person. |
| Eval | Testfall mit Soll-Ergebnis für LLM-gestützte Funktionen. |
| Consent | Einwilligung des Nutzers, pro Zweck gespeichert. |
| Zuständigkeit | Allgemeine Information, welche Stelle wofür zuständig ist (Hausarzt, Facharzt, 116117, 112). Keine individuelle Empfehlung. |
| Zweckbestimmung | Was VitaSync tut und nicht tut; Grenze zum Medizinprodukt. Siehe [[D08-Zweckbestimmung]]. |
| Task-ID | `F001`–`F015` (Grundlagen) oder `T-U<Story>-<Nr>`. |
| Dxx | Architekturentscheidung in `docs/decisions/`. |
| DOD1-xx | Kriterium der Definition of Done für Meilenstein 1. |

## Verknüpft
- [[Start]]
