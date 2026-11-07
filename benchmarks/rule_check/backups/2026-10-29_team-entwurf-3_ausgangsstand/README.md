# Regelprüfung mit LLM – Benchmark

Ein Kommandozeilenprogramm, das **Testprompts aus Excel** gegen eine **geordnete Regelliste (JSON)** von
einem lokalen Sprachmodell prüfen lässt und das Ergebnis samt **Zeitmessung und Statistik** wieder als
Excel ausgibt.

Es prüft nur, ob eine Nutzernachricht laut Regeln erlaubt ist (`allow`), blockiert wird (`block`) oder
unklar ist (`unclear`). Es **beantwortet keine Gesundheitsfragen** und ist kein Teil des Chatbots.

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

Nur **synthetische** Prompts verwenden, keine echten Gesundheitsdaten (harte Regel 1 im Repo).

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
| `team-entwurf-3` | R13 und R14 wieder entfernt; R01–R12 inhaltlich wie `team-entwurf-1`. Grund: Lauf mit 150 Prompts 127/150 statt 134/150 richtig, 4 neue falsche Freigaben bei Fällen, die R13/R14 nicht betreffen. Datenzugriff und Schreibverbot setzt das Backend durch (siehe unten). |

### Integrationsanforderungen an das Backend (R13, R14)

R13 und R14 sind seit `team-entwurf-3` nicht mehr im Filter. Die folgenden Anforderungen gelten trotzdem;
sie hingen nie vom Modell ab.

Der Benchmark misst nur, wie das Modell **Anfragen einstuft**. Er hat keine Datenbank, liest keine
Nutzerdaten und löscht nichts. Für die spätere Anwendung gilt:

- `allow` ist eine Einstufung, **keine Berechtigung**. Ein `allow` des Modells darf nie zusätzliche
  Zugriffs-, Schreib- oder Löschrechte gewähren.
- Identität kommt aus der serverseitigen Sitzung; eine im Text behauptete Rolle („Ich bin Administrator“)
  ist kein Nachweis (harte Regel 2 im Repo).
- Zugriff auf fremde Daten verhindert das Backend über seine Rechteprüfung, unabhängig vom Modell.
- Anlegen und Ändern von Nutzer- und Gesundheitsdatensätzen durch den Chat ist technisch gesperrt, nicht
  nur per Regel. Medizinische Quelldaten (FHIR, OMOP) sind ohnehin nur lesbar (harte Regel 14).
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

- Automatische Tests (51) mit simuliertem Modell: grün, darunter Übersichtsquoten von Hand nachgerechnet
  und R13/R14-Fälle (eigene/fremde Daten, Anlegen, Ändern, eindeutiges und mehrdeutiges Löschen,
  getarnte Korrektur) gegen die archivierte Datei `rules.team-entwurf-2.json`.
- Echte Läufe mit `qwen3:8b`: alle Antworten gültig, ca. 2,5 s pro Prompt mit 12 Regeln (ca. 3 s mit 14).

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
