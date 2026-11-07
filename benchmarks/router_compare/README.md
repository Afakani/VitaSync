# Router-Vergleich

Skripte, mit denen der Team-Router (`vitasync-router.zip`) gemessen und mit anderen Ansätzen verglichen
wurde. Nur Zahlen und IDs werden ausgegeben, nie Fragetexte. Ergebnisse landen in `results/` (eingecheckt), das
trainierte BERT-Modell in `bert_model/` (nicht eingecheckt, über 400 MB; mit `train_bert.py` neu erzeugen).

## Einrichtung

1. Team-Router entpacken (das Zip bleibt unverändert):
   ```powershell
   Expand-Archive ..\..\vitasync-router.zip -DestinationPath .team_router
   ```
   Oder einen anderen Ort über `VITASYNC_ROUTER_DIR` angeben (Ordner, der `vitasync_router\` enthält).
2. `run_team.py` und `compare.py` brauchen nur Python 3.12 und `openpyxl` (z. B. die venv von
   `..\rule_check`). Ollama mit `qwen3:8b` muss laufen.
3. Für die BERT-Skripte eine eigene venv: `torch` (CUDA), `transformers`, `scikit-learn`, `openpyxl`.
   Getestet mit torch 2.5.1+cu124 und transformers 4.46.3. Das Basismodell `deepset/gbert-base` lädt
   `transformers` beim ersten Training herunter.

## Skripte

| Skript | Zweck |
| --- | --- |
| `run_team.py <lang\|kurz\|zahl> <fragen> <out.csv>` | Team-Router auf einem Fragensatz (`.tsv` Batch, `.csv` oder `prompts.xlsx`). `lang` = Original; `kurz`/`zahl` = andere Schlüsselnamen der 17 Flags |
| `compare.py <batch_e5.xlsx> name=pfad ...` | Team-CSV und `rule_check`-Läufe auf demselben Batch vergleichen (Weg, unter-/über-blockiert, Notfall, Median) |
| `eval_prompts.py csv <out.csv> [name]` | Team-Router-Ergebnis auf `prompts.xlsx` je Kategorie bewerten |
| `train_bert.py` | BERT auf Batch 1–14 trainieren, 15–17 Validierung, 18–20 und S3-10 Test |
| `eval_prompts.py bert` | BERT auf `prompts.xlsx` |
| `hybrid.py <team_prompts.csv>` | offline: BERT sperrt nur bei hoher Sicherheit, sonst Team-Router |

Läufe nur auf Ansage und nie parallel zu anderen GPU-Läufen.

## Ergebnisse (05./06.11.2026, `qwen3:8b`)

**Team-Router auf `prompts.xlsx`** (660 Prompts ohne die drei Kategorien, für die das Team-Regelwerk keine
Klasse hat): 91,4 % richtig, unter-blockiert 16/360, Notfall verpasst 3/30, über-blockiert 14/270, unklar
erkannt 6/30, Median 7,5 s. Schwach: Mehrdeutig 6/30, Prompt Injection 21/30, Manipulation 12/30.

**BERT** (gbert-base, 8 ms auf GPU): auf ChatGPT-Testbatches 94 %, auf S3-10 (Team-Stil) nur 73 % und
11/20 Notfälle verpasst. Lernt den ChatGPT-Stil, nicht die Aufgabe. Allein nicht geeignet.

**Hybrid** (BERT sperrt bei Sicherheit ≥ T, sonst Team-Router):

| T | BERT allein | gespart | Notfall verpasst |
| --- | --- | --- | --- |
| 0,9 | 158/750 | 20 min | 6/30 (schlechter) |
| 0,95 | 115/750 | 14 von ca. 93 min | 3/30 (wie Team-Router) |

Schwelle auf denselben Daten gewählt, also optimistisch. Empfehlung: kein BERT; Team-Router verbessern.

**Schlüsselnamen** (Kurztest): Ausgabetokens lang 196, kurz 165, zahl 147. Voller Lauf auf Batch 2 steht aus.
