# Modul: Benchmarks

Zweck: Eigenständige Mess- und Prüfwerkzeuge für das Sprachmodell. Kein Teil der Anwendung.
- `rule_check/`: Regelprüfung von Testprompts mit Excel-Auswertung, Router-Versuch, CP1-Prototyp, Fragensätze (S3-10, ChatGPT-Batches 1–20).
- `router_compare/`: Messung des Team-Routers (`vitasync-router.zip`), Vergleiche, BERT- und Hybrid-Versuch.

Zuständig: Atakan Cubukcu. Im Team gehört Testen zu Modul M9 (Testrunner, VC-79) und zu den Testsätzen (VC-80, VC-115).

## Grenzen
- Darf nutzen: eigene Python-Umgebung je Unterordner, lokales Ollama, synthetische Testprompts, eine entpackte Kopie des Team-Routers (nur lesen, nie das Zip ändern).
- Darf nicht: aus `apps/` importieren oder von dort importiert werden; echte Nutzer- oder Gesundheitsdaten verarbeiten; Gesundheitsantworten erzeugen; externe KI-Dienste mit Nutzerdaten ansprechen; Modelle automatisch herunterladen (Ausnahme: das BERT-Basismodell beim ausdrücklich gestarteten Training).
- Regeldateien hier sind **Testmaterial**, keine freigegebenen Regeln. Maßgeblich sind R1–R6 in Confluence; die Zuordnung R01–R12 ↔ R1–R6 steht in `rule_check/README.md`.

## Verträge
- `rule_check/`: Antwortvertrag in `src/vitasync_benchmark/schemas.py`, Ein- und Ausgabeformat in `rule_check/README.md`.
- `router_compare/`: Eingaben über `common.load_questions` (`.tsv`, `.csv`, `prompts.xlsx`); Ergebnis-CSV-Spalten in `run_team.py`.
- Nicht eingecheckt: `bert_model/` (über 400 MB, zu groß für GitHub), `.team_router/` (Team-Code, nur lokal), lokale `config.json`. Läufe (`outputs/`, `results/`), `configs/` und `backups/` sind eingecheckt.

## Tests
- `cd benchmarks/rule_check && .venv/Scripts/python.exe -m pytest` (ohne Modellserver, mit simuliertem Client; Stand 06.11.2026: 76 grün)
- `router_compare/` hat keine automatischen Tests; Prüfung durch Nachrechnen bekannter Läufe (README dort).

## Fallen
- `KeyboardInterrupt` ist keine `Exception`: Test-Doppel, die Abbrüche simulieren, müssen auf `BaseException` prüfen.
- Qwen3 mit `think: true` braucht ein Vielfaches an Zeit; Messungen nur mit gleicher `think`-Einstellung vergleichen.
- Läufe nie parallel und nie neben anderer GPU-Last: Zeiten werden wertlos.
- Fragetexte der ChatGPT-Batches nicht lesen oder ausgeben, nur IDs und Zahlen; Batch 4–6 sind für eine Schlussmessung zurückgehalten.
- `hinweis`-Texte in `rules.json` und `data/cp1_muster.json` nicht ändern: Ihr SHA-256 steht in jedem Lauf.
- Unter Windows nie `localhost` als Ollama-Adresse: "localhost" wird zuerst als IPv6 `::1` aufgelöst, Ollama hört nur auf IPv4, jeder Aufruf wartet ~2,1 s. Immer `http://127.0.0.1:11434` (gemessen 08.11.2026: 2.123 ms gegenüber 82 ms je Embedding).
