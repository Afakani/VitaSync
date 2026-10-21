---
tags: [vitasync, research]
---

# Abgleich Research ↔ Repo

Stand 2026-10-21 (DOC-003). **Notiz, keine Entscheidung.** Hier steht, wo die Recherche des Teams mit dem
Regelwerk übereinstimmt, wo sie abweicht und was im Repo noch fehlt. Verbindlich bleiben `AGENTS.md` und
die Entscheidungen in `docs/decisions/`. Übernommen wird ein Punkt nur über einen Task im Backlog oder eine
eigene Entscheidung.

## Quellen

Ordner `research/` im Arbeitsverzeichnis (derzeit **nicht versioniert**):

| Kürzel | Datei |
| --- | --- |
| R1 | `VitaSync Chatbot Tasks Report.pdf` (VC-29 bis VC-35) |
| R2 | `Research Notes Chatbots in General.txt` |
| R3 | `research on security expectations as in dsgvo.md` |
| R4 | `Privacy Expectations & User-Centric Data Protection (Healthcare LLM).md` |
| R5 | `Chatbot_Research_Notes_VC8 (1).docx` |
| R6 | `VitaSync_AI_Mechanisms_Research (1).pptx` |
| R7 | `FHIR & OMOP(CDM)V2.pptx` |
| R8 | `VitaSync_Chatbot_Vergleich_v2_Deutsch (1).pptx` |
| R9 | `Healthcare_LLM_GDPR_Security.pptx` |
| R10 | `Healthcare_LLM_Privacy_Engineering.pptx` |

## 1. Übereinstimmung

| Research-Punkt | Quelle | Im Repo |
| --- | --- | --- |
| Kein Diagnose-Tool, sonst MDR bzw. AI-Act-Hochrisiko | R3, R9 | [[D08-Zweckbestimmung]], [[D09-Datenschutz-EU]], harte Regel 7 |
| Modell schlägt vor, Code entscheidet; Prompt ist kein Schutz | R1, R5, R6 | harte Regeln 2, 3, 5; [[D03-Modell]] |
| Nutzertext ist Datum, keine Anweisung (OWASP LLM01) | R1, R6 | harte Regel 4 |
| Enge strukturierte Ausgabe, Prüfung im Backend; gültig heißt nicht richtig | R1, R6, R8 | harte Regel 5, `contracts/llm/`, [[Architektur]] Schritt 3 |
| Wissen aus geprüften Quellen mit Quellenangabe, nicht aus dem Modellgedächtnis | R1, R2, R5, R6 | harte Regel 6, [[D04-Fachinhalte]], Feld `sources` im Vertragsentwurf |
| Niedrige Temperatur, Abwägung Länge und Latenz | R1, R6 | [[D03-Modell]] |
| Lokales Modell statt eigenem Training; kein Training mit Nutzerdaten | R1, R9 | [[D01-Stack]], [[D03-Modell]], harte Regel 13 |
| Ausdrückliche, widerrufbare Einwilligung nach Art. 9 Abs. 2 a | R3, R9 | harte Regel 3, [[D05-Identitaet-Einwilligung]] |
| Rechte je Nutzer bei jedem Aufruf; keine Vermischung zwischen Nutzern | R1, R6 | harte Regel 2, [[D05-Identitaet-Einwilligung]], [[D06-Speicherung]] |
| Zweckbindung, kein Tracking oder Profiling | R4, R10 | harte Regel 13, [[D09-Datenschutz-EU]] |
| Löschung, Widerruf getrennt; Auskunft und Export | R3, R7, R10 | [[D05-Identitaet-Einwilligung]], [[D09-Datenschutz-EU]] |
| KI-Kennzeichnung | R2, R4 | harte Regel 11, Vertragsentwurf (`origin`, `ai_generated`, `ai_disclosure`) |
| Disclaimer allein reicht nicht | R1 | [[D08-Zweckbestimmung]] |
| Eigenes Testset mit Messung | R6 | `evals/`, [[D03-Modell]] |
| Chatbot liest Gesundheitsdaten nur, verändert sie nicht | R7 | [[D02-FHIR]] |
| Logs ohne Inhalte | R9 | harte Regel 10 |

