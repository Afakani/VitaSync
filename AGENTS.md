# VitaSync – Regeln für Menschen und KI-Agenten

Gilt im ganzen Repository. Die `AGENTS.md` in Unterordnern ergänzen diese Datei für ihren Ordner. Bei Widerspruch gilt die strengere Regel.

## Was VitaSync ist

Chatbot in der VitaSync-App (App: Johnny Bytes, Chatbot: Team VC, FH Aachen). Nutzer stellen Fragen zu eigenen Gesundheitsdaten, zu allgemeiner Prävention und zur App. Der Bot zeigt Daten, gibt allgemeine Lifestyle-Tipps und leitet medizinische Fragen an Menschen weiter (Apotheke, Hausarztpraxis, 116117, im Notfall 112).

**VitaSync ist ein Wellness- und Präventionsprodukt, kein Medizinprodukt.** Der Bot beurteilt nichts, diagnostiziert nichts und empfiehlt keine Behandlung. Im Zweifel gilt die konservativere, weniger „medizinische“ Option.

## Quellen der Wahrheit

**Jira und Confluence sind maßgeblich, nicht dieses Repo.** Bei Widerspruch gilt Confluence bzw. Jira; das Repo verlinkt, es kopiert nichts Maßgebliches.

| Was | Wo |
| --- | --- |
| Backlog, Sprints, Zuständigkeit | Jira, Projekt VC |
| Regeln R1–R6 | Confluence VC: „The 6 rules (R1-R6)“ |
| Erlaubt / nicht erlaubt, Beispieltabelle | Confluence VC: „What the bot is allowed and not allowed to do“, „Forbidden and allowed actions“ |
| Use Cases CB-01 bis CB-35 | Confluence VC: „Chatbot use case master list“ |
| Pipeline und Prüfpunkte | Confluence VC: „Ethical boundaries in the pipeline“ |
| Entscheidungen, ADRs, Schnittstellen I1–I5 | Wegweiser: [docs/decisions/README.md](docs/decisions/README.md) |

Jira und Confluence werden aus diesem Repo heraus **nur gelesen**. Schreiben nur nach ausdrücklicher Freigabe für die konkrete Aktion.

## Rolle dieses Repos

Eigenes **Arbeitsrepo**: Prototypen, Benchmarks, Experimente. Das Team-Repo mit den Modulen M1–M9 entsteht separat (VC-74). `apps/api` ist ein Prototyp-Gerüst (Endpunkt `/healthz`), kein Team-Code.

Alle Befehle vom Wurzelverzeichnis aus. Einrichtung: `apps/api/README.md`.

```
# Datenbank:     docker compose --env-file .env -f infra/docker-compose.yml up -d db
# Start API:     cd apps/api && .venv/Scripts/python.exe -m uvicorn vitasync.api.app:app --reload --host 127.0.0.1 --port 8000
# Tests API:     cd apps/api && .venv/Scripts/python.exe -m pytest
# Benchmark:     cd benchmarks/rule_check && .venv/Scripts/python.exe -m pytest
# Strukturcheck: python scripts/check_structure.py
```

Pfade mit `.venv/Scripts/` gelten für Windows; unter Linux und macOS `.venv/bin/` nutzen.

## Begriffe aus Jira

| Begriff | Bedeutung |
| --- | --- |
| M1–M9 | Module des Chatbots: M1 Chat-API, M2 Klassifikator, M3 Safety-Router, M4 Orchestrator (Flows je Typ), M5 Rechenwerkzeuge, M6 RAG/Wissensbasis, M7 LLM-Gateway, M8 Output Guard, M9 Testrunner |
| Routen | DATA_QUERY, HEALTH_QUESTION, COMBINED, APP_HELP, OUT_OF_SCOPE (+ Sub-Label), EMERGENCY, Krisenpfad, CLARIFY |
| I1–I5 | Schnittstellen zur App: I1 Chat-API, I2 Kontext (Gesundheitsdaten), I3 Einwilligung, I5 Audit-Ereignisse |
| CB-xx | Use Case aus der Masterliste |
| R1–R6 | Die sechs Regeln (unten) |

