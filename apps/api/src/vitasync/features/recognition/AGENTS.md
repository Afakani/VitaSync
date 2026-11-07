# Modul: Anfrageerkennung (M2)

Zweck: Lässt das LLM erkennen, wonach gefragt wird (17 Flags plus Vorschlag und Confidence), und prüft die Ausgabe streng gegen das Schema. Entscheidet nichts.
Zuständig: Atakan Cubukcu

## Grenzen
- Darf nutzen: LLM-Port aus `core/ports.py`, `core/intent.py`.
- Darf nicht: Antworten formulieren; Regeln anwenden oder Wege wählen; Dringlichkeit, Ursachen oder Diagnosen ableiten; Modellausgabe ungeprüft weitergeben.

## Verträge
- Öffentlich: `extract_flags(text, extractor, retries=1)`, `parse_and_validate(content)`, `flag_schema()`.
- Ausgabe-Schema: `contracts/llm/intent_flags.v1.schema.json`. `flag_schema()` muss damit übereinstimmen (Test in `tests/contracts/`).
- Ungültige Ausgabe → `ExtractionError`; nach der Wiederholung entscheidet der Aufrufer (SAFE_DEFAULT).

## Tests
- `cd apps/api && .venv/Scripts/python.exe -m pytest tests/features/recognition`

## Fallen
- Ungültige oder unvollständige Modellausgabe ist ein Normalfall: definierter Fallback, kein Absturz.
- Fehlermeldungen enthalten nie den Nutzertext.
- Neue Flags ändern Schema, Prompt und Regel-Pipeline zugleich; danach mit `benchmarks/` messen.
