# Übergabe TEST-001

- Stand (Datum, Status): 2026-10-14, Erledigt (Prüfauftrag). Gerüst ist tragfähig; 8 bestätigte Befunde, davon 2 vor F001 zu klären.
- Branch / letzter Commit / PR: `master`, `1af3b67 chore: initial scaffold`, kein PR. Kein Branch angelegt (Auftrag war nur lesen + Bericht); siehe Offene Fragen.
- Erledigt:
  - Gelesen: `AGENTS.md`, `CLAUDE.md`, `docs/Architektur.md`, `docs/decisions/README.md`, `status:`-Kopfdaten aller neun Entscheidungen, `scripts/check_structure.py`, `planning/handoffs/TEMPLATE.md`.
  - Modul-`AGENTS.md` gelesen (gefordert waren drei Stichproben, acht wurden nötig, weil Befunde quer lagen): `core/`, `features/guidance/`, `contracts/`, zusätzlich `security/`, `features/consent/`, `features/` (Elterntabelle), `knowledge/`, `apps/web/`.
  - Strukturcheck ausgeführt, Widersprüche zwischen Root-Regeln, Modulregeln und Entscheidungen gesucht.
- Tatsächlich ausgeführte Tests (Befehl + Ergebnis):
  - `python scripts/check_structure.py` → `PASS: structure, agent files, links, knowledge metadata, decisions.`, Exit 0.
  - `rtk python scripts/check_structure.py` → `rtk: command not found` (Exit 127). RTK ist hier nicht installiert, daher direkt mit `python` ausgeführt.
  - Quervergleich Tabelle `docs/decisions/README.md` gegen `status:` in D01–D09 → deckungsgleich, keine Drift.
- Nicht geprüft: siehe Abschnitt „Ungeprüft“.
- Offene Fragen / Blocker: siehe U-Punkte und die Frage zum Branch unten.
- Nächster konkreter Schritt: siehe letzter Abschnitt.

## Bestätigt

Jeder Punkt ist aus den genannten Stellen direkt belegbar.

**B1 — Entscheidungsbereich im Root veraltet.** `AGENTS.md:15` nennt „Entscheidungen D01–D07“. Vorhanden und in `docs/decisions/README.md:8-16` gelistet sind D01–D09. Dieselbe Root-Datei zitiert D08 (Einleitung, Regel 7) und D09 (Regel 11) als bindend. Der Satz, der den Entscheidungsstand beschreibt, kennt zwei der Entscheidungen nicht, auf die er sich selbst stützt.

**B2 — Harte Regel auf unbestätigter Entscheidung.** `AGENTS.md:68` (Regel 11, KI-Kennzeichnung, AI Act Art. 50) stützt sich auf D09; `security/AGENTS.md:11` macht D05 zum Vertrag. Beide haben `status: empfohlen`. `AGENTS.md:15` sagt aber: „Auf unbestätigten Entscheidungen nur bauen, wenn der Task es ausdrücklich sagt.“ Damit ist eine „harte Regel“ formal nicht baubar, solange kein Task sie freigibt. Nur D08 ist `bestaetigt`.

**B3 — Design-Vorlage gegen Wissensquelle (wichtigster Befund).** `apps/web/AGENTS.md:23` macht `design/vitasync-ui-v1.5.html` verbindlich und verlangt, „Farben, Abstände, Rundungen, Layout **und Texte** übernehmen“. Diese Datei schreibt Gesundheits- und Notfalltexte fest, u. a. `:593` („Im Notfall rufe 112 an … 116117“), `:802` („Welche Stelle für welches Anliegen: Hausarzt, Facharzt, 116117“), `:829`, `:904-910`. Root-Regel 6 (`AGENTS.md:63`) erlaubt Gesundheitsinhalte, Notfall-Stichworte und Zuständigkeiten **nur** aus `knowledge/` mit `status: geprueft`. Wer `apps/web/AGENTS.md` wörtlich folgt, verletzt Regel 6.

