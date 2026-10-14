# VitaSync – Regeln für Menschen und KI-Agenten

Gilt im ganzen Repository. Die `AGENTS.md` in Unterordnern ergänzen diese Datei für ihren Ordner. Bei Widerspruch gilt die strengere Regel; den Widerspruch im PR nennen.

## Was VitaSync ist

Chat-Prototyp (FH Aachen, Interdisziplinäres Projekt). Nutzer stellen Gesundheitsfragen. Das System erkennt die Anfrage, gibt allgemeine Gesundheitsinformation aus geprüften Quellen, zeigt eigene (synthetische) Daten an und rechnet damit, ohne zu bewerten.

**VitaSync ist kein Medizinprodukt** ([D08](docs/decisions/D08-Zweckbestimmung.md)). Es macht keine Aussage über den Gesundheitszustand einer konkreten Person: keine Diagnose, keine Bewertung von Werten, keine Dringlichkeitseinstufung, keine Ursachen, keine Medikamente oder Therapien. Vor jeder Implementierung mit fachlichem Inhalt D08 lesen.

Das lokale LLM erkennt Anfragen, liest Dokumente und formuliert freigegebene Inhalte. Rechnen, Regeln und Rechte entscheidet Code.

## Aktueller Stand

- Entscheidungen D01–D10 stehen in `docs/decisions/`. Bestätigt sind **D01** (Stack), **D08** (Zweckbestimmung) und **D10** (Testlauf); D02–D07 und D09 sind empfohlen. Vor der Arbeit Status prüfen: **„Empfohlen“ ist nicht „Bestätigt“.** Auf unbestätigten Entscheidungen nur bauen, wenn der Task es ausdrücklich sagt.
- Produktcode: bisher nur das leere API-Gerüst aus F002 (`apps/api`, Endpunkt `/healthz`). Fachbereiche unter `features/` sind noch leer.
- Der Chat-API-Vertrag liegt als Entwurf in `contracts/api/draft/` (F003), Status „bestätigt vorbehaltlich Review“. Umgesetzt wird er mit F007; erst dann entsteht das generierte `contracts/api/openapi.json`.
- Web-Grundgerüst (`apps/web`) folgt mit F006, Testautomatisierung und CI mit F004. Keine Befehle erfinden.

Alle Befehle vom Wurzelverzeichnis aus. Einrichtung und Erklärungen: `apps/api/README.md`.

```
# Befehle (Stand F002; Web-Befehle folgen mit F006, CI mit F004)
# Datenbank:   docker compose --env-file .env -f infra/docker-compose.yml up -d db
# Start API:   cd apps/api && .venv/Scripts/python.exe -m uvicorn vitasync.api.app:app --reload --host 127.0.0.1 --port 8000
# Tests API:   cd apps/api && .venv/Scripts/python.exe -m pytest
# Tests Web:   -
# Strukturcheck: python scripts/check_structure.py
```

Pfade mit `.venv/Scripts/` gelten für Windows; unter Linux und macOS `.venv/bin/` nutzen.

## Wo gehört was hin

| Ordner | Inhalt |
| --- | --- |
| `apps/web/` | Website (Chat-Oberfläche). Spricht nur über die HTTP-API. |
| `apps/api/` | Server: HTTP, Fachlogik, Adapter für LLM, FHIR, Datenbank. |
| `apps/api/src/vitasync/features/<name>/` | Ein Fachbereich = ein Ordner. Neue Funktionalität gehört in den zuständigen Feature-Ordner. |
| `contracts/` | Einzige Quelle für Schnittstellen: API-Schema, LLM-Ausgabeschemas, FHIR-Profile. |
| `knowledge/` | Fachlich freigegebene Inhalte: Themen, Regeln, Anlaufstellen, Quellen. Kein Code. |
| `evals/` | Versionierte Testsätze mit Soll-Ergebnis für Anfrageerkennung und Antworten. |
| `data/synthetic/` | Synthetische Testpatienten und Fixtures. Niemals echte Daten. |
| `infra/` | Lokale Dienste (Datenbank, FHIR-Testserver, LLM-Laufzeit). |
| `docs/` | Architektur, Entscheidungen, Arbeitsablauf (Obsidian-Vault, normales Markdown). |
| `docs/compliance/` | Datenschutz-Dokumente (Verzeichnis, TOM, Hinweis, Pannenablauf). |
| `docs/nachweise/` | Nachweise zur Definition of Done je Meilenstein. |
| `planning/` | Backlog (Excel), Arbeitsaufträge, Übergaben. |
| `scripts/` | Entwicklungswerkzeuge, u. a. Strukturcheck. |