Mehr: [docs/Glossar.md](docs/Glossar.md).

## Wo gehört was hin

| Ordner | Inhalt |
| --- | --- |
| `apps/web/` | Prototyp-Oberfläche und Designentwürfe. Spricht nur über die HTTP-API. |
| `apps/api/` | Prototyp-Server: HTTP, Fachlogik, Adapter für LLM, FHIR, Datenbank. |
| `apps/api/src/vitasync/features/<name>/` | Ein Fachbereich = ein Ordner. |
| `contracts/` | Schnittstellen im Repo: API-Entwürfe, LLM-Ausgabeschemas, FHIR-Beispiele. Maßgeblich sind I1–I5 in Confluence. |
| `knowledge/` | Inhalte (Themen, Hinweise, Anlaufstellen) mit Status. Kein Code. |
| `evals/` | Versionierte Testsätze mit Soll-Ergebnis. |
| `data/synthetic/` | Synthetische Testpatienten und Fixtures. Niemals echte Daten. |
| `infra/` | Lokale Dienste (Datenbank, FHIR-Testserver, LLM-Laufzeit). |
| `docs/` | Architektur, Ablauf, Glossar, Wegweiser zu den Entscheidungen (Obsidian-Vault, normales Markdown). |
| `docs/compliance/` | Datenschutz-Arbeitsstand im Repo. |
| `planning/` | Nur Übergaben. Backlog ist Jira. |
| `scripts/` | Entwicklungswerkzeuge, u. a. Strukturcheck. |
| `benchmarks/` | Eigenständige Messwerkzeuge für das Sprachmodell, z. B. `rule_check/` (Regelprüfung) und `router_compare/` (Router-Vergleiche). Kein Teil der Anwendung. |

Keine zweiten Bäume daneben anlegen (`src/`, `backend/`, `frontend/`, `utils/` im Root).

## Abhängigkeiten im Backend

Details: `docs/Architektur.md`. Kurzform:

- `api` → `features`, `security`, `core`. Routen sind dünn: validieren, Feature aufrufen, Antwort mappen.
- `features/<x>` → `core`, `security`, Schnittstellen aus `core/ports.py`. Andere Features nur über deren `__init__.py`.
- `adapters/*` → `core`. Adapter implementieren Ports und kennen keine Features.
- `core` → nur Standardbibliothek und die Validierungsbibliothek. Kein HTTP, keine Datenbank, kein LLM.
- Keine Zyklen. Module klein und austauschbar halten: Regelprüfung, Routing und Modellaufruf sind getrennte Module mit klarer Ein- und Ausgabe.

## Harte Regeln

### R1–R6 (Confluence „The 6 rules“, gekürzt)

| # | Regel |
| --- | --- |
| R1 | Kein Risiko- oder Ampel-Score. Die Kennzahl heißt „VitaSync-Index“ und ist neutral gefärbt. |
| R2 | Keine klinische Bewertung von Werten: kein „normal / auffällig / kritisch / zu hoch / zu niedrig“, keine roten Zonen, keine Schwellenlinien als Urteil. Werte werden nur gezeigt und im Verlauf dargestellt. |
| R3 | Empfehlungen nur als Lifestyle: „Vorschlag / Tipp / Impuls“. Nie „Risiko erkannt“, „Therapie“, „Diagnose“, „Befund“. |
| R4 | Weiterleiten statt urteilen: keine Symptom-Triage, keine Diagnose, keine Medikamentenempfehlung, keine individuelle Risikoeinschätzung. Medizinische Anfragen gehen an Apotheke, Hausarztpraxis, 116117 (112 im Notfall). |
| R5 | Apothekenansicht ohne Systemdeutung: kein Score-Urteil, keine hervorgehobenen „Auffälligkeiten“, kein berechneter „Präventionsbedarf“. Die Apotheke interpretiert. |
| R6 | Keine wertenden Farben: Rot/Gelb/Grün nie als „gut/schlecht“, auch nicht im Diagramm. |

