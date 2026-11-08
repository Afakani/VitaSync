# Modul: Sicherheitsnetz (CP2)

Zweck: Prüft nach dem Routing den Text mit festen Wortmustern auf Bewertungs-, Score-, Farb- und Diagnosefragen. Ein Treffer macht aus einer erlaubten Route oder CLARIFY eine Weiterleitung (OUT_OF_SCOPE mit Sub-Label). Kann nur sperren, nie freigeben.
Zuständig: Atakan Cubukcu

## Grenzen
- Darf nutzen: `core/intent.py`, `input_guard.normalise` (gleiche Normalisierung wie CP1), Musterdatei (Standard `knowledge/rules/cp2_patterns.json`, Pfad aus `CP2_PATTERNS`).
- Darf nicht: eine Sperre aufheben; Notfall- oder Krisenrouten ändern; Text speichern oder loggen; Muster im Code festschreiben.

## Verträge
- Öffentlich: `SafetyNet(patterns)`, `SafetyNet.from_file(path)`, `check(text)`, `apply(decision, text, policy)`.
- Musterdatei: `rules` mit `id`, `sub_label`, `pattern`, optional `requires` (muss zusätzlich treffen) und `unless` (Ausnahme).
- Abschaltbar mit `ROUTER_POLICY=safety_net=false`. Übernommen aus dem Team-Router v0.5 (`safety_net.py`); Gleichheit mit Tolgas Pipeline am 08.11.2026 auf Batch 1 geprüft (250/250).

## Tests
- `cd apps/api && .venv/Scripts/python.exe -m pytest tests/features/safety_net`

## Fallen
- Die Muster sind ein Teamentwurf (Version 0.1-draft-2026-11-07) und wachsen mit jedem Test: Gefahr, an die Testdaten anzupassen. Neue Muster nur mit Beispiel und neuer Version.
- Kein Treffer heißt nicht „erlaubt“; entschieden haben vorher Regeln und Routing.