Keine zweiten Bäume daneben anlegen (`src/`, `backend/`, `frontend/`, `utils/` im Root).

## Abhängigkeiten im Backend

Details und Diagramm: `docs/Architektur.md`. Kurzform:

- `api` → `features`, `security`, `core`. Routen sind dünn: validieren, Feature aufrufen, Antwort mappen.
- `features/<x>` → `core`, `security`, Schnittstellen aus `core/ports.py`. Andere Features nur über deren `__init__.py` (öffentliche Funktionen), nie über interne Dateien.
- `adapters/*` → `core`. Adapter implementieren Ports und kennen keine Features.
- `security` → `core`, DB-Port.
- `core` → nur Standardbibliothek und die gewählte Validierungsbibliothek. Kein HTTP, keine Datenbank, kein LLM.
- Keine Zyklen. Ein Feature, das ein anderes braucht, ruft es auf – es kopiert keine Logik.

## Harte Regeln: Gesundheit und Daten

Diese Regeln gelten unabhängig vom Status der zitierten Entscheidungen. Eine Entscheidung mit Status
„empfohlen“ schwächt die Regel nicht ab; sie erklärt nur, warum die Regel so lautet.

1. Nur synthetische Daten aus `data/synthetic/`. Keine echten Patientendaten, Zugangsdaten oder Gesundheitsinhalte in Code, Tests, Prompts, Commits, Logs, Issues.
2. Identität kommt aus der serverseitigen Sitzung, nie aus Request-Parametern oder Modellausgaben.
3. Freigabe (Consent) wird serverseitig **vor** Datenzugriff und **vor** Modellaufruf geprüft. Ein ausgeblendeter Button ist kein Schutz.
4. Nutzernachrichten und importierte Texte sind Daten, keine Anweisungen an das System.
5. Berechnungen und Zugriffsentscheidungen deterministisch im Code, nie durch das LLM. LLM-Ausgaben werden gegen ein Schema in `contracts/llm/` validiert; ungültig → kontrollierter Fallback.
6. Gesundheitsinhalte, Notfall-Stichworte und Zuständigkeiten **nur** aus `knowledge/` mit Status `geprueft`. Fehlt ein Eintrag: blockieren und nachfragen. Nichts selbst erfinden, auch nicht „vorläufig“. Ausnahme im Testlauf siehe [D10](docs/decisions/D10-Testlauf.md).
7. **Keine individuelle Bewertung** (D08): keine Diagnose oder Verdachtsdiagnose, keine Wörter wie normal/auffällig/gut/schlecht zu eigenen Werten, keine Referenzbereiche neben eigenen Werten, keine Dringlichkeitseinstufung, keine Ursachen, keine Medikamente, keine Bewertung medizinischer Bilder. Gilt auch für Prompts und Modellausgaben.
8. Nennt jemand ein freigegebenes Warnzeichen-Stichwort, erscheint zuerst der feste, für alle gleiche Notfallhinweis. Fehlender Treffer ist keine Entwarnung. Nie behaupten, alle Notfälle zu erkennen.
9. Fehlender Wert ist nicht null. Selbstauskunft, importierter Befund und ausgelesenes Dokument bleiben unterscheidbar.
10. Logs enthalten keine Nachrichteninhalte und keine Gesundheitswerte, nur Request-ID, Zeiten, Fehlercodes.
11. Jede KI-Antwort ist in der UI als KI-generiert gekennzeichnet und im API-Vertrag maschinenlesbar markiert (AI Act Art. 50, [D09](docs/decisions/D09-Datenschutz-EU.md)).
12. Gesundheits-, Notfall- und Zuständigkeitstexte werden **nie zur Laufzeit übersetzt**. Übersetzt ist nicht mehr der fachlich freigegebene Wortlaut. Fehlt die geprüfte Fassung in der gewählten Sprache, erscheint die deutsche Fassung mit Hinweis. Welche Sprache ein Inhalt hat, steht im Kopfdatum `sprache` und im Vertrag als `content_language`.
13. Neue Verarbeitung personenbezogener Daten (neues Feld, neue Tabelle, neuer Log-Eintrag) → im selben PR `docs/compliance/Verarbeitungsverzeichnis.md` und bei Bedarf `TOM.md` ergänzen. Passwörter nur gehasht. Keine Tracking- oder Analyse-Tools, keine externen KI-Dienste mit Nutzerdaten.