## 2. Abweichungen, die bereits entschieden sind

Hier widerspricht die Recherche einer **bestätigten** Entscheidung oder einer harten Regel. Diese Punkte
werden nicht übernommen, solange D08 und die harten Regeln gelten.

| Research sagt | Quelle | Repo sagt |
| --- | --- | --- |
| Medikation als Datenquelle (`MedicationStatement`, Wechselwirkungen, Nebenwirkungen) | R4, R7, R10 | Keine Medikamente (harte Regel 7, [[D08-Zweckbestimmung]]); U018 gestrichen ([[D07-Optionaler-Umfang]]) |
| Symptomverständnis, Symptomzusammenfassungen; Ada und Infermedica (Ursachen, Triage) als Vorbilder | R1, R4, R8 | Keine Ursachen, keine Dringlichkeitseinstufung ([[D08-Zweckbestimmung]]); Vertragsentwurf schließt Stufe, Score und Zeitrahmen aus |
| „Erkennen, wann jemand professionelle Hilfe braucht“, „safe fallback to a doctor“ | R1, R6 | Nur der feste, für alle gleiche Notfallhinweis bei Stichwort (harte Regel 8) |
| Modell per API, Doku durchgehend von einem Cloud-Anbieter | R1, R6 | Keine externen KI-Dienste mit Nutzerdaten (harte Regel 13) |
| System-Prompt und Disclaimer als Schutz vor der Diagnose-Falle | R3 | Die Grenze liegt im Funktionsumfang, nicht im Hinweistext ([[D08-Zweckbestimmung]]) |

## 3. Abweichungen, die offen sind

Hier steht die Recherche gegen eine nur **empfohlene** Entscheidung oder gegen einen Punkt, den das Repo
nicht regelt. Zu besprechen, bevor die betroffene Entscheidung bestätigt wird.

| Thema | Research sagt | Quelle | Repo sagt | Betroffen (Status) |
| --- | --- | --- | --- | --- |
| Antwortweg | RAG mit Embeddings und Vektordatenbank; Modell antwortet aus gefundenen Texten | R1, R4, R6, R9 | Erkennung wählt geprüfte Einträge aus `knowledge/`, Modell formuliert nur; keine Vektorsuche | [[Architektur]], harte Regel 6, [[D04-Fachinhalte]] (empfohlen) |
| Werkzeugaufrufe | Modell ruft read-only FHIR-Abfragen auf; MCP-Schicht in Java | R1, R6, R7 | Keine Werkzeugaufrufe durch das Modell; Java verworfen | [[D03-Modell]] (empfohlen), [[D01-Stack]] (bestätigt) |
| Datenmodell | OMOP CDM zusätzlich zu FHIR für Laborwerte | R7 | Nur FHIR (`Patient`, `Observation`) | [[D02-FHIR]] (empfohlen) |
| Datenhaltung | Getrennter FHIR-Data-Lake, Pseudonym-Zuordnung in PostgreSQL | R3, R4, R9 | Nur PostgreSQL; FHIR-Daten gelesen, nicht dauerhaft kopiert | [[D06-Speicherung]] (empfohlen) |
| Rechtsgrundlage | Forschungsausnahme Art. 9 Abs. 2 j mit Pseudonymisierung | R3, R9 | Nur Einwilligung, Art. 9 Abs. 2 a | [[D09-Datenschutz-EU]] (empfohlen), Verarbeitungsverzeichnis |
| Verschlüsselung | TLS 1.3 überall (auch Backend → LLM), AES-256 im Ruhezustand – als umgesetzt dargestellt | R3, R9 | HTTPS außerhalb lokal; Speicherverschlüsselung „zu entscheiden“ (F018) | [[D09-Datenschutz-EU]] (empfohlen), `TOM.md` |
| Verlauf | Inkognito-Modus, Verlauf beim Schließen verworfen | R4, R10 | 30 Tage Aufbewahrung, dann automatische Löschung | [[D06-Speicherung]] (empfohlen), Datenschutzhinweis |
| Menschlicher Zugriff | „Kein Mensch liest die Chats“ | R4 | Protokollierter Admin-Zugriff zur Löschung und Fehleranalyse; Feedback geht ans Team | [[D09-Datenschutz-EU]] (empfohlen), Verarbeitungsverzeichnis V5 |
| Gedächtnis | Gespräche über Sitzungen hinweg fortsetzen | R1 | Kontext nur innerhalb eines Chats (U025) | [[D06-Speicherung]] (empfohlen) |
| Personenmerkmale | Altersgruppe („20–25“) in den Modellkontext geben | R4, R10 | Offener Punkt: Profilangaben in der Antwort derzeit nicht gedeckt | [[D08-Zweckbestimmung]] (bestätigt, Punkt offen) |
| EHDS | Verordnung 2025/327 samt Zugriffsprotokoll als verbindlich | R7 | Für den Prototyp nichts zu tun | [[D09-Datenschutz-EU]] (empfohlen) |