**B4 — Fallback in `guidance` erfindet eine Zuständigkeit.** `features/guidance/AGENTS.md:22`: „Kein passender geprüfter Eintrag → ehrlich sagen und allgemein auf Hausarzt oder 116117 verweisen.“ Das widerspricht zweifach: Root-Regel 6 verlangt „Fehlt ein Eintrag: blockieren und nachfragen“, und `guidance/AGENTS.md:8` verbietet dem Modul selbst, „Inhalte im Code festschreiben“. 116117 ist eine Zuständigkeit und müsste aus `knowledge/care_paths/` kommen — dieses Verzeichnis ist leer (siehe B7).

**B5 — Zwei Fachbereiche fehlen im Architekturdiagramm.** `features/AGENTS.md:19` schreibt für jeden Fachbereich „Zeile in dieser Tabelle und Knoten in `docs/Architektur.md`“ vor. Von den sechs Fachbereichen in `features/AGENTS.md:5-12` haben zwei keinen Knoten im Flowchart (`Architektur.md:11-24`): `analysis/` (nur im Prosaschritt 5 erwähnt) und `consent/` (nur eingefaltet in den Knoten „security/ Sitzung + Consent“). Die eigene Regel ist am Bestand nicht erfüllt.

**B6 — Abhängigkeitsregeln weichen zwischen Root und Architektur ab.**
- `api`: `Architektur.md:38` erlaubt `features/*` (öffentlich), `security`, `core`. `AGENTS.md:50` listet nur `features`, `security` — `core` fehlt. Da `AGENTS.md:3` bei Widerspruch „die strengere Regel“ anordnet, ist `api → core` damit verboten, obwohl dünne Routen Fehlerarten und Modelle aus `core` brauchen. Vermutlich unbeabsichtigt, aber heute normativ.
- `security`: `Architektur.md:41` hat eine Zeile (`core`, DB-Port). Die Kurzform in `AGENTS.md:50-54` hat für `security` **keine** Zeile, obwohl `security` dort als Importziel auftaucht.

**B7 — `knowledge/` deckt zwei der drei eigenen Kategorien nicht ab.** `knowledge/AGENTS.md:3` nennt `topics/`, `rules/` (Warnzeichen-Stichworte mit festem Notfallhinweis) und `care_paths/` (Anlaufstellen). Alle drei Ordner existieren, aber Inhalt gibt es nur in `topics/eisenmangel.md`; `rules/` und `care_paths/` sind leer. Root-Regeln 6 und 8 sowie `features/guidance` hängen an `rules/`. Für den Gerüststand erwartbar — relevant ist die Folge in B8.

**B8 — Der grüne Strukturcheck belegt keine inhaltliche Vollständigkeit.** `check_structure.py:111` iteriert je Wissensverzeichnis über `.glob("*.md")`. Ein leeres `rules/` erzeugt damit keinen Befund, weil es keine Datei zu prüfen gibt. Der Check prüft Kopfdaten vorhandener Einträge, nicht ob Pflichtkategorien belegt sind. `PASS` heißt also nicht, dass `knowledge/` benutzbar ist. Ebenso vergleicht der Check die Statustabelle in `docs/decisions/README.md` nicht gegen die Kopfdaten der Entscheidungsdateien — dieser Abgleich wurde hier manuell gemacht und war in Ordnung.

## Vermutet

Plausibel, aber nicht allein aus den Dateien entscheidbar; braucht eine menschliche Festlegung.

**V1 — Was zählt als „Produktcode“?** `AGENTS.md:15` sagt „Noch kein Produktcode“, während `apps/web/` bereits `design/` (verbindliche HTML-Vorlage, `tailwind.config.js`, `vendor/`), `src/` und `e2e/` enthält. Ob eine verbindliche Design-Vorlage den Stand „kein Produktcode“ bricht, ist offen. Hängt daran, wann F002/F004 die Befehlsliste füllen müssen.

**V2 — Consent-Schnitt ist nirgends ausgeschrieben.** Der Bestand liest sich sinnvoll: `security/AGENTS.md:3` hat die „zentrale Consent-Prüfung“, `features/consent/AGENTS.md:3` das Erteilen, Anzeigen, Widerrufen und Löschanfragen. Die Aufteilung steht aber in keiner Regel; `Architektur.md:16` beschriftet den Knoten „security/ Sitzung + Consent“, was nach Alleinbesitz klingt. Wer U023/U024 umsetzt, hat keine schriftliche Grenze zwischen Prüfung und Verwaltung.

