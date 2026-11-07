# Modul: Routing

Zweck: Wählt aus Regelergebnis, LLM-Vorschlag und CP1-Ergebnis die Route (Entscheidung des Safety-Routers M3): erlaubter Weg, OUT_OF_SCOPE mit Sub-Label, EMERGENCY, CRISIS oder CLARIFY.
Zuständig: Atakan Cubukcu

## Grenzen
- Darf nutzen: `core/intent.py` (`RuleResult`, `Extraction`, `GuardResult`, `RouteDecision`, `Policy`).
- Darf nicht: Regeln neu bewerten (das macht `rule_pipeline`); eine Sperre aufheben; LLM aufrufen; Antworttexte erzeugen; andere Features importieren.

## Verträge
- Öffentlich: `route(rule, extraction, guard, policy)`, `route_from_guard(guard)` (CP1-Treffer ohne LLM), `route_fallback(guard, error)` (SAFE_DEFAULT), `path_for_allowed(flags)`.
- Der LLM-Vorschlag darf nur verschärfen. Confidence unter `min_confidence` → CLARIFY. CP1-Injection → OUT_OF_SCOPE ohne Sub-Label.
- `RouteDecision.template` nennt den Knoten aus den Flowcharts S3-07a/b. `audit_record()` enthält nur Labels (I5).

## Tests
- `cd apps/api && .venv/Scripts/python.exe -m pytest tests/features/routing`

## Fallen
- Zwischen erlaubten Wegen (DATA_QUERY oder COMBINED) entscheiden die Flags, nicht der LLM-Vorschlag.
- `audit_record()` nie um Text, Flags oder Werte erweitern.