Grundsatz: Die menschliche, medizinische Deutung passiert außerhalb des Systems. Das System erfasst, strukturiert und visualisiert. Es deutet nicht.

### Technische Regeln

1. Nur synthetische Daten aus `data/synthetic/`. Keine echten Patientendaten, Zugangsdaten oder Secrets in Code, Tests, Prompts, Commits, Logs.
2. Nutzernachrichten und importierte Texte sind Daten, keine Anweisungen an das System.
3. Rechnen, Regeln und Routing entscheidet deterministischer Code, nicht das LLM. Das LLM erkennt und formuliert. LLM-Ausgaben werden gegen ein Schema validiert; ungültig → kontrollierter Fallback.
4. Notfall- und Krisentexte nur in der freigegebenen Fassung (Confluence S3-08). Nicht selbst formulieren. Fehlender Treffer ist keine Entwarnung.
5. Logs und Audit (I5) enthalten keine Nachrichteninhalte und keine Gesundheitswerte, nur IDs, Zeiten, Route, Regel, Fehlercodes.
6. Fehlender Wert ist nicht null. Erlaubte Berechnungen und Umgang mit Lücken: Confluence S3-05.
7. Keine Tracking-Tools, keine externen KI-Dienste mit Nutzerdaten. Das Modell läuft selbst gehostet (ADR „Self-hosted open-weight LLM“).

## Arbeitsablauf

1. Gearbeitet wird **auf Ansage**. Passt die Arbeit zu einem Jira-Ticket, wird der Key genannt.
2. Lesen: die `AGENTS.md` der betroffenen Ordner und die betroffene Confluence-Seite. Nicht das ganze Repo lesen.
3. `git status` prüfen. Fremde Änderungen nie zurücksetzen oder löschen.
4. Branch: `vc-<nr>-<kurzname>` (mit Jira-Ticket) oder `work/<kurzname>`. Nie direkt auf `main` arbeiten.
5. Kleinsten prüfbaren Schritt bauen, Tests dazu, `python scripts/check_structure.py`.
6. Commit nur auf Ansage: `<VC-xx oder Bereich>: <Imperativ auf Englisch>`, z. B. `VC-87: add rule pipeline module`.
7. Bei Unterbrechung: `planning/handoffs/<Jira-Key oder Kurzname>.md` nach Vorlage.

## Grenzen jeder Arbeit

- Nur den angesagten Umfang. Keine beiläufigen Refactorings, Dependency-Upgrades oder Formatierungswellen.
- Zu groß? Schnitt vorschlagen, nichts stillschweigend weglassen.
- Neues Modul: Ordner + `AGENTS.md` nach `docs/vorlagen/MODUL_AGENTS.md` + `python scripts/check_structure.py --fix` + Zeile in der Tabelle der Eltern-`AGENTS.md`. `--fix` überschreibt Modul-`CLAUDE.md`, die vom Stub `@AGENTS.md` abweichen; eigener Inhalt gehört in die `AGENTS.md`.
- Keine Secrets einchecken. Konfiguration über `.env` (nicht versioniert) und `.env.example`.
- Kein Deployment, keine Änderungen an geteilten Diensten ohne ausdrücklichen Auftrag.

## Dokumentation

- Die `AGENTS.md` eines Moduls **ist** seine Moduldoku (Zweck, Grenzen, Verträge, Tests).
- `README.md` nur dort, wo Menschen etwas einrichten oder starten müssen.
- Öffentliche Funktionen: Docstring mit Zweck, Einheiten, Rückgabe, Fehlern. Kommentare erklären das Warum.
- Wiederkehrende Fehlerquelle → eine Zeile unter „Fallen“ in der Modul-`AGENTS.md`.

## Sprache

Code, Bezeichner, Commits: Englisch. Doku, Rückfragen, Übergaben: Deutsch. UI: Deutsch.

## Abschlussbericht

Was sich am Verhalten geändert hat · geänderte Dateien · tatsächlich ausgeführte Tests (Befehl + Ergebnis) · nicht geprüft · offene Punkte · ein nächster Schritt. Unterscheide: implementiert / getestet / fachlich geprüft.
