# Modul: Input Guard (CP1)

Zweck: Prüft jede Nachricht vor dem Modell mit festen Mustern auf Notfall, Krise und Prompt-Injection. Ein Notfall- oder Krisentreffer führt ohne LLM zum festen Weg.
Zuständig: Atakan Cubukcu

## Grenzen
- Darf nutzen: `core/intent.py` (`GuardResult`), Musterdatei (Standard `knowledge/rules/cp1_patterns.json`, Pfad aus `CP1_PATTERNS`).
- Darf nicht: Muster im Code festschreiben; Text speichern oder loggen (Ergebnis enthält nur Muster-IDs); Dringlichkeit einstufen.

## Verträge
- Öffentlich: `InputGuard(patterns)`, `InputGuard.from_file(path)`, `check(text) -> GuardResult`, `normalise(text)`.
- Musterdatei: Abschnitte `emergency`, `crisis`, `injection`, je Liste aus `{id, pattern}`; Regex auf normalisiertem Text (klein, Umlaute als ae/oe/ue/ss, Satzzeichen zu Leerzeichen).

## Tests
- `cd apps/api && .venv/Scripts/python.exe -m pytest tests/features/input_guard`

## Fallen
- Die Musterdatei ist ein Teamentwurf und **nicht medizinisch geprüft**. Kein Treffer ist keine Entwarnung.
- Muster arbeiten auf normalisiertem Text: „ä“ steht dort als „ae“.
