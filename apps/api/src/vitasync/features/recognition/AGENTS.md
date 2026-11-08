# Modul: Anfrageerkennung (M2)

Zweck: Erkennt, wonach gefragt wird (17 Flags plus Intent-Vorschlag und Confidence). Zwei Wege: SLM (Embedding + Klassifikator, Team-Router v0.5, Standard) oder LLM (Prompt + JSON-Schema). Entscheidet nichts.
Zuständig: Atakan Cubukcu

## Grenzen
- Darf nutzen: LLM- und Embedding-Port aus `core/ports.py`, `core/intent.py`, Gewichtsdatei (`SLM_WEIGHTS`).
- Darf nicht: Antworten formulieren; Regeln anwenden oder Wege wählen; Dringlichkeit, Ursachen oder Diagnosen ableiten; Modellausgabe ungeprüft weitergeben.

## Verträge
- Öffentlich: `SlmRecognizer(embedder, weights)` und `LlmRecognizer(extractor)`, beide Text → `Extraction`; `SlmWeights`, `classify_vector`, `extract_flags`, `parse_and_validate`, `flag_schema()`.
- SLM (aus `slm_extractor.predict_lr`, Team v0.5): Sigmoid je Flag, Schwellen 0,35 für Sicherheits-Flags, 0,7 für die drei von CP2 abgedeckten Flags, sonst 0,5; Softmax für den Intent; `min_confidence` 0,5 (`SLM_MIN_CONFIDENCE`). Gewichte `apps/api/models/slm_lr_qwen3-embedding-8b.json` (Backend `api:qwen-qwen3-embedding-8b`, train_hash `c94ba9fb9ca1`, aus Tolgas Repo v0.5).
- Ausgabe-Schema: `contracts/llm/intent_flags.v1.schema.json`. `flag_schema()` muss damit übereinstimmen (Test in `tests/contracts/`).
- Ungültige Ausgabe → `ExtractionError`; nach der Wiederholung entscheidet der Aufrufer (SAFE_DEFAULT).

## Tests
- `cd apps/api && .venv/Scripts/python.exe -m pytest tests/features/recognition`

## Fallen
- Ungültige oder unvollständige Modellausgabe ist ein Normalfall: definierter Fallback, kein Absturz.
- Fehlermeldungen enthalten nie den Nutzertext.
- Neue Flags ändern Schema, Prompt und Regel-Pipeline zugleich; danach mit `benchmarks/` messen.
