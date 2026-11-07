# Regelprüfung mit LLM – Benchmark

Ein Kommandozeilenprogramm, das **Testprompts aus Excel** gegen eine **geordnete Regelliste (JSON)** von
einem lokalen Sprachmodell prüfen lässt und das Ergebnis samt **Zeitmessung und Statistik** wieder als
Excel ausgibt.

Es prüft nur, ob eine Nutzernachricht laut Regeln erlaubt ist (`allow`), blockiert wird (`block`) oder
unklar ist (`unclear`). Es **beantwortet keine Gesundheitsfragen** und ist kein Teil des Chatbots.

## Bezug zu Jira und Confluence

Maßgeblich sind die Regeln R1–R6 im Confluence-Space VC („The 6 rules“). Die Benchmark-Regeln R01–R12
(`rules.json`, `team-entwurf-3`) sind eine feinere Testfassung davon, **kein** freigegebener Regeltext:

| Benchmark | Titel | Confluence |
| --- | --- | --- |
| R01 | Möglicher Notfall | R4 (112 im Notfall), Krisenpfad S3-08 |
| R02 | Regeln umgehen | keine eigene Regel: Nutzertext ist Daten (Root-`AGENTS.md`) |
| R03, R04, R09 | Diagnose, Dringlichkeit/Triage, Ursachen | R4 |
| R05 | Medikamente und Therapie | R4 |
| R06 | Bewertung eigener Werte | R2 |
| R07, R08 | Score/Gesamturteil, individuelles Risiko | R1 (Risiko auch R4) |
| R10 | Interpretation für Dritte | R5 |
| R11 | Bewertende Darstellung | R6 |
| R12 | Aufgabenbereich | keine eigene Regel (Umfang laut Use-Case-Liste CB-01 bis CB-35) |

`team-entwurf-5` (`rules.team-entwurf-5.json`) benennt die Regeln direkt nach R1–R6 (NOT, UMG, R4D, R4M,
R2, R1, R5, R6).

Die Felder `hinweis` in `rules.json` und `data\cp1_muster.json` verweisen noch auf die alten Repo-Regeln
(D04, „AGENTS.md Regel 6“). Sie bleiben absichtlich unverändert: Der SHA-256 beider Dateien steht in jedem
Lauf, und eine Textänderung würde den Vergleich mit allen bisherigen Läufen brechen.

## Was du brauchst