**V3 — Zwei Formulierungen für dieselbe Statusregel.** Root-Regel 6 verlangt positiv `status: geprueft`. `guidance/AGENTS.md:8` verbietet negativ „Einträge mit Status `entwurf` verwenden“. Heute gleichwertig, weil `check_structure.py:121` nur diese zwei Werte zulässt. Käme je ein dritter Status hinzu, driften die Formulierungen auseinander; die Root-Fassung ist die strengere.

**V4 — `--fix` kann mehr als anlegen.** `AGENTS.md:89` beschreibt `--fix` als „legt `CLAUDE.md` an“. `check_structure.py:80-86` überschreibt zusätzlich eine abweichende bestehende `CLAUDE.md` mit dem Stub. Beim reinen Stub harmlos, in der Doku aber zu schwach beschrieben.

## Ungeprüft

- **U1** Inhaltliche Konsistenz der Entscheidungen untereinander (z. B. D02 FHIR gegen D06 Speicherung, D03 Modell gegen D09). Verglichen wurden nur Status und Tabellenabgleich.
- **U2** Nicht gelesene Modul-`AGENTS.md`: `features/chat/`, `features/recognition/`, `features/health_data/`, `features/analysis/`, `api/`, `adapters/llm|fhir|db/`, `migrations/`, `evals/`, `infra/`, `data/synthetic/`.
- **U3** Die Abhängigkeitsregeln aus B6 sind derzeit nicht maschinell prüfbar. `Architektur.md:44` verweist dafür auf import-linter ab F004; es gibt noch keinen Code zum Prüfen.
- **U4** `docs/compliance/` und `docs/nachweise/` wurden nicht gesichtet (Existenz und Vollständigkeit offen).
- **U5** Wiki-Links gelten nur so weit, wie `check_structure.py:93` prüft: Vault-Index aus `docs/**/*.md` über den Dateistamm, Anker hinter `#` werden abgeschnitten. Mehrdeutige Stämme und Anker sind nicht validiert.
- **U6** Inhalt von `planning/VitaSync_Coding_Backlog.xlsx` gegen Story-IDs in den Modul-Dateien (U001, U008, U023 …) nicht abgeglichen.
- **U7** `apps/web/design/README.md` wurde nur per Treffersuche berührt, nicht vollständig gelesen; die Gegenbeispiel-Tabelle dort ist inhaltlich ungeprüft.

## Abnahmekriterien

- [x] Strukturcheck ausgeführt, Ergebnis dokumentiert (`PASS`, Exit 0; Grenzen des Checks in B8).
- [x] Befunde getrennt nach bestätigt / vermutet / ungeprüft.
- [x] Keine Dateien außer diesem Bericht geändert. Nichts installiert, kein Commit, kein Branch, `--fix` nicht ausgeführt.

## Offene Frage an den Menschen

`AGENTS.md:76` verlangt für jede Task-ID einen Branch `task/<TASK-ID>-<kurzname>`. Dieser Auftrag war lesend mit einer Berichtsdatei; der Bericht wurde daher direkt auf `master` geschrieben, ohne Branch und ohne Commit. Soll auch ein reiner Prüfauftrag über `task/TEST-001-geruestpruefung` und einen PR laufen? Falls ja, gehört der Hinweis in die Workflow-Regel, weil er dort heute nicht steht.

## Genau ein nächster Schritt

Arbeitsauftrag **DOC-001** anlegen (reine Doku-Korrektur, vor F001): B3 und B4 beheben, also in `apps/web/AGENTS.md:23` „Texte“ auf UI-Rahmentexte einschränken und Gesundheits-, Notfall- und Zuständigkeitstexte ausdrücklich ausnehmen, und `features/guidance/AGENTS.md:22` auf „blockieren und nachfragen“ umstellen statt Hausarzt/116117 festzuschreiben; beide Stellen auf `knowledge/` mit `status: geprueft` verweisen. Begründung für den Vorrang: B3 und B4 sind die einzigen Befunde, die bei wörtlicher Befolgung der Modulregeln zu einem Verstoß gegen Root-Regel 6 und D08 im echten Code führen. B1, B2, B5–B7 sind Konsistenzmängel ohne unmittelbares Fachrisiko und können gebündelt danach laufen.