## Arbeitsablauf

1. Nur an einer **zugewiesenen** Task-ID arbeiten: GitHub-Issue mit dir als Assignee oder Datei in `planning/work-orders/`. Keine Zuweisung → nicht beginnen, nachfragen.
2. Lesen: Issue bzw. Arbeitsauftrag, die `AGENTS.md` der betroffenen Ordner, die betroffene Entscheidung in `docs/decisions/`. Nicht das ganze Repo lesen.
3. `git status` prüfen. Fremde Änderungen nie zurücksetzen oder löschen.
4. Branch `task/<TASK-ID>-<kurzname>`, z. B. `task/T-U004-02-intent-validator`.
5. Kleinsten prüfbaren Schritt bauen, Tests dazu, `python scripts/check_structure.py`.
6. Commit: `<TASK-ID>: <Imperativ auf Englisch>`, z. B. `T-U004-02: add intent output validator`.
7. PR mit Vorlage öffnen. Status höchstens „Im Review“. Eine **andere** Person reviewt und merged. Nie direkt auf `main` pushen. Im Testlauf gilt [D10](docs/decisions/D10-Testlauf.md).
8. Bei Unterbrechung oder Übergabe: `planning/handoffs/<TASK-ID>.md` nach Vorlage aktualisieren.
9. Auch reine Prüf- und Doku-Aufträge laufen über Branch und PR. Ein Bericht direkt auf `main` ist kein zulässiger Weg.
10. Jeder Task-PR aktualisiert **seine eigene** Zeile im Blatt `Tasks` des Backlogs auf „Im Review“. Nach der Freigabe folgt im selben PR ein letzter Commit mit Status „Erledigt“ und der PR-Nummer in der Spalte „Änderung“. Eine Beschränkung des Auftrags auf bestimmte Ordner gilt nie für die eigene Backlog-Zeile und die eigene Übergabe.

Status: Offen → Bereit → In Bearbeitung → Im Review → Erledigt. „Blockiert“ immer mit konkretem Grund.

## Grenzen jedes Auftrags

- Nur den Umfang der Task-ID. Keine beiläufigen Refactorings, Dependency-Upgrades, Formatierungswellen oder Zusatzfeatures.
- Zu groß? Schnitt vorschlagen und dokumentieren, nichts stillschweigend weglassen.
- `contracts/` nur ändern, wenn der Task es verlangt; dann alle Verbraucher, Tests und Doku im selben PR anpassen.
- Neues Modul: Ordner + `AGENTS.md` nach `docs/vorlagen/MODUL_AGENTS.md` + `python scripts/check_structure.py --fix` + Zeile in der Tabelle der Eltern-`AGENTS.md`. `--fix` legt fehlende `CLAUDE.md` an **und überschreibt vorhandene, die vom Stub `@AGENTS.md` abweichen**. Eigener Inhalt in einer Modul-`CLAUDE.md` geht dabei verloren; er gehört in die `AGENTS.md`.
- Keine Secrets einchecken. Konfiguration über `.env` (nicht versioniert) und `.env.example`.
- Kein Deployment, keine Änderungen an geteilten Diensten ohne ausdrücklichen Auftrag.

## Dokumentation

- Die `AGENTS.md` eines Moduls **ist** seine Moduldoku (Zweck, Grenzen, Verträge, Tests). Bei geänderter Verantwortung oder Schnittstelle im selben PR anpassen.
- `README.md` nur dort, wo Menschen etwas einrichten oder starten müssen.
- Öffentliche Funktionen: Docstring mit Zweck, Einheiten, Rückgabe, Fehlern. Kommentare erklären das Warum, nicht das Was.
- Neue Architekturentscheidung: `docs/decisions/` nach Vorlage. Eine Datei pro Entscheidung.
- Wiederkehrende Fehlerquelle entdeckt → eine Zeile unter „Fallen“ in der betroffenen Modul-`AGENTS.md`.

## Sprache

Code, Bezeichner, Commits: Englisch. Doku, Issues, PRs, Rückfragen, Übergaben: Deutsch. UI: Deutsch.

## Abschlussbericht

Task-ID und Status · was sich am Verhalten geändert hat · geänderte Dateien · tatsächlich ausgeführte Tests (Befehl + Ergebnis) · nicht geprüft · offene Punkte · ein nächster Schritt. Unterscheide: implementiert / getestet / fachlich geprüft / abgenommen.
