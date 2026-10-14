# Modul: Anfrageerkennung

Zweck: Intent, Entitäten (Symptome, Messgrößen), Verneinung und Zeitangaben aus der Nutzernachricht bestimmen.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: LLM-Port mit Schema aus `contracts/llm/`, `core/`.
- Darf nicht: Antworten formulieren; Dringlichkeit oder Diagnosen ableiten; Modellausgabe ungeprüft weitergeben.

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- Stories: U004, U010, U013

## Tests
- `apps/api/tests/features/recognition/`. Verhalten testen, nicht Implementierung spiegeln.

## Fallen
- Ungültige oder unvollständige Modellausgabe → definierter Fallback (Rückfrage), kein Absturz.
- Verneinungen („kein Fieber“) sind die häufigste Fehlerquelle; in `evals/recognition/` abdecken.