## 4. Was im Repo fehlt

Nur aufgelistet, nicht bewertet und nicht beauftragt.

**Datenschutz-Technik**
- Persönliche Angaben (Namen, Adressen, Geburtsdaten) im Freitext maskieren, bevor er zum Modell geht (R4, R6, R10).
- Pseudonymisierung und Schutz vor Re-Identifizierung über Quasi-Identifikatoren, z. B. Altersband statt Geburtsdatum (R3, R4, R10). Berührt den offenen Punkt in D08.
- Ausdrückliche Regel zur Datenminimierung im Prompt: nur die nötigen FHIR-Ressourcen, nie die ganze Akte (R10).
- Einzelnen Chat sofort löschen; bisher nur Löschung aller Daten (U024) und Frist (R10).
- Löschen von Nebenspeichern wie Caches und Indizes (R9); Backups sind nach D06 ausgeschlossen.
- Zusage im Datenschutzhinweis, dass Eingaben nie zum Training genutzt werden (R3, R4).
- Maßnahme für den protokollierten Admin-Zugriff in `TOM.md` (R3; D09 nennt ihn, TOM nicht).

**Recht**
- Eine eigentliche DSFA; vorhanden ist nur die Schwellwertprüfung in `Datenpanne.md` (R3, R9).
- Rechte auf Einschränkung und Widerspruch (Art. 18, 21); D09 deckt Art. 15–17 und 20.
- Offene Fristen: Nachweis der Einwilligung (V4), Logs (V6, „7 Tage“ unbestätigt), Konto (V1).
- Wortlaut und Bedienung der Einwilligung in der Oberfläche, Widerruf nach Art. 7 Abs. 3 sichtbar (R9); D05 regelt nur das Backend.
- Zugriffsprotokoll im Sinne des EHDS (wer, welche Datenkategorie, wann; R7) – nur relevant, falls EHDS doch greift.

**Sicherheit und Qualität**
- Bedrohungsmodell nach OWASP LLM Top 10 oder NIST GenAI Profile (R1, R6).
- Weitere Messgrößen über D03 hinaus: Halluzinationsrate, Verweigerungsverhalten, Belegtreue zu Quellen, Bias, Konsistenz bei gleicher Eingabe, Neutest nach Modell-Updates (R1, R6).
- Strategie für lange Gespräche bei 8K Kontext: Kürzen oder Zusammenfassen (R1, R6).
- Konkrete Grenze für `rate_limited` und Kostenbeobachtung (R1).
- FHIR-Leitfäden IPS/EPS und HL7 AI-Transparency-IG als Vorlage für die maschinenlesbare KI-Kennzeichnung (R7).

## 5. Offen zu diesem Abgleich

- `research/` ist nicht versioniert. Ob die Dateien ins Repo gehören (Urheberrecht fremder Folieninhalte,
  Dateigröße), entscheidet das Team.
- D04–D07 wurden für den Abgleich nur über Kopfdaten und Stichworte geprüft, nicht vollständig gelesen.
- Abschnitt 3 ist Gesprächsgrundlage; Folgearbeit läuft über Backlog-Tasks oder neue Entscheidungen.

## Verknüpft
- [[Architektur]] · [[Sicherheit-und-Grenzen]] · [[Compliance]]
- [[D08-Zweckbestimmung]] · [[D09-Datenschutz-EU]]