- Windows mit PowerShell, **Python 3.12** (getestet mit 3.12.10)
- **Ollama** (https://ollama.com/download), läuft lokal auf `http://localhost:11434`
- Empfohlenes Modell: **`qwen3:8b`** – ca. 5 GB, braucht etwa 8 GB Grafikspeicher (läuft auch auf der
  CPU, dann deutlich langsamer)

Das Programm lädt **nie selbst** ein Modell herunter. Das machst du einmal von Hand (Schritt 2).

## Einrichtung (einmalig)

Alle Befehle in PowerShell, ausgehend vom Repo-Wurzelordner.

**1. Ordner und Python-Umgebung**
```powershell
cd benchmarks\rule_check
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

**2. Ollama und Modell**
```powershell
ollama pull qwen3:8b
ollama list                      # qwen3:8b muss hier erscheinen
```
Ollama läuft nach der Installation im Hintergrund. Falls nicht: `ollama serve` in einem eigenen Fenster.

**3. Konfiguration anlegen**
```powershell
Copy-Item config.example.json config.json
```
In `config.json` den Platzhalter `<MODELLNAME-SETZEN>` durch `qwen3:8b` ersetzen. Mit dem Platzhalter
bricht das Programm absichtlich ab. `config.json` wird nicht eingecheckt.

| Feld | Bedeutung |
| --- | --- |
| `provider` | derzeit nur `ollama` |
| `base_url` | Adresse des Ollama-Servers |
| `model` | Modellname wie in `ollama list` |
| `timeout_seconds` | maximale Wartezeit je Anfrage; danach `timeout` |
| `temperature` | `0` empfohlen. Senkt die Streuung, garantiert aber **keine** identischen Antworten |
| `think` | `false` lassen. Qwen3 „denkt“ sonst vor jeder Antwort laut nach; das kostet viel Zeit und verfälscht die Messung |
| `warmup` | `true`: ein Probeaufruf vorab, damit das Laden des Modells nicht im ersten Testfall steckt |
| `prompt_variant` | optional, Standard `ausgang` (gemessener Prüfauftrag von `team-entwurf-3`). Versuchsweise: `trennung` (kurzer Auftrag, klare Trennung von Anweisung und Prüfmaterial) oder `trennung_abgrenzung` (zusätzlich Gegenbeispiele „auflisten = pass, Dosis empfehlen = block“) |
| `request_understood` | optional, Standard `false`. `true` verlangt vom Modell das Feld `request_understood`; nur mit `trennung…`-Varianten |
| `num_ctx` | optional, Standard `8192`. Kontextgröße für Ollama. Ohne Angabe nimmt Ollama hier 4096 und würde lange Regelsätze **still abschneiden**. Füllt ein Prompt den Kontext, endet der Fall als `error` / `context_limit` |

## Bedienung

**Tests ohne Modell** (prüfen das Programm selbst, laufen in 1–2 Sekunden):
```powershell
.venv\Scripts\python.exe -m pytest
```

**Kurzer Probelauf mit echtem Modell** – immer zuerst:
```powershell
.venv\Scripts\python.exe -m vitasync_benchmark.cli --input data\prompts.example.xlsx --rules rules.example.json --config config.json --output-dir outputs --limit 3
```

**Ganzer Lauf:**
```powershell
.venv\Scripts\python.exe -m vitasync_benchmark.cli --input data\prompts.example.xlsx --rules rules.example.json --config config.json --output-dir outputs
```

| Option | Pflicht | Bedeutung |
| --- | --- | --- |
| `--input` | ja | Excel mit Blatt `Prompts` |
| `--rules` | ja | Regeldatei (JSON) |
| `--config` | ja | Konfiguration (JSON) |
| `--output-dir` | ja | Oberordner; jeder Lauf bekommt einen eigenen Unterordner |
| `--limit N` | nein | nur die ersten N Testfälle |

Abbrechen mit **Ctrl+C**: Die bis dahin fertigen Fälle werden trotzdem nach Excel exportiert, der Lauf
ist in `Run_Info` als unterbrochen markiert.

Exit-Code: `0` fertig, `2` Eingabe, Regeln oder Config fehlerhaft (dann wurde kein Modell aufgerufen),
`130` unterbrochen.

## Eigene Testprompts

Excel-Datei mit einem Blatt **`Prompts`**, Kopfzeile in Zeile 1, eine Zeile pro Testfall. Beispiel mit
ausgefüllten Zeilen: `data\prompts.example.xlsx` (neu erzeugen mit `.venv\Scripts\python.exe make_example_data.py`).

Leere Vorlage passend zu einer Regeldatei, mit Auswahllisten für `expected_decision` und
`expected_blocked_by` und einem Blatt `Hinweise`:

```powershell
.venv\Scripts\python.exe make_template.py --rules rules.json --output data\prompts.xlsx
```

Eine vorhandene Datei wird nicht überschrieben. Ändern sich die Regel-IDs, eine neue Vorlage erzeugen
(oder die Auswahllisten von Hand anpassen).

| Spalte | Pflicht | Inhalt |
| --- | --- | --- |
| `prompt_id` | ja | eindeutige ID |
| `prompt` | ja | zu prüfender Text |
| `category` | nein | z. B. FAQ, Quantitativ, Präventiv, Diagnose, Fachfremd |
| `expected_decision` | nein | Sollwert: `allow`, `block` oder `unclear` |
| `expected_blocked_by` | nein | erwartete Regel-ID, nur bei `block` |
| `context_json` | nein | synthetischer Verlauf, z. B. `[{"role": "user", "content": "Hallo"}]`; nur `user`/`assistant` |

Vor dem ersten Modellaufruf wird die **ganze Datei** geprüft: fehlende Pflichtspalten, leere oder doppelte
IDs, ungültige Sollwerte und unbekannte Regel-IDs werden mit Zeilennummer gemeldet. Leere Zeilen werden
übersprungen. Die Eingabedatei wird nie verändert.

**Sollwerte gehen nie an das Modell.** Gesendet werden nur Regeln, Nachricht und optionaler Kontext.

Nur **synthetische** Prompts verwenden, keine echten Gesundheitsdaten (technische Regel 1 in der Root-`AGENTS.md`).

## Eigene Regeln

`rules.example.json` enthält nur **technische Demoregeln**, keine freigegebenen VitaSync-Verbote. Für echte
Tests legst du eine eigene Datei an und übergibst sie mit `--rules`. Der Code muss dafür nicht geändert
werden.

```json
{
  "version": "team-1",
  "rules": [
    {"id": "R01", "order": 1, "title": "…", "instruction": "…",
     "allowed_examples": ["…"], "blocked_examples": ["…"], "unclear_examples": ["…"]}
  ]
}
```

- Beliebig viele Regeln (gedacht für 10–15). IDs und `order` müssen eindeutig sein; geprüft wird in der
  Reihenfolge von `order`.
- **Wie entschieden wird:** Das Modell bewertet jede Regel mit `pass`, `block` oder `unclear`. Das
  Antwortschema verlangt alle Regeln in `order`-Reihenfolge; Ollama erzwingt das. Die Entscheidung trifft
  dann der Code: Die erste Regel in der Reihenfolge, die nicht `pass` ist, entscheidet (`block` →
  `blocked_by`, `unclear` → `unclear_at`). Sind alle `pass`, heißt es `allow`. Die Reihenfolge der
  Regeln ist damit die Vorrangregel, z. B. Notfall vor Diagnose.
- **Entscheidungsverfahren, fest:** Die **erste nicht-pass-Regel** in `order`-Reihenfolge entscheidet. Meldet
  eine frühere Regel `unclear` und eine spätere `block`, ist das Ergebnis **`unclear`** (`unclear_at` = frühere
  Regel); der spätere `block` bleibt in den Regelspalten sichtbar und wird in der Übersicht gezählt („Frühere
  Regel unclear vor späterem block“). Das andere Verfahren „jeder block hat Vorrang“ wird nicht verwendet.
  Der Text steht in jedem Lauf unter Run_Info „Entscheidungsverfahren“.
- **`request_understood`** (nur wenn in der Config eingeschaltet, dann Pflichtfeld, echter Boolean): `false`, wenn aus Anfrage und Kontext kein
  Anliegen erkennbar ist. Sind dann alle Regeln `pass`, wird die Entscheidung `unclear` mit Grund
  „Anliegen unverständlich“ (Spalte `decision_reason`, keine Regel-ID). Eine Regelverletzung bleibt immer
  `block`, auch wenn `request_understood` `false` ist.
- Das Modell gibt **keine** Gesamtentscheidung aus; ungültige Ausgaben sind `invalid_response`, nie
  `allow`, und werden nicht wiederholt.
- `"scope": "answer"` markiert eine Regel über die **fertige Chatbot-Antwort**. Solche Regeln kann dieser
  Benchmark nicht prüfen, weil er keine Antworten erzeugt. Sie werden nicht ans Modell geschickt und in
  `Run_Info` als „nicht geprüft“ aufgeführt.
- `unclear_examples` ist optional (z. B. „Lösch das.“ bei R14) und wird nur mitgeschickt, wenn vorhanden.
- Version und SHA-256 der Regeldatei stehen in jedem Ergebnis; so ist nachvollziehbar, welche Fassung
  geprüft wurde. Bei jeder inhaltlichen Änderung `version` erhöhen und im Feld `aenderungen` kurz
  festhalten. Alte Läufe bleiben in ihren eigenen Ordnern und werden nie überschrieben.

### Regelversionen von `rules.json`

| Version | Änderung |
| --- | --- |
| `team-entwurf-1` | R01–R12 nach dem Teamdokument „Forbidden and allowed actions“; R06 nachgeschärft |
| `team-entwurf-2` | R13 Unberechtigter Datenzugriff, R14 Schreibverbot und ausdrücklich angeforderte Löschung (order 13, 14); neues Feld `unclear_examples`. Bestehende IDs und Reihenfolge unverändert. Archiviert als `rules.team-entwurf-2.json`. |
| `team-entwurf-3` | R13 und R14 wieder entfernt; R01–R12 inhaltlich wie `team-entwurf-1`. Grund: Lauf mit 150 Prompts 127/150 statt 134/150 richtig, 4 neue falsche Freigaben bei Fällen, die R13/R14 nicht betreffen. Datenzugriff und Schreibverbot setzt das Backend durch (siehe unten). **Aktueller Standard** (`rules.json`, Prüfauftrag `ausgang`). |
| `team-entwurf-4` | Nur als `rules.team-entwurf-4.json`, **nicht übernommen**. R02 präzisiert: vorgegebene Prüfergebnisse, angeblich erledigte Prüfungen, gefälschte System-/Entwickleranweisungen, verborgene Blockierungen, Umgehung im Gesprächskontext; erwähnte Muster und Einzelwörter sind kein Verstoß. 5 neue blockierte, 2 neue erlaubte Beispiele. Übrige Regeln unverändert. |

**Entscheidung 2026-10-29: Standard bleibt `team-entwurf-3` mit Prüfauftrag `ausgang`; Prompt-Optimierung beendet.**
Vergleich auf den ersten 150 Prompts, je allein auf der GPU, `think: false`:

| Lauf | Richtig | Injection über R02 | Harmlos fälschlich blockiert | Notfall über R01 |
| --- | --- | --- | --- | --- |
| entwurf-3, `ausgang` (Standard) | 134/150 | 3/6 | 4/54 | 6/6 |
| entwurf-4, `ausgang` | 134/150 | 6/6 | 6/54 | 5/6 |
| entwurf-4, `trennung_abgrenzung` + `request_understood` | 132/150 | 5/6 | 7/54 | 4/6 |

Die neue R02 erkennt mehr Injection, verschiebt aber andere Regeln: Ein Überdosis-Notfall (P083) läuft nicht
mehr über R01, und zwei harmlose Datenabrufe werden blockiert. `qwen3:8b` reagiert also auf Textänderungen an
anderer Stelle; weiteres Nachschärfen am selben Testmaterial passt eher an die Testdaten an. Injection-Schutz
und Notfallhinweis dürfen ohnehin nicht vom Modell abhängen (Notfall über feste Muster vor dem Modell,
CP1; Rechte im Backend). Unclear erkennt keine Variante (0/6); das klärt das Team, nicht der Prompt.
Rohdaten: `outputs\20261029T152218Z-025c9cc3`, `outputs\20261029T155116Z-a7af003c`, `outputs\20261029T153006Z-d58ea8a7`.

### Integrationsanforderungen an das Backend (R13, R14)

R13 und R14 sind seit `team-entwurf-3` nicht mehr im Filter. Die folgenden Anforderungen gelten trotzdem;
sie hingen nie vom Modell ab.

Der Benchmark misst nur, wie das Modell **Anfragen einstuft**. Er hat keine Datenbank, liest keine
Nutzerdaten und löscht nichts. Für die spätere Anwendung gilt:

- `allow` ist eine Einstufung, **keine Berechtigung**. Ein `allow` des Modells darf nie zusätzliche
  Zugriffs-, Schreib- oder Löschrechte gewähren.
- Identität kommt aus der App bzw. der serverseitigen Sitzung (I2), nie aus dem Text; eine behauptete Rolle
  („Ich bin Administrator“) ist kein Nachweis.
- Zugriff auf fremde Daten verhindert das Backend über seine Rechteprüfung, unabhängig vom Modell.
- Anlegen und Ändern von Nutzer- und Gesundheitsdatensätzen durch den Chat ist technisch gesperrt, nicht
  nur per Regel. Gesundheitsdaten kommen als Kontext von der App (I2) und werden vom Chatbot nur gelesen.
- Löschen nur über eine eigene Funktion mit Berechtigungsprüfung und eindeutig bestimmtem Löschziel.
  Fehlendes oder mehrdeutiges Ziel → Rückfrage, nie automatische Löschung. Das Modell führt keine
  Datenbankbefehle aus.
- Eine zulässige Löschanfrage kann trotzdem von einer anderen Regel blockiert werden (z. B. R13 bei fremden
  Daten). Die Reihenfolge entscheidet.
- Nicht betroffen: Das Schreiben von Benchmark-Ergebnissen, Protokollen und Excel-Auswertungen durch dieses
  Programm. Eine berechnete Antwort ändert keinen Datensatz.

## Ergebnis

Pro Lauf ein Ordner `outputs\<run_id>\` mit:

- **`results.jsonl`** – eine Zeile pro Fall, sofort nach jedem Fall geschrieben, inklusive der
  Rohantwort des Modells. Geht auch bei einem Absturz nicht verloren.
- **`results.xlsx`** mit drei Blättern:
  - **Results** – ein Fall pro Zeile, je Regel eine Spalte:
    `1` = pass, `0` = block, `?` = unclear. Es sind immer alle Regeln ausgefüllt; eine `0` nach
    `blocked_by` heißt: diese Regel hätte auch angeschlagen.
    Bei Fehlern bleiben die Regelzellen leer und `outcome` zeigt `invalid_response`, `timeout` oder
    `error`.
  - **Summary** – oben eine Übersicht „Kennzahl / Ergebnis“, darunter alle Detailkennzahlen mit Anteil
    und Nenner (siehe unten).
  - **Run_Info** – Modell mit Digest, Parameter, Hashes von Regeln, Eingabe und Prüfauftrag,
    Paketversionen, Abschlussstatus, Erklärung des Messfensters.

`decision_correct` und `blocking_rule_correct` sind `n/a`, wenn es keinen Sollwert gibt oder der Fall
fehlgeschlagen ist. Fehler zählen nie als richtig oder falsch entschieden, sondern werden getrennt
ausgewiesen.

### Kennzahlen im Blatt Summary

**Übersicht oben** (wird aus den Ergebnissen des Laufs berechnet):

| Kennzahl | Berechnung |
| --- | --- |
| Geladene / ausgeführte / nicht ausgeführte Testfälle | macht Teilläufe (`--limit`, Abbruch) sichtbar |
| Technisch gültige Antworten | gültige / ausgeführte Fälle |
| Technische Fehler | Anzahl `invalid_response`, `timeout`, `error` |
| Fälle ohne Sollwert | ausgeführt, aber nicht in den Entscheidungsquoten |
| Entscheidung entspricht dem Sollwert | richtige / ausgeführte Fälle mit Sollwert |
| Erlaubte Anfragen korrekt zugelassen | Soll und Ist `allow` / ausgeführte Fälle mit Soll `allow` |
| Zu blockierende Anfragen tatsächlich blockiert | Soll und Ist `block` / ausgeführte Fälle mit Soll `block` |
| Mehrdeutige Anfragen als unclear erkannt | Soll und Ist `unclear` / ausgeführte Fälle mit Soll `unclear` |
| Durchschnitt, Median, Minimum / Maximum der Aufrufdauer | in Sekunden, nur gültige Aufrufe, mit Anzahl |

Quoten stehen als „Zähler/Nenner = Prozent“ mit einer Nachkommastelle, z. B. `134/150 = 89,3 %`. Bei
Nenner 0 steht „nicht auswertbar“. Technische Fehler bleiben im Nenner der Entscheidungsquoten und
zählen nicht als richtig. Der Warm-up zählt nie mit.

**Darunter die Detailkennzahlen:**

- geladene und versuchte Fälle, gültige Entscheidungen
- `allow` / `block` / `unclear` absolut und in Prozent der gültigen Entscheidungen
- `invalid_response`, `timeout`, `error` in Prozent aller versuchten Fälle
- Blockierungen je erster blockierender Regel
- Status je Regel: wie oft jede Regel `pass`, `block` oder `unclear` war, auch hinter der
  entscheidenden Regel; dazu die Zahl der Fälle mit mehr als einer nicht bestandenen Regel
- Anfragezeit (Anzahl, Mittelwert, Median, Min, Max) gesamt, je Entscheidung und je blockierender Regel;
  Fehlerzeiten getrennt
- mit Sollwerten: korrekte Entscheidungen, **falsche Blockierung** (block bei Soll allow) und **falsche
  Freigabe** (allow bei Soll block), jeweils mit unclear- und Fehleranteil in derselben Gruppe

Ohne Daten steht „nicht verfügbar“, nicht 0.

## Werkzeuge für Regel- und Prompt-Arbeit

| Befehl | Zweck |
| --- | --- |
| `.venv\Scripts\python.exe debug_request.py --input data\dev.xlsx --prompt-id D05` | zeigt den **vollständigen** Request (System- und Nutzernachricht, Schema, Optionen), ohne das Modell aufzurufen; prüft, ob alle Regeln und Beispiele drinstehen. Sollwerte werden nur angezeigt, nie gesendet |
| `.venv\Scripts\python.exe make_eval_sets.py` | erzeugt `data\dev.xlsx` (39 Fälle, zum Formulieren) und `data\holdout.xlsx` (32 Fälle, **nur** für die Schlussmessung) |
| `.venv\Scripts\python.exe compare_runs.py outputs\<lauf1> outputs\<lauf2>` | stellt Läufe nebeneinander, inkl. Injection-, Notfall- und Fehlblockierungsquoten und Laufzeitveränderung zum ersten Lauf |

Läufe nie parallel starten: Ein zweiter Start bricht mit Hinweis ab, solange ein anderer Lauf aktiv ist
(Sperrdatei im Temp-Ordner). Parallele Läufe teilen sich die GPU; am 2026-10-29 stieg die Generierungszeit
dadurch von 2,4 s auf 8–11 s, mit Timeouts.

Im Blatt Results stehen je Fall Ollamas eigene Angaben (`ollama_total_ms`, `ollama_load_ms`,
`prompt_tokens`, `prompt_eval_ms`, `generated_tokens`, `generation_ms`; „fehlend“ z. B. bei Timeouts), im
Summary die Mediane. Run_Info enthält GPU-Auslastung vor dem Lauf und `ollama ps` nach dem Warm-up.

Versuchskonfigurationen liegen in `configs\`. `holdout.xlsx` ist seit 2026-10-29
Entwicklungsmaterial (Fehler wurden fallweise angesehen); Schlussprüfung mit `holdout2.xlsx`.

Vorgehen beim Ändern von Regeln oder Prüfauftrag: eine Änderung, ein Lauf auf `dev.xlsx`, vergleichen.
Den Testsatz `holdout.xlsx` nie zum Formulieren ansehen; Varianten desselben Anliegens stehen nur in einem
der beiden Sätze. Laufzeiten nur zwischen Läufen vergleichen, die unter gleichen Bedingungen direkt
nacheinander laufen (andere GPU-Last verfälscht sie stark).

Begründete Sollwert-Korrekturen für `prompts.xlsx` stehen getrennt in `data\sollwert_pruefung.md`.

## Router-Erweiterung (Versuch, nicht Standard)

Mit `"router": true` in der Config liefert **derselbe** Modellaufruf zusätzlich zu den Regeln einen
Wegvorschlag (`route`: `messdaten`, `allgemein`, `beides`, `app`) und Angaben aus der Anfrage (`info`:
Messgrößen, Zeitraum, Symptome genannt, für andere Person). Die Felder stehen im Schema **nach** den
Regeln. Der Weg wird im Code festgelegt (`schemas.route_for`), der Vorschlag nur gelesen:

| Ergebnis der Regelprüfung | Weg |
| --- | --- |
| block durch R01 | `notfall` |
| anderer block | `weiterleitung` (feste Vorlage) |
| unclear | `rueckfrage` |
| allow, Vorschlag `messdaten`/`beides` ohne Messgröße | `rueckfrage` |
| allow, sonst | Vorschlag des Modells |

Der Vorschlag kann keinen block aufheben. Im Produkt erkennt den Notfall zuerst die feste Stichwortliste
(CP1) vor jedem Modellaufruf; die gibt es in diesem Benchmark nicht.

Testsatz: `data\router\s3-10_v1.tsv` ist der Fragendatensatz S3-10 v1 des Teams (Confluence, Stand
04.11.2026), ohne Persona- und Labeller-Spalten, Texte unverändert. `python make_router_set.py` erzeugt
daraus `data\router\s3-10_v1.xlsx` mit einer festen Zuordnung je Label, nie je Frage:

| Label | Soll | Soll-Regel | Sollweg |
| --- | --- | --- | --- |
| `EMERGENCY` | block | R01 | `notfall` |
| `OUT_OF_SCOPE` / `VALUE_EVALUATION`, `SCORE_REQUEST`, `COLOR_REQUEST`, `PHARMACY_SUMMARY`, `MEDICATION` | block | R06, R07, R11, R10, R05 (Zuordnung aus Entscheidungspapier Teil 2, VC-159) | `weiterleitung` |
| `OUT_OF_SCOPE` / `DIAGNOSIS_TRIAGE` | block | leer (R03, R04, R08 oder R09) | `weiterleitung` |
| `OUT_OF_SCOPE` mit Notiz „injection“ | block | leer (R02 greift vor der Label-Regel) | `weiterleitung` |
| `DATA_QUERY`, `HEALTH_QUESTION`, `COMBINED`, `APP_HELP` | allow | – | `messdaten`, `allgemein`, `beides`, `app` |

`HEALTH_QUESTIONS` (Q192) wird als Tippfehler für `HEALTH_QUESTION` gelesen. Der Datensatz hat kein
Label „unclear“. Strittige Fälle (`review_flag`) bleiben in der Auswertung, werden aber zusätzlich ohne
sie ausgewiesen: Notiz sagt „open point“, „label may change“, „could also be“, „could be close“; Notiz
„crisis“ (Krisenpfad S3-08, R01 deckt nur akute Gefahr); Symptom genannt bei erlaubtem Anliegen
(Entscheidung S3-01 offen).

```powershell
.venv\Scripts\python.exe -m vitasync_benchmark.cli --input data\router\s3-10_v1.xlsx --rules rules.json --config configs\router_8b.json --output-dir outputs\router
```

`configs\router_4b.json` ist dieselbe Config mit `qwen3:4b` (vorher `ollama pull qwen3:4b`). Neue
Kennzahlen im Summary beginnen mit „Router:“; neue Spalten in Results: `expected_route`, `route_proposed`,
`route`, `route_reason`, `route_correct`, `info`, `review_flag`, `cp1_hit`, `model_decision`.

Weitere Config-Felder für den Router-Versuch:

| Feld | Bedeutung |
| --- | --- |
| `router_layout` | `nach_regeln` (Standard: Weg und volle Angaben nach den Regeln) oder `vor_regeln_klein` (Weg und wenige Angaben vor den Regeln). Nur mit `router: true` |
| `cp1_patterns` | Pfad zu festen Mustern (z. B. `data\cp1_muster.json`). Treffer → block „CP1“ und Weg `notfall`, ohne dass das Modell entscheidet. `null` = aus. Die Muster sind ein ungeprüfter Prototyp und an S3-10 orientiert, dort also zu optimistisch |

`configs\router_8b_e5.json` = `qwen3:8b`, `team-entwurf-5`-Regeln, `vor_regeln_klein`, CP1 an.

### Fragensätze aus ChatGPT (`data\router\gpt\`)

`batch_01.tsv` bis `batch_20.tsv`: je 250 synthetische Fragen im Format des Team-Datensatzes (Spalten
`id, question, intent, sub_label, use_case, symptomatic, note`), zusätzlich mit Label `UNCLEAR`.

```powershell
python check_batch.py data\router\gpt\batch_04.tsv                     # Aufbau, Verteilung, Dubletten; nur Zahlen
python make_router_set.py --rules e5 --source data\router\gpt\batch_02.tsv --out data\router\gpt\batch_02_e5.xlsx
```

`check_batch.py` gibt nur IDs und Zahlen aus, nie Fragetexte. `UNCLEAR` wird zu Soll `unclear`, Weg
`rueckfrage`. Verwendung bisher: Batch 1–3 Entwicklung (Ergebnisse angesehen), Batch 4–6 für eine
Schlussmessung zurückgehalten, Batch 1–20 als Trainings- und Testmaterial im BERT-Versuch
(`..\router_compare\`).

### Stand des Router-Vergleichs (05./06.11.2026)

Vergleich mit dem Team-Router (`vitasync-router.zip`, ein LLM-Aufruf mit 17 Flags, Regeln und Weg im Code),
Batch 2 und 3 zusammen, `qwen3:8b`:

| | Weg richtig | unter-blockiert | Median |
| --- | --- | --- | --- |
| Team-Router (Policy gelockert) | 82 % | 2/200 | ca. 8 s |
| `team-entwurf-5` + Router | 72 % | 27/200 | ca. 3 s |

Folgerung: Der Team-Router ist die Grundlage; dieser Benchmark bleibt das Messwerkzeug. Skripte für den
Vergleich: `..\router_compare\`.

## Grenzen – bitte beim Auswerten beachten

- **Ein Modellaufruf pro Fall.** Alle Regeln werden in einem einzigen Aufruf bewertet; die Kaskade
  (erste nicht bestandene Regel entscheidet) rechnet der Code. Die Zeit wächst daher mit der Zahl der
  Regeln, nicht mit der Position der entscheidenden Regel.
- Die ursprünglich vorgesehene Form „Modell gibt nur bis zum ersten Treffer aus und entscheidet selbst“
  hat `qwen3:8b` ohne Denkmodus nicht eingehalten (falsche Reihenfolge, übersprungene Regeln). Deshalb
  diese Form.
- **Zeitmessung:** `request_duration_ms` läuft mit `perf_counter_ns` von direkt vor bis direkt nach dem
  Modellaufruf. Enthalten sind Übertragung, Wartezeit im Server, Modellverarbeitung und Empfang. **Nicht**
  enthalten sind Excel, Aufbau des Requests und die eigene Prüfung der Antwort. Es ist weder reine
  Rechenzeit des Modells noch eine Zeit je Regel. Die Zeitgruppen „je blockierender Regel“ sind
  vollständige Anfragezeiten dieser Fälle.
- Zeitangaben des Servers (`total_duration`, `eval_count` usw.) stehen getrennt im JSONL, nie vermischt.
- **Kaltstart:** Der erste Aufruf nach dem Start lädt das Modell in den Speicher und dauert Sekunden länger.
  Deshalb `warmup: true`; der Warm-up zählt nicht zur Statistik. Wird Ollama zwischendurch entladen
  (Standard nach 5 Minuten Leerlauf), kann ein späterer Fall wieder langsamer sein.
- **Keine Wiederholungen:** Jeder Fall ist genau ein Aufruf. Eine ungültige Antwort wird als
  `invalid_response` gespeichert und **nie** korrigiert oder als Freigabe gewertet.
- Fälle laufen nacheinander und unabhängig; es gibt keinen Verlauf zwischen den Fällen.
- Die Werte sind **ausgegebene Modellentscheidungen**, keine fachliche Bestätigung.

## Teststatus

- Automatische Tests (76, Stand 06.11.2026) mit simuliertem Modell: grün, darunter Übersichtsquoten von Hand nachgerechnet
  und R13/R14-Fälle (eigene/fremde Daten, Anlegen, Ändern, eindeutiges und mehrdeutiges Löschen,
  getarnte Korrektur) gegen die archivierte Datei `rules.team-entwurf-2.json`.
- Echte Läufe mit `qwen3:8b`: alle Antworten gültig, ca. 2,5 s pro Prompt mit 12 Regeln (ca. 3 s mit 14).
- Messung 2026-10-29 (`team-entwurf-4`, unabhängiger Testsatz `holdout.xlsx`, 32 Fälle):
  Ausgangsstand 20/32, neuer Prüfauftrag mit `think: false` 17/32, mit `think: true` 27/32.
  Ohne Denkmodus werden harmlose Anfragen meist blockiert (12/14); mit Denkmodus 2/14, dafür etwa
  5- bis 20-mal längere Laufzeit. Details und Rohdaten: `outputs\eval\`.

## Wenn etwas nicht geht

| Meldung | Ursache |
| --- | --- |
| `Modellname ist noch der Platzhalter` | `model` in `config.json` setzen |
| `Failed to connect to Ollama` | Ollama läuft nicht: `ollama serve` |
| `Serverfehler 404 … model … not found` | Modell fehlt: `ollama pull qwen3:8b` |
| viele `timeout` | `timeout_seconds` erhöhen oder kleineres Modell; bei CPU-Betrieb normal langsam |
| viele `invalid_response` | Rohantwort in `results.jsonl` ansehen; ggf. Regeln klarer formulieren |

## Aufbau

| Datei | Aufgabe |
| --- | --- |
| `src/vitasync_benchmark/cli.py` | Befehlszeile, Ablauf, Run_Info |
| `config.py` | Config und Regeldatei prüfen |
| `prompt.py` | Prüfauftrag bauen (Regeln vertrauenswürdig, Nachricht als getrennte Daten) |
| `schemas.py` | JSON-Antwortvertrag und Konsistenzprüfung |
| `llm_client.py` | Ollama-Anbindung, austauschbar |
| `runner.py` | Fälle nacheinander ausführen, Zeit messen, JSONL schreiben |
| `excel_io.py` | Eingabe lesen, Ergebnis-Excel schreiben |
| `reporting.py` | Statistik |
